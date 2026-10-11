---
name: live-ui-kanban-orchestration
description: Use when orchestrating tasks for live production services.
version: 1.2.0
metadata:
  hermes:
    tags: [ui, kanban, orchestration, devops, docker, systemd, live-services, sqlite, backup]
    category: custom
---

# Live Service Kanban Orchestration

## Overview
Standard operating procedure for discovering live production service environments, establishing staging safety barriers, decomposing audit and implementation missions into structured Kanban DAGs, steering workers mid-flight, managing SQLite WAL backup/DR, and executing safe production deployments.

## Core Rules & Workflow

### 1. Discover Workspace & Live Target
Before creating Kanban tasks for any live domain:
- **Docker services:** Inspect container labels to find the host workspace:
  `docker inspect <container_name> | grep -i "com.docker.compose.project.working_dir"`
- **Systemd / Native services:** Identify service configuration and working directory:
  `systemctl status <service>` or `systemctl cat <service>` -> find `WorkingDirectory=` and `ExecStart=`.
- **Serving Mechanism Check:** Verify how assets are served. If FastAPI, Flask, Express, or PHP mounts static directories directly from the working tree per-request without caching or restart, any file modification immediately impacts live users in real time.
- **Audit Isolation Invariant:** During audit and reconnaissance rounds, all red-teaming, security probes, and functional tests must be strictly non-mutating against live production databases and live external webhook/payment endpoints. Active exploit proofs must be executed against isolated local replicas or mock environments; never generate ghost orders or modify financial balances on a production instance.

### 2. The Staging Isolation Invariant (Zero Live In-Flight Edits)
- **Production is strictly READ-ONLY during development and testing:** Never set `workspace_path` to live production or allow workers to edit production files in place.
- **Git Baseline First:** Ensure a baseline git commit or tag exists on production (`git tag baseline-<campaign>` or `git status`). If the directory is unversioned, initialize git (`git init && git add -A && git commit -m "baseline"`) and tag it so one-command rollback (`git reset --hard baseline-...`) is guaranteed.
- **Pre-Work Database Snapshot:** Execute an atomic SQLite backup with `sqlite3 file:<db>?mode=ro ".backup <backup_path>"` before any worker activity begins.
- **Create Staging Working Copy:** Snapshot production source into a dedicated staging directory:
  `rsync -a --exclude '.venv' --exclude '.git' --exclude 'data' --exclude '.env' <prod_path>/ <staging_path>/`
- **Explicit Path Rule in Task Prompts:** Prepend the staging working copy path as the mandatory edit target in every task brief:
  `TARGET: <staging_working_copy_path> (Production is STRICTLY READ-ONLY reference)`.
- **Immediate Steering Protocol:** If tasks are dispatched referencing production paths, immediately post `kanban_comment` to running workers redirecting them to staging, and bulk-update pending tasks via `hermes kanban edit <id> --body ...` before workers claim them.

### 3. Kanban Task Creation & DAG Validation
When calling `kanban_create`:
- **Title (REQUIRED):** `title` is mandatory on every call; omitting `title` causes an immediate kernel error.
- **Parent ID Verification:** Always verify parent IDs exist before passing `parents=[...]`. Passing nonexistent or mistyped IDs aborts task creation with `unknown parent task(s)`.
- **Workspace:** Use `workspace_kind="scratch"` (or `workspace_kind="dir"` pointing to staging), never to production.
- **Dependency Sequencing:** Structure waves cleanly: Wave 0 (Test isolation/harness) -> Wave A/B/C (Backend/Services/DB) -> Wave D (Frontend overhaul) -> Independent Verification (Functional, Security, Visual) -> Gated Deployment Window -> Final Synthesis.
- **Same-Profile & Overlapping-File Serialization:** If multiple tasks share the same assignee profile (e.g. `forge`) or modify overlapping service/logic files in the staging copy, do NOT leave them unlinked as parallel ready tasks. The dispatcher will spawn them concurrently, leading to file write collisions and race conditions. Always link them sequentially (`parent -> child` via `kanban_link`) so they run in orderly succession. If parallel workers are spawned accidentally on overlapping files, immediately reclaim subsequent tasks (`hermes kanban reclaim <id>`), terminate their worker processes, and apply `kanban_link`.
- **Wave 0 Test Isolation Gate Invariant:** Any multi-agent implementation wave that relies on regression testing must be gated by a dedicated Wave 0 task. Wave 0 must establish a centralized `conftest.py` that enforces: (1) pre-import environment redirection of database and asset URLs to temporary locations, (2) patching of all import-time database singletons across all app modules and route handlers (preventing cross-datastore leaks to live DB), and (3) hard outbound socket/network blocking so tests never hit live third-party vendor APIs or read live production databases.

### 4. Mid-Flight Steering & Attachment Timeout Protocol
- **Steer Active Workers:** Use `kanban_comment` on running tasks to issue course corrections (e.g. redirected paths, updated constraints). Workers read comments during execution. In CLI commands, note that `hermes kanban comment <id> <text>` takes message text as a positional argument (not `--body`). Prefer the native `kanban_comment` tool inside agent sessions.
- **Disk-First Evidence Delivery:** Instruct workers to write heavy reports, logs, and screenshots directly to a designated evidence directory (`/root/fleet-evidence/<campaign>/...`) with SHA-256 manifests, keeping Kanban task metadata and summaries lightweight.
- **Attachment Upload Timeout Guard:** Heavy tasks often finish their reports and files on disk but time out while uploading large attachments via `kanban_attach` or `kanban_complete`.
- **Steering Retries:** When the dispatcher retries a timed-out task, inspect disk first. If the report or code is already complete, immediately post a steering comment via `kanban_comment` instructing the retry worker to verify existing disk artifacts and complete directly without re-running work from scratch.

### 5. SQLite WAL Database Backup & Disaster Recovery Standards
- **Never use `cp` on active SQLite WAL databases:** A raw file copy misses uncheckpointed WAL frames and risks a torn page copy during concurrent writes. Always use `sqlite3 file:<db>?mode=ro ".backup <dest>"` to execute an atomic, WAL-checkpointed backup.
- **Dual-Location Redundancy:** Store automated backups across at least two physically distinct block devices or filesystem mounts (e.g. root filesystem `/var/backups/...` and secondary storage `/mnt/...`), verifying byte-identical SHA-256 checksums.
- **Fail-Closed Restore Drill:** Verify backup usability by restoring to an isolated directory and booting the application on a temporary port with external payment and vendor APIs mocked or disabled, confirming `/api/health` and database integrity (`PRAGMA integrity_check`) without triggering external mutations.

### 6. Gated Production Deployment Window
Code changes reach production ONLY via a dedicated deployment task (owned by ATLAS):
1. **Pre-Deploy Database Backup & Integrity Check:** `sqlite3 <db> ".backup <backup_path>"` + SHA-256 hash + `PRAGMA integrity_check;`.
2. **Data Reconciliation & Idempotent Migrations:** Run reconciliation scripts before deploying new code schemas.
3. **Controlled Transfer:** Copy staging code to production using `rsync` with strict excludes:
   `rsync -a --exclude '.env' --exclude 'data/' --exclude '.venv/' --exclude '.git/' --exclude '__pycache__/' --exclude '.pytest_cache/' <staging_path>/ <prod_path>/`
4. **Environment & Secrets Hardening:** Update `.env` (enforcing `chmod 600`) and systemd units only during the maintenance window.
5. **Restart & Automated Smoke Testing:** Restart service, verify `health` endpoint, check error handling on tampered requests, and confirm restart counters (`NRestarts=0`).
6. **Executable Rollback Script:** Always author and test `ROLLBACK_<campaign>.sh` before closing the deployment task.

### 7. Mandatory Turn Release (Anti-Polling Invariant)
- **Zero Sleep Loop:** Never run `sleep` loops or while-loops in terminal waiting for task completion.
- **Native Wake:** Hermes automatically subscribes the creator session via `delivery_mode="notify+wake"`. Conclude your turn immediately after dispatching; the gateway will natively wake ORION when workers finish (`completed` / `blocked`).
