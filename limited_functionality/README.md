# Raspberry Pi Curse Word Detector (Limited Functionality)

This is a simplified version of the curse word detector that focuses on:
- Detecting curse words using speech recognition
- Keeping a tally of each specific curse word in a database
- Providing audio announcements when curse words are detected
- Providing special announcements on the 1st and 3rd occurrences

## Features

- **Speech Recognition**: Uses Vosk for offline speech-to-text processing
- **Word Tracking**: Tracks each curse word individually in a MySQL database
- **Smart Notifications**: Uses modulo operator to announce on the 1st and every 3rd occurrence
- **Docker Containerized**: Easy setup and deployment with Docker

## Requirements

- Raspberry Pi (3 or 4 recommended)
- Microphone
- Speaker connected to the Pi
- Internet connection (only needed for initial setup)

## Quick Start

1. Clone this repository to your Raspberry Pi
2. Run the setup script:
   ```bash
   cd limited_functionality
   sudo ./setup.sh
   ```
3. Edit the configuration file to customize curse words:
   ```bash
   nano docker/config.env
   ```
4. Build and run the Docker container:
   ```bash
   cd docker
   ./build_and_deploy.sh
   ```

## Configuration

Edit the `docker/config.env` file to customize:

- **Curse Words**: Update the `CURSE_WORDS` variable with your comma-separated list of words to detect
- **Audio Messages**: Customize the warning messages with `FIRST_CURSE_WARNING` and `THIRD_CURSE_WARNING`
- **Audio Settings**: Adjust volume with `AUDIO_VOLUME` (0-100)

## Docker Container Management

- **View logs**:
  ```bash
  cd docker
  docker-compose logs -f
  ```

- **Stop the service**:
  ```bash
  cd docker
  docker-compose down
  ```

- **Restart the service**:
  ```bash
  cd docker
  docker-compose restart
  ```

## Database Access

You can connect to the MySQL database to view curse word statistics:

```bash
cd docker
docker-compose exec db mysql -u pi_user -pyourpassword curse_word_db
```

Then run SQL queries like:
```sql
SELECT * FROM word_counts ORDER BY count DESC;
```

## Troubleshooting

- **No audio output**: Ensure your speaker is connected and working with `aplay /usr/share/sounds/alsa/Front_Center.wav`
- **Microphone issues**: Check if your microphone is detected with `arecord -l`
- **Container not starting**: Check logs with `docker-compose logs -f`