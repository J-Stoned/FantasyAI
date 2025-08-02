#!/usr/bin/env python3
"""
Fix Yahoo OAuth Configuration
This script sets up the proper environment variables for Yahoo OAuth
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file with proper OAuth configuration"""
    env_content = """# Fantasy AI Ultimate - Merged Project Environment Variables

# Application Settings
APP_NAME=Fantasy AI Ultimate - Merged
APP_VERSION=1.0.0
DEBUG=true
ENVIRONMENT=development

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./fantasy_ai.db

# Redis Configuration (optional, for caching)
REDIS_URL=redis://localhost:6379

# Yahoo Fantasy API Credentials
# These are the credentials found in the yahoo_wrapper/__init__.py file
YAHOO_CLIENT_ID=dj0yJmk9cGw4M25lT3VVVHdQJmQ9WVdrOWEyOTBibUppTkhRbWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTdi
YAHOO_CLIENT_SECRET=2639bea571d9487162f21ad839365fcdf67dddb7
YAHOO_REDIRECT_URI=http://localhost:8000/auth/callback

# Security
SECRET_KEY=dev-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI/ML Settings
MODEL_CACHE_DIR=./models
PREDICTION_CONFIDENCE_THRESHOLD=0.7
MAX_ANALYSIS_WORKERS=4

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/fantasy_ai.log

# Cache Settings
CACHE_TTL_SECONDS=3600
PLAYER_CACHE_TTL=1800
LEAGUE_CACHE_TTL=7200

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Development Settings
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
"""
    
    env_file = Path(".env")
    if env_file.exists():
        print(f"⚠️  .env file already exists at {env_file.absolute()}")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Skipping .env file creation")
            return False
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Created .env file at {env_file.absolute()}")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def set_environment_variables():
    """Set environment variables for current session"""
    print("Setting environment variables for current session...")
    
    # Yahoo OAuth credentials from the code
    os.environ["YAHOO_CLIENT_ID"] = "dj0yJmk9cGw4M25lT3VVVHdQJmQ9WVdrOWEyOTBibUppTkhRbWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTdi"
    os.environ["YAHOO_CLIENT_SECRET"] = "2639bea571d9487162f21ad839365fcdf67dddb7"
    os.environ["YAHOO_REDIRECT_URI"] = "http://localhost:8000/auth/callback"
    
    print("✅ Environment variables set for current session")
    return True

def verify_configuration():
    """Verify that the configuration is working"""
    print("\nVerifying configuration...")
    
    # Check environment variables
    client_id = os.getenv("YAHOO_CLIENT_ID")
    client_secret = os.getenv("YAHOO_CLIENT_SECRET")
    redirect_uri = os.getenv("YAHOO_REDIRECT_URI")
    
    print(f"YAHOO_CLIENT_ID: {'✅ Set' if client_id else '❌ Not set'}")
    print(f"YAHOO_CLIENT_SECRET: {'✅ Set' if client_secret else '❌ Not set'}")
    print(f"YAHOO_REDIRECT_URI: {'✅ Set' if redirect_uri else '❌ Not set'}")
    
    if client_id and client_secret and redirect_uri:
        print("✅ All required environment variables are set!")
        return True
    else:
        print("❌ Some environment variables are missing")
        return False

def main():
    """Main function to fix OAuth configuration"""
    print("Yahoo OAuth Configuration Fix")
    print("="*40)
    
    # Create .env file
    env_created = create_env_file()
    
    # Set environment variables for current session
    env_set = set_environment_variables()
    
    # Verify configuration
    config_verified = verify_configuration()
    
    print("\n" + "="*40)
    print("SUMMARY")
    print("="*40)
    print(f"Environment file created: {'✅' if env_created else '❌'}")
    print(f"Environment variables set: {'✅' if env_set else '❌'}")
    print(f"Configuration verified: {'✅' if config_verified else '❌'}")
    
    if config_verified:
        print("\n🎉 OAuth configuration is now ready!")
        print("\nNext steps:")
        print("1. Run the OAuth diagnostic again: python debug_oauth.py")
        print("2. Test the OAuth flow with your application")
        print("3. Make sure your redirect URI is registered in Yahoo Developer Console")
    else:
        print("\n❌ Configuration still has issues")
        sys.exit(1)

if __name__ == "__main__":
    main() 