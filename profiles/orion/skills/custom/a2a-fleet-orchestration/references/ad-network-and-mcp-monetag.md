# Ad Network Monetization & Monetag MCP Integration Runbook

## 1. Remote MCP OAuth 2.1 PKCE Integration (Monetag MCP)

Monetag MCP (`https://mcp.monetag.com/mcp`) enforces OAuth 2.1 with dynamic client registration and PKCE. It does not provide static API keys in the publisher dashboard.

### Direct Python PKCE Exchange Flow
Because authorization codes expire within ~60s and background daemons (like `npx mcp-remote`) can lose state across multi-turn chat loops, execute the exchange directly via Python:

1. **Register Dynamic Client:**
   ```python
   POST https://publishers.monetag.com/api/oauth2/register
   Content-Type: application/json
   {"client_name": "Hermes Monetag MCP", "redirect_uris": ["http://localhost:10266/oauth/callback"]}
   ```
2. **Generate PKCE Parameters:**
   - `code_verifier`: 64-byte urlsafe token (`secrets.token_urlsafe(64)`).
   - `code_challenge`: SHA-256 base64url-encoded verifier (`rtrim('=')`).
   - Store in `/root/.hermes/monetag_active_oauth.json`.
3. **User Authorize URL:**
   - `https://publishers.monetag.com/api/oauth2/authorize?partner_alias=monetag&response_type=code&client_id=<ID>&redirect_uri=http%3A%2F%2Flocalhost%3A10266%2Foauth%2Fcallback&scope=public_api%3Aread_write&state=<STATE>&code_challenge=<CHALLENGE>&code_challenge_method=S256`
4. **Exchange Authorization Code:**
   ```python
   POST https://publishers.monetag.com/api/oauth2/token
   Content-Type: application/x-www-form-urlencoded
   data = {
       "grant_type": "authorization_code",
       "client_id": client_id,
       "code": auth_code,
       "redirect_uri": "http://localhost:10266/oauth/callback",
       "code_verifier": code_verifier
   }
   ```
5. **Hermes Configuration (`config.yaml`):**
   ```yaml
   mcp_servers:
     monetag:
       url: https://mcp.monetag.com/mcp
       headers:
         Authorization: Bearer <access_token>
       timeout: 60
   ```
   Verify with `hermes mcp test monetag`. Note: Monetag requires `Accept: application/json, text/event-stream`.

---

## 2. Web Ad Network & Service Worker Lifecycle

### Deployment Checklist
- **Service Worker (`frontend/sw.js`):** Serve at root `/sw.js` with `Cache-Control: no-cache`. Zone ID must match active domain zones from MCP `get_zones` (e.g. `11740019`).
- **Client Registration (`frontend/index.html`):**
  ```html
  <script>
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').catch(console.warn);
      });
    }
  </script>
  ```
- **Companion Tag:** Add `<script src="https://quge5.com/88/tag.min.js" data-zone="..." async data-cfasync="false"></script>` before `</body>`. `data-cfasync="false"` prevents Cloudflare Rocket Loader corruption.

### Graceful Ad Disabling / Decommissioning
When temporarily or permanently turning off ads:
1. **Comment out companion tags** in `index.html`.
2. **Inject Unregistration Handler** to clean cached workers from visitors' browsers:
   ```html
   <script>
     if ('serviceWorker' in navigator) {
       window.addEventListener('load', () => {
         navigator.serviceWorker.getRegistrations().then(regs => {
           for (const r of regs) r.unregister();
         }).catch(console.warn);
       });
     }
   </script>
   ```
3. **Empty / Inert `frontend/sw.js`** to prevent executing remote scripts if still cached.
4. **Verify zero ad requests** using headless Playwright (`quge5.com`, `5gvci.com`, `6opo.com`).
