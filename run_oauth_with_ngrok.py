#!/usr/bin/env python3
"""
Run complete OAuth setup with ngrok
"""

import subprocess
import time
import threading
import requests
import webbrowser
import os
import sys

def check_ngrok_auth():
    """Check if ngrok is authenticated"""
    try:
        result = subprocess.run(["ngrok.exe", "config", "check"], capture_output=True, text=True)
        if "authtoken" in result.stdout.lower() and "valid" in result.stdout.lower():
            return True
    except:
        pass
    return False

def start_server():
    """Start the FastAPI server"""
    print("Starting FastAPI server on http://localhost:8000...")
    os.system("python scripts/start.py")

def get_ngrok_url(max_attempts=10):
    """Get the public URL from ngrok API"""
    for i in range(max_attempts):
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
            data = response.json()
            
            for tunnel in data.get('tunnels', []):
                if tunnel.get('proto') == 'https':
                    return tunnel.get('public_url')
        except:
            time.sleep(1)
    return None

def update_env_file(ngrok_url):
    """Update .env file with new ngrok URL"""
    redirect_uri = f"{ngrok_url}/auth/callback"
    
    # Read current .env
    with open('.env', 'r') as f:
        content = f.read()
    
    # Update or add YAHOO_REDIRECT_URI
    import re
    if 'YAHOO_REDIRECT_URI=' in content:
        content = re.sub(r'YAHOO_REDIRECT_URI=.*', f'YAHOO_REDIRECT_URI={redirect_uri}', content)
    else:
        content += f'\nYAHOO_REDIRECT_URI={redirect_uri}\n'
    
    # Write back
    with open('.env', 'w') as f:
        f.write(content)
    
    return redirect_uri

def main():
    print("=== Yahoo OAuth Complete Setup ===\n")
    
    # Check ngrok auth
    if not check_ngrok_auth():
        print("[!] Ngrok is not authenticated.")
        print("    Please run: python setup_ngrok_auth.py")
        return
    
    print("[OK] Ngrok is authenticated\n")
    
    # Kill any existing Python processes
    print("Stopping any existing servers...")
    os.system("taskkill /F /IM python.exe 2>nul")
    time.sleep(2)
    
    # Start server in background
    print("\nStarting FastAPI server...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(3)
    
    # Start ngrok
    print("\nStarting ngrok tunnel...")
    ngrok_process = subprocess.Popen(["ngrok.exe", "http", "8000"], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
    
    # Wait and get URL
    print("Waiting for ngrok to establish tunnel", end="")
    for i in range(10):
        print(".", end="", flush=True)
        time.sleep(1)
    print()
    
    # Get the ngrok URL
    url = get_ngrok_url()
    if not url:
        print("\n[ERROR] Could not get ngrok URL")
        print("Ngrok might still be starting. Try these commands manually:")
        print("  1. ngrok.exe http 8000")
        print("  2. Check http://localhost:4040 for the tunnel URL")
        return
    
    # Update .env
    redirect_uri = update_env_file(url)
    
    # Show success and instructions
    print("\n" + "="*70)
    print("SUCCESS! Ngrok tunnel established")
    print("="*70)
    
    print(f"\nPublic HTTPS URL: {url}")
    print(f"OAuth Redirect URI: {redirect_uri}")
    
    print("\n" + "-"*70)
    print("IMPORTANT - Update Yahoo Developer Console:")
    print("-"*70)
    
    print(f"\n1. Open Yahoo Developer Console:")
    print(f"   https://developer.yahoo.com/apps/")
    
    print(f"\n2. Find your app and click 'Update' or 'Edit'")
    
    print(f"\n3. Change the Redirect URI to EXACTLY:")
    print(f"   {redirect_uri}")
    
    print(f"\n4. Save the changes and wait a moment for them to take effect")
    
    print("\n" + "-"*70)
    print("TEST YOUR OAUTH:")
    print("-"*70)
    
    print(f"\n5. Open your browser and go to:")
    print(f"   {url}")
    
    print(f"\n6. Click 'Authorize with Yahoo'")
    
    print(f"\n7. Sign in with your Yahoo account")
    
    print(f"\n8. Grant permissions - you should be redirected back successfully!")
    
    print("\n" + "="*70)
    
    # Ask if user wants to open browser
    response = input("\nOpen browser to test OAuth? (y/n): ")
    if response.lower() == 'y':
        webbrowser.open(url)
    
    print("\n[!] Keep this window open while testing OAuth")
    print("    Press Ctrl+C to stop everything when done")
    
    try:
        ngrok_process.wait()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        ngrok_process.terminate()
        os.system("taskkill /F /IM python.exe 2>nul")
        print("Done!")

if __name__ == "__main__":
    main()