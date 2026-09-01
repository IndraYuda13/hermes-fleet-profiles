---
name: github-sparse-clone
description: "Clone huge repositories quickly using sparse-checkout and blob filtering to save disk space and bandwidth."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Repositories, Git, Clone, Sparse]
    related_skills: [github-repo-management]
---

# GitHub Sparse Clone (Partial Clone)

When cloning massive repositories where only specific subdirectories are needed, a normal `git clone` or even a shallow clone (`--depth=1`) can still pull too much data, or fail on timeout.

Use Git's built-in sparse-checkout combined with blob filtering to dramatically speed up the clone and save disk space.

## Prerequisites

- Git version 2.25.0 or newer (for the modern `git sparse-checkout` command).

## Cloning a Repository Sparsely

### 1. The Clone Command

Execute a clone that downloads the tree but skips the file blobs (contents) and history.

```bash
cd /mnt  # or your target directory
git clone --depth=1 --filter=blob:none --sparse https://github.com/owner/repo-name.git my_local_folder
```

**Flags explained:**
- `--depth=1`: Only get the latest commit history (shallow clone).
- `--filter=blob:none`: Tells Git to skip downloading file contents until they are explicitly needed.
- `--sparse`: Initializes the sparse-checkout file so the working directory starts empty (except for root files).

### 2. Specifying Directories

Once cloned, navigate into the directory and tell Git exactly which folders you want to populate. Git will then download only the blobs for those specific files.

```bash
cd my_local_folder
# Specify exactly which directories you want.
# Note: Root directory files (like README, .gitignore) are usually pulled by default.
git sparse-checkout set folderA/ folderB/
```

### 3. Adding More Directories Later

If you realize you need another folder later, use `add` instead of `set` (which overwrites).

```bash
git sparse-checkout add folderC/
```

### 4. Reverting to Full Clone (Optional)

If you decide you need the whole repository after all:

```bash
git sparse-checkout disable
```

## When to use this skill

- The user asks to clone a very large monorepo or specific folders from a repo.
- The user explicitly mentions "don't clone the whole thing", "it's too big", or "just grab folder X".
- Normal `git clone` times out or uses too much disk space.