---
name: service-api-verification
description: Use when verifying HTTP backend services, APIs, telemetry sync, and auth.
category: devops
---

# Service API Verification

Systematic verification workflow for backend HTTP services, REST APIs, AI-backed endpoints, telemetry synchronization, session authentication, and reverse-proxy edge behavior.

## Verification Procedure

### 1. Target Discovery and Topology Mapping
- Determine both the local origin listener (e.g. `127.0.0.1:<port>`) and the public edge URL (e.g. reverse proxy, Cloudflare domain).
- Inspect running processes (`ss -tulpn`, `ps`, environment variables) to identify active ports, routing configs, and upstream model/database providers.
- Check environment configs (`.env`, service account JSONs, secret files) to catalog credentials for zero-leak validation.

### 2. Origin vs Edge Parity Checks
- Always test identical endpoints on both local origin and public edge.
- Record status codes, latency, response headers (Server, Content-Type, Cache headers), and body hashes.
- Flag edge anomalies: caching of dynamic routes, header stripping, or TLS/proxy timeout mismatches.

### 3. Authentication and Session Flow Verification
- Inspect the authentication mechanism (cookies, Bearer tokens, headers).
- **Redirect Pitfall**: Avoid `curl -X POST -L` when testing login flows. Curl with `-X POST` forces the redirected request to remain POST, returning 405 Method Not Allowed on redirected GET dashboards.
- Use Python `requests.Session()` or distinct curl calls (POST credentials, capture cookie jar, GET target dashboard) to accurately simulate standard browser RFC 7231 redirect semantics.

### 4. API Contract and Route Verification
- When given an endpoint claim or user prompt (e.g. `GET /api/path?param=val`), inspect the actual server route definition (`methods=[...]`) and request parser (`request.json` vs `request.args`).
- If a method or parameter discrepancy exists:
  1. Test the literal user/spec request and record the actual response (e.g. 405 Method Not Allowed or 400 Bad Request).
  2. Test the valid API contract (e.g. POST with JSON body) to verify functionality.
  3. Report both clearly. Do not silently patch production code to make a mismatched test pass.

### 5. Upstream and AI Provider Verification
- For endpoints backed by LLM routers or external APIs (e.g. OpenAI-compatible proxies, Gemini, Anthropic):
  - Differentiate between cached database responses and live AI generation.
  - To verify live model generation, send a fresh/uncached input probe (e.g. timestamped nonce or unique term).
  - Inspect provider routing logs, latency, and response schemas (required JSON keys, types, structure).

### 6. Zero-Leak Credential Audit
- Extract non-trivial tokens and secrets from local configuration:
  - API keys, JWT/session secrets, database passwords, private keys.
- Scan HTTP responses across all tested routes (bodies, headers, error pages, cookies outside encrypted session hashes).
- Assert zero presence of raw credentials in responses.

### 7. Telemetry Sync & Upstream State Machine Invariants
- **Upstream Pagination & Ordering:** Upstream third-party APIs often default to ascending sort (`sort: asc, field: id`). Extract nested records defensively (e.g. check both `data.history.data` and `data.items`) and sort deterministically descending by timestamp or ID before returning the latest item to consumers.
- **Live Rendering & Cache-Busting Protocol:** Serve live templates directly from disk rather than stale in-memory constants. Enforce strict anti-caching HTTP headers across HTML and telemetry endpoints (`Cache-Control: no-cache, no-store, must-revalidate`, `Pragma: no-cache`, `Expires: 0`). Append client-side timestamp query params (`?_t=${Date.now()}`) to bypass intermediate proxy and CDN caching.
- **State Machine Safety Locks & Backoff:** Intermediate processing states (e.g. `UNDER REVIEW`, `IN PROGRESS`) must establish safety locks (`under_review = True`) and enforce backoff cooldowns to eliminate polling and trigger spam. Terminal states (`PAID`, `ERROR`) must automatically release safety locks.
- **Multi-View & Anti-CLS UI Layout:** Validate rendering consistency across all view modes (e.g. Card View, Matrix Table View). Use fixed spatial dimension placeholders to prevent Cumulative Layout Shift (CLS) when telemetry updates dynamically.

## Verification Checklist

- [ ] Local origin listener tested and status recorded.
- [ ] Public edge endpoint tested and status recorded.
- [ ] Auth login and redirection verified with session cookie preservation.
- [ ] Response schemas validated for required fields and types.
- [ ] Dynamic/AI generation verified with uncached probe.
- [ ] Telemetry pagination, ordering, and cache-busting headers verified.
- [ ] Upstream state machine safety locks and backoff cooldowns verified.
- [ ] Zero-leak scan completed with 0 secret occurrences in headers and bodies.
- [ ] Factual execution evidence formatted in clear tabular summary.
