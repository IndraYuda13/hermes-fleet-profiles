---
name: network-proxy-troubleshooting
description: Misleading 404/403/auth/stream errors from local proxies, reverse proxies, containers, tunnels, or AI gateways.
version: 2.0.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [networking, proxy, docker, cloudflared, gateway, nginx, troubleshooting]
    related_skills: [cloudflare-tunnel-operations]
---

# Network and Proxy Troubleshooting

## When to Use

Use when a request fails through a local gateway, container, reverse proxy, tunnel, or AI gateway and the client-side status code is misleading (wrong 404/403/401, ghost errors, stale bundles, broken streams). The status code at the client is not proof that the named endpoint, credential, or proxy is the source of the fault.

## Triage order

1. Capture the exact request, response headers/body, and the log source that emitted it.
2. Prove the intended architecture: which process should own the endpoint, authentication, and stream?
3. Test the path one hop at a time: caller → container/network → proxy/tunnel → origin service.
4. Inspect proxy environment variables and hostname/IP resolution before changing application code.
5. Apply one boundary-specific fix and rerun the same request through the full path.

## Container-to-host and proxy routes

- In bridge networking, `localhost` refers to the container. Resolve the host bridge or attach services to a shared Docker network and use service DNS.
- Check `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, and `NO_PROXY` before blaming the app — proxy variables commonly reroute private traffic unexpectedly. Add all intended private destinations to both `NO_PROXY` and `no_proxy`.
- A local bypass URL is not reachable as `localhost` from a container and may additionally be blocked by application SSRF policy — prefer the host gateway IP or `host.docker.internal` and whitelist it.
- Container-to-container calls routed via the `docker0` gateway can drop packets on iptables/firewall rules — use the target container's network IP, or better, connect both to a shared custom network and use service DNS.
- Async SOCKS5 clients (aiohttp/httpx) default to remote DNS (`rdns=True`), which local relays reject — set `rdns=False` on the connector (`ProxyConnector.from_url(..., rdns=False)`) or requests fail with `ProxyError` / `Server disconnected`.

## Symptom → first proof

| Symptom | First proof to collect |
|---|---|
| 404 | target service route table + caller path/base URL; verify the endpoint should exist on that service at all (frontend logs leak into backend views; bot engines may act internally without HTTP) |
| JSON parse failure | raw status, headers, and leading body bytes (HTML block page or SSE stream, not JSON) |
| Invalid credential | full configured key via a non-truncated read (hex-decode SQLite values) |
| Connection refused | listener bind address/port probed from the caller's namespace |
| WebSocket 1006 / origin mismatch | proxy upgrade behavior + application origin/CORS decision |
| 403 or empty results from proxied search | missing `X-Forwarded-For`/`X-Real-IP` at the reverse proxy, or a flagged datacenter egress IP (payload degrades silently — engines return empty, not errors) |

When a proxy or search path is degraded mid-task, report the failure and continue with fallbacks in the same turn — never stall on the first 403 or empty response.

## Credentials, strict JSON parsing, and streaming

- Never copy a value that terminal output has elided with `...` — retrieve long values in an untruncated representation (e.g. hex) and decode locally.
- If a JSON parser receives `invalid character` errors, capture the raw response first: it may be an HTML proxy block page or an SSE stream, not JSON.
- OpenAI-compatible clients behind a local gateway/proxy MUST support line-by-line SSE parsing (`data: {...}`) when `stream` framing is active, to avoid `JSONDecodeError` and silent model fallbacks. Confirm the caller's streaming mode before changing models or credentials.
- Upstream LLMs may wrap JSON output in Markdown fencing (```` ```json ````) even when `json_mode` is requested; capture the raw payload before parsing, and distinguish an application spec boundary from an upstream/gateway issue before changing anything. For combo/alias models on a gateway, upstream route selection can determine raw vs fenced output. Gateway audit depth: `references/9router-local-gateway.md`.

## AI gateway cases

A local model gateway can have separate guard-level and handler-level auth, lifecycle requirements, Docker reachability, CORS behavior, and stream framing. Work from the request origin outward. For read-only OpenAI-compatible gateway audits (`/v1/models`, chat, SSE termination, tool calling, `response_format`, combo fallback, retry, compression probes) see `references/9router-local-gateway.md`; historical case files: `references/9router-troubleshooting-legacy.md`.

## Reverse proxies (Nginx)

- Host-header rewriting: a loopback-only origin may require an internal host header; a public-origin WebSocket endpoint may reject it. Test both an HTTP request and the browser/WebSocket path before toggling. See `references/cloudflared-websocket-and-host-headers.md`.
- Split proxy buffering, connect/read timeouts, and upgrade-header mapping between streaming routes and REST routes — wrong values cause either stale-silent streams or hanging clients. Full rules: `references/nginx-caching-and-streaming.md`.
- Cache-Control + `add_header` interactions (dual headers, location-block header shadowing, CSP vs Cloudflare-injected beacon, SPA bundle staleness): `references/nginx-caching-and-streaming.md`.
- Node/Express services behind a proxy need `trust proxy` / `N8N_PROXY_HOPS=1` or the rate limiter crashes on `X-Forwarded-For`.

## Geo-restricted upstreams

- Streaming/media APIs behind regional gateways often return HTTP 200 while silently degrading payload structure (null/empty card arrays) — validate inner payload fields, not just the status code.
- Never trust a single IP-geo service for proxy egress (datacenter ASNs show inconsistent country attribution across databases) — probe multiple endpoints.
- Before switching production egress proxies: ≥5 consecutive latency/jitter probes through the candidate node, plus a real extractor smoke test (`yt-dlp --proxy socks5://<host>:<port>`) against a known-blocked title.

## Verification checklist

- [ ] The real response body and producing component were identified.
- [ ] Every network hop was tested independently.
- [ ] Proxy variables and Docker name/IP routing were checked.
- [ ] Any credential was read without display truncation.
- [ ] HTTP and WebSocket/SSE behavior were checked when relevant.
