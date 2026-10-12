---
name: frontend-design
description: "FRAME UI implementation, fleet visual QA & state contracts."
version: 1.1.0
license: MIT
metadata:
  hermes:
    tags: [frontend, design-contract, visual-qa, state-contract, anti-template]
    related_skills: [anti-ai-slop-web-design, anti-slop-ecommerce-architecture, impeccable]
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

## Implementation discipline
- Prefer additive, modular changes in the existing architecture. Treat the user's source-quality requirement as acceptance work before independent review, not optional polish. Keep comments for useful technical rationale; remove historical review IDs, fleet/agent narration, section-history chatter, and public “clean code/SOLID” announcements from touched surfaces. Preserve legitimate identifiers and concise non-obvious invariants.
- For a large workflow component, extract the smallest cohesive controlled panels or read-only summaries after the main flow works. Keep state, requests, mutations, and snapshot authority in one clear owner; pass typed values/actions instead of introducing duplicate fetch, grading, or evidence logic. Freeze cleanup before final build and affected browser verification.
- Before connecting a new route, inspect its layout/provider branch, legacy entry points, and static/offline-shell requirements. A route deliberately excluded from the ordinary provider needs an explicit new-flow provider without double-wrapping the legacy flow. Preserve required static shells; do not make their server page dynamic merely to read query parameters.
- Treat persisted snapshots, unsent drafts, accepted results, and public projections as distinct states. Never reconstruct a new protocol's frozen intent from a legacy field or display an optimistic local grade as an accepted result.
- Render domain reasons, not just status booleans. “Unknown for this decision” can mean missing, incomplete, unmapped, or valid-but-incomparable evidence; use reason-aware aggregate and per-item copy so available results are not falsely described as absent. Test the actual component across every reason.
- Verify suspected mobile occlusion with initial, scrolled, and keyboard-focused control geometry against fixed navigation. Below-fold content alone is not a defect; repair only actual clipping, overlap, or unreachable instructions/actions without gratuitous redesign.
- In shared candidates, freeze imports and ownership first, run only owned formatting/lint and bounded checks while peers write, and stage explicit owned paths. Coordinate the quiescent revision before full build or integrated certification.
- Bind verification claims to the states actually reached. An error-state screenshot is not evidence for the normal workflow; a requested test path is not coverage unless the runner reports that file matched. After backend readiness, build the quiescent candidate and rerun positive browser journeys against the production-style server before handoff.
- Make selected and submitted choices unmistakable in the rendered interface, using a visible state plus text or a coherent icon. An `aria-pressed` attribute alone does not communicate selection to sighted users.

For snapshot-bound printing, protocol upgrades, and asynchronous board workflows, load `references/snapshot-state-integration.md`.

## Verification & fleet QA
For fleet orchestration roles (ORION/AURORA/FRAME/LENS), the LENS 5-gate fail-fast QA pipeline, `data-ui-*` runtime schema contracts, synthetic mutation calibration, failure codes, and the macro-compositional diversity gate, load `references/orchestration-lens-visual-qa.md`.
