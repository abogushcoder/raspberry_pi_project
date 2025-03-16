import requests
import time
import smtplib
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def send_alert():
    """ Send email notification to parent """
    email = os.getenv("EMAIL_ADDRESS", "your-email@example.com")
    password = os.getenv("EMAIL_PASSWORD", "your-email-password")
    to_email = os.getenv("TO_EMAIL", "parent-email@example.com")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email, password)
            msg = "Subject: Alert! Raspberry Pi Disconnected\n\nThe Raspberry Pi has stopped sending heartbeats. Child's device is now permanently blocked."
            server.sendmail(email, to_email, msg)
            print("Alert email sent!")
    except Exception as e:
        print("Failed to send email:", e)


def block_child_device():
    """ Permanently block the child's device from the network """
    from block_device import block_device
    
    success = block_device()
    if success:
        print("Child's device permanently blocked!")
    else:
        print("Failed to block child's device")


def check_heartbeat():
    """ Check if the heartbeat server is responding """
    monitor_ip = os.getenv("MONITOR_IP", "192.168.1.2")
    monitor_port = os.getenv("MONITOR_PORT", "5000")
    
    url = f"http://{monitor_ip}:{monitor_port}/check"
    
    try:
        response = requests.get(url)
        return "Pi Disconnected" not in response.text
    except Exception as e:
        print("Failed to check status:", e)
        return False


if __name__ == "__main__":
    heartbeat_interval = int(os.getenv("HEARTBEAT_INTERVAL", "30"))
    
    print(f"Starting monitor service, checking heartbeat every {heartbeat_interval} seconds")
    
    while True:
        if not check_heartbeat():
            print("Heartbeat not detected! Sending alert and blocking device.")
            send_alert()
            block_child_device()
            break
        
        time.sleep(heartbeat_interval)