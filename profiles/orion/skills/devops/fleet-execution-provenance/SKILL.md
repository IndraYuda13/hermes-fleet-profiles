---
name: fleet-execution-provenance
description: Use when verifying multi-agent execution authenticity, Kanban provenance, worker dispatch logs, artifact SHA-256 integrity, and distinguishing native profile execution from scripted synthesis.
version: 1.0.0
author: Hermes Fleet Architecture
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [governance, quality, provenance, kanban, fleet-audit]
    category: devops
    requires_toolsets: [kanban, terminal, file]
environments:
  - kanban
  - agent
---

# Fleet Execution Provenance & Dispatch Audit Standard

Provides deterministic procedures for auditing multi-agent execution authenticity, ensuring task outcomes were produced by real dispatched worker profiles, and verifying artifact checksum integrity.

## Core Provenance Layers

### 1. Ingestion Provenance (Card Creation)
- Verify cards were created via native `kanban_create(title=..., assignee=..., ...)`.
- Check if direct database manipulation (`sqlite3` / raw script insertion) occurred. If cards were manually seeded into SQLite, execution provenance is categorized as `PARTIAL` rather than pure `VERIFIED`.

### 2. Dispatcher Lifecycle & Process Isolation
Audit the `task_runs` and `task_events` tables for the task:
- `task_runs`: Check `worker_session_id`, `started_at`, `ended_at`, `status='done'`, and `outcome='completed'`.
- `task_events`: Verify `spawned` event with a concrete OS `pid`, periodic `heartbeat` events during long runs, and a `completed` event with structured payload.
- Confirm independent profiles executed as isolated OS processes under the active daemon lock.

### 3. Artifact & Revision Integrity
- Verify all deliverable paths declared in completion metadata actually exist on disk.
- Compute SHA-256 checksums on all disk artifacts (`sha256sum <paths>`) and verify matching hashes.
- Verify exact Git commit SHA across all specialist reports and final synthesis (`stale_revision_pass_accepted = NO`).

## Diagnostic Queries

```bash
# Check run outcomes and worker session metadata
sqlite3 ~/.hermes/kanban.db "SELECT id, task_id, profile, started_at, ended_at, status, outcome FROM task_runs WHERE task_id = 't_example' ORDER BY id ASC;"

# Check lifecycle events (spawned PID, heartbeats, completed payload)
sqlite3 ~/.hermes/kanban.db "SELECT id, run_id, kind, created_at, substr(payload, 1, 60) FROM task_events WHERE task_id = 't_example' ORDER BY id ASC;"
```

## Verdict Classifications

| Verdict | Definition |
| :--- | :--- |
| **`FLEET_STRESS_EXECUTION_VERIFIED`** | Native `kanban_create`, daemon-spawned worker processes with valid PIDs/heartbeats, genuine file artifacts with matching SHA-256, and zero orchestrator production edits. |
| **`FLEET_STRESS_EXECUTION_PARTIAL`** | Genuine daemon-spawned execution and authentic specialist artifacts, but initial card creation or status was seeded/modified via direct database manipulation or script. |
| **`FLEET_STRESS_EXECUTION_INVALID`** | Fake/mocked execution, fabricated artifacts, missing run/event logs, or orchestrator directly generated specialist deliverables. |
