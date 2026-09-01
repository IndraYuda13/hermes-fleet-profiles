---
name: google-workspace-sync-automation
description: "Use when automating Google Drive uploads, OAuth flows, and Google Sheets formula syncing."
---

# Google Workspace Sync Automation (Drive & Sheets)

Use this skill when performing programmatic operations on Google Sheets and Google Drive via API, handling headless OAuth token refreshes, or syncing complex spreadsheet structures (images, hyperlinks, formulas, locale formatting).

## 1. Google OAuth2 Headless Auth & Token Refresh

When running in headless agent environments:
1. **PKCE Flow with State Preservation:**
   - Always persist `code_verifier` and `state` across turns in a local state JSON before providing the authorization URL to the user.
   - When receiving the redirect URL from the user, set `OAUTHLIB_INSECURE_TRANSPORT=1` if handling `http://localhost` callbacks.
   - Extract credentials and store refreshed JSON with `type: authorized_user`.

2. **Required Scopes:**
   - Spreadsheets: `https://www.googleapis.com/auth/spreadsheets`
   - Drive files: `https://www.googleapis.com/auth/drive`

## 2. Google Sheets Formula & Locale Pitfalls

1. **Formula Parameter Delimiters (Locale Dependent):**
   - In standard US locale (`en_US`), formulas use commas (`,`): `=HYPERLINK("url", "label")`.
   - In Indonesian (`in_ID`) and European locales, formulas **MUST** use semicolons (`;`): `=HYPERLINK("url"; "label")`.
   - Always inspect `spreadsheet.properties.locale` via API or inspect existing formula syntax before batch writing to avoid `#ERROR!` formula parse errors.

2. **Native Formula vs Excel Compatibility Wrappers:**
   - Excel exports often write compatibility wrappers like `_xlfn.SINGLE(_xlfn.IMAGE(...))` or `_xlfn.IMAGE(...)`.
   - Google Sheets will display `#NAME?` if written literally.
   - Strip `_xlfn` wrappers and write native `=IMAGE("direct_url")` and `=HYPERLINK("url"; "label")`.

3. **Drive Thumbnail Direct URLs for `=IMAGE()`:**
   - View URL (`/file/d/<id>/view`) is for human viewing via browser.
   - Direct image embed URL for `=IMAGE(...)` formula: `https://drive.google.com/thumbnail?id=<file_id>&sz=w1000`.
   - Ensure the uploaded file has public reader permissions (`role: reader, type: anyone`).

## 3. Google Sheets Batch Formatting Best Practices

1. **Row & Column Dimensions:**
   - For thumbnail previews in `=IMAGE(...)`, update row height (`dimension: ROWS, pixelSize: 80-100`) and column width (`dimension: COLUMNS, pixelSize: 120-150`) via `batchUpdate.updateDimensionProperties`.

2. **Batch Value Updates:**
   - Use `valueInputOption: "USER_ENTERED"` so formulas and hyperlinks are evaluated natively by Google Sheets engine instead of being stored as raw strings (`RAW`).
