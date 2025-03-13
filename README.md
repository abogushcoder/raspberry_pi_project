# Raspberry Pi Curse Word Detector

A system that detects spoken curse words using a Raspberry Pi, stores occurrences in a MySQL database, and controls network access for a target device.

## Overview

This system consists of two main components:

1. **Dockerized Application** (runs on primary Raspberry Pi)
   - Speech recognition using Vosk
   - MySQL database for tracking curse words
   - Network control via router API
   - Heartbeat mechanism

2. **Monitoring System** (runs on a secondary device)
   - Continuously checks for heartbeat from primary Pi
   - Blocks target device if primary Pi stops sending signals

## Configuration

All configuration is centralized in the `config.env` file. Edit this file to customize:

- Database credentials
- Network settings (router IP, API paths, credentials)
- Raspberry Pi IPs
- Email notification settings
- List of curse words to detect

## Installation

### On the Primary Raspberry Pi

1. Clone this repository
2. Edit `docker/config.env` to match your environment
3. Build and run the Docker container:

```bash
cd docker
docker-compose up -d
```

### On the Secondary Device (Monitor)

1. Install dependencies:

```bash
pip install requests python-dotenv
```

2. Copy the `config.env` file from primary Pi
3. Set up to run on startup by adding to crontab:

```bash
crontab -e
# Add the line:
@reboot python3 /path/to/monitoring/pi_monitor.py &
```

## Security Features

- Automatically blocks target device if primary Pi is unplugged or stops running
- Requires multiple failures before blocking to prevent false alarms
- Email notifications when blocking occurs

## Customization

You can customize:
- The list of curse words (CURSE_WORDS in config.env)
- Blocking behavior (modify block_device.py script)
- Monitoring interval (HEARTBEAT_INTERVAL in config.env)

## Troubleshooting

- Check logs: `docker-compose logs`
- Test network blocking manually: `python scripts/block_device.py`
- Test network unblocking manually: `python scripts/unblock_device.py`