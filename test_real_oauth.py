#!/usr/bin/env python3
"""
Test the real Yahoo OAuth2 flow
"""

import sys
import webbrowser
sys.path.insert(0, 'src')

from yahoo_wrapper import YahooFantasyAPI

def test_oauth():
    """Test the OAuth flow"""
    print("=== Yahoo OAuth2 Test ===")
    
    # Initialize API
    api = YahooFantasyAPI()
    
    # Check credentials
    print(f"\nCredentials loaded:")
    print(f"  Client ID: {api.client_id[:20]}..." if api.client_id else "  Client ID: NOT SET")
    print(f"  Client Secret: ***{api.client_secret[-4:]}" if api.client_secret else "  Client Secret: NOT SET")
    print(f"  Redirect URI: {api.redirect_uri}")
    
    # Generate auth URL
    auth_url = api.get_authorization_url()
    print(f"\nGenerated Authorization URL:")
    print(f"  {auth_url}")
    
    # Check if it's a real Yahoo URL
    if auth_url.startswith("https://api.login.yahoo.com/oauth2/request_auth"):
        print("\n✓ SUCCESS: Real Yahoo OAuth2 URL generated!")
        print("\nNext steps:")
        print("1. Start your app: python scripts/start.py")
        print("2. Visit: http://localhost:8000")
        print("3. Click 'Authorize with Yahoo'")
        print("4. Complete the OAuth flow")
        
        # Offer to open the URL
        response = input("\nWould you like to open the authorization URL in your browser? (y/n): ")
        if response.lower() == 'y':
            webbrowser.open(auth_url)
            print("\nOpened in browser. After authorizing, you'll be redirected to:")
            print(f"  {api.redirect_uri}")
    else:
        print("\n✗ ERROR: Not a real Yahoo OAuth URL")
        print("  Make sure you've updated the implementation to use real OAuth")

if __name__ == "__main__":
    test_oauth()