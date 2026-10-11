# Cloudflared host-header and WebSocket reference

Use origin host-header rewriting only to satisfy a verified origin requirement. A local dashboard may need `httpHostHeader: 127.0.0.1` for regular HTTP, while an application WebSocket may validate the browser's external `Origin` and fail with an origin mismatch.

1. Test the local origin with the required Host header.
2. Test the public HTTP page after the tunnel.
3. Test the WebSocket/interactive path separately and inspect origin logs.
4. If the app supports an external-origin or authenticated public-bind setting, use it instead of source patches.
5. If a bad static response was cached during setup, hard-refresh or purge the relevant Cloudflare cache after validating routing.

## Hermes dashboard behind a tunnel

- The dashboard refuses to bind `0.0.0.0` or accept remote CORS origins until an auth provider is configured. Expose it through a tunnel only with auth enabled, or keep the local `127.0.0.1` binding and use SSH tunneling.
- WebSocket `origin_mismatch` on a custom-domain tunnel is DNS-rebinding protection, not a bug to patch out. Fix natively: `hermes config set dashboard.cors_origins "['https://yourdomain.com']"` (or `dashboard.host: 0.0.0.0` together with `dashboard.auth`) — never edit `hermes_cli/web_server.py`.
- WebSocket 1006 through a tunnel usually means `originRequest: httpHostHeader: localhost` forces the Host header and a strict backend (FastAPI/Starlette) then rejects the browser's real origin with 403. Remove the override so the public hostname passes through, or allow that origin in the backend's CORS config.
- If Hermes stopped showing tool progress on Telegram, that is display defaults, not networking: set `display.tool_progress: all` and `display.platforms.telegram.busy_ack_detail: true`, then restart the dashboard service.
