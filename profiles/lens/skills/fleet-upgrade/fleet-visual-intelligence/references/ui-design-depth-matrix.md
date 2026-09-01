# UI Design Depth Decision Matrix

ORION must classify every UI task before dispatching specialist cards.

| Level | Name | Trigger & Criteria | Specialists Spawned | Deliverables Expected |
|---|---|---|---|---|
| **Depth 0** | Existing System | Minor patches, label fixes, single button/field adjustments where existing visual language is clear. | `FRAME` → optional `LENS` quick check | Direct code diff, minimal test assertion |
| **Depth 1** | Quick Visual Research | Small new UI features building on existing visual language. Scope is bounded. | `AURORA` → `FRAME` → `LENS` | Brief delta design guidance, functional code, visual QA |
| **Depth 2** | Full Visual Discovery | New dashboards, internal products, major redesigns, significant new sections. | `AURORA` → `FRAME` → `LENS` | Multi-source live research, Reference Matrix, >=3 directions + scoring, `DESIGN_DNA.md`, `DESIGN_CONTRACT.md`, full implementation, dual-mode QA report |
| **Depth 3** | Flagship / Premium Art Direction | Brand-critical products, primary public websites, high-visibility launches, "world-class/Apple-level" requests. | `AURORA` (with scouts) → `FRAME` → `LENS` → Remediation → Retest | Deep research, reference synthesis, 3-5 visual directions + scoring, `DESIGN_DNA.md`, `DESIGN_CONTRACT.md`, high-fidelity implementation, exhaustive dual-mode QA, remediation ledger, clean retest |

## Marginal Value Rule
Before spawning any specialist, ORION must answer:
> "What unique uncertainty, deliverable, or verification does this specialist own?"
If the answer is not unique, do not spawn.
