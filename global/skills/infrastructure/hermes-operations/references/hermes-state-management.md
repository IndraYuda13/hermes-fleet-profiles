---
name: hermes-state-management
description: Use when backing up, restoring, sizing, or safely managing Hermes Agent state such as configuration, skills, profiles, session databases, and durable memory.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, backup, restore, memory, state, cron, rsync, rclone]
    related_skills: [hermes-agent]
---

# Hermes State Management

## Overview

Hermes state needs two different treatment modes: compact durable memory for high-signal facts, and external backups/files for exact or large material. Never treat the live `.hermes` directory as a Git working tree.

## When to Use

- Backing up or restoring `~/.hermes` / `$HERMES_HOME`.
- Choosing a storage strategy for skills, profiles, config, sessions, logs, and databases.
- A memory entry or user profile is too large, needs exact preservation, or needs a current capacity check.

## Decide What Belongs Where

| Material | Preferred home |
|---|---|
| Compact durable facts and preferences | Hermes memory |
| Large/exact documents and reference material | File, skill support file, or user-managed repository |
| Config, skills, plugins, profiles | Backup target with secret-aware exclusions |
| Sessions/databases/logs | Backup deliberately; exclude from source-control snapshots unless specifically required |

Inspect the active configuration or official docs before quoting memory limits: providers and configured `memory_char_limit`/`user_char_limit` can vary. Do not bulk-edit source constants to change memory behavior.

## Backup Patterns

1. **Rsync to another host:** use SSH keys and selective excludes for logs/cache as appropriate.
2. **Rclone to cloud storage:** test the configured remote first; retain an exclusion policy for bulk runtime data.
3. **Git snapshot:** use a separate staging repository, not `~/.hermes` itself.

A Git snapshot needs a secret-aware `.gitignore` that excludes at least databases/WAL files, logs, caches, sessions as desired, `.env`, auth material, and any sensitive config. Mirror with `rsync -a --delete`, then commit only when `git status --porcelain` is non-empty.

```bash
rsync -a --delete --exclude-from="$REPO_DIR/.gitignore" "$HERMES_HOME/" "$TARGET_DIR/"
cd "$REPO_DIR"
git add .
git status --porcelain | grep -q . && git commit -m "Auto backup: $(date -Is)"
```

Schedule deterministic backup scripts with a `no_agent=True` local-delivery cron job so they run without model calls or delivery spam. Test the script manually before scheduling it.

## Restore Safely

1. Stop or quiesce state-writing services before replacing state.
2. Make a timestamped local safety copy first.
3. Restore only the selected state categories; preserve platform-specific secrets/paths unless intentionally migrating them.
4. Update absolute paths and verify permissions.
5. Start Hermes and validate config, skills, and one non-destructive session/read path before declaring recovery complete.

## Common Pitfalls

- Versioning secrets or mutable databases in a Git backup.
- Initializing a Git repository inside live application state.
- Backing up logs/cache indiscriminately until cost or size makes recovery impractical.
- Forcing large documents into memory instead of storing them as files and reading on demand.
- Assuming a historical numeric memory limit is a current configuration contract.

## Verification Checklist

- [ ] Backup source and destination are explicit.
- [ ] Secret/database/session exclusion policy was reviewed.
- [ ] Backup script completed a manual dry run or controlled test.
- [ ] Cron uses the intended mode and delivery behavior.
- [ ] Restore, when performed, was verified through live Hermes checks.
