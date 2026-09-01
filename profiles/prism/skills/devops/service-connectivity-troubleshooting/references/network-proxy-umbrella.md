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

## Credentials and streaming

Do not copy a value that terminal output has elided with `...`. Retrieve long SQLite values in an untruncated representation (for example hex), then decode locally. If a JSON parser receives `invalid character` errors, capture the raw response first: it may be an HTML proxy block or an SSE stream. Confirm the caller's streaming mode before changing models or credentials.

## AI gateway and 9router cases

A local model gateway can have separate local/public auth policy, service lifecycle requirements, Docker reachability, and stream behavior. Work from the request origin outward; a local bypass URL is not reachable as `localhost` from a container and may be blocked by application SSRF policy. See `references/9router-local-gateway.md`.

## Verification checklist

- [ ] The real response body and producing component were identified.
- [ ] Every network hop was tested independently.
- [ ] Proxy variables and Docker name/IP routing were checked.
- [ ] Any credential was read without display truncation.
- [ ] HTTP and WebSocket/SSE behavior were checked when relevant.
