# Host Layout Orientation (re-verify every run)

Topology map for the shared VPS so a cleanup session doesn't re-discover it. Numbers go stale within days — re-measure with `du`. Liveness goes stale within hours — re-check with `ps` / `docker ps` / `lsof` before acting on anything below.

## Disks
- `/dev/root` (~61G) — root filesystem. Critical when >90%; biggest consumers sit under `/root`.
- `/dev/sdb1` (`/mnt`, ~110G) — data disk: `/mnt/docker-data` is the Docker Root Dir; `/var/lib/containerd` symlinks to `/mnt/containerd`; also `/mnt/storage`, `/mnt/hermes-storage-offload` (fleet backups), `/mnt/ai-cache`, `/mnt/8ballpool-mod`, other project dirs.
- `/tmp` lives on the root disk (not tmpfs) — cleaning it frees root space.

## Routinely live (never clean)
- `/root/.hermes/profiles/<name>/` — one per Hermes profile: `state.db`, `cache/`, `browser-profile/`, `skills/` all in use. Only exception: your OWN profile's `cache/scratch` items stale >24h.
- `/root/.hermes/tools/` and `/root/.hermes/installs/` — live runtime (managed binaries + the gateway's venv). Never delete.
- `/root/projects/*` — per-project agent work; usually touched within 24h.
- `/root/.openclaw/` — another agent stack; node services run from `workspace/projects/*` (check `ps aux | grep -i openclaw`).
- `/root/.9router/` — 9router service listening on 20128; sqlite db under `db/`.
- `/root/.BurpSuite/` + `/opt/burpsuite/` — Burp behind the MCP (SSE 127.0.0.1:9876). `updates/` holds only the one-shot installer.
- Docker containers (n8n, surfshark proxy nodes, jualubot-platform business stack — keep its named `mysql-data` volume even at LINKS=0, telemetry, incidentops, lemonnokos, flaresolverr). All their volumes/networks are off-limits by default.

## Cleanup candidates by nature
- `/mnt/hermes-storage-offload/hermes-fleet-backups` — daily fleet snapshots (~9-10G); the oldest snapshots are the safe rotation target, with user approval.
- `/mnt/storage/root_cache` — regenerable caches (puppeteer, huggingface, ms-playwright, camoufox); also `/mnt/ai-cache` (huggingface, rembg).
- `/tmp` — stale build junk from modding/reversing work; pair age + `lsof` before deleting. Canonical artifacts live in project dirs like `/mnt/8ballpool-mod`.
- `/root/fleet-evidence`, `/root/reverse_work`, `/root/cust`, `/root/dailyfinance_web`, `/srv/*`, `/root/Downloads` — check mtimes; report as candidates, let the user decide.
- Docker images via `docker image prune -a` (safe); dead-project volumes only through the SKILL.md gate.
