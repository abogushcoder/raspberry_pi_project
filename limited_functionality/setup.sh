#!/bin/bash

# Make sure we're running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

# Update system packages
echo "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install system dependencies
echo "Installing dependencies..."
apt-get install -y python3 python3-pip python3-venv python3-full portaudio19-dev espeak alsa-utils mariadb-server mariadb-client

# Create project directory
PROJECT_DIR="/home/pi/curse_word_detector"
echo "Creating project directory at $PROJECT_DIR..."
mkdir -p $PROJECT_DIR
mkdir -p $PROJECT_DIR/scripts
mkdir -p $PROJECT_DIR/vosk-model

# Create and activate virtual environment
echo "Creating virtual environment..."
VENV_DIR="$PROJECT_DIR/venv"
python3 -m venv $VENV_DIR

# Install Python dependencies in the virtual environment
echo "Installing Python packages..."
$VENV_DIR/bin/pip install --upgrade pip
$VENV_DIR/bin/pip install pyaudio vosk mariadb python-dotenv

# Copy files to project directory
cp config.env $PROJECT_DIR/
cp curse_word_detector.py $PROJECT_DIR/
cp scripts/play_audio.py $PROJECT_DIR/scripts/
cp database_setup.sql $PROJECT_DIR/
cp setup_database.sh $PROJECT_DIR/

# Make scripts executable
chmod +x $PROJECT_DIR/setup_database.sh
chmod +x $PROJECT_DIR/scripts/play_audio.py

# Configure MariaDB
echo "Configuring MariaDB..."
systemctl enable mariadb
systemctl start mariadb

# Create database user and set permissions
echo "Creating database user and configuring database..."
mysql -e "CREATE USER IF NOT EXISTS 'pi_user'@'localhost' IDENTIFIED BY 'yourpassword';"
mysql -e "GRANT ALL PRIVILEGES ON curse_word_db.* TO 'pi_user'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"

# Create systemd service file
echo "Creating systemd service..."
cat > /etc/systemd/system/curse-word-detector.service << EOF
[Unit]
Description=Curse Word Detector Service
After=mariadb.service

[Service]
User=pi
WorkingDirectory=/home/pi/curse_word_detector
ExecStart=/home/pi/curse_word_detector/venv/bin/python /home/pi/curse_word_detector/curse_word_detector.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# Download Vosk model
echo "Downloading Vosk model (if needed)..."
if [ ! -f "$PROJECT_DIR/vosk-model/final.mdl" ]; then
    apt-get install -y wget unzip
    cd $PROJECT_DIR
    wget -q -O vosk-model.zip https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    unzip -q vosk-model.zip
    mv vosk-model-small-en-us-0.15/* vosk-model/
    rm -rf vosk-model-small-en-us-0.15 vosk-model.zip
    echo "Vosk model downloaded and extracted"
fi

# Run database setup script
echo "Setting up database..."
cd $PROJECT_DIR
./setup_database.sh

# Enable and start service
systemctl enable curse-word-detector.service

echo "Setup complete!"
echo "Next steps:"
echo "1. Review /home/pi/curse_word_detector/config.env and update the curse words list."
echo "2. Start the service with: sudo systemctl start curse-word-detector.service"
echo "3. Check status with: sudo systemctl status curse-word-detector.service"