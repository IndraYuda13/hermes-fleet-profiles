---
name: n8n-workflow-automation
description: Use when building, testing, or publishing n8n workflows.
---

# n8n Workflow Automation via n8n-mcp

Use this skill when designing, building, testing, or publishing n8n workflows programmatically using `n8n-mcp` tools and `@n8n/workflow-sdk`.

## Workflow Lifecycle & Tool Sequence

1. **Planning & SDK Reference**
   - Call `mcp__n8n_mcp__get_workflow_best_practices(technique=...)` to load pattern guidance.
   - Call `mcp__n8n_mcp__get_sdk_reference(section='all')` if syntax for specific node types, expressions, or credentials is needed.

2. **Validation & Creation**
   - Write workflow code importing `{ workflow, node, trigger, expr, newCredential }` from `@n8n/workflow-sdk`.
   - Validate code with `mcp__n8n_mcp__validate_workflow(code=...)`.
   - Create workflow with `mcp__n8n_mcp__create_workflow_from_code(code=..., name=..., description=...)`.

3. **Testing & Execution Inspection**
   - Test manual or trigger execution with `mcp__n8n_mcp__execute_workflow(workflowId=..., executionMode='manual')`.
   - Inspect output and node-by-node execution data using `mcp__n8n_mcp__get_execution(executionId=..., workflowId=..., includeData=true)`.

4. **Publishing & Maintenance**
   - Publish (activate) workflows using `mcp__n8n_mcp__publish_workflow(workflowId=...)`.
   - Clean up deprecated or trial draft workflows using `mcp__n8n_mcp__archive_workflow(workflowId=...)`.

---

## Critical Pitfalls & Execution Rules

### 1. Sub-workflow Dependency & Publishing Order
- **Rule:** If Parent Workflow A calls Child Workflow B via an `executeWorkflow` node, **Child Workflow B MUST be created and published FIRST**.
- **Pitfall:** Attempting to publish Workflow A before Workflow B is published results in error:
  `Cannot publish workflow: Node "X" references workflow Y which is not published. Please publish all referenced sub-workflows first.`

### 2. Sub-workflow Trigger Nodes
- **Rule:** Sub-workflows intended for invocation via `executeWorkflow` must use `n8n-nodes-base.executeWorkflowTrigger` as their trigger node.
- **Pitfall:** Creating sub-workflows without a trigger node causes publish failure: `Workflow cannot be activated because it has no trigger node.`

### 3. Sub-workflow ID References in SDK Code
- **Rule:** When configuring `n8n-nodes-base.executeWorkflow` in `@n8n/workflow-sdk`, pass `workflowId` as an n8n Resource Locator (`__rl`) object or n8n expression string.
- **Correct Format:**
  ```javascript
  workflowId: {
    __rl: true,
    value: 'TARGET_WORKFLOW_ID',
    mode: 'list',
    cachedResultName: 'Target Workflow Name'
  }
  ```
- **Pitfall:** Passing a bare string ID like `workflowId: 'XYZ'` will fail validation or throw runtime error: `No information about the workflow to execute found. Please provide either the "id" or "code"!`

### 4. Credentials & Activation
- **Rule:** Workflows containing nodes with unconfigured required credentials (e.g. `n8n-nodes-base.postgres` without an assigned credential ID) will fail `publish_workflow`.
- **Workaround:** For standalone or testing environments without UI-configured credentials, route external calls via `n8n-nodes-base.httpRequest` to local API endpoints or bridge HTTP services.

### 5. String Template & Expression Escaping
- Avoid raw `{{ }}` in parameter strings unless intended as n8n runtime expressions. Use `expr(...)` from `@n8n/workflow-sdk` when dynamic values from prior nodes are needed.

### 6. Sub-workflow Payload Data Passing
- **Rule:** When calling a sub-workflow via `n8n-nodes-base.executeWorkflow` in mode `each`, the item input payload must explicitly forward any parent data objects (e.g. `snapshot: $json`) in the item generation step (`n8n-nodes-base.code`).
- **Pitfall:** Generating item lists with only key/category metadata without passing the parent snapshot object will result in child sub-workflows receiving empty or undefined inputs instead of live real-time data.

### 7. Local HTTP & Container Networking in n8n
- **Rule:** When n8n runs inside a Docker container, `127.0.0.1` inside the node parameters points to the n8n container itself. To reach local host daemons (e.g. 9Router on port 20128 or local APIs on port 8130), route via the Docker host bridge IP (e.g. `http://172.20.0.1:<port>`) or public domain URLs.

### 8. Fan-Out Sub-workflow Execution Modes (`mode: 'once'` vs `mode: 'each'`)
- **Rule:** Use `mode: 'each'` when dispatching independent per-item tasks (e.g. 20 parallel agent workers). Use `mode: 'once'` when triggering downstream singleton workflows (e.g. Aggregation Coordinator, Notification Gate, or Telegram Sender).
- **Pitfall:** Using `mode: 'each'` on downstream singleton or notification sub-workflows after processing an array of items will trigger N separate executions of the coordinator/notifier, leading to duplicate execution loops and notification spam.

### 9. Dynamic Input Mapping vs Hardcoded Fallbacks
- **Rule:** When passing dynamic payload data into sub-workflow nodes (e.g. LLM prompts or Telegram notification text), ensure prior nodes explicitly forward the required properties.
- **Pitfall:** Relying on default string fallbacks (`$json.score || 88.5`) when input paths are misaligned or undefined will mask data-passing bugs, causing identical static messages or responses to be produced repeatedly on every run.

### 10. Postgres Node `typeVersion` Compatibility
- **Rule:** When configuring `n8n-nodes-base.postgres` nodes programmatically, check runtime supported `typeVersion`.
- **Pitfall:** Setting `typeVersion: 2.7` on n8n releases where 2.7 execute method is unmapped causes `TypeError: Cannot read properties of undefined (reading 'execute')`. Use `typeVersion: 2.6` for stable compatibility across n8n 1.x/2.x releases.

### 11. Credential ID Binding in Workflow JSON & Shared Credentials
- **Rule:** When binding credentials to workflow nodes programmatically or in database imports, include both `id` and `name` in the node's `credentials` object.
- **Example:** `credentials: { postgres: { id: 'maiPostgresCred01', name: 'MAI PostgreSQL' } }`.
- **Pitfall:** Omitting `id` leads to `Found credential with no ID.` or `SASL: SCRAM-SERVER-FIRST-MESSAGE: client password must be a string` runtime errors during node execution.
- **Database Entry:** When inserting credentials directly into PostgreSQL (`credentials_entity`), also insert corresponding project ownership records into `public.shared_credentials` (`credentialsId`, `projectId`, `role='credential:owner'`) so n8n runtime tasks can resolve them.

### 12. Local AI Gateway (9Router) Process Safety
- **Rule:** Never kill or terminate local 9router daemon processes (`port 20128`).
- **Pitfall:** Using `fuser -k 20128/tcp` disrupts local model routing for all connected agents and n8n workflows. Modify settings via SQLite/API directly without process termination.

### 13. Activation of Manual-Only / Triggerless Workflows
- **Rule:** Do NOT attempt to activate (`active: true` or `publish_workflow`) workflows that contain only `n8n-nodes-base.manualTrigger` or no trigger nodes.
- **Pitfall:** Activating manual-trigger-only workflows causes n8n startup/activation error: `Workflow "X" has no node to start the workflow - at least one active trigger, poll trigger, webhook trigger, or schedule trigger node is required`. Keep `active: false` for utility/bootstrap/test workflows executed on demand.

### 14. Non-Streaming JSON Output from OpenAI-compatible LLM Endpoints
- **Rule:** When calling OpenAI-compatible chat completion endpoints (e.g. 9Router, local vLLM, Ollama) via `n8n-nodes-base.httpRequest` or HTTP scripts to parse JSON outputs, explicitly pass `"stream": false` in the JSON request body.
- **Pitfall:** Defaulting to streaming (`"stream": true` or SSE chunk responses `data: {...}`) returns chunked event streams instead of a single completion object, causing JSON parsers in downstream nodes to fail.

### 15. Closed Candle Slicing for Technical Indicators
- **Rule:** When computing technical indicators (EMA, RSI, Volatility) from live exchange kline/candlestick data (e.g. Binance API), drop the last incomplete open bar (`klines[:-1]`).
- **Pitfall:** Including the unclosed open candle causes indicator values to fluctuate unpredictably mid-interval, leading to false signal triggers.

### 16. Deterministic Consensus Ceiling & Audit Trail
- **Rule:** In multi-agent AI systems, effective consensus score must be bounded by `min(AI consensus, deterministic consensus)`.
- **Audit Requirement:** Always persist notification decision rows with status `QUEUED` in database audit tables **prior** to attempting external delivery (Telegram/Webhook). Update to `SENT` with external message ID upon success, or `SEND_UNKNOWN` if delivery state is ambiguous.

### 17. Side-Effect Delivery & Disabling Blind Retries
- **Rule:** Disable `retryOnFail` on Telegram, Webhook, and other side-effect delivery nodes (`retryOnFail: false` or omit).
- **Pitfall:** Enabling `retryOnFail` on notification nodes causes duplicate messages when delivery timeouts occur, as retries execute within the same already-claimed node execution. Hand off delivery ambiguities to an audit log (`QUEUED` -> `SEND_UNKNOWN`) for manual or watchdog review.

### 18. n8n Error Workflow Assignment (`settings.errorWorkflow`)
- **Rule:** To attach a centralized Error Handler workflow to a Master workflow in n8n, assign the Error Handler's workflow ID to `settings.errorWorkflow` in the Master workflow's configuration.
- **Example:** `settings: { errorWorkflow: 'WORKFLOW_ID_OF_ERROR_HANDLER' }`.
- **Pitfall:** Merely creating an `n8n-nodes-base.errorTrigger` workflow does not automatically capture errors from other workflows until those workflows explicitly reference its ID in `settings.errorWorkflow`.

### 19. SHA-256 Cryptographic Snapshot Fingerprinting
- **Rule:** For immutable snapshot verification and deduplication, format `snapshot_hash` as `sha256-<64_hex_chars>` (71 characters total).
- **Pitfall:** Using non-cryptographic or 32-bit hashes (such as FNV-1a) increases collision risk across continuous 30-minute analysis intervals.

### 20. Database Credential Role Segregation (Admin vs Least-Privilege Runtime)
- **Rule:** Maintain two distinct database credentials in n8n: an Admin Bootstrap credential (`postgres` superuser) for schema migrations and DDL scripts, and a Least-Privilege Runtime credential (`mai_app` or app role) restricted to DML operations (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) on target schemas.
- **Pitfall:** Binding runtime execution nodes to superuser credentials introduces unnecessary database security exposure.

### 21. Coherent Checksum Manifests & Deployed Workflow Exports
- **Rule:** When generating `MANIFEST.sha256` for exported n8n workflow archives, ensure relative paths in the manifest match the export directory layout (e.g. `workflows_exported/<filename>.json`).
- **Verification:** Test checksum validation directly with `cd artifacts && sha256sum -c MANIFEST.sha256` to guarantee all exports verify cleanly as `OK`.
- **Evidence Separation:** Distinguish unit/invariant regression suites (deterministic logical checks) from integration execution fixtures (full DB state transitions & side-effect verification).

### 22. `n8n import:workflow` Top-Level `id` Requirement
- **Rule:** Workflow JSON files must contain a top-level `"id"` field before being passed to `n8n import:workflow`.
- **Pitfall:** Importing workflow JSON files missing the `"id"` key causes PostgreSQL constraint failure: `null value in column "id" of relation "workflow_entity" violates not-null constraint`.

### 23. CLI `n8n execute` vs Running Instance Port Conflict
- **Rule:** Do not run `n8n execute --id=<id>` CLI commands inside a container where the main n8n server process is active.
- **Pitfall:** `n8n execute` attempts to bind to the task broker port and fails with `n8n Task Broker's port 5679 is already in use`. Execute workflows via scheduled/manual triggers, webhooks, or database seed jobs when the n8n daemon is active.
- **Workaround for manual execution:** Log in via n8n REST API (`POST /rest/login` with `{"emailOrLdapLoginId":"<email>","password":"<pw>"}`), save cookies, navigate to the workflow editor in browser, and click the "Execute workflow" button on the trigger node. Alternatively, use `browser_console` to invoke `document.querySelectorAll('button').forEach(b => { if (b.textContent.trim() === 'Execute workflow') b.click(); })` after navigating to the workflow page.
- **Direct DB JSON Updating & In-Memory Cache Invalidation:** When updating `nodes` or `connections` directly in PostgreSQL (`workflow_entity`), n8n's in-memory workflow cache does not reload until the container is restarted (`docker restart n8n`) or activation is toggled via REST API (`PATCH /rest/workflows/<id>`).
- **Auth note:** The n8n user email may differ from the user's primary email. Check `SELECT email FROM "user"` in the n8n database if login fails.
- **REST API activation:** To reactivate workflows via API (not just DB), use `PATCH /rest/workflows/<id>` with body `{"active":true}` and session cookies. This properly registers triggers with n8n's internal scheduler. DB-only `UPDATE active=true` may not register the trigger until restart.

### 41. `n8n import:workflow` Deactivates Active Workflows
- **Rule:** `n8n import:workflow` automatically deactivates any workflow that was previously `active=true` in the database. After import, you MUST reactivate via direct DB update.
- **Reactivation command:** `docker exec <postgres_container> psql -U postgres -d n8n -c "UPDATE workflow_entity SET active = true WHERE id IN ('...');"`
- **Pitfall:** Forgetting to reactivate after import silently stops scheduled/triggered production workflows. Always verify activation state after import with `SELECT id, name, active FROM workflow_entity WHERE id IN ('...');`.

### 42. Model-Route Migration with Science Epoch Versioning
- **Rule:** When changing the LLM model alias (e.g. `ag-opus-pool` → `n8n`) in active MAI workflows, this is a data-generating configuration change. Do NOT rewrite historical records.
- **Procedure:**
  1. **Verify-first:** Inspect all active workflow JSON for old model references before changing anything.
  2. **Patch model fields only:** Change `model_specialist`, `model_aggregator`, `model_verifier`, and any `model:` in request body construction nodes. Do not change prompts, temperatures, schemas, thresholds, or weights.
  3. **Bump config_version:** Set a new epoch version (e.g. `mai-config-v2.2.0-n8n-r1`) so pre-switch and post-switch science samples can be distinguished.
  4. **Record switch timestamp UTC** in the migration report.
  5. **Verify zero old-alias references** across all active workflows after deployment.
  6. **LLM connectivity test:** Send a minimal request through the new model alias to confirm 9Router resolves it correctly.
- **Pitfall:** 9Router may return SSE streaming responses (`content-type: text/event-stream`) even for non-streaming requests. Use `"stream": false` in request body for JSON parsing compatibility.

### 34. Inspecting / Exporting Deployed Workflows via Docker CLI
- **Rule:** To list or export all workflows directly from a running Docker n8n container without stopping the service or requiring API tokens, use:
  `docker exec <container_name> n8n export:workflow --all --output=/tmp/workflows.json`
- **Utility:** Allows quick extraction and status inspection (`id`, `name`, `active`) across all workflows when `n8n-mcp` or direct DB access is unavailable.

### 24. Point-in-Time Leakage Prevention in Evaluation & Shadow SQL
- **Rule:** In shadow/science evaluation workflows joining time-stamped market analysis runs (`c.as_of`), domain observations must strictly enforce point-in-time boundaries: `d.window_start <= c.as_of AND d.observed_at <= c.as_of`.
- **Pitfall:** Using lookahead allowances such as `d.window_start <= c.as_of + INTERVAL '30 minutes'` causes evaluation runs at timestamp T to consume domain data collected after T, contaminating science layer validity with future information.

### 25. Workflow Activation Matrix Verification
- **Rule:** `n8n export:workflow` preserves the workflow's `active` state at export time. Newly imported scheduled workflows default to `active: false` unless explicitly activated.
- **Pitfall:** Leaving deployed scheduled science/evaluator workflows with `active: false` prevents automatic sample accumulation despite manual execution tests passing. Always update activation states in n8n per the project's activation matrix after integration tests pass.

### 35. Publishing and Activating Workflows on Current Docker n8n
- **Rule:** On current n8n 2.x Docker deployments, use `n8n publish:workflow --id=<workflow_id>` to publish the current version. The command can succeed while warning that changes will not take effect while the n8n server is running.
- **Procedure:** Inspect with `docker exec <container> n8n list:workflow --active=true` and `--active=false`. Publish referenced error handlers or child workflows first. Batch-publish the requested workflow IDs. Restart the n8n container once. Wait for `/healthz`, then verify the scheduler and exported workflow state.
- **Verification commands:**
  ```bash
  docker exec <container> n8n publish:workflow --id=<workflow_id>
  docker restart <container>
  curl -fsS http://127.0.0.1:5678/healthz
  docker exec <container> n8n list:workflow --active=true
  docker exec <container> n8n export:workflow --all --output=/tmp/workflows.json
  docker cp <container>:/tmp/workflows.json /tmp/workflows.json
  ```
  Inspect each target's top-level `active` and `activeVersionId` in the exported JSON. The export path is inside the container, not the host.
- **Pitfalls:** Do not treat `Publishing workflow...` as proof of runtime activation before restart and verification. Do not activate manual-only or triggerless utility workflows just to remove unrelated startup errors. Separate target activation results from pre-existing triggerless workflow errors in logs.

### 26. Overlapping Sample Protection & Wilson 95% Confidence Intervals
- **Rule:** When evaluation horizons (e.g. 1h/4h/12h/24h) overlap higher-frequency run schedules (e.g. every 30 mins), raw row count ($N_{raw}$) overstates statistical independence.
- **Pitfall of Naive `LAG` Slicing:** `LAG(as_of) OVER (...)` checking `as_of >= prev_as_of + horizon` fails on high-frequency runs (each row compares to 30m prior, failing forever).
- **Implementation:** Group outcomes into deterministic epoch cohorts `FLOOR(EXTRACT(EPOCH FROM as_of)/(horizon_minutes*60))` in SQL to select true non-overlapping samples (`effective_n`).
- **Uncertainty Bounds:** Compute Wilson 95% score interval using `effective_n` (not `raw_n`), and derive maturity labels (`EXPERIMENTAL`, `EARLY_EVIDENCE`, `REVIEWABLE`) explicitly from `effective_n`.

### 27. Read-Only Analytics Layer & Promotion Safety
- **Rule:** Science and analytics workflows (e.g. Scorecards, Champion vs Challenger evaluation) must be strictly READ-ONLY with respect to production champion configuration and agent weights.
- **Safety Invariant:** Never automatically update production agent registry weights (`mai.agent_registry.weight`) or production notification thresholds from analytics/evaluation workflows. Restrict outputs to research recommendations (`KEEP_CHAMPION`, `REVIEW_CHALLENGER`, `INSUFFICIENT_DATA`, `RESEARCH_ONLY`).

### 28. PostgreSQL View Syntax & Function Portability
- **Rule:** In PostgreSQL analytical views, use `SIGN(...)` for number signs (not JavaScript's `Math.sign`).
- **Privilege Grants:** Use `GRANT SELECT ON ALL TABLES IN SCHEMA mai TO mai_app;` which applies to both tables and views. Avoid invalid `GRANT SELECT ON ALL VIEWS` statements.

### 29. PIT-Safe Market Regime Analytics
- **Rule:** Never define market regimes (bull, bear, range, volatility) using future outcome returns (`return_pct` or post-decision price action).
- **Pitfall:** Using future realized returns to categorize historic predictions introduces severe target leakage, invalidating regime-specific model evaluation. Derive regimes strictly from pre-decision snapshot indicators at or before `as_of`.

### 30. Recursive CTE Greedy Selection for True Non-Overlapping Outcomes
- **Rule:** Fixed epoch bucketing (`FLOOR(EXTRACT(EPOCH FROM as_of)/...)`) can select runs 30 minutes apart across bucket boundaries when run cadence is high.
- **Implementation:** Use a PostgreSQL recursive CTE with `CROSS JOIN LATERAL` to enforce true greedy non-overlapping sample selection.
- **Seed exactness (V3.2.3):** Seed must use `DISTINCT ON (scope_type, symbol, horizon_label)` with deterministic tiebreaker `(as_of ASC, run_id ASC)`. Using `WHERE run_id IN (...)` to filter the outer query can pull extra horizon rows from multi-horizon runs, creating duplicate branches.
- **Matched-specific greedy:** When comparing Champion vs Challenger, run a separate greedy non-overlap selector over the matched population itself. Do NOT intersect matched rows with the global canonical sample, as this produces `effective_matched_n=0` even when valid matched rows exist.
- **Agent availability denominator:** `entity_effective_n / canonical_effective_n` (not `effective_n / raw_n`).
- **Agent-level maturity:** `maturity_label` must use `entity_effective_n` (per-agent count), not `canonical_effective_n` (per-horizon count). An agent with 2 samples on a horizon with 200 canonical samples is EXPERIMENTAL, not REVIEWABLE. Optionally expose `horizon_maturity_label` from `canonical_effective_n`.

### 37. Deterministic Threshold Consistency Across Views
- **Rule:** When multiple views (aggregator evaluation, ablation proxy) classify a directional mean into BULLISH/BEARISH/NEUTRAL, use the **same** threshold everywhere: `mean > +0.10 → BULLISH`, `mean < -0.10 → BEARISH`, otherwise `NEUTRAL`.
- **Pitfall:** Using `> 0` in one view and `> 0.10` in another creates impossible-to-reconcile disagreements between aggregator improvement counts and ablation hit rates. The neutral zone must be reachable for small values like ±0.05.

### 38. Aggregator Evaluation Semantics (Improved/Harmed)
- **Rule:** `aggregator_improved` must mean the Aggregator is correct AND the deterministic baseline is incorrect. `aggregator_harmed` must mean the Aggregator is incorrect AND the deterministic baseline is correct. Expose all four quadrants: `both_correct`, `aggregator_improved`, `aggregator_harmed`, `both_wrong`.
- **Pitfall:** Labeling every `aggregator_hit` as `aggregator_improved` inflates the Aggregator's perceived value and masks cases where both methods agree.

### 39. Ablation Delta Orientation
- **Rule:** `incremental_hit_rate_delta = full_ensemble_hit_rate - loo_hit_rate`. `incremental_signed_return_delta = full_avg_signed_return - loo_avg_signed_return`. Positive consistently means the included agent helped.
- **Pitfall:** Computing `loo - full` inverts the sign convention, making beneficial agents appear harmful.

### 43. N8N_RUNNERS_TASK_TIMEOUT and Heavy Code Nodes
- **Rule:** n8n 2.x with `N8N_RUNNERS_ENABLED=true` enforces a default 300-second timeout on each Code node execution via the task broker. Heavy computation nodes (e.g. multi-timeframe kline processing with EMA/RSI/stdev calculations) can exceed this.
- **Symptom:** `Task execution timed out after 300 seconds` error on a Code node, workflow marked as `error`, error handler fires. All subsequent scheduled runs fail identically.
- **Fix:** Set `N8N_RUNNERS_TASK_TIMEOUT=600` (or higher) in the n8n container environment. This is infrastructure config, not workflow logic.
- **Diagnosis:** Check `mai.workflow_errors` for repeated failures on the same node name with the timeout message. The `execution_entity` shows ~1200s total runtime (300s timeout + n8n overhead + retry delays).
- **Pitfall:** This issue is invisible until a Code node's data source (e.g. Binance API) returns slowly or the computation grows. It blocks ALL pipeline stages downstream (LLM calls, aggregation, notification).

### 44. Docker Container Env Var Changes Require Recreation
- **Rule:** Docker does not support modifying environment variables on a running container. To add/change an env var (e.g. `N8N_RUNNERS_TASK_TIMEOUT`), you must stop, remove, and recreate the container with the full original config plus the new var.
- **Procedure:**
  1. Capture current config: `docker inspect n8n --format='{{range .Config.Env}}{{println .}}{{end}}'` for env vars; also capture network, volume, port, and restart policy.
  2. `docker stop n8n && docker rm n8n`
  3. `docker run -d --name n8n --restart always --network <net> -p 5678:5678 -v n8n_data:/home/node/.n8n -e <ALL_ORIGINAL_ENVS> -e <NEW_ENV> <image>`
- **Pitfall:** Forgetting to include all original env vars in the new `docker run` command silently drops them, breaking DB connectivity, timezone, or other features.

### 45. Workflow Trigger Re-registration After Container Restart
- **Rule:** After recreating the n8n container or restarting it, workflows with `active=true` in the DB may NOT have their schedule triggers registered with n8n's internal scheduler. The scheduler state is in-memory and not persisted across restarts in all cases.
- **Fix:** Toggle activation via the REST API to force trigger re-registration:
  ```
  PATCH /rest/workflows/<id> {"active":false}
  PATCH /rest/workflows/<id> {"active":true}
  ```
  Use session cookies from `POST /rest/login`.
- **Diagnosis:** Workflow shows `active=true` in DB but no new `execution_entity` rows appear at the expected schedule times. Check `docker exec n8n env | grep RUNNER` to confirm the process is running.
- **Pitfall:** Simply setting `active=true` via direct DB `UPDATE` does not register triggers with the running n8n process. The API PATCH method is required.

### 46. Diagnosing Unfired Scheduled Triggers (`scheduled_job` Table vs In-Memory Scheduler)
- **Rule:** In standard single-instance n8n Docker setups, `scheduled_job` and `scheduled_task` database tables remain empty because n8n manages `scheduleTrigger` nodes using an in-memory event loop / timer wheel.
- **Diagnosis:** Do NOT rely on `SELECT * FROM scheduled_job` to verify scheduled triggers. Instead, query `execution_entity`:
  ```sql
  SELECT id, status, mode, "startedAt", "stoppedAt"
  FROM execution_entity
  WHERE "workflowId" = '<workflow_id>' AND mode = 'trigger'
  ORDER BY id DESC LIMIT 5;
  ```
- **Pitfall:** Assuming a trigger is active because `workflow_entity.active = true` will hide the fact that the in-memory timer wheel did not schedule the execution after container restart or direct DB updates. Always confirm active firing via `execution_entity`.

### 47. `scheduleTrigger` `minutesInterval` Upper Bound (<=59) & Cascading Startup Stalling
- **Rule:** In `n8n-nodes-base.scheduleTrigger` nodes, the `minutesInterval` parameter must NOT exceed 59. For intervals of 1 hour or more, use `field: "hours"` with `hoursInterval` (or `field: "days"` / cron expressions).
- **Symptom:** `WorkflowActivationError: There was a problem activating the workflow: "Invalid interval"` or triggerless workflow errors in n8n container logs.
- **Cascading Pitfall:** When any workflow marked `active=true` in PostgreSQL fails activation due to invalid interval parameters or missing trigger nodes, n8n's `ActiveWorkflowManager` enters an exponential backoff retry loop (2s, 4s, 8s, ... up to 4096s+). This retry loop can stall or delay the in-memory timer wheel registration for ALL other valid active workflows in the instance, silently preventing scheduled executions.
- **Remediation:** Unpublish/deactivate failing utility/broken workflows via `docker exec -i n8n n8n unpublish:workflow --id=<broken_id>` (do not use deprecated `update:workflow`) and restart n8n (`docker restart n8n`) so the startup activation queue completes cleanly without background retry stalls.

### 48. IPC TaskBroker Socket Stall on Long Sequential Pipelines
- **Rule:** When an n8n workflow executes long sequential HTTP fetches (e.g., 9+ HTTP request nodes taking 15+ minutes in total), the IPC/WebSocket connection between n8n main process and internal JS Task Runner (`port 5679`) can stall or lose task assignment context.
- **Symptom:** Subsequent `n8n-nodes-base.code` nodes time out after 600 seconds with `Task execution timed out after 600 seconds` error (`TaskBroker.handleTaskTimeout`), even if the JS code itself runs in 10-20ms in an isolated Node.js environment.
- **Diagnosis:** Inspect step-by-step timings in `execution_data` using PostgreSQL. Measure total upstream HTTP duration vs Code node duration. Perform an isolated `node` CLI benchmark on the exact Code node payload to rule out algorithm/loop stalls.
- **Mitigation:** Optimize upstream HTTP fetching concurrency or break single monolithic workflows into smaller sub-workflows when HTTP fetching takes >10 minutes.

### 50. HTTP Request Node Payload Inflation & Multiplier Pitfall (`executeOnce: true`)
- **Rule:** When an upstream node outputs an array of $N$ items (e.g. 192 candles from a kline fetch), downstream HTTP request nodes default to executing once per item unless `executeOnce: true` is set.
- **Pitfall:** Chaining 9 sequential HTTP request nodes without `executeOnce: true` causes item count inflation (e.g. 192 items $\rightarrow$ 46,080 item references per step), inflating PostgreSQL `execution_data` to millions of rows, triggering Node.js heap allocation OOM (`FATAL ERROR: Reached heap limit Allocation failed`), and causing IPC Task Broker timeouts on subsequent Code nodes.
- **Remediation:** Set `executeOnce: true` on all singleton API fetch nodes intended to retrieve reference or market snapshot data. On V2.2 Master, enabling `executeOnce: true` on the 9 HTTP fetch nodes reduced step 0–4 execution time from ~15 minutes down to 3.9 seconds total.

### 52. Node.js V8 Heap Memory Limit (`FATAL ERROR: Reached heap limit`)
- **Rule:** On n8n 2.x Docker containers executing complex workflows or parallel HTTP fetches, Node.js defaults to a 4GB (`--max-old-space-size=4096`) V8 heap allocation limit regardless of host system RAM capacity.
- **Symptom:** Container crashes or log shows `FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory`. `execution_entity` reports `NodeCrashedError`.
- **Fix:** Set environment variable `NODE_OPTIONS=--max-old-space-size=8192` (or 16384) in the n8n Docker container environment to allow n8n to utilize host system RAM.

### 53. Star Parallel Topology + Single-Item Normalize Pattern
- **Rule:** When fetching multiple market/reference datasets from public APIs (e.g. 9 Binance kline/ticker/funding endpoints), fan out HTTP requests in parallel from a single 1-item seed node instead of chaining them sequentially.
- **Pattern:** Pass each HTTP fetch output through a dedicated Normalize Code node (`return [{json:{data:$input.all().map(x=>x.json)}}];`) to collapse raw JSON arrays into exactly 1 output item before merging into downstream snapshot/feature calculation nodes.
- **Pitfall:** Chaining sequential HTTP fetches without normalization causes n8n to multiply items across arrays (e.g. 192 kline items $\times$ downstream fetches $\rightarrow$ 46,080 item iterations), causing severe memory pressure, task broker stalls, and V8 heap allocation OOM crashes.

### 54. Execution Memory Amplification & Single-Item Aggregate Barrier
- **Rule:** In n8n 2.x, `execution_data` graph object reference retention in TypeORM/V8 engine can create extreme memory amplification ($\sim 24,000\times$ ratio of peak V8 heap vs aggregate JSON payload size).
- **Single-Item Barrier Pattern:** When multiple parallel normalized branches feed into a single Code calculation node, insert an explicit single-item Aggregate Code node barrier (`return [{json:{spot: $('Normalize Spot').first().json.data[0], btc15m: $('Normalize BTC 15m').first().json.data, ...}}];`) to guarantee exactly 1 item input and prevent cross-branch item evaluation or V8 reference cloning overhead.
- **Pitfall:** Connecting multiple parallel branch outputs directly to a single Code node without a single-item Aggregate barrier causes n8n to retain full uncompacted branch execution graphs in memory, which can exhaust even 8 GB V8 heap limits on small (300 KB) aggregate payloads.

### 55. Controlled Node.js Heap Size Allocation (`NODE_OPTIONS="--max-old-space-size=8192"`)
- **Rule:** When running n8n in Docker on high-capacity VPS hardware (e.g. 54 GB RAM) processing heavy data pipelines, increase the V8 heap limit from default 4 GB (`--max-old-space-size=4096`) to 8 GB via `NODE_OPTIONS="--max-old-space-size=8192"` paired with Docker container memory caps (`--memory=16g`).
- **Safety Rule:** Never jump directly to 16 GB heap without first normalizing item topology and verifying that memory amplification ratio is bounded; an unnormalized item shape leak will exhaust 16 GB heap just as easily as 4 GB.

### 56. `shared_workflow` Ownership Requirement for Programmatic DB Workflows
- **Rule:** When inserting or seeding new sub-workflows directly into PostgreSQL (`workflow_entity`), also insert a corresponding project ownership record into `public.shared_workflow` (`workflowId`, `projectId`, `role='workflow:owner'`).
- **Pitfall:** Omitting the `shared_workflow` record causes n8n activation or sub-workflow execution to fail with `EntityNotFoundError: Could not find any entity of type "SharedWorkflow" matching: {"where":{"workflowId":"...","role":"workflow:owner"}}`.

### 57. Execution Memory Isolation (`EXECUTIONS_DATA_SAVE_ON_SUCCESS=none`)
- **Rule:** For high-frequency or data-heavy n8n pipelines, set `EXECUTIONS_DATA_SAVE_ON_SUCCESS=none` in the n8n container environment.
- **Pitfall:** Defaulting to saving successful execution data retains full TypeORM graph object references for all intermediate nodes in memory, causing severe memory amplification (up to 24,000x payload size) and triggering V8 heap allocation OOM crashes (`FATAL ERROR: Reached heap limit`).

### 58. Async `fetch()` in Code Nodes for Memory-Isolated HTTP Retrieval
- **Rule:** When fetching large arrays of JSON data (e.g. multi-timeframe klines or order books) where n8n's native HTTP Request node creates execution graph overhead, use an async `fetch()` call inside a single Code node (`const res = await fetch(...); const data = await res.json(); return [{json: {dataset_key: '...', data}}];`).
- **Benefit:** Returns exactly 1 n8n item containing the dataset array, bypassing n8n item-multiplier loops and zeroing out TypeORM execution graph memory retention overhead.

### 59. External Market Data Sidecar Pattern for OOM Prevention
- **Rule:** When an n8n workflow retrieves multiple high-volume raw HTTP datasets (e.g. 9 separate exchange endpoints returning thousands of kline arrays and order books), processing raw HTTP responses directly inside n8n nodes causes TypeORM execution graph object reference retention, driving V8 heap usage toward the 4 GB limit and causing `FATAL ERROR: Reached heap limit` crashes.
- **Pattern:** Offload raw multi-endpoint HTTP fetching to a lightweight external sidecar service/container (e.g. Python Flask/Gunicorn or Go) that aggregates and normalizes raw exchange responses into exactly ONE compact JSON payload (`mai.market_fetch.v1`, ~0.2 MB). n8n then uses a single HTTP Request node (`HTTP input items = 1`, `HTTP output items = 1`), reducing n8n execution graph retention and keeping V8 heap allocation completely flat.

### 60. Direct Database In-Place Workflow Patching & Trigger Re-registration
- **Rule:** When modifying workflow node graphs directly in PostgreSQL (`workflow_entity.nodes` and `workflow_entity.connections`), n8n's in-memory schedule trigger wheel will NOT automatically update.
- **Procedure:**
  1. Export nodes and connections JSON files and update `workflow_entity` via `UPDATE workflow_entity SET nodes = ..., connections = ..., "updatedAt" = NOW() WHERE id = '...';`.
  2. Toggle `active = false` and then `active = true` in DB, or click "Publish"/"Save" in the browser UI.
  3. Restart the n8n container (`docker restart <container>`).
  4. Inspect `docker logs <container>` to verify the startup message `Activated workflow "..."` appears under `Start Active Workflows:`.

### 51. Robust Schedule Migration: `n8n-nodes-base.cron` vs `scheduleTrigger`
- **Rule:** When configuring multi-hour (e.g. 6h) or multi-day (e.g. 7d) recurring workflows, prefer `n8n-nodes-base.cron` with explicit cron expressions (e.g., `0 */6 * * *` or `0 0 */7 * *`) over `n8n-nodes-base.scheduleTrigger`.
- **Pitfall:** `scheduleTrigger` parameter schemas across n8n 2.x versions (1.2 vs 1.3) can mismatch `interval` vs `mode`/`value` formats, throwing `WorkflowActivationError: Invalid interval` during startup activation and stalling the in-memory timer wheel for all other active workflows.
- **Cron node schema:**
  ```json
  {
    "name": "Every 6 Hours",
    "type": "n8n-nodes-base.cron",
    "typeVersion": 1,
    "parameters": {
      "triggerTimes": {
        "item": [{ "mode": "custom", "cronExpression": "0 */6 * * *" }]
      }
    }
  }
  ```

### 49. Programmatic Node-by-Node Timeline Extraction from `execution_data`
- **Rule:** In n8n 2.x, `execution_data.data` stores compressed execution steps. Node start times, execution durations (`executionTime`), statuses, and error indices can be retrieved programmatically via Python/JS by filtering items with `'startTime'`.
- **Snippet:**
  ```python
  steps = [item for item in data if isinstance(item, dict) and 'startTime' in item]
  for step in steps:
      print(f"Step {step['executionIndex']}: duration={step['executionTime']}ms, status={step['executionStatus']}")
  ```

### 40. Regime Performance Entity Identity
- **Rule:** Include `entity_type` in both SELECT and GROUP BY of regime performance views.
- **Pitfall:** Champion and Shadow entities sharing the same `entity_key` (e.g. both have agent `A01`) are merged into a single row, corrupting per-entity regime analysis.

### 31. Many-to-Many Join Elimination in Calibration Views
- **Rule:** When comparing raw sample counts ($N_{raw}$) and effective non-overlapping counts ($N_{eff}$) across confidence buckets, pre-aggregate raw statistics and effective statistics separately.
- **Pitfall:** Joining raw sample rows directly to effective sample rows on bucket keys creates many-to-many ($M \times N$) Cartesian row multiplication, distorting sample counts and calibration gaps.

### 32. Ensemble Variant Isolation in Correlation & Ablation
- **Rule:** Pairwise agent correlation and leave-one-out (LOO) deterministic ablation must be calculated separately per explicit `ensemble_variant` (`CHAMPION_INPUT`, `CHALLENGER_INPUT`).
- **Pitfall:** Unioning champion and shadow agents into a single unsegregated ensemble creates cross-mixed pairings and ablation scores for combinations that no actual policy or production system executed.
- **Exact ensemble reconstruction (V3.2.3):** `CHALLENGER_INPUT` must include Champion base valid agents PLUS V3 supplemental shadow agents (not shadow agents alone). Use a dedup rule with `ROW_NUMBER() OVER (PARTITION BY run_id, ensemble_variant, agent_key ORDER BY source_priority DESC)` where shadow supplemental has higher precedence.
- **Reconciliation view:** Compare reconstructed ensemble agent count and directional mean against the persisted `v3_shadow_predictions.valid_agent_count` and `deterministic_directional_mean`. Flag MATCH/MISMATCH/NO_PREDICTION states. A mismatch is a data-quality finding, never a promotion trigger.

### 36. Deployment Artifact Secret Scanning
- **Rule:** Before packaging deployment ZIPs, scan all SQL, workflow JSON, evidence markdown, and report files for secrets.
- **Patterns to check:** Telegram bot tokens (`\d{8,}:[A-Za-z0-9_-]{35}`), Bearer tokens, database passwords, API keys (`sk-*`, `AKIA*`).
- **Pitfall:** n8n workflow JSON exports can embed credential references. Verify that credential objects contain only `id`/`name` references, not plaintext passwords or tokens.

### 33. Database-Backed Test Workflow Discipline
- **Rule:** Test workflows (e.g. `MAI V3.2 - 99 Analytics Tests`) must execute real database queries against deployed PostgreSQL views (`mai.v3_2_3_v_*`) and perform structural graph/node scans.
- **Pitfall:** Relying on client-side JS duplicate formulas or hardcoded `t('assertion', true, true)` assertions masks underlying SQL defects and gives false-positive regression passes.
- **Transactional fixtures (V3.2.3):** Use `BEGIN; CREATE TEMP TABLE ... ON COMMIT DROP; INSERT INTO production tables; query views; assert; ROLLBACK;` to run controlled fixtures without polluting production data. The `ON COMMIT DROP` temp tables hold test metadata, while real production tables get synthetic rows that are rolled back.
- **Evidence consistency:** The exact number of assertions in the deployed test code must match the `passed/total` counts in evidence reports. Include a JS post-processor that recomputes counts from the actual tests array to catch drift.
- **Graph side-effect scan:** The test must statically scan deployed workflow JSON for zero Telegram market-signal nodes, zero exchange/trading nodes, zero production weight mutation SQL, and zero auto-promotion SQL. Exclude the test query node itself from the scan (it contains INSERT/UPDATE as fixture setup, not production side effects).

---

## References & Support Files

- [`references/mai_v3_n8n_import_pitfalls.md`](references/mai_v3_n8n_import_pitfalls.md): Detailed notes on n8n CLI workflow import ID requirements, task broker port 5679 collisions, and PostgreSQL schema permission grants.
- [`references/mai_v3_2_analytics_math.md`](references/mai_v3_2_analytics_math.md): Mathematical formulations for non-overlapping cohort statistics, Wilson 95% confidence intervals, and sample maturity classifications.
- [`references/mai_v3_2_3_test_fixtures.md`](references/mai_v3_2_3_test_fixtures.md): V3.2.3 transactional DB fixture test catalog (17 assertions A-O), pattern design, and fixture namespace conventions.

---

## Verification Steps

Before claiming an n8n workflow is complete:
1. Verify node execution status is `success` using `get_execution`.
2. Confirm all child sub-workflows are published before publishing parent workflows.
3. Validate end-to-end signal flow from trigger to final action (e.g. HTTP POST, Telegram notification, or database record).
