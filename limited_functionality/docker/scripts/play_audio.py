#!/usr/bin/env python3
"""
Audio playback utility for the Raspberry Pi curse word detector.
This script provides functionality to play spoken messages when curse words are detected.
"""

import os
import subprocess
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration
AUDIO_ENABLED = os.getenv("AUDIO_ENABLED", "true").lower() == "true"
AUDIO_VOLUME = int(os.getenv("AUDIO_VOLUME", "80"))  # 0-100
DEFAULT_MESSAGE = os.getenv("AUDIO_MESSAGE", "You have said a bad word")


def set_volume(volume_percent):
    """Set the system volume level"""
    if 0 <= volume_percent <= 100:
        try:
            subprocess.run(["amixer", "sset", "Master", f"{volume_percent}%"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            print(f"Failed to set volume: {e}")
            return False
    else:
        print("Volume must be between 0 and 100")
        return False


def play_message(message=None, voice="en+f3", speed=150, pitch=50):
    """
    Play a spoken message using espeak text-to-speech
    
    Args:
        message: Text message to speak (defaults to DEFAULT_MESSAGE)
        voice: Voice to use (default is female English voice)
        speed: Speaking speed (default 150 words per minute)
        pitch: Voice pitch (0-100, default 50)
    
    Returns:
        Boolean indicating success
    """
    if not AUDIO_ENABLED:
        print("Audio playback is disabled")
        return False
    
    # Use default message if none provided
    if message is None:
        message = DEFAULT_MESSAGE
    
    try:
        # Set volume first
        set_volume(AUDIO_VOLUME)
        
        # Use espeak for text-to-speech
        subprocess.run(["espeak", f"-v{voice}", f"-p{pitch}", f"-s{speed}", message])
        print(f"Played audio message: '{message}'")
        return True
    except Exception as e:
        print(f"Failed to play audio message: {e}")
        return False


if __name__ == "__main__":
    # When run directly, play the default message
    play_message()