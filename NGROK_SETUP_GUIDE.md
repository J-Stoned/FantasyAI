# Ngrok Setup Guide for Yahoo OAuth

Ngrok requires a free account to use. Here's how to set it up:

## Step 1: Create Free Ngrok Account

1. Go to: https://dashboard.ngrok.com/signup
2. Sign up with your email (it's free)
3. Verify your email

## Step 2: Get Your Auth Token

1. After signing in, go to: https://dashboard.ngrok.com/get-started/your-authtoken
2. Copy your auth token (looks like: `2abc123XYZ...`)

## Step 3: Configure Ngrok

Run this command with your auth token:
```bash
ngrok.exe authtoken YOUR_AUTH_TOKEN_HERE
```

Or I've created a script for you:
```bash
python setup_ngrok_auth.py
```

## Step 4: Run the OAuth Setup

Once ngrok is configured with your auth token:
```bash
python run_oauth_with_ngrok.py
```

This will:
1. Start your FastAPI server
2. Start ngrok with HTTPS tunnel
3. Update your .env file automatically
4. Show you exactly what to update in Yahoo Developer Console

## Manual Steps (Alternative)

If you prefer to do it manually:

1. **Terminal 1** - Start your server:
   ```bash
   python scripts/start.py
   ```

2. **Terminal 2** - Start ngrok:
   ```bash
   ngrok.exe http 8000
   ```

3. You'll see something like:
   ```
   Forwarding: https://abc123.ngrok-free.app -> http://localhost:8000
   ```

4. Update your `.env` file:
   ```
   YAHOO_REDIRECT_URI=https://abc123.ngrok-free.app/auth/callback
   ```

5. Update Yahoo Developer Console with the same URL

6. Restart your server and try OAuth!

## Important Notes

- The ngrok URL changes each time you restart it
- You'll need to update Yahoo Developer Console each time
- The free tier is perfect for development
- Keep ngrok running while testing OAuth