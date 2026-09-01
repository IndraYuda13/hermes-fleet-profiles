---
name: vps-disk-maintenance
description: Inspect, clean up, and maintain VPS disk space, troubleshoot log rotation failures, and manage systemd journal size.
---

# VPS Disk Maintenance

Guidelines for inspecting VPS disk space usage, identifying files/directories consuming large amounts of storage, safely clearing logs/caches, and troubleshooting log rotation (logrotate/journald) failures.

## Trigger Conditions
Use this skill when:
- Asked to check, inspect, or monitor VPS storage/disk space.
- Disk usage on the root partition (`/`) or other mount points is high (e.g., >85%).
- Logs are growing rapidly, or syslog rotation fails.

## Step-by-Step Maintenance Workflow

### 1. Inspect Disk Space Usage
Start by identifying where space is being consumed:
```bash
# Check overall disk usage
df -h

# Check top-level directories under root (excluding mounts if necessary)
du -h --max-depth=1 / 2>/dev/null | sort -hr
```

Common culprits to inspect next:
- `/var/log` (System and application logs)
- `/root` or `/home` (User files, caches, Node/NPM dependencies)
- `/var/lib/docker` or `/mnt/docker-data` (Docker volumes, images, containers)

### 2. Clean Up System Caches, Docker, & Runtimes
If space is tight, safely reclaim space from package managers, Docker, and runtimes:

#### Docker Cleanup
- **Docker Builder Cache (BuildKit/legacy build cache)**: Often holds tens of GBs of forgotten build layers.
  ```bash
  docker builder prune -f
  ```
- **CRITICAL PRE-CHECK**: Always list stopped containers and their sizes *before* running any prune command, so the user can verify no needed containers will be lost:
  ```bash
  docker ps -a --filter "status=exited" --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Size}}"
  ```
- **Safe Image Prune**: Clears unused images without touching stopped containers (preferred):
  ```bash
  docker image prune -f
  ```
- **Aggressive Prune**: Ask the user before running `docker system prune -a --volumes`.

#### Package, Decompilation & App Caches
```bash
# Clean apt & uv caches
apt-get clean
apt-get autoremove --purge

# Clean user/tool caches (always recreate ~/.cache after purging so tools don't break)
rm -rf ~/.cache && mkdir -p ~/.cache
rm -rf ~/.npm/_cacache
npm cache clean --force

# Clean decompilation, offload & temp directories
rm -rf /root/apk_extract /mnt/openclaw-offload /tmp/jadx_* /tmp/firecrawl
```

### 3. Manage and Vacuum Systemd Journals
Systemd journal files can consume gigabytes of storage over time. Limit their size:
```bash
# Check journal disk usage
journalctl --disk-usage

# Vacuum journal logs older than 7 days
journalctl --vacuum-time=7d

# Or restrict journal size to 500M
journalctl --vacuum-size=500M

# Restart systemd-journald to apply changes
systemctl restart systemd-journald
```

### 4. Clean Up and Troubleshoot Syslogs & Logrotate
When `/var/log/syslog` or `/var/log/syslog.1` grows extremely large, check if logrotate is failing:
```bash
# Run logrotate manually to verify
logrotate -f /etc/logrotate.d/rsyslog
```

#### Common Pitfall: Insecure Parent Directory Permissions
If logrotate fails with:
`error: skipping "/var/log/syslog" because parent directory has insecure permissions (It's world writable or writable by group which is not "root")`
This happens when `/var/log` is writable by a group (like `syslog` or `adm`) rather than just `root`.
- **Quick Fix/Workaround**:
  Either restrict the directory permissions (safely, as some services expect group write permissions):
  ```bash
  chmod 755 /var/log
  ```
  Or edit `/etc/logrotate.d/rsyslog` (or the global `/etc/logrotate.conf`) to include the `su` directive:
  ```text
  su root syslog
  ```

#### Safe Manual Log Truncation/Removal
Never delete an active log file that is being written to directly with `rm` without restarting its service, as the process will keep the file descriptor open and continue writing to deleted space (holding onto the storage).
- **Correct approach**:
  ```bash
  # Truncate the active syslog to 0 bytes
  truncate -s 0 /var/log/syslog
  
  # Or safely delete rotated/inactive logs (e.g. syslog.1, syslog.2.gz) and restart the logging service
  rm -f /var/log/syslog.1 /var/log/syslog.*.gz
  systemctl restart rsyslog
  ```

## Verification Checklist
- Run `df -h` to verify that space has been freed.
- For Docker cleanups, verify that no unintended containers were affected by checking `docker ps` before and after.
- Confirm system logging service is active and running: `systemctl status rsyslog`.
- Verify the active log file is being written to: `tail -n 20 /var/log/syslog`.

## Linked Reference Files
- [Logrotate Permissions & Workarounds](references/logrotate-insecure-permissions.md)
