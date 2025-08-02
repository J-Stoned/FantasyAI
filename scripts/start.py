#!/usr/bin/env python3
"""
Startup script for Fantasy AI Ultimate - Merged Project
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
# Add the root directory to the Python path for config
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
import uvicorn
from config.settings import settings

def setup_logging():
    """Setup logging configuration"""
    handlers = [logging.StreamHandler()]
    
    # Only add file handler if log_file is specified
    if settings.log_file:
        handlers.append(logging.FileHandler(settings.log_file))
    
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

def check_environment():
    """Check if required environment variables are set"""
    required_vars = [
        "YAHOO_CLIENT_ID",
        "YAHOO_CLIENT_SECRET"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("Warning: The following environment variables are not set:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nSome features may not work properly.")
        print("Please check the env.example file for required variables.")

def main():
    """Main startup function"""
    print("Starting Fantasy AI Ultimate - Merged Project")
    print(f"Version: {settings.app_version}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    # Setup logging
    setup_logging()
    
    # Check environment
    check_environment()
    
    # Create necessary directories
    os.makedirs("models", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    print(f"\nAPI will be available at: http://{settings.api_host}:{settings.api_port}")
    print(f"API Documentation: http://{settings.api_host}:{settings.api_port}/docs")
    print(f"Interactive API: http://{settings.api_host}:{settings.api_port}/redoc")
    
    # Start the server
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

if __name__ == "__main__":
    main() 