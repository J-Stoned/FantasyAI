# 🚀 Yahoo Developer Console - Quick Registration Card

## 📋 **Essential Information**

### **Registration URL**
https://developer.yahoo.com/apps/

### **Required Fields**
- **App Name**: `Fantasy AI Ultimate`
- **App Description**: `AI-powered fantasy sports analysis platform`
- **Application Type**: Web Application
- **Redirect URI**: `http://localhost:8000/auth/callback`
- **Permissions**: Fantasy Sports API

### **Expected Credentials**
- **Client ID**: 96 characters (starts with `dj0y`)
- **Client Secret**: 40 characters (hex format)

## ⚡ **Quick Steps**

1. **Go to**: https://developer.yahoo.com/apps/
2. **Sign in** with Yahoo account
3. **Click**: "Create an App"
4. **Fill out** the required fields above
5. **Submit** and wait 1-2 days for approval
6. **Copy** Client ID and Client Secret
7. **Run**: `python update_oauth_credentials.py`

## 🔧 **After Approval**

```bash
# Update your credentials
python update_oauth_credentials.py

# Test the OAuth flow
python test_oauth_flow.py

# Run diagnostics
python debug_oauth.py
```

## 🚨 **Common Issues**

| Issue | Solution |
|-------|----------|
| Invalid Redirect URI | Use exactly: `http://localhost:8000/auth/callback` |
| App Not Approved | Wait 1-2 business days, check email |
| Invalid Client ID | Copy exactly as provided, no extra spaces |
| Permission Denied | Request Fantasy Sports API access |

## 📞 **Need Help?**

- **Documentation**: https://developer.yahoo.com/oauth2/guide/
- **API Reference**: https://developer.yahoo.com/fantasysports/guide/
- **Support**: https://developer.yahoo.com/forum/

---

**Remember**: The approval process takes 1-2 business days. Use the mock OAuth flow for development until approved! 