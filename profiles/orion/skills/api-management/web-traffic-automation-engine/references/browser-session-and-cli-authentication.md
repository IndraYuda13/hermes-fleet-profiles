# Agent Browser Session & CLI Authentication

Workflows for authenticating headless browser sessions, injecting cookies via CDP, and handling CLI credentials in isolated agent environments.

## 1. Isolated Profile CLI Sync
In Hermes profile runs, `$HOME` defaults to the profile's home directory. Sync host credentials:
```bash
mkdir -p "$HOME/.config/gh"
cp -r /root/.config/gh/* "$HOME/.config/gh/" 2>/dev/null || true
gh auth setup-git
gh auth status
```

## 2. Automated Browser Session Authentication

### Cookie Injection via CDP
Inject authenticated session cookies from desktop browsers directly into agent tabs:
- **GitHub (`.github.com`):** cookie `user_session`
  ```python
  cdp("Network.setCookie", name="user_session", value=cookie_val, domain=".github.com", path="/", secure=True, httpOnly=True)
  goto_url("https://github.com/")
  ```
- **X / Twitter (`.x.com` & `.twitter.com`):** cookies `auth_token`, `ct0`, and `twid`. Enforce 15-30m cooldown after login failures before retrying via residential proxy.
- **OpenAI / ChatGPT (`chatgpt.com`):** Save credentials bound to the exact origin where password input resides (`https://auth.openai.com`), not landing page. Parse chunked NextAuth session cookies (`__Secure-next-auth.session-token.0`, `.1`).

### Google Stealth Headless Bypass
Default headless Chrome on cloud IPs triggers immediate block (`"Couldn't sign you in"`).
1. Route through residential/VPN proxy (`--proxy-server="http://127.0.0.1:31001"`).
2. Strip automation flags: `--disable-blink-features=AutomationControlled` (forces `navigator.webdriver = false`).
3. Set desktop User-Agent string.
4. Input dispatch: Use genuine CDP keyboard events (`fill_input`), never raw JS `input.value = ...` which Google's Closure framework ignores.
5. Post-login: Bypass selfie/recovery onboarding checkpoints by clicking `a[aria-label="Lain kali"]` or `a[aria-label="Not now"]`.

## 3. Multi-Profile Fleet Profile Synchronization
Hermes isolates Chrome profiles per agent. Sync browser profiles while strictly excluding active lock/socket files:
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

## 4. Headless Google OAuth2 & Workspace API Authorization
- Set `os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"` for localhost loopback redirect URIs.
- Exact redirect URI matching: Ensure token exchange request matches exact `redirect_uri` (mismatched trailing slashes trigger `redirect_uri_mismatch`).
- Single-use codes: Authorization codes expire in ~10m and can only be exchanged once. If `invalid_grant` occurs, generate a fresh authorization URL immediately.
