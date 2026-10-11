# Fleet QA Handoff Contract (Deterministic + Perceptual Planes)

Depth for the multi-agent verification pipeline described in SKILL.md §8. Role codenames below are this fleet's contract names; keep them consistent with the artifact filenames.

## Dual-plane separation of responsibilities
- **PRISM (Deterministic Execution Plane):** state machine transitions, form validation boundaries, route navigation contracts, ARIA/DOM accessibility mechanics (focus trapping, tabindex order), mock-data leakage regex, automated regression suites.
- **LENS (Perceptual Rendered Plane):** rendered visual quality, taste rubric, macro-diversity, layout metrology, rendered pixel contrast, perceptual anti-slop, motion feel.

## Mandatory inputs (from FRAME, the build agent)
1. `BUILD_MANIFEST.json` — exact `build_sha`, deterministic preview launch command, typecheck status, lint status.
2. `INTERACTION_CONTRACT.json` — stable test selectors (`data-testid` or accessibility roles) and state-machine transition tables. Never run tests against brittle Tailwind utility classes.
3. `ROUTE_AND_FIXTURE_MANIFEST.json` — explicit route map, 404 handling, realistic fixture datasets (no empty placeholders).

## Outputs (for the ORION release gate)
1. `PRISM_VERIFICATION_REPORT.json` — machine-readable results bound to the exact `build_sha`, covering all test domains.
2. `PRISM_COVERAGE_MAP.json` — reconciliation proving 0 unexercised state transitions against `INTERACTION_CONTRACT.json`.
3. `REPRODUCIBILITY_RUNBOOK.md` — single-line commands and environment seeds for identical reproduction.
4. `DEFECT_LEDGER.json` — structured defects with severity (`BLOCKER`, `HIGH`, `MEDIUM`), failing assertion, target selector, and stack trace (emitted on failure).

## Gate and routing invariants
- `RELEASE_GATE = PRISM_PASS && LENS_PASS` — an independent veto per plane; never average scores across functional and visual gates.
- Defect routing goes to the release gate (ORION) as a structured report for unified dispatch to FRAME or AURORA — never direct directives between verifiers.

## Feature-conditional checks & journey gating (anti-Goodhart)
- Conditional rules (focus trap only if a modal/dialog is present, form validation only if forms exist) never pass by omission alone.
- Cross-reference required components against the journey specifications in `INTERACTION_CONTRACT.json`. If a journey mandates a modal, dialog, or form but the DOM element is missing, emit `CONTRACT_VIOLATION_FAIL` rather than silently skipping the check.

## Concurrency & state-mutation isolation
- Functional QA is state-mutating (form submissions, error triggering, dialog toggles, local/sessionStorage writes); perceptual QA requires a quiescent DOM baseline.
- When running in parallel, the two planes must never share a browser context, incognito session, or mutable storage partition. Launch independent browser instances or isolated contexts with dedicated ephemeral storage.

## Accessibility division of labor (axe-core vs LENS)
- Automated DOM contrast engines fail or flag false-positive `needs review` warnings on gradient, backdrop-filter, canvas, or semi-transparent composite layers.
- The deterministic plane owns structural, keyboard, and programmatic accessibility: ARIA roles, accessible name computation, focus management/trapping, tabindex ordering, input labeling.
- Perceptual color contrast over layered or composite backgrounds is delegated to rendered metrology. Scope axe-core contrast checks strictly to solid, single-layer backgrounds to avoid deadlocks.
