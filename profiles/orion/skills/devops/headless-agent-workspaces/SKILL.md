---
name: headless-agent-workspaces
description: Use when deploying headless desktop AI agent workspaces.
version: 1.0.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [vps, docker, openbot, desktop-agents, electron, headless, container]
    related_skills: [self-hosted-service-operations, vps-operations]
---

# Headless Desktop AI Agent Workspaces

## When to Use
- Deploying or maintaining desktop-first, local-first AI agent workspaces (such as OpenBot / openbot.run) in a headless Linux VPS environment.
- Running containerized Electron / Chromium agent applications without a physical monitor (using virtual display / Xvfb).
- Configuring Docker seccomp permissions for unprivileged user namespaces and Chromium sandboxing.
- Setting up outbound-relay agent hosts that do not require inbound HTTP ports or reverse proxies.

## Overview
Guidelines and operational procedures for deploying and maintaining desktop-first, local-first AI agent workspaces (such as OpenBot / openbot.run) in a headless Linux VPS environment.

## Architecture Classification: Relay vs Inbound Ingress
Before configuring network or proxy rules, identify the agent communication model:
- **Outbound Relay Workspaces (e.g. openbot.run / nightly-labs)**: Publishes **0 inbound ports**. The container talks outbound to account auth APIs, AI model providers, and WebRTC/Signal relays. Do not configure port forwarding, Nginx reverse proxy, or Cloudflare Tunnel ingress for these services; pairing is done via interactive CLI tokens (`openbot login` or `openbot mobile-connect`).
- **Inbound Web Agent Workspaces (e.g. CopilotKit OpenBot, Open-WebUI)**: Exposes HTTP APIs and Web UIs (typically ports 3000-3010). Must be audited against active VPS ports (`ss -tulpn`) to avoid collisions with local daemons (such as WhatsApp bridges or host PostgreSQL).

## Container Runtime Invariants

### 1. Seccomp Profile for User Namespaces
Electron-based desktop agent containers require user namespace creation (`clone` and `unshare`) for Chromium sandboxing:
- **Never use `--privileged`, `seccomp=unconfined`, or `--no-sandbox`**: Disabling sandboxing removes isolation between agent browser execution and the container host.
- **Tailored Seccomp**: Download and attach the official seccomp profile that explicitly permits unconfined `clone`/`unshare` flags while maintaining standard syscall restrictions:
  ```bash
  curl -fsSLO https://raw.githubusercontent.com/nightly-labs/openbot/main/docker/seccomp.json
  # Pass via: --security-opt seccomp=/path/to/seccomp.json --security-opt no-new-privileges:true
  ```

### 2. Shared Memory Allocation (`--shm-size 1g`)
Chromium multi-process rendering crashes with `SIGBUS` or tab freezes if restricted to Docker's default 64MB `/dev/shm`. Always allocate at least `--shm-size 1g`.

### 3. Graceful Termination Timeout (`--stop-timeout 60`)
Desktop agents maintain active SQLite databases (`openbot.db`) and background CLI processes. Docker's default 10s SIGTERM window is insufficient for WAL checkpoints and agent process flushing. Enforce `--stop-timeout 60` to prevent database corruption.

### 4. Non-Root File Ownership (UID 1000:1000)
Containerized desktop agents run under an unprivileged user (UID 1000, GID 1000). When bind-mounting host directories from secondary storage (e.g. `/mnt/<service>-data`):
```bash
mkdir -p /mnt/<service>-data
chown -R 1000:1000 /mnt/<service>-data
```
Failing to set permissions will cause startup crashes when creating keyrings (`/data/.local/share/keyrings`) or SQLite locks.

## Deployment Procedure on VPS (`/mnt` Storage)

1. **Verify Partition Space & Docker Daemon**:
   ```bash
   df -h /mnt
   docker --version
   ```
2. **Prepare Workspace & Seccomp Profile**:
   ```bash
   mkdir -p /mnt/openbot /mnt/openbot-data
   chown -R 1000:1000 /mnt/openbot-data
   cd /mnt/openbot
   curl -fsSLO https://raw.githubusercontent.com/nightly-labs/openbot/main/docker/seccomp.json
   ```
3. **Launch Container**:
   ```bash
   docker run -d --name openbot --restart unless-stopped \
     --security-opt seccomp=/mnt/openbot/seccomp.json \
     --security-opt no-new-privileges:true \
     --shm-size 1g --stop-timeout 60 \
     -v /mnt/openbot-data:/data \
     ghcr.io/nightly-labs/openbot:latest
   ```
4. **Authenticate & Pair**:
   - Email Login:
     ```bash
     docker exec -it openbot openbot login
     ```
   - Mobile Connect QR Pairing:
     ```bash
     docker exec -it openbot openbot mobile-connect
     ```
   - Verify Status:
     ```bash
     docker exec openbot openbot status
     ```

## Pitfalls & Lessons Learned
- **Do not assign host port mappings to relay-based agents**: Relay agents connect outbound; exposing arbitrary ports opens unneeded attack surfaces and causes unnecessary port hunting.
- **Keep `/data` volume unified**: Encryption keys in the container keyring decrypt session tokens and provider keys in `/data`. Splitting or partially mounting subdirectories breaks credential decryption.
- **Upgrades are strictly forward-compatible**: Newer versions migrate the SQLite schema. Never downgrade container image tags against an already-migrated data directory.
