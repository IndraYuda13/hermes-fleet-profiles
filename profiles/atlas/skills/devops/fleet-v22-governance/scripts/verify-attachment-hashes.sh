#!/usr/bin/env bash
# Classify every stored attachment of a Kanban task as CURRENT or STALE against a source file.
#
# Usage: verify-attachment-hashes.sh <board-slug> <task_id> <source-path>
#
# Why this exists: the attachment store renames on collision instead of overwriting, so a
# canonical filename can hold stale bytes while a dedup variant holds the current bytes.
# The filename and the record id prove nothing about currency; only the hash does.
#
# Exit codes: 0 = at least one CURRENT copy and no STALE copies; 1 = at least one STALE copy
# present; 2 = no stored attachment matches the source at all (never prune anything).
set -uo pipefail

BOARD="${1:?board slug required}"
TASK="${2:?task id required}"
SRC="${3:?source path required}"

export HERMES_KANBAN_BOARD="$BOARD"

command -v sha256sum >/dev/null 2>&1 || { echo "sha256sum not found" >&2; exit 2; }
[ -r "$SRC" ] || { echo "source not readable: $SRC" >&2; exit 2; }

ATT_DIR="/root/.hermes/kanban/boards/$BOARD/attachments/$TASK"
[ -d "$ATT_DIR" ] || { echo "no attachment dir: $ATT_DIR" >&2; exit 2; }

src_hash=$(sha256sum -- "$SRC" | awk '{print $1}')
printf 'SOURCE     %s  %s\n\n' "$src_hash" "$SRC"

shopt -s nullglob
current=0
stale=0
for f in "$ATT_DIR"/*; do
    h=$(sha256sum -- "$f" | awk '{print $1}')
    if [ "$h" = "$src_hash" ]; then
        mark=CURRENT
        current=$((current + 1))
    else
        mark=STALE
        stale=$((stale + 1))
    fi
    printf '%-9s %s  %s  (%s bytes)\n' "$mark" "$h" "$(basename -- "$f")" "$(stat -c %s -- "$f")"
done

printf '\ncurrent=%d stale=%d total=%d\n' "$current" "$stale" "$((current + stale))"

if [ "$current" -eq 0 ]; then
    echo "VERDICT: no stored copy matches the source. Do NOT remove anything; attach the current source first."
    exit 2
fi
if [ "$stale" -gt 0 ]; then
    echo "VERDICT: stale copies present. Remove the STALE ids only, keeping a CURRENT copy under the canonical name."
    exit 1
fi
echo "VERDICT: exactly the source content is stored; safe to prune its redundant duplicate copies."
exit 0
