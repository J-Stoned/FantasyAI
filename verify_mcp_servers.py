#!/usr/bin/env python3
"""
Verify MCP Server Configuration
"""

import subprocess
import os
import json

def check_node():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] Node.js installed: {result.stdout.strip()}")
            return True
        else:
            print("[ERROR] Node.js not found")
            return False
    except:
        print("[ERROR] Node.js not found in PATH")
        return False

def check_npm():
    """Check if npm is installed"""
    try:
        # Try npm.cmd on Windows
        result = subprocess.run(["npm.cmd", "--version"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"[OK] npm installed: {result.stdout.strip()}")
            return True
        else:
            print("[ERROR] npm not found")
            return False
    except:
        print("[ERROR] npm not found in PATH")
        return False

def check_mcp_servers():
    """Check MCP server status"""
    print("\n[SERVERS] MCP Server Status:")
    print("=" * 50)
    
    # Run claude mcp list
    try:
        result = subprocess.run(["claude", "mcp", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("Error checking MCP servers:", result.stderr)
    except Exception as e:
        print(f"Error running claude mcp list: {e}")

def check_env_vars():
    """Check environment variables"""
    print("\n[ENV] Environment Variables:")
    print("=" * 50)
    
    env_vars = {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "GitHub integration",
        "CONTEXT7_API_KEY": "Context7 server",
        "FIRECRAWL_API_KEY": "Firecrawl server",
        "YAHOO_CLIENT_ID": "Yahoo OAuth",
        "YAHOO_CLIENT_SECRET": "Yahoo OAuth"
    }
    
    for var, description in env_vars.items():
        if os.getenv(var):
            print(f"[OK] {var} is set ({description})")
        else:
            print(f"[WARNING] {var} not set ({description})")

def check_database():
    """Check if SQLite database exists"""
    print("\n[DB] Database Check:")
    print("=" * 50)
    
    if os.path.exists("fantasy_ai.db"):
        size = os.path.getsize("fantasy_ai.db") / 1024  # KB
        print(f"[OK] fantasy_ai.db exists ({size:.1f} KB)")
    else:
        print("[WARNING] fantasy_ai.db not found")

def suggest_fixes():
    """Suggest fixes for common issues"""
    print("\n[TIPS] Quick Fixes:")
    print("=" * 50)
    print("1. If servers show 'Failed to connect' - this is normal")
    print("   They will download dependencies on first use")
    print("\n2. To add GitHub token:")
    print('   claude mcp update github -e GITHUB_PERSONAL_ACCESS_TOKEN="your_token"')
    print("\n3. To test a server:")
    print('   claude "Using the filesystem server, list files in the current directory"')
    print("\n4. For production deployment:")
    print("   - Push code to GitHub")
    print("   - Deploy to Render.com")
    print("   - Update Yahoo redirect URI")

def main():
    print("[ROCKET] MCP Server Configuration Verification")
    print("=" * 50)
    
    # Check prerequisites
    node_ok = check_node()
    npm_ok = check_npm()
    
    # Continue even if npm check fails (it might still work)
    if not node_ok:
        print("\n[ERROR] Node.js is required for MCP servers")
        print("   Download from: https://nodejs.org/")
        return
    
    # Check MCP servers
    check_mcp_servers()
    
    # Check environment
    check_env_vars()
    
    # Check database
    check_database()
    
    # Suggestions
    suggest_fixes()
    
    print("\n[DONE] Configuration check complete!")

if __name__ == "__main__":
    main()