#!/usr/bin/env python3
"""
Simple OAuth setup helper
"""

import subprocess
import time
import os
import webbrowser

print("=== Yahoo OAuth Setup with Ngrok ===\n")

# Kill existing processes
print("Stopping any existing servers...")
os.system("taskkill /F /IM python.exe 2>nul")
time.sleep(2)

# Start server
print("\nStarting FastAPI server...")
server_process = subprocess.Popen(["python", "scripts/start.py"])
time.sleep(5)

# Start ngrok
print("\nStarting ngrok tunnel...\n")
print("="*70)
print("IMPORTANT: When ngrok starts:")
print("1. Look for the HTTPS URL (like https://abc123.ngrok-free.app)")
print("2. Copy that URL")
print("3. You'll need to update Yahoo Developer Console with:")
print("   https://abc123.ngrok-free.app/auth/callback")
print("="*70)
print("\nStarting ngrok now...\n")

# Run ngrok in the foreground so user can see the URL
try:
    subprocess.run(["ngrok.exe", "http", "8000"])
except KeyboardInterrupt:
    print("\nShutting down...")
    server_process.terminate()
    print("Done!")