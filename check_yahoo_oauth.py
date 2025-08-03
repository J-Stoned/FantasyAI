"""
Debug Yahoo OAuth Configuration
"""
import requests
from urllib.parse import urlparse, parse_qs

# Get the authorization URL
response = requests.get("https://fantasyai.onrender.com/auth/authorize")
data = response.json()
auth_url = data["authorization_url"]

print("Authorization URL Analysis:")
print("=" * 50)
print(f"Full URL: {auth_url}")
print()

# Parse the URL
parsed = urlparse(auth_url)
params = parse_qs(parsed.query)

print("OAuth Parameters:")
for key, values in params.items():
    if key == 'client_id':
        print(f"  {key}: {values[0][:20]}...")
    else:
        print(f"  {key}: {values[0]}")

print()
print("Checklist:")
print("- [ ] Redirect URI matches Yahoo app exactly")
print("- [ ] Client ID matches Yahoo app")
print("- [ ] Scope is 'fspt-r' (Fantasy Sports Read)")
print("- [ ] No extra spaces or characters")
print()
print("Your redirect URI:", params.get('redirect_uri', ['NOT SET'])[0])
print()
print("This MUST match EXACTLY in your Yahoo app settings!")