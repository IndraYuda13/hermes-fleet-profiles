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
Use for independent review of important implementation, QA, deployment, benchmark, pre-publication artifacts, or final ORION PASS claims. For article and licensed-media review, follow `references/publication-review.md`.

## Procedure
1. Assume the claim may be wrong until evidence survives challenge.
2. Verify artifact/revision identity matches the evidence.
3. Map every acceptance criterion to evidence; identify missing/indirect rows.
4. Sample raw evidence, not only summaries: commands, logs, screenshots, test files, diffs, source references.
5. **QA Independence & Self-Review Guard:** Audit reviewer Git commits. Verify that `production_files_modified_by_reviewer == 0`. If the reviewer commit modified production application files (HTML, CSS, JS, backend logic) rather than purely test/evidence artifacts:
   - **Verdict:** `REJECT`
   - **Finding:** `[P0] QA_SELF_REVIEW_CONTAMINATION` (Reviewer repaired implementation and self-certified own changes).
6. Look for stale tests, cherry-picked subsets, skipped controls, impossible counts, untested negative paths, and self-review masquerading as independence.
7. Reproduce at least one high-risk assertion independently when practical.
8. For UI, audit interaction coverage arithmetic and sample critical controls. Separate browser DOM/layout evidence from screenshot pixel inspection; claim visual review only when the image was actually inspected. Exercise lazy-loaded content before treating an initial unloaded state as a defect.
9. For security/infra, check failure modes and rollback/containment, not only happy-path success.
10. Return APPROVE, REJECT, or APPROVE-WITH-RESIDUAL-RISK with blocking findings separated from recommendations. Scope artifact approval separately from staging and publication approval; a valid source artifact does not prove its template preserves required content, credits, or links.

## Verification
An approval must state what evidence was independently sampled and the exact revision/artifact reviewed.
