---
name: change-impact-verification
description: Verify changed code across its affected surface.
version: 1.0.0
author: Fleet Upgrade Research
license: MIT
metadata:
  hermes:
    tags: [engineering, testing, regression, debugging]
    category: fleet-upgrade
---
# Change Impact Verification

## When to Use
Use for non-trivial code changes, bug fixes, shared utilities, API/schema changes, or refactors.

## Procedure
1. Reproduce the original failure or define expected behavior before editing.
2. Identify changed symbols/files and their direct callers/consumers.
3. Classify risk: behavior, data/schema, API contract, concurrency, auth/security, performance, UI interaction, deployment.
4. Choose tests for the changed path plus the highest-risk neighboring paths. Include negative/edge cases where the bug class suggests them.
5. For bug fixes, create a regression test that would fail before the fix whenever feasible.
6. Run focused tests first; then the appropriate nearby/regression suite.
7. Inspect diff after tests to catch accidental changes.
8. Record exact commands, results, changed files, and residual untested surface.

## Pitfalls
- one new unit test while shared callers remain untested;
- mocks that bypass the failed integration;
- green tests from before the latest edit;
- changing production behavior without a reproducer.

## Verification
Handoff names the original reproducer, impact surface, regression tests, exact commands, and current revision.
