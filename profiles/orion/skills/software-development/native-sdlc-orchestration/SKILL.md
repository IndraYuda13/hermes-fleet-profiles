---
name: native-sdlc-orchestration
description: Orchestrate multi-stage SDLC pipelines via Kanban events.
version: 0.2.0
author: Hermes Fleet Architecture
platforms: [linux]
metadata:
  hermes:
    tags: [Kanban, Sdlc, Orchestration, Multi-Agent, Event-Driven, Dedicated-Boards, Rollback-Anchor]
    category: software-development
    requires_toolsets: [kanban, terminal]
---

# Native SDLC Orchestration

Orchestrate end-to-end software development lifecycles across specialized fleet profiles using event-driven Kanban wake notifications. This skill manages task stage gating, role handoffs, independent review gates, defect remediation loops, and campaign synthesis without busy-waiting or manual polling. Direct code changes are never performed by the orchestrator; all implementation and review work is routed to specialized agent profiles.

## When to Use

- When the user asks to audit, test, build, refactor, or overhaul a web application or software project across multiple stages.
- When coordinating sequential or parallel handoffs between designers (`aurora`), implementers (`frame`, `forge`), verifiers (`lens`, `prism`, `sentinel`), infra/SRE (`atlas`), research (`radar`, `quant`), and synthesis (`nexus`).
- When managing multi-stage SDLC gates: design contract, implementation slice, visual audit, functional testing, remediation loop, and production release.
- When an in-flight Kanban task completes and the orchestrator must inspect outcomes and determine the next stage.

## Prerequisites

- Hermes Agent runtime with active Kanban database (`/root/.hermes/kanban/boards/<board>/kanban.db` or current board DB).
- Hermes Gateway running with native event wake enabled (`delivery_mode="notify+wake"`).
- Target specialist profiles configured: `aurora` (design), `frame` (frontend), `forge` (backend), `lens` (visual QA), `prism` (functional/data verification), `sentinel` (security), `atlas` (SRE/infra), `radar` (technical/market research), `quant` (economics/pricing), `nexus` (synthesis/runbooks).
- Direct access to native `kanban_*` tools (`kanban_create`, `kanban_list`, `kanban_show`, `kanban_complete`).

## How to Run

Invoke orchestration actions primarily using the native `kanban_*` tools and board CLI when managing boards:

1. For multi-agent campaigns, create an isolated board with `hermes kanban boards create <slug>`.
2. Anchor live target state (revision manifest + verified SQLite backup) if working against a live deployment.
3. Create stage tasks with native `kanban_create(board="<slug>", ...)` — the session is automatically subscribed for `notify+wake`.
4. Release the conversation turn immediately to allow the gateway to run workers and wake on completion events.
5. On wake, inspect the completed run via `kanban_show`, evaluate acceptance criteria, and trigger the next stage or remediation.

## Quick Reference

- Create dedicated campaign board: `hermes kanban boards create <slug> --name "<name>" --description "<desc>"`
- Create task (native tool): `kanban_create(board="<slug>", assignee="<profile>", title="<title>", body="<spec>", priority=80, workspace_kind="scratch")`
  *(Note: Native `kanban_create` automatically subscribes the active session with `notify+wake`)*
- Inspect board tasks: `kanban_list(board="<slug>")`
- Inspect result: `kanban_show(board="<slug>", task_id="<task_id>")`
- Read deliverable: `read_file(path="<artifact_path>")`

## Procedure

### 1. Stage Inception & Contract Formulation
Before dispatching work, classify the change materiality (M1/M2/M3) and freeze interfaces:
- For frontend/UI: Require `aurora` to draft Design DNA, typography, color palette, and layout tokens before coding starts.
- For backend/API: Define explicit schema endpoints, request/response models, and error statuses before implementation.
- For full-stack: Partition frontend (`frame`) and backend (`forge`) boundaries with explicit mock contracts.

### 2. Dispatch Task & Register Wake Subscription
Invoke through the `terminal` tool:
```bash
TASK_JSON=$(/usr/local/lib/hermes-agent/venv/bin/hermes kanban create \
  --assignee "<assignee>" \
  --workspace scratch \
  --priority 80 \
  --body "<exact specification and acceptance criteria>" \
  --json "<Task Title>")
TASK_ID=$(echo "$TASK_JSON" | jq -r .id)

/usr/local/lib/hermes-agent/venv/bin/hermes kanban notify-subscribe \
  --platform telegram \
  --chat-id "${CHAT_ID:-696907598}" \
  --chat-type dm \
  --notifier-profile orion \
  --delivery-mode notify+wake \
  "$TASK_ID"

/usr/local/lib/hermes-agent/venv/bin/hermes kanban dispatch
```

### 3. Immediate Turn Release (Anti-Polling Invariant)
Immediately conclude the current conversation turn. Report the dispatched task ID, assignee, and objective to the user. Do not call `sleep` or execute polling loops in the `terminal` tool. The gateway will wake the session automatically when the status transitions to `completed`, `blocked`, or `review_requested`.

### 4. Wake Ingress & State Evaluation
When the gateway wakes the session with a task event:
1. Orient via `kanban_show` to read the worker's summary, run metadata, and artifact paths.
2. Inspect the produced artifacts using `read_file` or `search_files`.
3. Check the SDLC State Machine to decide the next action:
   - Case A: Design Complete (`aurora`) -> Spawn implementation task to `frame` (UI) or `forge` (Backend) referencing the approved design artifact.
   - Case B: Implementation Complete (`frame`/`forge`) -> Route to independent verification. Do NOT approve or self-review. Spawn `lens` for visual/DOM audit and `prism` for functional/unit test verification.
   - Case C: Review Rejection / Defects Found (`lens`/`prism`) -> Extract concrete defect list (P0/P1). Spawn a remediation task assigned back to the original implementer. Include exact failure evidence and re-verification criteria.
   - Case D: All Gates Passed (VERIFIED) -> Spawn deployment / ingress task to `atlas` (SRE).
   - Case E: Deployment Verified (`atlas`) -> Run post-deployment smoke check (HTTP 200, SSL, latency) and deliver final verified synthesis to the user.

### 5. Multi-Branch DAG Synchronization
When parallel tasks run (e.g. `lens` visual QA and `prism` functional QA simultaneously):
- On the first wake arrival, acknowledge receipt, inspect artifacts, record findings in working state, and yield turn if the sibling task is still in flight.
- On the second wake arrival, synthesize both results. Require unanimous PASS from all verifiers before proceeding to deployment.

## Pitfalls

- **Busy-waiting loops:** Executing `sleep 30` loops in the `terminal` tool locks the agent turn and wastes timeout budgets. Always release the turn after subscribing with `notify+wake`.
- **Implementer self-approval:** Never allow `frame` or `forge` to certify their own deliverables. Independent gates (`lens`, `prism`, `sentinel`) are mandatory.
- **Skipping remediation verification:** When a defect is fixed by an implementer, re-dispatch the verification task against the new revision rather than assuming the fix succeeded.
- **Missing wake subscription:** CLI-created tasks do not automatically inherit gateway session context. Always execute `hermes kanban notify-subscribe` with `--delivery-mode notify+wake` immediately after task creation.
- **Premature turn termination on errors:** If a worker completes with a failure or blocked status, do not silently abort. Inspect the blocker reason with `kanban_show` and either remediate or escalate to the user with actionable choices.

## Verification

Confirm the skill operational capability by validating the Kanban subscription delivery mode on an active task:

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/root/.hermes/kanban.db')
c = conn.cursor()
c.execute('SELECT task_id, platform, delivery_mode FROM kanban_notify_subs ORDER BY id DESC LIMIT 1')
row = c.fetchone()
print(f'Last Subscription: task={row[0]}, platform={row[1]}, mode={row[2]}')
assert row[2] == 'notify+wake', f'Expected notify+wake, got {row[2]}'
print('Verification PASS: Native wake delivery mode active.')
"
```
