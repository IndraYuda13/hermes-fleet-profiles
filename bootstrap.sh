#!/usr/bin/env bash
set -euo pipefail

# Hermes Fleet Profiles Bootstrap Script
# Restores / provisions declarative fleet configurations to ~/.hermes/

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${HOME}/.hermes"

echo "==> Bootstrapping Hermes Fleet Configurations..."

mkdir -p "${TARGET_DIR}/profiles"
mkdir -p "${TARGET_DIR}/skills"

# 1. Restore global skills
if [ -d "${REPO_DIR}/global/skills" ]; then
  echo " -> Restoring shared global skills..."
  rsync -av "${REPO_DIR}/global/skills/" "${TARGET_DIR}/skills/"
fi

# 2. Restore profiles
for profile_dir in "${REPO_DIR}/profiles/"*; do
  if [ -d "${profile_dir}" ]; then
    profile_name="$(basename "${profile_dir}")"
    echo " -> Provisioning profile: ${profile_name}..."
    dest="${TARGET_DIR}/profiles/${profile_name}"
    mkdir -p "${dest}"
    
    if [ -f "${profile_dir}/SOUL.md" ]; then
      cp -f "${profile_dir}/SOUL.md" "${dest}/"
    fi
    if [ -f "${profile_dir}/profile.yaml" ]; then
      cp -f "${profile_dir}/profile.yaml" "${dest}/"
    fi
    if [ -f "${profile_dir}/config.yaml" ] && [ ! -f "${dest}/config.yaml" ]; then
      cp -f "${profile_dir}/config.yaml" "${dest}/"
    fi
    if [ -d "${profile_dir}/skills" ]; then
      mkdir -p "${dest}/skills"
      rsync -av "${profile_dir}/skills/" "${dest}/skills/"
    fi
  fi
done

echo "==> Fleet profiles provisioned successfully!"
echo "    Run 'hermes profile list' to verify."
