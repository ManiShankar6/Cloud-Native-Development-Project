# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
ENV PORT 8080  # Cloud Run expects your app to run on port 8080

# Set the working directory in the container
WORKDIR $APP_HOME

# Copy only requirements first for caching dependencies
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port for Cloud Run
EXPOSE 8080

# Start the Flask app with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "--workers=1", "--threads=8", "--timeout=0", "main:app"]
