# P1 Outage Runbook Engineering: Defect Remediation & Verification Checklist

This reference guide captures concrete failure modes and remediation patterns encountered during production incident runbook reviews (e.g. ApexPay Core Payment API Gauntlet).

---

## 1. Automated Canary Rollback Gating (Istio / Ingress)

When defining progressive traffic rollouts (10% -> 25% -> 50% -> 100%), never rely on passive metric printing. Every stage must incorporate an automated abort-and-rollback trap.

```bash
MAX_ERROR_THRESHOLD="0.10" # 0.10% 5xx error cap

# In each stage:
QUERY_RESULT=$(curl -s -f -G "${PROMETHEUS_URL}/api/v1/query" \
  --data-urlencode 'query=(sum(rate(http_requests_total{job="apexpay-core-api",status=~"5.."}[2m])) / sum(rate(http_requests_total{job="apexpay-core-api"}[2m]))) * 100' || echo "FAILED")

if [ "${QUERY_RESULT}" = "FAILED" ] || [ $(echo "${ERR_RATE} > ${MAX_ERROR_THRESHOLD}" | bc -l) -eq 1 ]; then
  # Rollback immediately to 100% stable
  kubectl patch virtualservice apexpay-core-api-vs -n payments --type merge \
    -p '{"spec":{"http":[{"route":[{"destination":{"host":"apexpay-core-api...","subset":"stable"},"weight":100},{"destination":{"host":"apexpay-core-api...","subset":"canary"},"weight":0}]}]}}'
  exit 1
fi
```

---

## 2. PostgreSQL Blocker Inspection & Blast-Radius Controlled Termination

Indiscriminate killing of queries holding locks can abort critical payment authorizations. Follow a 3-tier sequence:

1. **Precise Inspection**:
   Query `pg_locks` joined with `pg_stat_activity` to find the exact `blocking_pid` holding conflicting locks on `datname = current_database()`.
2. **Graceful Cancellation**:
   Run `pg_cancel_backend(pid)` on identified blocking PIDs exceeding 15s to cancel the query without tearing down the connection.
3. **Gated Hard Termination**:
   Require explicit operator confirmation before executing `pg_terminate_backend(pid)` for stubborn blocking PIDs.
4. **Architectural Write-Workload Isolation**:
   If a background write job (such as settlement reconciliation) causes lock storms, do **NOT** claim to move it to a read replica (replicas cannot accept writes). Instead:
   - Route through a dedicated `pgbouncer-batch` writer partition.
   - Enforce strict `statement_timeout = 15s`.
   - Chunk batch operations into 50-row micro-transactions.

---

## 3. Telemetry Archival Script Resilience & Manifest Logging

When writing post-incident data capture scripts under `set -euo pipefail`:
- Use a `run_probe` helper that records per-command exit status into an `archive_manifest.log` inside the tarball.
- Derive UNIX epoch timestamps dynamically: `date -d "${INCIDENT_START_UTC}" +%s`.
- Distinguish automated infrastructure/database dumps from manual high-volume application heapdumps and logs.
