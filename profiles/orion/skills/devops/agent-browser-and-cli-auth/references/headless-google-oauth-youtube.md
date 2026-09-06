# Headless Google OAuth2 & YouTube API Automation

## Context & Challenges
When authenticating or automating Google APIs (YouTube Data API v3, Google Drive, Google Sheets) in headless server environments without a desktop GUI:
1. **Insecure Transport Error**:
   Google OAuth libraries enforce HTTPS by default. Localhost redirect URIs (`http://localhost:8080/` or `http://localhost`) raise:
   `oauthlib.oauth2.rfc6749.errors.InsecureTransportError: (insecure_transport) OAuth 2 MUST utilize https.`
2. **PKCE Code Verifier Desynchronization**:
   In interactive or multi-turn agent sessions, the initial authorization URL generation creates an internal `flow.code_verifier`. If the token exchange happens in a separate process or turn without the code verifier, token exchange fails.
3. **Hashtags / Tags Formatting Mismatch**:
   YouTube Data API expects video `tags` as a `list[str]`. Passing a raw string or splitting without sanitization causes API validation errors.

## Recommended Workflow

### 1. Robust Headless OAuth2 Flow (PKCE & Auto-Refresh)
```python
import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

# 1. Allow http://localhost redirect URI
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

client_secrets = "/path/to/client_secrets.json"
token_file = "/path/to/youtube_token.json"

flow = InstalledAppFlow.from_client_secrets_file(
    client_secrets,
    SCOPES,
    redirect_uri="http://localhost:8080/"
)

# Step A: Generate URL and persist PKCE verifier
auth_url, state = flow.authorization_url(prompt="consent", access_type="offline")
print("AUTH_URL:", auth_url)
# Save flow.code_verifier and state to disk/temporary file

# Step B: Exchange Authorization Code or Redirect URL
# flow.code_verifier = saved_code_verifier
# if response_str.startswith("http"):
#     flow.fetch_token(authorization_response=response_str)
# else:
#     flow.fetch_token(code=response_str)
#
# with open(token_file, "w") as f:
#     f.write(flow.credentials.to_json())
```

### 2. Auto-Refresh in Production Services
When initializing the YouTube API client in background daemons:
```python
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

with open(token_file, "r") as f:
    creds = Credentials.from_authorized_user_file(token_file, SCOPES)

if creds and creds.expired and creds.refresh_token:
    creds.refresh(Request())
    with open(token_file, "w") as f:
        f.write(creds.to_json())

youtube = build("youtube", "v3", credentials=creds)
```

### 3. YouTube Shorts Metadata Payload Specifications
- **Title**: Maximum 100 characters. Append `#Shorts` in title or description to ensure algorithmic classification into the Shorts shelf.
- **Privacy Status**: Use `"public"` for instant publishing, or `"private"` / `"unlisted"` for testing.
- **Category ID**: `"24"` (Entertainment), `"22"` (People & Blogs), or `"23"` (Comedy) for talkshows and podcasts.
- **Tags**: Must strictly be a list of strings (`["Shorts", "Podcast", "Viral"]`).
