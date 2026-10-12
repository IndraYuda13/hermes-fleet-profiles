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
- When execution tools or process sandboxes wedge and require peer delegation across A2A.

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
7. **Orchestrator Steering Retry Protocol (Adopt In-Flight Artifacts vs Redo):**
   When a worker times out and dispatcher spawns run #2, the spawned session starts fresh with zero conversational memory of run #1 (`kanban_resume_guard`). Without immediate guidance, the retry worker risks restarting from scratch—re-running long exploration suites, re-scaffolding, or getting confused by uncommitted working-tree files.
   Upon detecting run #2 active after a timeout, the orchestrator must immediately:
   a. **Audit disk state:** Check `git log -1`, `git status --short`, and existing probe JSONs/reports in the evidence directory.
   b. **Post a structured steering comment (`kanban_comment`):**
      - **Artifact Inventory:** List verified commit SHAs, passed/failed test artifacts, and pre-authored reports already on disk.
      - **Do-Not-Redo Invariant:** Explicitly forbid restarting analysis from scratch, re-running redundant suites, or revisiting passing sub-scopes.
      - **Remaining Delta Scope:** Pin down the exact uncommitted delta, failing assertion, or remaining edge case.
      - **Handoff Contract:** Direct the worker to verify the delta, commit, update the report, attach deliverables, and invoke `kanban_complete`.

### 4. Event-Driven Wake Subscriptions vs Busy-Waiting
For long-running autonomous worker pipelines:
1. **Subscribe to Task Completion Notifications:** Use `hermes kanban notify-subscribe --platform telegram --chat-id "<chat_id>" --chat-type dm --notifier-profile <profile> --delivery-mode notify+wake <task_id>` when launching long tasks.
2. **Release Turn Immediately:** Trigger dispatch (`hermes kanban dispatch`) and end the turn immediately. Do not execute synthetic polling or busy-wait loops; the runtime automatically wakes the session upon task completion or failure.

### 5. Parallel Independent Verifiers & Asymmetric Completion Gate
When dispatching parallel verifiers (e.g., functional verification by PRISM, security audit by SENTINEL, visual QA by LENS) against an implementer's frozen commit SHA:
1. **Asymmetric Completion & Turn Yield:** Parallel verifiers complete at different times. When the first verifier reports `VERIFIED`, inspect its report, verify sibling status (`kanban show <sibling_id>`), and NEVER unlock the next phase or claim completion while any sibling verifier remains in flight. State partial status and yield the turn cleanly.
2. **Database Contention Guard:** When verifiers execute parallel suites against a live database instance (PostgreSQL), run tests on distinct database names or isolated schemas/transaction rollbacks to prevent false-positive concurrency failures.
3. **Scratch Directory Vitest Scope Guard:** Verifiers creating probe tests in scratch directories (`/root/.hermes/profiles/<role>/cache/scratch/`) hit runner failures if `vitest` config restricts includes to `tests/**/*.test.ts`. Execute probes via `node ./node_modules/.bin/tsx <script>` or pass `--config <scratch_config>`.

### 6. Split Verdict Triage (VERIFIED vs REVISE)
When one verifier issues `VERIFIED` and a sibling issues `REVISE`:
1. **Preserve Validated Evidence:** Retain passing verifier results; do not discard them.
2. **Isolate Concrete Defect Ledger:** Extract the exact list of blocking defects and acceptance criteria from the revising verifier.
3. **Dispatch Targeted Remediation:** Assign a remediation task back to the original implementer referencing ONLY the failing items and the original commit SHA.
4. **Lock Remediated SHA & Targeted Re-Verification:** Once the implementer commits the fix, capture the new commit SHA and dispatch a re-verification card specifically to the verifier that flagged the issue. If shared contracts changed, re-run all verifiers. Advance to downstream stages only upon unanimous approval.

### 7. Worker Isolation & Context Injection (Anti-Memory-Leak Invariant)
Every Kanban worker dispatch executes as an independent, fresh process (`hermes -p <assignee> chat -q "work kanban task ..."`) without conversational history from prior tasks or sibling runs (`kanban_resume_guard` enforces isolation and rejects worker transcript resumption):
1. **Explicit Context Ingress via `kanban_show`:** Workers only know what `kanban_show()` provides in `worker_context` (task title, body, comments, attachments, prior attempts, and handoff summaries from completed parent cards).
2. **Context Propagation via Parent Handoffs:** When a downstream task depends on decisions, endpoints, or code written by a previous worker, link the prior task via `parents=[parent_id]`. The parent's `kanban_complete` summary and metadata are automatically passed to the child.
3. **Decoupled Sibling Synchronization:** Parallel workers cannot inspect sibling cards. When two tasks share an API route, database schema, or file format, the orchestrator must freeze the contract up front and stamp it into both card specifications.
4. **Goal-Mode Exception for Multi-Turn Continuity:** When an autonomous task requires iterative turns in the SAME session until completion criteria are met, set `goal_mode: true` (`--goal`) so the aux judge continues the loop within that single worker session.

### 8. Verification Probe Calibration & Headless Emulation Guardrails
When orchestrators or verifiers build deterministic probes to verify implementer handoffs:
1. **Semantic DOM Inspection vs Raw Markup Equality:** Never assert raw serialized HTML/SVG strings (`elem.outerHTML === expected`). Browsers and DOM parsers normalize attribute order, whitespace, and self-closing tags. Compare semantic DOM structures instead: count of specific child tags (e.g. `<path>` count, absence of `<circle>` fallback icons), `viewBox`, or computed dimensions.
2. **Component Geometry Calibration:** Calibrate numeric assertions against actual component specifications before failing a worker. E.g., single-chevron icons contain 1 `<path>`, while double-chevrons contain 2 `<path>`. An assertion requiring `len(paths) >= 2` on a single-chevron is mis-calibrated and derails workers into debugging the probe rather than the product.
3. **Headless Pseudo-State Emulation:** In headless Playwright/Puppeteer audits, CSS pseudo-classes (`:hover`, `:focus-visible`) cannot be measured via passive computed styles. The test must explicitly dispatch pointer events (`page.hover(selector)`) or toggle state emulation; otherwise, the probe falsely reports unapplied hover transitions.
4. **Reduced-Motion Transition Neutralization:** When verifying `prefers-reduced-motion: reduce`, verify both `animation: none` and `transition: none` (or `transition-duration: 0.01ms`) across interactive overlays and drawers to prevent false transition leaks.

### 9. Autonomous Execution Relay & Verbatim Evidence Handoff (Tool-Failure Fallback)
When an autonomous worker or orchestrator requires runtime command execution but lacks an execution tool or encounters an unrecoverable runner/tool lifecycle failure (e.g. process-capture cleanup wedges, ESRCH, non-retryable sandbox failure):
1. **Zero-Guessing Invariant:** Never substitute fabricated output or soften failing assertions into optimistic prose when an execution tool fails. A tool failure requires an alternative execution channel, not imagined success.
2. **A2A Peer Discovery & Delegation:** Discover live fleet peers over A2A (`a2a_discover` on local loopback ports) and delegate the exact, unmodified command to an idle capable peer (e.g. ATLAS, FORGE) via `a2a_call`.
3. **Bounded Execution & Durable Logging:** Enforce strict workspace boundaries in the delegation brief. Require the executing peer to:
   - Record pre-run target script and artifact SHA-256 digests and pre-state directory listings (`ls -la --time-style=full-iso`).
   - Execute the exact command while piping/teeing stdout to a durable log file in the evidence directory (`set -o pipefail; <cmd> 2>&1 | tee <log_file>; echo "exit=${PIPESTATUS[0]}"`).
   - Capture post-run directory listings to isolate freshly written deliverables from stale historical run artifacts.
4. **Kanban Provenance Breadcrumb:** Record a durable comment (`kanban_comment`) on the active task card documenting the delegation rationale, executing peer, script SHAs, exit code, and on-disk log paths so auditability is preserved.
5. **Verbatim Relay:** Relay the full raw stdout/JSON and exit status back to the requesting agent or caller without truncation, editorial filtering, or sugarcoating failed assertion lists.
6. **Transport Buffering & Compact Readbacks:** A2A transport channels truncate or corrupt large message payloads. Never request or stream bulk multi-kilobyte stdout/log dumps across A2A message bodies. Require the executing peer to write full output to disk in the evidence directory, and query compact, line-oriented slices (e.g. bounded `read_file` offsets, selective line searches, line counts, key=value digests) referencing file path and SHA-256.
7. **Concurrency & In-Flight Writer Quiescence:** Before executing a relayed run or inspecting evidence, check active host processes (`ps -eo args | grep <script> | grep -v grep | wc -l`) and relative timestamps (`stat -c '%y'`). If `BUSY >= 1`, do not launch a concurrent duplicate run (which corrupts output files and screenshots) and do not read intermediate reports. Furthermore, verify **quiescence** of the target scripts and artifacts: sample their SHA-256 hashes twice, spaced >=45s apart. If hashes are changing, the requesting worker is still editing mid-flight—abort with `ARTIFACT_STILL_MUTATING` rather than executing against moving bytes. A run during which inputs mutate is strictly VOID.
8. **A2A Transport Timeout Non-Cancellation Guard:** When delegating execution over A2A, transport timeouts (`[agent did not reply in time]`) only close the transport socket; they do NOT cancel the executing peer's process. Never chain a fallback delegation to a second peer immediately without checking if the first peer is still executing (`pgrep`, active logs). Chaining blindly creates colliding concurrent runs that invalidate each other's outputs.
9. **Target Card Status Gate (Superseded Relay Deduplication):** Before running an expensive inbound test request, check the target task's Kanban status (`kanban_show`). If the card was already completed (`status: done`) and certified by the worker's own subsequent run or existing on-disk reports, do not execute duplicate runs. Extract and report the bound evidence and log paths immediately.
10. **Post-Run Disk Overwrite & Hash Reconciliation:** When an implementer completes a task but mutates files post-run (e.g. touch-ups or cleanup after the certified test), the card's completion metadata may cite a dead hash that no longer matches disk. The orchestrator must audit disk hashes against completion metadata, record both revisions in a durable card comment (`kanban_comment`), and notify downstream consumers (e.g. FRAME/LENS) which exact revision is on disk versus certified.


## Pitfalls & Defensive Rules

- **Assuming cross-task conversational memory:** Every Kanban dispatch spawns a fresh worker session with no transcript memory of earlier tasks or sibling runs. Never expect a worker to remember prior chat discussions or unlinked tasks; pass all necessary context explicitly via card body, attachments, comments, or parent handoffs (`parents=[...]`).
- **Unguided retry worker restarting from scratch:** When a task times out and restarts in run #2, the worker has no memory of run #1's reasoning. Failing to post an immediate artifact inventory and delta scope leads the worker to wipe or re-do 80% of already-completed work. Always post an immediate steering comment with the disk inventory.
- **Fabricating output or halting when local process runners wedge:** When a container or process-capture runner hits an unrecoverable cleanup/lifecycle error, guessing output breaches evidence integrity. Delegate execution to an idle fleet peer via A2A and relay verbatim stdout.
- **Streaming bulk raw logs over A2A payloads:** Multi-KB logs or test outputs exceed message buffers and get truncated or mangled by agent-to-agent transports. Direct peers to write full output to a durable log file on disk and return compact digests with file paths and SHA-256.
- **Reading evidence from an active writer or unquiesced directory:** Reading stdout or JSON reports while a test runner process is still active (`BUSY >= 1`) captures partial files, incomplete summary fields, or stale output from prior runs. Verify process termination (`BUSY == 0`) and compare timestamps before certifying results.
- **Launching concurrent execution runs on shared evidence workspaces:** Re-running a probe or build script while another instance is still running in the same directory causes race conditions on output files, screenshot clobbering, and invalid test hashes.
- **Treating A2A transport timeouts as peer cancellations:** An A2A socket timeout (`agent did not reply in time`) leaves the remote peer's process running. Spawning a fallback peer immediately clobbers the shared evidence directory with concurrent executions.
- **Executing test relays while the authoring worker is still writing:** Running a probe while the requesting worker is actively saving edits results in mid-run hash mismatches, timeout crashes on deleted selectors, and void evidence. Require double-hash quiescence before executing.
- **Unreconciled post-completion file overwrites:** When workers touch or modify files after producing certified test reports, card completion hashes become stale relative to disk, breaking downstream verifier DAGs. Audit and comment the hash delta immediately.
- **Mis-calibrated orchestrator/verifier probes:** Failing implementers with probes asserting raw serialized markup equality or wrong glyph path counts derails workers into diagnosing the probe instead of shipping the deliverable. Always validate probe assertions against known-good baselines.
- **Uncoordinated sibling assumptions:** Parallel sibling cards cannot see each other's execution or decisions. The orchestrator must stamp shared schemas, formats, and conventions into all sibling card bodies before fan-out.
- **Do not cancel tasks during active dispatcher retries.** Terminating a task that timed out while its spawned retry is compiling creates orphaned processes and lost progress.
- **Do not permit implementers to certify their own deliverables.** An implementer claiming tests pass does not replace an independent verification pass against the frozen commit SHA.
- **Never design UI against unverified backend contracts.** Frontend implementations built against hypothetical schemas require costly refactoring once backend realities diverge.
- **Do not poll status in tight loops.** Rely on platform notification webhooks and wake events (`notify+wake`) rather than issuing repetitive heartbeat or status calls.
- **Supply compliant production credentials when testing Next.js servers locally:** `next start` forces `NODE_ENV=production`. If schemas strictly validate production secrets (e.g. `SESSION_SECRET`, `GOOGLE_CLIENT_ID`), verification runners must pass compliant dummy secrets to prevent immediate exit crashes during local E2E or visual audits. Ensure port 3000 is clean of dangling previous processes before starting.
- **Never invoke virtual environments or binaries outside the current repository/profile:** Calling external Python binaries or virtualenvs from unrelated host paths (e.g. other project dirs) triggers command execution security filters, wastes turn budget, and causes timeouts. Use the active project venv or system binaries.

## Lifecycle Verification Checklist

- [ ] Sibling task contracts and shared schemas stamped into card bodies before fan-out.
- [ ] Downstream worker context passed via parent links (`parents=[...]`) rather than assuming conversational memory.
- [ ] Upstream backend and worker services tested and verified before UI dispatch.
- [ ] Implementer card closed and Git commit SHA recorded before review dispatch.
- [ ] Workspace inspected for tangible progress upon task timeout notification.
- [ ] Independent verifier cards dispatched in isolated execution lanes.
- [ ] All final verification reports reference the exact same Git commit SHA.
- [ ] When execution is delegated to a peer, provenance comment logged on task card and raw stdout retained verbatim on disk.
