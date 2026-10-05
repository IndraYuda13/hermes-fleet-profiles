# Service API Verification Procedure

Systematic verification workflow for backend HTTP services, REST APIs, AI-backed endpoints, telemetry synchronization, session authentication, and reverse-proxy edge behavior.

## 1. Target Discovery & Topology Mapping
- Determine both the local origin listener (`127.0.0.1:<port>`) and public edge URL (reverse proxy, Cloudflare domain).
- Inspect running processes (`ss -tulpn`, `ps`) and service unit files to identify active ports, routing configs, and upstream model/database providers.
- Catalog configuration credentials (`.env`, secret files) to prepare for zero-leak audit.

## 2. Origin vs Edge Parity
- Test identical endpoints on both local origin and public edge.
- Record status codes, latency, response headers (`Server`, `Content-Type`, `Cache-Control`), and body hashes.
- Flag edge anomalies: intermediate proxy caching of dynamic routes, header stripping, or TLS/proxy timeout mismatches.

## 3. Authentication & Redirect Semantics
- **The `curl -X POST -L` Pitfall:** Using `-X POST` with `-L` forces the redirected request to remain a POST, causing `405 Method Not Allowed` on redirected GET endpoints (dashboards, post-login pages).
- **Fix:** Use Python `requests.Session()` or execute distinct curl requests:
  1. POST credentials and save cookie jar (`curl -c cookies.txt -d ...`).
  2. GET target dashboard with cookie jar (`curl -b cookies.txt ...`).

## 4. API Contract & Route Discrepancy Testing
- When verifying an endpoint against a claim or specification, inspect actual route definitions (`methods=[...]`) and request parsers (`request.json` vs `request.args`).
- If a discrepancy exists:
  1. Test the literal user/spec request and record actual response (e.g. 405 Method Not Allowed or 400 Bad Request).
  2. Test the valid API contract (e.g. POST with JSON body) to verify underlying functionality.
  3. Report both outcomes explicitly; never silently patch production code to make a mismatched test pass.

## 5. Upstream & AI Provider Verification
- Send fresh, uncached input probes (e.g. timestamped nonce) to distinguish live model generation from cached responses.
- Assert required response schema keys, data types, and latency bounds.

## 6. Zero-Leak Credential Audit
- Extract known tokens and secrets from environment and configuration (API keys, JWT secrets, DB passwords).
- Scan HTTP response bodies, headers, and error pages across all tested routes.
- Assert zero presence of raw credentials in responses.

## 7. Telemetry Sync & State Machine Invariants
- **Pagination & Ordering:** Defensively handle nested records and sort descending by timestamp/ID before returning latest items.
- **Cache-Busting Protocol:** Serve live templates directly from disk with anti-caching headers (`Cache-Control: no-cache, no-store, must-revalidate`, `Pragma: no-cache`) and append client-side timestamp query params (`?_t=${Date.now()}`).
- **State Machine Safety Locks & Backoff:** Intermediate processing states (`UNDER_REVIEW`, `IN_PROGRESS`) must establish safety locks and enforce backoff cooldowns to eliminate polling loops. Terminal states (`PAID`, `ERROR`) must release safety locks.
- **Layout Shift Prevention:** Use fixed spatial placeholders to prevent Cumulative Layout Shift (CLS) during telemetry updates.
