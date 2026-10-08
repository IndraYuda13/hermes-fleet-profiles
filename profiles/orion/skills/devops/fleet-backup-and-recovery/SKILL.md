---
name: fleet-backup-and-recovery
description: Use when syncing, backing up, or recovering fleet profiles.
version: 1.1.0
author: Hermes Fleet Architecture
license: MIT
metadata:
  hermes:
    tags: [fleet, backup, disaster-recovery, git-sync, secrets-vault]
    category: devops
    requires_toolsets: [terminal, file]
---

# Fleet Sync, Backup & Disaster Recovery

Standard operating procedure for synchronizing, validating, and performing dual-layer disaster recovery backups across the multi-agent Hermes fleet.

## Dual-Layer Backup Architecture

Public or audited Git repositories sanitize secrets (`REDACTED` or `${...}`). Therefore, Git alone cannot restore a fully functional fleet on bare metal without manual credential re-entry. Always maintain a dual-layer backup:

1. **Declarative Git Layer (`hermes-fleet-profiles`):**
   - Versioned prompts (`SOUL.md`), sanitized configs (`config.yaml`), `profile.yaml`, and custom skills across all active profiles.
   - Pushed to remote Git repo after passing all fleet policy gates and test suites.
   - Paired with an uncompressed declarative snapshot (`<timestamp>-fleet-complete`) on the offload volume for zero-git bare-metal rollbacks.
2. **Disaster Recovery Secrets Layer (`secrets-live-<timestamp>`):**
   - Stored in an offload volume (e.g. `/mnt/hermes-storage-offload/hermes-fleet-backups/`) with restricted permissions (`chmod 700` directories, `chmod 600` files).
   - Preserves live `.env`, `auth.json`, unredacted `config.yaml` (as `config.yaml.raw`), active `cron/jobs.json`, and `memories/` for root and every active profile.
   - Captures root-level service tokens (e.g. `gsc_service_account.json`, `google_token.json`).
   - Enables immediate restoration on a new host without re-authenticating Telegram bots or rotating LLM API keys.

## Sync & Verification Procedure

When running the declarative fleet sync script (`sync.sh`):

1. **Pre-flight Profile Audit:**
   - Verify every active profile directory under `$HERMES_ROOT/profiles/` (e.g. `atlas`, `aurora`, `forge`, `frame`, `groupbot`, `lens`, `nexus`, `orion`, `prism`, `quant`, `radar`, `sentinel`, `testing`) is explicitly declared in `KNOWN_PROFILES`.
2. **Environment & YAML Interpreter Resolution:**
   - Do not assume host `python3` has `yaml` (PyYAML). Resolve the interpreter via `$HERMES_ROOT/venv/bin/python` or the active virtualenv before running sanitization.
   - Resolve `$HERMES_ROOT` dynamically: `$HERMES_HOME` -> `/root/.hermes` -> `$HOME/.hermes`.
3. **Governance & Role-Separation Checks:**
   - Enforce profile role boundaries before running test suites. Non-design profiles (e.g. `orion`) must have UI-only toolsets like `ui-ux-pro-max` explicitly disabled (`enabled: false`) to pass `validate_fleet.py`.
4. **Verification Gates Before Git Push:**
   - Execute `python3 validate_fleet.py` (policy checks).
   - Execute `python3 validate_contracts.py` (A2A timeout and schema checks).
   - Run the full pytest suite (`pytest -q`).
   - Push to Git remote only when 100% of tests and policy checks pass.

## Backup Verification & Drift Audit Procedure

When auditing whether the fleet is currently backed up or has drifted:

1. **Declarative Git Layer Verification:**
   - Check the latest commit on remote Git repo (`git log -1` on `hermes-fleet-profiles`).
   - Verify working tree clean status (`git status`).
   - Audit drift against live `$HERMES_ROOT/profiles/` (new/modified skills, SOUL.md, config.yaml, or newly activated profiles) to identify uncommitted changes.
2. **Disaster Recovery Secrets Layer Audit:**
   - Inspect offload volume (`/mnt/hermes-storage-offload/hermes-fleet-backups/`).
   - Verify timestamps of the newest `<timestamp>-fleet-complete` declarative snapshot and `secrets-live-<timestamp>` directory against live updates.
   - Audit whether all active profiles and root-level tokens are captured in the latest secrets layer.
3. **Pre-Backup Test Suite Gate:**
   - Run `pytest -q` in repo root before executing any sync or backup. All policy and contract tests must pass 100% cleanly.

## Secrets Offload & Permission Invariants

When creating the Disaster Recovery Secrets Layer (`secrets-live-<timestamp>`):
- **Atomic Permission Lockdown:** Immediately enforce POSIX permissions on the target directory:
  ```bash
  find "${SECRETS_DEST}" -type d -exec chmod 700 {} +
  find "${SECRETS_DEST}" -type f -exec chmod 600 {} +
  ```
- **Profile Scope Checklist:** Ensure every active profile exports:
  - `.env` (environment variables and API credentials)
  - `auth.json` (platform tokens)
  - `config.yaml` copied as `config.yaml.raw` (raw unredacted config)
  - `cron/` (scheduler database and active jobs)
  - `memories/` (`USER.md` and `MEMORY.md` persistent state)

## Archive Timeout & Storage Guard

When creating live snapshots or tarball archives of `/root/.hermes/profiles/`:
- **Mandatory Exclusions:** Always exclude heavy dynamic caches:
  `--exclude='cache'` `--exclude='sandboxes'` `--exclude='terminal-sessions'`
  `--exclude='browser-profile'` `--exclude='lsp/node_modules'` `--exclude='home/.npm'`
  `--exclude='home/.cache'` `--exclude='*.db-wal'` `--exclude='*.db-shm'`
- **Mechanism:** Profile directories often contain multi-hundred-megabyte browser binaries and node_modules. Archiving without exclusions causes foreground command timeouts (exit code 124) and risks disk saturation.
