---
name: frontend-design
description: Contract-first frontend implementation intelligence for FRAME; preserves AURORA-authored design intent and prevents implementation-time template normalization.
license: MIT
---

# Frontend Design Intelligence — FRAME

Use this skill only for product/UI implementation. **AURORA defines design intent/system; FRAME implements it.** LENS independently verifies the rendered result.

## Contract-first workflow
1. Read `PRODUCT_CONTEXT.md`, `DESIGN_DNA.md`, `DESIGN_CONTRACT.md`, `INTERACTION_CONTRACT.json`, and `ASSET_MANIFEST.json` when the active workflow requires them.
2. Extract the selected direction's structural signature: focal path, grid/container topology, section rhythm, type roles, color/material topology, asset crops, signature devices, responsive thesis, and motion intent.
3. Implement those decisions faithfully with the existing stack and primitives. Component libraries are implementation primitives, not a substitute art direction.
4. Implement realistic content plus loading, empty, error, active, resolved, keyboard, focus, reduced-motion, and responsive behavior required by the contract.
5. Compare the real render against the contract before handoff and document any unavoidable implementation deviation.

For Depth 2/3 work, do **not** run `ui-ux-pro-max` style/color/typography/landing/design-system retrieval to choose or normalize art direction during implementation. If the required AURORA contract is missing or internally impossible, return the conflict to ORION/AURORA instead of inventing a replacement visual system.

## Anti-template rules
Avoid habitual AI-SaaS defaults unless the product genuinely calls for them: purple/cyan glow, decorative glass blur everywhere, endless rounded pills, generic centered hero blocks, random gradient blobs, mixed icon families, fake charts/data, and animation without information value.

Distinctiveness should come from deliberate typography, composition, content treatment, interaction, density and consistent system choices—not gimmicks.

## Scale-aware implementation gate
- **Major new UI / redesign:** consume AURORA's full implementation-ready design contract.
- **Small patch in an established system:** consume the established system plus the concise delta spec.
- FRAME may flag technical/accessibility constraints and propose the smallest coherent adjustment; it does not silently change the design thesis.
- LENS judges the actual rendering; a design spec is not visual QA evidence.
