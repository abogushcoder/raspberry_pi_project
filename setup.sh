#!/bin/bash

echo "================================"
echo "Raspberry Pi Curse Word Detector"
echo "================================"
echo

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "This script will help you set up the Raspberry Pi Curse Word Detector system."
echo "What would you like to set up?"
echo "1. Primary Raspberry Pi (Docker container with curse word detection)"
echo "2. Secondary Device (Monitoring system)"
echo "3. Both"
echo
echo "Enter your choice (1-3):"
read -r choice

case $choice in
    1)
        echo "Setting up Primary Raspberry Pi..."
        cd "$SCRIPT_DIR/docker"
        ./build_and_deploy.sh
        ;;
    2)
        echo "Setting up Secondary Device (Monitoring system)..."
        cd "$SCRIPT_DIR/monitoring"
        ./setup.sh
        ;;
    3)
        echo "Setting up both systems..."
        echo "First, let's set up the Primary Raspberry Pi"
        cd "$SCRIPT_DIR/docker"
        ./build_and_deploy.sh
        
        echo "Now, let's set up the Secondary Device (Monitoring system)"
        cd "$SCRIPT_DIR/monitoring"
        ./setup.sh
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo
echo "Setup complete! See README.md for additional configuration instructions."