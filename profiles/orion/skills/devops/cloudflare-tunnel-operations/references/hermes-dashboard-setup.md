# Exposing Hermes Agent Dashboard via Cloudflare Tunnels

The Hermes Agent Dashboard (`hermes dashboard`) enforces strict host-header validation on non-localhost bindings. When deploying it permanently on a headless VPS behind a Cloudflare tunnel, it must run as a background service binding to `127.0.0.1`, and the tunnel must rewrite the `Host` header.

## 1. Systemd Service Configuration
Create `/etc/systemd/system/hermes-dashboard.service`:

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

Enable and start:
```bash
systemctl daemon-reload
systemctl enable hermes-dashboard
systemctl start hermes-dashboard
```

## 2. Cloudflared Ingress Rule
In `/etc/cloudflared/config-<tunnel-name>.yml`:

```yaml
ingress:
  - hostname: hermes.yourdomain.com
    service: http://127.0.0.1:9119
    originRequest:
      httpHostHeader: 127.0.0.1
```

*Note: Without the `originRequest` block, Cloudflare forwards `Host: hermes.yourdomain.com`. The Hermes internal Uvicorn server will reject this with a `400 Bad Request` or an invalid host header error, resulting in a blank white page on the client side.*

## 3. Clear Caches
If a misconfiguration occurred first, Cloudflare's Edge nodes will cache the 404/403 responses for static dashboard assets (e.g., `index-*.js`). The user must perform a hard refresh or purge the Cloudflare zone cache.
