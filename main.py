
import os
import io
import json
from flask import Flask, render_template, request, redirect, url_for, send_file, abort, flash
from google.cloud import storage, secretmanager
import google.generativeai as genai

app = Flask(__name__)

# Function to retrieve secrets from Google Secret Manager
def get_secret(secret_name):
    client = secretmanager.SecretManagerServiceClient()
    secret_path = f"projects/cloud-app-cnd-2025/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(name=secret_path)
    return response.payload.data.decode("UTF-8")

# Retrieve Flash Warning Key from Google Secret Manager
app.secret_key = get_secret("FLASH_WARNING_KEY") # for flashing warning message 


# Retrieve Gemini API key from Google Secret Manager
genai.configure(api_key=get_secret("GEMINI_API_KEY"))

bucket_name = 'cloud-app-cnd-2025-bucket'

@app.route('/')
def index():
    return render_template('index.html', uploaded_files=list_files_from_bucket())

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('form_files')
    if not files or all(file.filename == "" for file in files):
        flash("⚠️ Please select at least one image to upload.", "warning")
        return redirect(url_for('index'))
    
    for file in files:
        filename = file.filename
        if filename and not blob_exists(bucket_name, filename):
            upload_blob(bucket_name, file, filename)
            generate_and_store_image_metadata(filename)
    return redirect(url_for('index'))

@app.route('/files/<filename>')
def get_file(filename):
    try:
        file_stream, content_type = download_blob(bucket_name, filename)
        return send_file(io.BytesIO(file_stream), mimetype=content_type, as_attachment=False, download_name=filename)
    except Exception:
        abort(404, description="File not found in the bucket")

def list_files_from_bucket():
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs()
    return [blob.name for blob in blobs if blob.name.lower().endswith(('.jpeg', '.jpg', '.png'))]

def blob_exists(bucket_name, blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    return bucket.blob(blob_name).exists()

def upload_blob(bucket_name, file, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.content_type = file.content_type
    blob.upload_from_file(file)

def download_blob(bucket_name, blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    if blob.exists():
        return blob.download_as_bytes(), blob.content_type
    else:
        raise Exception("Blob not found")

def generate_and_store_image_metadata(filename):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(filename)
    file_path = f"/tmp/{filename}"
    blob.download_to_filename(file_path)
    
    title, description = generate_image_description(file_path)
    title = title.strip()
    formatted_description = format_description(description.strip())
    metadata = {"title": title, "description": formatted_description}
    json_filename = f"{os.path.splitext(filename)[0]}.json"
    json_blob = bucket.blob(json_filename)
    json_blob.upload_from_string(json.dumps(metadata, indent=4), content_type='application/json')


def generate_image_description(file_path):
    img = upload_to_gemini(file_path, mime_type="image/jpeg")

    combined_request = [
        img,
        """Generate a title and a detailed description for the image:
        
        - The **title** should be short, professional, and without any punctuation.
        - The **description** should be detailed, formatted like markdown, and use **bold** for key elements.
        
        Return the output in this JSON format:
        ```
        {"title": "Generated title here", "description": "Generated description here"}
        ```
        """
    ]

    response = genai.GenerativeModel(model_name="gemini-1.5-flash").generate_content(combined_request)

    # Extract and parse JSON response
    try:
        json_str = response.text.strip().replace("```json", "").replace("```", "").strip()
        result = json.loads(json_str)
        title = result.get("title", "").strip()
        description = result.get("description", "").strip()
    except json.JSONDecodeError:
        title, description = "Untitled", "No description available."

    return title, description



def format_description(description):
    formatted_desc = description.replace("**", "<strong>").replace("**", "</strong>")
    formatted_desc = formatted_desc.replace("\n", "<br><br>")  
    return formatted_desc


def upload_to_gemini(path, mime_type=None):
    return genai.upload_file(path, mime_type=mime_type)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)), debug=True)
