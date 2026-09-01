# Operator v1 — Deployment Reference

## Cloudflare Tunnel Deployment

The PML API can be exposed via Cloudflare Tunnel for remote dashboard access.

### API Binding

The API is hardcoded loopback-only (`API_HOST` validator rejects non-loopback). Cloudflare Tunnel forwards from the public hostname to `127.0.0.1:8000`.

### CORS Configuration

Set `PML_DASHBOARD_ORIGIN=https://<public-hostname>` in `.env` so browser-initiated API calls (from dashboard JS) pass CORS. The API uses FastAPI CORSMiddleware with `allow_origins` including the configured `DASHBOARD_ORIGIN`.

### Ingress Entry

Standard entry, no host-header rewrite needed (FastAPI has no host validation middleware beyond the CORS layer):

```yaml
- hostname: prediction-lab.indrayuda.my.id
  service: http://127.0.0.1:8000
```

### Port Conflict

Port 8000 may be used by other services (e.g. `jualubot`). Check with `fuser 8000/tcp` before starting. If persistent, change `PML_API_PORT` in `.env` and update the ingress entry.

### Running as Background Process vs Systemd

Currently runs as a background process. For persistence across reboots, create a systemd unit:

```ini
[Unit]
Description=Prediction Market Lab API
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/root/pml-operator-v1/prediction-market-lab-operator-v1
ExecStart=/root/pml-operator-v1/prediction-market-lab-operator-v1/.venv/bin/python3 -m services.api.launcher
Restart=on-failure
RestartSec=5s
EnvironmentFile=/root/pml-operator-v1/prediction-market-lab-operator-v1/.env

[Install]
WantedBy=multi-user.target
```

### Live URL

https://prediction-lab.indrayuda.my.id/
