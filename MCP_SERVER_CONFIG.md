# MCP Server Configuration for Fantasy AI

## Current MCP Servers Configured

### ✅ Configured Servers:

1. **filesystem** - File operations within project directory
2. **github** - GitHub repository management  
3. **fetch** - Web content fetching
4. **sqlite** - SQLite database queries
5. **git** - Local git operations
6. **memory** - Persistent context storage
7. **sequential-thinking** - Complex problem solving
8. **context7** - Context management (needs API key)
9. **firecrawl** - Web scraping (needs API key)
10. **playwright** - Browser automation testing with Playwright
11. **puppeteer** - Browser automation with Puppeteer

## Server Configuration Details

### 1. Filesystem Server
- **Status**: Ready to use
- **Purpose**: Read/write files in your project
- **No additional config needed**

### 2. GitHub Server
- **Status**: Needs GitHub token
- **Configuration**:
```bash
# Create a GitHub Personal Access Token at:
# https://github.com/settings/tokens/new
# Scopes needed: repo, workflow

# Add to environment:
claude mcp update github -e GITHUB_PERSONAL_ACCESS_TOKEN="your_token_here"
```

### 3. Fetch Server
- **Status**: Ready to use
- **Purpose**: Fetch web content, test APIs
- **No additional config needed**

### 4. SQLite Server
- **Status**: Ready to use
- **Purpose**: Query your local database
- **Configured for**: `./fantasy_ai.db`

### 5. Git Server
- **Status**: Ready to use
- **Purpose**: Git operations on current repository
- **No additional config needed**

### 6. Memory Server
- **Status**: Ready to use
- **Purpose**: Persistent memory across sessions
- **No additional config needed**

### 7. Sequential Thinking Server
- **Status**: Ready to use
- **Purpose**: Step-by-step problem solving
- **No additional config needed**

### 8. Context7 Server
- **Status**: Needs API key
- **Configuration**:
```bash
# Get API key from: https://context7.com
claude mcp update context7 -e CONTEXT7_API_KEY="your_api_key"
```

### 9. Firecrawl Server
- **Status**: Needs API key
- **Configuration**:
```bash
# Get API key from: https://firecrawl.dev
claude mcp update firecrawl -e FIRECRAWL_API_KEY="your_api_key"
```

### 10. Playwright Server
- **Status**: Ready to use
- **Purpose**: Browser automation testing with Playwright
- **Features**: Web testing, form filling, screenshot capture
- **No additional config needed**

### 11. Puppeteer Server
- **Status**: Ready to use
- **Purpose**: Headless browser automation
- **Features**: Web scraping, PDF generation, testing
- **No additional config needed**

## Quick Setup Commands

### 1. Add GitHub Token
```bash
claude mcp update github -e GITHUB_PERSONAL_ACCESS_TOKEN="ghp_xxxxxxxxxxxx"
```

### 2. Test Servers
```bash
# Test filesystem
claude "Using the filesystem server, list files in src directory"

# Test SQLite
claude "Using the sqlite server, show tables in the database"

# Test git
claude "Using the git server, show recent commits"

# Test memory
claude "Using the memory server, remember that this is a Fantasy AI project"
```

## Environment File Setup

Create `.env.mcp` file:
```env
# GitHub
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here

# Context7 (if you have an account)
CONTEXT7_API_KEY=your_context7_key

# Firecrawl (if you have an account)
FIRECRAWL_API_KEY=your_firecrawl_key
```

## Restart Required

After configuring environment variables, you may need to:
1. Restart Claude Code
2. Or reload the window

## Troubleshooting

If servers show "Failed to connect":
1. This is normal on first run - npx will download packages
2. Try using a server - it will auto-download dependencies
3. If still failing, check Node.js is in PATH: `node --version`

## Production Use Cases

### For Deployment:
- **filesystem**: Update config files
- **git**: Create tags, check status
- **github**: Create releases, manage PRs

### For Monitoring:
- **fetch**: Test production endpoints
- **sqlite**: Query local development data

### For Development:
- **memory**: Track project context
- **sequential-thinking**: Plan features
- **firecrawl**: Scrape sports data (with API key)