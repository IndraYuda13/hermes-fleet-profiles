#!/usr/bin/env bash
set -euo pipefail

# Hermes Fleet Profiles Sync & Export Script
# Exports clean declarative configs from ~/.hermes/profiles to the repository

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROFILES_SRC="/root/.hermes/profiles"
GLOBAL_SRC="/root/.hermes"

echo "==> Syncing Hermes Fleet declarative configs to ${REPO_DIR}..."

PROFILES=(
  "atlas"
  "aurora"
  "default"
  "forge"
  "frame"
  "groupbot"
  "lens"
  "nexus"
  "orion"
  "prism"
  "quant"
  "radar"
  "sentinel"
)

mkdir -p "${REPO_DIR}/profiles"
mkdir -p "${REPO_DIR}/global/skills"

# 1. Sync global skills (declarative SKILL.md and references only)
if [ -d "${GLOBAL_SRC}/skills" ]; then
  rsync -av --delete \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    "${GLOBAL_SRC}/skills/" "${REPO_DIR}/global/skills/"
fi

# 2. Sync each profile
for p in "${PROFILES[@]}"; do
  SRC="${PROFILES_SRC}/${p}"
  DEST="${REPO_DIR}/profiles/${p}"
  
  if [ -d "${SRC}" ]; then
    echo " -> Syncing profile: ${p}"
    mkdir -p "${DEST}"
    
    # Sync SOUL.md and custom markdown docs
    if [ -f "${SRC}/SOUL.md" ]; then
      cp -f "${SRC}/SOUL.md" "${DEST}/"
    fi
    if [ -f "${SRC}/profile.yaml" ]; then
      cp -f "${SRC}/profile.yaml" "${DEST}/"
    fi
    
    # Sanitize config.yaml (strip sensitive keys if any before copying)
    if [ -f "${SRC}/config.yaml" ]; then
      python3 -c "
import re
src_path = '${SRC}/config.yaml'
dst_path = '${DEST}/config.yaml'
try:
    with open(src_path, 'r') as f:
        content = f.read()
    # Mask common api key patterns just in case
    content_clean = re.sub(r'(api_key:\s*[\'\"]?)[^\'\s\"]+([\'\"]?)', r'\1REDACTED\2', content)
    content_clean = re.sub(r'(token:\s*[\'\"]?)[^\'\s\"]+([\'\"]?)', r'\1REDACTED\2', content_clean)
    with open(dst_path, 'w') as f:
        f.write(content_clean)
except Exception as e:
    print('Failed to process config for ${p}:', e)
"
    fi
    
    # Sync profile-specific skills if any
    if [ -d "${SRC}/skills" ]; then
      mkdir -p "${DEST}/skills"
      rsync -av --delete \
        --exclude='*.pyc' \
        --exclude='__pycache__' \
        "${SRC}/skills/" "${DEST}/skills/"
    fi
  fi
done

echo "==> Sync complete!"
