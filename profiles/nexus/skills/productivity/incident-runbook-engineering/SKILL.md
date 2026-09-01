---
name: incident-runbook-engineering
description: Author and review production incident runbooks and SOPs.
tags: [runbook, sop, incident-response, sse, sre, operations, devops]
---

# Production Incident Runbook & SOP Engineering

Use this skill when authoring, reviewing, or remediating high-severity operational runbooks, emergency mitigation playbooks, disaster recovery procedures, or standard operating procedures (SOPs).

---

## 1. Runbook Architecture Standard

Every production-grade P1/P0 operational runbook must be fully self-contained and structured across the 7-phase incident lifecycle:

1. **Incident Metadata & Governance**: Severity triggers, Incident Command System (ICS) roles (IC, TL, CL, Scribe), strict SLA timetable, and system dependency map.
2. **Triage & Detection Checklist**: Copy-pasteable diagnostic commands, Prometheus/LogQL queries, and scope isolation decision matrix.
3. **Immediate Containment Playbooks**: Rollbacks, traffic shedding / rate limiting, circuit breaking, degraded modes, connection throttling.
4. **Investigation & Root Cause Flowchart**: Golden signals breakdown, ASCII/text triage tree, and diagnostic commands with expected healthy vs abnormal outputs.
5. **Incident Communications Kit**: Status page templates (Investigating, Identified, Monitoring, Resolved), executive flash briefings, and support deflection copy.
6. **Recovery & Validation Protocol**: Controlled traffic ramp-up, live synthetic end-to-end transaction test, and 5-point metric stabilization criteria.
7. **Post-Incident Review (PIR) & Telemetry SOP**: Blameless post-mortem template (5 Whys, Jira action table) and automated telemetry cold-storage dump script.

---

## 2. Critical Execution Pitfalls & Guardrails

When writing or reviewing executable commands in runbooks, always verify against these 5 critical failure modes:

### Pitfall 1: Traffic Ramp-Up Weight Inversion in Canary Loops
* **Bug**: Inverting target and baseline weights during progressive traffic rollout:
  ```bash
  # WRONG: When WEIGHT=10, stable gets 10% and canary gets 90%!
  subset: stable, weight: ${WEIGHT}
  subset: canary, weight: $((100 - WEIGHT))
  ```
* **Correct**:
  ```bash
  # CORRECT: Canary starts at 10% and scales up to 100%
  STABLE_WEIGHT=$((100 - WEIGHT))
  subset: stable, weight: ${STABLE_WEIGHT}
  subset: canary, weight: ${WEIGHT}
  ```

### Pitfall 2: Truncated or Literal Token Placeholders in Code Blocks
* **Bug**: Writing `Bearer ***` or `Bearer ${ACQU...KEN}` which breaks copy-paste execution.
* **Correct**: Use explicit, standard bash environment variables and provide export comments above the command block:
  ```bash
  # Required environment variables:
  # export CLOUDFLARE_ZONE_ID="023e105f4ecef8ad9ca31a8372d0c353"
  # export CLOUDFLARE_API_TOKEN="cf_api_token_..."
  curl -s -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" ...
  ```

### Pitfall 3: Incomplete Scope in Database Backend Termination Queries
* **Bug**: Running `pg_cancel_backend(pid)` or `pg_terminate_backend(pid)` without filtering by database or excluding the investigator's own connection.
* **Correct**:
  ```sql
  SELECT pg_cancel_backend(pid)
  FROM pg_stat_activity
  WHERE state != 'idle'
    AND datname = current_database()
    AND pid != pg_backend_pid()
    AND query NOT LIKE '%pg_stat%'
    AND (now() - query_start) > interval '30 seconds';
  ```

### Pitfall 4: Aborting Telemetry Dumps Under `set -euo pipefail`
* **Bug**: When capturing post-incident diagnostics in a bash script with `set -euo pipefail`, a non-zero exit from an optional probe (e.g. `psql SHOW STATS` failing if PgBouncer is restarting) will abort the entire script before compressing or uploading the S3 tarball.
* **Correct**: Append `|| true` to all exploratory diagnostic dumps:
  ```bash
  kubectl describe nodes > "${ARCHIVE_DIR}/k8s_nodes_describe.txt" || true
  psql -h pgbouncer.internal -c "SHOW STATS;" > "${ARCHIVE_DIR}/pgbouncer_stats.txt" || true
  ```

### Pitfall 5: Unscoped PromQL Aggregate Queries
* **Bug**: Using bare `sum(rate(http_requests_total[5m]))` which sums across all cluster jobs (including metrics scrapers or background workers).
* **Correct**: Always qualify target jobs explicitly on both numerator and denominator:
  ```promql
  sum(rate(http_requests_total{job="apexpay-core-api",status=~"5.."}[5m]))
  /
  sum(rate(http_requests_total{job="apexpay-core-api"}[5m])) * 100
  ```

### Pitfall 6: Long-Running Daemons with Unbounded Log Files & Missing Logrotate
* **Bug**: Configuring systemd services with `StandardOutput=append:/path/to/bot.log` or Python `FileHandler` without maxBytes/backupCount and lacking system logrotate. Over days of multi-threaded execution, disk runs out of space (`ENOSPC`) causing daemon failure and I/O degradation.
* **Correct**:
  - Always enforce `/etc/logrotate.d/<service>` with `copytruncate`, size threshold (e.g. `50M`), daily rotation, compression, and retention caps.
  - Pair systemd unit definitions with pre-flight readiness checks (`ExecStartPre`) for downstream dependency health (proxy pools, microservices, local solvers).

### Pitfall 7: Non-Atomic State Persistence in Multi-Threaded Daemon Tasks
* **Bug**: Writing runtime JSON states or configuration updates directly via `open("state.json", "w").write(...)`. If process crashes or threads collide mid-write, the file is corrupted into empty or invalid JSON.
* **Correct**: Use atomic file replacement (`tmp_file.write_text()` followed by `os.replace(tmp_file, target_file)`), ensuring state files remain consistently valid.

### Pitfall 8: Stale Frontend Template Caching Behind Reverse Proxies / CDN
* **Bug**: Web UI servers serving dynamic single-file templates (e.g. `dashboard_template.html`) or API stats without `Cache-Control` headers. Reverse proxies (Cloudflare Tunnel, Nginx) or browser disk cache aggressively cache outdated HTML and JSON, causing UI fixes and new feature deployments to remain invisible to end-users even after service restarts.
* **Correct**:
  - Always inject strict no-cache response headers in HTTP handlers:
    ```python
    self.send_header("Cache-Control", "no-cache, no-store, must-revalidate, max-age=0")
    self.send_header("Pragma", "no-cache")
    self.send_header("Expires", "0")
    ```
  - Read HTML templates dynamically from disk on each request (or check `mtime`) rather than relying purely on in-memory constants, and document hard refresh shortcuts (`Ctrl+F5` / `Cmd+Shift+R`) in the operational release runbook.

---

## 3. Verification Checklist for Runbook Certification

Before certifying an operational runbook:
- [ ] Every command block is copy-paste executable with explicit environment variable headers.
- [ ] Rollback and traffic shifting scripts have been mathematically verified for directionality.
- [ ] Database mitigation scripts contain safeguards against terminating administrative sessions.
- [ ] Definition of Done / Resolution criteria defines explicit sustained observation windows (minimum 15 mins).
- [ ] Communications kit contains separate, specialized wording for public status pages, executive flash briefings, and customer support deflection.
