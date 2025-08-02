#!/usr/bin/env python3
"""
Check ngrok tunnel status
"""

import requests
import time

def get_ngrok_info():
    """Get ngrok tunnel information"""
    try:
        response = requests.get('http://localhost:4040/api/tunnels')
        data = response.json()
        
        print("=== Ngrok Tunnel Information ===\n")
        
        for tunnel in data.get('tunnels', []):
            print(f"Protocol: {tunnel.get('proto')}")
            print(f"Public URL: {tunnel.get('public_url')}")
            print(f"Local: {tunnel.get('config', {}).get('addr')}")
            print()
            
            if tunnel.get('proto') == 'https':
                url = tunnel.get('public_url')
                redirect_uri = f"{url}/auth/callback"
                
                print("="*70)
                print("OAUTH SETUP INSTRUCTIONS:")
                print("="*70)
                print(f"\n1. Your ngrok HTTPS URL is:")
                print(f"   {url}")
                
                print(f"\n2. Update your .env file YAHOO_REDIRECT_URI to:")
                print(f"   {redirect_uri}")
                
                print(f"\n3. Go to Yahoo Developer Console:")
                print(f"   https://developer.yahoo.com/apps/")
                
                print(f"\n4. Update your app's Redirect URI to:")
                print(f"   {redirect_uri}")
                
                print(f"\n5. Save changes in Yahoo")
                
                print(f"\n6. Restart your FastAPI server")
                
                print(f"\n7. Visit {url} to test OAuth!")
                
                return url, redirect_uri
                
    except Exception as e:
        print(f"Error: Could not connect to ngrok API at http://localhost:4040")
        print(f"Make sure ngrok is running: ngrok.exe http 8000")
        return None, None

if __name__ == "__main__":
    url, redirect_uri = get_ngrok_info()
    
    if redirect_uri:
        print("\n" + "="*70)
        print("Would you like to update your .env file automatically? (y/n)")
        # Don't wait for input in automated context