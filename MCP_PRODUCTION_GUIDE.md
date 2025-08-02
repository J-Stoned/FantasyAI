# MCP Servers for Fantasy AI Production

## Overview
MCP (Model Context Protocol) servers extend Claude's capabilities for production deployment and management.

## Recommended MCP Servers

### 1. Filesystem Server
**Purpose**: Secure file operations within your project
```bash
claude mcp add filesystem "npx -y @modelcontextprotocol/server-filesystem ."
```

**Use cases**:
- Read/write configuration files
- Manage deployment scripts
- Update environment files
- Access logs and build artifacts

### 2. GitHub Server
**Purpose**: Repository management and CI/CD integration
```bash
# First, create a GitHub token at: https://github.com/settings/tokens
claude mcp add github "npx -y @modelcontextprotocol/server-github" -e GITHUB_PERSONAL_ACCESS_TOKEN="${GITHUB_TOKEN}"
```

**Use cases**:
- Create pull requests
- Manage issues
- Trigger deployments
- Update repository settings
- Monitor workflow runs

### 3. Fetch Server
**Purpose**: Web content fetching and API testing
```bash
claude mcp add fetch "npx -y @modelcontextprotocol/server-fetch"
```

**Use cases**:
- Test production APIs
- Monitor endpoint health
- Fetch deployment status
- Verify OAuth endpoints

## Quick Setup

1. **Run the setup script**:
```bash
python setup_mcp_servers.py
```

2. **Verify installation**:
```bash
claude mcp list
```

3. **Test a server**:
```bash
# Test filesystem access
claude "Using the filesystem MCP server, list files in the current directory"

# Test GitHub (if configured)
claude "Using the GitHub MCP server, show my recent repositories"
```

## Production Workflows

### Deployment Checklist
With MCP servers, Claude can help you:

1. **Pre-deployment**:
   - Check git status
   - Run tests
   - Update version numbers
   - Create release notes

2. **Deployment**:
   - Push to GitHub
   - Create release tags
   - Monitor deployment status
   - Update documentation

3. **Post-deployment**:
   - Verify production endpoints
   - Check error logs
   - Update status pages
   - Create deployment report

### Example Commands

```bash
# Check deployment readiness
claude "Using filesystem server, check if all tests pass and create a deployment checklist"

# Deploy to production
claude "Using GitHub server, create a new release tag and push to main branch"

# Verify deployment
claude "Using fetch server, test the production OAuth endpoint at https://fantasy-ai-oauth.onrender.com"
```

## Environment Variables

Create `.env.mcp` for sensitive data:
```env
GITHUB_TOKEN=your_github_personal_access_token
RENDER_API_KEY=your_render_api_key
YAHOO_CLIENT_ID=your_yahoo_client_id
```

## Security Notes

1. **Never commit** `.env.mcp` to version control
2. **Use minimal permissions** for GitHub tokens
3. **Restrict filesystem access** to project directory
4. **Rotate tokens regularly**

## Additional Servers to Consider

### For Enhanced Production Management:

1. **PostgreSQL Server** (if using PostgreSQL):
```bash
claude mcp add postgres "npx -y @modelcontextprotocol/server-postgres" -e DATABASE_URL="${DATABASE_URL}"
```

2. **Slack Server** (for notifications):
```bash
claude mcp add slack "npx -y @modelcontextprotocol/server-slack" -e SLACK_TOKEN="${SLACK_TOKEN}"
```

3. **Sentry Server** (for error tracking):
```bash
claude mcp add sentry "npx -y @modelcontextprotocol/server-sentry" -e SENTRY_AUTH_TOKEN="${SENTRY_TOKEN}"
```

## Troubleshooting

If servers aren't working:

1. **Check Node.js**: `node --version` (should be 16+)
2. **Reinstall server**: `npm install -g @modelcontextprotocol/server-name`
3. **Check logs**: `claude mcp logs <server-name>`
4. **Restart Claude**: Sometimes needed after adding servers

## Next Steps

1. Set up the basic three servers (filesystem, github, fetch)
2. Add your GitHub token for repository management
3. Test each server with simple commands
4. Integrate into your deployment workflow

These MCP servers will significantly enhance Claude's ability to help with your production deployment and management tasks!