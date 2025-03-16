#!/usr/bin/env python3
"""
UniFi CloudKey+ Integration: Device Unblocking Tool

This script unblocks network access for a device by its MAC address using the UniFi CloudKey+ API.
It authenticates with the UniFi Controller, obtains a session cookie and CSRF token,
then sends an unblock-sta command to the station manager API.

Usage:
    python unblock_device.py [mac_address]
    
    If mac_address is not provided, it will be read from the CHILD_DEVICE_MAC environment variable.
"""

import requests
import os
import sys
from pathlib import Path
import dotenv

# Try to find and load the config.env file
def load_environment():
    # Check for config.env in the current directory
    local_env = Path("config.env")
    if local_env.exists():
        dotenv.load_dotenv(local_env)
        return True
    
    # Check for config.env in the docker directory
    docker_env = Path("../config.env")
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

# Configuration from environment variables
controller_host = os.getenv("UNIFI_CONTROLLER", "unifi.example.com")
username = os.getenv("UNIFI_USERNAME", "admin")
password = os.getenv("UNIFI_PASSWORD", "yourpassword")
site = os.getenv("UNIFI_SITE", "default")
device_mac = os.getenv("CHILD_DEVICE_MAC", "AA:BB:CC:DD:EE:FF")
ssl_verify = os.getenv("UNIFI_SSL_VERIFY", "true").lower() == "true"

# Accept an optional MAC address as command-line argument
if len(sys.argv) > 1:
    device_mac = sys.argv[1]

session = requests.Session()
session.headers.update(
    {"Content-Type": "application/json", "Accept": "application/json"})
# Verify SSL certificates (can be disabled via environment variable, but not recommended)
session.verify = ssl_verify

# 1. Log in to UniFi controller
login_url = f"https://{controller_host}/api/auth/login"
credentials = {"username": username, "password": password}
try:
    resp = session.post(login_url, json=credentials, timeout=10)
    resp.raise_for_status()
except requests.exceptions.RequestException as err:
    print(f"Failed to connect or authenticate: {err}")
    exit(1)

if resp.status_code != 200 or resp.json().get("meta", {}).get("rc") == "error":
    msg = resp.json().get("meta", {}).get("msg", "") if resp.headers.get(
        "Content-Type", "").startswith("application/json") else resp.text
    print(f"Login failed. Server response: {msg or resp.status_code}")
    exit(1)

csrf_token = resp.headers.get("X-CSRF-Token")
if csrf_token:
    session.headers.update({"X-CSRF-Token": csrf_token})

# 2. Unblock the device
unblock_url = f"https://{controller_host}/proxy/network/api/s/{site}/cmd/stamgr"
payload = {"cmd": "unblock-sta", "mac": device_mac.lower()}
try:
    resp = session.post(unblock_url, json=payload, timeout=10)
    resp.raise_for_status()
except requests.exceptions.Timeout:
    print("Error: Request to unblock device timed out")
    exit(1)
except requests.exceptions.HTTPError as http_err:
    print(f"Error: Unblock request HTTP {
          http_err.response.status_code} - {http_err.response.text}")
    exit(1)
except requests.exceptions.RequestException as err:
    print(f"Error: Failed to send unblock request - {err}")
    exit(1)

result = resp.json()
if result.get("meta", {}).get("rc") == "ok":
    print(f"Device {device_mac} has been *unblocked* successfully.")
else:
    error_message = result.get("meta", {}).get("msg", "Unknown error")
    print(f"Failed to unblock device {
          device_mac}. Controller error: {error_message}")

session.post(f"https://{controller_host}/proxy/network/api/logout", timeout=5)
