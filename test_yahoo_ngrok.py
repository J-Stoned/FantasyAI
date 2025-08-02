#!/usr/bin/env python3
"""
Test Yahoo OAuth with ngrok URL
"""

import requests
from urllib.parse import urlparse, parse_qs
import sys
sys.path.insert(0, 'src')

from yahoo_wrapper import YahooFantasyAPI

# Get the OAuth URL
api = YahooFantasyAPI()
auth_url = api.get_authorization_url()

print("Testing Yahoo OAuth with ngrok redirect URI")
print("=" * 60)

# Parse to check redirect_uri
parsed = urlparse(auth_url)
params = parse_qs(parsed.query)

print("\nOAuth Parameters:")
print(f"  Client ID: {params.get('client_id', [''])[0][:30]}...")
print(f"  Redirect URI: {params.get('redirect_uri', [''])[0]}")
print(f"  Scope: {params.get('scope', [''])[0]}")

# Test with Yahoo
print("\nTesting with Yahoo...")
try:
    response = requests.get(auth_url, allow_redirects=False)
    print(f"Response Status: {response.status_code}")
    
    if 'Location' in response.headers:
        location = response.headers['Location']
        print(f"Redirect to: {location[:100]}...")
        
        if 'error=' in location:
            error_params = parse_qs(urlparse(location).query)
            print(f"\nError: {error_params.get('error', ['Unknown'])[0]}")
            print(f"Description: {error_params.get('error_description', ['No description'])[0]}")
            
            if 'invalid_request' in location:
                print("\nPossible issues:")
                print("1. The redirect URI in Yahoo Developer Console doesn't match exactly")
                print("2. Yahoo app might not be approved or active")
                print("3. The client ID or secret might be incorrect")
                
        else:
            print("\nSuccess! Yahoo accepted the request.")
            
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("IMPORTANT CHECKLIST:")
print("=" * 60)
print("\n1. In Yahoo Developer Console, is your redirect URI EXACTLY:")
print(f"   {params.get('redirect_uri', [''])[0]}")
print("\n2. Is your Yahoo app status 'Approved' or 'Active'?")
print("\n3. Did you save the changes after updating the redirect URI?")
print("\n4. Try waiting 1-2 minutes for Yahoo to update (sometimes there's a delay)")