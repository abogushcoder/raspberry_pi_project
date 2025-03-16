from play_audio import play_message
import sys
import pyaudio
import mysql.connector
import json
import os
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
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

# Audio playback function for curse word warnings


def play_curse_warning(count, word):
    try:
        # Get custom message based on count
        if count % 3 == 1:  # First occurrence using modulo
            custom_message = os.getenv(
                "FIRST_CURSE_WARNING", f"You said a bad word: {word}")
            play_message(custom_message)
        elif count % 3 == 0:  # Third occurrence using modulo
            custom_message = os.getenv(
                "THIRD_CURSE_WARNING", f"Warning! You have said bad words 3 times!")
            play_message(custom_message)
    except Exception as e:
        print(f"Failed to play warning audio: {e}")


# Audio input setup
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1,
                rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()

print("Curse word detector started. Listening for words...")

while True:
    data = stream.read(4000, exception_on_overflow=False)
    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        text = result.get("text", "").lower()

        # Check each word in the transcript
        words = text.split()
        for word in words:
            if word in curse_words:
                print(f"Detected curse word: {word}")

                # Get current count for this specific word
                cursor.execute(
                    "SELECT count FROM word_counts WHERE word = %s", (word,))
                result = cursor.fetchone()

                if result:
                    current_count = result[0] + 1  # Add 1 for this occurrence

                    # Update the count in the database
                    cursor.execute("UPDATE word_counts SET count = %s WHERE word = %s",
                                   (current_count, word))
                    db.commit()

                    print(f"Updated count for '{word}' to {current_count}")

                    # Play appropriate warning based on count
                    warning_thread = threading.Thread(
                        target=play_curse_warning,
                        args=(current_count, word)
                    )
                    warning_thread.start()
