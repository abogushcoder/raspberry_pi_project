import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def block_device(ip_address=None):
    # Get configuration from environment
    router_ip = os.getenv("ROUTER_IP", "192.168.1.1")
    api_path = os.getenv("ROUTER_API_PATH_BLOCK", "/api/block_device")
    router_username = os.getenv("ROUTER_USERNAME", "admin")
    router_password = os.getenv("ROUTER_PASSWORD", "password")
    
    # If no IP provided, use the configured child device IP
    if ip_address is None:
        ip_address = os.getenv("CHILD_DEVICE_IP", "192.168.1.100")
    
    # Build the URL
    router_url = f"http://{router_ip}{api_path}"
    
    # Create payload
    payload = {"ip": ip_address}
    
    try:
        response = requests.post(
            router_url, 
            auth=(router_username, router_password), 
            data=payload
        )
        print(f"Blocked {ip_address}: Status {response.status_code}")
        return True
    except Exception as e:
        print(f"Failed to block device: {e}")
        return False


if __name__ == "__main__":
    block_device()