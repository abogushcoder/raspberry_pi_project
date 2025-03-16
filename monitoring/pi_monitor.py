import os
import time
import requests
import subprocess
import sys
import threading
from pathlib import Path
from flask import Flask, jsonify
import dotenv


# Try to find and load the config.env file
def load_environment():
    # Check for config.env in the current directory
    local_env = Path("config.env")
    if local_env.exists():
        dotenv.load_dotenv(local_env)
        return True
    
    # Check for config.env in the docker directory
    docker_env = Path("../docker/config.env")
    if docker_env.exists():
        dotenv.load_dotenv(docker_env)
        return True
    
    # Check one more level up
    root_env = Path("../../docker/config.env")
    if root_env.exists():
        dotenv.load_dotenv(root_env)
        return True
    
    return False


# Make a best effort to load environment variables
if not load_environment():
    print("Warning: Could not find config.env file. Using default values.")


# Get configuration
PI_IP = os.getenv("PI_IP", "192.168.1.50")
ROUTER_IP = os.getenv("ROUTER_IP", "192.168.1.1")
ROUTER_API_PATH_BLOCK = os.getenv("ROUTER_API_PATH_BLOCK", "/api/block_device")
CHILD_DEVICE_IP = os.getenv("CHILD_DEVICE_IP", "192.168.1.100")
ROUTER_USERNAME = os.getenv("ROUTER_USERNAME", "admin")
ROUTER_PASSWORD = os.getenv("ROUTER_PASSWORD", "password")
HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", "30"))
MONITOR_PORT = int(os.getenv("MONITOR_PORT", "5000"))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "your-email@example.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your-email-password")
TO_EMAIL = os.getenv("TO_EMAIL", "parent-email@example.com")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))


# Create Flask app
app = Flask(__name__)
last_heartbeat = time.time()
pi_status = "online"  # Track overall Pi status


def ping(host):
    """
    Returns True if host responds to a ping request
    """
    # Check OS and use appropriate ping command
    if sys.platform.lower() == "win32":
        ping_cmd = ["ping", "-n", "1", host]
    else:
        ping_cmd = ["ping", "-c", "1", host]
    
    try:
        return subprocess.call(ping_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    except Exception as e:
        print(f"Error pinging {host}: {e}")
        return False


def block_device():
    """
    Blocks the target device by calling the block_device.py script
    """
    # Get the directory of this script
    current_dir = Path(__file__).parent.absolute()
    
    # Find the block_device.py script
    script_paths = [
        current_dir / "block_device.py",
        current_dir / "../docker/scripts/block_device.py",
        Path("/app/scripts/block_device.py")  # For Docker environment
    ]
    
    script_path = None
    for path in script_paths:
        if path.exists():
            script_path = path
            break
    
    if not script_path:
        print("Error: Could not find block_device.py script")
        return False
    
    try:
        # Run the block_device.py script
        child_mac = os.getenv("CHILD_DEVICE_MAC", "")
        cmd = [sys.executable, str(script_path)]
        if child_mac:
            cmd.append(child_mac)
            
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print(f"Device blocked successfully: {result.stdout.strip()}")
            return True
        else:
            print(f"Failed to block device: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"Failed to execute block_device.py: {e}")
        return False


def send_alert():
    """
    Send email notification about Pi being offline
    """
    import smtplib
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            msg = "Subject: Alert! Raspberry Pi Disconnected\n\nThe Raspberry Pi has stopped sending heartbeats. Child's device is now permanently blocked."
            server.sendmail(EMAIL_ADDRESS, TO_EMAIL, msg)
            print("Alert email sent!")
            return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    """
    Endpoint to receive heartbeats from the Pi
    """
    global last_heartbeat, pi_status
    last_heartbeat = time.time()
    pi_status = "online"
    return jsonify({"status": "ok", "timestamp": last_heartbeat})


@app.route('/status', methods=['GET'])
def status():
    """
    Endpoint to check Pi status
    """
    global last_heartbeat, pi_status
    
    time_since_last = time.time() - last_heartbeat
    timeout = HEARTBEAT_INTERVAL * 2
    
    return jsonify({
        "pi_status": pi_status,
        "last_heartbeat": last_heartbeat,
        "seconds_ago": time_since_last,
        "timeout_seconds": timeout
    })


def monitor_thread():
    """
    Background thread to monitor Pi status
    """
    global pi_status
    consecutive_failures = 0
    max_failures = 3
    
    while True:
        # Check time since last heartbeat
        time_since_last = time.time() - last_heartbeat
        
        # If heartbeat timeout or ping failed
        if time_since_last > HEARTBEAT_INTERVAL * 2 or not ping(PI_IP):
            consecutive_failures += 1
            print(f"Pi connection issue detected. Failure {consecutive_failures}/{max_failures}")
            
            if consecutive_failures >= max_failures and pi_status != "offline":
                print("Pi confirmed offline. Taking action...")
                pi_status = "offline"
                
                # Block device
                if block_device():
                    print("Child device blocked successfully")
                else:
                    print("Failed to block child device")
                
                # Send alert
                send_alert()
        else:
            if consecutive_failures > 0:
                print("Pi connection restored")
            consecutive_failures = 0
            pi_status = "online"
        
        time.sleep(HEARTBEAT_INTERVAL)


if __name__ == "__main__":
    print(f"Starting Pi Monitor")
    print(f"Monitoring Pi at {PI_IP}")
    print(f"Protected device: {CHILD_DEVICE_IP}")
    print(f"Starting server on port {MONITOR_PORT}")
    
    # Start monitoring thread
    monitor = threading.Thread(target=monitor_thread, daemon=True)
    monitor.start()
    
    # Start Flask server
    app.run(host='0.0.0.0', port=MONITOR_PORT)