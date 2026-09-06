---
name: network-proxy-troubleshooting
description: Use when local services, containers, reverse proxies, or AI gateways return misleading 404, authentication, connection, or streaming errors.
version: 1.0.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [networking, proxy, docker, cloudflared, gateway, troubleshooting]
    related_skills: [cloudflare-tunnel-management]
---

# Network and Proxy Troubleshooting

## Overview

Use this umbrella to locate the actual failing boundary when a request fails through a local gateway, container, reverse proxy, or tunnel. A status code at the client is not proof that the named endpoint, credential, or proxy is the source of the fault.

## Triage order

1. Capture the exact request, response headers/body, and the log source that emitted it.
2. Prove the intended architecture: which process should own the endpoint, authentication, and stream?
3. Test the path one hop at a time: caller → container/network → proxy/tunnel → origin service.
4. Inspect proxy environment variables and hostname/IP resolution before changing application code.
5. Apply one boundary-specific fix and rerun the same request through the full path.

## Container-to-host and proxy routes

In bridge networking, `localhost` refers to the container. Resolve the host bridge or attach services to a shared Docker network and use service DNS. Check `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, and `NO_PROXY`; proxy variables commonly reroute private traffic unexpectedly. Add all intended private destinations to both `NO_PROXY` and `no_proxy`.

For a service behind Cloudflared, decide host-header rewriting from the origin's validation behavior. A loopback-only origin may require an internal host header; a public-origin WebSocket endpoint may reject it. Do not toggle the header blindly—test both an HTTP request and the browser/WebSocket path. See `references/cloudflared-websocket-and-host-headers.md`.

## Credentials, strict JSON parsing, and streaming

Do not copy a value that terminal output has elided with `...`. Retrieve long SQLite values in an untruncated representation (for example hex), then decode locally. If a JSON parser receives `invalid character` errors, capture the raw response first: it may be an HTML proxy block or an SSE stream. OpenAI-compatible clients interfacing with 9Router or similar local proxies MUST support line-by-line SSE parsing (`data: {...}`) when `stream` framing is active, to avoid `JSONDecodeError` and unexpected fallbacks. Confirm the caller's streaming mode before changing models or credentials.

### Upstream LLM Markdown Fencing (````json`) vs Strict JSON Parsers
When routing structured output requests (`response_format: {"type": "json_object"}`) through AI gateways (e.g. 9Router) to various upstream LLM providers (Gemini, Grok, Claude, local models):
- **Problem:** Certain LLM backends (or specific models under load balancing) wrap their JSON output in Markdown code blocks (e.g., ````json\n{...}\n````), even when `json_mode` / `json_object` is requested.
- **Symptom:** Strict JSON validators or applications with anti-fencing security rules fail with errors like `ValueError: Markdown-fenced JSON is rejected`.
- **Diagnosis:** Capture the raw LLM response payload from the gateway (`client.complete_response` or raw HTTP body) before parsing to check if `response.content` begins with ` ``` `.
- **Handling:** Verify whether the strictness is an explicit security/spec boundary of the application (e.g., strict contract invariants) or an upstream gateway/prompt issue before attempting modifications. For 9Router combo/alias models, upstream route selection (`route_fingerprint`) can determine whether a model emits raw JSON or fenced JSON.

## AI gateway and 9router cases

A local model gateway can have separate guard-level and handler-level auth, service lifecycle requirements, Docker reachability, CORS behavior, and stream framing. Work from the request origin outward; a local bypass URL is not reachable as `localhost` from a container and may be blocked by application SSRF policy. For read-only 9Router/OpenAI-compatible audits, including `/v1/models`, chat, SSE termination, tool calling, `response_format`, combo fallback, retry, and compression probes, use `references/9router-local-gateway.md`.

## Cloudflare Edge Cache & Reverse-Proxy Asset Staleness (SPA/JS Bundle Mismatch)

- **Problem:** When Nginx/reverse proxy sets long `Cache-Control` (e.g. `expires 7d; max-age=604800`) on executable static assets (`.js`, `.css`, `.json`), Cloudflare edge caches and client mobile browsers serve outdated bundles after a deployment. If HTML templates are dynamic/no-cache while script assets remain cached, clients experience runtime initialization crashes (e.g. missing Alpine.js stores or undefined state properties).
- **Remediation:**
  1. **Split Nginx Asset Blocks:** Keep immutable fonts/images on long caching (`expires 7d; max-age=604800`), but configure `.js|.css|.json` with `expires -1;` and `add_header Cache-Control "no-cache, no-store, must-revalidate, max-age=0";`.
  2. **Avoid Header Duplication (expires -1 vs Cache-Control):** In Nginx, using `expires -1;` automatically emits `Cache-Control: no-cache`. Pairing it with `add_header Cache-Control "no-cache, no-store, must-revalidate, max-age=0";` produces dual `Cache-Control` headers on the wire. Drop `expires -1;` when defining explicit `Cache-Control` via `add_header`.
  3. **Nginx Header Inheritance Pitfall (Shadowing):** Any `add_header` defined in a child `location` block completely overrides and suppresses all `add_header` declarations from the parent `server` block. Always use an `include /etc/nginx/snippets/security-headers.conf` or replicate mandatory security headers (`X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, `X-Content-Type-Options`) inside every static/custom location block.
  4. **Query String Cache-Busting:** Inject explicit versioning parameters into HTML asset tags (e.g. `/js/app.js?v=2.0.0`, `/css/styles.css?v=2.0.0`) to immediately force Cloudflare edge cache misses (`cf-cache-status: BYPASS`) and mobile browser cache eviction without requiring Cloudflare API purge keys.
  5. **Verification:** Test via `curl -I "https://domain/js/app.js?v=2.0.0"` to verify `cf-cache-status: BYPASS` / `Cache-Control: no-store, no-cache`, followed by `curl -s` payload inspection.
  6. **Pitfall — No-Store on Versioned Bundles:** Avoid adding `no-store` globally to hashed or query-versioned static assets (`styles.css?v=...`). `no-store` completely disables browser disk caching and ETag 304 validation, forcing clients to re-download heavy CSS/JS bundles on every page navigation. Use `no-cache, must-revalidate` or immutable content hashing (`max-age=31536000, immutable`).

## Reverse Proxy Tuning for Streaming Endpoints vs REST APIs (Nginx & FastAPI/Uvicorn)

- **Proxy Buffering Segregation:**
  - Streaming endpoints (e.g. fragmented MP4 remuxing, video chunking, live SSE) require `proxy_buffering off;` so chunks are delivered immediately to clients without Nginx staging them in disk/memory temp buffers.
  - Applying `proxy_buffering off;` globally to `/api/` degrades REST API performance by forcing micro-writes over the wire. Keep REST routes (`/api/`) on `proxy_buffering on; proxy_buffer_size 8k; proxy_buffers 16 8k;` and isolate streaming routes (`location /api/stream/ { proxy_buffering off; }`).
- **Upstream Connect vs Read Timeouts:**
  - Setting `proxy_connect_timeout 600s;` on localhost loopback (`127.0.0.1`) creates hanging client connections if the backend daemon crashes or hangs. Keep loopback `proxy_connect_timeout` low (`5s`).
  - Set high read timeouts (`proxy_read_timeout 600s;`) specifically for streaming routes (`/api/stream/`) where clients may pause or buffer, while keeping REST API read timeouts bounded (`30s`).
- **Dynamic WebSocket / HTTP Upgrade Mapping:**
  - Never hardcode `proxy_set_header Connection "upgrade";` globally in Nginx locations. If the request is a standard HTTP request, sending `Connection: upgrade` violates RFC 7230 and breaks upstream HTTP/1.1 keep-alive pooling.
  - Always use standard map directives:
    ```nginx
    map $http_upgrade $connection_upgrade {
        default upgrade;
        '' close;
    }
    ```
    Then inside location: `proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection $connection_upgrade;`.

## Upstream Geo-Restriction & Silent API Payload Degradation

- **Problem:** Streaming/media APIs (e.g. Bstation / Bilibili TV) behind regional CDN/gateways often return HTTP `200 OK` even when geoblocked, but silently degrade payload structure:
  - Timeline APIs return HTTP `200` with empty/null card arrays (`"cards": null` across all date entries), crashing downstream parsers with `'NoneType' object is not iterable` (500 Internal Server Error).
  - Stream/playurl extractors (e.g. `yt-dlp` / BiliIntl) fail hard with explicit geo-restriction errors (`[BiliIntl] This video is not available from your location due to geo restriction`).
- **Diagnosis & Verification Protocol:**
  1. **Multi-Source Geo IP Check:** Never trust a single IP lookup service. Some datacenters/ASNs show inconsistent country attribution across databases (e.g. `ipinfo.io` showing Singapore while `ipwho.is` and `am.i.mullvad.net` resolve Thailand/Bangkok). Probe multiple endpoints (`curl -s --socks5 <proxy> https://ipwho.is/` and `https://am.i.mullvad.net/json`).
  2. **Payload-Level Validation (Not Just HTTP 200):** Inspect inner payload fields rather than HTTP status alone: verify `sum(len(d.get('cards') or []) for d in items) > 0`.
  3. **Multi-Trial Latency & Jitter Probing:** Run at least 5 consecutive calls through the candidate proxy node measuring `time_connect` and `time_total` to ensure latency stability (e.g. <300ms) and zero packet loss before switching production systemd egress proxies.
  4. **Direct Stream Extraction Smoke Test:** Test yt-dlp / extractor against a known geoblocked title/episode using `--proxy socks5://<host>:<port>` to verify valid CDN mirror URLs (e.g. Akamai/UPOS) are returned.

## Verification checklist

- [ ] The real response body and producing component were identified.
- [ ] Every network hop was tested independently.
- [ ] Proxy variables and Docker name/IP routing were checked.
- [ ] Any credential was read without display truncation.
- [ ] HTTP and WebSocket/SSE behavior were checked when relevant.
