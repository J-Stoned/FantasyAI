#!/usr/bin/env python3
"""
Test OAuth without scope parameter
"""

import requests
from urllib.parse import urlencode
import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv('YAHOO_CLIENT_ID')
redirect_uri = "https://436b00172fd8.ngrok-free.app/auth/callback"

print("Testing OAuth WITHOUT scope parameter...")
print("="*60)

# Test without scope
params = {
    'client_id': client_id,
    'redirect_uri': redirect_uri,
    'response_type': 'code',
    'state': 'test123'
}

url = f"https://api.login.yahoo.com/oauth2/request_auth?{urlencode(params)}"
print(f"URL: {url[:100]}...")

response = requests.get(url, allow_redirects=False)
print(f"\nStatus: {response.status_code}")

if response.status_code == 302:
    location = response.headers.get('Location', '')
    print(f"Redirects to: {location[:150]}...")
    
    if 'error=' not in location and 'login.yahoo.com' in location:
        print("\n✓ SUCCESS! Yahoo accepted the OAuth request!")
        print("\nThis means:")
        print("1. Your redirect URI is correctly configured")
        print("2. The issue was with the 'scope' parameter")
        print("\nNext steps:")
        print("- Remove or fix the scope parameter in the OAuth URL")
        print("- Check what scopes your Yahoo app is authorized for")
    elif 'error=' in location:
        from urllib.parse import urlparse, parse_qs
        error_params = parse_qs(urlparse(location).query)
        print(f"\nError: {error_params.get('error', ['Unknown'])[0]}")
        print(f"Description: {error_params.get('error_description', ['No description'])[0]}")

print("\n" + "="*60)
print("IMPORTANT DISCOVERY:")
print("="*60)
print("\nThe 'scope=fspt-r' parameter might be causing issues.")
print("Your Yahoo app might not have Fantasy Sports API access enabled.")
print("\nIn Yahoo Developer Console:")
print("1. Check what APIs your app has access to")
print("2. Make sure 'Fantasy Sports' is enabled")
print("3. The scope might need to be different or omitted")