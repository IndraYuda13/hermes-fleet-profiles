# Cloudflared host-header and WebSocket reference

Use origin host-header rewriting only to satisfy a verified origin requirement. A local dashboard may need `httpHostHeader: 127.0.0.1` for regular HTTP, while an application WebSocket may validate the browser's external `Origin` and fail with an origin mismatch.

1. Test the local origin with the required Host header.
2. Test the public HTTP page after the tunnel.
3. Test the WebSocket/interactive path separately and inspect origin logs.
4. If the app supports an external-origin or authenticated public-bind setting, use it instead of source patches.
5. If a bad static response was cached during setup, hard-refresh or purge the relevant Cloudflare cache after validating routing.

## Public HTTPS authentication behind a loopback proxy

1. Inspect the deployed application's origin resolver and same-origin guard together with the effective proxy headers. Capture actual public POST status and fresh runtime warnings; public GET200 alone does not exercise auth or CSRF.
2. Back up the target application's proxy stanza and private runtime configuration with restrictive permissions. Keep the source/build immutable and preserve unrelated private settings and new database writes.
3. Set the application's supported external-origin setting to the exact HTTPS origin. For an owned NGINX boundary, set `proxy_set_header Host <exact-public-host>;`, pass `proxy_set_header Origin $http_origin;`, and pin trusted forwarded Host/Proto to the owned public hostname and `https`. Do not manufacture a normal Origin for foreign or missing-Origin requests, add allow-all CORS, or disable the guard.
4. Run `nginx -t` before `systemctl reload nginx`, then restart only the affected application if its environment changed. Re-read the effective config and actual process/build identity. Roll back only this config/proxy change if it fails, never the database or an older unsafe application.
5. Exercise signup/login/logout and persisted owned class/group state through public HTTPS with a real cookie jar. Record only cookie name, Secure, HttpOnly, SameSite and Path. Verify separate board/device cookies stay scoped to their intended API path and do not authorize teacher/admin APIs.
6. Send a foreign-Origin state-changing request with an actual authenticated session. Require403 and compare the exact owned fixture state before/after; also verify a rejected foreign logout leaves the legitimate session usable. Test missing-Origin behavior against the source contract instead of assuming it should match foreign-Origin behavior.
7. Bind the sanitized receipt to current source SHA, BuildID, private-config/proxy hashes, raw probe exits and actual tested paths. State token-refresh and connected board/WebSocket lifecycle gaps explicitly; identity/challenge creation or assignment persistence is not evidence of a complete connected board flow. Retain prior synthetic fixtures and credentials privately when cleanup is not authorized.
