#!/bin/bash

# Make sure we're in the monitoring directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if config.env exists
if [ ! -f "config.env" ]; then
    if [ -f "../docker/config.env" ]; then
        echo "Copying config.env from docker directory..."
        cp "../docker/config.env" .
    else
        echo "Error: config.env not found. Please create it manually."
        exit 1
    fi
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set up crontab entry for automatic startup
echo "Would you like to set up automatic startup on boot? (y/n)"
read -r setup_crontab

if [ "$setup_crontab" == "y" ] || [ "$setup_crontab" == "Y" ]; then
    MONITOR_PATH="$SCRIPT_DIR/pi_monitor.py"
    
    # Check if entry already exists
    if crontab -l 2>/dev/null | grep -q "$MONITOR_PATH"; then
        echo "Crontab entry already exists"
    else
        # Add new crontab entry
        (crontab -l 2>/dev/null; echo "@reboot python3 $MONITOR_PATH &") | crontab -
        echo "Added crontab entry to start monitor on boot"
    fi
fi

echo "Setup complete!"
echo "To start the monitor manually, run: python3 pi_monitor.py"