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

## Pitfalls

- `docker system df` RECLAIMABLE is misaccounted: it can read "100% reclaimable" while every image is attached to a running container. Trust `docker ps` plus actual prune output over the column.
- `/var/lib/containerd` can be a symlink to `/mnt/containerd` (it is on this host) — containerd snapshots under /mnt look like disposable data but deleting them kills docker. Never touch; that size is live overhead.
- Directories that look archived can be live: big, "months old" dirs may have running processes launched from inside them. Always pair du + ls with a process check.
- Never touch: other Hermes profiles' dirs, DB dumps/secrets/backup dirs, sub-24h /tmp, project dirs touched today, browser profiles, running services' volumes/networks. Ambiguous candidate → list it for the user instead of acting.
- Full user sign-off ("gas") does not convert named data into junk — clean recreatable terra first, show real numbers, keep the judgment calls visible in the report.
- Check whether the same artifact exists twice (installer in home + cached copy) — delete one copy, not both.

## Reporting Format

Per disk: size / used / free / % + inode check. Then: what was cleaned (per item, real sizes), what was deliberately left untouched + why, remaining candidates ranked by size + risk with a recommended starting point. Indonesian, compact bullets.

## References

- `references/host-layout-orientation.md` — topology map of this VPS: which mounts/dirs are routinely live vs regenerable; re-verify liveness before acting.
