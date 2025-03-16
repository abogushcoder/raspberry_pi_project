#!/bin/bash
set -e

# Source the environment variables
source /app/config.env

# Wait for MySQL to be ready
echo "Waiting for MySQL server to be available..."
max_attempts=30
counter=0
while ! mysql -h "$MYSQL_HOST" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SELECT 1" >/dev/null 2>&1; do
    counter=$((counter+1))
    if [ $counter -ge $max_attempts ]; then
        echo "Error: MySQL server not available after $max_attempts attempts"
        exit 1
    fi
    echo "MySQL not ready yet. Waiting..."
    sleep 2
done

# Run database setup script
echo "Setting up database..."
./setup_database.sh

# Check if Vosk model is present, download if not
if [ ! -f "vosk-model/final.mdl" ]; then
    echo "Vosk model not found, downloading..."
    apt-get update && apt-get install -y wget unzip
    wget -q -O vosk-model.zip https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    unzip -q vosk-model.zip
    mv vosk-model-small-en-us-0.15/* vosk-model/
    rm -rf vosk-model-small-en-us-0.15 vosk-model.zip
    echo "Vosk model downloaded and extracted"
fi

# Start the curse word detector
echo "Starting curse word detector..."
python3 curse_word_detector.py