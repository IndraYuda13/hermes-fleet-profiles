---
name: weak-signal-triangulation
description: Escalate weak signals with calibrated evidence.
version: 1.0.0
author: Fleet Upgrade Research
license: MIT
metadata:
  hermes:
    tags: [research, osint, ai, monitoring, weak-signals]
    category: fleet-upgrade
---
# Weak-Signal Triangulation

## When to Use
Use for unreleased models/features, SDK identifiers, docs changes, commits, package metadata, endpoints, benchmark leaks, or rumors with potentially high impact.

## Procedure
1. Preserve the primary artifact: source, timestamp/first-seen time, exact changed identifier, and prior-vs-current delta when available.
2. Label facts as OBSERVED; label interpretation separately as INFERENCE.
3. Search at least one independent evidence class when possible (e.g. SDK + docs, repo + package registry, code + endpoint behavior).
4. Assess alternative explanations: test fixture, stale branch, typo, placeholder, generated code, regional rollout.
5. Score confidence and impact separately. Low evidence can still merit high-priority monitoring if impact is large.
6. Report early when the signal is decision-relevant, but never upgrade "identifier exists" into "model released".
7. Define what next evidence would confirm/refute the inference.

## Verification
Every alert contains primary source, first-seen time, fact/inference separation, confidence, impact, alternatives, and next confirmation trigger.
