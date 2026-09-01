---
name: hermes-dashboard-cloudflare
description: Set up Hermes web dashboard to run in the background (systemd) and expose it via Cloudflare Tunnel securely.
---
# Hermes Dashboard with Cloudflare Tunnel

When the user asks to run the Hermes dashboard in the background or expose it via Cloudflared, use this skill to configure it properly.

## 1. Systemd Service
The `hermes dashboard` command normally runs in the foreground. To keep it running persistently, wrap it in a systemd service.

```ini
[Unit]
Description=Hermes Agent Web Dashboard
After=network-online.target
Wants=network-online.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=root
Group=root
ExecStart=/usr/local/lib/hermes-agent/venv/bin/hermes dashboard --no-open --port 9119 --host 127.0.0.1
WorkingDirectory=/root
Environment="HOME=/root"
Environment="PATH=/usr/local/lib/hermes-agent/venv/bin:/usr/local/lib/hermes-agent/node_modules/.bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="VIRTUAL_ENV=/usr/local/lib/hermes-agent/venv"
Environment="HERMES_HOME=/root/.hermes"
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Crucial Note**: The dashboard MUST be bound to `--host 127.0.0.1`. If bound to `0.0.0.0`, Hermes enforces an authentication gate. If no OAuth or Password authentication provider is configured yet, the dashboard will actively refuse to bind to `0.0.0.0` and crash loop on startup.

## 2. Cloudflare Tunnel Configuration
When binding to `127.0.0.1` and proxying via Cloudflare Tunnel (`cloudflared`), you must override the `Host` header. 

By default, Cloudflared passes the external domain name (e.g., `hermes.example.com`) as the `Host` header. The Hermes dashboard will reject requests containing non-loopback Host headers if bound strictly to localhost (returns `Invalid Host header`).

Fix this in the `cloudflared` configuration (`config.yml`) by setting `httpHostHeader: 127.0.0.1` or `localhost`:

```yaml
ingress:
  - hostname: hermes.example.com
    service: http://127.0.0.1:9119
    originRequest:
      noTLSVerify: true
      httpHostHeader: 127.0.0.1    # CRITICAL to bypass Host header validation
```

After modifying the configuration, always restart the `cloudflared` service and check its status.

**CRITICAL ROUTING DNS VERIFICATION**: Do not assume that adding ingress rules automatically links the domain. If the domain was previously routed to another tunnel on the server, you MUST explicitly force-update the CNAME in Cloudflare:
```bash
cloudflared tunnel route dns -f <correct-tunnel-id-or-name> <hostname>
```
Without this explicit routing command, traffic for that hostname will continue routing through the old tunnel ID, causing 404 or connection failures on the new service.

## 3. Cache Poisoning Pitfall (Blank/White Screen)
If the tunnel and dashboard are initially misconfigured (e.g., missing the `httpHostHeader` override) or if the DNS CNAME record is pointing to the wrong/old tunnel ID, requests via the browser will hit a 404 or 403 error page. **Cloudflare aggressively caches these error pages (particularly the dashboard's `index-*.js` files) for several hours**.

If the user complains that the page is blank, white, or broken immediately *after* you applied the fix:
1. Verify the CNAME DNS record is explicitly routed to the correct tunnel ID (`cloudflared tunnel route dns -f <tunnel-id> <domain>`).
2. The blank screen is almost certainly a Cloudflare cache hit on the previous error.
3. Instruct the user to perform a **Hard Refresh** (`Ctrl + F5` or `Cmd + Shift + R`) or purge the cache from their Cloudflare dashboard.

## 4. WebSocket Origin Mismatch (`pty refused: origin_mismatch`)
Even with `httpHostHeader` configured, Cloudflared passes the original `Origin` header (e.g., `https://hermes.example.com`) during WebSocket upgrades (used for terminal PTY and logs). 

If you get `pty refused: origin_mismatch`, DO NOT modify `web_server.py`. Hermes enforces strict origin and host checks when the dashboard binds to `127.0.0.1`.

**The correct, native fix:**
Bind the dashboard to `0.0.0.0` and configure an authentication provider. When bound to `0.0.0.0` with authentication, Hermes trusts the upstream proxy to handle the boundary and disables the restrictive loopback origin checks.

1. Set the host to `0.0.0.0`:
   ```bash
   hermes config set dashboard.host 0.0.0.0
   ```
2. Set up authentication (e.g., password):
   ```bash
   hermes config set dashboard.auth "password:YOUR_SECURE_PASSWORD"
   ```
3. Restart the dashboard service:
   ```bash
   systemctl restart hermes-dashboard
   ```

*Alternative (if `0.0.0.0` is undesired)*: Set `dashboard.cors_origins` in the config to whitelist the external domain.