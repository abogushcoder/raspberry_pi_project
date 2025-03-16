#!/bin/bash

# Make sure we're running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo "Docker not found, installing..."
    curl -sSL https://get.docker.com | sh
    usermod -aG docker $USER
    echo "Docker installed. You may need to log out and back in for group changes to take effect."
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose not found, installing..."
    apt-get update
    apt-get install -y docker-compose
fi

# Install audio dependencies
echo "Installing audio dependencies..."
apt-get update
apt-get install -y portaudio19-dev espeak alsa-utils

# Make the build script executable
cd docker
chmod +x build_and_deploy.sh

echo "Setup complete!"
echo "Next steps:"
echo "1. Review docker/config.env and update the curse words list."
echo "2. Run docker/build_and_deploy.sh to build and start the containers."