---
name: vps-operations
description: Use when managing VPS security, git deploys, or AI apps.
version: 1.10.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [vps, ssh, fail2ban, git, deployment, reverse-proxy, security, fail-closed, devops, storage, maintenance, telemetry, speedtest, benchmarking, directory-conventions, scratch-hygiene]
---

# VPS Operations & Host Hardening Standard

Consolidated operational runbook for Linux VPS administration: automated attack triage, Fail2ban hardening, SSH key cutover, Git deployment hygiene, reverse-proxy ingress, fail-closed AI application architectures, host storage/process hygiene, directory placement standards, and telemetry/network benchmarking.

## When to Use
- Diagnosing authentication brute-force attacks, high `rsyslogd` CPU spikes, or configuring Fail2ban on public cloud servers.
- Safely transitioning SSH authentication to exclusive Ed25519/RSA keys without administrator lockouts.
- Deploying, pulling, and rebuilding Git repositories on live production VPS serving environments.
- Troubleshooting multi-tier ingress routing (Cloudflare Tunnel -> Nginx -> application daemons) and fail-closed AI application backends.
- Performing emergency disk rescue, purging hidden browser/package caches, and reaping container-orphaned zombie process storms.
- Establishing host directory placement standards, ephemeral scratch pruning (`TMPDIR`), and clutter audit protocols.
- Collecting synchronized host telemetry (CPU/RAM/Disk) or executing network speed benchmarks without CLI argument pitfalls.

## 1. Cloud Exposure & Automated Attack Triage

Public cloud IPv4 ranges (Azure, AWS, GCP, DigitalOcean) are continuously scanned by distributed botnets. Port 22 sweeps represent automated background radiation, not targeted intrusions.

### Fast Attack Triage
```bash
# Top attacking source IPs
grep "Failed password" /var/log/auth.log | awk '{for(i=1;i<=NF;i++) if($i=="from") print $(i+1)}' | sort | uniq -c | sort -nr | head -20

# Targeted usernames (generic sweeps target admin, ubuntu, root, deploy, test)
grep "Invalid user" /var/log/auth.log | awk '{for(i=1;i<=NF;i++) if($i=="user") print $(i+1)}' | sort | uniq -c | sort -nr | head -15
```

### OSINT Infrastructure Profiling
When assessing threat scale, profile top IPs with zero external dependencies:
```python
python3 -c "
import urllib.request, json
for ip in ['<ip1>', '<ip2>']:
    try:
        url = f'http://ip-api.com/json/{ip}?fields=status,country,city,isp,org,as'
        with urllib.request.urlopen(url, timeout=5) as r:
            print(ip, r.read().decode())
    except Exception as e:
        print(ip, e)
"
```
Diverse global hosting providers (e.g. DigitalOcean, Baidu, Hostzone) indicate distributed zombie swarms rather than localized human adversaries.

---

## 2. Hardened Fail2ban & 1-Strike Instant Ban

1. **Native Installation:**
   ```bash
   apt-get update && apt-get install -y fail2ban
   ```

2. **Configure `/etc/fail2ban/jail.local`:**
   Always use `.local` overrides, never edit `jail.conf` directly.
   ```ini
   [DEFAULT]
   bantime = 1d
   findtime = 10m
   maxretry = 3
   banaction = iptables-multiport

   # Exponential ban escalation for recidivists (1d -> 2d -> 4d up to 5 weeks)
   bantime.increment = true
   bantime.factor = 2
   bantime.maxtime = 5w

   [sshd]
   enabled = true
   port = ssh
   logpath = %(sshd_log)s
   backend = systemd
   mode = aggressive
   ```

3. **Zero-Tolerance (1-Strike Instant Ban) Mode:**
   When setting `maxretry = 1`:
   - **Mandatory Whitelist Invariant:** Always add the administrator's current public IP to `ignoreip` in `[DEFAULT]` before lowering `maxretry`. Dropping to 1-strike without whitelisting risks instant lockout on password typos.
   - Verify active session IP: `last -n 5` and `grep "Accepted" /var/log/auth.log | tail -n 5`.

4. **Service Verification:**
   ```bash
   systemctl daemon-reload && systemctl enable --now fail2ban
   fail2ban-client status sshd
   iptables -L f2b-sshd -v -n
   ```
   Incrementing `pkts` in `iptables` confirms the kernel firewall drops attack packets before they reach userspace `sshd` or generate disk I/O.

---

## 3. SSH Key Cutover & Safe Password Disabling

Switching to exclusive SSH key authentication eliminates password brute-force surfaces.

### Multi-Client Pre-flight Audit
Check existing keys: `cat /home/<username>/.ssh/authorized_keys`.
- **Lockout Prevention:** Administrators frequently use multiple endpoints (Termius laptop, Termux phone, desktop CLI). Verify that keys from *all* client machines are installed before disabling password authentication.

### Key Deployment Protocols
- **OpenSSH / macOS / Linux / Termux:**
  ```bash
  ssh-keygen -t ed25519 -C "device-label"
  ssh-copy-id -i ~/.ssh/id_ed25519.pub <username>@<vps-ip>
  ```
- **File Permissions:**
  ```bash
  chmod 700 /home/<username>/.ssh
  chmod 600 /home/<username>/.ssh/authorized_keys
  chown -R <username>:<username> /home/<username>/.ssh
  ```

### Safe Password Cutover Protocol
1. Keep the active SSH session open throughout configuration.
2. Check drop-in configuration evaluation order:
   ```bash
   sshd -T | grep -E "(passwordauthentication|kbdinteractiveauthentication|permitrootlogin)"
   ```
   OpenSSH evaluates `/etc/ssh/sshd_config.d/` alphabetically with first-match-wins. A file like `50-cloud-init.conf` with `PasswordAuthentication yes` overrides later configs.
3. Edit the highest-priority drop-in:
   ```ini
   PasswordAuthentication no
   KbdInteractiveAuthentication no
   ```
4. Test configuration syntax before reloading: `sshd -t`. If exit code is 0: `systemctl reload ssh`.
5. Verify effective settings: `sshd -T | grep -E "(passwordauthentication|kbdinteractiveauthentication)"` (both must show `no`).

### Sudden Port 22 Lockout Triage (Fail2ban Auto-Ban Trap)
When an administrator suddenly reports `Connection timed out` or `Connection reset` on port 22 across all client devices (laptop, mobile, terminal) right after testing credentials or before key enrollment completes:
1. **Root Cause Analysis:** Failed authentication attempts or probing SSH before a public key is registered trigger Fail2ban's sshd jail. Because mobile hotspots and residential connections share an ISP subnet or public IP, a single ban drops all traffic from that location at the firewall level.
2. **Immediate Unban:**
   ```bash
   fail2ban-client status sshd
   fail2ban-client unban <administrator-ip>
   ```
3. **ISP Subnet Whitelisting Invariant:**
   To prevent repeated lockouts during credential testing or iterative key setups, add the administrator's CIDR subnet to `ignoreip` in `/etc/fail2ban/jail.local`:
   ```ini
   ignoreip = 127.0.0.1/8 ::1 <admin-ip> 182.10.0.0/16 139.255.0.0/16 180.240.0.0/12
   ```
   Reload Fail2ban immediately: `systemctl reload fail2ban`.

### Enrolling New Client Devices Post-Password Cutover (`ssh-copy-id` Trap)
Once password authentication is disabled (`PasswordAuthentication no`), standard `ssh-copy-id -i ~/.ssh/id_ed25519.pub user@host` fails immediately with `Permission denied (publickey)` because the remote host rejects the initial password prompt required by `ssh-copy-id`. Users and operators frequently confuse this failure with "the VPS port is closed / external access is blocked".

To safely enroll a new client machine (laptop, desktop, or mobile) into a password-locked VPS:
1. **Clarify Access vs Authentication:** Confirm that port 22 remains reachable and listening (`ss -tlnp | grep :22`); only password authentication is closed.
2. **Client-Side Key Generation:**
   On the new client machine (Linux/macOS terminal, Termius, or Windows PowerShell/Git Bash):
   ```bash
   ssh-keygen -t ed25519 -C "new-device-label"
   cat ~/.ssh/id_ed25519.pub   # Windows: Get-Content ~\.ssh\id_ed25519.pub
   ```
3. **Canonical Username Resolution (8-Character Truncation Trap):**
   Classic `last` and `wtmp` utilities truncate usernames longer than 8 characters to 8 characters (e.g. `indrayuda` displays as `indrayud`). Never derive usernames for SSH configuration or `.ssh/authorized_keys` paths from bare `last` columns.
   - Always verify the true username via `/etc/passwd` (`getent passwd <user>` or `id -un`) or use `last -w` (`--fullnames`).
   - Using a truncated username in SSH client settings causes instant authentication failure (`Permission denied (publickey)`), and targeting `/home/<truncated>/.ssh/` fails with nonexistent path errors.
4. **Enrollment Pathways & Safe In-Band Append:**
   - **In-Band Automation/Agent Relay:** Have the user provide the single-line public key string (`ssh-ed25519 AAAAC3NzaC1lZDI1NTE5...`).
     - Always create a timestamped backup before mutation:
       ```bash
       cp -a /home/<username>/.ssh/authorized_keys /root/authorized_keys.<username>.$(date +%Y%m%d%H%M%S).bak
       ```
     - Ensure a preceding newline before appending:
       ```bash
       printf '\n# %s\n%s\n' "new-device-label" "<public_key_string>" >> /home/<username>/.ssh/authorized_keys
       ```
     - Enforce permissions: `chmod 700 /home/<username>/.ssh && chmod 600 /home/<username>/.ssh/authorized_keys && chown -R <username>:<username> /home/<username>/.ssh`.
     - Verify file integrity with `ssh-keygen -lf /home/<username>/.ssh/authorized_keys` to ensure OpenSSH parses all keys cleanly without line concatenation or format errors.
   - **Archive/Key Bundle Upload Triage & OpSec Sanitization:** Users frequently upload entire zipped `.ssh/` directories (e.g. `.ssh.zip`) containing both private keys (`id_ed25519`) and public keys (`id_ed25519.pub`).
     - *OpSec Sanitization:* Never print, echo, or store private keys in chat transcripts, logs, or persistent files. Extract in an isolated scratch path, inspect only the public key (`.pub`), and immediately purge the uploaded archive and private key (`rm -rf <scratch_dir> <uploaded_archive>`).
     - *Key Identification & Fingerprint Validation:* Extract the comment and type from the `.pub` file (`ssh-keygen -l -f id_ed25519.pub`). Compare against existing entries in `/root/.ssh/authorized_keys` and `/home/<username>/.ssh/authorized_keys`.
   - **Bridge via Existing Authorized Device:** If the operator has another device already authorized (e.g. smartphone running Termux or previous workstation), SSH from that device and append the new key string to `.ssh/authorized_keys`.
   - **Encrypted Manager Key Sync:** If using SSH clients with cloud key synchronization (e.g. Termius), logging into the client account automatically synchronizes existing private keys without host-side reconfiguration.
5. **Dual Privilege-Tier Key Sync Invariant:**
   If both a non-root administrative account (`/home/<username>`) and `root` exist on the host, append the new public key to both locations:
   - `/home/<username>/.ssh/authorized_keys`
   - `/root/.ssh/authorized_keys` (when root key login is permitted via `PermitRootLogin without-password` or `prohibit-password`).
   This prevents administrative lockouts during privilege-specific tasks or emergency recoveries.
6. **Pre-Handoff Fail2ban Audit & Client Setup Checklist:**
   - Before handing off connection instructions to the user, run `fail2ban-client status sshd` and check whether the administrator's IP was jailed during earlier connection attempts. Unban if necessary (`fail2ban-client unban <ip>`).
   - In GUI/mobile clients (Termius, JuiceSSH, PuTTY): explicitly instruct the user to configure the host entry with the full canonical username, public host IP, port 22, and select the enrolled Key from the Keychain rather than username/password authentication.

### Re-Enabling Password Authentication & Cloud-Init / Locked-Root Traps
When temporarily or permanently re-enabling password authentication on cloud VPS instances (Azure, AWS, GCP, Ubuntu cloudimg):
1. **First-Match-Wins Drop-In Precedence & PAM Interactive Auth:**
   Cloud images typically place `PasswordAuthentication no` and `KbdInteractiveAuthentication no` inside `/etc/ssh/sshd_config.d/50-cloud-init.conf` or `60-cloudimg-settings.conf`. Because OpenSSH parses drop-ins in alphabetical order and respects first-match-wins, adding settings to `/etc/ssh/sshd_config` (below `Include`) or a high-numbered drop-in (e.g. `99-custom.conf`) has NO effect.
   - Always place the override in a lower-numbered drop-in, such as `/etc/ssh/sshd_config.d/01-password-auth.conf`:
     ```ini
     PasswordAuthentication yes
     KbdInteractiveAuthentication yes
     ```
   - *Why `KbdInteractiveAuthentication yes` is mandatory:* Many clients (Termius, PuTTY, newer OpenSSH) negotiate password authentication via PAM keyboard-interactive prompts. If this remains `no`, clients attempting keyboard-interactive auth will be rejected even if `PasswordAuthentication` is `yes`.
2. **Locked Root Password Trap (`passwd -S root`) vs Non-Root User:**
   On cloud images, the `root` account password is often locked by default (`L` status in `passwd -S root` or `*`/`!` in `/etc/shadow`), and `PermitRootLogin` defaults to `without-password` or `prohibit-password`. Setting `PasswordAuthentication yes` alone is insufficient to log in as root; sshd will reject password login.
   - For direct root password access, both SSH config and shadow status must be updated:
     ```bash
     cat << 'EOF' > /etc/ssh/sshd_config.d/01-password-auth.conf
     PasswordAuthentication yes
     KbdInteractiveAuthentication yes
     PermitRootLogin yes
     EOF
     passwd root  # Set an active password to unlock the account
     systemctl restart ssh.service
     ```
   - For standard users whose passwords are already active (`P` status in `passwd -S <user>`): `01-password-auth.conf` takes effect immediately without resetting passwords. Verify the user has sudo elevation access: `groups <username>` (must include `sudo` or `wheel`).
3. **Socket-Activation Restart & Verification Command:**
   Ubuntu 22.04/24.04 uses systemd socket activation for ssh (`ssh.socket`). A simple `reload` may not apply socket changes cleanly. Always run `systemctl restart ssh.service` and verify active settings with `sshd -T`:
   ```bash
   systemctl restart ssh.service
   sshd -T | grep -E "(passwordauthentication|kbdinteractiveauthentication|permitrootlogin)"
   ```
   All directives must reflect the desired state before testing remote connection.
4. **Reverting Temporary Password Auth Back to Key-Only:**
   Once key enrollment or testing is confirmed, cleanly remove the temporary drop-in override:
   ```bash
   rm -f /etc/ssh/sshd_config.d/01-password-auth.conf
   sshd -t
   sshd -T | grep -E -i "(passwordauthentication|kbdinteractiveauthentication)"
   systemctl restart ssh.service
   ```
   Verify both directives report `no`. Existing active SSH sessions remain connected; new logins without an authorized key are rejected.

---

## 4. VPS Git Deployment Hygiene

A VPS running live services is a runtime environment, not a development sandbox.

### Core Rules
1. **Pull & Run Only Mandate:** Never write ad-hoc application code patches, refactorings, or Git commits directly on the VPS repository. If a project is designated as read-only / pull-and-run on the host, strictly enforce this: all code modifications must occur on local developer environments, committed, pushed to GitHub/remote, and pulled to the VPS.
2. **Upstream Remote as Truth:** Application changes must be authored, tested, committed, and pushed on local development workstations. The VPS pulls verified commits only.
3. **Preserve Pinned Host-Only Patches:** Identify and preserve necessary local host-only runtime patches (such as reverse-proxy header forwarding, QR pairing origins, or local socket binds) across git pulls using targeted stashes. Never discard them or commit them upstream.
4. **No Unrequested Resets:** Never run aggressive resets (`git reset --hard`, `git clean -fdx`) on a deployment directory without backing up uncommitted or local-only configurations.
5. **Ephemeral Staging vs Upstream Git Sync:** When a user requests temporary local staging changes on the VPS (e.g. testing local wire connectors or local models before authoring the upstream PR):
   - Never commit or push temporary staging modifications from the VPS to GitHub/remote.
   - Explicitly record all local modifications in session notes.
   - Revert intermediate test artifacts (e.g. `git checkout -- <file>`) to keep `git status` clean and prevent merge conflicts during future `git pull`.

### Synchronizing Upstream Changes
1. **Non-Destructive Remote Check:**
   Check for upstream commits without altering the working directory:
   ```bash
   git fetch origin <target-branch>
   git log HEAD..origin/<target-branch> --oneline
   ```
2. **Preserve Host Runtime Patches via Stash:**
   When the host requires uncommitted environment-specific adjustments (e.g. reverse proxy header forwarding or socket paths), stash before pull to avoid merge aborts:
   ```bash
   git stash push -m "vps-host-patch"
   git pull origin <target-branch>
   git stash pop
   ```
   - *Resolving Upstream Collisions on Host-Only Patches:* If upstream commits touch adjacent lines in the patched file (e.g. adding new API action branches in a pairing service), `git stash pop` may flag a conflict. Resolve the conflict by preserving both: keep upstream's new handlers while retaining host-specific overrides (e.g. `x-forwarded-*` header reconstruction or local socket binds). Verify syntax (`npx tsc --noEmit` or build check) before proceeding.
3. **Post-Build Tree Hygiene:**
   Build processes may mutate tracked test artifacts or generate untracked workers. Revert unintended changes to tracked artifacts with `git checkout -- <file>`. Never run `git clean -fdx` blindly, as it deletes untracked build bundles, cached certs, or host env files.
4. **Handling Diverged Tarball Histories:** If the directory originated from an unzipped archive, `git pull` may fail with `unrelated histories`. Back up local diffs, checkout the upstream commit cleanly, and test patches with `git apply --check`.
5. **Rebuild & Reload:**
   - Reinstall dependencies only if lockfiles changed (`pnpm install`, `npm ci`, `pip install`).
   - Run production build (`npm run build`).
   - Restart specific unit: `systemctl restart <unit>.service`.
   - Verify health: `systemctl status <unit>.service` and `curl -s -I https://<domain>`.

### Common Deployment Traps
- **Supervisor Process Child-Exit Leak (502 Bad Gateway with Active Unit):** When running a supervisor script (e.g. Node/Python script orchestrating web servers, mock providers, or tunnel daemons under systemd), never guard child process exit handlers with `if (code)` alone:
  `child.on("exit", (code) => { if (code) { cleanup(); process.exit(code); } })`
  If a child is terminated by a signal (e.g. SIGTERM, SIGKILL, OOM-killer) or exits cleanly (`code === 0`), `code` is null or 0 (falsy). The supervisor ignores the exit, keeping its own process running while the web server child is dead. Systemd sees the main supervisor PID alive, so it never restarts the unit (`Restart=on-failure`), leaving Nginx/Cloudflare returning 502 Bad Gateway indefinitely. Always propagate any child exit immediately: `child.on("exit", (code, signal) => { cleanup(); process.exit(code ?? (signal ? 1 : 0)); });`.
- **Database Migrations on Pull:** Upstream commits often introduce new SQL migrations (e.g. `supabase/migrations/<timestamp>_<name>.sql` for schema changes or board resets). When local Postgres/Supabase services are active, check if new migration files exist in the pulled commits (`git diff HEAD origin/<branch> -- supabase/migrations/`). Execute the project's migration/preparation runner (e.g. `node scripts/test-db.mjs prepare` or `npm run db:migrate`) BEFORE compiling Next.js. Next.js static generation (`next build`) runs database queries at build time; missing tables or columns from unapplied migrations will cause static page generation to crash during build.
- **Build Script Tracked-Artifact Pollution:** Compiling production builds often triggers pre-build or bundle generation scripts (e.g. `prepare-assets`, OMR worker generation, QA artifact bundlers) that mutate tracked test fixtures or manifests (e.g. `artifacts/qa/**/bundle.json`). Immediately inspect `git status` after building and revert unintentional modifications to tracked repository artifacts (`git checkout <file>`) to prevent dirty-tree blocking on future `git pull` or `git stash` operations.
- **Next.js Standalone Build Asset Sync (`output: 'standalone'`):** When deploying a Next.js application configured for standalone output on a VPS systemd service, `npm run build` only places minimal runtime files into `.next/standalone/`. It does not automatically copy `.next/static/` or `public/` into `.next/standalone/`. If the systemd unit runs `node .next/standalone/server.js`, client CSS, fonts, and JS chunks will 404 unless `.next/static` is synced to `.next/standalone/.next/static` and `public` is copied to `.next/standalone/public`. Verify this copy step in the build script or deployment pipeline before reloading systemd.
- **Next.js Standalone Ephemeral Build Wipe & Persistent Media Storage Trap:** In Next.js standalone mode (`output: 'standalone'`), `next build` purges and regenerates the `.next/` directory from scratch. If application code resolves storage paths relative to `process.cwd()` (e.g. `path.resolve(process.cwd(), 'storage/audio')`) while the server process runs inside `.next/standalone/`, files are saved under `.next/standalone/storage/`. On subsequent builds or redeployments, `.next/` is wiped, permanently deleting all user uploads or generated media while leaving database metadata intact.
  - *Symptom:* Metadata queries report media exists (`hasAudio: true`), rendering active player controls in the UI, but playback triggers HTTP 404 stream errors ("File missing on disk").
  - *Diagnosis:* Compare database `created_at` against `.next` directory mtime (`stat -c %y .next`). If missing files have creation timestamps *before* the build mtime and surviving files have timestamps *after* it, the storage was wiped during build.
  - *Remediation:* Enforce persistent storage roots outside `.next/` entirely (e.g. `<project-root>/storage` or `/var/data/...`) via explicit absolute environment variables (`STORAGE_DIR` / `DATA_DIR`), never relying on relative `process.cwd()`. In metadata/status endpoints, verify `fs.existsSync(file_path)` before asserting resource presence to prevent misleading client UI states.
- **Commit Timestamp Newer than Build Timestamp Diagnostic:** When auditing whether a live build is stale (`git log` commit time is newer than `.next/BUILD_ID`), do not conclude the build is stale solely from timestamps. If a commit was authored immediately after build or touched only docs/formatting without altering compiled source, test for the commit's changes directly: grep unique string tokens or function identifiers introduced in the commit diff against the compiled standalone bundle (`grep -rn '<unique_token>' .next/standalone/.next/server/`). If the token is present in compiled chunks, the active build is fresh.
- **Port Listener Probe vs Unit State:** After `systemctl restart <service>`, do not conclude the service is ready solely from `systemctl is-active`. A daemon running under Node/Next.js may report active for several seconds while bootstrapping or fail on cold-start routes. Probe the internal loopback socket (`curl -s -I http://127.0.0.1:<port>`) or check socket bindings (`ss -tlnp | grep <port>`) to confirm the process has bound to the listening port before verifying ingress.
- **Staging Database Fixture Seeding:** When exercising API endpoints that validate deep session state (e.g. classroom session syncing, teacher pairings) against PostgreSQL or SQLite, avoid empty JSON stub payloads that violate database schema validation. Seed valid payloads using existing test harness fixtures (e.g. `syncFixture().payload`) so endpoints return valid sync records instead of failing silently with 500 or 400 errors.
- **Reverse-Proxy Origin Headers (QR Pairing):** Behind Cloudflare Tunnel or Nginx, internal requests resolve `origin` to `http://127.0.0.1:<port>`. Public handoffs (mobile QR pairing, OAuth redirects) must reconstruct the origin from `x-forwarded-proto` and `x-forwarded-host`.
- **Migration Checksum Mismatch from Whitespace:** When database migration tables verify SHA-256 digests, upstream commits touching whitespace trigger `Applied migration changed: <file>.sql`. Do not edit repository migration SQL files on the VPS; update the digest in the database tracking table directly (`sha256sum <file>`).
- **In-Memory Mocks in Staging:** Check whether demo routes (e.g. `/auth/sample`, mock Supabase/auth doubles) are enabled before diagnosing phantom SMTP/DNS delivery issues.

---

## 5. Ingress Diagnostics & Fail-Closed AI Operations

For web applications running AI models or reverse proxies across multi-tier boundaries:
`Public Subdomain -> Cloudflare Tunnel -> Nginx -> Node/Next.js -> DB`

### Hop-by-Hop Ingress Diagnostics
1. Check public ingress: `curl -s -I https://<domain>/`
2. Check local reverse proxy: `curl -s -I http://127.0.0.1:<nginx_port>`
3. Check application daemon: `curl -s -I http://127.0.0.1:<app_port>`
4. Inspect unit journal: `journalctl -u <service> -n 30 --no-pager`

### Ingress & Tunnel Diagnostic Traps
- **Custom Cloudflare Tunnel Service Naming Trap:** Never assume the tunnel daemon runs under `cloudflared.service`. On customized hosts, it often runs under specific instance names like `cloudflared-vps-baru.service`. Verify active tunnel services with `systemctl list-units --type=service --state=running | grep -iE "cloudfl|tunnel"` or `pgrep -af cloudflared`.
- **502 Bad Gateway vs Parked/Disabled Unit Triage:** When probing multiple ingress hostnames and receiving 502 Bad Gateway (port connection refused), check whether the origin units are status `disabled` in systemd (`systemctl list-unit-files --state=disabled`). Distinguish intentionally parked/disabled services from crashed or failed active units before declaring an incident.
- **Canonical Ingress Hostname Extraction:** Do not guess domain extensions or hostnames (e.g. testing `papannalar.my.id` which fails with NXDOMAIN). Extract authoritative hostnames directly from the active tunnel config: `grep -E '^\s*-\s*hostname:' /etc/cloudflared/config*.yml`.

### Fail-Closed AI Architectural Guardrails
1. **Silent AI Failure Triage ("Button Clicked but Nothing Happens"):** When an interactive AI generation flow appears unresponsive without surfacing UI errors:
   - *Client Abort vs Model Generation Latency:* Check if the frontend instantiates an `AbortController` with a tight timeout (e.g. 5000ms). LLMs with reasoning/thinking phases or external gateway hops often require 6–12s. The client aborts silently before the response arrives. Ensure frontend timeouts (e.g. 15000ms) align with backend deadlines.
   - *Static Approval & Privacy Manifests:* Verify whether the route gates requests on a static review object (e.g. `PRIVACY_REVIEW !== null` or strategy hash manifests). In demo/staging modes, unpopulated review manifests silently reject requests or drop into static fallbacks.
   - *Premature History / Sync Verification:* Guarding AI routes by asserting that the session exists in permanent historical sync logs (`history.records.some(r => r.sessionId === id)`) rejects valid in-progress, newly initiated, or sample sessions that have not yet dispatched a sync upload. Validate authenticated ownership/scope rather than finished sync records.
2. **Configuration-Gated AI Fallbacks:** Gate AI features on system-wide provider configuration readiness (`cfg.enabled && cfg.provider.profile`) rather than hardcoding user-ID blocks (`teacher.id === SAMPLE_TEACHER_ID`), allowing demo accounts to exercise interactive flows when explicitly enabled without code changes.
2. **Transparent Static Fallback:** When `LLM_ENABLED=false` or upstream APIs fail, return pre-authored domain assets seamlessly (e.g. static strategy cards for teacher hints, template story frames for question generation). Never leak raw HTTP 500 errors to end users.
3. **Pedagogical & Role-Separation Guardrail:** In educational or multi-role platforms, orient AI to assist facilitators/teachers (whispering scaffolding, misconception diagnosis, contextual story enrichment) rather than answering directly on behalf of end users/students, keeping student interfaces grounded and deterministic.
4. **Content Whitelist & Hash Verification:** Incoming strategy or prompt codes must match an explicit approval manifest verified against SHA-256 hashes before dispatch. Unapproved codes fail closed to static fallbacks before any network call reaches the AI gateway.
5. **Database Token Ledger & Atomic RPC Reservation:** Enforce concurrency caps (e.g. 1 active generation per user) and rate limits via an atomic database reservation function (`llm_control`). Log only token usage and receipt metadata; never store raw user prompts in shared databases.
6. **PII Sanitization Gate:** Strip personal identifiers and roster numbers client-side and server-side before outbound API dispatch.
7. **OpenAI-Compatible Swaps & Latency Budgeting:** When connecting local or reverse-proxy OpenAI-compatible models (e.g. 9router, vLLM):
   - *Latency vs. Endpoint Deadlines:* Models with reasoning/thinking tokens (e.g. `ag-opus-pool`, `gemini-3.8-flash`, Claude extended thinking taking ~6-10s) will exceed tight synchronous endpoints (e.g. 5s hard timeout for real-time classroom suggestions) and trigger static fallbacks, while easily fitting background/enrichment deadlines (30s+). Ensure both route-level timeouts and server-side deadline calculators are budgeted consistently (e.g. 15-20s for interactive, 30-60s for batch tasks).
   - *Database Profile & Ledger Constraints:* In applications recording AI usage to audit tables (e.g. `llm_profiles`, `llm_usage` in PostgreSQL), registering a new OpenAI-compatible proxy profile (e.g. `local-9router`) requires inserting the profile row and verifying foreign-key or check constraints beforehand to prevent usage recording transactions from failing.
   - *Reverse Gateway Bridge:* Translate requests to OpenAI `/v1/chat/completions` locally and wrap responses into the expected vendor envelope to avoid modifying frozen codebases or DB ledger schemas.
   - *Native Abstraction:* Add `OpenAICompatibleProvider` to application configuration while simultaneously widening database JSON schema constraints (`const` -> `enum`/pattern allowlist).

---

## 6. Live Feature Demonstration & User Journey Walkthroughs

When demonstrating, verifying, or handing off newly deployed features on a live VPS for users who ask "where is it / how do I get there / I am confused":
- **Zero-Assumed-Context Entry:** Never present only direct sub-view URLs or screenshots of isolated nested components. Users navigate from public entry points (landing, login, or main dashboard).
- **Interactive Multi-Step Journey:** Break down the walkthrough into sequential stages starting from entry to active state:
  1. *Authentication / Demo Entry:* How to enter from scratch (e.g. `/masuk`, clicking "Coba dengan data contoh", or logging in).
  2. *Top-Level Navigation:* Which card or menu item leads to the workspace (e.g. clicking "Buka latihan & AI" from the teacher hub).
  3. *Step-by-Step Section Sequence:* Guide through the numbered stages on the page (e.g. Step 1: Siapkan latihan -> Step 2: Tambahkan cerita & bantuan AI -> Step 3: Mulai mengajar / Layar).
  4. *Side-by-Side Comparison & Generation Proof:* Capture the before-and-after or input-vs-output comparison view (e.g. original prompt vs generated story, or question vs AI suggestion) so the user clearly sees what the feature produced.
- **Numbered Artifact Sequencing:** Prefix deliverable screenshots sequentially (`01-landing-entry.png`, `02-flow-overview.png`, `03-feature-live.png`) and send them directly via `MEDIA:/path/to/file` so the user can follow along visually in chat without cognitive friction.

---

## 7. Host Storage & Process Hygiene (Disk Rescue & Zombie Reaping)

Long-lived production VPS servers running background workers, headless browsers, and containerized schedulers accumulate hidden disk hogs and process table leaks.

### Non-Overlapping Filesystem Probes & Inode Audit Protocol
When checking storage conditions or profiling disk consumption:
1. **Never Run Unbounded `du` across Root:**
   - *The Trap:* Running bare `du -d1 -h /` traverses across mount boundaries into `/mnt` (often 50–100+ GB secondary drives), Docker overlayfs points, and pseudo-filesystems (`/proc`, `/sys`). This produces distorted results, hangs on virtual mounts, and double-counts storage.
   - *The Rule:* Always use `du -x` (`--one-file-system`) to strictly bound disk usage calculations to the targeted partition:
     ```bash
     # Top consumers strictly on the root partition
     du -x -d1 -h / 2>/dev/null | sort -rh | head -15

     # Top consumers on secondary persistent mounts
     du -x -d1 -h /mnt 2>/dev/null | sort -rh | head -15
     ```
   - **Quick Storage Check (fast path for "cek storage" requests):** run the partition check first, then bounded top-level sizes. Include hidden dot-directories with `/root/.[!.]*`, because `/root/.[a-z]*` silently skips dot-dirs whose names start with a digit or capital. Always pass `-x` to `du`, even on simple `du -sh` variants.
     ```bash
     df -h /root /mnt
     du -xsh /root/* /root/.[!.]* 2>/dev/null | sort -rh | head -12
     du -xsh /mnt/* 2>/dev/null | sort -rh | head -12
     ```
     Run `df` again immediately before reporting, since shared hosts change during the scan.
2. **Dual Block & Inode Audit (`df -hT` + `df -ih`):**
   - Disk full errors (`No space left on device`) can be caused by block exhaustion OR inode exhaustion.
   - Always run both checks simultaneously:
     ```bash
     df -hT | grep -v tmpfs
     df -ih | grep -v tmpfs
     ```
   - If blocks show free space but writes fail, check `IUse%`. Millions of tiny files (session files, lockfiles, temporary scraping chunks) exhaust the inode table.

3. **Multi-Agent Profile Cache Triage (`~/.hermes/profiles/` & `~/.openclaw/`):**
   - In autonomous fleet environments with multiple agent profiles (e.g. Orion, Forge, Frame, Prism), each profile maintains independent scratch directories and browser profiles:
     ```bash
     du -x -d0 -h ~/.hermes/profiles/*/cache/scratch ~/.hermes/profiles/*/browser-profile 2>/dev/null | sort -rh
     ```
   - Scratch directories (`.../cache/scratch`) are safe Tier 1 garbage to prune, whereas browser profiles require targeted pruning of cache subfolders only (`Default/Cache/*`), preserving session cookies and credentials.

### Storage Reporting Presentation Standard
- **Quick-request format:** when the operator asks for a fast check ("cek cepat", "cek storage sekarang"), reply with a short summary: one line per partition (used / total / free / percent), then the top 5 consumers per partition. Put the deeper breakdown and cleanup options behind an offer, not in the first reply. Match the operator's language and casual register.
- **Full reviews** (only when asked) use the rules below.
- **Partition Separation:** Clearly distinguish root `/` (system) from secondary mount `/mnt` (data). Never lump them together into a single ambiguous percentage.
- **Threshold Warning:** Explicitly call out when a partition crosses the critical 90% threshold (e.g. `/` at 91%, remaining 6.1 GB).
- **Categorized Breakdown:** Group usage by top consumers (e.g. `/root/.hermes`, `/root/projects`, Docker, container runtimes).
- **Tiered Action Plan:** Present immediate, zero-risk cleanup targets (scratch caches, dangling Docker images) alongside items requiring caution/confirmation. Execute zero destructive commands without explicit operator approval.

### Two-Tier Disk Rescue Protocol (Spikes Near 100% / <1 GB Free)
When emergency disk reclamation is required, categorize targets strictly into two tiers before taking action:

#### Tier 1: 100% Regenerable Garbage (Safe for Immediate Purge)
1. **Chrome BrowserMetrics Dump Accumulation (`.pma` files):**
   Headless Chrome/Chromium sessions (scrapers, solvers, auth probes, backup scripts) write a ~4MB `.pma` diagnostic dump on every launch. These accumulate across root and per-profile directories.
   ```bash
   # Scope each delete to one named browser home; never a wide find over /root
   find /root/.config/google-chrome -maxdepth 2 -name 'BrowserMetrics*.pma' -delete 2>/dev/null || true
   find /root/.hermes/profiles -maxdepth 6 -name 'BrowserMetrics*.pma' -delete 2>/dev/null || true
   find /root/.openclaw/browser -maxdepth 5 -name 'BrowserMetrics*.pma' -delete 2>/dev/null || true
   ```
   - **Scope rule:** keep each delete command bound to one named path. A broad recursive delete spanning `/root` or the interpreter/runtime tree is refused by the runtime guard, and it is unsafe even when allowed. Run one command per target class so a refusal does not hide the others.
   - Hermes profile browser homes live under `~/.hermes/profiles/<profile>/browser-profile/chrome/`, not `~/.hermes/browser-profile`.
   - **Automated Watchdog Invariant:** A one-time purge is insufficient because background automation will regenerate files. Always embed `.pma` cleanup rules into the host's recurring maintenance script (`disk_watchdog.sh` or cron) so they are cleared automatically every hour.
2. **Selective Browser Profile Cache Pruning (Cache vs Session Invariant):**
   - Safe to delete: `Default/Cache/*`, `Default/Code Cache/*`, and `component_crx_cache/*`.
   - **Never delete:** `Cookies`, `Login Data`, `Web Data`, `Local Storage/`, `Session Storage/`, `WebStorage/`, `IndexedDB/`, `Service Worker/`, `History`, or `Preferences`. Several of these are session or offline-app data that a cache purge does not regenerate; `Service Worker/` often holds the largest share of a profile and is still session-bound. Purging the entire profile destroys live authenticated sessions (SSO, LMS, reseller auth, CDP bridges).
   - Inspect the profile before pruning: `du -sh <profile>/Default/*` shows which subfolders are large; only `Cache`, `Code Cache`, and top-level `component_crx_cache` are in the safe set above.
3. **Stale Upgrade Snapshots, Multi-Profile State Snapshots & Build Caches:**
   - Framework and profile pre-update state snapshots: In multi-agent fleets, each profile creates full database and config snapshots under `~/.hermes/profiles/*/state-snapshots/` (e.g. `20261016-...-pre-update`). Across a fleet of 10+ profiles, these silently consume 2.5GB+ of root partition space. Once the running framework version and active services are verified healthy, prune snapshot contents across all profiles while preserving directory structure:
     ```bash
     rm -rf /root/.hermes/profiles/*/state-snapshots/* /root/.hermes/state-snapshots/*
     ```
   - Package manager and tool caches: Hermes-managed tools and package managers store large download caches on root:
     ```bash
     # Hermes uv cache can consume >1GB alone; npm _npx caches add 300MB+
     rm -rf /root/.hermes/cache/uv ~/.cache/uv /root/.npm/_npx ~/.npm ~/.npx ~/.cache/pip
     pnpm store prune 2>/dev/null || true
     apt-get clean 2>/dev/null && rm -f /var/cache/apt/*.bin
     journalctl --vacuum-size=20M
     ```
   - Rotated agent logs & runaway streams: Remove numbered historical logs (`rm -f ~/.hermes/logs/*.log.[0-9]` and `rm -f ~/.hermes/logs/errors.log.[0-9]`) and truncate active runaway log streams in place (`truncate -s 0 ~/.hermes/logs/mcp-stderr.log`) without destroying open file descriptors held by running services.
4. **Dangling Container Images & Orphaned Worktrees:**
   - `docker image prune -f` reclaims unreferenced build layers without touching active containers.
   - Stale git worktrees (`git worktree remove <path>` or `git worktree prune`) reclaim working copy disk while preserving all branches and commits in the primary git object database.
5. **Oversized Container JSON Logs (`/var/lib/docker` or `<docker-data>/containers/*/*-json.log`):**
   - Find them with `find <docker-data>/containers -name '*-json.log' -size +20M`, map each to its container name with `docker inspect <id> --format '{{.Name}}'`.
   - Truncate in place (`truncate -s 0 <file>`), not delete: the container keeps running and its open file descriptor stays valid. Only the historical log lines are lost.
   - This is history loss, not regenerable cache. Run it only after per-target approval. Prevent regrowth with `log-opts` (`max-size`, `max-file`) in the container's compose file, which is a config change the owner must approve.
6. **Ephemeral `/tmp` Directory Clutter & Process Binding Verification:**
   Extracted repository archives, test deployment instances (e.g. unzipped web roots), and compiler scratch trees accumulate in `/tmp` and persist across reboots on cloud VPS.
   - *Verification before deletion:* Check whether any active daemon or subshell has its working directory inside the targeted `/tmp` path:
     ```bash
     ls -l /proc/*/cwd 2>/dev/null | grep -E "/tmp/(target1|target2)"
     ```
   - If unreferenced, safely purge the directories and their archive tarballs (`rm -rf /tmp/<dir> /tmp/<dir>.tar.gz`).

#### Tier 2: Ambiguous / Legacy Artifacts (Reversible Staged Recycling)
Never run irreversible `rm -rf` on deprecated tools, old project clones, or unknown virtual environments when executing an emergency disk cleanup:
1. **Staged Migration to Secondary Storage:** Move ambiguous directories to a timestamped folder on a secondary mount or non-root partition:
   ```bash
   mkdir -p /mnt/.recycle_$(date +%Y%m%d)
   mv /path/to/legacy-candidate /mnt/.recycle_$(date +%Y%m%d)/
   ```
2. **Immediate Health Check:** Immediately verify all systemd units and port listeners (`systemctl is-active`, `curl -s -I http://127.0.0.1:<port>`) to prove zero live services depended on the moved paths.
3. **Inventory Hand-off:** Present the moved inventory to the operator with sizes and paths, allowing them to permanently purge (`rm -rf`) or restore with zero data loss risk.
4. **Active Project & Mission Audit Evidence Offload (Compress-and-Verify Invariant):**
   When cleaning audit artifacts (e.g. `/root/fleet-evidence/*`), never delete evidence directories for projects or competitions currently within their active submission or operational window.
   - Instead of deleting, offload to secondary storage (`/mnt/.../archive/...tar.gz`).
   - *Integrity & Count Verification Invariant:* Before removing the source directory on the root partition, verify archive extraction readability (`tar tzf <archive>.tar.gz > /dev/null`) AND confirm the archive file count matches the source file count (`[ $(find <source> | wc -l) -le $(tar tzf <archive>.tar.gz | wc -l) ]`). Only delete source after validation passes.

### Process Termination Discipline (`pkill -f` Self-Termination Trap)
When terminating background watchers, test servers, or orphan processes from inside automation scripts or agent sessions:
- **The Mechanism:** `pkill -f "<pattern>"` inspects `/proc/<pid>/cmdline`. If the pattern matches the command line of the executing subshell or agent command, the operating system sends SIGTERM to the caller, abruptly terminating the active session.
- **The Rule:** Never run naked `pkill -f` on generic script names. Always filter out the calling process ID (`$$`), target recorded PIDs directly, or anchor to specific binary paths:
  ```bash
  # Safe pattern: exclude caller PID
  for pid in $(pgrep -f "target-script.py" 2>/dev/null); do
    [ "$pid" != "$$" ] && kill "$pid" 2>/dev/null
  done
  ```

### Diagnosing and Reaping Zombie Process Storms (`<defunct>`)
When `ps aux` reveals zombie processes (e.g. `[git] <defunct>`):
1. **Find Top Leaky Parent (PPID) & Zombie Count:**
   ```bash
   # Total zombie count
   ps -eo stat | awk '$1 ~ /Z/ {c++} END {print c+0}'

   # Rank parent PIDs spawning unreaped zombies
   ps -eo ppid,stat | awk '$2 ~ /Z/ {print $1}' | sort | uniq -c | sort -rn | head -5
   ```
2. **Two-Hop Container Tracing Trap:**
   When inspecting the parent (`ps -fp <PPID>`), the command often appears as a standard command (e.g. `python -m app.scheduler.jobs`) because container processes share the host kernel and are visible from the root PID namespace. The process itself is running inside a Docker container, not on bare metal.
   - **Trace container ownership via grandparent shim or cgroup:**
     ```bash
     # Inspect the parent's parent (grandparent)
     ps -fp $(ps -o ppid= -p <PPID>)
     # Grandparent CMD displays: /usr/bin/containerd-shim-runc-v2 -namespace moby -id <container_hash>

     # Or inspect the process cgroup directly:
     cat /proc/<PPID>/cgroup 2>/dev/null
     ```
   - Do NOT attempt to kill the parent process blindly from the host.
   - Map the container hash to its container name:
     ```bash
     docker ps --filter "id=<container_hash_first_12>" --format "{{.ID}} | {{.Names}}"
     ```
   - Restart the offending container:
     ```bash
     docker restart <container_name>
     ```
   Restarting the container destroys its isolated PID namespace and reaps all orphaned defunct processes instantly, restoring a clean host process table (`ps aux | grep -i defunct | grep -v grep | wc -l` drops to `0`).
3. **A restart clears the backlog, never the cause:** reaping is done by the parent (`subprocess`/`Popen().wait()`, `child.on('exit')`, `SIGCHLD` handler) inside the app. If that code never waits, the count climbs again within hours. Re-count on a later probe before calling the issue closed, and when it recurs, name the defect as an application-code fix in that repo (spawn path must `wait()`/reap) rather than reporting a repeat `docker restart` as remediation.

### Report-Only Storage Reviews (Default) & Protected Work Areas
When the operator asks to "check storage conditions" on a shared production host:
- Run READ-ONLY diagnostics only (`df`, `du`, `find -printf`, `docker system df`, `docker inspect`). Present findings with reclaimable estimates; execute zero deletions during a review. The operator may be actively using directories that look like garbage (live capture sessions, model workspaces, container runtime storage).
- Deletions require explicit, per-target operator approval in the same session. A general request to clean up ("bersih-bersih", "clean up the VPS") authorizes the audit only, not any deletion: present the candidate list with sizes and paths, then wait for approval before running any `rm`, `truncate`, `find -delete`, or prune. "Don't delete that" (or any similar nudge) is a hard stop for the entire cleanup class, not just the named item.
- After any approved cleanup, verify before reporting: listeners on known service ports (`ss -tlnp`, e.g. the AI gateway port), `docker ps` status for every container, and `df` for both partitions. State explicitly which live services were checked and confirmed untouched.
- Treat as protected unless told otherwise: `/mnt/8ballpool-mod` (live adb/logcat capture work), `/mnt/laya-test` (models), `/mnt/docker-data` + `/mnt/containerd` (live container runtime), in-flight project evidence (`/root/fleet-evidence/<active-project>`) during active competition/deployment periods, active project work dirs under `/mnt` and `/root/projects`.
- Shared hosts change underneath you mid-review (parallel automation, capture loops, cron). Re-run `df` right before reporting numbers so the report is current.

### Host Directory Placement Conventions & Ephemeral Scratch Hygiene
To prevent `/root` clutter and avoid emergency storage rescue operations:
1. **Root-Level Cleanliness Mandate (No Bare Writes):**
   - Never write loose output files (`*.jpg`, `*.webp`, `*.html`, `*.json`, `*.zip`, `*.md`) directly to the root home directory (`/root`).
   - Every write, scrape download, image transformation, or probe output must target an explicit subdirectory according to its lifecycle.
2. **Directory Taxonomy & Placement Standards:**
   - **Active Projects (`/root/projects/<name>/`):** Active repositories, long-term application code, and production services.
   - **Historical Archives (`/root/archive/`):** Inactive legacy code, obsolete clones, past review docs, and retired bundles.
   - **Operational Scripts & Tools (`/root/scripts/`, `/root/tools/`):** System maintenance, backup hooks, and custom binaries.
   - **Ephemeral Scratch (`/root/tmp/` or `$TMPDIR`):** One-off scraping dumps, temporary crops/resizes, ephemeral logs, and transient test payloads.
3. **Environment Variable Enforcement (`TMPDIR`):**
   - Export `TMPDIR=/root/tmp` in `/root/.bashrc` and daemon environment files so tools, standard library modules (e.g. Python `tempfile`), and headless browsers default to scratch storage rather than polluting the home directory.
   - Ensure the directory exists with proper permissions: `mkdir -p /root/tmp && chmod 700 /root/tmp`.
4. **Automated Scratch Pruning (Cron TTL Guard):**
   - Ephemeral directories will grow silently unless guarded by automated TTL pruning.
   - Maintain a daily cronjob that prunes unaccessed items older than 3 days:
     ```bash
     17 4 * * * find /root/tmp -mindepth 1 -depth -mtime +3 -delete >> /var/log/tmp-purge.log 2>&1
     ```
5. **Audited Cleanup Manifest & Non-Destructive Archival Protocol:**
   - When cleaning or reorganizing cluttered directories, record every deletion (`DEL`) and relocation (`MOVE`) in a timestamped audit manifest: `/root/archive/cleanup-manifest-<timestamp>.txt`.
   - Never delete ambiguous or non-trivial directories outright; move them into `/root/archive/` or a structured project subfolder.
   - Explicitly verify and preserve operator-protected assets (such as SSH key backups, specialized toolchain upgrades, or live configuration files).
6. **Root Item Count Metric as Clutter Alarm:**
   - Track total entries at root level: `ls -1A /root | wc -l`.
   - On a clean production server, root entries should remain bounded (typically 70–85 items including dotfiles). A sudden jump indicates an unconstrained script or background worker dumping files outside designated directories.

---

## 8. Host Telemetry & Network Benchmarking

### Standard System Resource Spec Format
When formatting live host telemetry for reporting or monitoring dashboards:
```text
- CPU: <cores> Core | Load: <1m>, <5m>, <15m>
- RAM: <used> MB / <total> MB (<pct>%) | Free: <free> MB
- Disk: <used> GB / <total> GB (<pct>%) | Free: <free> GB
```

One-line Python probe ensuring synchronized values matching `free -m` and `df -m`:
```python
python3 -c "
import os, subprocess

cores = os.cpu_count()
l1, l5, l15 = os.getloadavg()
mem = subprocess.check_output(['free', '-m']).decode().splitlines()[1].split()
ram_tot, ram_used = int(mem[1]), int(mem[2])
ram_free, ram_pct = ram_tot - ram_used, (ram_used / ram_tot) * 100

df = subprocess.check_output(['df', '-m', '/']).decode().splitlines()[1].split()
d_tot, d_used, d_avail = int(df[1]) / 1024, int(df[2]) / 1024, int(df[3]) / 1024
d_pct = (int(df[2]) / int(df[1])) * 100

print(f'- CPU: {cores} Core | Load: {l1:.2f}, {l5:.2f}, {l15:.2f}')
print(f'- RAM: {ram_used} MB / {ram_tot} MB ({ram_pct:.1f}%) | Free: {ram_free} MB')
print(f'- Disk: {d_used:.1f} GB / {d_tot:.1f} GB ({d_pct:.1f}%) | Free: {d_avail:.1f} GB')
"
```
*Note on separate mount points:* If secondary persistent storage exists (e.g. `/mnt`), report it as a distinct entry (`- Disk (/mnt): ...`) rather than conflating mount boundaries.

### Network Speed & Bandwidth Testing
1. **Ookla CLI vs Python `speedtest-cli` Flag Incompatibility Trap:**
   On Debian/Ubuntu hosts, `/usr/bin/speedtest` is frequently a symlink or wrapper for the Python `speedtest-cli` package rather than the official compiled Ookla binary.
   - Do NOT pass official Ookla flags (`--accept-license --accept-gdpr`) without verifying the binary first; `speedtest-cli` throws `unrecognized arguments: --accept-license --accept-gdpr`.
   - Run `speedtest --share` (or `speedtest-cli --share`): this tests latency, download, and upload, and generates a shareable result link image without interactive prompts or license flags.
