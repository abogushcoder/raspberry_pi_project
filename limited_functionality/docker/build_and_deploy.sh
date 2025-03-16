#!/bin/bash

# Ensure script is executable
chmod +x setup_database.sh
chmod +x entrypoint.sh
chmod +x scripts/*.py

# Build and start the containers
docker-compose build
docker-compose up -d

echo "Curse word detector is now running!"
echo "To see logs: docker-compose logs -f"
echo "To stop: docker-compose down"