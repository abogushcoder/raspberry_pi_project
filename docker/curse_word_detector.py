import pyaudio
import mysql.connector
import json
import os
import time
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
        else:
            print("No curse word detected.")