---
name: autonomous-worker-lifecycle
description: Use when managing autonomous worker runs and pipelines.
version: 1.0.0
author: Hermes Fleet Architecture
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [autonomous-agents, kanban, lifecycle, timeout-handling, pipeline-gating, dag-orchestration]
    category: autonomous-ai-agents
    requires_toolsets: [kanban, terminal, file]
environments:
  - kanban
  - agent
---

# Autonomous Worker Lifecycle & Pipeline Gating

Comprehensive operating standard for managing autonomous worker tasks, long-running execution limits, dispatcher timeouts, review handoffs, and multi-stage pipeline sequencing.

## When to Use

- When coordinating multi-phase software engineering pipelines across autonomous specialist profiles (e.g., FORGE, FRAME, PRISM, SENTINEL, LENS).
- When an autonomous worker task reports a `timed_out` state with active dispatcher retries (`retry_status: ready`).
- When managing implementer handoffs (`review_requested`) and preparing independent verification DAGs without self-review loops.
- When sequencing full-stack systems requiring database and worker contracts to freeze before frontend binding.

## Core Lifecycle Procedures

### 1. Multi-Stage Pipeline Staging (Backend Freeze Before Frontend Binding)
When delivering complex multi-tier systems (database, authentication, background worker, and frontend user interfaces):
1. **Sequence Upstream First:** Implement core data schemas, authentication routines, and asynchronous worker loops before building frontend routes.
2. **Verify Upstream Contracts:** Run full test suites against the backend services before dispatching frontend implementation.
3. **Bind Live Services:** Direct the frontend worker to import and bind to the verified server services and schemas rather than stubbed mock objects, preventing API contract drift.
4. **Continuous Multi-Phase Advancement:** When directed to execute until completion, do not stall at intermediate phase boundaries. Immediately advance to the subsequent phase once independent verification certifies the active phase (`VERIFIED`). Pre-author downstream mission contracts and task specifications so tasks dispatch without latency.

### 2. Implementer Review Handoff & Revision Locking
When an implementer finishes work and requests review:
1. **Inspect Git Tree:** Verify that working directory changes are clean and committed to the intended target branch.
2. **Lock Revision SHA:** Do not allow implementers to review or certify their own cards. Close the implementation card cleanly (`hermes kanban complete --force --summary "<summary>" <task_id>`) to freeze the commit SHA.
3. **Dispatch Independent Verifiers:** Spawn distinct reviewer cards for independent audit (e.g. security audit, functional regression, visual audit) with parent links to the completed implementation card.
4. **Exact-Revision Binding:** Review task bodies must explicitly specify the frozen commit SHA and declare read-only inspection mode to guarantee separation of duties.
5. **Post-Review Verification Tracking:** When a verifier commits an independent verification report artifact (`docs/*_VERIFICATION_REPORT.md`), verify working tree cleanliness via git status and ensure the report commit SHA is recorded before dispatching downstream tasks.

### 3. Worker Timeout Diagnosis & Retry Management
Heavy builds, framework scaffolding, and multi-suite integration tests frequently exceed standard per-task execution budgets (e.g. 1800s):
1. **Differentiate Timeout from Failure:** A `timed_out` event with `retry_status: ready` indicates the dispatcher is actively continuing the task in a new run.
2. **Do Not Recreate Tasks on Automatic Notifications:** When receiving an automated notification that a task timed out and dispatcher will retry, inspect the board (`kanban show <id>`). Verify the active retry run exists before taking any action. Never spawn duplicate tasks or rebuild existing DAGs.
3. **Inspect Before Intervening:** Run read-only filesystem or git status checks on the target workspace before canceling or re-creating cards.
4. **Preserve In-Flight Artifacts:** If untracked components, build outputs, or partial test passes exist, avoid touching workspace files. Allow the spawned retry run to finish its build and tests cleanly.
5. **Enforce Idempotent Continuity:** When workers resume on an existing workspace, they must detect pre-existing files, avoid redundant scaffolding steps, and proceed directly to testing and completion.
6. **Recover Exhausted Timeouts with Working Tree Audit:** When a task exhausts retries and stays timed out, audit the workspace immediately with `git status` and test logs before rescheduling. If the worker completed code generation, compilation, and tests before the deadline, lock the commit and complete the card with `--force` rather than discarding working artifacts or recreating duplicate tasks.

### 4. Event-Driven Wake Subscriptions vs Busy-Waiting
For long-running autonomous worker pipelines:
1. **Subscribe to Task Completion Notifications:** Use `hermes kanban notify-subscribe --platform telegram --chat-id "<chat_id>" --chat-type dm --notifier-profile <profile> --delivery-mode notify+wake <task_id>` when launching long tasks.
2. **Release Turn Immediately:** Trigger dispatch (`hermes kanban dispatch`) and end the turn immediately. Do not execute synthetic polling or busy-wait loops; the runtime automatically wakes the session upon task completion or failure.

## Pitfalls & Defensive Rules

- **Do not cancel tasks during active dispatcher retries.** Terminating a task that timed out while its spawned retry is compiling creates orphaned processes and lost progress.
- **Do not permit implementers to certify their own deliverables.** An implementer claiming tests pass does not replace an independent verification pass against the frozen commit SHA.
- **Never design UI against unverified backend contracts.** Frontend implementations built against hypothetical schemas require costly refactoring once backend realities diverge.
- **Do not poll status in tight loops.** Rely on platform notification webhooks and wake events (`notify+wake`) rather than issuing repetitive heartbeat or status calls.
- **Supply compliant production credentials when testing Next.js servers locally:** `next start` forces `NODE_ENV=production`. If schemas strictly validate production secrets (e.g. `SESSION_SECRET`, `GOOGLE_CLIENT_ID`), verification runners must pass compliant dummy secrets to prevent immediate exit crashes during local E2E or visual audits. Ensure port 3000 is clean of dangling previous processes before starting.
- **Never invoke virtual environments or binaries outside the current repository/profile:** Calling external Python binaries or virtualenvs from unrelated host paths (e.g. other project dirs) triggers command execution security filters, wastes turn budget, and causes timeouts. Use the active project venv or system binaries.

## Lifecycle Verification Checklist

- [ ] Upstream backend and worker services tested and verified before UI dispatch.
- [ ] Implementer card closed and Git commit SHA recorded before review dispatch.
- [ ] Workspace inspected for tangible progress upon task timeout notification.
- [ ] Independent verifier cards dispatched in isolated execution lanes.
- [ ] All final verification reports reference the exact same Git commit SHA.
