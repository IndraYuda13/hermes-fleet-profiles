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

## Test-first implementation

For behavior changes, write the smallest red test or executable assertion at the affected seam, make the minimal change to turn it green, then refactor only while it stays green. A manual happy-path check is supplementary, not proof of a regression fix. Use focused tests first, then the project's relevant broader validation. See `references/test-first-development.md`.

## Python environment diagnosis

Use the interpreter that runs the application to inspect `sys.executable`, `sys.path`, package metadata, and the import itself. Check for local files shadowing package names before reinstalling. For service failures, inspect the service's `ExecStart` interpreter and environment rather than assuming an interactive shell's venv is relevant. See `references/python-environment.md`.

## Disposable feasibility spikes

A spike answers one observable risk and is throwaway by default. State the question as Given/When/Then, choose the riskiest unknown first, build the smallest runnable artifact, exercise edge cases, and finish with a `VALIDATED`, `PARTIAL`, or `INVALIDATED` verdict plus the constraint that produced it. Do not promote spike code to production without a normal implementation pass. See `references/feasibility-spikes.md`.

## Review and cleanup

Review the real diff before changing it. Separate findings into blocking correctness/security defects, safe cleanup, and risky design changes. For cleanup, search the surrounding codebase for an existing helper or contract before removing or consolidating anything. Apply only safe or clearly verified changes; leave public-contract and behavioral rewrites for explicit review. Run the narrowest relevant test/lint command after each meaningful change. See `references/pre-commit-review.md` and `references/cleanup-review.md`.

For read-only audits of ADRs, architecture documents, implementation plans, build logs, deployed SQL views, and base schemas, use `references/read-only-engineering-artifact-audit.md` and `references/postgresql-view-schema-audit.md`. The PostgreSQL guide adds catalog-first inspection, deployed-definition versus source comparison, join-cardinality checks, recursive effective-sample validation, PIT/leakage checks, NULL-aware confusion matrices, coverage-preserving left joins, and explicit no-change confirmation. It adds snapshot re-anchoring, actionable-plan criteria, reproducible build-log evidence, bounded secret claims, negative-path consistency checks, and explicit no-change confirmation.

For an independent read-only release audit of a deployed web mockup/frontend, use `references/web-ui-audit.md`; `references/deep-web-release-audit.md` adds a compact release-gate checklist for live/source equivalence, transaction integrity, DOM-XSS proof, Three.js mobile attribution, deployment ownership, and no-change verification. For a read-only phase/specification compliance audit, use `references/spec-compliance-audit.md` and `references/phase-gate-verification.md` for reproducible phase-gate verification scripts and term matching. For a read-only upstream dependency/server audit, use `references/upstream-runtime-contract-audit.md`: it covers SHA pinning, isolated fresh-install probes, runtime MCP tool enumeration, read/mutation boundaries, storage/schema inspection, backtest and resolution semantics, metadata drift, and consumer-project no-change evidence. When an audited mockup is approved for implementation, follow `references/frontend-redesign-promotion.md` for the audit-to-code phase boundary, Git checkpoint/worktree isolation, static-SPA regression seams, CSS-3D trade-offs, responsive/deep-flow verification, Cloudflare nested-asset cache busting, and the live promotion oracle. For checkout/account/tracking mockups, also run `references/transactional-ui-runtime-probes.md`: it covers concurrent source-change detection, stale async callbacks, implicit Enter in native dialog forms, payment-method consistency, timer expiry, product-specific validation, composed motion-pause reasons, and search combobox semantics. If delegated or independent review finishes after implementation or an earlier completion message, use `references/late-review-release-gate.md` to anchor findings to the current revision, distinguish harness failures from product defects, reopen the release gate honestly, and re-prove the fix on the public target.

## Strict implementation and review guardrails

- **Test-first:** work in vertical `RED → GREEN → REFACTOR` slices. The first test must fail for the missing behavior—not a typo—and later tests must not be written as a speculative horizontal batch. Treat throwaway spikes and explicitly user-approved exceptions as exceptions, not a quiet escape from test-first work.
- **Pre-commit verification:** inspect the real diff, scan added lines for secrets and dangerous execution/deserialization patterns, then run the narrowest relevant tests/lint. Compare any failures with the pre-existing baseline; a newly introduced failure blocks completion.
- **Evidence & Manifest Revision Locking (Self-Referential SHA Resolution):** Manifests, QA audits, and verification records must never attempt to store their own commit SHA (which creates an impossible circular dependency / self-referential hash). Instead, lock all phase manifests (design, implementation, QA, closure) to the sealed implementation commit SHA (`feat: ...` where the code was frozen and verified). Evidence, reports, and screenshots are then committed or squashed cleanly on top without mutating the verified target revision.
- **Independent review:** for consequential code changes, use a fresh reviewer context and require evidence-backed findings. Keep any fix loop bounded and re-run the same checks after each change.
- **Cleanup:** search for established helpers and public contracts before simplifying. Apply only safe scope-local cleanup automatically; flag behavior, performance, concurrency, or public-API changes for explicit review.

The full prior checklists and recipes are preserved in `references/test-first-development.md`, `references/pre-commit-review.md`, and the `*-legacy.md` references. For dynamic static asset endpoints and test traversal URL normalization pitfalls, see `references/secure-static-asset-endpoints.md`. For lightweight Swagger UI embedding, OpenAPI 3.0 specs, PEP 621 pyproject.toml packaging, and CI testing discovery, see `references/openapi-swagger-and-packaging.md`. For zero-dependency multi-threaded telemetry servers, live template reloading, anti-caching headers, and log-driven state aggregation using pure Python standard library (`http.server` + `ThreadingMixIn`), see `references/pure-python-telemetry-server.md`. For FastAPI HTTP HEAD 405 probe pitfalls, root entrypoint proxies, and decoupled systemd worker/web services, see `references/fastapi-probes-and-service-architecture.md`. For defensive upstream JSON parsing (`dict.get` null pitfalls with `or []`) and systemd service proxy updates, see `references/defensive-json-parsing-and-upstream-resilience.md`.

For phase-based project execution (e.g. multi-phase build specs), execute tasks phase by phase. After completing each phase, run the phase verification gate (e.g. `python3 scripts/verify_phaseX.py` or unit/integration test suite) and commit the changes to Git with a descriptive commit message before advancing to the next phase. If `pytest` is unavailable in the execution environment, fall back to `PYTHONPATH=. python3 -m unittest discover -s tests -p "test_*.py"`. When mocking `httpx.AsyncClient` methods in `unittest.IsolatedAsyncioTestCase` with `unittest.mock.patch`, ensure synchronous response methods like `.json()` return `MagicMock()` or a standard dict rather than `AsyncMock` to prevent `'coroutine' object is not subscriptable` errors. When output gets interrupted or cut off mid-turn (e.g. system cutoff or network error), continue directly from the exact truncation point without repeating prior context or restarting.
- **Handling mid-turn stream cutoffs:** When continuing from a `[System: The previous response was cut off ...]` prompt, do NOT repeat any already-sent text or headers. Jump straight into the cut-off word or sentence and finish the turn cleanly.

## Verification checklist

- [ ] The chosen lane's observable check was actually run.
- [ ] Claims distinguish evidence, hypothesis, and remaining risk.
- [ ] The final change is limited to the identified cause or requirement.
- [ ] Relevant tests, lint, or a runnable repro were re-run after edits.
- [ ] Remaining limitations are stated rather than implied away.
