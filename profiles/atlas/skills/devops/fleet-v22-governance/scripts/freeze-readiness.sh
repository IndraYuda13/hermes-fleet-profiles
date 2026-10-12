#!/usr/bin/env bash
# freeze-readiness.sh — is this evidence directory settled enough to freeze, copy, or relay?
#
# Usage: freeze-readiness.sh <dir> [file ...] [--gap N]
#   <dir>    directory to inspect (default: cwd)
#   [file]   files to hash-check (default: every non-PNG file directly in <dir>)
#   --gap N  seconds between hash passes (default 5; raise it for slow writers)
#
# Exit 0 = every checked file hash-stable, no writer holds the dir; 1 = NOT retry-free; 2 = usage.
#
# Why both halves exist: a single hash pass cannot distinguish a settled file from one still being
# written, and a writer holding the directory open (a browser probe, a lane's polling wrapper, an
# http.server) mutates artefacts between your passes. Both conditions must hold before a revision
# set can be called frozen or relayed.

set -u
GAP=5
ARGS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --gap) GAP="${2:-5}"; shift 2 ;;
    --gap=*) GAP="${1#--gap=}"; shift ;;
    *) ARGS+=("$1"); shift ;;
  esac
done

DIR="${ARGS[0]:-$(pwd)}"
[ -d "$DIR" ] || { echo "freeze-readiness: not a directory: $DIR" >&2; exit 2; }
DIR="$(cd "$DIR" && pwd -P)"

FILES=()
if [ "${#ARGS[@]}" -gt 1 ]; then
  for f in "${ARGS[@]:1}"; do FILES+=("$DIR/$f"); done
else
  while IFS= read -r f; do FILES+=("$f"); done < <(find "$DIR" -maxdepth 1 -type f ! -name '*.png' ! -name '*.jpg' | sort)
fi

rc=0
echo "dir= $DIR"
echo "now= $(date -u +%FT%TZ)"
echo
echo "== writers holding this directory open (cwd or an open fd) =="
found=0
for p in $(ls /proc | grep -E '^[0-9]+$'); do
  hit=""
  c=$(readlink "/proc/$p/cwd" 2>/dev/null || true)
  case "$c" in "$DIR"|"$DIR"/*) hit="cwd=$c" ;; esac
  if [ -z "$hit" ]; then
    for fd in /proc/$p/fd/*; do
      t=$(readlink "$fd" 2>/dev/null || true)
      case "$t" in "$DIR"/*) hit="fd=$t"; break ;; esac
    done
  fi
  [ -n "$hit" ] || continue
  # The invoking shell and its own here-doc/snapshot wrapper self-match: a writer must be
  # something that can change a file, so require a real command, not this script's ancestors.
  cmd=$(tr '\0' ' ' < "/proc/$p/cmdline" 2>/dev/null | cut -c1-120)
  proc=$(readlink "/proc/$p/exe" 2>/dev/null || echo '?')
  case "$cmd" in *freeze-readiness.sh*) continue ;; esac
  echo "WRITER pid=$p exe=$(basename "${proc:-?}") $hit"
  echo "        cmd=$cmd"
  case "$cmd" in *http.server*|*'bash -c'*) echo "        note=wrapper or static file server; check what it launches before blaming it" ;; esac
  found=1
  rc=1
done
[ "$found" -eq 1 ] || echo "(none)"

echo
echo "== hash pass 1 =="
declare -A H1 M1 S1
for f in "${FILES[@]}"; do
  [ -e "$f" ] || { echo "$(basename "$f") MISSING"; continue; }
  H1["$f"]=$(sha256sum "$f" | cut -d' ' -f1)
  M1["$f"]=$(stat -c %Y "$f"); S1["$f"]=$(stat -c %s "$f")
  echo "$(basename "$f") sz=${S1[$f]} mt=${M1[$f]} $(date -u -d @${M1[$f]} +%T)Z sha=${H1[$f]}"
done

echo
echo "waiting ${GAP}s for pass 2 ..."
sleep "$GAP"

echo "== hash pass 2 (stability) =="
for f in "${FILES[@]}"; do
  [ -e "$f" ] || { echo "$(basename "$f") MISSING"; rc=1; continue; }
  h=$(sha256sum "$f" | cut -d' ' -f1); m=$(stat -c %Y "$f")
  if [ "$h" = "${H1[$f]:-}" ]; then
    echo "$(basename "$f") STABLE sha=${h:0:16}"
  else
    echo "$(basename "$f") CHANGED ${H1[$f]:0:16} -> ${h:0:16} mt=${m}"
    rc=1
  fi
done

echo
if [ "$rc" -eq 0 ]; then
  echo "FREEZE-READY: no writer, all checked files hash-stable across ${GAP}s."
  echo "Copy the exact revision into your own custody before relaying; a shared .frozen/ beside the"
  echo "evidence is not a freeze, the owning lanes keep writing their own copies there."
else
  echo "NOT RETRY-FREE: settle the writers or copy the exact revision to immutable storage and run that copy."
fi
exit "$rc"
