# Deploy to Render.com - Elite Developer Way

## Why Render?
- **Free tier** with HTTPS
- **Automatic deploys** from GitHub
- **Stable URL** that Yahoo will accept
- **Zero configuration** headaches

## Step 1: Prepare Your Code

### Install Git (if not already)
```bash
git init
git add .
git commit -m "Initial commit for Yahoo OAuth"
```

### Create GitHub Repository
1. Go to https://github.com/new
2. Create a new repository (e.g., `fantasy-ai-oauth`)
3. Push your code:
```bash
git remote add origin https://github.com/YOUR_USERNAME/fantasy-ai-oauth.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy to Render

1. **Sign up** at https://render.com (free, use GitHub login)

2. **New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Select your repository

3. **Configure**:
   - **Name**: `fantasy-ai-oauth` (or whatever you want)
   - **Region**: Oregon (US West)
   - **Branch**: main
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

4. **Environment Variables** (click "Advanced"):
   Add these:
   - `PYTHONPATH` = `/opt/render/project/src:/opt/render/project/src`
   - `YAHOO_CLIENT_ID` = (your client ID)
   - `YAHOO_CLIENT_SECRET` = (your client secret)
   - `DATABASE_URL` = (leave empty, will use SQLite)
   - `ENVIRONMENT` = `production`
   - `SECRET_KEY` = (generate a random string)

5. **Create Web Service**

## Step 3: Update Yahoo App

Once deployed, you'll get a URL like:
```
https://fantasy-ai-oauth.onrender.com
```

1. Update your **Render environment variable**:
   - `YAHOO_REDIRECT_URI` = `https://fantasy-ai-oauth.onrender.com/auth/callback`

2. Update **Yahoo Developer Console**:
   - Set redirect URI to: `https://fantasy-ai-oauth.onrender.com/auth/callback`
   - Save changes

3. **Redeploy** on Render (click "Manual Deploy" → "Deploy latest commit")

## Step 4: Test OAuth

Visit: `https://fantasy-ai-oauth.onrender.com`

The OAuth flow will now work because:
- ✅ Stable HTTPS URL
- ✅ No ngrok complications
- ✅ Yahoo trusts render.com domains
- ✅ URL won't change

## Pro Tips

1. **Free Tier Limits**: Render free tier spins down after 15 min of inactivity. First request will be slow.

2. **Logs**: Check logs in Render dashboard for debugging

3. **Custom Domain**: You can add your own domain later if needed

4. **Database**: For production, upgrade to PostgreSQL (Render offers free PostgreSQL)

## Alternative: Quick Deploy with Replit

If you want even faster deployment:
1. Go to https://replit.com
2. Import from GitHub
3. It auto-deploys with HTTPS
4. Update Yahoo with the Replit URL

---

**Elite developers ship to production early** to avoid wasting time on local OAuth setup issues!