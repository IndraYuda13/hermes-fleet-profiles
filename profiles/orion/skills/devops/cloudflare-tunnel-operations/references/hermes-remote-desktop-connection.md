# Remote Desktop to Headless Hermes Dashboard / Gateway Connection

When connecting a local Hermes Desktop App (Electron) to a remote headless Hermes instance (e.g. VPS behind Cloudflare Tunnel):

## 1. Static Session Token Configuration
By default, `hermes dashboard` generates a random session token on every process startup (`_resolve_session_token()` via `secrets.token_urlsafe(32)`). To prevent Desktop app disconnection upon VPS/service restart, export a static token in the systemd unit.

In `/etc/systemd/system/hermes-dashboard.service`:
```ini
[Service]
Environment="HERMES_DASHBOARD_SESSION_TOKEN=your-custom-static-token"
```

Reload and restart:
```bash
systemctl daemon-reload
systemctl restart hermes-dashboard
```

## 2. Desktop Connection Configuration
In Hermes Desktop App (**Settings** → **Gateway**):
- **Mode:** `Remote`
- **Remote URL:** `https://hermes.yourdomain.com`
- **Session Token:** `your-custom-static-token`

## 3. Ingress Header Requirements
Ensure the Cloudflare Tunnel ingress configuration rewrites the Host header:
```yaml
ingress:
  - hostname: hermes.yourdomain.com
    service: http://127.0.0.1:9119
    originRequest:
      noTLSVerify: true
      httpHostHeader: 127.0.0.1
```
