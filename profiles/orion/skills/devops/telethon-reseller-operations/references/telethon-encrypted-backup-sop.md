# Telethon Reseller Encrypted Backup & Recovery SOP

This document defines the production procedure to snapshot, encrypt, and back up all 49 customer Telethon sessions and configs across `/root/cust/reseller1..5` to a private GitHub repository.

## Background & Constraints

- Directory: `/root/cust` (reseller, reseller2, reseller3, reseller4, reseller5).
- Size: ~232 MB uncompressed (~165 MB compressed).
- Data: 49 `.session` SQLite databases storing plaintext 256-bit MTProto `auth_key` credentials.
- GitHub Limitations:
  - Max single file size: 100 MB (warning at 50 MB).
  - Git LFS free tier: only 1 GB storage / 1 GB bandwidth monthly.
  - Committing raw binary SQLite creates full-blob churn on every snapshot, bloating `.git` packfiles past 1.5 GB in a few commits.

## Backup Pipeline Architecture

```
/root/cust (Active Sessions)
       │
       ▼ [sqlite3 .backup API - Safe Non-Blocking Snapshot]
/tmp/staging_cust/
       │
       ▼ [tar -czf]
/tmp/cust_backup_YYYYMMDD.tar.gz (~165 MB)
       │
       ▼ [age / gpg AES-256 Symmetric Client-Side Encryption]
/tmp/cust_backup_YYYYMMDD.tar.gz.age
       │
       ▼ [gh release create OR git split rolling branch]
GitHub Private Repo (IndraYuda13/<repo>)
```

## Production Backup Procedure

```bash
#!/usr/bin/env bash
set -euo pipefail

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
STAGING_DIR="/tmp/cust_snapshot_${BACKUP_DATE}"
TAR_PATH="/tmp/cust_backup_${BACKUP_DATE}.tar.gz"
ENC_PATH="${TAR_PATH}.age"
REPO="IndraYuda13/cust-backup-private"

mkdir -p "${STAGING_DIR}"

# 1. Snapshot each reseller folder safely using sqlite3 .backup for sessions
for r in reseller reseller2 reseller3 reseller4 reseller5; do
  mkdir -p "${STAGING_DIR}/${r}/session" "${STAGING_DIR}/${r}/cf" "${STAGING_DIR}/${r}/newcf"
  
  # Copy configs and scripts
  cp -r /root/cust/${r}/*.py "${STAGING_DIR}/${r}/" 2>/dev/null || true
  cp -r /root/cust/${r}/cf/*.json "${STAGING_DIR}/${r}/cf/" 2>/dev/null || true
  cp -r /root/cust/${r}/newcf/*.json "${STAGING_DIR}/${r}/newcf/" 2>/dev/null || true
  
  # Online backup for SQLite sessions to avoid torn pages while active
  for s in /root/cust/${r}/session/*.session; do
    if [ -f "$s" ]; then
      bname=$(basename "$s")
      sqlite3 "$s" ".backup '${STAGING_DIR}/${r}/session/${bname}'"
    fi
  done
done

# 2. Archive and compress
tar -czf "${TAR_PATH}" -C "${STAGING_DIR}" .

# 3. Encrypt using age (passphrase via env or stdin)
age -p "${TAR_PATH}" > "${ENC_PATH}"

# 4. Upload as GitHub Release asset (bypasses git blob history bloat)
gh release create "backup-${BACKUP_DATE}" "${ENC_PATH}" \
  --repo "${REPO}" \
  --title "Encrypted Telethon Backup ${BACKUP_DATE}" \
  --notes "Full snapshot of cust 1-5 (49 sessions + configs). Encrypted with age AES-GCM/ChaCha20-Poly1305."

# 5. Cleanup temporary plain files
rm -rf "${STAGING_DIR}" "${TAR_PATH}" "${ENC_PATH}"
echo "Backup successfully created and uploaded to ${REPO}."
```

## Restoration Procedure

```bash
# 1. Download release asset
gh release download "backup-YYYYMMDD_HHMMSS" --repo "IndraYuda13/cust-backup-private" -p "*.age"

# 2. Decrypt
age -d cust_backup_*.tar.gz.age > cust_backup.tar.gz

# 3. Stop running screens or services
# screen -X -S cust1 quit ...

# 4. Extract into /root/cust/
tar -xzf cust_backup.tar.gz -C /root/cust/

# 5. Verify file permissions and start runners
chmod 600 /root/cust/reseller*/session/*.session
```
