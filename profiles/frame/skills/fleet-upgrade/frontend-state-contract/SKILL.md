---
name: frontend-state-contract
description: Turn UI interactions into tested state contracts.
version: 1.0.0
author: Fleet Upgrade Research
license: MIT
metadata:
  hermes:
    tags: [frontend, interaction, state, testing, accessibility]
    category: fleet-upgrade
---
# Frontend State Contract

## When to Use
Use whenever FRAME implements or changes a control, preference, form, navigation interaction, dialog/menu, theme, or other stateful UI.

## Procedure
1. Enumerate changed interactive controls and write each transition as `initial state → action → expected state/output`.
2. Define observable outcomes: DOM attribute/class, ARIA state, visible content, route, request, storage, callback, or computed style. Never define success as "handler exists".
3. Implement semantic controls first; preserve keyboard and focus behavior.
4. Add/modify the smallest useful automated test for the transition. Use TDD for bug fixes where practical.
5. For preference/theme controls, test: click, keyboard activation, visible/computed state change, ARIA/label state, persistence after reload when specified, and restore/reverse transition.
6. Test loading/disabled/error states affected by the change.
7. Run relevant unit/component/integration tests plus build/type/lint checks that actually apply to the repo.
8. Record exact commands and revision identity.
9. Hand off to LENS with interaction names and expected outcomes, not only screenshots.

## Pitfalls
- CSS theme tokens exist but toggle never changes the root state.
- state changes internally but no accessible name/state updates.
- tests call implementation functions instead of the user-facing control.
- fixing mouse click while keyboard activation remains broken.

## Verification
Every changed interaction has an observable state transition and at least one executed verification path. A control that only renders correctly is not verified.
