# HTTPS OAuth Setup Guide for Yahoo

Yahoo requires HTTPS for OAuth redirect URIs. Here are your options:

## Option 1: Use ngrok (Recommended for Development)

1. **Download ngrok**: https://ngrok.com/download
2. **Start your server normally**:
   ```bash
   python scripts/start.py
   ```
3. **In another terminal, run ngrok**:
   ```bash
   ngrok http 8000
   ```
4. **You'll get an HTTPS URL** like:
   ```
   https://abc123.ngrok.io
   ```
5. **Update your Yahoo app** redirect URI to:
   ```
   https://abc123.ngrok.io/auth/callback
   ```
6. **Update your .env** file:
   ```
   YAHOO_REDIRECT_URI=https://abc123.ngrok.io/auth/callback
   ```

## Option 2: Use Local HTTPS Certificate

1. **Generate a certificate**:
   ```bash
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
   ```
2. **Update start script** to use SSL
3. **Add certificate exception** in your browser

## Option 3: Deploy to a Service with HTTPS

Deploy to services that provide HTTPS automatically:
- Render.com
- Railway.app
- Heroku (with SSL addon)
- AWS/GCP/Azure with Load Balancer

## Current Setup Status

Your `.env` file has been updated to use HTTPS:
```
YAHOO_REDIRECT_URI=https://localhost:8000/auth/callback
```

**Next Steps**:
1. Choose one of the options above
2. Update your Yahoo app's redirect URI to match
3. Restart your application

## Testing with ngrok

Once ngrok is running:
1. Copy the HTTPS URL from ngrok
2. Update both Yahoo Developer Console and your `.env` file
3. Restart your app
4. The OAuth flow should work!

Remember: The ngrok URL changes each time you restart it, so you'll need to update your Yahoo app accordingly.