#!/usr/bin/env python3
"""
Start server and test OAuth flow
"""

import sys
import time
import threading
import webbrowser
import requests
from urllib.parse import urlparse, parse_qs

# Add paths
sys.path.insert(0, 'src')
sys.path.insert(0, '.')

def start_server():
    """Start the FastAPI server in a thread"""
    import uvicorn
    from main import app
    from config.settings import settings
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )

def test_oauth_flow():
    """Test the OAuth flow"""
    # Give server time to start
    print("Starting server...")
    time.sleep(3)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/api")
        print(f"Server is running: {response.status_code}")
        print(f"API Response: {response.json()}")
    except Exception as e:
        print(f"Server not responding: {e}")
        return
    
    # Get authorization URL
    try:
        response = requests.get("http://localhost:8000/auth/authorize")
        auth_data = response.json()
        auth_url = auth_data.get('authorization_url')
        
        print(f"\nAuthorization URL received:")
        print(f"  {auth_url}")
        
        # Parse the URL to check if it's real Yahoo
        parsed = urlparse(auth_url)
        if parsed.hostname == "api.login.yahoo.com":
            print("\nSUCCESS: Real Yahoo OAuth2 URL!")
            print("\nTo complete OAuth flow:")
            print("1. Open this URL in your browser")
            print("2. Sign in to Yahoo")
            print("3. Authorize the app")
            print("4. You'll be redirected to http://localhost:8000/auth/callback")
            
            # Open in browser
            print("\nOpening in browser...")
            webbrowser.open(auth_url)
        else:
            print(f"\nERROR: Not a Yahoo URL. Host: {parsed.hostname}")
            
    except Exception as e:
        print(f"Error getting auth URL: {e}")

if __name__ == "__main__":
    # Start server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Test OAuth flow
    test_oauth_flow()
    
    # Keep running
    print("\nServer is running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")