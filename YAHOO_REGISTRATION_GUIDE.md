# Yahoo Fantasy API Registration Guide

This guide will walk you through registering your application with Yahoo to use the real OAuth2 flow.

## Prerequisites

- Yahoo account (any Yahoo email account will work)
- Your application running on `http://localhost:8000`

## Step 1: Create a Yahoo App

1. Go to [Yahoo Developer Console](https://developer.yahoo.com/apps/)
2. Click **"Create an App"**
3. Sign in with your Yahoo account if prompted

## Step 2: Configure Your App

Fill in the following information:

### Application Details
- **Application Name**: Fantasy AI Ultimate (or your preferred name)
- **Application Type**: Installed Application
- **Description**: AI-powered fantasy sports analysis platform
- **Home Page URL**: http://localhost:8000

### OAuth 2.0 Redirect URI
- **Redirect URI**: `http://localhost:8000/auth/callback`
  
⚠️ **IMPORTANT**: This must match EXACTLY with what's in your `.env` file

### API Permissions
Select the following permissions:
- ✅ **Fantasy Sports** - Read
- ✅ **Fantasy Sports** - Read/Write (if you want to make changes)

## Step 3: Create the App

1. Review all settings
2. Accept the Yahoo Developer Terms
3. Click **"Create App"**

## Step 4: Get Your Credentials

After creating the app, you'll see:
- **Client ID** (App ID)
- **Client Secret** (App Secret)

## Step 5: Update Your .env File

Update your `.env` file with the new credentials:

```env
# Replace these with your actual values from Yahoo
YAHOO_CLIENT_ID=your_new_client_id_here
YAHOO_CLIENT_SECRET=your_new_client_secret_here
YAHOO_REDIRECT_URI=http://localhost:8000/auth/callback
```

## Step 6: Restart Your Application

```bash
# Stop your app if running
# Then restart it
python scripts/start.py
```

## Step 7: Test OAuth Flow

1. Visit http://localhost:8000
2. Click on "Authorize with Yahoo"
3. You'll be redirected to Yahoo's login page
4. Sign in with your Yahoo account
5. Grant permissions to your app
6. You'll be redirected back to your app

## Troubleshooting

### "Invalid redirect_uri" Error
- Ensure the redirect URI in Yahoo Developer Console matches EXACTLY with your `.env` file
- Check for trailing slashes or different ports
- The URI must be: `http://localhost:8000/auth/callback`

### "Invalid client" Error
- Double-check your Client ID and Secret
- Make sure there are no extra spaces or quotes in the `.env` file
- Restart your application after updating credentials

### "Access denied" Error
- Make sure you granted the necessary permissions
- Check that Fantasy Sports permissions are enabled in Yahoo Developer Console

### Token Expiration
- Yahoo access tokens expire after 1 hour
- The app will automatically refresh tokens using the refresh token
- Refresh tokens are valid for longer periods

## Production Considerations

For production deployment:

1. **Update Redirect URI**: Change from `http://localhost:8000` to your production URL (must be HTTPS)
2. **Secure Storage**: Store tokens in a secure database, not in memory
3. **State Validation**: Implement proper state parameter storage (Redis/Database)
4. **Error Handling**: Add comprehensive error handling for OAuth failures
5. **Rate Limiting**: Implement rate limiting to avoid Yahoo API limits

## API Rate Limits

Yahoo Fantasy API has the following limits:
- **Per Hour**: 2,000 requests per hour
- **Per Day**: 20,000 requests per day

Plan your API usage accordingly.

## Additional Resources

- [Yahoo Fantasy Sports API Documentation](https://developer.yahoo.com/fantasysports/)
- [OAuth 2.0 Guide](https://developer.yahoo.com/oauth2/guide/)
- [API Forums](https://developer.yahoo.com/forums/) 