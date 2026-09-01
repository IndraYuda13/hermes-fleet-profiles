# Cloudflared host-header and WebSocket reference

Use origin host-header rewriting only to satisfy a verified origin requirement. A local dashboard may need `httpHostHeader: 127.0.0.1` for regular HTTP, while an application WebSocket may validate the browser's external `Origin` and fail with an origin mismatch.

1. Test the local origin with the required Host header.
2. Test the public HTTP page after the tunnel.
3. Test the WebSocket/interactive path separately and inspect origin logs.
4. If the app supports an external-origin or authenticated public-bind setting, use it instead of source patches.
5. If a bad static response was cached during setup, hard-refresh or purge the relevant Cloudflare cache after validating routing.
