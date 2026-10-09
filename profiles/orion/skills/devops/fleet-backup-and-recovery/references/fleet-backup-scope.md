# Fleet Backup Scope & Disaster Recovery Manifest

## 1. Strict Fleet Isolation Boundary Invariant

When assessing backup status or responding to open-ended backup prompts (e.g., "apakah ada lagi yang bisa di backup?"), maintain STRICT isolation to the Hermes fleet ecosystem.

### Scope Boundaries:
- **IN-SCOPE (Hermes Fleet Ecosystem):**
  - All 13 profile trees (`atlas`, `aurora`, `forge`, `frame`, `groupbot`, `lens`, `nexus`, `orion`, `prism`, `quant`, `radar`, `sentinel`, `testing`).
  - Root identity, operational plans, and channel configurations.
  - Internal databases: `kanban.db`, `projects.db`, `verification_evidence.db`.
  - Encrypted credential vault: `$HERMES_ROOT/vault/` (`vault.json.enc` & `vault.key`).
  - Platform communications: WhatsApp bridge session stores (`$HERMES_ROOT/platforms/whatsapp/session/` and profile sessions).
  - Fleet system extensions: `$HERMES_ROOT/fleet_v2_system/` (Lens QA engine & benchmarks) and `$HERMES_ROOT/plugins/`.
- **OUT-OF-SCOPE (External Host Assets):**
  - External host development repositories (`/root/projects/*`).
  - Standalone daemons and external scrapers (`/root/cust/*`, `luckywatch-bot`, etc.).
  - Host system configurations (`/etc/systemd/*`, `/etc/nginx/*`).
  - Independent web mirrors and client projects.

Do not audit or offer to back up out-of-scope host assets during fleet backup operations unless the user explicitly requests host-wide or multi-project coverage.

## 2. In-Flight Drift Detection

Do not rely solely on Git status within `hermes-fleet-profiles`. Profiles undergo live modifications during interactive turns (prompt posture tuning, skill authoring, memory compaction, reference drafting).

### In-Flight Probing:
```bash
# Detect files modified within the last 3 hours across all profiles
find /root/.hermes/profiles/ -type f -mmin -180
```
Key files to inspect when changes appear:
- `<profile>/SOUL.md`: In-flight behavioral directives, authorization postures, safety rules.
- `<profile>/skills/**/SKILL.md`: Newly authored or patched capabilities.
- `<profile>/skills/**/references/*.md`: Deep reference notes or attack/debugging methodologies.
- `/root/.hermes/plans/*.md`: Operational architecture plans.

## 3. Disaster Recovery Manifest

The DR secrets layer (`secrets-live-<timestamp>`) must be stored on offload storage (`/mnt/hermes-storage-offload/hermes-fleet-backups/`) with strict POSIX permissions (`700` directories, `600` files).

### File Manifest:
| Source Path | Backup Target Name | Purpose |
|---|---|---|
| `$HERMES_ROOT/.env` | `root.env` | Root environment variables |
| `$HERMES_ROOT/auth.json` | `root.auth.json` | Platform authentication tokens |
| `$HERMES_ROOT/google_token.json` | `root.google_token.json` | Google Workspace OAuth token |
| `$HERMES_ROOT/gsc_service_account.json` | `root.gsc_service_account.json` | Google Search Console service key |
| `$HERMES_ROOT/config.yaml` | `root.config.yaml.raw` | Unredacted root configuration |
| `$HERMES_ROOT/SOUL.md` | `root.SOUL.md` | Root agent personality & core rules |
| `$HERMES_ROOT/USER.md` | `root.USER.md` | Root user profile & preferences |
| `$HERMES_ROOT/profile.yaml` | `root.profile.yaml` | Root profile configuration |
| `$HERMES_ROOT/channel_directory.json` | `root.channel_directory.json` | Multi-agent communication directory |
| `$HERMES_ROOT/kanban.db` | `root.kanban.db` | Orchestration board database |
| `$HERMES_ROOT/projects.db` | `root.projects.db` | Fleet project database |
| `$HERMES_ROOT/verification_evidence.db`| `root.verification_evidence.db` | QA verification evidence ledger |
| `$HERMES_ROOT/monetag_tokens.json` | `root.monetag_tokens.json` | Monetag platform OAuth token |
| `$HERMES_ROOT/monetag_active_oauth.json` | `root.monetag_active_oauth.json` | Monetag active session state |
| `$HERMES_ROOT/vault/` | `vault/` | Encrypted credential vault (`vault.key`, `vault.json.enc`) |
| `$HERMES_ROOT/platforms/whatsapp/session/` | `root_whatsapp_session/` | Root WhatsApp bridge session |
| `$HERMES_ROOT/memories/` | `root_memories/` | Root persistent memories |
| `$HERMES_ROOT/cron/` | `root_cron/` | Root scheduled cron jobs |
| `$HERMES_ROOT/plans/` | `plans/` | Operational architecture and task plans |
| `$HERMES_ROOT/bot_relay/` | `bot_relay/` | Cross-bot communication relay state |
| `$HERMES_ROOT/profiles/<p>/.env` | `<p>/.env` | Per-profile environment variables |
| `$HERMES_ROOT/profiles/<p>/auth.json` | `<p>/auth.json` | Per-profile authentication tokens |
| `$HERMES_ROOT/profiles/<p>/config.yaml`| `<p>/config.yaml.raw` | Per-profile unredacted configs |
| `$HERMES_ROOT/profiles/<p>/cron/` | `<p>/cron/` | Per-profile cron schedules |
| `$HERMES_ROOT/profiles/<p>/memories/` | `<p>/memories/` | Per-profile persistent memories |
| `$HERMES_ROOT/profiles/<p>/whatsapp/` | `<p>/whatsapp/` | Per-profile WhatsApp credentials |
| `$HERMES_ROOT/profiles/<p>/platforms/whatsapp/` | `<p>/platforms_whatsapp/` | Per-profile WhatsApp multi-device bridge |

## 4. Verification and Parity Cycle

1. **Dry-Run Check:** Run `bash scripts/sync.sh` to preview declarative drift.
2. **Apply Drift:** Run `bash scripts/sync.sh --apply` to stage changes into `hermes-fleet-profiles`.
3. **Validate:** Execute `python3 scripts/sanitize_config.py`, `python3 scripts/validate_fleet.py`, `python3 scripts/validate_contracts.py`, and `pytest -q`.
4. **Push Git:** Commit and push to `origin/main`.
5. **Automated Snapshot Offload:** Run `python3 /root/.hermes/profiles/orion/skills/devops/fleet-backup-and-recovery/scripts/backup_fleet_dual_layer.py` to generate paired declarative snapshot (`<timestamp>-fleet-complete`) and secrets layer (`secrets-live-<timestamp>`) on offload storage with strict POSIX 700/600 permissions.
6. **Parity Confirmation:** Re-run `bash scripts/sync.sh` dry-run; verify 0 proposed changes.
