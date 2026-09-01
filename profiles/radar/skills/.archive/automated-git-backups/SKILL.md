---
name: automated-git-backups
description: Setup silent, automated Git backups using rsync, git porcelain, and no_agent cronjobs.
---

# Automated Git Backups

Use this pattern when setting up automated, silent backups of active application directories (like `~/.hermes/` or app configs) to a Git repository.

## The Pattern

Never `git init` directly inside an active application directory. It causes file locking issues, clutters the app directory, and risks accidental commits of massive active databases. Instead, use a separate staging directory and `rsync`.

### 1. Setup Staging & Ignore
Create a dedicated backup repo directory and a `.gitignore` that ruthlessly filters out:
- Databases (`*.db`, `*.db-shm`, `*.db-wal`)
- Logs (`logs/`, `*.log`)
- Caches and temporary state files
- Large downloaded binaries

### 2. The Sync Script
Create a bash script in the staging directory (e.g., `sync.sh`):
```bash
#!/bin/bash
SOURCE_DIR="$HOME/.hermes/"
TARGET_DIR="/mnt/backup-repo/data/"
REPO_DIR="/mnt/backup-repo"

mkdir -p "$TARGET_DIR"
# Sync while respecting the repo's gitignore
rsync -a --delete --exclude-from="$REPO_DIR/.gitignore" "$SOURCE_DIR" "$TARGET_DIR"

cd "$REPO_DIR"
git add .
# Check if changes exist before committing
if git status --porcelain | grep -q .; then
    git commit -m "Auto backup: $(date +'%Y-%m-%d %H:%M:%S')"
    git push -u origin master
fi
```

### 3. Hermes Cronjob Deployment
Schedule the script using a `no_agent=true` cronjob so it runs completely silently as a background watchdog without consuming AI tokens or spamming the chat:
```python
cronjob(
    action="create",
    name="Git Backup Watchdog",
    schedule="every 1h",
    script="sync.sh",
    no_agent=True, # CRITICAL: Makes the job run the script directly and silently
    enabled_toolsets=["terminal"]
)
```

## Pitfalls
- **Missing `--delete` in rsync:** Without `--delete`, deleted files in the source will never be removed from the backup repo.
- **Pushing without checking changes:** Always use `git status --porcelain | grep -q .` before committing to avoid empty commit errors and spamming the git history.
- **Excluding .env:** Explicitly manage whether `.env` or files containing secrets should be backed up, depending on repo visibility (private vs public).