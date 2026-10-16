# Fleet Backup & Restore

Applies to any multi-profile Hermes host (profiles under `~/.hermes/profiles/<name>/`
plus the default home `~/.hermes/`). Canonical script: `scripts/hermes-fleet-backup.sh`
in this skill — deploy with
`install -m 755 scripts/hermes-fleet-backup.sh /usr/local/bin/hermes-fleet-backup.sh`.

## Always-on rules

- **Two tiers.** Tier 1 (default) = everything irreplaceable except `state.db`
  (configs, skills, cron, memories, plugins, kanban, sessions, fleet metadata +
  external tooling). Tier 2 (`--with-state`) adds per-profile `state.db` — multi-GB,
  only when conversation state matters. Default to Tier 1; state.db is largely
  regenerable.
- **Snapshot SQLite, never rsync a live DB.** The gateway writes constantly;
  `sqlite3 <db> ".backup '<tmp>'"` per DB is the only consistent copy. Do it AFTER
  the rsync, mapping each copied DB back to its live source, then delete `-wal`/
  `-shm` from the copy.
- **Tolerate rsync exit code 24** (source vanished mid-transfer — live DB/cron
  churn). Under `set -euo pipefail`, treat 24 as success; any other non-zero is a
  real failure.
- **Exclude regenerable trees:** `tools/`, `installs/`, `lsp/`, `bin/`, `logs/`,
  `cache/`, `scratch/`, `browser-profile/`, `node_modules/`, `*.log`, `*.sock`,
  and `state.db.*` sidecars — stale `.lock`/repair metadata in a restored copy
  confuses maintenance logic.
- **Rotate with `find -printf '%T@ %p' | sort -rn`**, never `ls <glob> | tail` under
  `set -euo pipefail`: a non-matching glob makes `ls` exit non-zero and pipefail
  aborts the script AFTER the archive was already written.
- **Encrypt the archive.** Profile configs carry bot tokens, MCP bearer tokens,
  and OAuth state. Use `age` with a recipient (env `HERMES_BACKUP_RECIPIENT` or
  `/etc/hermes-fleet-backup.agekey`); if neither is set the script warns loudly —
  an unencrypted fleet archive must never be the silent default.
- **External tooling is NOT under `~/.hermes`** — back it up in the same run:
  hand-written wrapper scripts (`/usr/local/bin/*`), application extension jars
  plus their registration JSON, and the pinned manifests + mirror/update scripts
  of isolated tool installs (e.g. a `/mnt/tools/<tool>` prefix). Losing the
  wrapper or the pin file means re-deriving the setup from scratch.
- **Offsite or it doesn't count.** An archive on the same disk dies with the host.
  Rsync the archive directory to another reachable node (Tailscale) or cloud
  storage; keep local copies only as the fast-restore tier.
- **Dry-run before the real run** (`--dry-run`) to validate excludes and size.

## Procedure — backup

1. Timestamped staging dir; rsync `~/.hermes/` with the exclude set above.
2. sqlite `.backup` every `*.db` in the copy from its live source; strip
   `-wal`/`-shm`; drop `state.db` unless `--with-state`.
3. Collect external tooling (wrappers, jars, registration JSON, pinned
   `package.json`/lockfile, update scripts, skill mirrors) into `external/`;
   write a `MANIFEST.txt` (stamp, host, hermes version, profile count).
4. `tar czf` → optional `age -r <recipient>` → rotate to N newest.
5. Verify the artifact: entry count, MANIFEST contents, spot-check that every
   profile's `config.yaml` and `memories/MEMORY.md` are inside, and that no
   `state.db` junk or sockets slipped in.

## Procedure — restore (new or rebuilt host)

1. Install Hermes; recreate every profile (`hermes profile create <name>` for each
   name in the archive) plus the default home.
2. Extract the archive; rsync `hermes/` back over `~/.hermes/`, and the
   `external/` pieces back to their absolute paths.
3. Reinstall what the archive deliberately excludes: npm-global MCP packages
   (`command` paths under `lib/node_modules`), isolated tool prefixes per their
   pinned manifests + update scripts, static binaries from their upstream
   releases, and GUI-dependent app extensions (start them; follow the relevant
   headless-revival procedure if they park in a startup wizard).
4. Reinstall any skill `node_modules` from the hub if a skill errors.
5. Verify per server: `hermes -p <profile> mcp test <server>` against the known
   tool counts, and `hermes skills list` for the external skill mirror.

## Pitfalls

- A bare `hermes config set` on a multi-profile host writes to the STICKY
  profile, not the default home — always pass `-p <name>` (`-p default` for the
  home). See the Hard Invariants in SKILL.md.
- `mcp test` spawns a fresh connection: after restoring, it proves config health
  independently of any stale live children.
- Keep the deployed `/usr/local/bin` copy in sync with this skill's script — the
  skill copy is the source of truth; redeploy after editing.
