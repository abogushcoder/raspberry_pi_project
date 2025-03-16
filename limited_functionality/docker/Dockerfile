# Use an ARM-compatible Python base image for Raspberry Pi
FROM arm32v7/python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    mysql-client \
    espeak \
    alsa-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy all necessary files
COPY requirements.txt .
COPY config.env .
COPY *.py .
COPY scripts/ ./scripts/
COPY database_setup.sql .
COPY setup_database.sh .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make scripts executable
RUN chmod +x setup_database.sh
RUN chmod +x scripts/*.py

# Create directory for Vosk model
RUN mkdir -p vosk-model

# Set up entrypoint script
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Use entrypoint script to handle startup tasks
ENTRYPOINT ["/app/entrypoint.sh"]