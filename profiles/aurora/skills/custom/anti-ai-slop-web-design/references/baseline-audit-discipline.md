# Baseline vs New Mutation Discipline & Real Fleet Stress Testing

## Overview
When auditing, stress-testing, or reviewing an existing production codebase using multi-agent fleet orchestration:

### 1. Establish Exact Baseline First
- Capture `BASELINE_REVISION = <exact git SHA>` before any task dispatch.
- Document clean git status, existing test pass counts, catalog/data volume, asset checksums, and runtime service health.

### 2. Explicit 4-Way Capability Partitioning
Never conflate existing capabilities with newly built improvements. Every report must partition claims into:
1. `EXISTING_BASELINE_FEATURE`: Features present at `BASELINE_REVISION` that were verified intact (e.g. multi-step wizard, spotlight search, token auth).
2. `NEWLY_IMPLEMENTED_CHANGE`: Material source/design modifications introduced in the current run.
3. `DEFECT_FIXED`: Concrete bugs resolved with explicit before/after regression proof.
4. `VERIFIED_EXISTING_BEHAVIOR`: Pre-existing system invariants confirmed via unit/functional/visual testing.

### 3. No Manufactured Activity
- If the audited application is already strong, well-tested, and free of P0/P1 defects, `RELEASE_CANDIDATE_VERIFIED` or `NO_MATERIAL_CHANGE_REQUIRED` is a valid, high-integrity verdict.
- Never manufacture unnecessary code mutations or refactors solely to simulate activity.

### 4. ORION Zero-Production-Edit Invariant
- ORION maintains `orion_production_edits == 0`.
- ORION performs only orchestration: inspects read-only, seeds Kanban DAGs, reviews specialist handoffs, and synthesizes evidence.
- All code/DB/config modifications must be executed by assigned specialists (FRAME, FORGE, ATLAS, etc.) via dedicated Kanban cards.
