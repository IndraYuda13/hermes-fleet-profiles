---
name: software-development-workflows
description: Use when diagnosing, validating, reviewing, or experimenting on software changes before implementation or completion.
version: 1.0.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [software-development, debugging, testing, review, spike, python]
    related_skills: [plan]
---

# Software Development Workflows

## Overview

Use this umbrella for the engineering loop around a change: prove the problem, choose a minimal path, validate it, and report evidence. Select the narrow section that matches the current phase; do not load several session-specific skills to reconstruct one workflow.

## Choose the lane

| Situation | Start here | Completion criterion |
|---|---|---|
| Stuck in repetitive tool errors or empty turns | Breaking tool loops | Strategy pivoted, file state verified, and batch findings reported |
| Failure, regression, or unexpected behavior | Root-cause debugging | A reproducible cause and a focused regression check |
| New behavior or a bug fix | Test-first implementation | A check failed before the change and passes after it |
| `ModuleNotFoundError`, import, or pip/venv conflict | Python environment diagnosis | The intended interpreter imports the intended package |
| Feasibility or competing approach is uncertain | Disposable spike | An observable validated, partial, or invalidated verdict |
| Preparing to commit, merge, or clean up a diff | Review and cleanup | Scope reviewed, findings resolved/recorded, targeted checks pass |

## UI design and audit expectations

When asked to make a UI modern or distinctive, do not prescribe a universal look such as dark navy, glassmorphism, neon glow, or gradient CTAs. Those effects frequently produce generic template aesthetics. Start from product purpose, audience, brand assets, conversion path, and content hierarchy. Pick one intentional art direction, then make typography, color, iconography, elevation, motion, and responsive behavior serve it.

For redesign reviews and mockup audits, verify the live page against its real source and runtime, then audit visual hierarchy, conversion flow, deep interactions, dependent state resets, keyboard and dialog semantics, mobile touch targets, injection sinks, and graceful degradation. Automated accessibility and Lighthouse scores are evidence, not verdicts. Use `references/web-ui-audit.md` for the full evidence-driven procedure.

If a frontend appears to lose dynamic components such as categories or catalog items, inspect the backend API response and cache or database state before assuming the frontend alone is responsible.

## Root-cause debugging

1. Read the complete error and construct the tightest repeatable command that asserts the reported symptom.
2. Inspect recent changes, inputs, configuration, and each component boundary. Trace the bad value or failed request upstream to its source.
3. Form falsifiable hypotheses, test one variable at a time, and compare with a working local pattern.
4. Only then make one root-cause change. Keep the reproducer as the regression check.

Do not stack speculative fixes. After repeated failed fixes, return to the evidence and question the design rather than adding a fourth workaround. See `references/root-cause-debugging.md` for the full investigation discipline.

## Breaking tool loops and stuck states

When an agent enters repetitive failure loops (repeated identical errors or empty conversational responses):
- **Never retry identical actions:** If a tool call fails, do not repeat it with identical parameters. Change the approach or inspect live state first.
- **Resolve patch ambiguity:** If `patch` fails with "Could not find a match", read the target file with `read_file` or `skill_view` to inspect live state and widen context lines. If "Found multiple matches" occurs, supply more surrounding context. If patching fails 2-3 times, overwrite with `write_file`.
- **Pre-empt test failure loops:** When a test fails due to missing modules or syntax errors, fix the underlying code before re-running the test suite.
- **Synthesize tool outputs:** After multi-tool execution batches, synthesize findings into a clear conversational summary explaining what succeeded, what failed, and the next step; avoid returning empty responses.

## Test-first implementation

For behavior changes, write the smallest red test or executable assertion at the affected seam, make the minimal change to turn it green, then refactor only while it stays green. A manual happy-path check is supplementary, not proof of a regression fix. Use focused tests first, then the project's relevant broader validation. See `references/test-first-development.md`.

## Python environment diagnosis

Use the interpreter that runs the application to inspect `sys.executable`, `sys.path`, package metadata, and the import itself. Check for local files shadowing package names before reinstalling. For service failures, inspect the service's `ExecStart` interpreter and environment rather than assuming an interactive shell's venv is relevant. See `references/python-environment.md`.

## Disposable feasibility spikes

A spike answers one observable risk and is throwaway by default. State the question as Given/When/Then, choose the riskiest unknown first, build the smallest runnable artifact, exercise edge cases, and finish with a `VALIDATED`, `PARTIAL`, or `INVALIDATED` verdict plus the constraint that produced it. Do not promote spike code to production without a normal implementation pass. See `references/feasibility-spikes.md`.

## Review and cleanup

Review the real diff before changing it. Separate findings into blocking correctness/security defects, safe cleanup, and risky design changes. For cleanup, search the surrounding codebase for an existing helper or contract before removing or consolidating anything. Apply only safe or clearly verified changes; leave public-contract and behavioral rewrites for explicit review. Run the narrowest relevant test/lint command after each meaningful change. See `references/pre-commit-review.md` and `references/cleanup-review.md`.

### Read-only audit references

| Audit target | Reference |
|---|---|
| ADRs, architecture docs, implementation plans, build logs | `references/read-only-engineering-artifact-audit.md` |
| Deployed PostgreSQL views & base schemas | `references/postgresql-view-schema-audit.md` — catalog-first inspection, deployed-vs-source diff, join cardinality, recursive effective-sample validation, PIT/leakage checks, NULL-aware confusion matrices, coverage-preserving left joins, snapshot re-anchoring, bounded secret claims, explicit no-change confirmation |
| Backend HTTP service & API contracts (origin/edge topologies, session redirects, telemetry sync) | `references/service-api-verification.md` |
| Testability & data-integrity of web/cloud/AI-backed apps | `references/testability-and-data-integrity-audit.md` — module-level side effects, loose relational string matching, NoSQL document-ID injection, in-memory sorting, client-secret leakage, AI prompt/fallback contract drift |
| LLM reverse proxies & OpenAI-compatible tool-calling gateways | `references/llm-gateway-tool-calling-verification.md` — contract compliance, multi-turn stateful pool continuity, adversarial verification |
| Vertical video re-framing & burned-in subtitles | `references/video-quality-framing-verification.md` — dual-layer composite boundaries, temporal hysteresis, displacement clamping, nonsense-token filtering |
| Deployed web mockup/frontend release audit | `references/web-ui-audit.md`; release-gate depth: `references/deep-web-release-audit.md` (live/source equivalence, transaction integrity, DOM-XSS proof, Three.js attribution, deployment ownership, no-change verification) |
| Phase/specification compliance | `references/spec-compliance-audit.md`; reproducible gate scripts & term matching: `references/phase-gate-verification.md` |
| Upstream dependency/server contract | `references/upstream-runtime-contract-audit.md` — SHA pinning, isolated fresh-install probes, MCP tool enumeration, read/mutation boundaries, backtest semantics, metadata drift, consumer no-change evidence |
| Daemon routines vs upstream in-review errors | `references/upstream-backoff-state-machine-verification.md` — idempotency backoff, zero-spamming invariants |
| Approved mockup → implementation | `references/frontend-redesign-promotion.md` — phase boundary, Git checkpoint/worktree isolation, static-SPA regression seams, cache busting, live promotion oracle; checkout/account/tracking flows: `references/transactional-ui-runtime-probes.md` |
| Delegated review finishing after implementation/ship | `references/late-review-release-gate.md` — anchor findings to the current revision, distinguish harness failures from product defects, reopen the gate, re-prove on the public target |

## Strict implementation and review guardrails

- **Test-first:** work in vertical `RED → GREEN → REFACTOR` slices. The first test must fail for the missing behavior—not a typo—and later tests must not be written as a speculative horizontal batch. Treat throwaway spikes and explicitly user-approved exceptions as exceptions, not a quiet escape from test-first work.
- **Pre-commit verification:** inspect the real diff, scan added lines for secrets and dangerous execution/deserialization patterns, then run the narrowest relevant tests/lint. Compare any failures with the pre-existing baseline; a newly introduced failure blocks completion.
- **Independent review:** for consequential code changes, use a fresh reviewer context and require evidence-backed findings. Keep any fix loop bounded and re-run the same checks after each change.
- **Cleanup:** search for established helpers and public contracts before simplifying. Apply only safe scope-local cleanup automatically; flag behavior, performance, concurrency, or public-API changes for explicit review.

The full prior checklists and recipes are preserved in `references/test-first-development.md`, `references/pre-commit-review.md`, and the `*-legacy.md` references.

For phase-based project execution (e.g. multi-phase build specs), execute tasks phase by phase. After completing each phase, run the phase verification gate (e.g. `python3 scripts/verify_phaseX.py` or unit/integration test suite) and commit the changes to Git with a descriptive commit message before advancing to the next phase. If `pytest` is unavailable in the execution environment, fall back to `PYTHONPATH=. python3 -m unittest discover -s tests -p "test_*.py"`. When running `pytest` in multi-directory or skill-bearing repos, scope test discovery to the target directory (`PYTHONPATH=. pytest tests/ -v`) or configure `testpaths = tests` in `pytest.ini` to prevent collection collisions (`ModuleNotFoundError`, `import file mismatch`) on sibling subtrees. When mocking `httpx.AsyncClient` methods in `unittest.IsolatedAsyncioTestCase` with `unittest.mock.patch`, ensure synchronous response methods like `.json()` return `MagicMock()` or a standard dict rather than `AsyncMock` to prevent `'coroutine' object is not subscriptable` errors. When output gets interrupted or cut off mid-turn (e.g. system cutoff or network error), continue directly from the exact truncation point without repeating prior context or restarting.
- **Handling mid-turn stream cutoffs:** When continuing from a `[System: The previous response was cut off ...]` prompt, do NOT repeat any already-sent text or headers. Jump straight into the cut-off word or sentence and finish the turn cleanly.

## Verification checklist

- [ ] The chosen lane's observable check was actually run.
- [ ] Claims distinguish evidence, hypothesis, and remaining risk.
- [ ] The final change is limited to the identified cause or requirement.
- [ ] Relevant tests, lint, or a runnable repro were re-run after edits.
- [ ] Remaining limitations are stated rather than implied away.
