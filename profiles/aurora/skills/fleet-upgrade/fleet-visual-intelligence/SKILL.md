---
name: fleet-visual-intelligence
description: Route UI builds via visual intelligence design & QA.
version: 3.1.0
author: Fleet Architecture & Orion Lead
license: MIT
metadata:
  hermes:
    tags: [ui, ux, design-intelligence, visual-qa, art-direction, orchestration, aurora, frame, lens]
    category: fleet-upgrade
---

# Fleet Visual Intelligence Standard (V3.1)

Additive visual intelligence workflow for UI/UX missions across the Hermes fleet. Governs ORION routing, AURORA design leadership, FRAME implementation fidelity, and LENS dual-mode verification.

## When to Use
Use when orchestrating, designing, building, or reviewing web and mobile user interfaces, dashboards, or flagship web applications. Triggers on any UI/UX task requiring design exploration, design contracts, high-fidelity implementation, or dual-mode visual QA.

## Core Philosophy
Do not optimize for generic beauty or copy Apple/Linear/Stripe visual identities. Optimize for:
**Context Fit + Usability + Visual Distinction + Polish + Clarity + Accessibility + Product Identity.**

---

## 1. ORION: UI Design Depth Routing

ORION must classify the UI mission into a Design Depth level before dispatching work:

| Depth | Trigger & Scope | Expected Workflow |
|---|---|---|
| **Depth 0: Existing System** | Minor patches, label fixes, single button/field adjustments where design system is clear. | `FRAME → optional LENS quick check`. No AURORA research. |
| **Depth 1: Quick Visual Research** | Small new UI features building on existing visual language. Scope is bounded. | `AURORA (delta guidance) → FRAME → LENS`. |
| **Depth 2: Full Visual Discovery** | New dashboards, internal products, major redesigns, significant new sections. | `AURORA (multi-source research, >=3 directions, scoring, Design DNA + Contract) → FRAME → LENS`. |
| **Depth 3: Flagship / Premium Art Direction** | Brand-critical products, primary public websites, high-visibility launches, "world-class/Apple-level" requests. | `AURORA (deep research, scouts, 3-5 directions, Design DNA + Contract) → FRAME → LENS → remediation → retest`. |

### Orion Marginal Value Rule
Before spawning any specialist card, answer: *"What unique uncertainty, deliverable, or verification does this specialist own?"* If the answer is not unique, do not spawn.
- **AURORA:** What should the experience and design be? (Design DNA & Contract)
- **FRAME:** How should it be faithfully implemented? (Code & Functional States)
- **LENS:** What does the user actually see and experience? (Dual-mode Verification)

---

## 2. AURORA: Product Design Intelligence & Art Direction

For Design Depth 2 and 3, AURORA acts as Art Direction Director across 8 mandatory steps:

1. **Step 1 — Product Understanding:** Define product context (audience, user jobs, environment of use, information density, usage frequency, trust needs, device priorities, and prohibited styles) *before* picking any design language.
2. **Step 2 — Live Design Research:** Conduct live web/browser research for references (>=8 references, >=3 direct-domain, >=3 aspirational, >=1 interaction/motion, >=3 distinct visual families). Give each reference one primary job: `composition`, `typography`, `content/asset`, `interaction/motion`, `responsive`, or `material/color`. Quantity without role separation is mood-board averaging. Subagent scouts may be used for large tasks.
3. **Step 3 — Design Reference Matrix:** Map every reference with: Primary Job, Relevance, Transferable Principle, What NOT to Copy, and Product Fit. Extract principles, never clone identities. Create `DEFAULT_DEBT.md` for likely category/framework defaults before directions are authored.
4. **Step 4 — Multi-Direction Exploration:** Develop >=3 distinct visual directions (3-5 for Depth 3) that remain different with logos hidden and in grayscale. At least two structural axes must differ: reading/focal path, shell topology, repetition model, content/media relationship, density, navigation relationship, or interaction model. Palette/font/effect swaps are one direction.
5. **Step 5 — Direction Scoring:** Score directions against product fit, task efficiency, information clarity, distinctiveness, accessibility, responsive suitability, and implementation feasibility.
6. **Step 6 — Anti-Generic-AI Design Gate:** Run logo-off/copy-swap, squint/grayscale, and effect-off probes. Inspect the dominant shell, type treatment, palette/material, repeated-container pattern, and motion as a cluster. `>=3` unexplained category/model defaults => `GENERIC RISK: HIGH`; redesign at composition/content level. A single justified motif is never rejected merely because it is common.
7. **Step 7 — Design DNA (`DESIGN_DNA.md`):** Document Archetype, Product Mechanism/Proof, Product Character, Grid, Density rationale, Composition Rhythm, Typography Roles, Color/Material Topology, Effect Budget, Surface Hierarchy, Corner Philosophy, Spacing Rhythm, Motion, Navigation, Data Presentation, Signature Elements (1-2 functional/memorable elements), Default-Debt Decisions, Responsive Identity Invariants, and Anti-Patterns.
8. **Step 8 — Design Contract (`DESIGN_CONTRACT.md`):** Concrete engineering specification covering layout, route composition, breakpoints, component hierarchy, all states (empty/loading/error/hover/focus/pressed/disabled), form/table behaviors, design tokens, and motion specs so FRAME never guesses art direction.

---

## 3. FRAME: High-Fidelity Design Implementation

FRAME faithfully implements AURORA's design intent without falling back to default framework presets:
- Read `DESIGN_DNA.md` and `DESIGN_CONTRACT.md` before coding.
- Treat UI libraries (Tailwind, shadcn, Radix) as primitives to customize, not final art direction.
- Implement all real functional states (empty, loading, error, interactive mutations); no fake screenshots.
- Ensure responsive adaptation (mobile/tablet/desktop) is architectural, not just shrinking desktop layout.
- Preserve the accepted macro fingerprint (topology, focal relationships, repetition model, content/media relationship, type roles, color/material ownership). Do not normalize an authored direction back into a stock shell for coding convenience.
- When parallelizing child workers across complex surfaces, partition by coherent ownership (shell, dashboard/data, forms/modals, responsive, motion polish). Parent FRAME must merge, build, test, and verify holistic design consistency.

---

## 4. LENS: Dual-Mode Visual QA & Verification

LENS operates in two distinct, mandatory review modes:

### Mode A: Visual Correctness QA
- Exhaustive surface audit across viewports (Desktop 1920x1080, Tablet 768x1024, Mobile 390x844).
- Inspect overflow, clipping, overlap, alignment, typography rendering, touch targets, keyboard focus, console errors, network errors, hydration/runtime warnings.
- Real-browser execution (Playwright/CDP) with interactive mutation assertions.

### Mode B: Art Direction QA
- Audit implementation fidelity against `DESIGN_DNA.md` and `DESIGN_CONTRACT.md`.
- Evaluate product-mechanism visibility, focal hierarchy, composition rhythm, typographic roles/measure, color/material ownership, effect budget, asset proof, motion causality, responsive identity preservation, and signature visual elements.
- Run **logo-off/copy-swap**, **squint/grayscale**, and **effect-off** probes on representative screenshots. A render cannot score as authored if its identity disappears when decorative effects are mentally removed.
- **Anti-Generic Review Rating:** Assign `GENERIC RISK: LOW`, `MEDIUM`, or `HIGH`.
  - `HIGH` includes `>=3` unexplained dominant category/model defaults across shell/type/palette-material/repetition/motion. Final visual PASS is strictly blocked for Depth 2/3 missions. Document exact structural decisions requiring remediation; recoloring alone is not remediation.

### Coverage Reconciliation Rule
Enforce mathematical closure on surface audit: `Discovered = Tested + Justified N/A + Blocked`. Any unclassified or missing surface triggers a `FAIL`.

### Output Deliverable
Produce `VISUAL_QA_REPORT.md` containing: Revision SHA, tested routes/states, viewports, screenshot artifacts, correctness defects, art direction defects, generic risk rating, console/network audit, and final verdict.

---

## 5. Remediation Loop & Retest Integrity

- **Implementation Defects:** `LENS → Request Changes → FRAME Remediation → LENS Retest (fresh revision)`.
- **Design Intent Defects:** `LENS → AURORA Clarification/Revision → FRAME Implementation → LENS Retest`.
- Implementers may never self-certify visual quality.
- Any code modification made during remediation invalidates previous PASS assertions and requires a fresh verification run against the updated Git commit SHA or artifact hash.

---

## 6. Design Taste Memory vs Template Trap

- Do NOT store entire project designs as reusable templates.
- Record only high-signal principles validated by operator feedback (e.g. typographic hierarchy, high density for operational telemetry, tactile active states).
- Every new major project starts from fresh product understanding and live domain research.
