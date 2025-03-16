import pyaudio
import mysql.connector
import json
import os
import time
import subprocess
import threading
from vosk import Model, KaldiRecognizer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load Vosk Model
model_path = os.getenv("VOSK_MODEL_PATH", "vosk-model")
model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

# Connect to local MySQL database
db = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "localhost"),
    user=os.getenv("MYSQL_USER", "pi_user"),
    password=os.getenv("MYSQL_PASSWORD", "yourpassword"),
    database=os.getenv("MYSQL_DATABASE", "curse_word_db")
)
cursor = db.cursor()

# List of curse words
curse_words_str = os.getenv("CURSE_WORDS", "curse1,curse2,curse3")
curse_words = [word.strip() for word in curse_words_str.split(",")]

# Import the scripts from the scripts directory
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
from block_device import block_device as block
from play_audio import play_message

# Function to call block_device.py script
def block_device():
    try:
        # Execute blocking
        success = block()
        print(f"Device blocking {'succeeded' if success else 'failed'}")
        return success
    except Exception as e:
        print(f"Error blocking device: {e}")
        return False

# Audio playback function for the warning message
def play_warning_audio():
    try:
        # Get custom message from environment or use default
        custom_message = os.getenv("CURSE_WORD_WARNING", "You have said a bad word")
        play_message(custom_message)
    except Exception as e:
        print(f"Failed to play warning audio: {e}")

# Audio input setup
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()

while True:
    data = stream.read(4000, exception_on_overflow=False)
    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        detected_word = result.get("text", "").lower()
        
        if any(curse in detected_word for curse in curse_words):
            print(f"Detected curse word: {detected_word}")
            cursor.execute("UPDATE word_counts SET count = count + 1 WHERE word = %s", (detected_word,))
            db.commit()
            
            # Block the device when curse word detected
            blocking_thread = threading.Thread(target=block_device)
            blocking_thread.start()
            
            # Play warning message through speakers
            play_warning_thread = threading.Thread(target=play_warning_audio)
            play_warning_thread.start()
        else:
            print("No curse word detected.")