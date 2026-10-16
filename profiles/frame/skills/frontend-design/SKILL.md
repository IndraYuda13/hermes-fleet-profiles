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
- Verify the working tree before executing the tasks a plan or peer hands you: confirm the prerequisite tasks are actually complete and committed (`git log`, `git status`) and adjust the plan's file/line references against the live files. A follow-up request can predate your own state, so finish or explicitly flag the gap before building on top of it — starting a later step on an uncommitted earlier step yields a broken tree and a false green.
- Confirm the *branch* (not just cleanliness) immediately before committing, and re-read it in the same breath as the handoff. On a shared repo a peer can squash your commits, merge them, and check out a different branch between rounds, so the branch named in the brief may no longer be where HEAD sits — and a clean tree plus a matching file list make the wrong ref silent. Before that, read the actual refs (`git rev-parse HEAD <branch> <default>`) and the parents of any commit that appeared in between (`git rev-list --parents -1`) to see whose work is whose.
- Never relocate refs to repair your own placement when the history changed underneath you: cherry-pick or fast-forward only on the owner's instruction. Report the ref state, the squash and its verified content equivalence (`git diff old new`), and where the commit actually landed; moving a branch on a repo another writer just rewrote can discard their work.
- Prefer additive, modular changes in the existing architecture. Treat the user's source-quality requirement as acceptance work before independent review, not optional polish. Keep comments for useful technical rationale; remove historical review IDs, fleet/agent narration, section-history chatter, and public “clean code/SOLID” announcements from touched surfaces. Preserve legitimate identifiers and concise non-obvious invariants.
- For a large workflow component, extract the smallest cohesive controlled panels or read-only summaries after the main flow works. Keep state, requests, mutations, and snapshot authority in one clear owner; pass typed values/actions instead of introducing duplicate fetch, grading, or evidence logic. Freeze cleanup before final build and affected browser verification.
- Before connecting a new route, inspect its layout/provider branch, legacy entry points, and static/offline-shell requirements. A route deliberately excluded from the ordinary provider needs an explicit new-flow provider without double-wrapping the legacy flow. Preserve required static shells; do not make their server page dynamic merely to read query parameters.
- Treat persisted snapshots, unsent drafts, accepted results, and public projections as distinct states. Never reconstruct a new protocol's frozen intent from a legacy field or display an optimistic local grade as an accepted result.
- Render domain reasons, not just status booleans. “Unknown for this decision” can mean missing, incomplete, unmapped, or valid-but-incomparable evidence; use reason-aware aggregate and per-item copy so available results are not falsely described as absent. Test the actual component across every reason.
- Verify suspected mobile occlusion with initial, scrolled, and keyboard-focused control geometry against fixed navigation. Below-fold content alone is not a defect; repair only actual clipping, overlap, or unreachable instructions/actions without gratuitous redesign.
- In shared candidates, freeze imports and ownership first, run only owned formatting/lint and bounded checks while peers write, and stage explicit owned paths. Coordinate the quiescent revision before full build or integrated certification.
- Bind verification claims to the states actually reached. An error-state screenshot is not evidence for the normal workflow; a requested test path is not coverage unless the runner reports that file matched. After backend readiness, build the quiescent candidate and rerun positive browser journeys against the production-style server before handoff.
- A numeric controlled field must keep its raw string draft and clamp only at submit: binding the parsed number as the controlled value collapses a cleared field to `0` and re-renders that over the user's next keystroke (deleting `3` yields `03`). Normalize input (digits only, strip leading zeros, cap length) in the change handler and clamp to the ceiling where the request is built, then keep the draft and the applied count as the same single source of truth.
- When extracting markup into a presentational child component, preserve the DOM shape that locators and CSS depend on — element types, ids, labels, and conditional attributes — and pass typed values plus callbacks instead of duplicating state. Callbacks the child now needs (commit a move, complete an assignment) stay in the state owner. Verify the structural contract still holds by grepping the consumer tests for the element and summary text they match on.
- Re-read a file from disk before rewriting it after any in-session edit: the copy in context goes stale and the write is refused or silently reverts work.
- Keep the controls a step *requires* visible without any interaction; collapse only supplementary detail. A disclosure wrapping the method/option/config inputs makes the flow read as unfinished and empty on first paint, and the teacher concludes the feature is missing rather than hidden. Roster, member lists, and other reference detail may stay behind a toggle.
- When a primary action is gated, surface the reason and the unlocking control next to the action itself, not inside a collapsed section. A disabled button with no visible explanation is indistinguishable from a broken one; name the specific blocking items (group labels, not a count) and put the checkboxes that clear the gate in the same view, writing the exact key the gate reads.
- Constrain form controls to an explicit width (`max-w-*` on the wrapping label) rather than letting them span a wide card; a full-width input reads as an over-wide editor at desktop. Cap every control whose expected value is a few characters, and leave genuinely long-text fields alone.

For snapshot-bound printing, protocol upgrades, and asynchronous board workflows, load `references/snapshot-state-integration.md`.

## Verification & fleet QA
For fleet orchestration roles (ORION/AURORA/FRAME/LENS), the LENS 5-gate fail-fast QA pipeline, `data-ui-*` runtime schema contracts, synthetic mutation calibration, failure codes, and the macro-compositional diversity gate, load `references/orchestration-lens-visual-qa.md`.
