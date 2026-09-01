# Test-first development reference

For a behavior change or regression, write the smallest executable check that fails for the missing or broken behavior before changing production code.

1. **Red:** run the focused test/assertion and record its failure. If setup is too hard, first make a narrow harness at the system seam.
2. **Green:** implement only what makes that check pass; do not mix in cleanup or speculative features.
3. **Refactor:** improve names or duplication only while the check remains green.
4. **Verify:** rerun the focused check and the relevant project-level test/lint command.

Tests written after implementation are valuable coverage but do not demonstrate that the test detects the original defect. Do not accept a manual happy-path run as the only regression proof.
