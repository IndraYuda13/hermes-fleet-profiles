#!/usr/bin/env bash
set -euo pipefail

# Export live Hermes profile declarations through a staged, validated snapshot.
# Default mode is read-only. Pass --apply only from a clean Git worktree.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
if [[ -n "${HERMES_ROOT:-}" ]]; then
  :
elif [[ -d "${HERMES_HOME:-}/profiles" ]]; then
  HERMES_ROOT="${HERMES_HOME}"
elif [[ -d "${HOME}/.hermes/profiles" ]]; then
  HERMES_ROOT="${HOME}/.hermes"
elif [[ -d "/root/.hermes/profiles" ]]; then
  HERMES_ROOT="/root/.hermes"
else
  HERMES_ROOT="${HERMES_HOME:-${HOME}/.hermes}"
fi
APPLY=false

case "${1:-}" in
  "") ;;
  --apply) APPLY=true ;;
  *) echo "Usage: $0 [--apply]" >&2; exit 2 ;;
esac

for command_name in git python3 rsync; do
  command -v "${command_name}" >/dev/null || {
    echo "Missing required command: ${command_name}" >&2
    exit 1
  }
done

PYTHON_BIN="python3"
if ! python3 -c "import yaml" >/dev/null 2>&1; then
  if /usr/bin/python3 -c "import yaml" >/dev/null 2>&1; then
    PYTHON_BIN="/usr/bin/python3"
  fi
fi

PROFILES=(atlas aurora forge frame groupbot lens nexus orion prism quant radar sentinel testing)
SKILL_RUNTIME_EXCLUDES=(
  --exclude='.archive/'
  --exclude='.hub/'
  --exclude='.curator_backups/'
  --exclude='.curator_*'
  --exclude='.locks/'
  --exclude='.bundled_manifest'
  --exclude='.usage.json'
  --exclude='hermes-index.json'
  --exclude='*.db*'
  --exclude='*.lock*'
  --exclude='*.log'
  --exclude='*.jsonl'
  --exclude='__pycache__/'
)
STAGE_PARENT="$(mktemp -d)"
STAGE_REPO="${STAGE_PARENT}/repo"
trap 'rm -rf -- "${STAGE_PARENT}"' EXIT

rsync -a \
  --exclude='.git/' \
  "${SKILL_RUNTIME_EXCLUDES[@]}" \
  "${REPO_DIR}/" "${STAGE_REPO}/"

sync_skills() {
  local source_dir="$1"
  local destination_dir="$2"
  if [[ -d "${source_dir}" ]]; then
    mkdir -p "${destination_dir}"
    # --delete-excluded purges obsolete runtime artifacts copied from the
    # repository into the staging snapshot before validation can inspect it.
    rsync -a --delete --delete-excluded \
      "${SKILL_RUNTIME_EXCLUDES[@]}" \
      "${source_dir}/" "${destination_dir}/"
  fi
}

sync_skills "${HERMES_ROOT}/skills" "${STAGE_REPO}/global/skills"

for profile_name in "${PROFILES[@]}"; do
  source_dir="${HERMES_ROOT}/profiles/${profile_name}"
  destination_dir="${STAGE_REPO}/profiles/${profile_name}"
  [[ -d "${source_dir}" ]] || {
    echo "Missing live profile: ${source_dir}" >&2
    exit 1
  }
  mkdir -p "${destination_dir}"
  for declaration in SOUL.md profile.yaml config.yaml; do
    [[ -f "${source_dir}/${declaration}" ]] && cp "${source_dir}/${declaration}" "${destination_dir}/${declaration}"
  done
  sync_skills "${source_dir}/skills" "${destination_dir}/skills"
done

"${PYTHON_BIN}" "${STAGE_REPO}/scripts/sanitize_config.py" "${STAGE_REPO}"/profiles/*/config.yaml
"${PYTHON_BIN}" "${STAGE_REPO}/scripts/sanitize_skill_examples.py" "${STAGE_REPO}/global/skills" "${STAGE_REPO}/profiles"
"${PYTHON_BIN}" "${STAGE_REPO}/scripts/apply_role_policy.py" --repo-root "${STAGE_REPO}"
"${PYTHON_BIN}" "${STAGE_REPO}/scripts/validate_fleet.py" --repo-root "${STAGE_REPO}"

echo "Proposed declarative changes:"
rsync -ainc --no-times --delete --exclude='.git/' "${STAGE_REPO}/global/" "${REPO_DIR}/global/"
rsync -ainc --no-times --delete --exclude='.git/' "${STAGE_REPO}/profiles/" "${REPO_DIR}/profiles/"

if [[ "${APPLY}" != true ]]; then
  echo "Dry-run complete. Re-run with --apply after reviewing the itemized diff."
  exit 0
fi

if [[ -n "$(git -C "${REPO_DIR}" status --porcelain)" ]]; then
  echo "Refusing --apply: Git worktree is not clean." >&2
  exit 1
fi

backup_dir="${REPO_DIR}/../hermes-fleet-backups/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "${backup_dir}"
cp -a "${REPO_DIR}/global" "${REPO_DIR}/profiles" "${backup_dir}/"

rsync -a --delete "${STAGE_REPO}/global/" "${REPO_DIR}/global/"
rsync -a --delete "${STAGE_REPO}/profiles/" "${REPO_DIR}/profiles/"

"${PYTHON_BIN}" "${REPO_DIR}/scripts/validate_fleet.py" --repo-root "${REPO_DIR}"
echo "Sync applied. Recovery copy: ${backup_dir}"
