---
name: anti-ai-slop-web-design
description: "Eliminate generic AI slop and enforce world-class UI craft."
version: 2.0.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [Frontend, Design, UI, Anti-Slop, Typography, Art-Direction, Lens-Review-Contract]
    category: custom
---

# Anti-AI Slop Web Design & Aesthetic Enforcement V2

This skill provides supporting design references to eliminate generic AI slop.
**Canonical Upstream Design Authority**: The canonical product design intelligence protocol for AURORA resides in `visual-authoring-core`.

**Fleet Invariant**: All fleet members involved in frontend design, implementation, and review (AURORA, FRAME, LENS, PRISM, and ORION) consult these references alongside `visual-authoring-core`.

## When to Use

- When consulting specific reference modules for anti-slop quality gates, lens review contract schemas, or macro-diversity rules.
- For primary upstream design workflow (discovery, candidate hypotheses, spikes, contract authoring), use canonical `visual-authoring-core`.

## The 8 Non-Negotiable Hard Checks (Lens Review Contract)

Before any UI build can receive a PASS verdict, all 8 hard checks must be verified as TRUE:

1. **`no_emoji_ui_icons`**: Unicode emoji are strictly forbidden as UI navigation, action, button, card header, or decorative icons. A single, coherent SVG family (e.g. Lucide/custom) or text labels must be used.
2. **`stable_status_not_animated`**: Stable states (`Active`, `Online`, `Available`, `Connected`, `Operational`) must NEVER pulse, ping, blink, breathe, or animate continuously. Use a calm text label with an optional static dot.
3. **`primary_flow_works`**: Primary CTAs must not be dead links (`href="#"`, `href=""`, `javascript:void(0)` without handlers). All primary flows must be clickable and navigable.
4. **`important_content_not_clipped`**: Critical titles, metrics, hero copy, and navigation items must never be clipped by `overflow: hidden` without intentional ellipsis or line-clamp.
5. **`keyboard_and_touch_usable`**: Mobile touch targets must meet ergonomic standards ($\ge 44 \times 44\text{px}$). No essential navigation or data may be locked behind desktop-only hover states.
6. **`reduced_motion_reviewed`**: All motion must respect `@media (prefers-reduced-motion: reduce)` and gracefully stop or dampen for users sensitive to vestibular motion.
7. **`fonts_and_assets_loaded`**: Zero broken images (`naturalWidth > 0`), zero 4xx/5xx network asset failures, and clean web font readiness before capture.
8. **`claims_and_data_are_grounded`**: Strictly zero generic marketing hallucinations: no fake testimonials ("John Doe, CEO at Acme"), fake metrics ("10,000+ Happy Customers"), or fake media badges ("As featured on Forbes/TechCrunch").

## The 6-Dimension Heuristic Scoring Rubric (`CALIBRATION_V0`)

Lens audits builds across 6 weighted dimensions (Total 100 points, Pass requires $\ge 85$ total and $\ge 8$ per dimension). `CALIBRATION_V0` is deliberately labeled an **uncalibrated heuristic** until repeated owner-rated examples establish empirical anchors. The score is a strict internal floor, not proof that the result is world-class or matches the owner's taste.

- **Identity & Brief Match** (25%): Specificity to product/domain; custom character; zero template genericness.
- **Composition & Hierarchy** (25%): Clear primary/secondary focal path; rhythm; breathing room; anti-card-grid.
- **Typography** (15%): Type scale, measure, and font personality justified by product voice; contrast ratio >= 4.5:1 (WCAG AA); no mandatory universal font triad.
- **Assets & Visual Direction** (15%): Proof-driven visuals; authentic photography/renders; intentional cropping.
- **Interaction & Motion** (10%): Tactile micro-interactions; calm anchored macro; reduced-motion compliance.
- **Responsive** (10%): Intentional mobile recomposition; touch targets >= 44px (Hermes UX target); zero unintended overflow.

## Knowledge Base & Reference Modules

Load the relevant reference module on demand using `skill_view`:
- `skill_view("anti-ai-slop-web-design", "references/lens-review-contract.md")`: The complete Lens review instructions, rubric anchors, and JSON report schema.
- `skill_view("anti-ai-slop-web-design", "references/hermes-orchestrator-protocol.md")`: The 12-stage anti-slop pipeline and worker handoff contract template.
- `skill_view("anti-ai-slop-web-design", "references/hermes-design-research.md")`: Root-cause diagnosis of AI slop, OFF+BRAND study, and operational design rules.
- `skill_view("anti-ai-slop-web-design", "references/anti-ai-slop-universal-principles.md")`: Complete 7 universal anti-slop laws, 8 hard checks, and scoring rubric.
- `skill_view("anti-ai-slop-web-design", "references/macro-compositional-diversity-gate.md")`: 12-dimension macro fingerprinting and anti-token-gaming rules.
- `skill_view("anti-ai-slop-web-design", "references/archetypes-reference.md")`: Retrieval vocabulary for spatial/aesthetic qualities. It is not a menu for choosing a finished style.
- `skill_view("anti-ai-slop-web-design", "references/mobile-zero-overflow-discipline.md")`: Strict viewport constraint invariants.
- `skill_view("anti-ai-slop-web-design", "references/exhaustive-audit-protocol.md")`: LENS/PRISM multi-viewport inspection procedure.

## Verification

To verify that an interface adheres to this skill:
1. Bind the review to the exact `BUILD_SHA` and inspect rendered evidence at every canonical viewport required by the active workflow.
2. Produce `LENS_REVIEW_REPORT.json` using the current fleet contract; do not depend on a hard-coded legacy runtime path.
3. Confirm all applicable hard checks are true, weighted score $\ge 85$, every applicable dimension $\ge 8$, zero blocking findings, and `GENERIC RISK != HIGH`.
4. Treat the numeric result as a heuristic gate only. Rendered evidence and blocking verifier findings remain authoritative.
