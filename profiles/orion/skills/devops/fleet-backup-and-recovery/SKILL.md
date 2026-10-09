---
name: fleet-backup-and-recovery
description: Use when syncing, backing up, or recovering fleet profiles.
version: 1.7.0
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

Public or audited Git repositories sanitize secrets (`REDACTED` or `${...}`). Therefore, Git alone cannot restore a fully functional fleet on bare metal without manual credential re-entry. Always maintain a dual-layer backup with synchronized ISO UTC timestamps (`TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)`):

1. **Declarative Git Layer (`hermes-fleet-profiles`):**
   - Versioned prompts (`SOUL.md`), sanitized configs (`config.yaml`), `profile.yaml`, and custom skills across all active profiles.
   - Pushed to remote Git repo after passing all fleet policy gates, sanitization checks, and test suites.
   - Paired with an uncompressed declarative snapshot (`<timestamp>-fleet-complete`) on the offload volume for zero-git bare-metal rollbacks.
2. **Disaster Recovery Secrets Layer (`secrets-live-<timestamp>`):**
   - Stored in an offload volume (e.g. `/mnt/hermes-storage-offload/hermes-fleet-backups/`) with restricted permissions (`chmod 700` directories, `chmod 600` files).
   - Preserves live `.env`, `auth.json`, unredacted `config.yaml` (as `config.yaml.raw`), active `cron/jobs.json`, and `memories/` for root and every active profile.
   - Captures root-level service tokens and raw configs: `root.env`, `root.auth.json`, `root.google_token.json`, `root.gsc_service_account.json`, and `root.config.yaml.raw`.
   - Preserves operational plans under `$HERMES_ROOT/plans/` to retain in-flight multi-step architecture and implementation plans.
   - Preserves encrypted credential vault (`$HERMES_ROOT/vault/`), WhatsApp bridge session stores, and internal orchestration SQLite databases (`kanban.db`, `projects.db`, `verification_evidence.db`).
   - Correlate timestamps identically with the declarative snapshot to enable deterministic pairing during bare-metal recovery without re-authenticating Telegram bots, re-scanning WhatsApp QR codes, or rotating LLM API keys.

## Sync & Verification Procedure

When running the declarative fleet sync script (`sync.sh`):

1. **Pre-flight Profile Audit:**
   - Verify every active profile directory under `$HERMES_ROOT/profiles/` (e.g. `atlas`, `aurora`, `forge`, `frame`, `groupbot`, `lens`, `nexus`, `orion`, `prism`, `quant`, `radar`, `sentinel`, `testing`) is explicitly declared in `KNOWN_PROFILES`.
   - Synchronize test suite profile tuples (`PROFILES` in `tests/test_fleet_profiles.py`) whenever profiles are activated or restored; otherwise `test_all_profiles_present` fails.
2. **Skill Frontmatter & Description Gate:**
   - Every skill `SKILL.md` across all synced profiles must have a non-empty `description:` field in its YAML frontmatter; missing descriptions will fail `test_skills_frontmatter`.
3. **Environment & YAML Interpreter Resolution:**
   - Do not assume host `python3` has `yaml` (PyYAML). Resolve the interpreter via `$HERMES_ROOT/venv/bin/python` or the active virtualenv before running sanitization.
   - Resolve `$HERMES_ROOT` dynamically: `$HERMES_HOME` -> `/root/.hermes` -> `$HOME/.hermes`.
4. **Governance & Role-Separation Checks:**
   - Enforce profile role boundaries before running test suites. Non-design profiles (e.g. `orion`) must have UI-only toolsets like `ui-ux-pro-max` explicitly disabled (`enabled: false`) to pass `validate_fleet.py`.
5. **Secret Sanitization Audit:**
   - Run `python3 scripts/sanitize_config.py --check profiles/*/config.yaml` before staging or committing. Ensure raw API keys and tokens are never staged.
6. **Verification Gates Before Git Push:**
   - Execute `python3 validate_fleet.py` (policy checks).
   - Execute `python3 validate_contracts.py` (A2A timeout and schema checks).
   - Run the full pytest suite (`pytest -q`).
   - Push to Git remote only when 100% of tests and policy checks pass.

## Backup Verification & Drift Audit Procedure

When auditing whether the fleet is currently backed up or has drifted:

1. **Fast Dry-Run Drift Detection:**
   - Run `bash scripts/sync.sh` (default dry-run mode without `--apply`).
   - Inspect the `Proposed declarative changes:` block. If lines prefixed with `>f` (modified/added files), `cd` (new directories), or `*deleting` appear, live profiles have drifted from declarative Git.
   - If the output shows no proposed changes, declarative Git is in 100% parity with live profiles.
2. **Minute-Level In-Flight Modification Audit:**
   - When verifying whether live changes occurred recently, do not rely solely on repo git status:
     - Run `find "$HERMES_ROOT/profiles/" -type f -mmin -180` to detect newly authored skills, hot memory updates, reference files (`references/*.md`), or prompt edits made during live interactive turns across all profiles.
     - Check modification timestamps in `$HERMES_ROOT/plans/` and host binary directories (e.g. `ls -lat /usr/local/bin/ | head -n 10`) for newly deployed CLI tools and supporting orchestrators.
3. **Internal Fleet Asset Boundary Invariant (Strict Fleet Isolation):**
   - When auditing backup readiness broadly ("apakah ada lagi yang bisa di backup?"), maintain STRICT isolation to the Hermes fleet itself. Do NOT expand into external host projects, unrelated git repos, or host daemons unless explicitly requested. See `references/fleet-backup-scope.md` for the comprehensive boundary specification and file manifest.
   - Comprehensive fleet backup covers all internal Hermes state:
     - **All 13 Profile Trees:** Prompts (`SOUL.md`), credentials (`.env`, `auth.json`), unredacted configs (`config.yaml.raw`), scheduled jobs (`cron/`), and memories (`memories/`).
     - **Encrypted Vault:** `$HERMES_ROOT/vault/` (`vault.json.enc` & `vault.key`).
     - **Platform Communication Sessions:** WhatsApp bridge and profile credentials (`$HERMES_ROOT/platforms/whatsapp/session/`, profile WhatsApp sessions).
     - **Runtime SQLite DBs & Ledgers:** `kanban.db`, `projects.db`, `verification_evidence.db`, and `bot_relay/`.
     - **Fleet System & Plugins:** `$HERMES_ROOT/fleet_v2_system/` (Lens QA engine & benchmarks) and `$HERMES_ROOT/plugins/`.
     - **Root Identity & Config:** Root `SOUL.md`, `USER.md`, `profile.yaml`, `channel_directory.json`, `root_memories`, `root_cron`.
4. **Declarative Git Layer Verification:**
   - Check the latest commit on remote Git repo (`git log -1` on `hermes-fleet-profiles`).
   - Verify working tree clean status (`git status`).
   - Confirm local `main` is up to date with `origin/main`.
5. **Disaster Recovery Secrets Layer Audit:**
   - Inspect offload volume (`/mnt/hermes-storage-offload/hermes-fleet-backups/`).
   - Verify timestamps of the newest `<timestamp>-fleet-complete` declarative snapshot and `secrets-live-<timestamp>` directory match the latest live changes.
   - Audit whether all active profiles and root-level tokens are captured in the latest secrets layer.
6. **Post-Sync Verification Loop:**
   - When drift is applied via `sync.sh --apply` and pushed to Git:
     1. Run full test gates (`pytest -q`, `validate_fleet.py`, `validate_contracts.py`).
     2. Create paired `<timestamp>-fleet-complete` and `secrets-live-<timestamp>` snapshots on offload storage with POSIX 700/600 permissions. Never skip the offload snapshot during an incremental push; bare-metal recovery requires 1:1 parity between Git commits and unredacted secrets layers.
     3. Re-run `bash scripts/sync.sh` dry-run to verify zero pending changes remain.

## Secrets Offload & Permission Invariants

When creating the Disaster Recovery Secrets Layer (`secrets-live-<timestamp>`):
- **Automated Dual-Layer Execution:** Run the deterministic backup script `python3 /root/.hermes/profiles/orion/skills/devops/fleet-backup-and-recovery/scripts/backup_fleet_dual_layer.py` to create the paired `<timestamp>-fleet-complete` declarative snapshot and `secrets-live-<timestamp>` secrets layer with atomic 700/600 permissions.
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
- **Internal Fleet State & Vault Scope:** Ensure secrets layer captures the encrypted vault (`$HERMES_ROOT/vault/`), WhatsApp session stores (`$HERMES_ROOT/platforms/whatsapp/session/` and per-profile sessions), internal database files (`kanban.db`, `projects.db`, `verification_evidence.db`), plugins, and root-level tokens.
- **Root Token & Operational State Scope:** Ensure root secrets include `root.env`, `root.auth.json`, `root.google_token.json`, `root.gsc_service_account.json`, `root.config.yaml.raw`, and uncommitted operational plans under `$HERMES_ROOT/plans/`.

## Archive Timeout & Storage Guard

When creating live snapshots or tarball archives of `/root/.hermes/profiles/`:
- **Mandatory Exclusions:** Always exclude heavy dynamic caches:
  `--exclude='cache'` `--exclude='sandboxes'` `--exclude='terminal-sessions'`
  `--exclude='browser-profile'` `--exclude='lsp/node_modules'` `--exclude='home/.npm'`
  `--exclude='home/.cache'` `--exclude='*.db-wal'` `--exclude='*.db-shm'`
- **Mechanism:** Profile directories often contain multi-hundred-megabyte browser binaries and node_modules. Archiving without exclusions causes foreground command timeouts (exit code 124) and risks disk saturation.
