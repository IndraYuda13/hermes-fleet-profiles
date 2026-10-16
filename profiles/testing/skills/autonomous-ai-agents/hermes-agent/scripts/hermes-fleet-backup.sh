#!/usr/bin/env bash
# hermes-fleet-backup.sh — backup a multi-profile Hermes fleet (default home +
# ~/.hermes/profiles/*) plus the external tooling the fleet depends on.
#
# Tier 1 (default): configs, skills, cron, memories, plugins, kanban, sessions,
#   fleet metadata + external tooling (wrappers, extension jars, pinned
#   manifests, skill mirrors). state.db NOT included.
# Tier 2 (--with-state): also every profile's state.db (sqlite snapshot).
#
# Excluded (regenerable): tools/, installs/, lsp/, bin/, logs/, cache/,
#   scratch/, browser-profile/, node_modules/, *.log, *.sock, state.db.*
#
# Encryption: age. Set HERMES_BACKUP_RECIPIENT (age1...) or put the recipient in
#   /etc/hermes-fleet-backup.agekey. Without either, the archive is written
#   UNENCRYPTED with a loud warning (it contains bot/MCP tokens).
#
# Usage:
#   hermes-fleet-backup.sh [--with-state] [--dest DIR] [--keep N] [--dry-run]
#
# Rules behind the details (skill hermes-agent, references/fleet-backup.md):
#   sqlite .backup per DB (never rsync a live DB), rsync exit 24 tolerated,
#   find-based rotation (ls glob + pipefail aborts under set -e).

set -euo pipefail

WITH_STATE=0
DEST=/mnt/backups/hermes-fleet
KEEP=5
DRY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --with-state) WITH_STATE=1; shift ;;
    --dest) DEST="$2"; shift 2 ;;
    --keep) KEEP="$2"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    -h|--help) sed -n '2,24p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

STAMP=$(date +%Y%m%d-%H%M)
AGEKEY_FILE=/etc/hermes-fleet-backup.agekey
RECIPIENT="${HERMES_BACKUP_RECIPIENT:-}"
[ -z "$RECIPIENT" ] && [ -f "$AGEKEY_FILE" ] && RECIPIENT=$(cat "$AGEKEY_FILE")

EXCLUDES=(
  --exclude='tools/' --exclude='installs/' --exclude='lsp/' --exclude='bin/'
  --exclude='logs/' --exclude='cache/' --exclude='scratch/'
  --exclude='browser-profile/' --exclude='node_modules/'
  --exclude='profiles/*/logs/' --exclude='profiles/*/cache/'
  --exclude='profiles/*/scratch/' --exclude='profiles/*/lsp/'
  --exclude='profiles/*/bin/' --exclude='*.log'
  --exclude='state.db.*' --exclude='*.sock'
)

if [ "$DRY" = 1 ]; then
  echo "== DRY RUN (rsync -n, writes nothing) =="
  rsync -a --dry-run --itemize-changes "${EXCLUDES[@]}" \
    /root/.hermes/ /tmp/_hermes_dryrun_probe/ 2>/dev/null | wc -l | xargs echo "files to copy:"
  du -sh --exclude=tools --exclude=installs --exclude=lsp --exclude=bin \
    --exclude=logs --exclude=cache --exclude=scratch --exclude=browser-profile \
    --exclude=node_modules /root/.hermes 2>/dev/null | awk '{print "source size ~", $1}'
  rm -rf /tmp/_hermes_dryrun_probe
  [ "$WITH_STATE" = 1 ] && echo "(--with-state: +state.db of every profile)"
  exit 0
fi

WORK=$(mktemp -d /root/.hermes-fleet-backup.XXXXXX)
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$DEST"

echo "[1/5] rsync config+skills+cron+memories+kanban+sessions..."
# exit 24 (file vanished — live DB/cron churn under the running gateway) = benign
rc=0; rsync -a "${EXCLUDES[@]}" /root/.hermes/ "$WORK/hermes/" || rc=$?
[ "$rc" = 0 ] || [ "$rc" = 24 ] || exit "$rc"

echo "[2/5] sqlite snapshot DBs (consistent, torn-write safe)..."
find "$WORK/hermes" -name '*.db' | while read -r db; do
  orig="/root/.hermes/${db#"$WORK"/hermes/}"
  if [ -f "$orig" ]; then
    if sqlite3 "$orig" ".backup '$db.tmp'" 2>/dev/null; then
      mv "$db.tmp" "$db"
    else
      echo "  WARN: snapshot failed for $db (keeping rsync copy)" >&2
      rm -f "$db.tmp"
    fi
  fi
done
find "$WORK/hermes" \( -name '*-wal' -o -name '*-shm' \) -delete

if [ "$WITH_STATE" != 1 ]; then
  echo "[3/5] skipping state.db (pass --with-state to include)..."
  find "$WORK/hermes" -name 'state.db' -delete
else
  echo "[3/5] including state.db."
fi

echo "[4/5] external tooling..."
mkdir -p "$WORK/external"
# --- host-specific: adjust these paths to the fleet's real external dependencies
cp -a /usr/local/bin/rea-mcp "$WORK/external/" 2>/dev/null \
  || echo "  WARN: /usr/local/bin/rea-mcp not found" >&2
cp -a /opt/burp-extensions/burpmcp-ultra-*.jar "$WORK/external/" 2>/dev/null || true
cp -a /root/.BurpSuite/UserConfigCommunity.json "$WORK/external/" 2>/dev/null || true
cp -a /mnt/tools/rea/package.json /mnt/tools/rea/package-lock.json \
      /mnt/tools/rea/update-rea.sh "$WORK/external/" 2>/dev/null || true
tar czf "$WORK/external/rea-skill-backups.tgz" -C /mnt/tools/rea skill-backups 2>/dev/null || true
rc=0; rsync -a /mnt/tools/rea-skills/ "$WORK/external/rea-skills/" 2>/dev/null || rc=$?
[ "$rc" = 0 ] || [ "$rc" = 24 ] || true
# --- end host-specific
{
  echo "backup: $STAMP"
  echo "host: $(hostname)"
  echo "hermes: $(hermes --version 2>/dev/null || echo '?')"
  echo "with_state: $WITH_STATE"
  echo "profiles: $(ls /root/.hermes/profiles | wc -l)"
} > "$WORK/MANIFEST.txt"

echo "[5/5] archive..."
ARCHIVE="$DEST/hermes-fleet-$STAMP.tar.gz"
tar czf "$ARCHIVE" -C "$WORK" .
if [ -n "$RECIPIENT" ] && command -v age >/dev/null; then
  age -r "$RECIPIENT" -o "$ARCHIVE.age" "$ARCHIVE" && rm "$ARCHIVE"
  echo "OK (age-encrypted): $ARCHIVE.age"
else
  [ -z "$RECIPIENT" ] && echo "WARNING: no age recipient — archive is UNENCRYPTED and contains credentials." >&2
  echo "OK: $ARCHIVE"
fi

# rotate: keep N newest (find-based — ls glob + pipefail aborts under set -e)
find "$DEST" -maxdepth 1 -name 'hermes-fleet-*.tar.gz*' -printf '%T@ %p\n' 2>/dev/null \
  | sort -rn | tail -n +$((KEEP+1)) | cut -d' ' -f2- | xargs -r rm -f || true
echo "Rotation: keeping $KEEP newest in $DEST"
du -sh "$DEST"/hermes-fleet-$STAMP* 2>/dev/null || true
