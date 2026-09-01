# Root-cause debugging reference

Use a tight reproducible feedback loop before proposing a fix. The loop must assert the reported symptom—not merely prove the program starts—and be fast enough to rerun after every probe.

## Evidence sequence

1. Read the full error, logs, and request/fixture that caused it.
2. Reproduce the failure with the smallest test, CLI command, request replay, or harness available.
3. Check recent diffs, configuration, environment, and dependency changes.
4. At each component boundary, capture what entered and left. Trace bad state upstream to the first incorrect producer.
5. Compare against a working adjacent path; list concrete differences.
6. State ranked, falsifiable hypotheses. Change or observe one variable at a time.

## Guardrails

- No speculative fixes before the failing path and a causal hypothesis are known.
- For flaky behavior, raise the repro rate with repetitions, isolation, seeded inputs, or narrowed timing before editing.
- If two fixes fail, return to the evidence. Repeated unrelated patches signal a design problem, not permission to keep guessing.
- Keep the minimal repro as the regression check once the cause is fixed.
