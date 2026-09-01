---
name: cdp-cloudflare-browser-bypass
description: Bypass Cloudflare in real Chrome using CDP cookie injection.
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Cloudflare, CDP, Browser, Bypass, Automation]
---

# CDP Cloudflare Browser Bypass

Bypass Cloudflare Bot Protection ("Just a moment...") and Turnstile challenges directly inside real Chromium/Chrome sessions using Chrome DevTools Protocol (CDP) and local clearance solvers.

This skill does NOT run headless scrapers as standalone HTTP clients; it operates inside live real-browser tool engines (`browser_exec`).

## When to Use
- Navigating to Cloudflare-protected sites in Hermes real browser sessions.
- Hitting `🐴 Just a moment...` or Ray ID challenge pages in browser automation.
- Automating SSO login flows behind Cloudflare protection (e.g. university LMS, enterprise portals).
- Persisting real-profile sessions while overcoming dynamic anti-bot checks.

## Prerequisites
- Local FlareSolverr running on `http://127.0.0.1:8191` (or Turnstile Solver on `:5072`).
- Hermes real-profile browser configured (`browser.use_real_profile: true`).
- Access to Hermes CDP helpers inside `browser_exec`.

## How to Run
Invoke inside Hermes `browser_exec` scripts in Python using stdlib `urllib.request` and pre-imported `cdp` helpers.

## Quick Reference
```python
# 1. Fetch clearance & UA
sol = get_flaresolverr_solution(target_url)

# 2. Match UA and remove webdriver flag via CDP
cdp('Emulation.setUserAgentOverride', userAgent=sol['userAgent'])
cdp('Page.addScriptToEvaluateOnNewDocument', source="Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")

# 3. Inject cookies
for c in sol['cookies']:
    cdp('Network.setCookie', name=c['name'], value=c['value'], domain=c['domain'], path=c.get('path', '/'), secure=c.get('secure', False), httpOnly=c.get('httpOnly', False))

# 4. Navigate
goto_url(target_url)
```

## Procedure

1. **Detect Cloudflare Challenge:**
   In `browser_exec`, navigate to the target URL and verify if the page title contains `Just a moment...` or Ray ID.

2. **Obtain Solution from Local Solver:**
   Query FlareSolverr or local Turnstile solver to obtain the valid `cf_clearance` cookie and bound `userAgent`:
   ```python
   import urllib.request, json
   payload = json.dumps({"cmd": "request.get", "url": target_url, "maxTimeout": 60000}).encode('utf-8')
   req = urllib.request.Request("http://127.0.0.1:8191/v1", data=payload, headers={'Content-Type': 'application/json'})
   with urllib.request.urlopen(req) as resp:
       solution = json.loads(resp.read().decode('utf-8'))['solution']
   ```

3. **Mask Navigator Fingerprint via CDP:**
   Synchronize the browser User-Agent and mask automation artifacts before reload:
   ```python
   cdp('Emulation.setUserAgentOverride', userAgent=solution['userAgent'])
   cdp('Page.addScriptToEvaluateOnNewDocument', source="""
       Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
   """)
   ```

4. **Inject Cookies into Browser Network Stack:**
   Inject `cf_clearance` and all associated session cookies:
   ```python
   for cookie in solution['cookies']:
       cdp('Network.setCookie',
           name=cookie['name'],
           value=cookie['value'],
           domain=cookie['domain'],
           path=cookie.get('path', '/'),
           secure=cookie.get('secure', False),
           httpOnly=cookie.get('httpOnly', False)
       )
   ```

5. **Navigate and Complete Multi-Step Flow:**
   Navigate directly to the destination or login landing page. If completing SSO (e.g. Microsoft OIDC), proceed through interactive form clicks using `js(...)` or `click_at_xy`.

## Pitfalls
- **User-Agent Mismatch:** `cf_clearance` is strictly bound to the exact User-Agent string from the solver. Always override the browser UA via `Emulation.setUserAgentOverride`.
- **Egress IP Binding:** The clearance token is bound to the solver's exit IP. Both solver and browser must use the same network egress.
- **OIDC Callback Re-check:** On OAuth/OIDC redirect callbacks (e.g. `/auth/oidc/`), Cloudflare may issue a secondary check if cookies expired mid-flow. Re-inject clearance cookies before final redirection to dashboard.
- **Timeout on Screenshot:** Capturing screenshots immediately during active CDP IPC calls can time out if the browser page is busy navigating. Use short `time.sleep()` before `capture_screenshot()`.

## Verification
Navigate to the protected site in `browser_exec`. The page title must reflect the authentic site title rather than `Just a moment...`, and `js('document.body.innerText')` must display target content.
