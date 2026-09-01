---
name: github-repository-operations
description: Use when cloning, maintaining, auditing, or administering GitHub repositories at individual or fleet scale, including sparse clones, profile repositories, and bulk metadata changes.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, repositories, clone, sparse-checkout, profile-readme, bulk-operations]
    related_skills: [github-auth, github-pr-workflow, github-issues]
---

# GitHub Repository Operations

## Overview

Repository work ranges from one safe clone to a fleet-wide change. Authenticate first, identify scope, preview candidates, use native Git/GitHub tools, and require explicit approval before mutations that affect many repositories or public visibility.

## When to Use

- Creating, cloning, forking, configuring, releasing, or synchronizing repositories.
- Working with very large repositories or selected subdirectories.
- Updating a GitHub profile README or scanning many repositories.
- Applying a controlled bulk repository update through `gh` or the API.

## Core Workflow

1. Check `gh auth status` and repository remotes; use Git-only operations where API access is unnecessary.
2. For a single repository, prefer `gh repo` where it makes intent clear, otherwise use Git.
3. For fleet work, list/filter candidates and present the exact set before changing it.
4. Use bounded concurrency for network inspection; log each mutation and verify its returned state.
5. Keep public profile content concise—one curated projects view, no internal build notes, and no duplicate repo lists.

## Clone Modes

| Need | Command shape |
|---|---|
| Standard | `git clone <url>` |
| Shallow latest history | `git clone --depth=1 <url>` |
| Specific branch | `git clone --branch <branch> <url>` |
| Large repo / selected paths | `git clone --depth=1 --filter=blob:none --sparse <url> <dir>` |

For sparse clones:

```bash
cd <dir>
git sparse-checkout set pathA/ pathB/
git sparse-checkout add pathC/
# Later, restore the complete tree:
git sparse-checkout disable
```

This needs Git 2.25+ and avoids fetching unnecessary blobs.

## Bulk Operations

Use `gh api --paginate` or a bounded Python I/O worker for discovery. Filter forks/archived repos as needed, save the candidate list, then make one auditable API call per approved repository. Do not hide visibility changes or other destructive mutations behind a broad loop.

```bash
for repo in approved-a approved-b; do
  gh api -X PATCH repos/<owner>/$repo -f private=true
done
```

## Profile Repository

The `<username>/<username>` repository is a public profile artifact. Keep its README focused on current work, consolidate overlapping project sections, and remove authoring/meta commentary that visitors do not need.

## Verification Checklist

- [ ] Auth and target owner/repository were confirmed.
- [ ] Large or destructive scope was previewed before mutation.
- [ ] Sparse paths or clone mode match the task.
- [ ] Bulk operations logged each repository and verified results.
- [ ] Profile content contains no redundant or internal-facing sections.
