#!/usr/bin/env python3
"""
Setup ngrok auth token
"""

import subprocess
import os

def setup_auth_token():
    print("=== Ngrok Auth Token Setup ===\n")
    
    print("To use ngrok, you need a free account.")
    print("\n1. Sign up at: https://dashboard.ngrok.com/signup")
    print("2. Get your auth token at: https://dashboard.ngrok.com/get-started/your-authtoken")
    print("\nYour auth token looks like: 2abc123XYZ...")
    
    token = input("\nEnter your ngrok auth token: ").strip()
    
    if not token:
        print("No token provided. Exiting.")
        return False
    
    print(f"\nSetting up ngrok with your auth token...")
    
    try:
        result = subprocess.run(["ngrok.exe", "authtoken", token], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Auth token configured successfully!")
            print("\nNgrok is now ready to use!")
            return True
        else:
            print(f"[ERROR] Failed to set auth token: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    if setup_auth_token():
        print("\n" + "="*50)
        print("Next step: Run 'python run_oauth_with_ngrok.py'")
        print("="*50)