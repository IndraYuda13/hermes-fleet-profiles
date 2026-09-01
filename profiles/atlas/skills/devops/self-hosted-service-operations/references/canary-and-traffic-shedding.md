# Production Canary Gates, Fail-Closed SRE Invariants & Edge Shedding Patterns

## 1. Fail-Closed Canary Progression & Zero-Mutation Preflight Gate

When implementing automated traffic shifts or canary ramp-up scripts (e.g. Istio VirtualService or ingress controllers):

### Preflight Zero-Mutation Invariant
Before modifying any routing configuration:
1. Verify required CLI binaries (`curl`, `jq`, `bc`, `kubectl`).
2. Assert cluster context, namespace presence, and manifest schema validity.
3. Assert exact route and subset counts: verify that the target host exists in exactly one HTTP route rule, with exactly one `stable` subset destination and exactly one `canary` subset destination. If duplicate destinations, missing subsets, or ambiguous route rules exist, abort immediately with exit 1 before applying any changes.
4. Establish an immutable whole-object JSON backup (`VS_BACKUP`) and test dry-run apply capability (`kubectl apply --dry-run=client -f ${VS_BACKUP}`).
5. Check telemetry endpoint reachability (`curl -s -f -m 5 "${PROMETHEUS_URL}/api/v1/query?query=up"`).

### Non-Reentrant Shell Traps & Guaranteed Rollback
- Arm an active execution trap (`trap 'handle_unexpected_failure' ERR EXIT`) guarded by state variables:
  - `MUTATION_STARTED=false` (preflight errors exit 0/1 without firing rollback)
  - `ROLLBACK_IN_PROGRESS=false` (prevents recursive re-entry if rollback fails)
  - `RAMP_COMPLETED=false` (disarmed on clean completion)
- Execute rollback via whole-object restore (`kubectl apply -f ${VS_BACKUP}`).
- **Live State Verification**: Always query live cluster state post-rollback (`kubectl get ... -o json`) and assert `stable_weight == 100` and `canary_weight == 0`. If the live cluster state does not match, log a critical failure alert and exit non-zero.

### Fail-Closed Telemetry Validation
At each ramp stage, validate Prometheus telemetry across all failure modes:
1. HTTP exit code (catch network timeouts / DNS drops).
2. JSON syntax validity (`jq empty`).
3. Prometheus status (`.status == "success"`).
4. Vector result length (`.data.result | length >= 1`) — **never coerce empty vectors to zero errors**. Scrape failures and unpopulated metrics are unknown states requiring immediate rollback.
5. Float format validation (`^[0-9]+(\.[0-9]+)?$`).
6. Threshold evaluation via `bc -l` (avoids bash integer truncation).

---

## 2. Cloudflare Scoped Rulesets API (Single-Rule Lifecycle)

To avoid breaking B2B API integrations or wiping pre-existing production WAF rules:

### API Invariant: Never Use Global "Under Attack Mode" for APIs
JavaScript challenges break non-browser B2B SDKs and automated webhooks. Use the Cloudflare Rulesets API to enforce IP-based rate limiting strictly on core API routes.

### Cloudflare Ruleset v4 Invariants
- **Phase Entrypoint**: Target `PUT/POST /client/v4/zones/${ZONE_ID}/rulesets/phases/http_ratelimit/entrypoint`.
- **Colocation Characteristics**: Rate limiting rules on Cloudflare v4 Rulesets require `"characteristics": ["cf.colo.id", "ip.src"]` in the `ratelimit` block.
- **Single-Rule Atomic Lifecycle**:
  - `GET /entrypoint` to resolve `RULESET_ID` and snapshot pre-emergency rules array.
  - `POST /rulesets/${RULESET_ID}/rules` to append only the emergency rule.
  - Resolve created rule ID directly from response (`(.result.rules[-1].id // .result.id)`), avoiding fragile description matching.
  - `DELETE /rulesets/${RULESET_ID}/rules/${EMERGENCY_RULE_ID}` on recovery.
  - Verify post-rollback rules against pre-emergency snapshot using normalized JSON diff (`del(..|.last_updated?, .version?)`) to guarantee zero drift on pre-existing production rules.

### Wirefilter Path Scoping
Use exact matches and subpath prefixes to prevent over-matching unrelated routes:
```
(http.host eq "api.apexpay.global" and (http.request.uri.path eq "/v1/payments" or starts_with(http.request.uri.path, "/v1/payments/") or http.request.uri.path eq "/v1/charges" or starts_with(http.request.uri.path, "/v1/charges/")))
```

---

## 3. PostgreSQL Authoritative Blocker Identification (`pg_blocking_pids`)

When resolving connection pool saturation and lock contention:
- Do not rely on loose duration-only queries that risk canceling innocent queries or self-killing DBA sessions.
- Use `pg_blocking_pids(blocked.pid)` to unnest the exact conflict graph.
- Scope queries strictly to `cardinality(pg_blocking_pids(pid)) > 0`, `state != 'idle'`, `datname = current_database()`, and `pid != pg_backend_pid()`.
- Execute a two-phase mitigation: graceful `pg_cancel_backend(pid)` (15s query duration) followed by hard `pg_terminate_backend(pid)` (30s duration) only after operator review.
