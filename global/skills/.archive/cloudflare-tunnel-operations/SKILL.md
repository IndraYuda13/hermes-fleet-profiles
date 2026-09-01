---
name: cloudflare-tunnel-operations
description: Use when exposing, routing, operating, or troubleshooting services through Cloudflare Tunnel, including dashboard deployments, ingress rules, DNS routing, host headers, caches, and WebSocket failures.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [cloudflare, cloudflared, tunnel, ingress, dns, reverse-proxy, dashboard]
    related_skills: [hermes-agent, systematic-debugging]
---

# Cloudflare Tunnel Operations

## Overview

Operate a tunnel as a chain—public hostname, DNS route, cloudflared ingress, local origin, and application host/origin policy. Change one layer deliberately and verify both the local origin and the public route before blaming cache or the app.

## When to Use

- Exposing a local web service through Cloudflare Tunnel.
- Adding, modifying, or debugging cloudflared ingress and DNS routes.
- Fixing blank pages, 400/403/404 responses, or WebSocket failures behind a tunnel.
- Deploying Hermes Dashboard under systemd with a secure public entry point.

## Safe Workflow

1. Identify the tunnel, systemd unit, config file, target hostname, and local listener.
2. Inspect the complete ingress list. Each host gets one `service`; retain a final `http_status:404` fallback.
3. Keep local origins loopback-bound unless the application is explicitly configured for authenticated public binding.
4. Route DNS to the chosen tunnel explicitly: `cloudflared tunnel route dns -f <tunnel> <hostname>`.
5. Restart with systemd and inspect status; never detach a second unmanaged cloudflared process.
6. Verify the local origin, then the public route, and only then investigate CDN/browser caching.

## Ingress Pattern

```yaml
ingress:
  - hostname: app.example.com
    service: http://127.0.0.1:9119
    originRequest:
      httpHostHeader: 127.0.0.1
  - service: http_status:404
```

Use host-header rewriting only when the loopback-bound origin requires it. A strict application can still reject a browser WebSocket because its public `Origin` differs; solve that with its supported authenticated public-bind/CORS configuration, never by patching out validation.

## Hermes Dashboard

Run the dashboard through a restartable systemd unit on `127.0.0.1`. It needs a valid auth configuration before a public bind is safe. With a loopback bind, the ingress normally needs `httpHostHeader: 127.0.0.1`; if PTY WebSockets report `origin_mismatch`, configure the dashboard's supported CORS/origin and authentication settings rather than weakening source code.

## Diagnostics

```bash
systemctl status <cloudflared-unit> --no-pager
cloudflared tunnel list
curl -sSI -H 'Host: 127.0.0.1' http://127.0.0.1:<port>
cloudflared tunnel route dns -f <tunnel-id-or-name> <hostname>
```

- **404:** confirm the hostname reaches the correct tunnel and ingress rule before adding application endpoints.
- **400 / invalid host:** confirm origin host-header policy and rewrite only if appropriate.
- **WebSocket 1006/origin mismatch:** inspect application CORS/origin policy; a successful HTTP page does not prove websocket compatibility.
- **Blank page after a repair:** verify source and DNS first; then use a hard refresh or purge stale CDN assets.

## Completion Record

Report the tunnel/unit/config file changed, hostname, target listener, DNS operation, and the exact local/public checks run.
