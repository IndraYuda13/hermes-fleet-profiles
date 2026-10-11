# Cloudflare bot-protection bypass (authorized automation)

Depth for the umbrella's Cloudflare section: solver workflow, injection mechanics, and a worked target example. Authorized targets only.

## Local Turnstile solver workflow

A local solver daemon (reference deployment: `/root/projects/Turnstile-Solver-NEW`, listening on `127.0.0.1:5072`; start with `python3 api.py --port 5072` if down) exposes two task types:

- **Clearance (IUAM):** `GET /cf_clearance?url=<target>` returns `{taskId}`; poll `GET /result?id=<taskId>` every ~2s until `status: ready`. The solution carries `cookies` (including `cf_clearance`) and `user_agent`.
- **Widget token:** `GET /turnstile?url=<url>&sitekey=<sitekey>&action=<action>&proxy=<urlencoded-proxy>` returns a token for `input[name="cf-turnstile-response"]` or API payload `captchaResponse`.

### Cookie injection into Playwright

```python
context = browser.new_context(user_agent=solution['user_agent'])  # MUST match the solver's UA
pw_cookies = [{
    'name': c['name'], 'value': c['value'], 'domain': c['domain'],
    'path': c.get('path', '/'), 'secure': c.get('secure', True),
    'httpOnly': c.get('httpOnly', False),
    **({'sameSite': c['sameSite']} if c.get('sameSite') in ('Strict', 'Lax', 'None') else {}),
} for c in solution['cookies']]
context.add_cookies(pw_cookies)  # append cookie dicts, never the list into itself (RecursionError)
```

## Worked example: x.ai (`accounts.x.ai`)

- **Turnstile sitekey:** `0x4AAAAAAAhr9JGVDZbrZOo0` (page widget; pair with the widget-token endpoint).
- **gRPC-Web auth endpoints** (unlocked once clearance cookies are set — background XHR/gRPC pass the same edge check):
  - `POST https://accounts.x.ai/auth_mgmt.AuthManagement/CreateEmailValidationCode`
  - `POST https://accounts.x.ai/auth_mgmt.AuthManagement/VerifyEmailValidationCode`
  - `POST https://accounts.x.ai/auth_mgmt.AuthManagement/ValidatePassword`
- **OAuth device flow (grok-cli):** client id `b1a00492-073a-47ea-816f-4c329264a828`; `POST https://auth.x.ai/oauth2/device/code` with `client_id` and scopes `openid profile email offline_access grok-cli:access api:access conversations:read conversations:write`; poll `POST https://auth.x.ai/oauth2/token` with the device_code grant; user verifies at `https://accounts.x.ai/oauth2/device?user_code=<USER_CODE>`.
- **Symptom map:** submitting the sign-in form without a valid widget token or edge session silently redirects to `/reset-password?email=...` instead of erroring; target `data-testid` selectors (e.g. `button[data-testid="continue-with-email"]`) and use explicit fill + Enter when `.click()` misses Next.js state updates.

Sitekeys, client IDs, and endpoint paths change per target — treat them as examples to re-derive from the live page, not constants to trust.
