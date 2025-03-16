# Raspberry Pi Curse Word Detector (Limited Functionality)

This is a simplified version of the curse word detector that focuses on:
- Detecting curse words using speech recognition
- Keeping a tally of each specific curse word in a database
- Providing audio announcements when curse words are detected
- Providing special announcements on the 1st and 3rd occurrences

## Features

- **Speech Recognition**: Uses Vosk for offline speech-to-text processing
- **Word Tracking**: Tracks each curse word individually in a MariaDB database
- **Smart Notifications**: Uses modulo operator to announce on the 1st and every 3rd occurrence

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
   nano config.env
   ```
4. Start the service:
   ```bash
   sudo systemctl start curse-word-detector.service
   ```

## Configuration

Edit the `config.env` file to customize:

- **Curse Words**: Update the `CURSE_WORDS` variable with your comma-separated list of words to detect
- **Audio Messages**: Customize the warning messages with `FIRST_CURSE_WARNING` and `THIRD_CURSE_WARNING`
- **Audio Settings**: Adjust volume with `AUDIO_VOLUME` (0-100)

## Service Management

- **View logs**:
  ```bash
  sudo journalctl -u curse-word-detector.service -f
  ```

- **Stop the service**:
  ```bash
  sudo systemctl stop curse-word-detector.service
  ```

- **Restart the service**:
  ```bash
  sudo systemctl restart curse-word-detector.service
  ```

## Database Access

You can connect to the MariaDB database to view curse word statistics:

```bash
mysql -u pi_user -pyourpassword curse_word_db
```

Then run SQL queries like:
```sql
SELECT * FROM word_counts ORDER BY count DESC;
```

## Troubleshooting

- **No audio output**: Ensure your speaker is connected and working with `aplay /usr/share/sounds/alsa/Front_Center.wav`
- **Microphone issues**: Check if your microphone is detected with `arecord -l`
- **Service not starting**: Check logs with `sudo journalctl -u curse-word-detector.service -e`