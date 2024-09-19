# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /opt/application/flask

# Copy the requirements.txt first to leverage Docker cache
COPY requirements.txt /opt/application/flask/

# Install any dependencies
RUN apt-get update && apt-get install -y build-essential
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the entire project to the working directory
COPY . /opt/application/flask

# Expose port 8088 for the Flask app
EXPOSE 8088

# Define the entry point for the Flask app
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8088", "project.app:create_app()"]
