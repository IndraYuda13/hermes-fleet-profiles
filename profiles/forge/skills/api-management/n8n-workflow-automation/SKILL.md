---
name: n8n-workflow-automation
description: Use when building, testing, or publishing n8n workflows.
---

# n8n Workflow Automation via n8n-mcp

Design, build, test, and publish n8n workflows programmatically using `n8n-mcp` tools and `@n8n/workflow-sdk`.

## Workflow lifecycle & tool sequence

1. **Plan:** `mcp__n8n_mcp__get_workflow_best_practices(technique=...)`; `get_sdk_reference(section='all')` when node/expression/credential syntax is needed.
2. **Validate & create:** write code importing `{ workflow, node, trigger, expr, newCredential }` from `@n8n/workflow-sdk`; run `validate_workflow(code=...)`, then `create_workflow_from_code(code=..., name=..., description=...)`.
3. **Test:** `execute_workflow(workflowId=..., executionMode='manual')`; inspect per-node output with `get_execution(executionId=..., workflowId=..., includeData=true)`.
4. **Publish:** `publish_workflow(workflowId=...)`; retire drafts with `archive_workflow(workflowId=...)`.
5. Before calling a workflow complete: node status `success` in `get_execution`, all referenced sub-workflows published, and end-to-end signal flow verified from trigger to final action.

## Sub-workflows

- **Publish children first.** Publishing a parent whose `executeWorkflow` child is unpublished fails: `Node "X" references workflow Y which is not published`.
- Sub-workflows invoked via `executeWorkflow` must use `n8n-nodes-base.executeWorkflowTrigger` as their trigger node; anything else fails activation (`Workflow cannot be activated because it has no trigger node`).
- Pass `workflowId` as a Resource Locator (`{__rl: true, value: '<id>', mode: 'list', cachedResultName: '<name>'}`) or an n8n expression string; a bare string ID fails validation or throws `No information about the workflow to execute found`.
- **Forward payloads explicitly.** In `mode: 'each'`, the item-generating Code node must forward parent data objects (e.g. `snapshot: $json`); generating items with only metadata leaves children with empty inputs.
- **`mode: 'each'` vs `mode: 'once'`:** `each` for independent per-item tasks; `once` for singleton downstream workflows (coordinator, notifier). Running `each` into a notifier after N items fires N duplicate executions.
- Use `expr(...)` from the SDK for dynamic values; raw `{{ }}` in parameter strings is n8n runtime expression syntax and will be evaluated as such.

## Credentials & project ownership

- Nodes with unconfigured required credentials fail `publish_workflow`. Bind credentials with both `id` and `name`: `credentials: { postgres: { id: '<id>', name: '<name>' } }`. Omitting `id` causes `Found credential with no ID` / SASL errors at runtime.
- Rows inserted directly into `credentials_entity` or `workflow_entity` also need project ownership rows: `public.shared_credentials` (`credentialsId`, `projectId`, `role='credential:owner'`) and `public.shared_workflow` (`workflowId`, `projectId`, `role='workflow:owner'`). Omitting them fails activation/execution with `EntityNotFoundError ... SharedWorkflow/SharedCredentials`.
- Maintain two DB credentials: an admin bootstrap (superuser, schema migrations/DDL) and a least-privilege runtime role (DML only on target schemas) for workflow nodes.
- For environments without UI-configured credentials, route external calls through `n8n-nodes-base.httpRequest` to local API endpoints instead.

## Item multiplication & memory (the #1 OOM cause)

- An upstream node outputting N items runs every downstream node N times unless `executeOnce: true`. Chaining 9 HTTP fetch nodes after a 192-item kline response produces 46k+ item iterations, millions of `execution_data` rows, V8 heap OOM, and task-broker timeouts. Set `executeOnce: true` on all singleton fetch/reference nodes.
- Fan out parallel fetches from a single 1-item seed node; pass each fetch output through a dedicated Normalize Code node (`return [{json:{data:$input.all().map(x=>x.json)}}];`) collapsing output to exactly 1 item before merging.
- Insert a single-item Aggregate Code node barrier where parallel normalized branches converge (`$('Normalize X').first().json.data`): without it, TypeORM/V8 retain uncompacted branch execution graphs (~24,000× payload amplification can exhaust even 8 GB heaps).
- For large datasets, use `await fetch(...)` inside one Code node to return exactly 1 item, bypassing HTTP-node graph overhead; or offload multi-endpoint fetching to an external sidecar service returning one compact payload.
- Set `EXECUTIONS_DATA_SAVE_ON_SUCCESS=none` for high-frequency/data-heavy pipelines. Raise `NODE_OPTIONS=--max-old-space-size` (e.g. 8192, paired with a container memory cap) only AFTER item topology is normalized — a bigger heap does not fix an unnormalized item shape.

## Triggers, activation & scheduling

- Never activate manual-trigger-only or triggerless workflows (startup error: `at least one active trigger ... required`). Keep `active: false` for utility/bootstrap/test workflows executed on demand.
- `n8n import:workflow` deactivates previously-active workflows. Reactivate after import and verify: `SELECT id, name, active FROM workflow_entity WHERE id IN (...)`.
- **The scheduler is in-memory.** Direct DB `UPDATE active=true` (or direct node/connections patches) does NOT register triggers with the running process. Toggle via REST with session cookies from `POST /rest/login`: `PATCH /rest/workflows/<id>` `{"active":false}` then `{"active":true}`, or restart the container, then confirm startup logs show `Activated workflow "..."`.
- `scheduled_job`/`scheduled_task` tables stay empty in single-instance setups (in-memory timer wheel). Verify actual firing via `execution_entity`: `SELECT id, status, mode, "startedAt" FROM execution_entity WHERE "workflowId"='<id>' AND mode='trigger' ORDER BY id DESC LIMIT 5`.
- `scheduleTrigger.minutesInterval` must be ≤ 59; use `field: "hours"`/`"days"` or cron expressions beyond that. For multi-hour/day recurrences prefer `n8n-nodes-base.cron` with explicit cron expressions — scheduleTrigger parameter schemas vary across n8n versions and throw `WorkflowActivationError: Invalid interval`.
- One failing activation (invalid interval, missing trigger) sends ActiveWorkflowManager into exponential-backoff retry (up to 4096s+), stalling timer-wheel registration for ALL active workflows. Unpublish broken workflows (`n8n unpublish:workflow --id=...`, not deprecated `update:workflow`) and restart so startup activation completes cleanly.
- Task runners: n8n 2.x with `N8N_RUNNERS_ENABLED=true` enforces a 300s default Code-node timeout via the task broker (`N8N_RUNNERS_TASK_TIMEOUT`); raise it for heavy computation. Long sequential HTTP pipelines (10+ min) can stall the IPC task broker (port 5679) — diagnose with step timings from `execution_data` (items with `startTime`), benchmark the Code node in isolation, and split monolithic workflows into sub-workflows.

## Docker & CLI operations

- Env vars cannot be changed on a running container. Recreate it with the FULL original config plus new vars — `docker inspect` first for env/network/volume/port/restart policy; dropping one original env var silently breaks DB/timezone features.
- `n8n execute --id=...` fails while the daemon runs (`Task Broker's port 5679 is already in use`). Trigger via schedule/webhook/REST/UI instead.
- Publish flow on Docker n8n 2.x: `docker exec <c> n8n publish:workflow --id=...` (child/error workflows first) → `docker restart <c>` → wait for `/healthz` → `n8n list:workflow --active=true` → export and inspect top-level `active`/`activeVersionId`. `Publishing workflow...` output alone is not proof of runtime activation.
- Inspect/export without API tokens: `docker exec <c> n8n export:workflow --all --output=/tmp/workflows.json` (path is inside the container; `docker cp` it out).
- Patching `workflow_entity.nodes/connections` directly in PostgreSQL does not reach the running in-memory cache — restart the container or toggle activation via REST afterwards.
- The n8n UI login email may differ from the user's primary email; check `SELECT email FROM "user"` if login fails.

## Delivery, audit & safety

- Disable `retryOnFail` on side-effect delivery nodes (Telegram, webhooks): retries execute within the same already-claimed node execution and duplicate messages. Persist audit rows with status `QUEUED` before attempting delivery; update to `SENT` with the external message ID on success, `SEND_UNKNOWN` when delivery state is ambiguous, and hand ambiguity to review rather than blind retries.
- Attach a centralized error workflow via `settings: { errorWorkflow: '<error-handler-id>' }` on each master workflow; an `errorTrigger` workflow alone captures nothing until referenced.
- Requesting JSON from OpenAI-compatible endpoints (9Router, local vLLM, Ollama): always pass `"stream": false` — SSE chunk streams break downstream JSON parsers.
- Never kill local router daemon processes (e.g. 9Router on port 20128); reconfigure via SQLite/API without process termination.
- Use SHA-256 for snapshot fingerprints/dedup (format `sha256-<64 hex>`); 32-bit non-cryptographic hashes collide across continuous runs.
- Scan exported workflow JSON, SQL, and deployment archives for secrets before distribution (bot tokens, bearer tokens, API keys); verify credential objects contain only `id`/`name` references, never plaintext.
- Keep analytics/evaluation workflows strictly read-only toward production configuration: never auto-update production weights or notification thresholds; emit recommendations only.
- For exported artifact archives, ensure `MANIFEST.sha256` relative paths match the export layout and verify with `sha256sum -c` from the artifact root.

## Test & evidence discipline

- Test workflows must execute real queries against deployed views and perform structural graph scans; client-side re-implementations of SQL logic give false-positive regression passes.
- Use transactional fixtures — `BEGIN; CREATE TEMP TABLE ... ON COMMIT DROP; INSERT ...; query views; assert; ROLLBACK;` — to test without polluting production data. Exclude the fixture-setup node itself from production-side-effect scans.
- The assertion count in evidence reports must match the deployed test code; recompute counts from the actual test array to catch drift.

## References & support files

- `references/mai_v3_2_analytics_math.md` — MAI science-layer SQL/statistics: non-overlapping sample selection (recursive CTE greedy), Wilson 95% CI on effective N, maturity labels, PIT/leakage safety, ensemble reconstruction, evaluation-view and migration rules.
- `references/mai_v3_2_3_test_fixtures.md` — transactional DB fixture test catalog and conventions.
- `references/mai_v3_n8n_import_pitfalls.md` — CLI import ID requirements, task-broker port collisions, schema permission grants.
- `references/docker_activation_runbook.md` — container activation runbook.
- `references/n8n_2_33_7_upgrade_diagnostic.md` — upgrade diagnostics.
