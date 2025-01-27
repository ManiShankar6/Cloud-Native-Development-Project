import os
from flask import Flask, render_template, request, redirect, url_for, send_file, abort
from google.cloud import storage
import io

app = Flask(__name__)

bucket_name = 'cloud-app-cnd-2025-bucket'

@app.route('/')
def index():
    # Render the index.html file from the templates folder
    return render_template('index.html', uploaded_files=list_files_from_bucket())

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('form_files')
    for file in files:
        filename = file.filename
        # Upload directly to the bucket
        if not blob_exists(bucket_name, filename):
            upload_blob(bucket_name, file, filename)
    return redirect('/')

@app.route('/files/<filename>')
def get_file(filename):
    # Retrieve file directly from the bucket
    try:
        file_stream, content_type = download_blob(bucket_name, filename)
        return send_file(
            io.BytesIO(file_stream),
            mimetype=content_type,
            as_attachment=False,
            download_name=filename
        )
    except Exception as e:
        abort(404, description="File not found in the bucket")

def list_files_from_bucket():
    # List all image files in the bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs()
    return [blob.name for blob in blobs if blob.name.lower().endswith(('.jpeg', '.jpg', '.png'))]

def blob_exists(bucket_name, blob_name):
    # Check if a blob exists in the bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    return bucket.blob(blob_name).exists()


def upload_blob(bucket_name, file, destination_blob_name):
    # Upload file directly to Google Cloud Storage
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.content_type = file.content_type  # Set the MIME type explicitly
    blob.upload_from_file(file)


def download_blob(bucket_name, blob_name):
    # Download a file from Google Cloud Storage
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    if blob.exists():
        file_stream = blob.download_as_bytes()
        content_type = blob.content_type or "image/jpeg"  # Default to a common image type
        return file_stream, content_type
    else:
        raise Exception("Blob not found")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)), debug=True)
