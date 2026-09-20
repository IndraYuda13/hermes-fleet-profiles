---
name: fleet-runtime-containment-and-recovery
description: Use when containing P0 runtime services or rescuing tasks.
version: 1.5.0
---

# Runtime Containment on Critical Findings & Sealed Commit Recovery

Use when orchestrating multi-agent engineering workflows where independent verifiers (SENTINEL/PRISM) uncover critical vulnerabilities (P0/P1) on active services, or when tasks hit retry limits during completion.

## 1. P0 Active Runtime Containment Protocol
When an independent security review (SENTINEL) or functional audit identifies an active P0/P1 vulnerability (e.g. arbitrary local file exfiltration, unauthenticated RCE, credential leak) on an actively running system daemon/service:
- **The Exposure Trap**: Dispatching an asynchronous remediation task to FORGE while leaving the vulnerable service listening. If remediation hits worker timeouts or requires multiple turns, the vulnerable root/privileged port remains exposed to callers or other local processes.
- **Protocol**:
  1. Immediately dispatch runtime containment to **ATLAS** (or execute reversible containment such as `systemctl stop <service>`) to close the listener *concurrently with or before* dispatching remediation.
  2. Verify that the listening port is closed and no orphan process remains (`ss -ltnp '( sport = :<port> )'`).
  3. Record clear before/after listener and process status evidence.
  4. Never treat loopback bind (`127.0.0.1`) or "remediation is currently in flight" as an acceptable risk mitigation for an active P0.

## 2. Reverse-Proxy & Edge Tunnel Exposure Trap (Loopback False Security)
- **The Loopback Trap**: Assuming a service is safe from external attack because it is bound strictly to `127.0.0.1:<port>`. An active edge tunnel (e.g., Cloudflare Tunnel `cloudflared`, reverse proxy, or ngrok) may hold an unauthenticated ingress mapping from a public domain directly to that loopback port, exposing unauthenticated routes or credential-backed APIs to the public Internet.
- **Containment Protocol**:
  1. Audit active tunnel ingress rules (`/etc/cloudflared/config*.yml`) and reverse proxy configs before declaring a loopback service isolated.
  2. If unauthenticated public ingress is discovered, immediately stop the local service first to close the exposure window.
  3. Back up the proxy/tunnel config to root-only storage, remove ONLY the offending hostname mapping (preserving all unrelated ingress routes byte-for-byte and keeping terminal 404), validate syntax (`cloudflared tunnel --config ... ingress validate`), and restart the tunnel unit.
  4. **Falsification Gate (External Verification)**: Issue cache-busted HTTPS probes (`curl -ksS ...?probe_id=...`) to the public hostname from outside and inspect the daemon's journal. The probe must return edge 404/denial, and the unique probe query tag must have ZERO occurrences in the daemon access logs.
  5. Only after public non-forwarding is proven with zero journal correlation, restart the loopback service and run local smoke tests.

## 3. Kanban Timeout & Retries Exhausted Recovery (Sealed Commit & Scratch Artifact Rescue)
When a worker completes implementation or authors a large specification/contract, but times out during packaging/attaching:
- The dispatcher marks the task `gave up (retries exhausted), timed out` and moves it to `status: blocked`.
- **The Duplication Trap**: Blindly decomposing or recreating the task from scratch wastes agent compute, duplicates tickets, and risks discarding working commits already sealed in git or fully written markdown artifacts in the task workspace.
- **Protocol for Code Tasks (Sealed Commit Rescue)**:
  1. Inspect Git status, log, and worktree in the target workspace (`git status --short`, `git log -1 --stat`).
  2. If a clean, test-passing commit SHA was already sealed before the timeout, unblock the card (`kanban_unblock`).
  3. Instruct the worker (or record the handoff comment) to seal that exact SHA.
  4. Wire downstream verification gates (PRISM functional / SENTINEL security) directly to the recovered commit SHA so independent re-testing proceeds immediately.
- **Protocol for Authoring/Contract Tasks (Scratch Workspace Artifact Rescue)**:
  1. For tasks writing specifications or contract revisions in scratch workspaces (`workspace_kind: scratch`), inspect `/root/.hermes/kanban/workspaces/<task_id>/`.
  2. Verify if the artifact was already completely written before the timeout: check line count, required sections, and compute `sha256sum <file>`.
  3. Append a durable recovery comment (`kanban_comment`) stating the artifact's exact path, line count, and SHA-256, instructing the worker on retry not to restart research or alter source, but only to verify the file, attach it along with its `.sha256` sidecar, and complete.
  4. Unblock the task (`kanban_unblock`). When the worker resumes, it attaches the existing artifact and completes immediately without burning another 20-minute authoring run.
- **Empty Scratch Workspace on Authoring Timeout (Analysis Paralysis / Scope Bloat Recovery)**:
  - *The Trap*: When an authoring worker (writing complex contracts, specifications, or architecture docs) exhausts retries (`gave up (retries exhausted), timed out` -> `status: blocked`) and inspection reveals an empty scratch workspace (`/root/.hermes/kanban/workspaces/<task_id>/` has 0 files). Orchestrators often either decompose the task into duplicate splinter cards (losing parent linkage and cluttering the board) or blindly unblock without instructions, causing the worker to repeat the identical 30-minute reading/inspection loop and time out again.
  - *Protocol*:
    1. Inspect workspace and task runs to confirm: 0 files written, failure caused by elapsed time (>1800s) during broad inspection or narrative generation.
    2. Do NOT decompose, re-parent, or create new cards. Preserve the existing task ID and its downstream dependency graph.
    3. Post a targeted recovery comment (`kanban_comment`) enforcing execution compression:
       - Explicitly instruct the worker NOT to re-inspect historical inputs or re-read preceding revision documents.
       - Command direct drafting of the deliverable file.
       - Enforce structural conciseness over narrative bloat: prioritize concrete coverage tables, explicit state machines, and test vectors rather than multi-page prose justifications that exhaust context and time limits.
       - Mandate immediate single-command SHA-256 sidecar generation and completion.
    4. Unblock the task (`kanban_unblock`). The worker executes with narrowed focus and delivers within the turn budget.
- **Immediate In-Flight Steering on First Timeout (`dispatcher will retry`)**:
  When a task times out on attempt 1, the dispatcher automatically respawns a retry run with the workspace preserved. Do NOT wait for retries to exhaust (`gave_up`). In that exact wake turn, inspect `/root/.hermes/kanban/workspaces/<task_id>/` or the worktree. If a draft or report exists, immediately inject a steering comment (`kanban_comment`) with the file path, line count, and SHA-256, commanding the active retry run NOT to rewrite from scratch, but to adopt the existing draft, perform only final verification and sidecar generation, attach, and complete.
- **Reviewer Timeout Artifact Rescue & Multi-Timeout Verdict Recovery**:
  When an independent reviewer (PRISM/SENTINEL) completes an audit report in its scratch workspace finding concrete defects (`REVISE` / `BLOCKED`), but repeatedly times out during the uploader/attachment phase:
  1. Inspect the reviewer's workspace file directly to extract the definitive verdict, target artifact SHA, and numbered actionable defects.
  2. Compare attachment byte sizes and hashes against the workspace source to detect truncated attachment fragments (e.g. 600–3,000 bytes vs 9–85 KB in workspace); quarantine fragmented attachments.
  3. If uploader timeouts persist across retries, do NOT enter an infinite unblock loop or restart the 20-minute audit from scratch. Record an authoritative durable **Verdict Manifest** comment on the board (`kanban_comment`) binding the verdict to the exact report hash.
  4. Advance the dependency DAG immediately by creating the downstream remediation task (e.g. `FORGE WP01 R2`) targeting those verified findings, bypassing the reviewer's uploader hang while maintaining 100% audit integrity.

## 4. Worker Bootstrap Crash Recovery (Immutable Skill Pin Trap)
When a worker crashes instantly on spawn with `Error: Unknown skill(s): <skill>` or `Warning: Unknown toolset(s)`:
- **The Immutable Skill Trap**: Task attributes (including `skills: [...]`) are immutable in the Kanban database. When an unavailable, mistyped, or profile-mismatched skill is pinned during card creation, 100% of dispatcher retries will fail at bootstrap before executing a single command. Waiting for retries to exhaust (`gave up (retries exhausted), crashed`) burns time and clutters the board.
- **Protocol**:
  1. Inspect the crash error in `kanban_show`. If the worker exited with `Error: Unknown skill(s)`, do not wait for retries or treat it as an implementation/test failure.
  2. Leave a comment on the failed card documenting the bootstrap failure.
  3. Immediately spawn a replacement task with identical title, body, and workspace, but sanitize `skills: []` (empty array) so the worker loads its profile defaults.
  4. Re-link downstream child tasks or verifier gates to the replacement task ID.

## 5. Multi-Finding Remediation DAG in Shared Directory Workspaces (`workspace_kind: "dir"`)
When an independent audit (SENTINEL/PRISM) yields multiple concurrent findings (e.g. P1 delimiter binding, P2 CORS/error redaction, P2 DNS-rebinding SSRF) targeting the same repository checkout:
- **The Concurrency Collision Trap**: Dispatching multiple findings simultaneously as sibling `ready` tasks in the same shared working directory (`workspace_kind: "dir"`). Concurrent workers in the same checkout cause git index locks, uncommitted working-tree collisions (e.g. multiple workers editing `routes.py`), and test runs mutating shared session state.
- **Protocol**:
  1. Strictly serialize code remediation tasks across shared working trees using parent dependency chaining (`parents: ["<prior_task_id>"]`): Finding 1 (P1) -> Finding 2 (P2) -> Finding 3 (P2).
  2. Only split tasks into parallel branches if they operate in disjoint, orthogonal workspaces (e.g. an infrastructure systemd unit drop-in owned by ATLAS vs Python backend code owned by FORGE).
  3. Every worker in a serialized chain must re-read `git rev-parse HEAD` upon start, stage only explicit files (`git add <file>`, never `git add -A`), and seal its commit before handing off to the child card.
  4. Wire independent re-verification (PRISM/SENTINEL) only to the final consolidated commit SHA after all chained remediations complete.

## 6. Review-Lane Crash & Retries-Exhausted Rescue (Attached Artifact Preservation)
When an implementer finishes work and calls `kanban_request_review`, moving the task to `status: review`, but the designated reviewer worker crashes repeatedly until retries exhaust (`gave up (retries exhausted), crashed` -> `status: blocked`):
- **The Rework / False-Failure Trap**: Treating the task as failed and re-dispatching the implementer from scratch. This discards the finished deliverable, duplicates authoring work, and confuses reviewer execution failure with artifact rejection.
- **Protocol**:
  1. Orient via `kanban_show`: verify whether the implementer successfully attached the deliverable artifact before review was requested, and record its SHA-256 digest from the task attachments.
  2. If the deliverable is intact and only the reviewer run crashed, append a durable comment to the blocked task (`kanban_comment`) documenting that the artifact is preserved at its verified SHA-256 and that review execution failed without a verdict.
  3. Spawn a standalone replacement review task (e.g. assigned to PRISM or an alternate qualified verifier) with a strict, read-only contract: verify the specific attached artifact digest against task acceptance criteria, without repeating implementer discovery or touching runtime.
  4. When the replacement review completes:
     - If approved: record the planning/implementation artifact accepted against its exact SHA-256.
     - If changes are requested (`REVISE`): dispatch a single, serialized revision task back to the original author referencing only the concrete findings (e.g. R-01..R-03), producing a new revision artifact (e.g. `*_R1.md`) bound to a fresh SHA-256 for re-review. Never patch the artifact yourself or bypass the verifier.
