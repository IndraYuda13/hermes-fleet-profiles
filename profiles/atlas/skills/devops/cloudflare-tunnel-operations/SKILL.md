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
   *Note: If `patch` or `write_file` tools refuse direct edits to `/etc/cloudflared/config*.yml` or `/etc/nginx/sites-available/*` due to sensitive system paths, use a small inline Python script via `terminal` to modify or write the file.*
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
- Single-origin setup: Attaching `ws.Server` directly to Node's `http.Server` serving the frontend avoids CORS/Origin issues and allows dynamic client connections (`const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'; new WebSocket(\`\${protocol}//\${location.host}\`)`).
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

### Cloudflare Edge & Browser Cache-Control on Origin Servers
When exposing dynamic single-page applications (SPAs), real-time dashboards, or live telemetry servers through Cloudflare Tunnel:
- **Heuristic Caching Trap:** Without explicit HTTP headers on HTML and API routes, Cloudflare edge and Chromium/WebKit browsers apply heuristic caching to `GET /` and `/api/*`. Updates to templates or frontend builds on the origin will not reflect in users' browsers upon reload.
- **Enforced No-Cache Headers:** Always configure origin web servers to send explicit cache-invalidation headers:
  ```http
  Cache-Control: no-cache, no-store, must-revalidate, max-age=0, proxy-revalidate
  Pragma: no-cache
  Expires: 0
  X-Content-Type-Options: nosniff
  ```
- **Service Restart vs File Reload:** Ensure the origin application dynamically reads external template files on disk rather than serving in-memory cached string constants on startup, and restart the backend systemd service cleanly after mutations.

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

### Port Collisions & Existing Listener Conflicts
Before assigning a local origin port for a new ingress rule (e.g. `127.0.0.1:8088`), verify that the port is not already bound by another service or proxy (`netstat -tlpn | grep :8088` or `grep -rn "8088" /etc/cloudflared/ /etc/nginx/`). Binding a tunnel to a port already served by Nginx or another tunnel ingress will cause the public domain to route to the wrong application or throw 502/405 errors.

### Application Host Header Rejection ("Untrusted local API host" / 403 / Invalid Host)
When routing custom domains or proxies through Cloudflare Tunnel to FastAPI/Starlette applications or Vite dev servers:
- **FastAPI/Starlette:** Accessing via domain can trigger 403 Forbidden with `{"detail": "Untrusted local API host"}`. Fix: Set `API_ALLOWED_HOSTS=subdomain.domain.com,localhost,127.0.0.1` in `.env`.
- **Vite Dev Server:** Accessing via domain triggers 403 Forbidden ("Invalid Host header" or blank 403). Fix: Set `server.allowedHosts: true` (or list specific hostnames) in `vite.config.ts`.
- **Vite Dev Server API Proxy:** When SPA routes API requests to a separate backend port via `fetch("/api/...")`, configure `server.proxy` in `vite.config.ts` so Vite forwards requests locally to the backend port.
- **Port vs Public URL Mismatch:** When configuring apps behind Cloudflare Tunnel with public HTTPS URLs (e.g. `WEB_URL=https://app.domain.com`), ensure internal bind port (`WEB_PORT`) is explicitly set to an unprivileged loopback port (e.g. 8090) rather than defaulting to `urlparse(WEB_URL).port` (443), which causes local permission errors or binds to port 443 unexpectedly.
- **Port Collision with Reverse Proxies:** Always verify via `netstat -tlpn` / `ss -tlpn` that a target port (e.g. 8088) is not already bound by local Nginx or another tunnel before mapping ingress rules. Multiple ingress targets sharing a port with Nginx serve wrong web pages or HTTP 405 errors.

### DNS CNAME routed to wrong tunnel
When multiple tunnels exist on the same CF account, `cloudflared tunnel route dns <name> <host>` may bind the CNAME to the wrong tunnel (e.g. an inactive one that doesn't have the hostname in its ingress). Always use the tunnel UUID and `--overwrite-dns`:
```bash
cloudflared tunnel route dns --overwrite-dns <tunnel-uuid> <hostname>
```
Verify: `cloudflared tunnel route dns -f <tunnel-uuid> <hostname>` prints "already configured to route to your tunnel" if correct.

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
