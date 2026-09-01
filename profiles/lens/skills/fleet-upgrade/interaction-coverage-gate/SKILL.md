---
name: interaction-coverage-gate
description: Exercise every safe interactive UI surface.
version: 1.0.0
author: Fleet Upgrade Research
license: MIT
metadata:
  hermes:
    tags: [qa, playwright, browser, ui, regression, accessibility]
    category: fleet-upgrade
---
# Interaction Coverage Gate

## Separation of Duties & Reviewer Boundaries
When LENS is assigned QA, verification, or acceptance review:
- **Allowed Modifications:** QA reports, screenshots, evidence artifacts, Playwright/browser test files, QA fixtures, isolated test harnesses, and temporary test artifacts.
- **Prohibited Modifications:** Production application source code, production CSS/styles, production components, backend implementation, infrastructure configurations, or business logic.
- Reviewer and implementer roles MUST NOT exist in the same task run. LENS must never repair defects directly.

## Defect Handoff Contract
When LENS discovers a defect during inspection/testing:
1. Record defect ID (`DEFECT-xxx`) and affected revision SHA.
2. Record reproduction steps, expected behavior, actual behavior, and attach runtime/console evidence.
3. Mark the QA task `BLOCKED` or `FAILED` with an explicit handoff payload.
4. Route remediation to the designated implementer (FRAME for frontend UI/styles, FORGE for backend/logic, ATLAS for infra).
5. Retest only after the implementer produces a new revision SHA (`tested_revision != reviewer_modified_revision`).

## Procedure
Use for every UI QA task, especially redesigns, settings/preferences, forms, navigation, dashboards, and bug-fix verification.

## Procedure
1. Open the **rendered application**, not only source code.
2. Inventory interactive surfaces from semantic roles/DOM plus visible affordances: buttons, links, fields, selects, switches, checkboxes/radios, tabs, menus, dialogs, popovers, accordions, filters/sorts, pagination, theme/language controls, gestures, documented shortcuts.
3. Assign each a stable ID in a coverage table.
4. For every safe control, perform the real interaction and assert the intended result. Use auto-retrying assertions; do not use arbitrary sleeps as primary synchronization.
5. For destructive controls, use disposable data/environment or record `SKIPPED-DESTRUCTIVE` with rationale and alternative evidence.
6. Exercise keyboard path for keyboard-operable controls and verify visible focus. Check accessible name/role/state for critical controls.
7. Capture console errors and failed/relevant network requests during interaction runs.
8. For stateful visual changes, capture before/after screenshots and assert a semantic/DOM/computed-state change—not screenshots alone.
9. Repeat critical interactions at representative mobile + desktop viewport and both themes when applicable.
10. For persisted preferences, reload/new-context as appropriate and assert persistence.
11. Report totals. Gate condition: `discovered == tested + skipped + failed`; `failed == 0`; every skip documented.

## Theme Toggle Minimum Test
1. Record initial root theme signal and computed background/text.
2. Click toggle.
3. Assert root theme or equivalent semantic state changed.
4. Assert computed visual values changed where expected.
5. Assert toggle accessible state/label is correct.
6. Activate via keyboard (Enter/Space as semantically appropriate).
7. If persistence is required, reload and assert the selected theme remains.
8. Toggle back and verify reversibility.
9. Check console errors.

## Pitfalls
- Counting a visible control as tested.
- Testing only happy-path mouse clicks.
- missing controls below the fold or inside menus.
- screenshot appears different due animation but application state did not change.
- silently skipping destructive or auth-gated paths.

## Verification
Deliver the interaction coverage table, exact automation/manual procedures, screenshots/log pointers, failures, skips, and current revision identity.
