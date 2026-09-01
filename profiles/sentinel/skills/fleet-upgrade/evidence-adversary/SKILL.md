---
name: evidence-adversary
description: Falsify unsupported completion and review claims.
version: 1.0.0
author: Fleet Upgrade Research
license: MIT
metadata:
  hermes:
    tags: [review, evidence, security, verification]
    category: fleet-upgrade
---
# Evidence Adversary

## When to Use
Use for independent review of important implementation, QA, deployment, benchmark, or final ORION PASS claims.

## Procedure
1. Assume the claim may be wrong until evidence survives challenge.
2. Verify artifact/revision identity matches the evidence.
3. Map every acceptance criterion to evidence; identify missing/indirect rows.
4. Sample raw evidence, not only summaries: commands, logs, screenshots, test files, diffs, source references.
5. **QA Independence & Self-Review Guard:** Audit reviewer Git commits. Verify that `production_files_modified_by_reviewer == 0`. If the reviewer commit modified production application files (HTML, CSS, JS, backend logic) rather than purely test/evidence artifacts:
   - **Verdict:** `REJECT`
   - **Finding:** `[P0] QA_SELF_REVIEW_CONTAMINATION` (Reviewer repaired implementation and self-certified own changes).
6. Look for stale tests, cherry-picked subsets, skipped controls, impossible counts, untested negative paths, and self-review masquerading as independence.
6. Reproduce at least one high-risk assertion independently when practical.
7. For UI, audit interaction coverage arithmetic and sample critical controls.
8. For security/infra, check failure modes and rollback/containment, not only happy-path success.
9. Return APPROVE, REJECT, or APPROVE-WITH-RESIDUAL-RISK with blocking findings separated from recommendations.

## Verification
An approval must state what evidence was independently sampled and the exact revision/artifact reviewed.
