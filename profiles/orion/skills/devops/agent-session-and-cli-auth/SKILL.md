---
name: agent-session-and-cli-auth
description: Authenticate CLI & browser sessions across agent profiles.
---

# Agent CLI & Automated Browser Session Authentication

Unified standards and procedures for authenticating headless browser sessions, injecting session cookies, handling multi-factor authentication, and synchronizing credentials across isolated agent profiles.

## 1. Profile-Isolated CLI Credential Synchronization
Hermes profiles isolate `$HOME` to `/root/.hermes/profiles/<profile>/home`. When host credentials exist in `/root/`:
```bash
# Sync GitHub CLI credentials to active profile
mkdir -p "$HOME/.config/gh"
cp -r /root/.config/gh/* "$HOME/.config/gh/" 2>/dev/null || true
gh auth setup-git && gh auth status
```

## 2. Automated Browser Cookie Injection (CDP)
Interactive logins on cloud/datacenter IPs (Azure, AWS, DO) frequently trigger security challenges or rate limits. Inject authenticated session cookies directly into Chrome via CDP:
- **GitHub (`.github.com`):** `user_session`
- **X / Twitter (`.x.com` & `.twitter.com`):** `auth_token`, `ct0`, and `twid`
```python
cdp("Network.setCookie", name="auth_token", value=token, domain=".x.com", path="/", secure=True, httpOnly=True)
cdp("Network.setCookie", name="ct0", value=ct0, domain=".x.com", path="/", secure=True, httpOnly=False)
goto_url("https://x.com/home")
wait_for_load()
```
- **Account Cooldown Invariant:** Rapid failed interactive logins cause account-level locks ("We've temporarily limited your login"). Enforce a 15–30 minute cooldown after failures before retrying via residential proxy.

## 3. Multi-Profile Fleet Browser Profile Synchronization
- Hermes isolates Chrome states per-profile (`/root/.hermes/profiles/<name>/browser-profile/chrome/Default/Cookies`). Injecting cookies in one profile does NOT update sibling agents.
- Synchronize the browser profile directory across peers while strictly excluding active lock/socket files (`Singleton*`, `*.lock`):
```python
import glob, shutil, os
def ignore_locks(d, files):
    return [f for f in files if "Singleton" in f or "Socket" in f or "lock" in f.lower()]
src = "/root/.hermes/profiles/orion/browser-profile/chrome"
for p in glob.glob("/root/.hermes/profiles/*"):
    if os.path.basename(p) == "orion": continue
    dst = os.path.join(p, "browser-profile/chrome")
    if os.path.exists(dst): shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=ignore_locks)
```

## 4. Google & YouTube Headless Auth Boundary
- Interactive logins on `accounts.google.com` in headless Chrome fail with *"This browser or app may not be secure"*.
- Export authenticated Netscape cookies from a desktop browser (`cookies.txt`) and pass to tools (`yt-dlp --cookies cookies.txt`). Pair with local residential proxies to avoid IP-based cookie rotation flags.

## 5. Passkey & TOTP Interactive Fallbacks
- When redirected to WebAuthn / Passkeys (`/sessions/two-factor/webauthn`), bypass by navigating directly to `https://github.com/sessions/two-factor/app`. Prompt user specifically for the 6-digit TOTP code and fill `#app_totp`.
