# Fleet Excellence Governance V1 — Reference Guide

*Source: Owner Directive `/dev/shm/HERMES_FLEET_EXCELLENCE_GOVERNANCE_V1.md`*

## Core Quality Hierarchy
1. Owner outcome
2. Correctness
3. Completeness
4. User-visible quality
5. Reliability
6. Maintainability / reversibility
7. Evidence quality
8. Efficiency
9. Speed

*Speed must never silently outrank quality on a material task.*

## Anti-Lazy Contract
Verify before declaring material completion:
- Target runtime directly inspected.
- Full scope covered without unauthorized simplification.
- Result actively tested and exercised.
- Boundary conditions and edge cases checked.
- Zero regressions.
- No rough edges, placeholders, TODOs, or default unstyled controls.
- Evidence reproducible and tied to exact revision/build.
- Nothing remains that would embarrass the fleet under close owner inspection.

## Materiality Router
- **Tier 0 (Trivial):** Solo fast-path (1 agent).
- **Tier 1 (Standard):** Implementation + self-review + direct verification.
- **Tier 2 (Material):** Explicit acceptance criteria + specialist ownership + independent verification (`implementer != certifier`) + reproducible evidence.
- **Tier 3 (Critical / Public):** Staging + rollback + independent QA + security gate + production verification + owner acceptance state machine.

## Invariants & State Machine
- **No Self-Certification:** `IMPLEMENTATION_COMPLETE` vs `VERIFIED_PASS` / `VERIFIED_FAIL`.
- **False PASS Handling:** Serious defect; investigate missed gate, root cause, and remediation.
- **Revision Lock:** SHA-256 / commit SHA binding across implementation, verification, and deploy.
- **Owner Delight Gate:** `OWNER_DELIGHT_READINESS = PASS | CONDITIONAL | FAIL`.
- **Release State Machine:** `INTERNAL_RELEASE_GATE = PASS` | `OWNER_ACCEPTANCE = PENDING` | `MISSION_RELEASE_STATE = AWAITING_OWNER`.
