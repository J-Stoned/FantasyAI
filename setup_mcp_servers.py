#!/usr/bin/env python3
"""
Setup MCP servers for Fantasy AI production deployment
"""

import subprocess
import os
import json

def run_command(cmd):
    """Run a command and return its output"""
    try:
        # Use explicit shell on Windows
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, executable=None)
        if result.returncode == 0:
            print(f"[OK] {cmd}")
            return result.stdout
        else:
            print(f"[ERROR] {cmd}")
            print(f"Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to run command: {e}")
        return None

def setup_mcp_servers():
    """Setup MCP servers for production use"""
    
    print("Setting up MCP servers for Fantasy AI production...")
    print("=" * 50)
    
    # Check if Node.js is installed
    print("\n1. Checking Node.js installation...")
    node_version = run_command("node --version")
    if not node_version:
        print("Node.js is not installed. Please install Node.js first.")
        print("Download from: https://nodejs.org/")
        return False
    
    # Install MCP servers globally
    print("\n2. Installing MCP servers...")
    servers = [
        "@modelcontextprotocol/server-filesystem",
        "@modelcontextprotocol/server-github", 
        "@modelcontextprotocol/server-fetch"
    ]
    
    for server in servers:
        print(f"\nInstalling {server}...")
        run_command(f"npm install -g {server}")
    
    # Create environment file for GitHub token
    print("\n3. Setting up environment variables...")
    env_file = ".env.mcp"
    
    if not os.path.exists(env_file):
        github_token = input("Enter your GitHub Personal Access Token (or press Enter to skip): ").strip()
        
        with open(env_file, 'w') as f:
            f.write("# MCP Server Environment Variables\n")
            if github_token:
                f.write(f"GITHUB_TOKEN={github_token}\n")
            f.write("\n# Add other environment variables as needed\n")
        
        print(f"[OK] Created {env_file}")
    else:
        print(f"[OK] {env_file} already exists")
    
    # Add MCP servers using Claude CLI
    print("\n4. Configuring MCP servers in Claude...")
    
    # Get current directory
    current_dir = os.getcwd()
    
    # Add filesystem server
    print("\nAdding filesystem server...")
    run_command(f'claude mcp add filesystem "npx -y @modelcontextprotocol/server-filesystem {current_dir}"')
    
    # Add GitHub server (with token if available)
    print("\nAdding GitHub server...")
    if os.path.exists(env_file):
        run_command('claude mcp add github "npx -y @modelcontextprotocol/server-github" -e GITHUB_PERSONAL_ACCESS_TOKEN="${GITHUB_TOKEN}"')
    else:
        run_command('claude mcp add github "npx -y @modelcontextprotocol/server-github"')
    
    # Add fetch server
    print("\nAdding fetch server...")
    run_command('claude mcp add fetch "npx -y @modelcontextprotocol/server-fetch"')
    
    print("\n" + "=" * 50)
    print("MCP Server Setup Complete!")
    print("\nAvailable servers:")
    print("- filesystem: File operations within your project")
    print("- github: GitHub repository management") 
    print("- fetch: Web content fetching and API testing")
    
    print("\nTo verify setup, run: claude mcp list")
    print("To use in production, these servers will help with:")
    print("- Deployment automation")
    print("- File management") 
    print("- GitHub integration")
    print("- API testing and monitoring")
    
    return True

if __name__ == "__main__":
    setup_mcp_servers()