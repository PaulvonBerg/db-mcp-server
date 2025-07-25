# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Using --no-cache-dir makes the image smaller
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code to the working directory
COPY . .

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Set the transport mode for the production environment
ENV MCP_TRANSPORT_MODE="streamable"

# Run the main.py application with uvicorn.
# Uvicorn will listen on the port specified by the $PORT environment variable,
# defaulting to 8080 if it's not set.
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
