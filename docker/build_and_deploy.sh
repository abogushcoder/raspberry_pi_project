#!/bin/bash

# Make sure we're in the docker directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Ask for Docker Hub username
echo "Enter your Docker Hub username (or leave blank to skip Docker Hub push):"
read -r docker_username

# Build for ARM
echo "Building Docker image for Raspberry Pi (ARM)..."
docker buildx build --platform linux/arm/v7 -t curse-word-detector .

# Optionally tag and push to Docker Hub
if [ -n "$docker_username" ]; then
    echo "Tagging image..."
    docker tag curse-word-detector "$docker_username/curse-word-detector:latest"
    
    echo "Pushing to Docker Hub..."
    docker push "$docker_username/curse-word-detector:latest"
    
    # Update docker-compose.yml with user's Docker Hub username
    sed -i "s/your-dockerhub-username/$docker_username/g" docker-compose.yml
    
    echo "Image pushed to Docker Hub as $docker_username/curse-word-detector:latest"
    echo "docker-compose.yml updated with your username"
fi

echo "Build complete!"
echo "To deploy to Raspberry Pi, run: docker-compose up -d"