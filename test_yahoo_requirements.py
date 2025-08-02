#!/usr/bin/env python3
"""
Test what Yahoo requires for OAuth
"""

import requests
from urllib.parse import urlencode
import os
from dotenv import load_dotenv

load_dotenv()

# Test different redirect URI formats
client_id = os.getenv('YAHOO_CLIENT_ID')

test_uris = [
    "http://localhost:8000/auth/callback",
    "https://localhost:8000/auth/callback",
    "http://127.0.0.1:8000/auth/callback",
    "https://127.0.0.1:8000/auth/callback",
]

print("Testing Yahoo OAuth Requirements")
print("=" * 50)

for uri in test_uris:
    params = {
        'client_id': client_id,
        'redirect_uri': uri,
        'response_type': 'code',
        'scope': 'fspt-r'
    }
    
    url = f"https://api.login.yahoo.com/oauth2/request_auth?{urlencode(params)}"
    
    try:
        response = requests.get(url, allow_redirects=False)
        
        print(f"\nTesting: {uri}")
        print(f"  Status: {response.status_code}")
        
        if 'Location' in response.headers:
            location = response.headers['Location']
            if 'error=' in location:
                # Extract error
                from urllib.parse import urlparse, parse_qs
                error_params = parse_qs(urlparse(location).query)
                error = error_params.get('error', ['Unknown'])[0]
                desc = error_params.get('error_description', ['No description'])[0]
                print(f"  Error: {error}")
                print(f"  Description: {desc}")
            else:
                print("  Result: SUCCESS - No error in redirect")
        else:
            print("  Result: No redirect")
            
    except Exception as e:
        print(f"  Failed: {e}")

print("\n" + "=" * 50)
print("SUMMARY:")
print("Yahoo requires HTTPS for redirect URIs in production.")
print("For local development, use ngrok or similar tunneling service.")
print("\nRecommended approach:")
print("1. Use ngrok: ngrok http 8000")
print("2. Update Yahoo app with the ngrok HTTPS URL")
print("3. Update your .env file with the same URL")