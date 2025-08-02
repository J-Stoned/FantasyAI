#!/usr/bin/env python3
"""
Download and setup ngrok for Yahoo OAuth
"""

import os
import sys
import zipfile
import requests
import platform
from pathlib import Path

def download_ngrok():
    """Download ngrok for Windows"""
    print("Downloading ngrok...")
    
    # Determine the correct download URL for Windows
    system = platform.system()
    machine = platform.machine()
    
    if system == "Windows":
        if machine == "AMD64" or machine == "x86_64":
            url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
        else:
            url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-386.zip"
    else:
        print(f"Unsupported system: {system}")
        return False
    
    # Download the file
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Save to current directory
        zip_path = Path("ngrok.zip")
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded ngrok.zip ({zip_path.stat().st_size / 1024 / 1024:.1f} MB)")
        
        # Extract ngrok.exe
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall('.')
        
        # Clean up zip file
        zip_path.unlink()
        
        print("[OK] ngrok.exe extracted successfully!")
        return True
        
    except Exception as e:
        print(f"Error downloading ngrok: {e}")
        return False

def create_ngrok_config():
    """Create ngrok configuration file"""
    config_content = """version: "2"
authtoken: # Add your authtoken here if you have one
tunnels:
  fantasy-ai:
    proto: http
    addr: 8000
    schemes: ["https"]
"""
    
    config_path = Path("ngrok.yml")
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print("✓ Created ngrok.yml configuration file")

def create_start_scripts():
    """Create convenient start scripts"""
    
    # Batch script for Windows
    batch_content = """@echo off
echo Starting ngrok tunnel for Fantasy AI OAuth...
echo.
echo After ngrok starts:
echo 1. Copy the HTTPS URL (like https://abc123.ngrok-free.app)
echo 2. Update your .env file with the new redirect URI
echo 3. Update your Yahoo app settings with the same URI
echo.
ngrok http 8000
"""
    
    with open("start_ngrok.bat", 'w') as f:
        f.write(batch_content)
    
    print("✓ Created start_ngrok.bat")
    
    # Python script to automate the process
    python_content = '''#!/usr/bin/env python3
"""
Start ngrok and help update configuration
"""

import subprocess
import time
import requests
import json
import re

def get_ngrok_url():
    """Get the public URL from ngrok API"""
    try:
        # ngrok exposes a local API
        response = requests.get('http://localhost:4040/api/tunnels')
        data = response.json()
        
        for tunnel in data.get('tunnels', []):
            if tunnel.get('proto') == 'https':
                return tunnel.get('public_url')
    except:
        return None
    return None

def update_env_file(ngrok_url):
    """Update .env file with new ngrok URL"""
    redirect_uri = f"{ngrok_url}/auth/callback"
    
    # Read current .env
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    # Update YAHOO_REDIRECT_URI
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('YAHOO_REDIRECT_URI='):
            lines[i] = f'YAHOO_REDIRECT_URI={redirect_uri}\\n'
            updated = True
            break
    
    if not updated:
        lines.append(f'\\nYAHOO_REDIRECT_URI={redirect_uri}\\n')
    
    # Write back
    with open('.env', 'w') as f:
        f.writelines(lines)
    
    return redirect_uri

def main():
    print("Starting ngrok tunnel...")
    
    # Start ngrok in background
    process = subprocess.Popen(['ngrok', 'http', '8000'])
    
    # Wait for ngrok to start
    print("Waiting for ngrok to initialize...")
    time.sleep(3)
    
    # Get the public URL
    url = get_ngrok_url()
    if url:
        print(f"\\n✓ Ngrok tunnel established!")
        print(f"  Public URL: {url}")
        
        # Update .env file
        redirect_uri = update_env_file(url)
        print(f"\\n✓ Updated .env file with new redirect URI:")
        print(f"  {redirect_uri}")
        
        print(f"\\n📋 Next Steps:")
        print(f"1. Go to Yahoo Developer Console: https://developer.yahoo.com/apps/")
        print(f"2. Update your app's redirect URI to: {redirect_uri}")
        print(f"3. Save the changes in Yahoo")
        print(f"4. Restart your FastAPI server")
        print(f"5. Try the OAuth flow again")
        
        print(f"\\nPress Ctrl+C to stop ngrok")
        
        try:
            process.wait()
        except KeyboardInterrupt:
            process.terminate()
            print("\\nNgrok stopped.")
    else:
        print("❌ Could not get ngrok URL. Please check if ngrok started correctly.")
        print("   You can also run 'ngrok http 8000' manually.")

if __name__ == "__main__":
    main()
'''
    
    with open("start_ngrok_auto.py", 'w') as f:
        f.write(python_content)
    
    print("✓ Created start_ngrok_auto.py (automated setup)")

def main():
    """Main setup function"""
    print("=== Ngrok Setup for Yahoo OAuth ===\n")
    
    # Check if ngrok already exists
    if Path("ngrok.exe").exists():
        print("✓ ngrok.exe already exists")
    else:
        print("Downloading ngrok...")
        if not download_ngrok():
            print("\n❌ Failed to download ngrok.")
            print("Please download manually from: https://ngrok.com/download")
            return
    
    # Create configuration
    create_ngrok_config()
    
    # Create start scripts
    create_start_scripts()
    
    print("\n=== Setup Complete! ===")
    print("\nTo use ngrok with Yahoo OAuth:")
    print("\n1. First, start your FastAPI server:")
    print("   python scripts/start.py")
    print("\n2. Then, in another terminal, run:")
    print("   .\\start_ngrok.bat")
    print("   OR")
    print("   python start_ngrok_auto.py  (for automated setup)")
    print("\n3. Follow the instructions shown by the script")
    
    # Test if ngrok works
    print("\nTesting ngrok...")
    result = os.system("ngrok.exe version")
    if result == 0:
        print("✓ ngrok is ready to use!")
    else:
        print("❌ Could not run ngrok. You may need to add it to PATH.")

if __name__ == "__main__":
    main()