#!/usr/bin/env bash
set -euo pipefail

# Safely provision declarative prompts/skills. Existing runtime config and .env
# are preserved unless --replace-config is explicitly supplied.

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${HERMES_HOME:-${HOME}/.hermes}"
APPLY=false
REPLACE_CONFIG=false

for argument in "$@"; do
  case "${argument}" in
    --apply) APPLY=true ;;
    --replace-config) REPLACE_CONFIG=true ;;
    *) echo "Usage: $0 [--apply] [--replace-config]" >&2; exit 2 ;;
  esac
done

for command_name in python3 rsync; do
  command -v "${command_name}" >/dev/null || {
    echo "Missing required command: ${command_name}" >&2
    exit 1
  }
done

python3 "${REPO_DIR}/scripts/sanitize_config.py" --check "${REPO_DIR}"/profiles/*/config.yaml
python3 "${REPO_DIR}/scripts/validate_fleet.py" --repo-root "${REPO_DIR}"

echo "Target: ${TARGET_DIR}"
echo "Profiles: atlas aurora forge frame groupbot lens nexus orion prism quant radar sentinel"
echo "Config replacement: ${REPLACE_CONFIG}"

if [[ "${APPLY}" != true ]]; then
  echo "Dry-run complete. Use --apply after stopping profile gateways and reviewing this plan."
  exit 0
fi

mkdir -p "${TARGET_DIR}/profiles" "${TARGET_DIR}/skills" "${TARGET_DIR}/backups/fleet-bootstrap"
backup_dir="${TARGET_DIR}/backups/fleet-bootstrap/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "${backup_dir}/profiles"

if [[ -d "${TARGET_DIR}/skills" ]]; then
  cp -a "${TARGET_DIR}/skills" "${backup_dir}/global-skills"
fi

rsync -a --delete \
  --exclude='.archive/' --exclude='.hub/' --exclude='*.log' --exclude='*.jsonl' \
  "${REPO_DIR}/global/skills/" "${TARGET_DIR}/skills/"

for profile_dir in "${REPO_DIR}"/profiles/*; do
  [[ -d "${profile_dir}" ]] || continue
  profile_name="$(basename "${profile_dir}")"
  destination="${TARGET_DIR}/profiles/${profile_name}"
  mkdir -p "${destination}" "${backup_dir}/profiles/${profile_name}"

  for declaration in SOUL.md profile.yaml; do
    if [[ -f "${destination}/${declaration}" ]]; then
      cp -a "${destination}/${declaration}" "${backup_dir}/profiles/${profile_name}/"
    fi
    [[ -f "${profile_dir}/${declaration}" ]] && cp "${profile_dir}/${declaration}" "${destination}/${declaration}"
  done

  if [[ "${REPLACE_CONFIG}" == true ]]; then
    if [[ -f "${destination}/config.yaml" ]]; then
      cp -a "${destination}/config.yaml" "${backup_dir}/profiles/${profile_name}/"
    fi
    cp "${profile_dir}/config.yaml" "${destination}/config.yaml"
  fi

  if [[ -d "${profile_dir}/skills" ]]; then
    if [[ -d "${destination}/skills" ]]; then
      cp -a "${destination}/skills" "${backup_dir}/profiles/${profile_name}/skills"
    fi
    mkdir -p "${destination}/skills"
    rsync -a --delete \
      --exclude='.archive/' --exclude='.hub/' --exclude='*.log' --exclude='*.jsonl' \
      "${profile_dir}/skills/" "${destination}/skills/"
  fi
done

echo "Bootstrap applied. Config replacement: ${REPLACE_CONFIG}"
echo "Recovery copy: ${backup_dir}"
echo "Restart affected gateways, then run: hermes status --deep"

