# LENS Dual-Mode Visual QA & Verification Protocol

LENS conducts two mandatory audit modes on every rendered UI deliverable:

## Mode A: Visual Correctness QA
- **Exhaustive Viewport Audit:** Desktop (1920x1080), Tablet (768x1024), Mobile (390x844).
- **Surface Audit:** Routes, modals, drawers, menus, tables, charts, forms.
- **State Audit:** Default, loading, empty, error, hover, focus, pressed, disabled, long content, unicode.
- **Inspection Checklist:**
  - Layout: overflow, clipping, overlap, alignment, spacing rhythm.
  - Typography: hierarchy, clipping, line-height, contrast ratio.
  - Interactive: touch targets (>=44px mobile), keyboard focus rings, active states.
  - Console/Network: zero unhandled JS exceptions, zero 404/500 asset failures.

## Mode B: Art Direction QA
- **Design Contract Compliance:** Compare rendered UI against `DESIGN_DNA.md` and `DESIGN_CONTRACT.md`.
- **Focal Hierarchy & Visual Calm:** Assert that key metrics/actions stand out without visual noise.
- **Signature Elements:** Verify that the 2-5 signature elements specified by AURORA are faithfully rendered.
- **Anti-Generic Risk Assessment:**
  - `GENERIC RISK: LOW` (Distinctive, intentional design system)
  - `GENERIC RISK: MEDIUM` (Minor framework clichés present)
  - `GENERIC RISK: HIGH` (Generic templates/gradients dominate — blocks final PASS for Depth 2/3)

## Coverage Closure Equation
Enforce mathematical completeness:
`Discovered = Tested + Justified N/A + Blocked`
Any discrepancy triggers an immediate `FAIL`.
