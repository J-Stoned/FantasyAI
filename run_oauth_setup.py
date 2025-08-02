#!/usr/bin/env python3
"""
Run server and ngrok for OAuth setup
"""

import subprocess
import time
import threading
import requests
import os
import sys

def start_server():
    """Start the FastAPI server"""
    print("Starting FastAPI server on port 8000...")
    subprocess.run([sys.executable, "scripts/start.py"])

def get_ngrok_url():
    """Get the public URL from ngrok API"""
    try:
        response = requests.get('http://localhost:4040/api/tunnels')
        data = response.json()
        
        for tunnel in data.get('tunnels', []):
            if tunnel.get('proto') == 'https':
                return tunnel.get('public_url')
    except:
        pass
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
            lines[i] = f'YAHOO_REDIRECT_URI={redirect_uri}\n'
            updated = True
            break
    
    if not updated:
        lines.append(f'\nYAHOO_REDIRECT_URI={redirect_uri}\n')
    
    # Write back
    with open('.env', 'w') as f:
        f.writelines(lines)
    
    print(f"[OK] Updated .env file with: {redirect_uri}")
    return redirect_uri

def main():
    print("=== Yahoo OAuth Setup with Ngrok ===\n")
    
    # Start server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Give server time to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    # Start ngrok
    print("\nStarting ngrok tunnel...")
    ngrok_process = subprocess.Popen(["ngrok.exe", "http", "8000"])
    
    # Wait for ngrok to initialize
    print("Waiting for ngrok to initialize...")
    time.sleep(5)
    
    # Get the ngrok URL
    url = get_ngrok_url()
    if url:
        print(f"\n[OK] Ngrok tunnel established!")
        print(f"Public HTTPS URL: {url}")
        
        # Update .env file
        redirect_uri = update_env_file(url)
        
        print("\n" + "="*60)
        print("NEXT STEPS:")
        print("="*60)
        print(f"\n1. Go to Yahoo Developer Console:")
        print(f"   https://developer.yahoo.com/apps/")
        print(f"\n2. Find your app and click 'Update'")
        print(f"\n3. Change the Redirect URI to:")
        print(f"   {redirect_uri}")
        print(f"\n4. Save the changes")
        print(f"\n5. Open your browser and go to:")
        print(f"   {url}")
        print(f"\n6. Click 'Authorize with Yahoo'")
        print(f"\n7. Complete the OAuth flow!")
        print("\n" + "="*60)
        
        print("\nPress Ctrl+C to stop everything")
        
        try:
            ngrok_process.wait()
        except KeyboardInterrupt:
            print("\nShutting down...")
            ngrok_process.terminate()
            
    else:
        print("[ERROR] Could not get ngrok URL")
        print("You can run ngrok manually: ngrok.exe http 8000")
        ngrok_process.terminate()

if __name__ == "__main__":
    main()