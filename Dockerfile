# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app
COPY requirements.txt requirements.txt
# requirements.txt file containing all the required libraries.
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE $PORT

# Run gunicorn with the specified parameters from our existing Procfile
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
