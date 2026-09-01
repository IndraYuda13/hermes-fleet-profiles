# QA Separation of Duties Reference

## Overview
Reviewer agents (such as LENS, SENTINEL, or PRISM) and Implementer agents (FRAME, FORGE, ATLAS) must maintain strict operational boundaries during review and acceptance verification.

## Core Rules
1. **Production Code Guard:**
   Reviewers evaluating a candidate revision MAY NOT modify production files (`HTML`, `CSS`, `JS`, backend source, database schemas, or deployment manifests).
2. **Permitted Reviewer Artifacts:**
   Reviewers may author and commit only test scripts, Playwright fixtures, screenshots, logs, and report markdown documents.
3. **Defect Handoff Cycle:**
   When QA uncovers a bug:
   - Mark QA task `BLOCKED` or `FAILED`.
   - Record `DEFECT-ID`, affected Git SHA, reproduction steps, expected vs actual behavior, and runtime error output.
   - Route remediation to the responsible implementer.
   - Implementer issues a fix in a new Git commit (`REV_B`).
   - QA re-tests `REV_B` independently (`tested_revision != reviewer_modified_revision`).
4. **Enforcement Oracle & Invariants:**
   The orchestrator (ORION) and security reviewer (SENTINEL) assert `production_files_modified_by_reviewer == 0`. Any violation results in `[P0] QA_SELF_REVIEW_CONTAMINATION` and immediately blocks `FINAL VERIFIED`.
5. **Evidence Scope Invariant:**
   Enforce `claim_scope <= evidence_scope`. Synthetic in-memory Python models or mock dictionaries cannot be used to certify real multi-agent runtime dispatch or Git revision provenance.
