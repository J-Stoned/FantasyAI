# Testing Guide for Fantasy AI with MCP Servers

## Browser Testing with Playwright & Puppeteer

### Available Testing Servers

1. **playwright** - Modern browser automation with Playwright
2. **puppeteer** - Headless Chrome automation

## Test Scenarios for Fantasy AI

### 1. OAuth Flow Testing
```bash
# Test Yahoo OAuth flow
claude "Using the playwright server, test the OAuth login flow at http://localhost:8000"
```

### 2. API Endpoint Testing
```bash
# Test API endpoints
claude "Using the fetch server, test all API endpoints at http://localhost:8000/docs"
```

### 3. Database Integration Testing
```bash
# Test database operations
claude "Using the sqlite server, verify all tables are created correctly in fantasy_ai.db"
```

### 4. End-to-End Testing
```bash
# Full user journey test
claude "Using the playwright server, test the complete user flow from login to viewing fantasy stats"
```

## Example Test Scripts

### OAuth Flow Test with Playwright
```python
# test_oauth_flow.py
async def test_yahoo_oauth():
    """Test Yahoo OAuth authentication flow"""
    # Using playwright MCP server
    # 1. Navigate to homepage
    # 2. Click "Login with Yahoo"
    # 3. Verify redirect to Yahoo
    # 4. Check callback handling
    pass
```

### API Health Check
```python
# test_api_health.py
def test_api_endpoints():
    """Test all API endpoints are responding"""
    endpoints = [
        "/",
        "/api/health",
        "/api/leagues",
        "/api/players"
    ]
    # Using fetch MCP server to test each endpoint
```

### Database Verification
```sql
-- Using sqlite MCP server
-- Check tables exist
SELECT name FROM sqlite_master WHERE type='table';

-- Verify schema
SELECT sql FROM sqlite_master WHERE name='users';
```

## Production Testing Checklist

### Pre-Deployment Tests
- [ ] OAuth flow works locally
- [ ] All API endpoints return correct status codes
- [ ] Database migrations complete successfully
- [ ] Environment variables are properly set

### Post-Deployment Tests (on Render)
- [ ] Production URL is accessible
- [ ] HTTPS certificate is valid
- [ ] OAuth redirect works with production URL
- [ ] API rate limiting is functional

## Automated Testing Commands

### Run All Tests
```bash
# Using sequential-thinking server to plan test execution
claude "Using the sequential-thinking server, create and execute a comprehensive test plan for the Fantasy AI application"
```

### Browser Automation Test
```bash
# Visual regression testing
claude "Using the playwright server, take screenshots of all main pages and compare with baseline"
```

### Performance Testing
```bash
# Load testing with fetch server
claude "Using the fetch server, perform load testing on the /api/leagues endpoint with 100 concurrent requests"
```

## Testing with MCP Servers

### 1. Interactive Browser Testing
```bash
# Launch browser and interact
claude "Using the puppeteer server, launch a browser, navigate to our app, and take a screenshot"
```

### 2. Form Testing
```bash
# Test form submissions
claude "Using the playwright server, test the league creation form with various inputs"
```

### 3. Mobile Testing
```bash
# Test responsive design
claude "Using the playwright server, test the app in mobile viewport sizes"
```

## Continuous Testing

### GitHub Actions Integration
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          python -m pytest
          # Additional browser tests
```

### Monitoring Production
```bash
# Regular health checks
claude "Using the fetch server, set up a monitoring script that checks production endpoints every 5 minutes"
```

## Debugging Failed Tests

### View Browser Actions
```bash
# Debug with headed browser
claude "Using the playwright server with headed mode, slowly go through the OAuth flow so I can see what's happening"
```

### Check Network Requests
```bash
# Monitor API calls
claude "Using the playwright server, log all network requests during the login flow"
```

## Best Practices

1. **Test Early**: Run tests before pushing code
2. **Test Often**: Automate tests in CI/CD
3. **Test Realistically**: Use production-like data
4. **Test Comprehensively**: Cover edge cases
5. **Test Visually**: Screenshot comparisons

## Quick Test Commands

```bash
# Quick smoke test
claude "Run a quick smoke test of the main features using playwright"

# Full regression test
claude "Using sequential-thinking and playwright, run a full regression test suite"

# Performance baseline
claude "Using fetch server, establish performance baselines for all API endpoints"
```

Remember: The MCP servers will download Playwright/Puppeteer dependencies on first use, so the initial run may take longer.