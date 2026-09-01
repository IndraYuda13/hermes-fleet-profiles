---
name: sre-mission-control-security
description: Use for security and threat audits of SRE control portals.
version: 1.0.0
author: SENTINEL
license: MIT
metadata:
  hermes:
    tags: [security, threat-model, rbac, xss, sqli, chaos, observability, sre]
    category: reverse-engineering
---

# SRE & Observability Mission Control Security Review

## When to Use
Use when performing security audits, STRIDE threat modeling, injection testing, RBAC verification, or chaos engineering sandbox isolation reviews on Mission Control, SRE observability portals, topology explorers, or automated deployment consoles.

## Automation Dashboard & Multi-Account Fleet Security Matrix
1. **Secret & Session Leakage Prevention:**
   - Verify `.gitignore` rules strictly block credential files (`config.json`, `state/`, `.env`, `bot.log`, session tokens) before any public git commit or push.
   - Enforce audit checks on staged files (`git diff --cached`) during continuous release pipelines.

2. **Upstream Injection & Template Escaping (DOM XSS):**
   - External data retrieved from third-party APIs (e.g. payout IDs, transaction amounts, status labels, wallet strings) must be treated as untrusted input.
   - Enforce `escapeHtml()` sanitization or strict enum mapping (`status_map`) before interpolating into HTML template literals or dynamic table rows (`innerHTML`).

3. **Upstream Rate Limiting & Concurrency DOS Protection:**
   - Multi-account upstream polling must maintain in-memory TTL caching (`CACHE_TTL >= 60s`) and strict per-request timeouts (<= 2.5s).
   - Upstream mutation gates: When upstream reports account state as `UNDER REVIEW` or `IN PROGRESS`, suppress subsequent automated trigger requests with backoff windows (e.g. 6h) to prevent account fraud flagging or upstream throttling.

4. **Action Endpoint Authentication & Authorization:**
   - Dedicated management and mutation endpoints (e.g. manual payouts, wallet configuration, daemon settings) must enforce API key validation (e.g. `X-Dashboard-Key` header verification) to prevent unauthorized execution via public domain exposures.

## Threat Modeling (STRIDE) Matrix
1. **Spoofing (Authentication & Token Security):**
   - Inspect JWT signing algorithm configuration (`HS256`/`RS256`), prevent `alg:none`, verify expiration and secret entropy.
   - Audit fallback authentication logic: verify if unauthenticated anonymous requests receive default demo privileges (e.g. `SRE` or `ADMIN` role) that allow state mutations.
   - Verify `X-API-Key` header timing attack resilience (`hmac.compare_digest`).

2. **Tampering (SQL Injection & Stored DOM XSS):**
   - **SQLite WAL & Embedded DB Parameterization:** Ensure all dynamic query parameters (`?` bind variables) are strictly used across service lookup, endpoint listings, incident filtering, and deployment history.
   - **Stored DOM XSS in Incident Timelines & Copilot Notes:** Audit UI frontend template interpolations (`innerHTML`). Verify user-controlled incident titles, commander names, notes, and copilot diagnostics are HTML-entity escaped before DOM insertion.

3. **Repudiation (Immutable Audit Trail):**
   - Ensure every mutation (deployments, incident state transitions, rollback commands, chaos triggers) writes a structured audit log containing actor username, action enum, target resource ID, client IP, and ISO UTC timestamp.

4. **Information Disclosure (Path Traversal & Data Hygiene):**
   - Test static asset routing (`/static`) against traversal vectors (`../../../../etc/passwd`).
   - Ensure user password hashes (`PBKDF2-SHA256`) and internal secret keys are never serialized in API responses.

5. **Denial of Service (Telemetry & WebSocket Flood):**
   - Verify WebSocket telemetry tick rates (bounded to 1Hz) and verify client disconnect cleanup.
   - Monitor time-series snapshot tables (`telemetry_snapshots`) for bounding/retention policies.

6. **Elevation of Privilege (RBAC Gating):**
   - Test role decorators (`require_role`) against `ADMIN`, `SRE`, `ENGINEER`, and `VIEWER`.
   - Ensure viewers cannot execute rollbacks, resolve incidents, or trigger failure injections.

## Chaos Engineering Sandbox Safety Boundary Protocol
- **Port & Process Isolation:**
  - Verify failure injections are strictly contained to dedicated mock microservice loopback ports (e.g. `8381-8384`).
  - Verify zero host-level contagion: no `iptables` rules, no host interface drops, no host filesystem corruption.
- **Safety Interlocks:**
  - Enforce 2-step physical arming mechanism before failure execution.
  - Implement auto-disarm timer (e.g. 10s timeout disarms armed state if unexecuted).
  - Implement auto-abort countdown timer (e.g. 10s auto-abort recovers healthy baseline automatically).

## Automated Verification Harness
```python
import requests

def run_sre_security_smoke_test(base_url: str):
    # 1. SQL Injection Checks
    for p in ["' OR '1'='1", "admin'--", "1; DROP TABLE services;"]:
        r = requests.get(f"{base_url}/api/v1/services/{p}")
        assert r.status_code in [400, 404]

    # 2. Path Traversal Checks
    for p in ["../../../../etc/passwd", "..%2F..%2F..%2Fetc%2Fpasswd"]:
        r = requests.get(f"{base_url}/static/{p}")
        assert r.status_code == 404

    # 3. Unauthenticated Mutation Check
    r_deploy = requests.post(f"{base_url}/api/v1/deployments", json={"service_id": "svc_test", "version": "v1"})
    print(f"Unauthenticated deploy response status: {r_deploy.status_code}")
```
