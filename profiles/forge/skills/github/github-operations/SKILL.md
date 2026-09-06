---
name: github-operations
description: Use when authenticating with GitHub or managing repositories, issues, pull requests, reviews, releases, CI, sparse clones, or scoped bulk operations.
version: 1.0.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [github, git, pull-requests, issues, review, ci, repositories]
---

# GitHub Operations

## Overview

This umbrella covers the GitHub lifecycle from credentials and repository access through issues, pull requests, reviews, releases, CI, and controlled batch operations. Prefer `gh` when it is authenticated; use `git` plus the REST API only when necessary. Keep an explicit repository/owner scope and verify every mutating action from its response or resulting state.

## Start with auth and scope

Check `gh auth status`, the current remote, and the repository owner/name before API actions. If `gh` is unavailable, use an approved token source without printing it. Configure commit identity separately from API access. The full auth fallback and helper are in `scripts/gh-env.sh` and `references/github-auth.md`.

## Repository, clone, and inventory operations

Use `git`/`gh repo` to clone, create, fork, configure remotes, manage releases, secrets, and Actions. For a large monorepo or a request for only selected directories, use a shallow blob-filtered sparse clone, then `git sparse-checkout set <dirs>`; verify with `git sparse-checkout list`. See `references/repository-and-sparse-clone.md` and `references/github-api-cheatsheet.md`.

### Codebase inventory

When the question is repository size or language composition rather than a GitHub mutation, run `pygount --format=summary` with explicit exclusions for `.git`, dependency directories, virtual environments, caches, and build artifacts. Use suffix filters for huge monorepos; interpret Markdown as documentation/comment content rather than executable LOC. Command variants and output interpretation are retained in `references/codebase-inspection-legacy.md`.

## Issues and pull requests

For issues: capture the report, classify/label/assign deliberately, and use templates for bug reports or feature requests. For pull requests: create a focused branch, commit only intended files, push, open the PR with a summary and test plan, then inspect CI rather than assuming it is green. See `references/issues-and-prs.md` and `templates/`.

### Commit metadata and cryptographic invariants

Never attempt to self-reference a commit's own SHA inside files tracked within that same commit (e.g. evidence manifests or closure reports). Changing the file changes the tree hash, preventing `git commit --amend` loops from ever converging. Always pin the target snapshot commit being audited, or attach post-commit metadata via Git tags or external release records. See `references/git-commit-hash-invariants.md`.

## Review workflow

Read PR metadata and changed files before the diff. For each meaningful change, inspect enough surrounding code to validate its contract; run focused checks when the repository permits. Post only evidence-backed findings, separated into blocking defects, warnings, and suggestions. Do not approve based on a summary alone. See `references/code-review.md`.

## Scoped bulk work and profile content

For repeated actions, first list the concrete target set, dry-run/read it, then apply narrowly with rate-conscious loops or a bounded parallel script. Keep output concise and verify every target's final state. GitHub profile README edits are normal repository edits: remove redundant public content, retain unique project links, and avoid exposing internal workflow notes. See `references/bulk-and-profile-operations.md`.

## Verification checklist

- [ ] Auth method and owner/repository scope are known.
- [ ] The target object(s) were read before a mutating action.
- [ ] Repository, issue, PR, or CI result confirms the requested outcome.
- [ ] For code changes, the diff and focused validation were inspected.
- [ ] Batch operations report successes and exceptions separately.
