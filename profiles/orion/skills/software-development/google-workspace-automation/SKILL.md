---
name: google-workspace-automation
description: Automate Google Sheets, Google Drive, and headless OAuth authentication workflows.
---

# Google Workspace Automation & Sheets Integration

Use this skill when interacting programmatically with Google Sheets, Google Drive, or managing Google OAuth tokens in a headless server environment.

## 1. Headless OAuth2 Flow (PKCE & Token Management)

When renewing or initiating Google API authorization on a headless machine:
1. **Initialize Flow with Client Secret:**
   ```python
   import os, json
   from google_auth_oauthlib.flow import Flow

   os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

   with open('/root/.hermes/google_client_secret.json') as f:
       client_config = json.load(f)

   flow = Flow.from_client_config(
       client_config,
       scopes=[
           'https://www.googleapis.com/auth/spreadsheets',
           'https://www.googleapis.com/auth/drive'
       ],
       redirect_uri='http://localhost'
   )
   ```
2. **Generate Auth URL & Store PKCE Code Verifier:**
   ```python
   auth_url, state = flow.authorization_url(prompt='consent', access_type='offline')
   # Persist flow.code_verifier and state
   ```
3. **Exchange Redirect URL for Token:**
   ```python
   # When the user returns the localhost redirect URL:
   flow.fetch_token(authorization_response=redirect_url)
   creds = flow.credentials
   # Save creds.token, creds.refresh_token, client_id, client_secret to google_token.json
   ```

## 2. Google Sheets API Formula & Locale Quirks

### Semicolon vs. Comma Formula Delimiters
- Spreadsheets with regional locales using comma decimal formatting (e.g. `in_ID`, `de_DE`, `fr_FR`) require **semicolon (`;`)** as the argument separator in `USER_ENTERED` value updates.
- Example:
  - **Wrong (causes `#ERROR!` in `in_ID`):** `=HYPERLINK("https://...", "Label")`
  - **Correct:** `=HYPERLINK("https://..."; "Label")`

### Native Formulas vs. Excel `_xlfn.` Wrappers
- Excel files loaded via `openpyxl` often contain compatibility wrappers such as `_xlfn.SINGLE(_xlfn.IMAGE(...))` or `_xlfn.IMAGE(...)`.
- Writing these strings to Google Sheets results in `#NAME?`.
- **Fix:** Strip `_xlfn.` prefixes and write clean native formulas (e.g. `=IMAGE("...")`).

## 3. Google Drive Image Embedding in Sheets

To embed Drive images into Google Sheets cells with `=IMAGE(...)`:
1. Ensure the file has public viewer permissions:
   ```python
   drive_service.permissions().create(
       fileId=file_id,
       body={'role': 'reader', 'type': 'anyone'}
   ).execute()
   ```
2. Use Google Drive's high-res thumbnail endpoint as the direct source URL:
   `https://drive.google.com/thumbnail?id=<FILE_ID>&sz=w1000`
3. Formula in cell:
   `=IMAGE("https://drive.google.com/thumbnail?id=<FILE_ID>&sz=w1000")`

## 4. Batch Formatting & Dimension Sizing
Use `spreadsheets().batchUpdate` with `updateDimensionProperties` to set row heights (e.g. 90px for images) and column widths, ensuring rendered images are legible.
