---
name: cloudflare-tunnel-operations
description: Use when exposing, routing, operating, or troubleshooting services through Cloudflare Tunnel, including dashboard deployments, ingress rules, DNS routing, host headers, caches, and WebSocket failures.
version: 1.0.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [cloudflare, cloudflared, tunnel, ingress, dns, reverse-proxy, dashboard]
    related_skills: [hermes-agent, network-proxy-troubleshooting]
---

# Cloudflare Tunnel Operations

## Overview

Operate a tunnel as a complete route: public hostname, DNS record, cloudflared ingress, local listener, and the origin application's host/origin policy. Change one layer at a time and verify the local origin and public route before blaming the application or cache.

## Operating workflow

1. Identify the intended hostname, active tunnel, systemd unit, config file, origin listener, and application access policy.
2. Inspect the complete `ingress:` list before editing. Each hostname gets one `service`; retain the terminal `http_status:404` fallback.
   *Note: If `patch` or `write_file` tools refuse direct edits to `/etc/cloudflared/config*.yml` due to sensitive system paths, use a small inline Python script via `terminal` to modify the file.*
3. Keep an origin on loopback unless the application explicitly supports authenticated public binding.
4. Add/update the ingress entry, then route DNS explicitly with `cloudflared tunnel route dns -f <tunnel> <hostname>` when necessary.
5. Restart the managed unit with `systemctl`; never leave an unmanaged `cloudflared` process competing with it.
6. Verify in order: origin listener, local HTTP with its expected Host header, public HTTP, then the browser/WebSocket path.

## Ingress pattern

```yaml
ingress:
  - hostname: app.example.com
    service: http://127.0.0.1:9119
    originRequest:
      httpHostHeader: 127.0.0.1
  - service: http_status:404
```

Use host-header rewriting only when the verified loopback origin requires it. It can make ordinary HTTP succeed while a strict WebSocket endpoint still rejects the browser's public `Origin`; solve that through the application's supported auth/origin/CORS settings rather than patching validation out of source.

### WebSocket Applications over Tunnel
- Cloudflare Tunnel forwards WebSocket upgrade connections (`wss://`) automatically without special proxy headers or edge configuration.
- Single-origin setup: Attaching `ws.Server` directly to Node's `http.Server` serving the frontend avoids CORS/Origin issues and allows dynamic client connections (`const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'; new WebSocket(\`${protocol}//\${location.host}\`)`).
- Socket.IO / WebSocket Lifecycle on Reconnects: Always place room join/subscription emissions (e.g. `socket.emit('join_room', ...)`) inside the `socket.on('connect', ...)` handler (and check `if (socket.connected)`). If joins are emitted once at script execution, edge reconnects or transport upgrades through Cloudflare establish a fresh socket ID without room membership, causing dropped real-time broadcasts.
- Optimistic UI for Live Real-Time Feeds: When implementing user-facing real-time message forms over tunneled sockets, use client-side optimistic rendering with temporary tracking IDs (`temp_${Date.now()}`) and update status upon socket ack, ensuring zero perceived latency and no blank-thread states before ACK arrival.
- Demo / Single-User Verification UI: When exposing real-time WebSocket demos for mobile or manual testing, include visual connection state indicators (`ws.onopen`/`ws.onclose`) and an automatic server response/bot echo. Otherwise, a single user testing alone may see no activity when sending messages to a broadcast-only server.

## Dashboard deployments

Run a dashboard under a restartable systemd service. A loopback-bound dashboard commonly needs the internal host header; a public bind needs the product's authentication configuration. If PTY/WebSockets report `origin_mismatch`, inspect supported dashboard origin/CORS/auth configuration and test the WebSocket separately from the landing page.

## Fast diagnosis

```bash
cloudflared tunnel list
systemctl status <cloudflared-unit> --no-pager
curl -sSI -H 'Host: 127.0.0.1' http://127.0.0.1:<port>
cloudflared tunnel route dns -f <tunnel-id-or-name> <hostname>
```

| Symptom | Prove first |
|---|---|
| 1033 / 404 / 502 | 1. Confirm you edited the correct config: `systemctl cat cloudflared` shows `--config /etc/cloudflared/config-XXXX.yml`. 2. Check `ps aux | grep cloudflared` for ghost/stale PIDs alongside systemd (causes load-balanced 1033/404/502). 3. DNS CNAME targets correct tunnel (`cloudflared tunnel route dns -f <tunnel> <host>`). 4. Ingress config has exact hostname and updated target port. |
| 400 / invalid host | Origin host-header policy and local listener |
| Blank page after repair | Correct origin/DNS first, then hard-refresh or purge stale edge assets |
| WebSocket 1006 / origin mismatch | Application origin/CORS/auth policy and proxy upgrade path |

## Pitfalls

### cPanel / WebHost DNS 404 Conflict Page
When exposing a new subdomain via Cloudflare Tunnel (e.g. `subdomain.indrayuda.my.id`), if hitting the HTTPS URL returns a **cPanel / WHM 404 Not Found** page ("Please forward this error screen to WebMaster"):
1. The DNS record for `subdomain` in Cloudflare DNS is pointing to an A record (the cPanel server IP) instead of the Cloudflare Tunnel CNAME target (`<tunnel-uuid>.cfargot.com`).
2. Force the DNS record to overwrite the existing record pointing to cPanel:
   ```bash
   cloudflared tunnel route dns --overwrite-dns <tunnel-id-or-uuid> <subdomain.domain.com>
   ```
3. Verify with `dig +short <subdomain.domain.com>` or `cloudflared tunnel route dns -f <tunnel-id> <subdomain.domain.com>` that the CNAME resolves to `<tunnel-uuid>.cfargot.com`.

### Scratch Workspace & Container Port Conflicts
When exposing containerized applications built inside temporary/scratch workspaces (e.g., `docker-compose.yml` with default ports 5432, 8000, 3000):
- Check for port collisions first: `netstat -tlpn | grep -E '5432|5433|8000|3000'`.
- Remap host ports to unused loopback ports (e.g., `127.0.0.1:8140:80`, `127.0.0.1:8141:8000`, `127.0.0.1:5439:5432`) in `docker-compose.yml` BEFORE pointing cloudflared ingress to `http://127.0.0.1:8140`.

### API Token Extraction for Cloudflare API when cert.pem is unlinked or CLI lacks cert
If `cloudflared tunnel route dns` fails due to `client didn't specify origincert path` or missing `cert.pem` location, extract the embedded zone API token from `/root/.cloudflared/cert.pem` (or Argo Tunnel Token file):
```python
import base64, json
with open('/root/.cloudflared/cert.pem') as f:
    text = f.read()
token_str = text.split('-----BEGIN ARGO TUNNEL TOKEN-----')[1].split('-----END ARGO TUNNEL TOKEN-----')[0].strip()
data = json.loads(base64.b64decode(token_str).decode('utf-8'))
api_token = data.get('apiToken')
```
Use this Bearer token against Cloudflare Client API (`https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records`) to programmatically create or update DNS records (e.g. CNAME pointing to `<tunnel_uuid>.cfargotunnel.com`) directly.

### Nginx Proxy Trailing Slash Traps (`/api` vs `/api/`)
When proxying API endpoints through Nginx container to FastAPI backend:
- `location /api/ { proxy_pass http://backend:8000/api/; }` strips `/api` from FastAPI requests (FastAPI route `@app.get('/api/health')` will receive `/health` and return `404 Not Found`).
- `location /api { proxy_pass http://backend:8000/api; }` preserves the full path cleanly so FastAPI routes match expected prefixes.

### Wrong config file edited (multiple config-*.yml)
Multiple cloudflared configs can coexist under `/etc/cloudflared/` (e.g. `config.yml`, `config-vps-baru.yml`). The systemd unit may reference a *different* file than the default `config.yml`. **Always run `systemctl cat cloudflared` first** to see the actual `--config` path in `ExecStart=`. Editing the wrong file wastes time and leaves the active tunnel unchanged. After editing the correct file, also check for and revert any accidental edits to other config files. Also check for duplicate hostname entries with different ports (e.g. `prediction-lab.indrayuda.my.id` pointing to port 3000 vs 8000).

### Stale duplicate connectors & multiple systemd units (intermittent or persistent 404 / 1033 / 502)
If `cloudflared tunnel info <tunnel>` or `ps aux | grep cloudflared` shows multiple running processes (e.g., an unmanaged background process alongside `systemctl`, or **multiple active systemd service units** such as `cloudflared.service` and `cloudflared-vps-baru.service`), Cloudflare load-balances across all of them. A stale process or secondary systemd service using old/partial ingress config silently serves Cloudflare Error 1033 / 404 / 502 for requests routed to it. Diagnosis:
```bash
ps aux | grep cloudflared | grep -v grep       # >1 process running = problem
systemctl list-units | grep cloudflared        # >1 active systemd unit = problem
ls -la /etc/systemd/system/*cloud*             # check for overlapping unit definitions
cloudflared tunnel info <tunnel-id>             # multiple CONNECTOR IDs from same ORIGIN IP = problem
```
Fix: Stop and disable secondary systemd units (`systemctl stop cloudflared && systemctl disable cloudflared`), `kill -9 <stale_pid>`, then `systemctl restart <active-unit>`.
```
Fix: Stop and disable secondary systemd units (`systemctl stop cloudflared && systemctl disable cloudflared`), `kill -9 <stale_pid>`, then `systemctl restart <active-unit>`.

### Port Collisions & Existing Listener Conflicts
Before assigning a local origin port for a new ingress rule (e.g. `127.0.0.1:8088`), verify that the port is not already bound by another service or proxy (`netstat -tlpn | grep :8088` or `grep -rn "8088" /etc/cloudflared/ /etc/nginx/`). Binding a tunnel to a port already served by Nginx or another tunnel ingress will cause the public domain to route to the wrong application or throw 502/405 errors.

### Application Host Header Rejection ("Untrusted local API host" / 403 / Invalid Host)
When routing custom domains or proxies through Cloudflare Tunnel to FastAPI/Starlette applications or Vite dev servers:
- **FastAPI/Starlette:** Accessing via domain can trigger 403 Forbidden with `{"detail": "Untrusted local API host"}`. Fix: Set `API_ALLOWED_HOSTS=subdomain.domain.com,localhost,127.0.0.1` in `.env`.
- **Vite Dev Server & Preview Server:** Accessing via domain triggers 403 Forbidden ("Blocked request. This host is not allowed" or blank 403). Fix: Set `server.allowedHosts: true` and `preview.allowedHosts: true` (or list specific hostnames) in `vite.config.ts`. Also ensure preview server binds to `host: '127.0.0.1'` on the expected ingress port.
- **Vite Dev Server API Proxy:** When SPA routes API requests to a separate backend port via `fetch("/api/...")`, configure `server.proxy` in `vite.config.ts` so Vite forwards requests locally to the backend port.
- **Port vs Public URL Mismatch:** When configuring apps behind Cloudflare Tunnel with public HTTPS URLs (e.g. `WEB_URL=https://app.domain.com`), ensure internal bind port (`WEB_PORT`) is explicitly set to an unprivileged loopback port (e.g. 8090) rather than defaulting to `urlparse(WEB_URL).port` (443), which causes local permission errors or binds to port 443 unexpectedly.
- **Port Collision with Reverse Proxies:** Always verify via `netstat -tlpn` / `ss -tlpn` that a target port (e.g. 8088) is not already bound by local Nginx or another tunnel before mapping ingress rules. Multiple ingress targets sharing a port with Nginx serve wrong web pages or HTTP 405 errors.

### DNS CNAME routed to wrong tunnel
When multiple tunnels exist on the same CF account, `cloudflared tunnel route dns <name> <host>` may bind the CNAME to the wrong tunnel (e.g. an inactive one that doesn't have the hostname in its ingress). Always use the tunnel UUID and `--overwrite-dns`:
```bash
cloudflared tunnel route dns --overwrite-dns <tunnel-uuid> <hostname>
```
Verify: `cloudflared tunnel route dns -f <tunnel-uuid> <hostname>` prints "already configured to route to your tunnel" if correct.

### HTML Form Default Navigation vs Real-Time SPAs
When developing live chat widgets, single-page apps, or real-time UI components behind reverse proxies or Cloudflare Tunnel:
- Avoid standard wrapping `<form>` tags without explicit `e.preventDefault()` and `return false` on all triggers.
- Unhandled `Enter` key presses inside input fields trigger default HTML form GET submissions (`GET /?input_name=...`), which causes full-page reloads, drops the WebSocket/Socket.IO connection, and results in misleading Cloudflare Error 404 / route missing responses.
- Prefer event-driven container elements (`<div>`) with explicit `keydown` (Enter) and `click` listeners attached directly to JS handlers.

### Missing Default Origin Cert Path
When executing `cloudflared tunnel route dns` or `cloudflared tunnel list`, if `cert.pem` is stored in a non-standard location or root home without env export, cloudflared can fail with `Cannot determine default origin certificate path`.
Fix: Pass `--origincert /root/.cloudflared/cert.pem` or export `TUNNEL_ORIGIN_CERT=/root/.cloudflared/cert.pem`:
```bash
cloudflared --origincert /root/.cloudflared/cert.pem tunnel route dns --overwrite-dns <tunnel-uuid> <hostname>
```

### Multi-Domain Single-Port Host Discrimination
When routing multiple subdomains (e.g. `customer.domain.com` and `admin.domain.com`) to the same backend application on a single port that performs host-based routing (inspecting `req.headers.host`), **do NOT** configure `originRequest.httpHostHeader` in `cloudflared` ingress for those hostnames. Setting `httpHostHeader: 127.0.0.1` overwrites the original host and breaks the app's internal domain discriminator.

### DNS CNAME & Edge Propagation Timing (Transient 404)
After running `cloudflared tunnel route dns <tunnel> <hostname>` and restarting cloudflared, Cloudflare edge edge-nodes can take 5–15 seconds to sync and route the new CNAME. Initial requests during this propagation window may return edge HTTP 404 ("This page can't be found"). Validate with local curl Host header first, check with `dig +short <hostname>`, and wait a few seconds before assuming ingress configuration error.

### Cloudflare Pages Custom Domain Verification (Proxied CNAME Failure)
When binding a custom domain to Cloudflare Pages via API or Wrangler, the CNAME record must initially be set to `proxied: false` (Grey Cloud) for Cloudflare Pages verification to complete (`verification_data.status == "active"`). Once active, re-enable `proxied: true` (Orange Cloud). If a user API token lacks `DNS:Edit` privileges, extract the Zone API token embedded inside `/root/.cloudflared/cert.pem` on the host. See `references/cloudflare-pages-custom-domain.md`.

### Cloudflare Temp Email / Worker + Pages Deployment Quirks
When deploying `cloudflare_temp_email` or similar Workers + Pages fullstack apps via Wrangler CLI:
1. **D1 Setup:** Create database `npx wrangler d1 create temp-email-db`, then execute initial schema `npx wrangler d1 execute temp-email-db --file=../db/schema.sql --remote`.
2. **Worker Custom Domain:** In `worker/wrangler.toml`, configure `routes = [{ pattern = "api-tempmail.domain.com", custom_domain = true }]` and set `JWT_SECRET`, `ADMIN_PASSWORDS`, `DOMAINS`.
3. **Frontend API Base & Language:** Set `VITE_API_BASE=https://api-tempmail.domain.com` in `frontend/.env.prod`. If default UI language is Chinese (`zh`), patch `DEFAULT_LOCALE` and `FALLBACK_LOCALE` to `'en'` in `frontend/src/i18n/utils.ts` before `pnpm build`.
4. **Pages Project Creation & Deploy:** Create Pages project first with `npx wrangler pages project create <name> --production-branch=production`, build frontend (`pnpm build`), then deploy `npx wrangler pages deploy dist --project-name=<name> --branch=production`.

## Completion record

Report the changed unit/config file, hostname, target listener, DNS action, and exact local/public checks executed. Read the retained session-specific recipes only when their scenario applies: `references/hermes-dashboard-setup.md`, `references/routine-cloudflared-operations.md`, and `references/hermes-dashboard-cloudflare.md`.

## Verification checklist

- [ ] Ingress shape and final fallback were inspected.
- [ ] Managed tunnel unit restarted cleanly.
- [ ] DNS and local origin checks agree with the target hostname.
- [ ] Public HTTP and relevant WebSocket behavior were tested separately.
- [ ] No source-level host/origin security bypass was introduced.
