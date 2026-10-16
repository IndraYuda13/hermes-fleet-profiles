---
name: vps-disk-cleanup
version: 1.0.0
author: Hermes Agent
title: VPS / Host Disk Cleanup
description: "Use when a VPS disk fills up: clean it safely."
tags: [sysadmin, disk, docker, cleanup, multi-agent-host]
related_skills: [service-origin-tracing, hermes-agent]
---

# VPS / Host Disk Cleanup

## When to Use

"cek storage vps", disk/capacity questions, "bersih bersih" on the shared VPS. The host runs one multiplexed Hermes gateway serving ~14 profiles plus dockerized services and several agent workspaces — every path is somebody's live work until proven otherwise. Goal: maximum space back, zero broken services.

## Procedure

1. **Baseline always first**: `df -h / /mnt`, `df -i`, `free -h`, `lsblk`. Identify which mount is critical (root is small and fills first; the big data disk is /mnt). Report % used per disk.
2. **Rank sizes with du — never guess**: `du -x -h -d1 / 2>/dev/null | sort -rh | head -25`, then drill one level at a time into the top offenders. `-x` keeps it on one filesystem.
3. **Date every candidate before deleting**: `ls -lat --time-style=long-iso <dir>` and `stat -c '%y' <path>`. Anything touched today = live. `find /tmp -maxdepth 1 -mtime +2` separates stale build junk; sub-24h /tmp items on this host are active agent work.
4. **Check ownership by processes**: `lsof +D <item> | wc -l` (per item, not over a whole tree), plus a direct `ps aux | grep '[a]ppname'` for the app that might own the dir. No process + old mtime = disposable; running process = hands off even if it looks like junk.
5. **Clean in safe tiers** (below), re-running `df -h` after each batch so every step's effect is visible.
6. **Verify services after**: `docker ps --format '{{.Names}}' | wc -l`, `ss -tlnp` for key ports. Then report: real du numbers per item, what was deliberately left and why, remaining candidates ranked for the user to approve. Reply in Indonesian.

## Safe tiers (high value, low risk)

- Logs: `journalctl --vacuum-size=50M`; `truncate -s 0` on noisy app logs (syslog, cloudflare-warp) — truncation, not deletion, keeps live writers happy; `find /var/log/sysstat -type f -mtime +5 -delete`; `apt-get clean`.
- One-shot installers / caches in home: e.g. `~/.BurpSuite/updates/*/*.sh` is a downloaded updater — deleting it does not affect the running app (confirm with `ps aux` which jar executes); `npm cache clean --force`; disabled snap revisions (`snap list --all` → `snap remove --revision=<rev> <snap>`, then `snap set system refresh.retain=2`).
- `/tmp` build junk older than 24h with lsof=0 and canonical copies preserved elsewhere (e.g. mod APKs kept under /mnt/<project>).
- Own-profile caches only: `~/.hermes/profiles/<own>/cache/scratch` items >1440 min; old `terminal-output`/`spillover` files. NEVER another profile's cache/state/browser-profile — a profile's `state.db` is a live database.
- Docker images: `docker image prune -a -f` is safe — running containers keep their images. Volumes need the gate below.

## Docker volume deletion gate (most dangerous step)

`docker system df -v` LINKS=0 means no container currently attaches the volume — it does NOT mean safe. Before each `docker volume rm`, require all three:
1. `docker ps -a` shows zero containers of that compose project (match the project prefix everywhere, not just running ones).
2. `docker volume inspect <vol>` labels show the dead project, or it is an anonymous leftover volume.
3. Read related containers' env (`docker inspect <c> --format '{{range .Config.Env}}...'`) to know what a next start would recreate. A stack whose bot/api run while its `mysql-data` volume shows LINKS=0 is still live — leave it.
Never run blanket `docker volume prune`: it deletes named unused volumes including live stacks' databases. Remove volumes explicitly by name.

## Log-flood triage (when syslog/journals are the disk hog)

- Find the spammer: `awk '{print $5}' /var/log/syslog | sort | uniq -c | sort -rn | head`, then confirm rate with two `stat -c%s` samples. A 500MB/day flood usually has ONE culprit process.
- Restart-loop unit (exit 78, `EADDRINUSE`, "already running"): check for a duplicate — `systemctl --user list-units` + `loginctl show-user root -p Linger`; disable the *system-level* duplicate (`systemctl disable --now <unit>`) and leave the healthy user-scope service running. Ping-loop `Restart=always` units re-spawn every ~20s; count with `journalctl -u <unit> --since today | grep -c starting`.
- Script spam loops (e.g. observer scanning stub DBs): back up the script first (`cp -p`), then patch: skip empty/<4KB stubs (`path.stat().st_size < 4096`) and throttle repeated warnings (per-key 600s gate). Restart via its unit name (`systemctl restart hermes-fleet-observer`).
- After `logrotate -f`, verify rsyslog recreated files: `/var/log` must be `drwxrwxr-x root:syslog` — if it lost group-write, rsyslogd suspends forever ("open error: Permission denied"); fix `chmod g+w /var/log` + `systemctl restart rsyslog` (reload not supported). Gzip the big rotated file: `gzip -f /var/log/syslog.1`.
- Corrupted 0-byte state JSON behind API 500: `cp -p` backup, then delete — most services recreate defaults on next read; verify with a curl of the API endpoint.

## Pitfalls

- Live work hides in /root/projects: multiple agent campaigns run in parallel here (15 'papannalar*' variants observed live on 2026-10-15; also lens-r2v, indra-shop, ceri-direction...). Judge liveness by process CWD, not by name: `ls -l /proc/[0-9]*/cwd | grep -oE '/root/projects/[A-Za-z0-9_.-]+' | sort | uniq -c | sort -rn`. `ps -eo cmd | grep <name>` substring-matches other commands' arguments and gives false '1 process' hits — forbid using it as a liveness proof, and never delete a project dir that shows a CWD hit or was written within 48h; the disk problem must be solved from caches/logs/spillover instead. `papannalar-*`/`lens-*` test harnesses (provider.mjs, ingress tunnels) launch from these dirs continuously.

- `~/.hermes/installs/<hash>/` looks like a stale duplicate venv but the multiplexed gateway + dashboard hold open leases on `.leases/` inside it (check `ls -l /proc/<pid>/fd | grep installs`). If leased, leave it — deleting breaks lease semantics; it also resolves per-process via `readlink /proc/<pid>/exe` (/root/.hermes/tools/.previous-python-*), not via PATH.
- `~/.BurpSuite/updates/*/burpsuite_linux_*.sh` (380M+) is deletable while Burp runs: verify first that the running `java` cmdline references `/opt/burpsuite/...jar`, not the updater. Burp re-downloads it on the next update check.
- Check for the project's own cleanup scripts before manual deletion — e.g. `/mnt/8ballpool-mod/cleanup_vps{,2,3}.sh` already encode what is safe to remove (re-runnable, idempotent); run those instead of guessing.
- qmd GPU dirs (`@node-llama-cpp/linux-x64-cuda*`, `linux-x64-vulkan`) are dead weight on this GPU-less VPS (wrapper forces GPU off) and are not reference-counted; moving them breaks nothing. qmd itself may already be broken (better-sqlite3 NODE_MODULE_VERSION mismatch) — capture `qmd vsearch` before/after so you can prove it was pre-existing.
- `/mnt/hermes-storage-offload/hermes-fleet-backups/` auto-grows ~400M per generation, several per day; September generations (>3wk) are safe to stage. Moving within /mnt frees nothing until staged data is deleted — say so in the report.
- Orphaned AI caches: `/mnt/ai-cache` (HF hub + rembg) had no refs anywhere and no file activity since September — verify with mtime + grep over scripts/env before deleting; retraining redownloads them. `~/.local/share/claude` (CLI + local data) can also go stale, but check last session date first.
- A git repo with almost no files can still be huge: `/mnt/MYvps_sparse` had 2.4G of packless loose objects under a 'No commits yet' repo (no refs/FETCH_HEAD, remote on GitHub) — count `find .git/objects -type f` and `git show-ref` before trashing; stage rather than delete when the objects can't be reproduced locally.
- `git gc --prune=now` on the hermes-agent checkout trimmed `.git` 645M->252M; safe while gateway runs (no dangling refs needed by the update flow's recovery closure lives under `hermes-update-recovery/`, a ref — packed objects stay).
- APK reverse-engineering dirs: delete `apktool_out/`, `jadx_out/`, `*_extract/` derived copies (regenerable from the source .xapk/.apk) and keep the original archive + scripts + JSON captures.
- `docker system df` RECLAIMABLE is misaccounted: it can read "100% reclaimable" while every image is attached to a running container. Trust `docker ps` plus actual prune output over the column.
- `/var/lib/containerd` can be a symlink to `/mnt/containerd` (it is on this host) — containerd snapshots under /mnt look like disposable data but deleting them kills docker. Never touch; that size is live overhead.
- Directories that look archived can be live: big, "months old" dirs may have running processes launched from inside them. Always pair du + ls with a process check.
- Never touch: other Hermes profiles' dirs, DB dumps/secrets/backup dirs, sub-24h /tmp, project dirs touched today, browser profiles, running services' volumes/networks. Ambiguous candidate → list it for the user instead of acting.
- Full user sign-off ("gas") does not convert named data into junk — clean recreatable terra first, show real numbers, keep the judgment calls visible in the report.
- Check whether the same artifact exists twice (installer in home + cached copy) — delete one copy, not both.
- Hardlink-cloned variant dirs (cp -al style, e.g. `papannalar*`): per-dir `du` double-counts shared inodes — get the true combined cost with ONE `du -sc` over all variants (7× papannalar*: 6.75G summed vs 5.88G unique) and split own vs shared via `find <dir> -type f -printf '%n %s\n'` nlink==1/nlink>1 byte sums. One clone can be nearly all hardlinks (frame-p3: 927M apparent / 69M unique); deleting a clone frees only its own bytes — shared bytes return only when the LAST holder is deleted. The pnpm store is empty on this host (4K), so node_modules clones are literal hardlink trees; plan deletions as a group.

## Reporting Format

Per disk: size / used / free / % + inode check. Then: what was cleaned (per item, real sizes), what was deliberately left untouched + why, remaining candidates ranked by size + risk with a recommended starting point. Indonesian, compact bullets.

## References

- `references/host-layout-orientation.md` — topology map of this VPS: which mounts/dirs are routinely live vs regenerable; re-verify liveness before acting.
