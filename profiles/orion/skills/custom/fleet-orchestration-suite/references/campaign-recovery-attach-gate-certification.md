# Campaign Recovery Patterns — Attach Transport, Gate Interception, Frozen Certification

Distilled from the OTP-R3 UI campaign (12-task DAG, FRAME/FORGE/LENS/PRISM/ATLAS/AURORA, zero failed releases).

## 1. Proactive Attach Assist (pre-timeout intervention on uploader struggle)

**Trigger:** live log/process inspection shows a worker iterating on `kanban_attach` uploads — base64 size mismatches, `content_base64 is not valid base64`, re-reading files to re-encode, `python -m http.server` + SSRF attempts, or re-computing base64 of the same file repeatedly.

**Why it matters:** the attach transport failing is NOT a work failure, but workers burn their entire remaining budget on it and then time out at the finish line (observed on FRAME, FORGE, LENS, ATLAS — 4 of 12 tasks in one campaign).

**Procedure:**
1. Locate the canonical file on disk (worker report dir, not the scratch workspace copy).
2. Compute `sha256sum` and byte size.
3. Attach it yourself:
   `<hermes-venv>/bin/hermes kanban --board <board> attach <task_id> <file> --author orion`
4. Verify byte identity between the disk file and the registered attachment (compare sizes + hashes; note that re-encodings like `.b64.txt` may be identical after decode — check before declaring a truncation).
5. Post a steering comment with the exact attached byte size + SHA and the command: **"JANGAN attach ulang, JANGAN cek ulang; langsung kanban_complete SEKARANG"** plus the exact summary/metadata you expect.

**Note:** base64 bloat is ~33% (18022 B file -> 24032 B b64) — that difference is normal, NOT evidence of corruption. Verify via decode + hash compare, never via size guess.

## 2. REVISE Gate Interception Before Downstream Deploy Spawn

**Trigger:** a verifier returns `REVISE` on a release candidate, and the downstream deploy card's parents are technically `done` (task status does not encode verdict). The dispatcher may auto-promote and spawn the deploy worker before the orchestrator reacts.

**Procedure (intercept at fire time):**
1. Immediately comment on the deploy card with a hard STOP quoting its own contract ("deploy only if both gates SATISFIED; REVISE -> stop"), cite the blocking item and root cause.
2. Verify no production mutation happened (prod git log, file hashes, service state, listening ports).
3. Create remediation card (implementer, priority 100), then a re-verify card gated on it (parents=[remediation]).
4. `kanban_link` both as new parents of the deploy card, then `kanban_unblock` it. With incomplete parents it sits in parent-gated `todo` and self-heals: deploy re-spawns only on a gate-passing revision.
5. Tell the blocked deploy worker to `kanban_block(kind=dependency)` and not to preflight/snapshot/touch anything; it will be re-dispatched when parents complete.

**Invariant:** never let a REVISE verdict coexist with an unblocked deploy lane.

## 3. Independent Certification Run on Frozen Bytes (orchestrator as executor of last resort)

**Trigger:** a verification harness was corrected after its last green run (e.g. probe assert predicate fixed post-certification), so no green evidence exists for the corrected revision. Honest state: "harness has an open calibration fix, unverified" — not a pass.

**Procedure (without racing live writers):**
1. Create an isolated dir; copy ONLY the frozen probe + artifact bytes into it.
2. FIRST verify the probe resolves its subject relative to its own location (e.g. `os.path.join(HERE, 'prototype.html')`). If it uses absolute paths, isolation is invalid — stop and use a different approach.
3. Confirm no other writer runs in the source dir (pgrep for the probe process).
4. Run the single certification run bounded with `timeout <N>`.
5. Freeze stdout + report + pre/post hash manifests into `.frozen/` with distinguished names (`cert_vNN__<hash12>__stdout.txt` etc.).
6. Pre == post hash identity proves no mutation during the run; post the verbatim result + frozen paths to the task card.

**Distinguish from replay:** this is one bounded run of exactly the corrected bytes, not a re-litigation of earlier verdicts. It turns a derived assertion into run-verified evidence.

## 4. Stale Notification Triage

Kanban notifications can arrive after the described event was already handled (worker retried successfully, task completed in a later run). Before acting on any notification:
1. Query the task's actual status + all `task_runs` rows (`status`, `outcome`, `ended_at`).
2. If `done` with a successful run whose `ended_at` postdates the notification's failure: the notification is stale — verify no zombie runs (`status='running'` count = 0) and no live worker process for that task, then take no action.
3. Never re-dispatch, re-comment, or re-create tasks based on a stale notification.
