---
name: code-review-workflows
description: Use when reviewing a pull request, requesting review for completed changes, or deciding whether code is safe to commit, push, merge, or approve.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [code-review, pull-requests, pre-commit, verification, github, quality]
    related_skills: [github-auth, github-repo-management, test-driven-development, systematic-debugging]
---

# Code Review Workflows

## Overview

Review has two different directions: verify your own pending changes before they land, or assess somebody else’s pull request. In both cases, inspect the actual diff and surrounding code, run appropriate checks, classify findings by severity, and keep side effects—such as posting a formal GitHub review—explicit.

## When to Use

- Before committing, pushing, merging, or declaring an implementation complete.
- Reviewing local changes, a GitHub pull request, or a proposed patch.
- Requesting an independent review after a non-trivial implementation or bug fix.

Do not substitute a review for reproducing and fixing a known bug; use systematic debugging first.

## First Decide the Review Direction

| Situation | Primary work | External side effect |
|---|---|---|
| Your uncommitted or just-finished changes | Pre-commit verification | None unless user asks to commit/push. |
| Another contributor’s PR | PR review | Posting comments/approval requires explicit user direction. |
| Need fresh eyes on a substantial change | Independent review | Share the diff and requirements, not implementation narrative. |

## Pre-Commit Verification

1. Inspect scope: `git status`, `git diff --cached` (then `git diff` if unstaged), and a stat summary.
2. Read changed files in context; scan added lines for credentials, injection sinks, unsafe deserialization, debug code, and conflict markers.
3. Run focused tests, then project checks relevant to the affected language. Existing baseline failures are not newly introduced regressions.
4. Use an independent reviewer context for non-trivial changes. Give it the requirements, diff, test output, and a structured verdict schema.
5. Fix blocking correctness or security findings, then rerun the same checks. A clean status from the reviewer never overrides a failing real test.

## Reviewing a GitHub Pull Request

1. Gather PR metadata, changed file names, checks, and base/head branches with `gh pr view`, `gh pr diff`, and `gh pr checks` (or REST equivalents).
2. Inspect the diff and full context in a local checkout. Do not review solely from a summary.
3. Apply the checklist below, run safe relevant tests if possible, and write evidence-backed findings with path and line references.
4. Choose the outcome: **approve** only if no blocking issue; **request changes** for correctness/security/test-blocking problems; **comment** for non-blocking observations.
5. Post a formal review or inline comments only when the user asked for that external action. Otherwise, report the review in chat.

## Review Checklist

- **Correctness:** intended behavior, boundaries, error paths, concurrency, state transitions.
- **Security:** secrets, validation, authorization, injection, traversal, unsafe subprocesses/deserialization.
- **Testing:** focused regression coverage, meaningful error paths, actual command output.
- **Maintainability:** clear responsibilities, no needless duplication or abstraction, appropriate documentation.
- **Operations:** config migration, observability, resource use, rollback consequences where relevant.

## Findings Format

```text
## Review Summary
Verdict: Approve | Request changes | Comment | Needs investigation

### Blocking
- path:line — evidence, impact, and a concrete correction.

### Non-blocking
- path:line — improvement or coverage gap.

### Verified
- Exact test/check command and observed result.
```

Do not invent findings to make a review look thorough. If a concern cannot be demonstrated from the diff, context, or check output, label it as a question rather than a defect.

## Common Pitfalls

- **Reviewing only the diff:** surrounding callers and invariants can overturn a seemingly safe patch.
- **Treating agent output as proof:** inspect the diff and run checks independently.
- **Scope creep during review:** report unrelated cleanup separately; do not block a sound patch for cosmetic preferences.
- **Silent external posting:** approvals, request-changes, and comments are user-visible side effects.
- **No severity boundary:** distinguish blockers from suggestions so authors know what must change.

## Verification Checklist

- [ ] Review direction and user authority to post externally were clear.
- [ ] Actual diff and relevant context were read.
- [ ] Relevant checks were run or their absence was stated.
- [ ] Every blocker cites evidence and a location.
- [ ] Review outcome matches the findings.
