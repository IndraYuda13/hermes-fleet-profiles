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

This skill provides an authoritative, fleet-wide design governance standard to eliminate generic "AI slop" and elevate all web user interfaces, dashboards, 3D experiences, and landing pages to museum-grade, editorial, and architectural excellence.

**Fleet Invariant**: All fleet members involved in frontend design, implementation, and review (AURORA, FRAME, LENS, PRISM, and ORION) MUST read and apply the principles in this skill before authoring or modifying any UI.

## When to Use

- When authoring design specs, wireframes, color systems, or typography (`AURORA`).
- When implementing HTML, CSS, Three.js, WebGL, Tailwind, or frontend components (`FRAME`).
- When conducting rendered visual QA, screenshot audits, or anti-slop checks (`LENS`, `PRISM`).
- When orchestrating UI pipelines, fanning out tasks, or gating releases (`ORION`).
- Trigger phrases: "buat UI", "bikin frontend", "redesign", "anti AI slop", "Awwwards grade", "world class design".

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

## The 6-Dimension Calibrated Scoring Rubric

Lens audits builds across 6 weighted dimensions (Total 100 points, Pass requires $\ge 85$ total and $\ge 8$ per dimension):

- **Identity & Brief Match** (25%): Specificity to product/domain; custom character; zero template genericness.
- **Composition & Hierarchy** (25%): Clear primary/secondary focal path; rhythm; breathing room; anti-card-grid.
- **Typography** (15%): Typographic triad; measure; optical tracking; contrast ratio $\ge 7:1$.
- **Assets & Visual Direction** (15%): Proof-driven visuals; authentic photography/renders; intentional cropping.
- **Interaction & Motion** (10%): Tactile micro-interactions; calm anchored macro; reduced-motion compliance.
- **Responsive** (10%): Intentional mobile two-tier stage; touch targets $\ge 44\text{px}$; zero overflow.

## Knowledge Base & Reference Modules

Load the relevant reference module on demand using `skill_view`:
- `skill_view("anti-ai-slop-web-design", "references/lens-review-contract.md")`: The complete Lens review instructions, rubric anchors, and JSON report schema.
- `skill_view("anti-ai-slop-web-design", "references/hermes-orchestrator-protocol.md")`: The 12-stage anti-slop pipeline and worker handoff contract template.
- `skill_view("anti-ai-slop-web-design", "references/hermes-design-research.md")`: Root-cause diagnosis of AI slop, OFF+BRAND study, and operational design rules.
- `skill_view("anti-ai-slop-web-design", "references/anti-ai-slop-universal-principles.md")`: Complete 7 universal anti-slop laws, 8 hard checks, and scoring rubric.
- `skill_view("anti-ai-slop-web-design", "references/macro-compositional-diversity-gate.md")`: 12-dimension macro fingerprinting and anti-token-gaming rules.
- `skill_view("anti-ai-slop-web-design", "references/archetypes-reference.md")`: 88+ non-slop design archetypes catalog.
- `skill_view("anti-ai-slop-web-design", "references/mobile-zero-overflow-discipline.md")`: Strict viewport constraint invariants.
- `skill_view("anti-ai-slop-web-design", "references/exhaustive-audit-protocol.md")`: LENS/PRISM multi-viewport inspection procedure.

## Verification

To verify that an interface adheres to this skill:
1. Run `python3 /root/.hermes/fleet_v2_system/core/lens_engine_v2.py <URL> <OUT_DIR> <BUILD_SHA>`
2. Inspect `LENS_REVIEW_REPORT.json` for `verdict == "pass"` and `all(hard_checks.values()) == true`.
3. Confirm that weighted score $\ge 85$ and all individual dimensions $\ge 8$.
