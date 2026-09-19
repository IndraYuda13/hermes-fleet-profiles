---
name: fleet-runtime-containment-and-recovery
description: Use when containing P0 runtime services or rescuing tasks.
version: 1.2.0
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

## 3. Kanban Timeout & Retries Exhausted Recovery (Sealed Commit Rescue)
When a worker completes implementation and commits the fix to git, but times out during handoff/packaging:
- The dispatcher marks the task `gave up (retries exhausted), timed out` and moves it to `status: blocked`.
- **The Duplication Trap**: Blindly decomposing or recreating the task from scratch wastes agent compute, duplicates tickets, and risks discarding working commits already sealed in git.
- **Protocol**:
  1. Inspect Git status, log, and worktree in the target workspace (`git status --short`, `git log -1 --stat`).
  2. If a clean, test-passing commit SHA was already sealed before the timeout, unblock the card (`kanban_unblock`).
  3. Instruct the worker (or record the handoff comment) to seal that exact SHA.
  4. Wire downstream verification gates (PRISM functional / SENTINEL security) directly to the recovered commit SHA so independent re-testing proceeds immediately.

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
