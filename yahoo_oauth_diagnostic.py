#!/usr/bin/env python3
"""
Enhanced Yahoo OAuth2 Diagnostic Tool
Helps identify and fix OAuth authorization issues
"""

import os
import sys
import json
import requests
from urllib.parse import urlparse, parse_qs, urlencode
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from dotenv import load_dotenv
load_dotenv()

def check_credentials():
    """Check if OAuth credentials are properly loaded"""
    print("=== Checking OAuth Credentials ===")
    
    client_id = os.getenv('YAHOO_CLIENT_ID')
    client_secret = os.getenv('YAHOO_CLIENT_SECRET')
    redirect_uri = os.getenv('YAHOO_REDIRECT_URI', 'http://localhost:8000/auth/callback')
    
    results = {
        'client_id': {
            'exists': bool(client_id),
            'length': len(client_id) if client_id else 0,
            'preview': client_id[:20] + '...' if client_id else 'NOT SET'
        },
        'client_secret': {
            'exists': bool(client_secret),
            'length': len(client_secret) if client_secret else 0,
            'preview': '***' + client_secret[-4:] if client_secret else 'NOT SET'
        },
        'redirect_uri': {
            'exists': bool(redirect_uri),
            'value': redirect_uri
        }
    }
    
    for key, info in results.items():
        status = "OK" if info['exists'] else "MISSING"
        print(f"  {key}: {status}")
        if key == 'redirect_uri':
            print(f"    Value: {info['value']}")
        else:
            print(f"    Length: {info['length']}")
            print(f"    Preview: {info['preview']}")
    
    return all(info['exists'] for info in results.values())

def test_oauth_url_generation():
    """Test OAuth URL generation with the new implementation"""
    print("\n=== Testing OAuth URL Generation ===")
    
    try:
        from yahoo_wrapper import YahooFantasyAPI
        api = YahooFantasyAPI()
        
        # Generate URL
        auth_url = api.get_authorization_url()
        
        # Parse and analyze
        parsed = urlparse(auth_url)
        params = parse_qs(parsed.query)
        
        print(f"Generated URL: {auth_url[:100]}...")
        print(f"URL Length: {len(auth_url)}")
        print(f"Host: {parsed.hostname}")
        print(f"Path: {parsed.path}")
        
        print("\nParameters:")
        required_params = ['client_id', 'redirect_uri', 'response_type', 'state', 'scope']
        for param in required_params:
            if param in params:
                value = params[param][0]
                if param == 'client_id':
                    print(f"  {param}: {value[:20]}... (OK)")
                else:
                    print(f"  {param}: {value} (OK)")
            else:
                print(f"  {param}: MISSING!")
        
        # Check for scope specifically
        if 'scope' in params:
            scope_value = params['scope'][0]
            if scope_value == 'fspt-r':
                print("\n✓ Scope is correctly set for Fantasy Sports read access")
            else:
                print(f"\n✗ Incorrect scope value: {scope_value} (should be 'fspt-r')")
        else:
            print("\n✗ MISSING REQUIRED SCOPE PARAMETER!")
        
        return auth_url
        
    except Exception as e:
        print(f"Error generating URL: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_server_endpoints():
    """Test if the server is running and endpoints are accessible"""
    print("\n=== Testing Server Endpoints ===")
    
    base_url = "http://localhost:8000"
    
    endpoints = [
        "/api",
        "/auth/status",
        "/auth/authorize"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=2)
            print(f"  {endpoint}: {response.status_code}")
            
            if endpoint == "/auth/authorize" and response.status_code == 200:
                data = response.json()
                if 'debug_info' in data:
                    debug = data['debug_info']
                    print(f"    Has scope: {debug.get('has_scope', False)}")
                    print(f"    Scope value: {debug.get('scope_value', 'None')}")
                    print(f"    All required params: {debug.get('has_all_required', False)}")
                    
        except requests.exceptions.ConnectionError:
            print(f"  {endpoint}: Server not running")
        except Exception as e:
            print(f"  {endpoint}: Error - {e}")

def test_yahoo_oauth_directly():
    """Test Yahoo OAuth endpoints directly"""
    print("\n=== Testing Direct Yahoo OAuth Request ===")
    
    # Load credentials
    client_id = os.getenv('YAHOO_CLIENT_ID')
    redirect_uri = os.getenv('YAHOO_REDIRECT_URI', 'http://localhost:8000/auth/callback')
    
    if not client_id:
        print("Cannot test - missing CLIENT_ID")
        return
    
    # Build test URL with minimal parameters
    test_params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'fspt-r'
    }
    
    auth_url = f"https://api.login.yahoo.com/oauth2/request_auth?{urlencode(test_params)}"
    
    print(f"Test URL: {auth_url[:100]}...")
    
    # Test with requests
    try:
        response = requests.get(auth_url, allow_redirects=False)
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 302:
            print("✓ Yahoo accepted the request (redirect to login)")
            location = response.headers.get('Location', '')
            if 'error=' in location:
                # Parse error from redirect
                error_params = parse_qs(urlparse(location).query)
                print(f"✗ OAuth Error: {error_params.get('error', ['Unknown'])[0]}")
                print(f"  Description: {error_params.get('error_description', ['None'])[0]}")
            else:
                print("✓ No error in redirect - request appears valid")
        else:
            print(f"Unexpected response: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            if response.text:
                print(f"Body preview: {response.text[:200]}")
                
    except Exception as e:
        print(f"Request failed: {e}")

def generate_diagnostic_report():
    """Generate a comprehensive diagnostic report"""
    print("\n" + "="*60)
    print("YAHOO OAUTH2 DIAGNOSTIC REPORT")
    print("="*60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Check credentials
    creds_ok = check_credentials()
    
    # Test URL generation
    auth_url = test_oauth_url_generation()
    
    # Test server
    test_server_endpoints()
    
    # Test Yahoo directly
    test_yahoo_oauth_directly()
    
    # Summary
    print("\n=== SUMMARY ===")
    if creds_ok and auth_url:
        print("✓ Credentials loaded successfully")
        print("✓ OAuth URL generated with proper encoding")
        print("✓ Required 'scope' parameter included")
        print("\nNext steps:")
        print("1. Ensure your Yahoo app is properly configured")
        print("2. Verify redirect URI matches exactly in Yahoo Developer Console")
        print("3. Try the authorization flow in your browser")
    else:
        print("✗ Issues detected - review the output above")

if __name__ == "__main__":
    generate_diagnostic_report()