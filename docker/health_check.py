import os
import time
import threading
from flask import Flask, jsonify
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration from environment variables
monitor_ip = os.getenv("MONITOR_IP", "192.168.1.2")
monitor_port = os.getenv("MONITOR_PORT", "5000")
heartbeat_interval = int(os.getenv("HEARTBEAT_INTERVAL", "30"))
flask_port = int(os.getenv("FLASK_PORT", "5000"))

# Status tracking
last_heartbeat = time.time()
app = Flask(__name__)

@app.route('/heartbeat', methods=['POST'])
def receive_heartbeat():
    """Endpoint to receive heartbeats from the monitor"""
    global last_heartbeat
    last_heartbeat = time.time()
    return jsonify({"status": "ok", "timestamp": last_heartbeat})

@app.route('/check', methods=['GET'])
def check_status():
    """Endpoint to check if Pi is still sending heartbeats"""
    global last_heartbeat
    time_since_last = time.time() - last_heartbeat
    
    if time_since_last > heartbeat_interval * 2:
        return jsonify({
            "status": "Pi Disconnected", 
            "last_heartbeat": last_heartbeat,
            "seconds_ago": time_since_last
        })
    else:
        return jsonify({
            "status": "Pi Active", 
            "last_heartbeat": last_heartbeat,
            "seconds_ago": time_since_last
        })

def send_heartbeats():
    """Thread function to send heartbeats"""
    heartbeat_url = f"http://{monitor_ip}:{monitor_port}/heartbeat"
    
    while True:
        try:
            response = requests.post(heartbeat_url)
            print(f"Heartbeat sent: {response.status_code}")
        except Exception as e:
            print("Failed to send heartbeat:", e)
        time.sleep(heartbeat_interval)

if __name__ == "__main__":
    # Start heartbeat sender in a separate thread
    heartbeat_thread = threading.Thread(target=send_heartbeats, daemon=True)
    heartbeat_thread.start()
    
    # Start Flask server
    print(f"Starting health check service on port {flask_port}")
    app.run(host='0.0.0.0', port=flask_port)