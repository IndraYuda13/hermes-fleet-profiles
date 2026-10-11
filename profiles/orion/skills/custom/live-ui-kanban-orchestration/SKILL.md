---
name: live-ui-kanban-orchestration
description: Use when orchestrating tasks for live production services.
version: 1.5.0
metadata:
  hermes:
    tags: [ui, kanban, orchestration, devops, docker, systemd, live-services, sqlite, postgresql, backup]
    category: custom
---

# Live Service Kanban Orchestration

## Overview
Standard operating procedure for discovering live production service environments, establishing staging safety barriers, decomposing audit and implementation missions into structured Kanban DAGs, steering workers mid-flight, managing SQLite WAL & PostgreSQL backup/DR, and executing safe production deployments.

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
- **Pre-Work Database Snapshot:** Execute an atomic backup before any worker activity begins (see Section 6).
- **Worker Git Committer Identity Isolation:**
  Configure local repository git identity on the staging/audit tree before workers commit changes (`git config --local user.name "Fleet <profile>" && git config --local user.email "fleet@local.internal"`). Without local repository configuration, automated worker commits inherit the host's global `~/.gitconfig` identity, accidentally attributing automated pipeline commits to the server owner's personal git account.
- **No Hardlinked Dependencies Across Staging/Audit Trees (`cp -al` Invariant):**
  Never use `cp -al` (hardlinks) to snapshot or copy `node_modules` between production and staging or audit trees. In package managers like `pnpm`, metadata files (`.modules.yaml`, `.pnpm/lock.yaml`, workspace states) share identical inodes across trees. Any `pnpm` command (lint, test, build) executed in staging mutates production's metadata inode and can invalidate or drift production dependencies. Always use independent installs, clean git worktrees, or explicitly verify and break shared inodes (`find node_modules -links +1`) before dispatching workers.
- **Disk Floor & Cross-Filesystem Store Trap during Migration:**
  When planning to migrate hardlinked `node_modules` off a tree to break shared links, calculate apparent vs shared inode disk cost first. If `node_modules` is shared with prod (`stat -c %h > 1`), `rm -rf` frees almost 0 bytes, while a re-install from a package store on a separate filesystem mount (e.g. store on `/mnt` while working tree is on `/`) cannot hardlink across devices and must copy ~800 MB onto the root filesystem. If available disk space is near a critical safety floor (e.g. < 8 GB), running migration will plunge disk space into critical territory. Measure `df -h` and check store mount points before scheduling dependency re-installations.
- **Active Worker Quiet-Window Gate (Never rm -rf in-use dependencies):**
  Never run `rm -rf node_modules` or trigger dependency re-installations on a workspace while ANY active worker process has its working directory (`cwd`) pinned to that tree or is executing commands in it. If downstream workers are actively executing in staging, defer workspace dependency migrations to an idle maintenance window or pre-deploy gate.
- **Pruning Completed Worktree Dependencies Before Build Waves:**
  During multi-agent campaigns on disk-constrained hosts, upstream audit tasks (e.g. backend code audits, baseline verification) leave behind multi-gigabyte worktrees and temporary dependencies. Once an upstream audit task completes and its report/evidence is verified, snapshot minimal dependency metadata (`.modules.yaml`) to the evidence folder and immediately purge `node_modules` from the completed task's workspace (`rm -rf node_modules`). This frees critical gigabytes of disk headroom before downstream build, Playwright, or container tasks run, preventing disk full aborts during heavy compilation waves.
- **Create Staging Working Copy:** Snapshot production source into a dedicated staging directory:
  `rsync -a --exclude '.venv' --exclude '.git' --exclude 'data' --exclude '.env' <prod_path>/ <staging_path>/`
- **Explicit Path Rule in Task Prompts:** Prepend the staging working copy path as the mandatory edit target in every task brief:
  `TARGET: <staging_working_copy_path> (Production is STRICTLY READ-ONLY reference)`.
- **Immediate Steering Protocol:** If tasks are dispatched referencing production paths, immediately post `kanban_comment` to running workers redirecting them to staging, and bulk-update pending tasks via `hermes kanban edit <id> --body ...` before workers claim them.
- **Parallel Staging Port Parameterization & Loopback Guard Widening:**
  When configuring a staging instance to run alongside production on the same host, parameterize app ports, mock/provider ports, and test database URLs (e.g. `APP_PORT`, `PROVIDER_PORT`, `TEST_DATABASE_URL`). Crucially: audit internal route guards, pairing handlers, or demo authentication gates. If application guards enforce hardcoded literal origin/host strings (e.g. `origin === "http://127.0.0.1:3100"`), widen the check to general loopback host semantics (`new URL(origin).hostname in {"127.0.0.1", "localhost", "::1"}`) rather than an exact port number. This preserves the local-only security boundary while allowing parallel staging instances to boot and pass end-to-end tests without binding production ports or throwing false-positive 404s/403s.
- **Next.js App Router Transport Socket Invisibility & Reverse Proxy Host Rewrites:**
  In Next.js App Router (Next 16+), `NextRequest` wraps the Node incoming request and intentionally strips transport socket metadata (`hasIp: false`, socket peer address symbol not exposed). `x-forwarded-for` is injected or forwarded by upstream proxies and can be spoofed if untrusted. Consequently, an application-level route handler cannot observe the raw client transport/socket IP. Furthermore, reverse proxies (Nginx / Cloudflare Tunnel) frequently rewrite `proxy_set_header Host 127.0.0.1:<port>`, meaning public external requests will satisfy naive `Host === "127.0.0.1"` checks inside the application.
- **Multi-Layer Fail-Closed Local & Demo Surface Guarding:**
  Any demo or debug route (e.g. `/demo`, `/auth/demo`) that mints authenticated sessions must NEVER rely on a single guard term like a loopback adapter flag or Host header check. Video launchers and local adapter flags (`LOCAL_ADAPTER=1`, `--video`) are often executed in production, making them insecure proxies for authorization. Enforce defense-in-depth across 4 independent layers:
  1. *Explicit operator opt-in:* Require an independent, deliberate switch (e.g. `DEMO_MODE=1` or `--demo`) that is never inferred from general recording or video flags (`--video`).
  2. *Reverse proxy detection:* Reject requests carrying proxy-injected headers (e.g. `x-real-ip` or foreign `x-forwarded-host`/`x-forwarded-proto`) when routes are restricted to direct loopback callers, provided the ingress sets them unconditionally.
  3. *Production environment backstop:* In `NODE_ENV=production`, unconditionally return 404 on demo/sample surfaces unless an explicit public override (`ALLOW_PUBLIC_DEMO=1`) is set. This backstop does not depend on proxy header invariants.
  4. *Unified gate contract:* Consolidate the evaluation into a single server module (e.g. `demoSurfaceAllowed()`) invoked across all route handlers and server components to prevent boundary drift.
- **Scoped Process Teardown (Never Naked pkill on Shared VPS Hosts):**
  Never use broad pattern-based kills (`pkill -f <script_name>`) during test harness cleanup or service teardown. In multi-tenant environments or hosts where staging and production run identical framework scripts (e.g. `node scripts/demo.mjs`), a generic `pkill -f` terminates the supervisor-managed production process as well, triggering service restarts or temporary outages. Always scope teardowns strictly:
  1. Record the spawned process PID at launch (`$! > harness.pid`) and kill only that specific PID (`kill $(cat harness.pid)`).
  2. Kill by isolated bound port (`fuser -k <staging_port>/tcp` or `lsof -ti :<staging_port> | xargs kill`).
  3. If process filtering is required, verify working directory before killing (`pgrep -f <name> | xargs -I{} pwdx {}` and filter for staging/test paths).
- **Pre-Audit Baseline Lint & Dead Code Check on Hotfixed Revisions:**
  When freezing a live instance that contains emergency uncommitted patches or hotfixes, run `lint` and `typecheck` on the frozen branch immediately before dispatching audit workers. Emergency fixes often delete conditional branches but leave behind unused variables and dead database/network calls (`const x = await readSync(...)`). Unused variables cause strict CI linters (e.g. `--max-warnings=0`) to fail, and extraneous I/O calls skew baseline benchmarks. Triage and cleanly excise dead hotfix debris in an initial infra/harness commit so baseline verification suites test real logic rather than crashing on lint warnings.

### 3. Kanban Task Creation & DAG Validation
When calling `kanban_create`:
- **Title (REQUIRED):** `title` is mandatory on every call; omitting `title` causes an immediate kernel error.
- **Parent ID Verification:** Always verify parent IDs exist before passing `parents=[...]`. Passing nonexistent or mistyped IDs aborts task creation with `unknown parent task(s)`.
- **Workspace:** Use `workspace_kind="scratch"` (or `workspace_kind="dir"` pointing to staging), never to production.
- **Dependency Sequencing:** Structure waves cleanly: Wave 0 (Test isolation/harness) -> Wave A/B/C (Backend/Services/DB) -> Wave D (Frontend overhaul) -> Independent Verification (Functional, Security, Visual) -> Wave R3 (Delta Close-Out) -> Gated Deployment Window -> Final Synthesis.
- **Dynamic Link Immutability on Running Tasks (Cannot Link to Running Child):**
  In Hermes Kanban, `kanban_link` strictly refuses adding parent edges to tasks whose status is already `running` (`cannot link: child is already running`). If an unexpected prerequisite task or urgent test-infra fix is identified after a downstream worker has already been dispatched and entered `running`, do not attempt to retroactively gate the running worker via `kanban_link`. Instead:
  1. Post an immediate directive `kanban_comment` to the running worker explaining the situation (e.g. instructing it to cherry-pick the fix commit into its local workspace, or to classify failing tests on the unpatched surface as environment-limited rather than product defects).
  2. Gate subsequent *unstarted* tasks (in `todo` or `ready`) to the new fix task via `kanban_link`.
- **Multi-Board Context Discipline:**
  When operating on a dedicated campaign board, always specify `--board <slug>` on every CLI command or `board="<slug>"` on native tool calls. Unscoped commands fall back to the environment-default or symlinked board, resulting in phantom task lookup errors or links across disjoint boards.
- **Kanban CLI Lock Contention under High Dispatcher Load:**
  During concurrent dispatcher polling, worker heartbeats, and rapid status transitions, CLI operations (`hermes kanban edit` / `hermes kanban comment`) can encounter SQLite database lock contention and hang or terminate with SIGINT. Prefer native agent tool calls (`kanban_comment`) over shell CLI commands for agent-to-worker steering, and convey spec adjustments or constraints via comments on running tasks rather than repeatedly attempting blocking CLI edits on task definitions.
- **Same-Profile & Overlapping-File Serialization:** If multiple tasks share the same assignee profile (e.g. `forge`) or modify overlapping service/logic files in the staging copy, do NOT leave them unlinked as parallel ready tasks. The dispatcher will spawn them concurrently, leading to file write collisions and race conditions. Always link them sequentially (`parent -> child` via `kanban_link`) so they run in orderly succession. If parallel workers are spawned accidentally on overlapping files, immediately reclaim subsequent tasks (`hermes kanban reclaim <id>`), terminate their worker processes, and apply `kanban_link`.
- **Wave 0 Test Isolation Gate Invariant:** Any multi-agent implementation wave that relies on regression testing must be gated by a dedicated Wave 0 task. Wave 0 must establish a centralized `conftest.py` that enforces: (1) pre-import environment redirection of database and asset URLs to temporary locations, (2) patching of all import-time database singletons across all app modules and route handlers (preventing cross-datastore leaks to live DB), and (3) hard outbound socket/network blocking so tests never hit live third-party vendor APIs or read live production databases.

### 4. Mid-Flight Steering, Timeout & Retry Exhaustion Protocol
- **Steer Active Workers:** Use `kanban_comment` on running tasks to issue course corrections (e.g. redirected paths, updated constraints). Workers read comments during execution. In CLI commands, note that `hermes kanban comment <id> <text>` takes message text as a positional argument (not `--body`). Prefer the native `kanban_comment` tool inside agent sessions.
- **Disk-First Evidence Delivery:** Instruct workers to write heavy reports, logs, and screenshots directly to a designated evidence directory (`/root/fleet-evidence/<campaign>/...`) with SHA-256 manifests, keeping Kanban task metadata and summaries lightweight.
- **Attachment Upload Timeout Guard:** Heavy tasks often finish their reports and files on disk but time out while uploading large attachments via `kanban_attach` or `kanban_complete`.
- **Steering Retries:** When the dispatcher retries a timed-out task, inspect disk first. If the report or code is already complete, immediately post a steering comment via `kanban_comment` instructing the retry worker to verify existing disk artifacts and complete directly without re-running work from scratch.
- **Timeout from Over-Hardening vs Re-Execution Waste:**
  When an autonomous specialist times out near the deadline after producing an executable script, audit report, or test suite that already passed its primary acceptance criteria (e.g. continuing indefinitely through extended sabotage suites or deep property runs), steer the retry worker with an explicit inventory of on-disk verified deliverables. Forbid repeating completed test suites from scratch, and instruct the worker to append the missing resolution/receipt note and call `kanban_complete` immediately. Prevent retry workers from repeating multi-hour benchmark or fuzzing pipelines when verified evidence is already present on disk.
- **Closure-Phase Timeout Protocol (Evidence-on-Disk Steering Invariant):**
  When a specialist times out near or at its runtime limit (e.g. 10800s) during heavy implementation or verification waves, immediately inspect the workspace and evidence directories before re-running anything. If git commits are committed and working tree is clean, unit/e2e test suites are already passed in on-disk logs, and gate files exist, the worker timed out strictly during report synthesis or final completion handoff. Immediately steer the retry worker via `kanban_comment`: supply the exact verified git HEAD SHA, gate log filenames, and test pass counts; forbid repeating the long test suites or rebuilds for ceremony; and direct the worker to bind the verified disk artifacts, update the report header, and call `kanban_complete`.
- **Exhausted Retries Rescue Protocol:** When a task reaches `gave up (retries exhausted)` / `blocked`, inspect disk artifacts before re-creating or decomposing the task. If code edits and verification evidence JSON are already committed and verified on disk/staging (the worker merely timed out formatting prose or uploading attachments):
  1. Call `kanban_unblock(task_id)` to clear the blocked status.
  2. Post an immediate directive comment via `kanban_comment`: confirm that implementations and tests are verified, forbid re-running measurements/edits, and instruct the worker to compile the concise summary report and call `kanban_complete`.

### 5. Independent Verification & Delta Close-Out Gate (Wave R3)
- **Separation of Duties:** Implementers (FORGE, FRAME) cannot be the sole verifiers of their own work. Independent specialists (PRISM for functional/data, SENTINEL for security exploits, LENS for UI/a11y) must assess the frozen staging revision independently.
- **Adversarial Falsification Directive ("Falsify, Do Not Concur"):**
  When commissioning an independent verifier (e.g. SENTINEL auditing a backup tool or PRISM auditing data integrity), explicitly mandate: *"falsify, do not concur"*. Implementers frequently suffer confirmation bias and author test harnesses that yield false PASSes (e.g. verifying table row counts and content hashes while silently omitting RLS policies, trigger catalogs, or failing to test URI percent-encoding bypasses). The independent verifier must specifically hunt for structural catalog omissions, security boundary leaks, and negative-control weaknesses (proving that the harness genuinely trips when objects are omitted or corrupted) before certifying any tool or fix.
- **Delta Remediation Wave Before Deploy:** Independent verifiers frequently uncover actionable integration deltas (missing routes, timing oracles, console errors, touch-target sub-thresholds). Never deploy to production with unresolved verifier findings.
- **Chain Delta Gate:** Insert an explicit Delta Close-Out Wave (Wave R3):
  1. Backend Delta Task (FORGE) + Frontend Delta Task (FRAME).
  2. Independent Delta Verification Gate Task (PRISM) that validates all delta fixes against a frozen revision manifest hash.
  3. Gate the production deployment task strictly on the delta verification task passing (`parent = delta_verification_task_id`).

### 6. Database Backup & Disaster Recovery Standards (SQLite & PostgreSQL)
- **Never use `cp` on active SQLite WAL databases:** A raw file copy misses uncheckpointed WAL frames and risks a torn page copy during concurrent writes. Always use `sqlite3 file:<db>?mode=ro ".backup <dest>"` to execute an atomic, WAL-checkpointed backup.
- **PostgreSQL Custom-Format (`-Fc`) Table Data Ordering & TOC Hoisting:**
  Never assume `pg_restore` automatically resolves data dependency order in custom archives (`pg_dump -Fc`). While `pg_restore` reorders schema DDL items, it restores `TABLE DATA` entries in strict alphabetical order. If table A has a CHECK constraint or validation trigger depending on rows in table B, and table B sorts alphabetically after table A (e.g. `board_packages` vs `pn_private.sync_schemas`), a plain `pg_restore --exit-on-error` fails with a constraint violation. Always extract the archive TOC (`pg_restore -l <dump> > toc.list`), hoist the validator table's `TABLE DATA` entry ahead of the dependent table in the list, and restore using `pg_restore -L <ordered_toc>`. For plain-text SQL dumps, hoist the validator's COPY chunks ahead of dependent data chunks and execute under `psql --single-transaction` so constraint evaluation succeeds.
- **TOC Desynchronization Hazard on Safety Rollback Dumps (Cross-Archive `--use-list`):**
  Never apply an ordered TOC list derived from a forward target dump to a pre-restore safety dump. Archive TOC entry IDs are assigned sequentially per `pg_dump` invocation and differ between dumps. Supplying archive A's TOC list to archive B's restore causes `pg_restore: error: could not find entry for ID <N>`. Every rollback restore must derive, hoist, and apply its `--use-list` TOC specifically from the safety archive itself.
- **Automated Round-Trip Verification Receipt, Content-Parity Hashing & Structural Security Checks:**
  A backup script or runbook is incomplete without an automated round-trip verification drill into a throwaway cluster. Assert row-count equality across 100% of tables and row-by-row content parity hashing (order-independent multiset hash) to detect silent row corruption or missing values. Crucially: row counts and content hashes alone can produce a **false PASS** if structural security objects are lost. Verification must explicitly compare structural catalogs (`pg_tables`, `pg_policy`, `pg_trigger`, `pg_indexes`) against the source database: fail closed if Row Level Security (`ENABLE ROW LEVEL SECURITY`) or security policies are missing, and verify index health via `amcheck` (`--heapallindexed`). Include an explicit negative control (tamper sabotage test) demonstrating that the harness fails when data is corrupted or rows are missing. Output must be saved to a dated verification receipt (`backup-restore-verify-<timestamp>.log`). Never clear a pre-deploy or baseline backup gate without an inspectable round-trip receipt.
- **Fail-Closed Target Database Guards (Libpq URI Percent-Decoding & Service Aliases):**
  When guarding destructive restore operations (e.g. `--allow-prod` gates to prevent overwriting production databases), never rely on raw substring matching on the connection URI (e.g. `case "$url" in *prod_db*)`). Libpq automatically percent-decodes URI paths (allowing `postgresql://.../%70rod_db` to bypass string filters while connecting to `prod_db`), and connection strings using `service=<alias>` resolve out-of-band via `pg_service.conf` with no database name in the URI. Always resolve the destination database name directly through libpq (`psql "$target" -t -A -c 'SELECT current_database()'`) or percent-decode URIs and resolve service definitions before checking production authorization gates.
- **Safety Dump Location & Scratch Hygiene:**
  Dry-run restore drills and throwaway test runs must never write safety dumps into versioned or baseline directories under production database names. They should write to isolated temporary directories (`mktemp -d`) and clean up immediately upon exit.
- **Dual-Location Redundancy:** Store automated backups across at least two physically distinct block devices or filesystem mounts (e.g. root filesystem `/var/backups/...` and secondary storage `/mnt/...`), verifying byte-identical SHA-256 checksums.
- **Fail-Closed Restore Drill:** Verify backup usability by restoring to an isolated directory and booting the application on a temporary port with external payment and vendor APIs mocked or disabled, confirming `/api/health` and database integrity (`PRAGMA integrity_check` or PostgreSQL amcheck) without triggering external mutations.

### 7. Gated Production Deployment Window & Service Hardening
Code changes reach production ONLY via a dedicated deployment task (owned by ATLAS):
1. **Pre-Deploy Database Backup & Integrity Check:** `sqlite3 <db> ".backup <backup_path>"` + SHA-256 hash + `PRAGMA integrity_check;`.
2. **Data Reconciliation & Idempotent Migrations:** Run reconciliation scripts before deploying new code schemas. Verify balance/order invariants (e.g. total debits == total credits, delta = 0) fail-closed.
3. **Controlled Transfer:** Copy staging code to production using `rsync` with strict excludes:
   `rsync -a --exclude '.env' --exclude 'data/' --exclude '.venv/' --exclude '.git/' --exclude '__pycache__/' --exclude '.pytest_cache/' <staging_path>/ <prod_path>/`
4. **Environment & Secrets Hardening:** Update `.env` (enforcing `chmod 600`) and ensure no default fallback secrets exist (fail-fast on startup if secrets are missing).
5. **Least-Privilege Systemd Hardening:** Migrate service units from root to a dedicated unprivileged user (`User=<user>`, `Group=<group>`). Enforce sandboxing: `ProtectSystem=strict`, `ProtectHome=true`, `PrivateTmp=true`, `NoNewPrivileges=true`, and explicit `ReadWritePaths=`. Audit security score with `systemd-analyze security <service>` (target <2.0 OK).
6. **Framework Build Invalidation Invariant (Next.js / Vite / Nuxt):**
   A service or supervisor restart alone does NOT deploy new code or roll back changes if the build output directory (`.next/BUILD_ID`, `dist/`) is present, because framework boot scripts skip recompilation when markers exist. Production deployment and rollback runbooks must explicitly purge build output (`rm -rf .next`), recompile, and assert that the new build marker (`BUILD_ID`) differs from the pre-deployment marker before restarting the supervisor or service unit.
7. **Restart & Automated Smoke Testing:** Restart service, verify `health` endpoint, check error handling on tampered requests, and confirm restart counters (`NRestarts=0`).
8. **Executable Rollback Script:** Always author and test `ROLLBACK_<campaign>.sh` before closing the deployment task.

### 8. Live DOM Fold & Visual Invariant Measurement via CDP
- When validating mobile UI above-the-fold invariants (e.g. service tiles visible without scrolling, ratio <= 0.45):
  1. Emulate viewport via CDP: `cdp('Emulation.setDeviceMetricsOverride', width=390, height=844, deviceScaleFactor=1, mobile=True)`.
  2. Reset scroll: `js("window.scrollTo(0,0)")`.
  3. Measure live bounding client rects: `const r = el.getBoundingClientRect(); const ratio = r.top / window.innerHeight;`.
  4. Verify overflow: `document.documentElement.scrollWidth <= document.documentElement.clientWidth`.
  5. Clear emulation: `cdp('Emulation.clearDeviceMetricsOverride')`.
- **Deterministic DOM Probe Fallback When Multimodal Vision Times Out:**
  When multimodal vision tools or local vision servers time out on large full-page renders, never block the pipeline or substitute unverified prose: fall back to deterministic DOM/computed-style probes via Playwright or CDP:
  1. Assert design typography tokens: `window.getComputedStyle(el).fontFamily.includes(...)`.
  2. Compute mathematical relative luminance contrast on computed foreground/background colors against WCAG AA (4.5:1).
  3. Assert minimum interactive touch targets: `el.getBoundingClientRect().height >= 44 && el.getBoundingClientRect().width >= 44`.
  4. Assert zero document overflow: `document.documentElement.scrollWidth <= document.documentElement.clientWidth`.
  Deliver the rendered HTML visual dossier or screenshots directly to the user for human review while certifying contract adherence programmatically.

### 9. Mandatory Turn Release (Anti-Polling Invariant)
- **Zero Sleep Loop:** Never run `sleep` loops or while-loops in terminal waiting for task completion.
- **Native Wake:** Hermes automatically subscribes the creator session via `delivery_mode="notify+wake"`. Conclude your turn immediately after dispatching; the gateway will natively wake ORION when workers finish (`completed` / `blocked`).
