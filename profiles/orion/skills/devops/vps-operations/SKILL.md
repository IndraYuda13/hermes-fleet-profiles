---
name: vps-operations
description: Use when managing VPS security, git deploys, or AI apps.
version: 1.5.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [vps, ssh, fail2ban, git, deployment, reverse-proxy, security, fail-closed, devops, storage, maintenance]
---

# VPS Operations & Host Hardening Standard

Consolidated operational runbook for Linux VPS administration: automated attack triage, Fail2ban hardening, SSH key cutover, Git deployment hygiene, reverse-proxy ingress, fail-closed application architectures, and host storage/process hygiene.

## When to Use
- Diagnosing authentication brute-force attacks, high `rsyslogd` CPU spikes, or configuring Fail2ban on public cloud servers.
- Safely transitioning SSH authentication to exclusive Ed25519/RSA keys without administrator lockouts.
- Deploying, pulling, and rebuilding Git repositories on live production VPS serving environments.
- Troubleshooting multi-tier ingress routing (Cloudflare Tunnel -> Nginx -> application daemons) and fail-closed AI application backends.
- Performing emergency disk rescue, purging hidden browser/package caches, and reaping container-orphaned zombie process storms.

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

### Enrolling New Client Devices Post-Password Cutover (`ssh-copy-id` Trap)
Once password authentication is disabled (`PasswordAuthentication no`), standard `ssh-copy-id -i ~/.ssh/id_ed25519.pub user@host` fails immediately with `Permission denied (publickey)` because the remote host rejects the initial password prompt required by `ssh-copy-id`. Users and operators frequently confuse this failure with "the VPS port is closed / external access is blocked".

To safely enroll a new client machine (laptop, desktop, or mobile) into a password-locked VPS:
1. **Clarify Access vs Authentication:** Confirm that port 22 remains reachable and listening (`ss -tlnp | grep :22`); only password authentication is closed.
2. **Client-Side Key Generation:**
   On the new client machine (Linux/macOS terminal or Windows PowerShell/Git Bash):
   ```bash
   ssh-keygen -t ed25519 -C "new-device-label"
   cat ~/.ssh/id_ed25519.pub   # Windows: Get-Content ~\.ssh\id_ed25519.pub
   ```
3. **Enrollment Pathways:**
   - **In-Band Automation/Agent Relay (Recommended when an active agent/session exists):** Have the user paste the single-line public key (`ssh-ed25519 AAAAC3NzaC1lZDI1NTE5...`) into the active session. Append it directly on the host:
     ```bash
     echo "<public_key_string>" >> /home/<username>/.ssh/authorized_keys
     ```
   - **Bridge via Existing Authorized Device:** If the operator has another device already authorized (e.g. smartphone running Termux or previous workstation), SSH from that device and append the new key string to `.ssh/authorized_keys`.
   - **Encrypted Manager Key Sync:** If using SSH clients with cloud key synchronization (e.g. Termius), logging into the client account automatically synchronizes existing private keys without host-side reconfiguration.
4. **Dual Privilege-Tier Key Sync Invariant:**
   If both a non-root administrative account (`/home/<username>`) and `root` exist on the host, append the new public key to both locations:
   - `/home/<username>/.ssh/authorized_keys`
   - `/root/.ssh/authorized_keys` (when root key login is permitted via `PermitRootLogin without-password` or `prohibit-password`).
   This prevents administrative lockouts during privilege-specific tasks or emergency recoveries.

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
- **Database Migrations on Pull:** Upstream commits often introduce new SQL migrations (e.g. `supabase/migrations/<timestamp>_<name>.sql` for schema changes or board resets). When local Postgres/Supabase services are active, check if new migration files exist in the pulled commits (`git diff HEAD origin/<branch> -- supabase/migrations/`). Execute the project's migration/preparation runner (e.g. `node scripts/test-db.mjs prepare` or `npm run db:migrate`) BEFORE compiling Next.js. Next.js static generation (`next build`) runs database queries at build time; missing tables or columns from unapplied migrations will cause static page generation to crash during build.
- **Build Script Tracked-Artifact Pollution:** Compiling production builds often triggers pre-build or bundle generation scripts (e.g. `prepare-assets`, OMR worker generation, QA artifact bundlers) that mutate tracked test fixtures or manifests (e.g. `artifacts/qa/**/bundle.json`). Immediately inspect `git status` after building and revert unintentional modifications to tracked repository artifacts (`git checkout <file>`) to prevent dirty-tree blocking on future `git pull` or `git stash` operations.
- **Next.js Standalone Build Asset Sync (`output: 'standalone'`):** When deploying a Next.js application configured for standalone output on a VPS systemd service, `npm run build` only places minimal runtime files into `.next/standalone/`. It does not automatically copy `.next/static/` or `public/` into `.next/standalone/`. If the systemd unit runs `node .next/standalone/server.js`, client CSS, fonts, and JS chunks will 404 unless `.next/static` is synced to `.next/standalone/.next/static` and `public` is copied to `.next/standalone/public`. Verify this copy step in the build script or deployment pipeline before reloading systemd.
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

### Fail-Closed AI Architectural Guardrails
1. **Configuration-Gated AI Fallbacks:** Gate AI features on system-wide provider configuration readiness (`cfg.enabled && cfg.provider.profile`) rather than hardcoding user-ID blocks (`teacher.id === SAMPLE_TEACHER_ID`), allowing demo accounts to exercise interactive flows when explicitly enabled without code changes.
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

### High-Yield Disk Rescue Targets
When `/` partition usage spikes near 100% (e.g. <1 GB free):
1. **Chrome BrowserMetrics Dump Accumulation (`.pma` files):**
   Headless Chrome/Chromium runs write metrics dumps to `~/.config/google-chrome/BrowserMetrics/` or profile directories. These unpruned diagnostic `.pma` files can quietly consume 5–10+ GB of root storage.
   ```bash
   # Inspect and purge metrics dumps
   du -sh ~/.config/google-chrome/BrowserMetrics/ 2>/dev/null
   rm -rf ~/.config/google-chrome/BrowserMetrics/*.pma
   ```
2. **Headless Browser Scratch Profiles & CRX Caches:**
   Automation tools (Playwright, Puppeteer, browser sessions) generate temporary profile directories in `/tmp` and cache extension files:
   ```bash
   # Clean orphaned headless profiles in /tmp
   rm -rf /tmp/playwright* /tmp/.org.chromium.* /tmp/chromium*
   # Clean extension installer caches across profiles
   find ~/.hermes/profiles -name "component_crx_cache" -type d -exec rm -rf {} + 2>/dev/null || true
   ```
3. **Package Manager & Compile Caches:**
   Safe pruning of package download caches that do not affect runtime dependencies:
   ```bash
   rm -rf ~/.cache/uv ~/.npm ~/.npx ~/.cache/pip
   pnpm store prune 2>/dev/null || true
   journalctl --vacuum-time=3d
   ```

### Diagnosing and Reaping Zombie Process Storms (`<defunct>`)
When `ps aux` reveals hundreds or thousands of zombie processes (e.g. `[git] <defunct>`):
1. **Identify the Defunct Parent (PPID):**
   ```bash
   # Find PPID of the first few defunct processes
   ps -eo pid,ppid,stat,cmd | grep ' Z' | head -n 5
   # Inspect the parent process
   ps -fp <PPID>
   ```
2. **Container Namespace Isolation Trap:**
   If the parent process is a script inside a Docker container (e.g. a Python scheduler spawning subcommands like `git` or `curl` without calling `wait()` / `waitpid()`), its PPID on the host points to `containerd-shim-runc-v2 -id <container_hash>`.
   - Do NOT kill host processes blindly or reboot the VPS host.
   - Map the container hash to the container name:
     ```bash
     docker ps --filter "id=<container_hash_first_12>" --format "{{.ID}} | {{.Names}}"
     ```
   - Restart the offending container:
     ```bash
     docker restart <container_name>
     ```
   Restarting the container destroys its isolated PID namespace and reaps all thousands of orphaned defunct processes instantly, restoring a clean host process table (`ps aux | grep -i defunct | grep -v grep | wc -l` drops to `0`).
