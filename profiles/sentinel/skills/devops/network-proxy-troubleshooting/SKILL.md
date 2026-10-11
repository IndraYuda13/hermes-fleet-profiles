---
name: network-proxy-troubleshooting
description: Use when requests fail with misleading 404/403, authentication, connection, or streaming errors at local services, containers, reverse proxies, AI gateways, or Cloudflare bot-protection.
version: 1.1.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [networking, proxy, docker, cloudflared, cloudflare, turnstile, bot-protection, gateway, troubleshooting]
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

Preserve evidence before restarting anything: restarting components during diagnosis masks the original fault. Test the listener from its own network namespace, then from the caller's.

| Symptom | First proof to collect |
|---|---|
| 404 | target service's route table and the caller's path/base URL |
| JSON parse failure | raw status, headers, and leading body bytes |
| Invalid credential | selected auth mechanism and a non-truncated key reference |
| Connection refused | listener bind address/port probed from the caller's namespace |
| WebSocket 1006 | proxy upgrade behavior plus the application's origin/CORS decision |
| 403 at an edge | bot-protection/challenge markers in the response vs a genuine origin 403 |

## Container-to-host and proxy routes

In bridge networking, `localhost` refers to the container. Resolve the host bridge or attach services to a shared Docker network and use service DNS. Check `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, and `NO_PROXY`; proxy variables commonly reroute private traffic unexpectedly. Add all intended private destinations to both `NO_PROXY` and `no_proxy`.

For a service behind Cloudflared, decide host-header rewriting from the origin's validation behavior. A loopback-only origin may require an internal host header; a public-origin WebSocket endpoint may reject it. Do not toggle the header blindly—test both an HTTP request and the browser/WebSocket path. See `references/cloudflared-websocket-and-host-headers.md`.

Prefer shared custom networks (`docker network connect <network> <container>`) with service DNS over host-gateway IP routing; default-bridge gateway paths can silently drop packets on host firewall rules. Never disable SSRF protections to make a private address reachable — configure an approved internal route or allowlist instead.

SOCKS5 client connectors default to remote DNS (`rdns=True`); a local relay without remote resolution fails instantly with `ProxyError`/`Server disconnected`, so set `rdns=False` for local SOCKS relays.

## Credentials, strict JSON parsing, and streaming

Do not copy a value that terminal output has elided with `...`. Retrieve long SQLite values in an untruncated representation (for example hex), then decode locally. If a JSON parser receives `invalid character` errors, capture the raw response first: it may be an HTML proxy block or an SSE stream. OpenAI-compatible clients interfacing with 9Router or similar local proxies MUST support line-by-line SSE parsing (`data: {...}`) when `stream` framing is active, to avoid `JSONDecodeError` and unexpected fallbacks. Confirm the caller's streaming mode before changing models or credentials.

### Upstream LLM Markdown Fencing (````json`) vs Strict JSON Parsers
When routing structured output requests (`response_format: {"type": "json_object"}`) through AI gateways (e.g. 9Router) to various upstream LLM providers (Gemini, Grok, Claude, local models):
- **Problem:** Certain LLM backends (or specific models under load balancing) wrap their JSON output in Markdown code blocks (e.g., ````json\n{...}\n````), even when `json_mode` / `json_object` is requested.
- **Symptom:** Strict JSON validators or applications with anti-fencing security rules fail with errors like `ValueError: Markdown-fenced JSON is rejected`.
- **Diagnosis:** Capture the raw LLM response payload from the gateway (`client.complete_response` or raw HTTP body) before parsing to check if `response.content` begins with ` ``` `.
- **Handling:** Verify whether the strictness is an explicit security/spec boundary of the application (e.g., strict contract invariants) or an upstream gateway/prompt issue before attempting modifications. For 9Router combo/alias models, upstream route selection (`route_fingerprint`) can determine whether a model emits raw JSON or fenced JSON.

## Tunnel Exposure & Mutating Endpoint Security
When local dashboards or microservices are mapped to public Cloudflare Tunnels:
- **Unauthenticated Mutating APIs**: Check if internal endpoints (e.g., `/api/actions/*` for fund withdrawal, credentials, service restarts) are left unauthenticated on the public tunnel hostname. Ensure Cloudflare Zero Trust / Access or HTTP basic/bearer auth gates every mutating route.
- **Wildcard CORS Risks**: Avoid `Access-Control-Allow-Origin: *` on mutating endpoints. Cross-origin requests from third-party sites can trigger unintended state mutations.

## AI gateway and 9router cases

A local model gateway can have separate guard-level and handler-level auth, service lifecycle requirements, Docker reachability, CORS behavior, and stream framing. Work from the request origin outward; a local bypass URL is not reachable as `localhost` from a container and may be blocked by application SSRF policy. For read-only 9Router/OpenAI-compatible audits, including `/v1/models`, chat, SSE termination, tool calling, `response_format`, combo fallback, retry, and compression probes, use `references/9router-local-gateway.md`.

## Cloudflare bot-protection and Turnstile bypass (authorized automation)

When an edge (Cloudflare) blocks the automated client while browsers pass, harvest clearance with a local Turnstile solver (`/cf_clearance?url=<target>` task plus `/result?id=<taskId>` polling; the same daemon solves widget tokens via `/turnstile?url=...&sitekey=...`) and obey its binding rules:

- `cf_clearance` is bound to exit IP, TLS fingerprint, and User-Agent: the client context MUST use the solver's returned `user_agent`, and one preserved context must carry the cookies across every navigation of a multi-step (e.g. OAuth) flow.
- Turnstile widget tokens are bound to the solving egress IP: pass the same `proxy` parameter to the solver task that the worker session uses, and inject the token into `input[name="cf-turnstile-response"]` or the payload's `captchaResponse` through that same egress.
- Match Client Hints (`Sec-CH-UA`, `-Mobile`, `-Platform`) to the emulated device profile to avoid heuristic fingerprint bans.
- Auth flows lie about the cause: a missing or invalid Turnstile response usually surfaces as a silent redirect to `/reset-password?email=...`, not an error.
- Playwright form quirks: when `.click()` does not trigger framework state updates, fill inputs explicitly and `press('input[name=...]', 'Enter')` or target `data-testid` selectors; never append a cookie list to itself before `add_cookies`.

Solver deployment, cookie-injection code shape, and a worked auth-flow example (x.ai: gRPC endpoints, sitekey, OAuth device flow) live in `references/cloudflare-bypass.md`.

## Verification checklist

- [ ] The real response body and producing component were identified.
- [ ] Every network hop was tested independently.
- [ ] Proxy variables and Docker name/IP routing were checked.
- [ ] Any credential was read without display truncation.
- [ ] HTTP and WebSocket/SSE behavior were checked when relevant.
- [ ] For edge 403s, solver and client IP/User-Agent bindings were aligned.
