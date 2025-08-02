#!/usr/bin/env python3
"""
Debug Yahoo App Configuration
"""

import requests
from urllib.parse import urlencode, quote
import os
from dotenv import load_dotenv
import time

load_dotenv()

# Get credentials
client_id = os.getenv('YAHOO_CLIENT_ID')
client_secret = os.getenv('YAHOO_CLIENT_SECRET')
ngrok_url = "https://436b00172fd8.ngrok-free.app"
redirect_uri = f"{ngrok_url}/auth/callback"

print("=== Yahoo App Debug ===\n")
print(f"Client ID: {client_id[:30]}...")
print(f"Redirect URI: {redirect_uri}")

# Test 1: Basic OAuth URL
print("\n--- Test 1: Basic OAuth URL ---")
basic_params = {
    'client_id': client_id,
    'redirect_uri': redirect_uri,
    'response_type': 'code'
}
basic_url = f"https://api.login.yahoo.com/oauth2/request_auth?{urlencode(basic_params)}"
print(f"URL: {basic_url[:100]}...")

response = requests.get(basic_url, allow_redirects=False)
print(f"Status: {response.status_code}")
if 'Location' in response.headers and 'error=' in response.headers['Location']:
    print(f"Error in redirect: {response.headers['Location'][:100]}...")

# Test 2: With scope
print("\n--- Test 2: With Fantasy Sports Scope ---")
scoped_params = {
    'client_id': client_id,
    'redirect_uri': redirect_uri,
    'response_type': 'code',
    'scope': 'fspt-r'
}
scoped_url = f"https://api.login.yahoo.com/oauth2/request_auth?{urlencode(scoped_params)}"

response = requests.get(scoped_url, allow_redirects=False)
print(f"Status: {response.status_code}")
if 'Location' in response.headers and 'error=' in response.headers['Location']:
    print(f"Error in redirect: {response.headers['Location'][:100]}...")

# Test 3: Try localhost instead
print("\n--- Test 3: Testing with localhost ---")
localhost_params = {
    'client_id': client_id,
    'redirect_uri': 'http://localhost:8000/auth/callback',
    'response_type': 'code',
    'scope': 'fspt-r'
}
localhost_url = f"https://api.login.yahoo.com/oauth2/request_auth?{urlencode(localhost_params)}"

response = requests.get(localhost_url, allow_redirects=False)
print(f"Status: {response.status_code}")
if 'Location' in response.headers:
    if 'error=' in response.headers['Location']:
        print(f"Error: Still getting error with localhost")
    else:
        print(f"Success?: {response.headers['Location'][:100]}...")

# Test 4: Check if it's a timing issue
print("\n--- Test 4: Timing Test ---")
print("Sometimes Yahoo takes time to propagate changes...")
print("When did you update the redirect URI in Yahoo Developer Console?")
print("It can take 5-15 minutes for changes to take effect.")

# Test 5: Try with different encoding
print("\n--- Test 5: Different URL Encoding ---")
manual_url = f"https://api.login.yahoo.com/oauth2/request_auth?client_id={client_id}&redirect_uri={quote(redirect_uri, safe='')}&response_type=code&scope=fspt-r"
print(f"Manual URL: {manual_url[:100]}...")

response = requests.get(manual_url, allow_redirects=False)
print(f"Status: {response.status_code}")
if 'Location' in response.headers and 'error=' not in response.headers['Location']:
    print("Success with manual encoding!")

print("\n=== Recommendations ===")
print("\n1. Wait 10-15 minutes if you just updated Yahoo Developer Console")
print("\n2. Try creating a completely new Yahoo app with the ngrok URL")
print("\n3. Check if your Yahoo app has any special restrictions or requirements")
print("\n4. Consider using a persistent tunnel service instead of ngrok free tier:")
print("   - Cloudflare Tunnel (free with domain)")
print("   - localtunnel.me")
print("   - serveo.net")
print("\n5. As a last resort, try deploying to a free hosting service:")
print("   - Render.com")
print("   - Railway.app")
print("   - Fly.io")