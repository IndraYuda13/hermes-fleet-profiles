---
name: history-preserving-storage-audit
description: Use when auditing storage while preserving history.
---
# Read-only storage audit
- Write evidence only in your own scratch. Do not delete, move, prune, load models, install or restart in audit-only scope.
- Inventory lstat size, st_blocks*512, device/inode, nlink, symlink and mtime. Count reclaim once per inode only when all links are nominated; retained or unknown hardlinks yield zero reclaim.
- Stream SHA256 for APK duplicates. Test unsigned/aligned versus signed decompressed ZIP-entry equality separately, excluding signature metadata. Preserve originals and one representative per meaningful or uncertain revision.
- Match extracted files individually to retained original APK entries by size and SHA256. Protect unmatched patches/source; do not recommend whole fix trees by size alone.
- Read docs, scripts and journals for separate final/research branches and required build inputs. Preserve source, patches, signing keys, logs, captures and forensic dumps.
- Inspect /proc cwd, scoped argv paths, maps and fds plus systemd units/timers and model code/config references. Allowlist non-secret environment fields. Unmapped now does not mean unnecessary later.
- Treat HF cache blobs as shared content-addressed data. Save snapshot-to-blob reachability and revision metadata. Active HF_HOME and SDK model-root references disallow automatic cache-wide disposal.
- Keep target categories disjoint, re-stat targets at close, and emit exact candidate/keep manifests. Separate verified observations/calculations from unapproved proposals and unverified physical reclaim.
