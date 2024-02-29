# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy all files into container
COPY . /app

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the environment variables
ENV HOST=0.0.0.0
ENV PORT=8000

# Set the command to run the application
CMD ["sh", "-c", "uvicorn main:app --host ${HOST} --port ${PORT}"]
