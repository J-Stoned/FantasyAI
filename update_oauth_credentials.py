#!/usr/bin/env python3
"""
Update OAuth Credentials
This script helps update the OAuth credentials after Yahoo Developer Console registration
"""

import os
import sys
from pathlib import Path

def update_env_file(client_id, client_secret, redirect_uri=None):
    """Update .env file with new OAuth credentials"""
    
    if not client_id or not client_secret:
        print("❌ Client ID and Client Secret are required")
        return False
    
    # Default redirect URI if not provided
    if not redirect_uri:
        redirect_uri = "http://localhost:8000/auth/callback"
    
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env file not found. Please run fix_oauth_config.py first.")
        return False
    
    try:
        # Read current .env file
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Update the OAuth credentials
        lines = content.split('\n')
        updated_lines = []
        
        for line in lines:
            if line.startswith('YAHOO_CLIENT_ID='):
                updated_lines.append(f'YAHOO_CLIENT_ID={client_id}')
            elif line.startswith('YAHOO_CLIENT_SECRET='):
                updated_lines.append(f'YAHOO_CLIENT_SECRET={client_secret}')
            elif line.startswith('YAHOO_REDIRECT_URI='):
                updated_lines.append(f'YAHOO_REDIRECT_URI={redirect_uri}')
            else:
                updated_lines.append(line)
        
        # Write updated content
        with open(env_file, 'w') as f:
            f.write('\n'.join(updated_lines))
        
        print(f"✅ Updated .env file with new credentials")
        print(f"   Client ID: {client_id[:20]}...")
        print(f"   Client Secret: ***{client_secret[-4:]}")
        print(f"   Redirect URI: {redirect_uri}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

def update_yahoo_wrapper_file(client_id, client_secret, redirect_uri=None):
    """Update the yahoo_wrapper/__init__.py file with new credentials"""
    
    if not client_id or not client_secret:
        print("❌ Client ID and Client Secret are required")
        return False
    
    # Default redirect URI if not provided
    if not redirect_uri:
        redirect_uri = "http://localhost:8000/auth/callback"
    
    wrapper_file = Path("src/yahoo_wrapper/__init__.py")
    
    if not wrapper_file.exists():
        print("❌ yahoo_wrapper/__init__.py file not found")
        return False
    
    try:
        # Read current file
        with open(wrapper_file, 'r') as f:
            content = f.read()
        
        # Update the credentials in the file
        lines = content.split('\n')
        updated_lines = []
        
        for line in lines:
            if 'self.client_id = ' in line:
                updated_lines.append(f'        self.client_id = "{client_id}"')
            elif 'self.client_secret = ' in line:
                updated_lines.append(f'        self.client_secret = "{client_secret}"')
            elif 'self.redirect_uri = ' in line:
                updated_lines.append(f'        self.redirect_uri = "{redirect_uri}"')
            else:
                updated_lines.append(line)
        
        # Write updated content
        with open(wrapper_file, 'w') as f:
            f.write('\n'.join(updated_lines))
        
        print(f"✅ Updated yahoo_wrapper/__init__.py with new credentials")
        return True
        
    except Exception as e:
        print(f"❌ Error updating yahoo_wrapper file: {e}")
        return False

def verify_credentials(client_id, client_secret):
    """Verify that the credentials look valid"""
    print("\nVerifying credentials...")
    
    # Basic validation
    if len(client_id) < 10:
        print("❌ Client ID seems too short")
        return False
    
    if len(client_secret) < 10:
        print("❌ Client Secret seems too short")
        return False
    
    # Check for common patterns
    if 'dj0y' in client_id:
        print("✅ Client ID format looks correct (Yahoo format)")
    else:
        print("⚠️  Client ID format may be different from expected")
    
    if len(client_secret) == 40:
        print("✅ Client Secret length is correct (40 characters)")
    else:
        print(f"⚠️  Client Secret length is {len(client_secret)} characters (expected 40)")
    
    return True

def test_oauth_flow():
    """Test the OAuth flow with new credentials"""
    print("\nTesting OAuth flow with new credentials...")
    
    try:
        # Import and test the Yahoo API
        import sys
        sys.path.append('src')
        from yahoo_wrapper import YahooFantasyAPI
        
        yahoo_api = YahooFantasyAPI()
        
        # Test authorization URL generation
        auth_url = yahoo_api.get_authorization_url()
        
        if "mock-callback" in auth_url:
            print("⚠️  Still using mock OAuth flow")
            print("   This is expected until you implement real OAuth endpoints")
        else:
            print("✅ Real OAuth flow detected")
        
        print(f"   Authorization URL: {auth_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing OAuth flow: {e}")
        return False

def main():
    """Main function to update OAuth credentials"""
    print("Yahoo OAuth Credentials Update")
    print("="*40)
    print("\nThis script will help you update your OAuth credentials")
    print("after registering your app in Yahoo Developer Console.\n")
    
    # Get credentials from user
    print("Please enter your Yahoo Developer Console credentials:")
    client_id = input("Client ID (Consumer Key): ").strip()
    client_secret = input("Client Secret (Consumer Secret): ").strip()
    redirect_uri = input("Redirect URI [http://localhost:8000/auth/callback]: ").strip()
    
    if not redirect_uri:
        redirect_uri = "http://localhost:8000/auth/callback"
    
    # Validate input
    if not client_id or not client_secret:
        print("❌ Client ID and Client Secret are required")
        sys.exit(1)
    
    # Verify credentials
    if not verify_credentials(client_id, client_secret):
        print("❌ Credentials validation failed")
        sys.exit(1)
    
    print("\n" + "="*40)
    print("UPDATING FILES")
    print("="*40)
    
    # Update .env file
    env_updated = update_env_file(client_id, client_secret, redirect_uri)
    
    # Update yahoo_wrapper file
    wrapper_updated = update_yahoo_wrapper_file(client_id, client_secret, redirect_uri)
    
    print("\n" + "="*40)
    print("TESTING OAUTH FLOW")
    print("="*40)
    
    # Test OAuth flow
    oauth_tested = test_oauth_flow()
    
    print("\n" + "="*40)
    print("SUMMARY")
    print("="*40)
    print(f"Environment file updated: {'✅' if env_updated else '❌'}")
    print(f"Wrapper file updated: {'✅' if wrapper_updated else '❌'}")
    print(f"OAuth flow tested: {'✅' if oauth_tested else '❌'}")
    
    if env_updated and wrapper_updated:
        print("\n🎉 OAuth credentials updated successfully!")
        print("\nNext steps:")
        print("1. Run the OAuth diagnostic: python debug_oauth.py")
        print("2. Test the OAuth flow: python test_oauth_flow.py")
        print("3. Implement real OAuth endpoints in your application")
        print("4. Make sure your redirect URI is registered in Yahoo Developer Console")
    else:
        print("\n❌ Some updates failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 