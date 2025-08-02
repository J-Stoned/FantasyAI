#!/usr/bin/env python3
"""
Configure ngrok with auth token
Usage: python configure_ngrok.py YOUR_AUTH_TOKEN
"""

import subprocess
import sys

def configure_ngrok(token):
    """Configure ngrok with the provided auth token"""
    print(f"Configuring ngrok with your auth token...")
    
    try:
        result = subprocess.run(["ngrok.exe", "authtoken", token], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Ngrok configured successfully!")
            print("\nYou can now run: python run_oauth_with_ngrok.py")
            return True
        else:
            print(f"[ERROR] Failed to configure ngrok: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python configure_ngrok.py YOUR_AUTH_TOKEN")
        print("\nGet your token from: https://dashboard.ngrok.com/get-started/your-authtoken")
        sys.exit(1)
    
    token = sys.argv[1]
    configure_ngrok(token)