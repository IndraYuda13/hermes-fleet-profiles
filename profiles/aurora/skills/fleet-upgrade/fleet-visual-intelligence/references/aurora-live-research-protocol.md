# AURORA 8-Step Product Design Intelligence Protocol

## Step 1 — Product Understanding
Define product context before choosing aesthetics:
- Product Type & Core Domain
- Target Audience & User Persona
- Primary User Jobs & Workflows
- Product Mechanism / Proof: the behavior, artifact, content or transformation that can visibly shape the interface
- Environment of Use (office, mobile, field, darkroom)
- Information Density & Usage Frequency
- Emotional Target & Trust Requirements
- Accessibility & Device Priorities (mobile-first, desktop-dense, responsive)
- Existing Brand Commitments
- Likely Category/Framework Defaults (`DEFAULT_DEBT.md` candidates)

## Step 2 — Live Design Research
Conduct real web/browser research:
- Target: >=8 live references (>=3 direct-domain, >=3 aspirational, >=1 interaction/motion, >=3 distinct visual families)
- Every reference gets **one primary job**: composition, typography, content/asset, interaction/motion, responsive, or material/color. A reference count without role separation is mood-board averaging.
- Scout decomposition for Depth 3:
  - Scout A: Direct-domain competitors
  - Scout B: Best-in-class SaaS/product UI
  - Scout C: Interaction/motion patterns
  - Scout D: High-density information design
  - Scout E: Mobile/responsive adaptations

## Step 3 — Design Reference Matrix
Map every reference systematically:
| Reference | Primary Job | Relevance | Transferable Principle | What NOT to Copy | Product Fit |
|---|---|---|---|---|---|

Do not let one fashionable reference dominate several jobs unless the product independently earns that relationship. Research should widen the decision space, not turn a benchmark site into a house style.

## Step 4 — Multi-Direction Exploration
Develop >=3 distinct visual directions (3-5 for Depth 3). Directions must remain materially different with brand names/logos hidden and in grayscale. At least two structural axes differ: reading/focal path, shell topology, repetition model, content/media relationship, density, navigation relationship, or interaction model. Palette/font/effect swaps count as one direction.

## Step 5 — Direction Scoring
Score each direction (1-5) across:
1. Product Fit
2. Task Efficiency
3. Information Clarity
4. Product Specificity / Distinctiveness
5. Accessibility
6. Responsive Suitability
7. Implementation Feasibility
8. Long-Session Comfort

Before scoring, run squint/grayscale and effect-off probes so color/effects cannot inflate perceived quality.

## Step 6 — Anti-Generic-AI Design Gate
Apply the ablation test: *"If product name, logo, and copy were removed, would this still look meaningfully distinct from generic AI dashboards?"*
List the dominant shell, type treatment, palette/material treatment, repeated-container pattern and motion pattern. If `>=3` are recognizable category/model defaults without independent product/brief rationale, set `GENERIC RISK: HIGH` and redesign at composition/content level. A single justified motif is never rejected merely for being common.

## Step 7 — Design DNA (`DESIGN_DNA.md`)
Specify: Archetype, Product Mechanism/Proof, Product Character, Grid, Density, Composition Rhythm, Typography Roles, Color/Material Topology, Effect Budget, Surface Hierarchy, Corner Philosophy, Spacing Rhythm, Motion, Navigation, Data Presentation, Signature Elements (1-2 functional/memorable elements), Default-Debt Decisions, Responsive Identity Invariants, and Anti-Patterns.

## Step 8 — Design Contract (`DESIGN_CONTRACT.md`)
Deliver concrete engineering specification covering layout, route composition, breakpoints, component hierarchy, all states (empty/loading/error/hover/focus/pressed/disabled), form/table behaviors, design tokens, and motion specs.
