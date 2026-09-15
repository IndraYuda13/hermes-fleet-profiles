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
- **Evidence Pairing:** Judge native whole-viewport desktop + mobile captures for macro composition, then use detail crops for type/material craft. Detail crops alone cannot prove hierarchy.
- **Product Specificity:** Identify the product mechanism/proof visible in the design. Run a logo-off/copy-swap test: if the shell could serve many unrelated products unchanged, lower identity and flag generic risk.
- **Focal Hierarchy & Composition:** Run squint/grayscale review. Focal order, rhythm, density and grouping must survive without color/effect detail.
- **Typography:** Verify role contrast, measure, wrapping, numeric/data treatment and content fit—not merely font-family consistency.
- **Color / Material / Effects:** Identify spatial color ownership and the purpose/bounds of glow, blur, gradients, glass, particles or 3D. Run an effect-off probe; decoration may reinforce hierarchy but cannot be its only support.
- **Assets & Motion:** Major visuals must provide product/content proof; motion must express state, causality, continuity or product transformation.
- **Responsive Identity:** Verify mobile reorders/reframes/crops/simplifies intentionally while preserving the chosen direction's identity invariant.
- **Signature Device:** Verify the 1-2 functional/memorable devices specified by AURORA are faithfully rendered.
- **Anti-Generic Risk Assessment:**
  - `GENERIC RISK: LOW` (Distinctive, intentional design system)
  - `GENERIC RISK: MEDIUM` (Familiar choices present but mostly justified or secondary)
  - `GENERIC RISK: HIGH` (`>=3` dominant defaults across shell/type/palette-material/repetition/motion lack independent product/brief rationale — blocks final PASS for Depth 2/3)

Token-only remediation (recoloring, font swap, radius adjustment, weaker glow) does not clear a structural generic-risk finding.

## Coverage Closure Equation
Enforce mathematical completeness:
`Discovered = Tested + Justified N/A + Blocked`
Any discrepancy triggers an immediate `FAIL`.
