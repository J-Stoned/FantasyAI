#!/usr/bin/env python3
"""
Test Yahoo OAuth Flow
This script tests the complete OAuth flow with proper environment variable loading
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from yahoo_wrapper import YahooFantasyAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class YahooOAuthTester:
    """Test Yahoo OAuth flow"""
    
    def __init__(self):
        self.yahoo_api = YahooFantasyAPI()
        self.test_results = {}
    
    def test_environment_loading(self):
        """Test if environment variables are properly loaded"""
        print("Testing environment variable loading...")
        
        # Check environment variables
        client_id = os.getenv("YAHOO_CLIENT_ID")
        client_secret = os.getenv("YAHOO_CLIENT_SECRET")
        redirect_uri = os.getenv("YAHOO_REDIRECT_URI")
        
        results = {
            "client_id_loaded": bool(client_id),
            "client_secret_loaded": bool(client_secret),
            "redirect_uri_loaded": bool(redirect_uri),
            "client_id_length": len(client_id) if client_id else 0,
            "client_secret_length": len(client_secret) if client_secret else 0
        }
        
        print(f"  YAHOO_CLIENT_ID: {'✅ Loaded' if client_id else '❌ Not loaded'}")
        print(f"  YAHOO_CLIENT_SECRET: {'✅ Loaded' if client_secret else '❌ Not loaded'}")
        print(f"  YAHOO_REDIRECT_URI: {'✅ Loaded' if redirect_uri else '❌ Not loaded'}")
        
        return results
    
    def test_api_initialization(self):
        """Test Yahoo API initialization"""
        print("\nTesting Yahoo API initialization...")
        
        results = {
            "client_id_set": bool(self.yahoo_api.client_id),
            "client_secret_set": bool(self.yahoo_api.client_secret),
            "redirect_uri_set": bool(self.yahoo_api.redirect_uri),
            "oauth_client_created": hasattr(self.yahoo_api, 'oauth_client')
        }
        
        print(f"  Client ID configured: {'✅' if results['client_id_set'] else '❌'}")
        print(f"  Client Secret configured: {'✅' if results['client_secret_set'] else '❌'}")
        print(f"  Redirect URI configured: {'✅' if results['redirect_uri_set'] else '❌'}")
        print(f"  OAuth client created: {'✅' if results['oauth_client_created'] else '❌'}")
        
        return results
    
    def test_authorization_url_generation(self):
        """Test authorization URL generation"""
        print("\nTesting authorization URL generation...")
        
        try:
            auth_url = self.yahoo_api.get_authorization_url()
            results = {
                "success": True,
                "auth_url": auth_url,
                "is_mock": "mock-callback" in auth_url,
                "has_state": "state=" in auth_url,
                "has_code": "code=" in auth_url
            }
            
            print(f"  Authorization URL generated: ✅")
            print(f"  URL: {auth_url}")
            print(f"  Using mock flow: {'✅' if results['is_mock'] else '❌'}")
            print(f"  Contains state parameter: {'✅' if results['has_state'] else '❌'}")
            print(f"  Contains code parameter: {'✅' if results['has_code'] else '❌'}")
            
        except Exception as e:
            results = {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
            print(f"  Authorization URL generation failed: ❌")
            print(f"  Error: {e}")
        
        return results
    
    async def test_token_exchange(self):
        """Test token exchange with mock code"""
        print("\nTesting token exchange...")
        
        try:
            # Use mock authorization code
            mock_code = "mock_auth_code_12345"
            mock_state = "test_state_123"
            
            success = await self.yahoo_api.exchange_code_for_token(mock_code, mock_state)
            
            results = {
                "success": success,
                "access_token_set": bool(self.yahoo_api.access_token),
                "refresh_token_set": bool(self.yahoo_api.refresh_token),
                "token_expires_set": bool(self.yahoo_api.token_expires_at)
            }
            
            print(f"  Token exchange: {'✅ Success' if success else '❌ Failed'}")
            print(f"  Access token set: {'✅' if results['access_token_set'] else '❌'}")
            print(f"  Refresh token set: {'✅' if results['refresh_token_set'] else '❌'}")
            print(f"  Token expiry set: {'✅' if results['token_expires_set'] else '❌'}")
            
        except Exception as e:
            results = {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
            print(f"  Token exchange failed: ❌")
            print(f"  Error: {e}")
        
        return results
    
    async def test_api_calls(self):
        """Test API calls with mock data"""
        print("\nTesting API calls with mock data...")
        
        try:
            # Test getting user leagues
            leagues = await self.yahoo_api.get_user_leagues()
            
            results = {
                "leagues_retrieved": bool(leagues),
                "leagues_count": len(leagues) if leagues else 0,
                "is_mock_data": any("mock" in str(league).lower() for league in leagues) if leagues else False
            }
            
            print(f"  User leagues retrieved: {'✅' if results['leagues_retrieved'] else '❌'}")
            print(f"  Number of leagues: {results['leagues_count']}")
            print(f"  Using mock data: {'✅' if results['is_mock_data'] else '❌'}")
            
            if leagues:
                print(f"  Sample league: {leagues[0].get('name', 'Unknown') if leagues else 'None'}")
            
        except Exception as e:
            results = {
                "leagues_retrieved": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
            print(f"  API call failed: ❌")
            print(f"  Error: {e}")
        
        return results
    
    def generate_oauth_flow_summary(self):
        """Generate a summary of the OAuth flow test"""
        print("\n" + "="*60)
        print("YAHOO OAUTH FLOW TEST SUMMARY")
        print("="*60)
        
        # Check if all tests passed
        all_tests_passed = (
            self.test_results.get("env_loading", {}).get("client_id_loaded", False) and
            self.test_results.get("env_loading", {}).get("client_secret_loaded", False) and
            self.test_results.get("api_init", {}).get("client_id_set", False) and
            self.test_results.get("api_init", {}).get("client_secret_set", False) and
            self.test_results.get("auth_url", {}).get("success", False)
        )
        
        print(f"Overall Status: {'✅ PASSED' if all_tests_passed else '❌ FAILED'}")
        
        print("\nTest Results:")
        print(f"  Environment Loading: {'✅' if self.test_results.get('env_loading', {}).get('client_id_loaded') else '❌'}")
        print(f"  API Initialization: {'✅' if self.test_results.get('api_init', {}).get('client_id_set') else '❌'}")
        print(f"  Auth URL Generation: {'✅' if self.test_results.get('auth_url', {}).get('success') else '❌'}")
        print(f"  Token Exchange: {'✅' if self.test_results.get('token_exchange', {}).get('success') else '❌'}")
        print(f"  API Calls: {'✅' if self.test_results.get('api_calls', {}).get('leagues_retrieved') else '❌'}")
        
        if all_tests_passed:
            print("\n🎉 OAuth flow is working correctly!")
            print("\nNext steps:")
            print("1. Your OAuth configuration is ready for development")
            print("2. The mock OAuth flow is working as expected")
            print("3. You can now integrate this with your application")
        else:
            print("\n❌ OAuth flow has issues that need to be addressed")
            print("\nCommon issues:")
            print("1. Environment variables not loaded from .env file")
            print("2. Yahoo API credentials not properly configured")
            print("3. Redirect URI not registered in Yahoo Developer Console")
        
        return all_tests_passed

async def main():
    """Main function to test OAuth flow"""
    print("Yahoo OAuth Flow Test")
    print("="*50)
    
    tester = YahooOAuthTester()
    
    try:
        # Test environment loading
        tester.test_results["env_loading"] = tester.test_environment_loading()
        
        # Test API initialization
        tester.test_results["api_init"] = tester.test_api_initialization()
        
        # Test authorization URL generation
        tester.test_results["auth_url"] = tester.test_authorization_url_generation()
        
        # Test token exchange
        tester.test_results["token_exchange"] = await tester.test_token_exchange()
        
        # Test API calls
        tester.test_results["api_calls"] = await tester.test_api_calls()
        
        # Generate summary
        success = tester.generate_oauth_flow_summary()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"Error testing OAuth flow: {e}")
        print(f"\n❌ Error testing OAuth flow: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 