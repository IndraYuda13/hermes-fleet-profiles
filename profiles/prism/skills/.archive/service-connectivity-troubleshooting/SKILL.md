---
name: service-connectivity-troubleshooting
description: Use when internal services fail through Docker, proxies, reverse proxies, or API routes with unexpected 404, authentication, connection, proxy, or WebSocket errors.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [networking, docker, proxy, api, 404, websocket, connectivity]
    related_skills: [systematic-debugging, cloudflare-tunnel-operations]
---

# Service Connectivity Troubleshooting

## Overview

A route failure can originate at the caller, proxy environment, container network, reverse proxy, local listener, or application route/auth layer. Trace the exact request across those boundaries; do not disable security controls or add endpoints just because a log contains a 404.

## When to Use

- A service returns unexpected 404, invalid-key, connection-refused, timeout, or WebSocket errors.
- Dockerized software cannot reach a local host service or proxy.
- Proxy environment variables redirect an internal request unexpectedly.
- A client expects JSON but receives an HTML/proxy/SSE response.

## Boundary-First Workflow

1. Capture the exact caller URL, method, host header, auth mode, and response body/content type.
2. Verify whether that endpoint belongs to the target service before implementing anything.
3. Test the listener locally from its own network namespace, then test from the caller/container namespace.
4. Inspect `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY`, and `no_proxy` at the failing process.
5. Inspect Docker networks and prefer a shared custom network plus service DNS over guessed bridge addresses where possible.
6. Verify authentication with the full configured credential through approved secret handling; never rely on visibly truncated terminal output.
7. For browser/WebSocket failures, validate host and origin policy separately from ordinary HTTP reachability.

## Docker and Proxy Rules

- In a container, `localhost` refers to that container—not the host.
- Use `host.docker.internal` where supported, a verified host-gateway mapping, or a shared network/service name.
- Set `NO_PROXY` for loopback, host gateway, and internal service names so traffic does not escape through an external proxy.
- Do not remove SSRF protections to make a private address reachable. Configure an approved internal route or allowlist instead.

## Response Diagnosis

| Symptom | First proof to collect |
|---|---|
| 404 | target service route table and caller path/base URL |
| JSON parse failure | raw response status, headers, and leading body bytes |
| Invalid credential | selected auth mechanism and non-truncated configured key reference |
| Connection refused | listener bind address/port from caller namespace |
| WebSocket 1006 | proxy upgrade behavior plus application origin/CORS decision |

## Common Pitfalls

- Restarting every component before preserving evidence.
- Treating frontend logs as proof a backend endpoint should exist.
- Assuming Docker bridge addresses or `localhost` are portable.
- Letting an outbound proxy capture local API traffic.
- “Fixing” a network path by bypassing SSRF, auth, or origin protections.

## Verification Checklist

- [ ] Caller-to-target route and network namespace were identified.
- [ ] Response body/type was inspected rather than inferred from an error label.
- [ ] Proxy variables and NO_PROXY exclusions were checked.
- [ ] Auth and origin policies were verified without weakening security controls.
- [ ] A focused end-to-end request now proves the intended route.
