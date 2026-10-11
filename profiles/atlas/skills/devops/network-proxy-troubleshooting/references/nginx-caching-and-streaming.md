# Nginx Caching, Headers, and Streaming Reverse-Proxy Tuning

Always-on rules live in SKILL.md. This file is the depth for Nginx `Cache-Control` / `add_header` interactions and buffering/timeout splits.

## Static-asset caching vs SPA staleness

- Keep long caching for immutable assets (fonts, images, hashed bundles); configure `.js|.css|.json` with explicit `Cache-Control: no-cache, no-store, must-revalidate, max-age=0` when clients must see fresh bundles after deployment.
- `expires -1;` already emits `Cache-Control: no-cache` — pairing it with an explicit `add_header Cache-Control ...` produces dual `Cache-Control` headers on the wire. Drop `expires -1;` when using `add_header`.
- `add_header` in a child `location` block completely overrides ALL parent `server`-block `add_header` declarations. Use an include snippet (e.g. `/etc/nginx/snippets/security-headers.conf`) and replicate mandatory security headers (`X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, `X-Content-Type-Options`) inside every static/custom location.
- Avoid `no-store` on versioned bundles: it kills ETag/304 validation and forces full re-downloads every navigation. Prefer `no-cache, must-revalidate` or `max-age=31536000, immutable` content hashing.
- Query-string cache-busting (`/js/app.js?v=2.0.0`) forces immediate `cf-cache-status: BYPASS` at Cloudflare edge without API purge keys. Verify: `curl -I` the versioned URL and check `cf-cache-status` + `Cache-Control`.
- After purging dev assets, ensure SPA icon references (`/favicon.ico`, `/vite.svg`) exist in `public/` AND `dist/` — browsers fetch them unconditionally and the 404s pollute production audits.

## CSP vs Cloudflare Web Analytics beacon

Cloudflare Web Analytics/RUM injects `<script src='https://static.cloudflareinsights.com/beacon.min.js'>` and beacons to `https://cloudflareinsights.com`. A strict origin CSP (`script-src 'self'`) silently blocks it. Fix: add `https://static.cloudflareinsights.com` to `script-src` and both `https://cloudflareinsights.com https://static.cloudflareinsights.com` to `connect-src` — in the server block AND any child location that re-declares `add_header` (inheritance shadowing).

## Streaming endpoints vs REST APIs

- `proxy_buffering off;` only on streaming routes (`location /api/stream/`) — fragmented MP4/SSE/video chunks must bypass Nginx staging. Keep REST routes buffered (`proxy_buffering on; proxy_buffer_size 8k; proxy_buffers 16 8k;`) — global `off` degrades REST to micro-writes.
- Keep loopback `proxy_connect_timeout` low (~5s): a high value on `127.0.0.1` creates hanging clients when the backend daemon dies. High `proxy_read_timeout` (e.g. 600s) belongs on streaming routes where clients pause; keep REST read timeouts bounded (~30s).
- Never hardcode `proxy_set_header Connection "upgrade";` globally — sending `Connection: upgrade` on plain HTTP requests violates RFC 7230 and breaks keep-alive pooling. Use the standard map:

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}
# location: proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection $connection_upgrade;
```
