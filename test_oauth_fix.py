#!/usr/bin/env python3
"""
Test the fixed OAuth implementation
"""

import webbrowser
import sys
sys.path.insert(0, 'src')

from yahoo_wrapper import YahooFantasyAPI

# Initialize API
api = YahooFantasyAPI()

# Generate OAuth URL
auth_url = api.get_authorization_url()

print("=== OAuth URL Analysis ===")
print(f"URL Length: {len(auth_url)}")

# Check for required parameters
required_checks = [
    ('client_id=', 'Client ID'),
    ('redirect_uri=', 'Redirect URI'),
    ('response_type=code', 'Response Type'),
    ('state=', 'State Parameter'),
    ('scope=fspt-r', 'Fantasy Sports Scope'),
    ('language=', 'Language'),
    ('nonce=', 'Nonce')
]

print("\nParameter Checks:")
for param, name in required_checks:
    if param in auth_url:
        print(f"  [OK] {name}: Present")
    else:
        print(f"  [MISSING] {name}: MISSING")

print(f"\nGenerated OAuth URL:")
print(auth_url)

print("\n=== Instructions ===")
print("1. Copy the URL above")
print("2. Open it in your browser")
print("3. Sign in with your Yahoo account")
print("4. Grant permissions to the app")
print("5. You'll be redirected to http://localhost:8000/auth/callback")

# Ask if user wants to open in browser
response = input("\nOpen in browser? (y/n): ")
if response.lower() == 'y':
    webbrowser.open(auth_url)
    print("\nOpened in browser!")