---
name: fleet-evidence-gate
description: Gate final claims on fresh acceptance evidence.
version: 1.0.0
author: Fleet Upgrade Research
license: MIT
metadata:
  hermes:
    tags: [orchestration, verification, kanban, evidence]
    category: fleet-upgrade
---
# Fleet Evidence Gate

## When to Use
Use before ORION claims VERIFIED/DONE on multi-agent software, UI, infra, security, or production-workflow changes.

## Procedure
1. Freeze the candidate revision/artifact identity (Git SHA or deterministic hash).
2. List every acceptance criterion as `AC-xx`.
3. For each AC, identify the responsible worker, independent reviewer when required, and fresh evidence pointer.
4. Reject stale evidence produced against a different revision unless you can prove the changed files cannot affect that AC.
5. For UI work, require interaction coverage totals: discovered, tested, skipped, failed. Require `discovered = tested + skipped + failed`. Every skip needs a reason.
6. Require actual commands/procedures run—not planned tests, mock helper functions, or source inspection posing as runtime verification.
7. **Runtime Tool Provenance Rule:** In multi-agent/delegation audits, evidence MUST capture actual runtime-generated identifiers (e.g. `sa-...` child IDs) and real model-facing tool call transcripts. Never accept direct calls to internal test doubles (`_register_subagent`, `_handle_control_action`) as E2E proof. When execution is delegated to an A2A peer due to local runner constraints, the evidence record must capture executing peer identity, script SHA-256 digests, raw tee log path, explicit exit status (`PIPESTATUS[0]`), and a durable Kanban provenance comment.
8. **Sanitized Bundle Fidelity:** Review artifacts must undergo fail-closed secret scanning while maintaining 100% valid YAML/JSON parseability and scalar type fidelity (e.g. quoted string scalars, preserved generic SHA-256 digests).
9. Require residual risk to be explicit.
10. Check reviewer independence: an implementer-only signoff is not sufficient when the plan required LENS/SENTINEL/PRISM.
11. **Verify QA Separation of Duties:** Assert `production_files_modified_by_reviewer == 0`. If LENS/reviewer modified production source files during QA, reject with `QA_INDEPENDENCE_VIOLATION` and require remediation loop via implementer.
12. If anything is missing, return `NOT VERIFIED` with exact missing AC/evidence rows.
13. Only return `VERIFIED` when the matrix is complete, current, and independence invariants hold.

## Concurrent-producer freeze rule
When the evidence producer (probe script, prototype, generator) may still be edited by a live worker:
- Require quiescence before running: sample the artifact hash twice, >=45s apart. If it changes, wait; if it keeps changing, do not run - report ARTIFACT STILL BEING WRITTEN.
- Bind identity: record pre-hash, run, post-hash. A run whose artifact changed mid-window is VOID unless the process provably loaded stable bytes at start; void runs are never cited as PASS.
- Preserve bytes: snapshot each certified revision pair into an immutable copy (chmod 444, e.g. `.frozen/`). A hash without a byte copy cannot be re-verified or re-run.
- Filenames lie: same path, new bytes. Trust in-report anchors (probe_version, assert counts) plus hashes, not filenames; reused output filenames may hold a different revision's results.
- Peer relays keep the same rule: when the caller's executor is unavailable, a peer may execute - but only under the freeze protocol, and only a byte-bound run counts as evidence.

## Pitfalls
- "All tests pass" without exact test evidence.
- screenshots without interaction assertions.
- a reviewer reading the implementer's summary but not the artifact/evidence.
- one final edit after QA that invalidates the SHA.
- a run over an artifact being concurrently rewritten: quiesce the writer, run from immutable bytes, hash before AND after, and void the run if either hash moves.
- `skipped: 0` while discovered count exceeds tested+failed.
- **Binding attachments/hashes from a hot directory:** when concurrent workers/verification runs still write into the evidence dir (post-closure churn), any hash/attachment you bind is invalidated within seconds. Before binding: quiesce-check (two stat samples a few seconds apart + `pgrep` for live writers). If not quiesced, bind a frozen snapshot generation (e.g. `.frozen/` copies with pre/post hash pairs) instead, and mark any quoted hash that no longer matches disk as STALE in the ledger.
- substituting simulated output or optimistic summaries when a local execution runner wedges instead of delegating to a peer.

## Verification
A final report must include revision, AC matrix, evidence pointers, review owners, residual risks, and a mathematically consistent interaction-coverage summary when UI is involved.
