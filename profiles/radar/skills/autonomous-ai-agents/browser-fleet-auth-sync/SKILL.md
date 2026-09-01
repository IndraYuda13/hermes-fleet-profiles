---
name: browser-fleet-auth-sync
description: "Sync browser auth cookies and CDP sessions across fleet."
version: 1.0.0
author: RADAR
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Browser, CDP, Multi-Agent, Auth, Cookies, SSO, Cloudflare]
---

# Browser Fleet Auth Sync

Guides synchronizing authenticated browser sessions, CDP endpoints, and cookies across multi-agent profiles (Hermes fleet).

## When to Use
- An agent needs to execute authenticated browser actions (`browser_exec`, Playwright) on services like X/Twitter, Microsoft SSO, or LMS, but the local profile lacks auth cookies.
- Cloudflare WAF or Microsoft OIDC SSO blocks a standalone headless browser, but a shared proxy browser on port 9222 has an active session.

## Workflows

### 1. Attaching to Shared CDP Port 9222 (Fastest & Most Reliable)
If a primary Chrome instance is already running with proxy and authenticated sessions on port 9222:

```bash
# Point the current Hermes profile to the shared CDP endpoint
hermes config set browser.cdp_url http://127.0.0.1:9222

# Restart browser harness daemon to bind to the new CDP URL
pkill -f "browser_harness.daemon" || true
```

### 2. Cookie Extraction & Injection via CDP
When running an isolated browser instance, auth cookies can be queried and injected directly via CDP:

```python
# In browser_exec:
import json

# Inspect existing cookies
cookies = cdp("Network.getCookies", urls=["https://x.com", "https://twitter.com"])

# Inject cookies
for c in cookies_list:
    cookie_param = {
        'name': c['name'],
        'value': c['value'],
        'domain': c['domain'],
        'path': c.get('path', '/'),
        'secure': c.get('secure', True),
        'httpOnly': c.get('httpOnly', False),
    }
    if 'sameSite' in c:
        cookie_param['sameSite'] = c['sameSite']
    if 'expires' in c and c['expires'] > 0:
        cookie_param['expires'] = c['expires']
    cdp("Network.setCookie", **cookie_param)
```

## Pitfalls
- `browser.use_real_profile: true` without `cdp_url` creates separate profile directories (`/root/.hermes/profiles/<profile>/browser-profile/chrome`).
- SQLite `Cookies` files cannot be read cleanly if Chrome has exclusive locks; prefer CDP `Network.getAllCookies` / `Network.setCookie` or dump while Chrome is stopped.
