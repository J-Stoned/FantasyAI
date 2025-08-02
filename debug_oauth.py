#!/usr/bin/env python3
"""
Yahoo OAuth Debugging Script
This script helps diagnose and fix OAuth issues with the Yahoo Fantasy API
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs
import requests
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from yahoo_wrapper import YahooFantasyAPI
from config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class YahooOAuthDebugger:
    """Debug Yahoo OAuth configuration and flow"""
    
    def __init__(self):
        self.yahoo_api = YahooFantasyAPI()
        self.debug_results = {}
    
    def check_environment_variables(self) -> Dict[str, Any]:
        """Check if required environment variables are set"""
        logger.info("Checking environment variables...")
        
        results = {
            "yahoo_client_id": {
                "set": bool(os.getenv("YAHOO_CLIENT_ID")),
                "value": os.getenv("YAHOO_CLIENT_ID", "NOT_SET")[:20] + "..." if os.getenv("YAHOO_CLIENT_ID") else "NOT_SET",
                "length": len(os.getenv("YAHOO_CLIENT_ID", ""))
            },
            "yahoo_client_secret": {
                "set": bool(os.getenv("YAHOO_CLIENT_SECRET")),
                "value": "***" + os.getenv("YAHOO_CLIENT_SECRET", "")[-4:] if os.getenv("YAHOO_CLIENT_SECRET") else "NOT_SET",
                "length": len(os.getenv("YAHOO_CLIENT_SECRET", ""))
            },
            "yahoo_redirect_uri": {
                "set": bool(os.getenv("YAHOO_REDIRECT_URI")),
                "value": os.getenv("YAHOO_REDIRECT_URI", "NOT_SET")
            }
        }
        
        # Check if .env file exists
        env_file_path = os.path.join(os.path.dirname(__file__), '.env')
        results["env_file"] = {
            "exists": os.path.exists(env_file_path),
            "path": env_file_path
        }
        
        logger.info(f"Environment variables check: {results}")
        return results
    
    def check_yahoo_api_configuration(self) -> Dict[str, Any]:
        """Check Yahoo API configuration"""
        logger.info("Checking Yahoo API configuration...")
        
        results = {
            "client_id": {
                "set": bool(self.yahoo_api.client_id),
                "value": self.yahoo_api.client_id[:20] + "..." if self.yahoo_api.client_id else "NOT_SET",
                "length": len(self.yahoo_api.client_id) if self.yahoo_api.client_id else 0
            },
            "client_secret": {
                "set": bool(self.yahoo_api.client_secret),
                "value": "***" + self.yahoo_api.client_secret[-4:] if self.yahoo_api.client_secret else "NOT_SET",
                "length": len(self.yahoo_api.client_secret) if self.yahoo_api.client_secret else 0
            },
            "redirect_uri": {
                "set": bool(self.yahoo_api.redirect_uri),
                "value": self.yahoo_api.redirect_uri
            },
            "auth_url": self.yahoo_api.auth_url,
            "token_url": self.yahoo_api.token_url,
            "base_url": self.yahoo_api.base_url
        }
        
        logger.info(f"Yahoo API configuration: {results}")
        return results
    
    def test_oauth_url_generation(self) -> Dict[str, Any]:
        """Test OAuth URL generation"""
        logger.info("Testing OAuth URL generation...")
        
        try:
            auth_url = self.yahoo_api.get_authorization_url()
            results = {
                "success": True,
                "auth_url": auth_url,
                "url_length": len(auth_url),
                "is_mock": "mock-callback" in auth_url
            }
        except Exception as e:
            results = {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
        
        logger.info(f"OAuth URL generation test: {results}")
        return results
    
    def test_yahoo_api_endpoints(self) -> Dict[str, Any]:
        """Test Yahoo API endpoints connectivity"""
        logger.info("Testing Yahoo API endpoints...")
        
        endpoints = {
            "auth_url": self.yahoo_api.auth_url,
            "token_url": self.yahoo_api.token_url,
            "base_url": self.yahoo_api.base_url
        }
        
        results = {}
        for name, url in endpoints.items():
            try:
                response = requests.get(url, timeout=10)
                results[name] = {
                    "reachable": True,
                    "status_code": response.status_code,
                    "content_length": len(response.content)
                }
            except requests.exceptions.RequestException as e:
                results[name] = {
                    "reachable": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
        
        logger.info(f"Yahoo API endpoints test: {results}")
        return results
    
    def check_redirect_uri_registration(self) -> Dict[str, Any]:
        """Check if redirect URI is properly registered"""
        logger.info("Checking redirect URI registration...")
        
        redirect_uri = self.yahoo_api.redirect_uri
        parsed_uri = urlparse(redirect_uri)
        
        results = {
            "redirect_uri": redirect_uri,
            "scheme": parsed_uri.scheme,
            "netloc": parsed_uri.netloc,
            "path": parsed_uri.path,
            "is_localhost": parsed_uri.netloc.startswith("localhost"),
            "port": parsed_uri.port,
            "recommendations": []
        }
        
        # Add recommendations
        if not results["is_localhost"]:
            results["recommendations"].append("Consider using localhost for development")
        
        if not results["port"]:
            results["recommendations"].append("Consider adding explicit port (e.g., :8000)")
        
        if not redirect_uri.endswith("/auth/callback"):
            results["recommendations"].append("Ensure redirect URI ends with /auth/callback")
        
        logger.info(f"Redirect URI registration check: {results}")
        return results
    
    def generate_fix_recommendations(self) -> Dict[str, Any]:
        """Generate recommendations to fix OAuth issues"""
        logger.info("Generating fix recommendations...")
        
        recommendations = {
            "immediate_actions": [],
            "configuration_fixes": [],
            "development_setup": [],
            "production_considerations": []
        }
        
        # Check environment variables
        env_check = self.check_environment_variables()
        if not env_check["yahoo_client_id"]["set"]:
            recommendations["immediate_actions"].append(
                "Set YAHOO_CLIENT_ID environment variable"
            )
        
        if not env_check["yahoo_client_secret"]["set"]:
            recommendations["immediate_actions"].append(
                "Set YAHOO_CLIENT_SECRET environment variable"
            )
        
        if not env_check["env_file"]["exists"]:
            recommendations["configuration_fixes"].append(
                "Create .env file from env.example template"
            )
        
        # Check API configuration
        api_check = self.check_yahoo_api_configuration()
        if not api_check["client_id"]["set"]:
            recommendations["immediate_actions"].append(
                "Configure Yahoo client ID in the API wrapper"
            )
        
        # Check redirect URI
        redirect_check = self.check_redirect_uri_registration()
        recommendations["configuration_fixes"].extend(redirect_check["recommendations"])
        
        # Development setup
        recommendations["development_setup"].extend([
            "Ensure your application is running on the correct port",
            "Verify that the redirect URI matches exactly in Yahoo Developer Console",
            "Test OAuth flow with a simple callback endpoint",
            "Use mock OAuth flow for development if needed"
        ])
        
        # Production considerations
        recommendations["production_considerations"].extend([
            "Use HTTPS for production redirect URIs",
            "Implement proper state parameter validation",
            "Add error handling for OAuth failures",
            "Implement token refresh logic",
            "Use secure storage for tokens"
        ])
        
        logger.info(f"Generated recommendations: {recommendations}")
        return recommendations
    
    def run_full_diagnostic(self) -> Dict[str, Any]:
        """Run complete OAuth diagnostic"""
        logger.info("Running full OAuth diagnostic...")
        
        diagnostic = {
            "timestamp": datetime.now().isoformat(),
            "environment_variables": self.check_environment_variables(),
            "yahoo_api_configuration": self.check_yahoo_api_configuration(),
            "oauth_url_generation": self.test_oauth_url_generation(),
            "api_endpoints": self.test_yahoo_api_endpoints(),
            "redirect_uri_registration": self.check_redirect_uri_registration(),
            "recommendations": self.generate_fix_recommendations()
        }
        
        # Add summary
        issues = []
        if not diagnostic["environment_variables"]["yahoo_client_id"]["set"]:
            issues.append("Missing YAHOO_CLIENT_ID")
        if not diagnostic["environment_variables"]["yahoo_client_secret"]["set"]:
            issues.append("Missing YAHOO_CLIENT_SECRET")
        if not diagnostic["oauth_url_generation"]["success"]:
            issues.append("OAuth URL generation failed")
        
        diagnostic["summary"] = {
            "total_issues": len(issues),
            "issues": issues,
            "status": "FAILED" if issues else "PASSED"
        }
        
        return diagnostic
    
    def print_diagnostic_report(self, diagnostic: Dict[str, Any]):
        """Print a formatted diagnostic report"""
        print("\n" + "="*80)
        print("YAHOO OAUTH DIAGNOSTIC REPORT")
        print("="*80)
        print(f"Timestamp: {diagnostic['timestamp']}")
        print(f"Status: {diagnostic['summary']['status']}")
        print(f"Total Issues: {diagnostic['summary']['total_issues']}")
        
        if diagnostic['summary']['issues']:
            print("\nISSUES FOUND:")
            for issue in diagnostic['summary']['issues']:
                print(f"  ❌ {issue}")
        
        print("\n" + "-"*80)
        print("ENVIRONMENT VARIABLES")
        print("-"*80)
        env_vars = diagnostic['environment_variables']
        for key, value in env_vars.items():
            if key != "env_file":
                status = "✅" if value["set"] else "❌"
                print(f"  {status} {key}: {value['value']}")
        
        print(f"  {'✅' if env_vars['env_file']['exists'] else '❌'} .env file: {env_vars['env_file']['path']}")
        
        print("\n" + "-"*80)
        print("YAHOO API CONFIGURATION")
        print("-"*80)
        api_config = diagnostic['yahoo_api_configuration']
        for key, value in api_config.items():
            if key in ['client_id', 'client_secret', 'redirect_uri']:
                status = "✅" if value["set"] else "❌"
                print(f"  {status} {key}: {value['value']}")
            else:
                print(f"  ℹ️  {key}: {value}")
        
        print("\n" + "-"*80)
        print("OAUTH URL GENERATION")
        print("-"*80)
        oauth_test = diagnostic['oauth_url_generation']
        if oauth_test['success']:
            print(f"  ✅ Success: {oauth_test['auth_url']}")
            if oauth_test['is_mock']:
                print("  ⚠️  Using mock OAuth flow")
        else:
            print(f"  ❌ Failed: {oauth_test['error']}")
        
        print("\n" + "-"*80)
        print("RECOMMENDATIONS")
        print("-"*80)
        recs = diagnostic['recommendations']
        
        if recs['immediate_actions']:
            print("\nIMMEDIATE ACTIONS:")
            for action in recs['immediate_actions']:
                print(f"  🔧 {action}")
        
        if recs['configuration_fixes']:
            print("\nCONFIGURATION FIXES:")
            for fix in recs['configuration_fixes']:
                print(f"  ⚙️  {fix}")
        
        if recs['development_setup']:
            print("\nDEVELOPMENT SETUP:")
            for setup in recs['development_setup']:
                print(f"  🛠️  {setup}")
        
        print("\n" + "="*80)
    
    def save_diagnostic_report(self, diagnostic: Dict[str, Any], filename: str = "oauth_diagnostic.json"):
        """Save diagnostic report to file"""
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, 'w') as f:
            json.dump(diagnostic, f, indent=2)
        logger.info(f"Diagnostic report saved to: {filepath}")
        return filepath

def main():
    """Main function to run OAuth diagnostic"""
    print("Yahoo OAuth Debugging Tool")
    print("="*50)
    
    debugger = YahooOAuthDebugger()
    
    try:
        # Run full diagnostic
        diagnostic = debugger.run_full_diagnostic()
        
        # Print report
        debugger.print_diagnostic_report(diagnostic)
        
        # Save report
        report_file = debugger.save_diagnostic_report(diagnostic)
        print(f"\nDetailed report saved to: {report_file}")
        
        # Exit with appropriate code
        if diagnostic['summary']['status'] == 'FAILED':
            print("\n❌ OAuth configuration has issues that need to be fixed.")
            sys.exit(1)
        else:
            print("\n✅ OAuth configuration looks good!")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Error running diagnostic: {e}")
        print(f"\n❌ Error running diagnostic: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 