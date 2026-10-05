# Runtime Containment & Sealed Task Recovery

Standard protocols for containing active P0 vulnerabilities, preventing edge tunnel exposure, and recovering blocked Kanban tasks without duplicating work.

## 1. P0 Active Runtime Containment Protocol
When an independent security review (SENTINEL) or audit identifies an active P0/P1 vulnerability (e.g. unauthenticated RCE, arbitrary file exfiltration, credential leak) on an active service:
1. Immediately execute reversible containment (`systemctl stop <service>`) to close the listener before or concurrently with dispatching remediation.
2. Verify listening port is completely closed (`ss -ltnp '( sport = :<port> )'`).
3. Never treat loopback binding (`127.0.0.1`) or "fix is in flight" as acceptable risk mitigation for an active P0.

## 2. Reverse-Proxy & Edge Tunnel Exposure Trap
- **The Loopback Fallacy:** A daemon bound to `127.0.0.1:<port>` is NOT isolated if an edge tunnel (`cloudflared`, ngrok, or reverse proxy) has an unauthenticated public ingress rule mapping to it.
- **Protocol:**
  1. Audit active tunnel ingress rules (`/etc/cloudflared/config*.yml`) and reverse proxy configs.
  2. If exposed, stop the local service immediately.
  3. Back up the tunnel config to root storage, remove ONLY the offending hostname mapping (preserving terminal 404), validate syntax (`cloudflared tunnel ingress validate`), and restart tunnel.
  4. Falsify externally: `curl -ksS ...?probe_id=...` must return edge 404/denial and produce 0 hits in daemon access logs.

## 3. Kanban Timeout & Sealed Commit Recovery
When a task exhausts retries and is marked `gave up (retries exhausted), timed out` -> `status: blocked`:
- **Do Not Recreate Tasks:** Blindly decomposing or recreating the card discards working commits already sealed in Git.
- **Protocol:**
  1. Inspect Git status and log in workspace: `git status --short`, `git log -1 --stat`.
  2. If a clean, test-passing commit SHA was sealed before timeout, call `kanban_unblock` and instruct the worker to seal that exact SHA.
  3. Wire downstream verification gates (PRISM / SENTINEL) directly to the recovered commit SHA.
- **Authoring / Scratch Tasks:** Inspect `/root/.hermes/kanban/workspaces/<task_id>/`. If deliverable was drafted, post a comment with file path, line count, and SHA-256 sidecar, and instruct retry worker to verify and attach rather than restart research.

## 4. Multi-Finding Remediation DAG in Shared Worktrees
When an audit yields multiple concurrent findings targeting the same checkout:
1. Strictly serialize code fixes via parent dependency chaining: Finding 1 -> Finding 2 -> Finding 3.
2. Concurrent workers in the same checkout cause Git index locks and collision.
3. Every worker in the chain must re-read `git rev-parse HEAD`, stage only explicit files (`git add <file>`), and seal before handoff.

## 5. Host Disk Exhaustion & Browser Scratch Reclamation
When root disk space is exhausted (< 2-5 MB free), agents crash on persistence save.
1. Target disposable Chrome user-data directories under `profiles/<profile>/cache/scratch/`.
2. Inspect running Chrome processes (`pgrep -a chrome`) and exclude any directory currently opened by a live PID.
3. Assert path protection: never touch application source, Git worktrees, release trees (`/srv/`), Kanban attachments, or database files.
4. Delete verified inactive scratch dirs until free space reaches >= 1.5-2.0 GB.
5. Inspect `git status --short` in worktree to verify uncommitted edits are intact, then `kanban_unblock`.
