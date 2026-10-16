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
0. For a failing-first browser regression, run the spec against a pre-fix production build before applying the fix and capture that failure, then bring the fix and the spec into one commit; a spec-only commit makes the red-to-green transition unauditable. An explicit commit-granularity instruction from the orchestrating handoff overrides this: follow it and state the deviation in the report so the split is deliberate rather than accidental. Reproduce a rendered defect by injecting the old rule at runtime (`page.addStyleTag({ content: "<old rule> !important" })`) and measuring the affected element in the same run as the fixed render — that proves the assertion discriminates instead of passing for an unrelated reason. Stage probes in a throwaway `tmp-*.spec.ts` and delete it before the final gate run, so the gates execute on the exact deliverable revision.
1. Enumerate changed interactive controls and write each transition as `initial state → action → expected state/output`.
2. Define observable outcomes: DOM attribute/class, ARIA state, visible content, route, request, storage, callback, or computed style. Never define success as "handler exists".
3. Implement semantic controls first; preserve keyboard and focus behavior.
4. Add/modify the smallest useful automated test for the transition. Use TDD for bug fixes where practical.
5. For preference/theme controls, test: click, keyboard activation, visible/computed state change, ARIA/label state, persistence after reload when specified, and restore/reverse transition.
6. Test loading/disabled/error states affected by the change.
7. Run relevant unit/component/integration tests plus build/type/lint checks that actually apply to the repo. When the user requests fast completion and minimal tests, select representative failure families rather than repeatedly running the entire browser suite. Fix shared fixture/setup causes first; preserve semantic assertions and report unselected coverage as unverified.
8. For asynchronous mutations, assert the acknowledged visible result before reload, logout, or navigation; a completed click does not mean the server write completed. Then assert persistence after reload separately.
9. Record exact commands and revision/build identity. Recheck the affected tests together after a repair: a standalone pass does not establish stability in the intended sequence. Fresh contradictory evidence supersedes the earlier pass immediately, including in an already-written handoff.
10. Freeze source before the final build and handoff. Avoid full builds during concurrent writes, and never reuse a build after runtime/CSS changes. Hand off interaction names, expected outcomes, raw counts, and unresolved failure families, not only screenshots.

For authentication transitions, offline adapter migrations, and measured display pagination, use [Stateful regression recipes](references/stateful-regressions.md). Monitoring or review ownership remains with the task's designated verifier.

## Pitfalls
- CSS theme tokens exist but toggle never changes the root state.
- state changes internally but no accessible name/state updates.
- tests call implementation functions instead of the user-facing control.
- fixing mouse click while keyboard activation remains broken.
- a geometry assertion measures the container box instead of the rendered content: a collapsed track reports a zero-width cell, so `cell.right <= row.right` passes while the label is visibly cut. Measure the glyphs with a `Range` over the cell's contents and also assert the measured width is non-zero.
- asserting layout before `setViewportSize` to the target width; resize first, then measure.
- authenticating twice as the same seeded account on one page: when global setup already establishes a session from a fixed fixture identity, an additional login helper for that same identity invalidates it and every following request fails. Use the established session, or create a uniquely identified account per spec.

## Verification
Every changed interaction has an observable state transition and at least one executed verification path. A control that only renders correctly is not verified.
