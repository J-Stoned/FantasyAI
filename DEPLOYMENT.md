# Deployment Guide - Fantasy AI Ultimate

## Current Deployment

The application is currently deployed at: https://fantasyai.onrender.com

## Environment Configuration

### Required Environment Variables

1. **Yahoo Fantasy API**:
   ```
   YAHOO_CLIENT_ID=your_client_id
   YAHOO_CLIENT_SECRET=your_client_secret
   YAHOO_REDIRECT_URI=https://fantasyai.onrender.com/auth/callback
   ```

2. **Database Configuration**:
   ```
   DATABASE_URL=postgresql://user:password@host:port/dbname
   ```

3. **Desktop Database Access** (Optional):
   ```
   DESKTOP_DATABASE_URL=postgresql://postgres:postgres@10.0.0.231:5432/fantasy_ai_local
   ENABLE_DESKTOP_SYNC=true
   ```
   Note: Desktop database access will only work if:
   - The desktop is accessible from the deployment environment
   - You set up a VPN or tunnel (e.g., ngrok, Tailscale)
   - Or use a cloud-hosted PostgreSQL instance

4. **Security**:
   ```
   SECRET_KEY=your-production-secret-key
   ```

### Important Yahoo API Configuration

You must update your Yahoo App settings to include the production callback URL:
1. Go to https://developer.yahoo.com/apps/
2. Select your app
3. Add `https://fantasyai.onrender.com/auth/callback` to the Redirect URI(s)
4. Save the changes

## Deployment Steps

### For Render.com

1. **Connect GitHub Repository**:
   - Connect your GitHub repository to Render
   - Select the `fantasy-ai-merged` directory as the root

2. **Configure Build Settings**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables** in Render Dashboard:
   - Add all required environment variables listed above
   - Ensure `YAHOO_REDIRECT_URI` matches your Render URL

4. **Deploy**:
   - Trigger a manual deploy or push to your connected branch

## Testing the Deployment

Run the test script to verify all endpoints:

```bash
python test_api_endpoints.py
```

This will test:
- Desktop database connectivity (if configured)
- Yahoo API integration
- All new unified data endpoints

## API Endpoints

### Desktop Database Endpoints
- `GET /desktop/status` - Check connection status
- `GET /desktop/players/{sport}` - Get player data
- `GET /desktop/dfs-slate/{sport}` - Get DFS slate information
- `GET /desktop/injuries` - Get injury reports

### Unified Data Endpoints
- `GET /unified/player/{player_name}` - Get comprehensive player data
- `GET /unified/optimization/{sport}` - Get lineup optimization data

### Yahoo Fantasy Endpoints
- `GET /auth/authorize` - Start OAuth2 flow
- `GET /auth/callback` - OAuth2 callback
- `GET /yahoo/leagues` - Get user leagues
- `GET /yahoo/league/{league_id}` - Get league details
- `GET /yahoo/players/{league_id}` - Get league players

## Troubleshooting

### Desktop Database Connection Issues

If the desktop database is not accessible from production:

1. **Option 1: Use a VPN**
   - Set up Tailscale or similar VPN
   - Connect both desktop and Render to the same VPN

2. **Option 2: Use ngrok**
   - Run ngrok on desktop: `ngrok tcp 5432`
   - Update `DESKTOP_DATABASE_URL` with ngrok URL

3. **Option 3: Migrate to Cloud**
   - Export data from desktop PostgreSQL
   - Import to a cloud PostgreSQL service (Supabase, Neon, etc.)
   - Update `DESKTOP_DATABASE_URL` to cloud instance

### Yahoo OAuth Issues

If OAuth2 authentication fails:
1. Verify redirect URI matches exactly in Yahoo App settings
2. Check that client ID and secret are correct
3. Ensure cookies are enabled (required for state parameter)

## Monitoring

Check application health:
- Health endpoint: `GET /health`
- Metrics endpoint: `GET /metrics` (if enabled)

## Updates

To deploy updates:
1. Push changes to GitHub
2. Render will automatically deploy (if auto-deploy is enabled)
3. Or trigger manual deploy in Render dashboard