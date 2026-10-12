---
name: self-hosted-service-operations
description: Operate, troubleshoot, deploy, or decommission self-hosted services, containers, bots, or local LLM runtimes on a VPS.
version: 2.0.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [vps, docker, systemd, services, maintenance, operations, llm]
    related_skills: [network-proxy-troubleshooting, cloudflare-tunnel-operations]
---

# Self-Hosted Service Operations

## When to Use

Use when a long-lived service on a VPS needs operating, troubleshooting, deployment, upgrade, or decommissioning: systemd units, Docker/Compose stacks, worker/bot daemons, scrapers, AI-agent servers, trading bots, or local LLM runtimes. For request-path failures through proxies, tunnels, or AI gateways use `network-proxy-troubleshooting`; for Cloudflare Tunnel specifics use `cloudflare-tunnel-operations`.

## Operating loop

1. Identify the owning service/container/unit, its configuration source, and the expected health signal.
2. Inspect status, recent logs, ports/networks, and disk/memory pressure before restarting anything.
3. Reproduce the request or job at the nearest useful boundary.
4. Change one configuration or runtime condition; restart/recreate only the affected unit.
5. Verify health, logs, external behavior, and disk/resource state after the change.

## Isolated candidate preparation before release

1. Read the production launcher, test bootstrap, port helpers and environment loading before running any test command. Derive the live DB endpoint from the actual app/provider process environment, printing only an allowlisted sanitized subset; a database named `test` can still serve production.
2. Record exact live Git HEAD and dirty paths. Create an independent candidate at that SHA with `git clone --no-hardlinks --no-checkout <live-repo> <candidate>` followed by checkout of the exact SHA. Preserve live dirty files separately; never raw-promote an older staging checkout or copy live `.next`/credential env into the test candidate. Compare storage across filesystems and put dependencies, builds, DB and evidence on the volume with headroom before considering cache deletion.
3. Provision a dedicated loopback PostgreSQL cluster when strong isolation is required. Compare live and candidate SQL identities, not names alone: `select current_database(), inet_server_addr(), inet_server_port(), current_setting('data_directory'), (select system_identifier from pg_control_system());`. Use a privileged read-only inspection connection where required; stop if identity proof is unavailable. Require distinct cluster identifier and data directory for a separate-cluster claim.
4. Generate a sanitized test-env loader with explicit app/provider/DB ports, test-only keys, disabled LLM gate and no real provider credentials, and server reuse disabled. Guard the exact candidate cwd, expected DB URL, actual cluster identity and env values before migrations/tests. Allow tracked `.env.example` files in the guard while rejecting runtime credential env files. Probe app/provider ports by binding loopback sockets and repeat immediately before launch; free-port evidence does not reserve a port.
5. Keep candidate dependencies private, not symlinked to live modules. If copied pnpm modules trigger a location-based reinstall, test `pnpm --config.verifyDepsBeforeRun=false exec <tool>` or direct `node <tool-cli>` for the unchanged dependency set. Do not mask a changed lockfile or missing dependency with this bypass. Pass the flag explicitly to child commands; shell wrappers are not reliably inherited by non-Bash subprocesses. Record executable versions separately from package pins and leave compatibility unverified until exercised.
6. Dump live DB read-only and protect backup files with restrictive permissions. Restore into a different isolated rehearsal DB from the synthetic app-test DB, because restored private production data must not become browser fixtures. Start restore from an empty DB; create needed cluster roles separately rather than bootstrapping schemas already contained in the dump. Use `pg_restore --exit-on-error`, preserve each failed attempt, and check every command exit instead of letting a later successful command mask failure.
7. If a CHECK function reads other restored tables and COPY fails, inspect its dependencies before changing anything. In the rehearsal DB only, try pre-data restore, temporarily remove the specific dependency-sensitive CHECK, restore data/post-data, recreate it `NOT VALID`, then `VALIDATE CONSTRAINT`. Do not certify success unless validation succeeds and table counts/invariants match the snapshot; never bypass constraints on live. Count equality is corroborating evidence, not a proof of identical contents.
8. Hand off concise Indonesian facts: absolute candidate/receipt/env/backup paths, commands to load and guard, exact SHA, identity comparison, free ports, tool versions, storage headroom, restore method and residual blockers. Prep-only scope must remain prep-only: no release claim, restart, deployment or full-suite claim without execution evidence. Recheck live dirty state and service identity after prep.

## Resource and log maintenance

- Start with filesystem and journal measurements; isolate heavy targets on `/` (e.g. `~/.openclaw`, `/usr`, `/var/lib`, `~/.npm`, `~/.cache`) vs `/mnt` (docker-data, containerd, backups, offload, big venvs). Keep large installs on `/mnt` to protect the root partition.
- Inspect stopped containers before pruning; never run an aggressive volume prune without explicit confirmation.
- Truncate an actively written log rather than removing its open file, and validate logrotate configuration after remediation. See `references/vps-disk-maintenance.md` and `references/logrotate-insecure-permissions.md`.
- After purging a user cache dir, recreate it (`mkdir -p`) — tools crash on a missing `~/.cache`.
- Flag disk ≥75% on `/` or `/mnt` in health reports even when not yet critical.
- Add Docker json-file log rotation (`max-size: 10m`, `max-file: 3`) to every container service — unrotated container logs bloat the disk.
- After a Docker daemon upgrade, legacy `docker-compose` v1 can fail recreations with `KeyError: 'ContainerConfig'` — force-remove the stuck container and switch to `docker compose` v2.
- Check `git status`/`git diff` before pulling self-hosted repos; local environment patches (proxy/SSRF overrides) cause stash-pop conflicts — resolve inline before building.

## Systemd units

- File tools block protected paths (`/etc/systemd/system`) — write unit files via terminal heredoc.
- Before starting a daemon, probe for lingering sessions or orphan processes (`screen -ls`, `tmux ls`, `pgrep -fa <script>`) — two instances on one SQLite DB (WAL) or download dir cause split-brain corruption and duplicate spend.
- Heavy pipelines need `TimeoutStopSec` ≥ 90s and `KillMode=mixed` so SIGTERM reaches the root process for graceful cleanup before SIGKILL escalates to the cgroup.
- Never use unconstrained `Restart=always`: add `StartLimitIntervalSec=300s` + `StartLimitBurst=5` under `[Unit]` to prevent crash-loop CPU spin and provider rate-limit burn.
- Python services: set `Environment=PYTHONUNBUFFERED=1`, journal stdio, and an explicit `SyslogIdentifier` so logs appear immediately in `journalctl -u <name> -f`.
- Use the exact virtualenv python in `ExecStart` AND in any inner subprocess creation — a generic `python3` in subprocesses causes C-extension/SQLite driver mismatches.
- Before restarting a Python service after code edits, run `<venv>/bin/python -m py_compile` on the modified modules — never crash-loop a live daemon on a syntax error.
- Bind internal dashboards to loopback (`127.0.0.1:<port>`) unless behind an authenticated reverse proxy; check socket availability first (`ss -tulpn`). Confirm "already running" from the socket, not from a `curl` any process on the port could satisfy, and name the listening PID.
- Honour an idempotent start rule literally: when told to start a service only if it is down, do NOT restart one that is up. A restart drops in-memory state other lanes may be mid-run against and destroys the timeline the caller was reasoning from; report the observed argv, PID, start time, and cwd instead.
- A service launched under `timeout <N>` (or any self-expiring wrapper) has a hard self-expiry. Read the wrapper's start time, compute `start + N`, and report the exact expiry so a later connection-refused reads as the predicted lapse rather than a new incident; raise the TTL only if asked, since a bounded lifetime is often deliberate.
- A dashboard streaming logs via SSE needs the daemon writing BOTH stdout (journald) and the tailed file (`FileHandler`) — logging to only one leaves the stream at 0 bytes.
- On a major-version cutover (new `WorkingDirectory`/`ExecStart`), preflight all dashboard endpoints against schema drift (renamed columns/tables cause instant 500s or zeroed telemetry).
- Never reuse a bounded soak-test entrypoint (e.g. `--hours 24`) as production `ExecStart`; production runners are infinite loops with graceful SIGTERM handling and scratch-disk cleanup per cycle.

### Unit removal and lifecycle

- `systemctl disable --now` before deleting; stop/disable the **timer first or together** for oneshot+timer pairs (service-only removal leaves a failed `not-found` timer); delete unit files plus `*.wants` symlinks; then `daemon-reload && reset-failed`; verify `systemctl --failed` is empty.
- Removal scope default is unit files only — do not delete project dirs, data, or logs unless explicitly asked; call out sibling units still present.

See `references/systemd-unit-lifecycle.md`, `references/multi-service-cluster-deployment.md`, `references/canary-and-traffic-shedding.md`.

### Locating a dormant / "lost" project

Systemd is the authoritative index, not the filesystem: `ls /etc/systemd/system/ | grep -iE "<kw1>|<kw2>"`, read `WorkingDirectory` from the unit, cross-check `docker ps -a` and cloudflared ingress configs. Projects can live outside the usual workspace dir (e.g. `/mnt/<name>`), so a projects-listing that comes back empty proves nothing. Confirm liveness with evidence (git log/remote; `sqlite3 <db> ".tables"` + row count) and report row counts with their staleness (DB mtime). Never declare a project dead from one missing directory. Avoid whole-workspace `grep -ril` — it times out on `node_modules`/`.venv`; scope searches to project dirs.

## Webhook receivers and payment bots

- Check BOTH the bot runner unit and the separate uvicorn webhook receiver unit (distinct ports) before blaming either.
- Verify callbacks from durable evidence — JSONL event logs or `deposits`/`orders` DB tables — not just service status.
- Probe FastAPI/Starlette `StaticFiles` mounts with GET, not HEAD: `curl -I` returns `405 Method Not Allowed`.

## Worker/bot runtime patterns

- Never feed whole multi-MB logs to polling web servers (`read_text().splitlines()` drives RSS to hundreds of MB); tail with a fixed-size binary seek and cap the line count.
- Do not create a `ThreadPoolExecutor` per HTTP request — per-request thread churn fragments glibc arenas (64MB each, RSS 500MB–1GB). Poll upstream from one persistent background worker thread and serve cached state from request handlers; set `Environment=MALLOC_ARENA_MAX=2` and `MemoryHigh`/`MemoryMax` in the unit.
- Protect shared JSON state files with a lock + atomic `os.replace` — concurrent non-atomic writes truncate the file mid-read.
- Persist cooldowns, backoffs, and upstream lock states (payout/ban guards) to durable storage, never in-memory variables — restarts reset them and cause startup bursts, spam, and upstream bans. Prefer passive polling of read-only status endpoints with backoff over active mutating retries, and disable dashboard triggers while an account is under upstream review.
- In multi-account proxy fleets, do not hard-bind one account to one node — run an active health probe (latency, consecutive timeouts) and fail over to standby ports; static 1:1 binding starves workers whenever a node hangs.
- Grep large daemon scripts for duplicate `def <method>(` definitions — later definitions silently shadow earlier ones with no syntax error.
- Stateful bots: verify exact virtualenv, account/token store, proxy format, and headless mode; preserve auth databases before resets. See `references/grass-bot-management.md` and `references/grass-proxies-generator.py`.
- Automated video pipelines on low-disk hosts: run jobs in `/dev/shm` scratch with guaranteed `try/finally` cleanup, pin FFmpeg resources (`-threads 2`, `nice -n 15 ionice -c 2 -n 7`, concurrency 1), and enforce CFR (`-fps_mode cfr -r 30`) with PTS re-basing to kill A/V drift. See `references/video-processing-pipeline.md`.

## Containerized search and proxy services

For SearXNG-like services, distinguish upstream engine blocking from local networking failure by inspecting container logs and testing proxy connectivity inside the container. Prefer a shared Docker network/service DNS over brittle host-bridge routes. Treat commercial/VPS proxy reputation as a separate issue from rotation configuration. See `references/searxng-operations.md`.

## Scraper, AI-agent, and Node.js services

- Treat Firecrawl-class stacks as the same operating loop: check Chromium/Postgres/Redis resource footprint and confirm auth/queue env vars are supported by the deployed version before restarting; test the API internally before exposing a tunnel. See `references/firecrawl-operations.md`, `references/firecrawl-self-hosted-legacy.md`, `references/firecrawl-custom-llm-config.md`.
- Self-hosted Python AI agents: keep heavy venvs on `/mnt`, wire local OpenAI-compatible gateways with a REAL key and explicit provider/model env (placeholder keys get 401; missing provider/model fails startup preflight), and when exposing via tunnel set `API_ALLOWED_HOSTS` + `API_AUTH_KEY`. Full Vibe-Trading deployment recipe: `references/ai-agent-services.md`.
- n8n behind a reverse proxy needs `N8N_PROXY_HOPS=1` and a pinned known-good version (do not float `latest` — regressions ship); npm installs require Node ≤22, so on newer hosts use Docker or nvm. Details in `references/ai-agent-services.md`.
- Next.js standalone daemons: use the standalone build's supported `PORT` env var rather than assuming `-p` works. Allocate a separate verified-free test port; never use `fuser -k` on an occupied port without identifying its owner and obtaining restart/stop authorization, because it can kill an unrelated or protected service. Honour an explicit provider freeze without diagnostic calls. For authorized combo-alias resolution and runtime details, see `references/nextjs-node-daemon.md`.
- Containers calling host services can trip internal SSRF/private-IP blocks unless whitelisted — prefer `extra_hosts: ["host.docker.internal:host-gateway"]` and route via `host.docker.internal`.

## Trading bots

OctoBot, NoFx AI Trading OS, and Hummingbot/Condor deployment, purge/reinstall, port-mapping, and encrypted-key recipes: `references/trading-bot-services.md`. Standing safeguard: enable simulator/paper-trading mode and store no real exchange credentials during setup.

## Reseller bot fleet

`cust1`–`cust5` unit template (ExecStartPre login cleanup), worker zombie diagnosis, and fleet restore: `references/reseller-bot-fleet.md`. Routine restart/bootstrap/status checks are also covered by the manage-server skill.

## Local LLM runtimes (CPU-only VPS)

- RAM decides whether a model fits; CPU cores decide generation speed — a high-RAM 4 vCPU host still bottlenecks a 32B model near ~1.3 tok/s.
- Verify AVX2/AVX-512 support (`lscpu | grep -E "Model name|Flags"`) before deploying — without vector extensions throughput is not viable.
- BitNet requires models natively pretrained with 1.58-bit ternary weights; standard models (Gemma, Llama, Qwen) cannot be post-training converted without destroying quality — use llama.cpp/Ollama standard quantization instead.

Sizing matrix, instruct-vs-reasoning behavior, and Ollama partial-blob recovery: `references/local-llm-sizing.md`.

## Cloudflare serverless apps

Self-hosted Workers/Pages/D1 apps (e.g. temp email): prefer GitHub Actions deployment for automated updates, or Wrangler CLI; requires Cloudflare Email Routing catch-all binding to the Worker. See `references/cloudflare-temp-email.md`.

## Quick VPS status snapshot

When the user asks "kondisi VPS", "status server", or a general health check, one batched shell is enough. Report as compact tables in Bahasa Indonesia (santai, no em dash).

```bash
hostname; uptime
free -h; nproc
df -h / /mnt 2>/dev/null; df -h | head -20
ps aux --sort=-%mem | head -12
systemctl --failed --no-pager
systemctl list-units --type=service --state=running --no-pager | head -40
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' 2>/dev/null | head -30
ss -tlnp 2>/dev/null | head -30
```

Report: host/uptime/load, RAM, disk (flag ≥75%), top mem consumers, failed units, key running services/containers. Offer to dig failed units or free disk — do not auto-delete or prune.

## Verification checklist

- [ ] The responsible unit/container and config path were identified.
- [ ] Relevant logs and resource measurements were collected before remediation.
- [ ] Only the affected service was restarted or recreated.
- [ ] The user-facing health signal and the service logs agree after the change.
- [ ] Any cleanup avoided unreviewed persistent volumes, credentials, and active logs.
- [ ] Unit removals also cleared paired timers; `systemctl --failed` is empty.
