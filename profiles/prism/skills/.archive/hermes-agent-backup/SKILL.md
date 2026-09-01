---
name: hermes-agent-backup
description: Configure automated external backups for Hermes Agent data (.hermes directory) via rsync, rclone, or git using internal cron jobs.
---

# Hermes Agent Backup

Hermes Agent stores its critical state—skills, plugins, configuration, cron jobs, profiles, and the SQLite memory/history database (`state.db`)—in the `~/.hermes/` directory. Since there is no native `hermes backup --cloud` command, automated external backups must be configured using the agent's built-in `cronjob` tool combined with standard Linux utilities.

This skill outlines the three standard methods for backing up the `~/.hermes/` directory to an external location.

## Target Directory

The target for all backup operations is:
`~/.hermes/` (or `$HERMES_HOME` if configured differently).

**Crucial exclusions:** 
- If backing up to Git, the SQLite database (`state.db` / `hermes.db`) and secrets (`.env`, `config.yaml` if it contains keys) MUST be excluded via `.gitignore` as the database changes constantly and secrets should not be version controlled.
- `logs/` directory should generally be excluded from remote backups to save bandwidth.
- `sessions/` can grow large; consider excluding `.jsonl` or `.json` snapshot files if storage is a concern.

## Method 1: Rsync (Backup to another Server/VPS)

Best for: Fast, secure, differential backups to an existing remote machine.

1. Ensure SSH keys are configured for passwordless login to the target VPS.
2. Create a cron job using the `cronjob` tool:

```python
cronjob(
    action='create',
    schedule='0 2 * * *', # Daily at 2 AM
    prompt="Run the rsync backup script to mirror ~/.hermes/ to the remote backup server.",
    script="""#!/bin/bash
rsync -avz --exclude 'logs/' ~/.hermes/ user@remote_host:/path/to/backup/hermes_backup/
"""
)
```

## Method 2: Rclone (Backup to Cloud Storage)

Best for: Free/cheap storage (Google Drive, AWS S3, Cloudflare R2, Dropbox) without needing a second server.

1. Ensure `rclone` is installed (`sudo apt install rclone` or via script) and configured with a remote (e.g., `my_gdrive:`).
2. Create a cron job using the `cronjob` tool:

```python
cronjob(
    action='create',
    schedule='0 3 * * *', # Daily at 3 AM
    prompt="Run the rclone backup script to sync ~/.hermes/ to cloud storage.",
    script="""#!/bin/bash
rclone sync ~/.hermes/ my_gdrive:hermes_backup/ --exclude "logs/**" -v
"""
)
```

## Method 3: Git (Backup to a Private Repository)

Best for: Versioning `skills/`, `plugins/`, and `profiles/` configurations.

**Warning:** Do NOT commit `state.db`, `hermes.db`, `.env`, or sensitive `config.yaml` data.

1. Initialize a git repository in a separate directory (e.g., `~/hermes-backup-repo/`).
2. Create a rigorous `.gitignore` in that repo:
   ```text
   # Ignore databases
   *.db
   *.db-shm
   *.db-wal
   
   # Ignore logs & runtime state
   logs/
   gateway.pid
   gateway.lock
   gateway_state.json
   
   # Ignore caches & heavy dynamic data
   cache/
   audio_cache/
   image_cache/
   browser_recordings/
   sessions/
   sandboxes/
   
   # Ignore binaries
   lsp/
   bin/
   
   # Ignore system generated files
   *cache.json
   *.bak*
   processes.json
   auth.lock
   .update_check
   .restart_last_processed.json
   ```
3. Create a cron job using the `cronjob` tool. Set `no_agent=True` and `deliver='local'` (to prevent stdout spamming the chat on every commit):

```python
cronjob(
    action='create',
    schedule='every 60m', 
    name='Github Backup Watchdog',
    no_agent=True,
    deliver='local', # CRITICAL: Prevents silent watchdog spam
    prompt="Auto sync .hermes configuration to private github repository",
    script=\"\"\"#!/bin/bash
SOURCE_DIR="$HOME/.hermes/"
TARGET_DIR="$HOME/hermes-backup-repo/hermes-data/"
REPO_DIR="$HOME/hermes-backup-repo"

mkdir -p "$TARGET_DIR"

# Fast rsync excluding gitignored files
rsync -a --delete --exclude-from="$REPO_DIR/.gitignore" "$SOURCE_DIR" "$TARGET_DIR"

cd "$REPO_DIR"
git add .
if git status --porcelain | grep -q .; then
    git commit -m "Auto backup: $(date +'%Y-%m-%d %H:%M:%S')"
    git push -u origin master
fi
\"\"\"
)
```

## Restoring Git Backups Locally (Windows/Linux)

To sync a remote Git backup back to a local Hermes instance (e.g., pulling VPS config to a local Windows machine), use a symlink/junction rather than cloning directly into `.hermes`. This avoids nested path issues when the repo contains subfolders (like `hermes-data/`).

**Windows (PowerShell):**
```powershell
git clone <URL_REPO> "C:\\Users\\<User>\\hermes-backup"
if (Test-Path "C:\\Users\\<User>\\.hermes") { Rename-Item "C:\\Users\\<User>\\.hermes" ".hermes_backup" -Force }
New-Item -ItemType Junction -Path "C:\\Users\\<User>\\.hermes" -Target "C:\\Users\\<User>\\hermes-backup\\hermes-data"
```

**Linux/Mac:**
```bash
git clone <URL_REPO> ~/hermes-backup
mv ~/.hermes ~/.hermes_backup
ln -s ~/hermes-backup/hermes-data ~/.hermes
```
Update absolute paths in `config.yaml` post-restore.

## Creating the Cron Job via Hermes

When the user selects a backup method, use the `cronjob(action='create', ...)` tool directly to set it up, defining the `script` parameter as shown above, and ensuring `no_agent=True` is set if the script requires no LLM processing (which is true for all these backup scripts). 

Example tool call:
```python
cronjob(
    action='create',
    schedule='0 2 * * *',
    name='hermes_rsync_backup',
    no_agent=True,
    script='rsync -avz --exclude "logs/" ~/.hermes/ user@remote_host:/path/to/backup/'
)
```