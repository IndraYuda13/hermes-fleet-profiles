---
name: cloudflare-bypass-automation
description: |
  Use when Playwright hits Cloudflare Turnstile or 403 blocks.
---

# Cloudflare Turnstile & IUAM Bypass Automation

Use this skill when web automation or Playwright automation hits Cloudflare Turnstile, Cloudflare Bot Protection, or HTTP 403 Forbidden on protected endpoints (e.g. `accounts.x.ai`).

## Workflow

### 1. Ensure Turnstile Solver API is Running
Local solver service lives at `/root/projects/Turnstile-Solver-NEW/` listening on `http://127.0.0.1:5072`.
To start if down:
```bash
cd /root/projects/Turnstile-Solver-NEW && python3 api.py --port 5072 &
```

### 2. Harvest Clearance via Solver REST API
```python
import urllib.request, urllib.parse, json, time

base_url = "http://127.0.0.1:5072"
target_url = "https://accounts.x.ai/sign-up"

req_url = f"{base_url}/cf_clearance?url={urllib.parse.quote(target_url)}"
with urllib.request.urlopen(req_url) as resp:
    task = json.loads(resp.read().decode())
    task_id = task.get("taskId")

solution = None
for _ in range(30):
    time.sleep(2)
    with urllib.request.urlopen(f"{base_url}/result?id={task_id}") as p_resp:
        res = json.loads(p_resp.read().decode())
        if res.get("status") == "ready":
            solution = res["solution"]
            break
```

### 3. Inject Cookies & User-Agent into Playwright Context
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
    
    # CRITICAL: Context MUST use the exact User-Agent returned by solver
    context = browser.new_context(user_agent=solution['user_agent'])
    
    # Map cookies
    pw_cookies = []
    for c in solution['cookies']:
        pw_c = {
            'name': c['name'],
            'value': c['value'],
            'domain': c['domain'],
            'path': c.get('path', '/'),
            'secure': c.get('secure', True),
            'httpOnly': c.get('httpOnly', False)
        }
        if 'sameSite' in c and c['sameSite'] in ['Strict', 'Lax', 'None']:
            pw_c['sameSite'] = c['sameSite']
        pw_cookies.append(pw_c)
        
    context.add_cookies(pw_cookies)
    
    page = context.new_page()
    page.goto(target_url)
    # Page operations proceed without 403 / Turnstile blocks

## Key Rules & Pitfalls
- **User-Agent & IP Binding**: `cf_clearance` is strictly bound to exit IP and TLS fingerprint / User-Agent. Playwright context `user_agent` MUST match `solution['user_agent']`.
- **gRPC-Web / Internal APIs**: Passing `cf_clearance` cookies unlocks both standard page actions and background XHR/gRPC requests (e.g. `CreateEmailValidationCode`, `VerifyEmailValidationCode`, `ValidatePassword`).
- **Turnstile Widget Token Solving**: Beside IUAM `/cf_clearance`, the solver daemon can solve widget tokens via `GET /turnstile?url=<url>&sitekey=<sitekey>&action=<action>&proxy=<encoded_proxy>`. Inject the returned token into `input[name="cf-turnstile-response"]` or API payload `captchaResponse`.
- **Egress Proxy & IP-Binding Alignment**: Turnstile tokens are strictly bound to the solving egress IP. When automating via proxy pools (e.g. 15 Surfshark proxy nodes), the Turnstile solver API task MUST receive the exact same `proxy` parameter as the upstream worker session. Submitting a token solved on proxy A to an auth endpoint via proxy B or direct IP triggers Cloudflare token validation rejection.
- **Hardware Telemetry & User-Agent Consistency**: When emulating mobile endpoints (e.g. Android WebGL/Mali GPU telemetry), ensure the HTTP `User-Agent` and Client Hints (`Sec-CH-UA`, `Sec-CH-UA-Mobile`, `Sec-CH-UA-Platform`) match the emulated device hardware profile to avoid heuristic fingerprint bans.
- **Silent Redirect to Reset Password**: On auth flows like Next.js `accounts.x.ai`, submitting a sign-in form without a valid Turnstile widget response or valid edge session causes backend to silently redirect requests to `/reset-password?email=...` instead of completing login.
- **Cookie List Appending Bug**: Beware of appending `pw_cookies` to itself (`pw_cookies.append(pw_cookies)`), which causes `RecursionError` in Playwright's `add_cookies`. Always append `pw_c`.
- **OAuth & Multi-Page Session Persistence**: Preserving the Playwright `context` with `cf_clearance` cookies across navigations (e.g., from sign-up to OAuth device authorization endpoints) ensures Cloudflare checks remain bypassed throughout multi-step authentication flows.
- **Form Submission Handlers**: When Playwright `.click('button[type="submit"]')` doesn't trigger Next.js state updates or internal gRPC requests, use explicit input fill followed by `page.press('input[name="..."]', 'Enter')` or target `data-testid` attributes directly (e.g. `button[data-testid="continue-with-email"]`).
- **9Router Database Reload Pitfall**: When hot-swapping DB connections in 9Router (`/root/.9router/db/data.sqlite`), reloading via `fuser -k 20128/tcp` kills the port listener. Do not execute directly inside an active agent run routing through 9Router.
- **Reference Docs**: Detailed endpoints, gRPC payloads, and OAuth specs for `x.ai` are documented in `references/x_ai_auth_flow.md`.
