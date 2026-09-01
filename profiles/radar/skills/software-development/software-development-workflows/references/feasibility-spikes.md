# Feasibility spikes reference

A spike is a disposable proof for one risky unknown—not a premature production implementation.

1. State the question with observable Given/When/Then acceptance.
2. Start with the risk most likely to invalidate the idea.
3. Research only enough to choose a plausible path; compare variants when the choice is material.
4. Build the smallest runnable artifact that exposes real output and exercise non-happy-path inputs.
5. Record `VALIDATED`, `PARTIAL`, or `INVALIDATED`, with evidence, constraints, and the production recommendation.

Keep spike artifacts isolated and throw them away or reimplement deliberately for production. A log message claiming success is not a useful verdict.
