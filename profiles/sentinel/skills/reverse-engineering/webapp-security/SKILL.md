---
name: webapp-security
description: Use for authorized web app and portal security reviews.
version: 1.0.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [security, threat-model, stride, rbac, xss, sqli, hardening, dos, web]
    category: reverse-engineering
---

# Web Application Security Review (internal portals & control planes)

## When to Use

Use for authorized security audits and STRIDE threat modeling of internal web applications: admin dashboards, SRE/observability portals, deployment consoles, automation control planes, and streaming backends. For pure API attack-surface work use `api-security`; for source-code/SAST review use `code-audit`; for cloud/K8s infrastructure use `cloud-k8s`; for network-path failures in front of the app use `network-proxy-troubleshooting`.

## Review workflow

1. Enumerate the trust boundaries: authentication (login, API keys, JWT, sessions), mutating routes, file/static serving, streaming (SSE/WebSocket), background jobs, and any public tunnel exposure.
2. Run the STRIDE pass (matrix below) against each boundary; record one finding per threat, each with a concrete repro.
3. Verify every hardening invariant below — each is a check, not a suggestion.
4. Exercise the probes in `scripts/security_smoke_test.py` (SQLi, path traversal, unauthenticated mutation); rejected requests must return 400/401/403/404, never 2xx/3xx.
5. Report findings ordered by exploitability, each with the exact request that demonstrates it.

## Universal invariants

- **Input → DOM:** upstream and third-party data is untrusted; HTML-escape or strict-enum-map before any `innerHTML`/template interpolation (stored DOM XSS in titles, notes, timelines, labels).
- **SQL:** parameterized queries everywhere, including service lookups, filters, and history tables.
- **Audit trail:** every mutation writes a structured record — actor, action enum, target ID, client IP, ISO UTC timestamp.
- **Response hygiene:** never serialize password hashes, secret keys, internal filesystem paths, or unmasked internal proxy/connection strings — including from health endpoints.
- **Mutating routes:** authenticated and authorized, always; public tunnel exposure requires a Zero Trust / access gate on every mutating route. Probe POST/PUT/DELETE without credentials and expect failure.
- **CORS:** never `allow_origins=["*"]` together with `allow_credentials=True` (Starlette reflects arbitrary origins with credentials). Whitelist trusted production origins.
- **Security headers:** CSP, HSTS, `X-Frame-Options: SAMEORIGIN`, `X-Content-Type-Options: nosniff`, `Permissions-Policy` on static routes AND reverse-proxied API locations.
- **Auth crypto:** verify JWT algorithm (reject `alg:none`), expiry, and secret entropy; compare API keys with `hmac.compare_digest`; no unauthenticated fallback that grants default demo/admin privileges.
- **RBAC:** test role decorators per role (admin/engineer/viewer); viewers must not reach rollbacks, incident resolution, or failure injections.
- **Resource exhaustion:** bound subprocess-spawning endpoints (e.g. `asyncio.Semaphore`) and kill children on client disconnect; bound WebSocket tick rates and clean up on disconnect; retention-bound telemetry/snapshot tables.
- **Log streaming:** tail from end-of-file offset (`max(0, size - 16384)`), never `readlines()` an active log; reset the offset when the file shrinks (rotation) or the stream stalls.
- **Cleanup paths:** contain automated deletions — check `Path(target).resolve().is_relative_to(base_dir.resolve())` before `unlink()`.
- **Embedded DB:** SQLite in WAL mode with busy timeout, single-writer/multi-reader; close connections in `finally:` (`with conn:` covers transactions only).

## STRIDE matrix

| Threat | Checks |
|---|---|
| Spoofing | JWT alg/expiry/entropy; API-key timing safety; anonymous fallback roles |
| Tampering | Parameterized SQL; stored XSS in user-content fields |
| Repudiation | Immutable audit log on every mutation |
| Information disclosure | Path traversal on static routes; hashes/secrets/paths in responses |
| Denial of service | WebSocket/telemetry flood limits; subprocess concurrency; retention bounds |
| Elevation of privilege | RBAC gating per role; viewers cannot mutate |

## Chaos-engineering sandbox isolation

- Failure injections touch only dedicated mock services on loopback ports; zero host contagion — no iptables changes, interface drops, or host filesystem writes.
- Two-step arming before execution; auto-disarm if left unexecuted; auto-abort countdown restores the healthy baseline.

SRE/observability-specific depth (systemd hardening, process lifecycle, SSE pipelines, streaming media) is in `references/sre-portal-hardening.md`.
