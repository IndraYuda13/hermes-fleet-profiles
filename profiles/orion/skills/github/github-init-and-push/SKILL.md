---
name: github-init-and-push
description: Use when creating and pushing new GitHub repos.
---

# GitHub Init and Push

## Overview

Use when publishing a local workspace or project to a new GitHub repository (`gh repo create --source=. --push`).

## Procedure

1. **Pre-push hygiene & secret audit:**
   - Inspect `.gitignore` and `git status`.
   - Run `git ls-files | grep -E "(\.env|secret|key|token)"` to verify no live credentials or un-gitignored `.env` files are tracked. Only `.env.example` templates should be committed.
2. **README verification:**
   - Verify that `README.md` exists and clearly documents project overview, features, tech stack, environment variables, and run/build commands before initial push.
3. **Remote repository creation:**
   - Check if remote or GitHub repository already exists (`git remote -v && gh repo view <owner>/<repo>`).
   - Default to `--private` unless explicitly instructed otherwise:
     ```bash
     gh repo create <owner>/<repo> --source=. --remote=origin --private --push --description "<description>"
     ```
4. **Verification:**
   - Confirm branch tracking and fetch URL via `git remote -v` and `gh repo view <owner>/<repo>`.
