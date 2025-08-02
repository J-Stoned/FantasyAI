#!/usr/bin/env python3
"""
Test Yahoo OAuth directly to capture exact error
"""

import requests
import sys
from urllib.parse import urlparse, parse_qs
sys.path.insert(0, 'src')

from yahoo_wrapper import YahooFantasyAPI

# Initialize API
api = YahooFantasyAPI()

# Generate OAuth URL
auth_url = api.get_authorization_url()

print("=== Testing Yahoo OAuth URL ===")
print(f"URL: {auth_url[:100]}...")
print(f"Full URL length: {len(auth_url)}")

# Parse URL to check parameters
parsed = urlparse(auth_url)
params = parse_qs(parsed.query)

print("\n=== URL Parameters ===")
for key, values in params.items():
    value = values[0] if values else 'None'
    if key == 'client_id':
        print(f"{key}: {value[:30]}...")
    elif key in ['state', 'nonce']:
        print(f"{key}: {value[:20]}...")
    else:
        print(f"{key}: {value}")

# Test the URL with requests
print("\n=== Testing with Requests ===")
try:
    # Don't follow redirects to capture the exact response
    response = requests.get(auth_url, allow_redirects=False)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if 'Location' in response.headers:
        redirect_url = response.headers['Location']
        print(f"\nRedirect URL: {redirect_url[:100]}...")
        
        # Parse redirect URL for error details
        redirect_parsed = urlparse(redirect_url)
        redirect_params = parse_qs(redirect_parsed.query)
        
        if 'error' in redirect_params:
            print("\n=== OAuth Error Details ===")
            print(f"Error: {redirect_params.get('error', ['Unknown'])[0]}")
            print(f"Error Description: {redirect_params.get('error_description', ['No description'])[0]}")
        else:
            print("\nNo error in redirect - this is good!")
            
except Exception as e:
    print(f"Request failed: {e}")

# Test minimal URL
print("\n=== Testing Minimal OAuth URL ===")
minimal_params = {
    'client_id': api.client_id,
    'redirect_uri': api.redirect_uri,
    'response_type': 'code'
}

from urllib.parse import urlencode
minimal_url = f"https://api.login.yahoo.com/oauth2/request_auth?{urlencode(minimal_params)}"
print(f"Minimal URL: {minimal_url[:100]}...")

try:
    response = requests.get(minimal_url, allow_redirects=False)
    print(f"Status Code: {response.status_code}")
    
    if 'Location' in response.headers and 'error=' in response.headers['Location']:
        redirect_parsed = urlparse(response.headers['Location'])
        redirect_params = parse_qs(redirect_parsed.query)
        print(f"Error: {redirect_params.get('error', ['Unknown'])[0]}")
        print(f"Description: {redirect_params.get('error_description', ['No description'])[0]}")
        
except Exception as e:
    print(f"Request failed: {e}")

print("\n=== Debugging Tips ===")
print("1. Check if your Yahoo app is approved and active")
print("2. Verify the redirect URI matches EXACTLY in Yahoo Developer Console")
print("3. Try creating a new Yahoo app if this one isn't working")
print("4. Check if the client_id and client_secret are correct")