---
name: agent-browser-and-cli-auth
description: Use when authenticating CLI or browser sessions in agents.
version: 1.0.0
author: Orion Curator
license: MIT
metadata:
  hermes:
    tags: [auth, browser, github, cli, cookies, agent-environment]
---

# Agent Browser and CLI Auth

## Overview

When running inside an isolated Hermes profile (such as `/root/.hermes/profiles/<profile>/home`), CLI utilities (`gh`, `git`) and automated headless browsers (CDP, Chrome Harness) often lack inherited credentials or active browser sessions present on the host.

## Isolated Profile CLI Sync

In Hermes profile runs, `$HOME` defaults to the profile's dedicated home directory. If host credentials exist in `/root/`:

```bash
# GitHub CLI sync
mkdir -p "$HOME/.config/gh"
cp -r /root/.config/gh/* "$HOME/.config/gh/" 2>/dev/null || true
gh auth setup-git
gh auth status
```

Always verify `gh auth status` and `git ls-remote` after syncing.

## Automated Browser Session Authentication

Websites with multi-factor authentication (2FA), device checks, or bot detection (like GitHub) cannot easily be authenticated via automated form submission without triggering extra security gates.

### 1. Cookie Injection (Recommended Fast Path)
Inject an already authenticated session cookie from the user's primary desktop browser directly into the agent browser tab via CDP:

- **GitHub**: cookie `user_session` on domain `.github.com`
- Pattern:
  ```python
  cdp("Network.setCookie", name="user_session", value=cookie_val, domain=".github.com", path="/", secure=True, httpOnly=True)
  goto_url("https://github.com/")
  wait_for_load()
  ```
- Verification: inspect `meta[name="user-login"]` to confirm authenticated DOM state.

### 2. Google / YouTube Headless Auth Boundary & Cookies Export
Google accounts have strict headless browser / automated environment detection:
- Attempting direct form submission on `accounts.google.com` in headless Chrome triggers:
  `"Couldn't sign you in: This browser or app may not be secure."`
- **Mitigation Workflow**:
  1. Do NOT attempt interactive credential injection for Google/YouTube on headless Chrome.
  2. Have user export authenticated cookies via browser extension (e.g. *Get cookies.txt LOCALLY*) in Netscape format.
  3. Load exported `cookies.txt` into tools (`yt-dlp --cookies cookies.txt`, `requests.cookies.MozillaCookieJar`, or CDP `Network.setCookies`).
  4. This reliably bypasses YouTube bot checks on datacenter/VPS IPs without triggering account lockout.
- **YouTube 2026 Datacenter Bot Protection & Cookie Rotation Quirk**:
  - Exported cookies used from cloud/datacenter IPs (Azure, AWS, DO) are frequently invalidated rapidly by YouTube security heuristics with:
    `"The provided YouTube account cookies are no longer valid. They have likely been rotated in the browser as a security measure."`
  - When yt-dlp runs on datacenter VPS, pair cookies with:
    - Dedicated JS runtime (`--js-runtimes node` or `deno` and `--remote-components ejs:github`) to resolve challenges.
    - Residential/ISP proxy routing (`--proxy`) to prevent IP-based session invalidation.
  - Detailed mitigation playbook: see `references/youtube-bot-mitigation-2026.md`.

### 3. Headless Google OAuth2 & YouTube API Authorization
When authorizing Google APIs (YouTube Data API v3, Drive, Sheets) without a desktop browser on the server:
- Set `os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"` to permit `http://localhost:8080` redirect URIs.
- Explicitly persist and reload `flow.code_verifier` across multi-turn PKCE exchange steps.
- Complete playbook: see `references/headless-google-oauth-youtube.md`.

### 4. Interactive Fallback (Handling Passkeys & TOTP Routing)
If the user prefers manual login or provides credentials interactively:
1. Navigate to the login page and fill `#login_field` and `#password`.
2. Inspect destination after submit. GitHub frequently redirects to WebAuthn / Passkey first (`/sessions/two-factor/webauthn` with *"This browser or device is reporting partial passkey support"*).
3. Do NOT stall on WebAuthn prompts. Immediately route to standard TOTP authenticator flow:
   - Navigate directly to `https://github.com/sessions/two-factor/app`, OR
   - Click "More options" -> "Authenticator app".
4. Prompt the user specifically for the 6-digit TOTP code.
5. Fill into `#app_totp` / `input[name="app_otp"]` / `input[autocomplete="one-time-code"]`.
6. Verify successful authentication via URL redirect to `https://github.com/` and DOM confirmation:
   ```javascript
   document.querySelector('meta[name="user-login"]')?.content
   ```

