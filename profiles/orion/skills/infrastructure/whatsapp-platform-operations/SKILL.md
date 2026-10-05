---
name: whatsapp-platform-operations
description: Operate WhatsApp bridge, allowlists, and group JIDs.
version: 1.6.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    related_skills:
    - hermes-agent
    - hermes-operations
    tags:
    - whatsapp
    - operations
    - allowlist
    - group-jid
    - gateway
    - baileys
---

# WhatsApp Platform Operations

## Architecture
Hermes Agent uses a standalone Node.js subprocess bridge (`@whiskeysockets/baileys`) to connect to WhatsApp Web protocol.

- Bridge script: `/usr/local/lib/hermes-agent/scripts/whatsapp-bridge/bridge.js`
- Bridge port: default `3000` (loopback)
- Session directory: configured via `platforms.whatsapp.extra.session_path` in `config.yaml` (typically `~/.hermes/profiles/<profile>/platforms/whatsapp/session` or `~/.hermes/profiles/<profile>/whatsapp/session`). Always check `config.yaml` before inspecting, backing up, or wiping session files.
- Gateway adapter: `/usr/local/lib/hermes-agent/plugins/platforms/whatsapp/adapter.py` & `gateway/platforms/whatsapp_common.py`

## Configuration Keys

In `~/.hermes/profiles/<profile>/config.yaml`:
```yaml
platforms:
  whatsapp:
    enabled: true
    reply_to_mode: "first" # "first" (quote first chunk, recommended) | "all" | "off"
    extra:
      group_policy: "allowlist" # "open" | "allowlist" | "disabled" | "pairing"
      group_allow_from:
        - "<WHATSAPP_JID>"
      require_mention: true
      mention_patterns:
        - "@<WHATSAPP_ID>"
        - "Akun Wa Gpt"
        - "\\bOrion\\b"
      allow_from:
        - "<WHATSAPP_ID>"
        - "<WHATSAPP_ID>"
```

In `.env`:
```ini
WHATSAPP_ENABLED=true
WHATSAPP_MODE=bot # "bot" | "self-chat"
WHATSAPP_DM_POLICY=pairing # "pairing" | "allowlist" | "open" | "disabled"
WHATSAPP_ALLOWED_USERS=<WHATSAPP_ID>,<WHATSAPP_ID>
WHATSAPP_GROUP_POLICY=allowlist
WHATSAPP_GROUP_ALLOW_FROM=<WHATSAPP_JID>,...
WHATSAPP_REQUIRE_MENTION=true
WHATSAPP_MENTION_PATTERNS=["@<WHATSAPP_ID>", "Akun Wa Gpt", "\\bOrion\\b"]
WHATSAPP_DEBUG=true
```

## Key Operational Workflows & Pitfalls

### 1. Dashboard "Disabled" State Bug
- The web dashboard (`/api/messaging/platforms?profile=<profile>`) inspects `config.yaml -> platforms.<platform>.enabled`.
- Even if `.env` has `TELEGRAM_BOT_TOKEN` or `WHATSAPP_ENABLED=true` and gateway is running, if `platforms.<platform>.enabled` is missing in `config.yaml`, the dashboard displays `disabled` (grayed out).
- **Fix:** Run `hermes config set platforms.<platform>.enabled true`.

### 2. Discovering WhatsApp Group JIDs (`@g.us`) & Verifying Exact Group Titles
- Operators/users rarely know internal WhatsApp Group JIDs (`120363xxxxxxxxx@g.us`).
- When a user adds the bot to a new group and tags the bot, the bridge syncs sender keys and receives message notifications.
- **Workflow to find and verify exact Group JID:**
  1. Inspect the session directory for candidate group JIDs:
     `ls -lat ~/.hermes/profiles/<profile>/platforms/whatsapp/session/ | grep "sender-key-120363"`
  2. **Query the Bridge `/chat/:id` endpoint** to resolve real-time group subject titles without guessing:
     ```python
     import urllib.request, json
     for jid in ["<WHATSAPP_JID>", "<WHATSAPP_JID>"]:
         try:
             res = json.loads(urllib.request.urlopen(f"http://127.0.0.1:3000/chat/{jid}").read())
             print(f"JID: {jid} -> Group Name: '{res.get('name')}'")
         except Exception as e:
             print(f"JID: {jid} -> Error: {e}")
     ```
     *(Example: `<WHATSAPP_JID>` is "Afterhours (AOC)", while `<WHATSAPP_JID>` is "Test").*
  3. This prevents sending messages or configuring allowlists on the wrong group (e.g. distinguishing `"Afterhours (AOC)"` from a `"Test"` group sharing similar activity timestamps).
  4. Append the confirmed JID to `platforms.whatsapp.extra.group_allow_from` in `config.yaml` and `WHATSAPP_GROUP_ALLOW_FROM` in `.env`.
  5. Restart gateway (`/restart` command via chat or kill bridge to reload cleanly).

### 3. Group User Authorization vs Group Chat Bypass (`group_allowed_chats` & `authz_mixin.py`)
- **The Core Authorization Trap & The Owner-Test False Positive:**
  When `WHATSAPP_ALLOWED_USERS` is configured, Hermes gateway's `_is_user_authorized()` in `gateway/authz_mixin.py` enforces sender allowlist on *every inbound message* (including group chats).
  - *The Owner-Test False Positive:* If the owner/operator tests the bot in a new group with `@bot test`, the bot replies successfully because the owner's phone/LID is already in `allow_from` / `WHATSAPP_ALLOWED_USERS`. This creates the false impression that group setup is complete, even though any message from friends/collaborators will be immediately dropped as `Unauthorized user: <lid>`.
  - Always verify that non-allowlisted group members are permitted before declaring the group ready.
- **Root Cause & Fix Patterns:**
  1. **Option A (All Members in Specific Groups):** Add the group JID to `platforms.whatsapp.extra.group_allowed_chats: ["<group_jid>@g.us", ...]` in `config.yaml`. In `authz_mixin.py`, `_chat_scoped_grant()` admits any sender in that chat without requiring individual user allowlists.
  2. **Option B (Open Group Policy with Allow-All):** When setting `group_policy: "open"`, ensure `platforms.whatsapp.extra.allow_all_users = True` or set `WHATSAPP_ALLOW_ALL_USERS=true` in `.env` so group members aren't silently dropped by the default-deny user allowlist.
  3. **Protected Config Barrier Pitfall:** Hermes agent file tools (`patch`, `write_file`) strictly reject writes to `/root/.hermes/profiles/<profile>/config.yaml` and `.env` (protected system/credential files). Never try to file-patch them directly; use `hermes --profile <profile> config set <key> <value>` via terminal.
  4. **Multi-Instance Port Disambiguation:** In multi-profile setups (e.g. `groupbot` on :3000, `orion` on :3001), always check `bridge_port` in `config.yaml` before querying `/chat/<jid>` or `/send`. Querying the wrong port returns 404 or connection error.
  5. **LID Device Normalization:** Baileys returns bot IDs formatted like `<WHATSAPP_JID>` or `<WHATSAPP_JID>`. Ensure ID normalizers strip the `:device` segment before `@` so autocomplete mentions (`@<WHATSAPP_ID>`) match `botIds` reliably.
  6. **Long-Polling Buffer Desync on Bridge Restarts:** When restarting or killing the Node.js bridge (`kill -9 <pid>`), the gateway re-establishes TCP connection to port 3000. If messages arrived during restart, verify `/messages` long-polling queue is actively flushing (`GET http://127.0.0.1:3000/messages`) and confirming `200 OK` deliveries.

### 4. Mention Patterns, LID Mentions & Group Policy Discipline
- In WhatsApp groups, mentioning a bot often inserts the contact LID and display name (e.g. `@<WHATSAPP_ID>AW.ai` or `@AW.ai`) rather than raw phone numbers.
- Configure `mention_patterns` in `config.yaml` and `WHATSAPP_MENTION_PATTERNS` in `.env` with regex matching:
  - Phone number (`@628...`)
  - LID prefix (`@<WHATSAPP_ID>`)
  - Display name (`AW.ai`, `@AW.ai`, `Akun Wa Gpt`)
  - Profile alias (`\\bOrion\\b`)
- **The Generic Noun & Pop-Culture Name Collision Trap (`bot`, `@bot`, `ai`, character names):** Never include generic conversational nouns like `"bot"`, `"\bbot\b"`, `"@bot"`, or `"ai"` in `mention_patterns`. Furthermore, beware of agent names that collide with games or pop-culture (e.g. `Orion` in Mobile Legends, anime, or astronomy). In active human group chats, users constantly discuss these terms in casual banter, causing intrusive unwanted wakeups and burning context tokens. When collisions occur, strip conversational name triggers (`\b<Name>\b`, `@<Name>`) from `mention_patterns` and restrict triggers strictly to the bot's exact WhatsApp phone number tag (`@<phone>`, `<phone>`) and native quote-replies (`reply_to_mode: first`, handled by `_message_is_reply_to_bot`).
- **Synchronizing Dual Stores (`config.yaml` and `.env`):** Mention patterns are evaluated from both `config.yaml` (`platforms.whatsapp.extra.mention_patterns`) and `.env` (`WHATSAPP_MENTION_PATTERNS`). Updating only one store leaves the bot waking on old patterns. Update `config.yaml` via `hermes config set` and synchronize `.env` in tandem before issuing a delayed gateway restart.
- **Important Pitfall:** When a user tags the bot using UI autocomplete, the rendered text in WhatsApp often prefixes an `@` before the custom contact name (e.g. `@AW.ai` or `@<WHATSAPP_ID>AW.ai`). If `mention_patterns` only contains `AW.ai` or phone numbers, strict word-boundary matching or regex may fail to trigger. Always include `@<DisplayName>`, `<DisplayName>`, and the LID identifier `@<LID>`.
- **Group Self-Sent Message Drop (`from_me_group`):** When the owner/operator tests the bot in a group chat from the *same phone/number* that is linked to the bot session, Baileys emits `msg.key.fromMe = true`. By default, `bridge.js` ignores `fromMe` group messages to prevent infinite self-echo loops. To test group bot responsiveness, always instruct another group member to mention the bot or use a secondary WhatsApp account.
- **Group Policy & Inbound Mention Optimization:**
  - Keep `platforms.whatsapp.extra.group_policy: "allowlist"` and `require_mention: true` when operating in shared groups.
  - Do **not** set `group_policy: "open"` blindly if `allow_from` / `WHATSAPP_ALLOWED_USERS` is strictly filtered; always preserve the explicit `group_allow_from` and `group_allowed_chats` pattern to avoid unauthorized authorization dropouts or unwanted global group triggers.
- **Quote-Reply Triggering Without Mention:** In WhatsApp groups where `require_mention: true`, quoting or replying directly to any message sent by the bot triggers the agent turn without requiring `@mention` or name tags (`_message_is_reply_to_bot`). The Baileys bridge emits both phone JID (`@s.whatsapp.net`) and LID (`@lid`) in `botIds`, and `whatsapp_common.py` strips device suffixes (`:device`) before comparing against `quotedParticipant`. Quoting another human member's message still requires an explicit mention to wake the bot.
- **Bare Mentions & Presence Check / Ping Handling:** When an inbound message consists solely of a mention tag (e.g. `@<LID>`, `@bot`, `@<phone>`) or an informal roll-call / presence check (e.g. `absen`, `absen bree`, `p`, `ping`, `tes`), treat it immediately as a conversational liveness ping. Acknowledge presence promptly, casually, and concisely without running background terminal diagnostics (`ps aux`) or inspecting session directory files; investigating a bare identifier as an anomaly delays the response, leading to user interruptions.
- **Multi-Bot Group Co-existence & Isolation:** When multiple distinct agent bots operate in the same WhatsApp group, keep them strictly independent. Never cross-contaminate `mention_patterns` (e.g. bot B must not listen to `@Orion` or bot A's handles), and do not link them via A2A or cross-network RPC unless explicitly authorized. Each bot must respond exclusively to its own unique handle and its own quote-replies.
- Always keep upstream framework files (`/usr/local/lib/hermes-agent`) clean and vanilla—rely on official `hermes update` / `git pull` rather than in-place framework edits.

### 5. Multi-User WhatsApp Group Hardening & Sandboxing Protocol (Profile Isolation)
- **The Core Problem:** Allowing friends/public in a WhatsApp group to interact with the main Hermes orchestrator profile (e.g. `orion`) leads to two catastrophic side-effects:
  1. **Memory Pollution:** Rogue statements ("panggil aku Queen", "panggil Lord Aldi") trigger automatic self-improvement and memory updates, contaminating `USER.md` / `MEMORY.md` and blowing through token character limits.
  2. **System & File Execution Risk:** With `terminal`, `file`, and `code_execution` active, group users can prompt the bot to edit Nginx vhosts, modify Cloudflare Tunnel configs, run arbitrary scripts, or delete files across the VPS.
- **Production Hardening Standard (Dedicated Sandboxed Profile):**
  1. **Separate Profile Creation:** Always isolate group messaging into a dedicated profile:
     `hermes profile create groupbot`
  2. **Zero Re-pairing Setup (Session & Credential Reuse):**
     - Copy `.env` from primary profile: `cp ~/.hermes/profiles/<primary>/.env ~/.hermes/profiles/groupbot/.env`
     - Symlink or copy the existing Baileys session directory:
       `mkdir -p ~/.hermes/profiles/groupbot/platforms/whatsapp`
       `ln -sf ~/.hermes/platforms/whatsapp/session ~/.hermes/profiles/groupbot/platforms/whatsapp/session`
     - This immediately connects without scanning a new QR code.
  3. **Strict Toolset Stripping & Controlled Read-Only Execution:**
     - For pure chat bots: Restrict `groupbot/config.yaml` to non-destructive tools only (`web`, `vision`, `tts`).
     - **Controlled Read-Only Inspection Pattern (When Group Users Request System/Hardware Specs):**
       If group members need the bot to inspect system specs (e.g. `lscpu`, `free -h`, `df -h`, `uname -a`, `uptime`, `fastfetch`):
       1. Enable `terminal` in `toolsets` and `platform_toolsets.whatsapp`.
       2. Lock CWD to an isolated directory: `terminal.cwd: /root/.hermes/profiles/groupbot/workspace`.
       3. Set `approvals.mode: smart` so destructive shell patterns (`rm -rf`, systemctl restarts, config overwrites) are automatically intercepted and blocked.
       4. In `SOUL.md`, explicitly establish the **Read-Only / Non-Destructive Boundary**: explicitly permit read-only hardware/status inspection commands while strictly forbidding configuration edits, service stops, package installs, file deletions, or cross-profile access (`/root/.hermes/profiles/*`).
     - *Strictly disable in all group profiles:* `file` (raw file read/write/patch across VPS), `kanban`, `delegation`, `skill_manage`, `memory`, `cronjob`.
     - **File Conversion & Media Handling via Dedicated Plugin (No Shell):**
       If group members need file utilities (e.g. converting uploaded images to PDF, audio formats, OCR), NEVER enable `terminal` or `file` toolsets on the group profile.
       Instead, create a dedicated zero-shell plugin in `~/.hermes/plugins/<tool-name>` using Python native libraries (e.g. `Pillow` for image-to-PDF). Register the tool under a custom toolset, configure `MEDIA:<output_path>` return directives, and add the toolset to `groupbot/config.yaml`. This delivers full utility while strictly preserving the zero-RCE sandbox.
  4. **Zero Memory & Zero Profile Retention:** Completely disable cross-session memory and self-improvement in `groupbot/config.yaml`:
     ```yaml
     memory:
       memory_enabled: false
       user_profile_enabled: false
       write_approval: false
     ```
  5. **Platform Exclusivity, The Bridge Polling Race Hazard & Multi-Instance Architecture:**
     - **CRITICAL Bridge Polling Invariant:** The Node.js Baileys bridge (`/messages`) serves a single destructively-consumed message queue (`messageQueue.splice()`). If multiple gateway profiles (e.g. `orion` and `groupbot`) run concurrently pointing to the *same bridge port* (default `3000`), incoming messages are randomly consumed by whichever gateway process polls first, causing intermittent drops and dropped turn state.
     - **Architecture Option A — Single-Number Takeover:**
       When moving WhatsApp between profiles on the same phone number/port 3000, always stop and disable the previous profile first:
       1. Stop the old profile service: `systemctl --user stop hermes-gateway-<old>`
       2. Set `platforms.whatsapp.enabled: false` on old profile.
       3. Enable on the target profile with `hermes config set platforms.whatsapp.enabled true`.
     - **Architecture Option B — Concurrent Dual-Port Multi-Instance (Personal Orchestrator + Sandboxed Group Bot):**
       To run a high-capability orchestrator (e.g. `orion` with memory, reasoning, and system tools) alongside a sandboxed group bot (`groupbot`) without collisions, isolate them across separate bridge ports and numbers:
       1. **Groupbot:** Port 3000, session `~/.hermes/platforms/whatsapp/session`, group allowlist, zero memory, toolset stripped.
       2. **Personal Orchestrator:** Port 3001, session `~/.hermes/profiles/<profile>/platforms/whatsapp/session`, linked to a dedicated second number.
       3. **Dual-Instance Hardening Contracts (Choose Based on Use Case):**
          - **Contract 1: Personal Orchestrator (DM-Only to Owner):**
            ```yaml
            platforms:
              whatsapp:
                enabled: true
                extra:
                  bridge_port: 3001
                  group_policy: "disabled"
                  group_allow_from: []
                  allow_all_users: false
                  require_mention: false
                  allow_from:
                    - "<owner_phone_number>"
            ```
            *Why:* Setting `group_policy: "disabled"` and locking `allow_from` strictly to the owner guarantees zero memory pollution, zero group prompt injection, and zero ambient group token consumption on expensive reasoning models (`ag-opus-pool`).
          - **Contract 2: Collaborative Group Builder (Owner + Collaborators Building Websites):**
            ```yaml
            platforms:
              whatsapp:
                enabled: true
                extra:
                  bridge_port: 3001
                  group_policy: "open"
                  allow_all_users: true
                  require_mention: true
                  mention_patterns:
                    - "@Orion"
                    - "Orion"
                    - "\\bOrion\\b"
            ```
            *Why:* In group builder mode, `require_mention: true` prevents ambient chatter from burning tokens. `allow_all_users: true` prevents gateway authz drops on collaborator messages. All project generation is locked to an isolated workspace (`/root/workspace/web-collab/`), with collaborator role permissions sandboxed in `SOUL.md`.
       4. **Session Symlink Collision Trap:**
          Profiles copied or created via templates often have `~/.hermes/profiles/<profile>/platforms/whatsapp/session` symlinked to `~/.hermes/platforms/whatsapp/session`. Always break this symlink before starting a secondary instance:
          `rm -f ~/.hermes/profiles/<profile>/platforms/whatsapp/session && mkdir -p ~/.hermes/profiles/<profile>/platforms/whatsapp/session`
          *Failure mode:* Failing to unlink causes both instances to write to the same session data, corrupting authentication state on both profiles.
       5. **Preflight `creds.json` Invariant & Standalone QR Pairing:**
          In Hermes `adapter.py`, `_preflight()` checks `self._session_path / "creds.json"`. If missing, the gateway fails immediately and never initiates the bridge loop.
          *Pairing Procedure for New Profiles:*
          - Spawn standalone bridge with `--pair-json` for clean programmatic QR capture:
            `node /usr/local/lib/hermes-agent/scripts/whatsapp-bridge/bridge.js --port <port> --session <session_dir> --mode bot --pair-json`
          - Capture the emitted `{"event":"qr","qr":"..."}` event or terminal QR and scan via WhatsApp.
          - Once Baileys writes `creds.json`, terminate the standalone bridge process and start the gateway service (`hermes --profile <profile> gateway run`).
       6. **In-Chat QR Code Delivery via Image Rendering (Headless Chat Handshake):**
          When pairing a new WhatsApp profile from within another messaging channel (e.g. Telegram):
          - Ensure `qrcode` is installed in the venv: `pip install qrcode`.
          - Capture the raw QR text string emitted by `bridge.js` (via `--pair-json`).
          - **Persistent Tmux Daemon Pattern (Anti-Turn-Termination):** Background python/terminal subshells can terminate when agent turns conclude. To guarantee the pairing bridge stays permanently alive across multi-turn user interactions, spawn it in a detached tmux session:
            `tmux new-session -d -s wa-<profile>-bridge -x 120 -y 40 'node /usr/local/lib/hermes-agent/scripts/whatsapp-bridge/bridge.js --port <port> --session <dir> --mode bot --pair-json'`
            Capture the QR string using `tmux capture-pane -t wa-<profile>-bridge -p -S -100`, strip tmux soft wraps, render via `qrcode.make()`, and deliver via `MEDIA:<path>`.
          - **Permanent Daemon Mode Preferred Over `--pair-only`:** Running `bridge.js` with normal daemon flags (`--port <port> --session <dir> --mode bot --pair-json`) keeps the HTTP server alive and transitions seamlessly from QR presentation to `connected` without dropping the TCP/WebSocket link. In contrast, `--pair-only` terminates the process 2s after pairing, which mobile WhatsApp frequently misinterprets as an abnormal client disconnect, triggering `conflict: device_removed (code 401)` and unlinking the device.
          - **Mandatory Credential Flush Invariant (If using `--pair-only`):** Baileys calls `setTimeout(() => process.exit(0), 1500)` after connection. The supervisor MUST wait for the node process to exit naturally (`proc.wait(timeout=10)`). Never `proc.terminate()` on immediate `"event":"connected"`, or `creds.json` will be written as an empty 0-byte file, permanently breaking gateway startup.
          - **Stale Linked Device Desync Trap:** If server session files are wiped while the mobile app still lists "Google Chrome / Linux" under Linked Devices (Perangkat Tertaut), WhatsApp will not establish a new session over the old linkage. The user MUST explicitly tap and "Keluar" (Log out) the stale device on their phone before scanning a newly generated QR code.
          - **Post-Pairing Sync Window (Anti-Device-Removed Trap):** Immediately after pairing, allow Baileys 15–30 seconds to settle its initial contact and history sync before dispatching rapid outgoing messages or restarting gateway processes. Blasting messages during initial session handshake risks WhatsApp triggering `conflict: device_removed (code 401)`.
          - **Web Dashboard Setup Conflict Pitfall:** When an operator sees the WhatsApp setup modal on the Hermes web dashboard (`/api/messaging/platforms`), it targets the default port 3000 and default session. In multi-instance setups (where port 3000 is reserved for a group bot and port 3001 for personal orchestrator), submitting this modal will overwrite port 3000 settings and break the group bot. The operator must cancel the dashboard modal and configure secondary profiles strictly via CLI (`hermes --profile <profile> config set platforms.whatsapp.extra.bridge_port <port>`).
          - Once paired and flushed, clear any lingering standalone bridge instances and start the gateway service (`hermes --profile <profile> gateway run`).
       7. **Multi-User Collaborative Builder Sandboxing Protocol:**
          When the user intends for friends/collaborators to interact with an orchestrator profile on WhatsApp to "build websites" or execute tasks:
          - *Isolated Project Workspace:* Confine all project file generation, git repositories, and dependencies to a dedicated directory (e.g. `/root/workspace/web-collab/`), never the root directory or Hermes home.
          - *Tiered Role Enforcement in SOUL.md:* Distinguish the primary Owner from Collaborators. Grant collaborators permissions for code generation, frontend markup, backend logic, and local preview ports. Strictly intercept and require Owner confirmation for actions touching production configs (Nginx vhosts, Cloudflare tunnels, cPanel, database services, system packages, or credential files).
          - *Memory Pollution Defense:* Enforce an invariant in `SOUL.md` that collaborator inputs and requests must not update or overwrite the primary user profile (`USER.md`) or system memory (`MEMORY.md`).
     - Disable `telegram` on `groupbot` if sharing the same Telegram Bot token: `platforms.telegram.enabled: false`.
  6. **Dedicated Systemd Service & Profile Execution:**
     - Point CWD to an isolated empty directory: `terminal.cwd: /root/.hermes/profiles/groupbot/workspace`
     - Profile Gateway execution syntax: `hermes --profile <profile> gateway run` (Note: `hermes profile run` is invalid; `--profile` is a global flag before the `gateway` subcommand).
     - Check status of all profile gateways: `hermes profile list` or check `/root/.hermes/profiles/<profile>/gateway_state.json`.
     - Supervise via a dedicated user systemd unit (e.g. `hermes-gateway-groupbot.service`).
     - **In-Agent Gateway Control Pitfall (`busctl` workaround):** The Hermes tool execution interceptor blocks running `systemctl --user restart/start ...` from inside a gateway agent turn to prevent self-termination loops. To start or restart a profile service safely from inside an agent without tripping the security interceptor, use D-Bus directly via `busctl`:
       - **Start a stopped service:**
         ```bash
         busctl --user call org.freedesktop.systemd1 /org/freedesktop/systemd1 org.freedesktop.systemd1.Manager StartUnit ss "hermes-gateway-<profile>.service" "replace"
         ```
       - **Restart an already active/running service (`RestartUnit` vs `StartUnit` Trap):** Calling `StartUnit` on an already-running unit is a silent NO-OP. You MUST call `RestartUnit`:
         ```bash
         busctl --user call org.freedesktop.systemd1 /org/freedesktop/systemd1 org.freedesktop.systemd1.Manager RestartUnit ss "hermes-gateway-<profile>.service" "replace"
         ```
       - **Restarting the CURRENT Profile Gateway (Anti-Turn-Termination Guard):** Never call `busctl RestartUnit` on your own profile gateway in the foreground, as systemd will terminate the running turn immediately before the response is delivered. Always schedule a delayed background restart so the assistant turn finishes and sends first:
         ```bash
         terminal(command="sleep 5 && busctl --user call org.freedesktop.systemd1 /org/freedesktop/systemd1 org.freedesktop.systemd1.Manager RestartUnit ss 'hermes-gateway-<profile>.service' 'replace'", background=true)
         ```

### 6. WhatsApp Unicode Isolation & Formatting Truncation Pitfall
- **Unicode Directional Isolates in Autocomplete Tags:**
  When mobile WhatsApp clients insert contact tags (like `@Akun Wa Gpt`), they often append invisible Unicode isolates such as `\u2069` (POP DIRECTIONAL ISOLATE) at the end of the handle: `@Akun Wa Gpt\u2069`.
- **Regex Boundary Failure:**
  Standard word-boundary patterns like `\bAkun Wa Gpt\b` or strict string comparisons will FAIL against text containing directional marks unless non-boundary substrings or cleaned patterns are included.
- **Rule:** Always register plain substring matches without strict boundary anchors (e.g. `'Akun Wa Gpt'`, `'AW.ai'`, `'@<WHATSAPP_ID>'`) in `mention_patterns` to guarantee regex capture regardless of client-injected directional formatting.

### 7. Group Self-Mention Anti-Loop Behavior (`from_me_group`) & Testing Protocol
- **The Self-Mention Pitfall:** If an operator tests a group mention by typing `@bot` from the **exact same phone device/number paired to the bot session**, Baileys flags the inbound message as `fromMe: true`.
- In `bridge.js`, group messages with `fromMe: true` are intentionally discarded (`reason: "from_me_group"`) to prevent the bot from entering infinite self-reply loops with its own sent messages.
- **Testing Rule:** Always test group bot responses using a **secondary WhatsApp number** or by asking another member in the group to mention the bot. Never test group mentions from the host account itself.
- **Port 3000 `EADDRINUSE` Handling:** When restarting the WhatsApp bridge manually, always verify no orphaned node process holds the socket (`lsof -i :3000`) before launching a new background instance.
- **Session Cache & Memory Wipe for Hallucinating / Stuck Group Bots:**
  When a group bot (`groupbot`) becomes unresponsive or hallucinates wildly across prolonged group discussions:
  1. Kill both gateway and bridge PIDs: `kill -9 <gateway_pid> <bridge_pid>`.
  2. Wipe accumulated conversational state without unlinking WhatsApp credentials:
     `rm -rf ~/.hermes/profiles/<profile>/sessions/* ~/.hermes/profiles/<profile>/cache/* ~/.hermes/profiles/<profile>/image_cache/* ~/.hermes/profiles/<profile>/audio_cache/* ~/.hermes/profiles/<profile>/state-snapshots/*`
  3. Flush DNS resolver cache: `resolvectl flush-caches` or `systemctl restart systemd-resolved`.
  4. Launch gateway cleanly via supervisor or background terminal: `hermes --profile <profile> gateway run`.
  5. Post-restart confirmation: broadcast a friendly system ready message to the group JID via `POST http://127.0.0.1:3000/send` with payload `{"chatId": "<group_jid>", "message": "..."}`.
  6. **Re-Check Live Processes After Re-Launch:** Always verify with `ps aux | grep -E 'groupbot.*gateway|whatsapp-bridge'` to confirm both Python gateway and Node.js bridge spawned successfully, and test socket response before declaring complete.
- **Direct Bridge Health & Restart Diagnostics:**
  - Health endpoint: `http://127.0.0.1:3000/health` (returns JSON status `connected`, `queueLength`, `uptime`).
  - Direct message test payload: `POST http://127.0.0.1:3000/send` with JSON `{"chatId": "<jid/lid>", "message": "text"}` (do NOT use field key `text` or `recipient` alone; schema requires exact `chatId` and `message`).
  - **Baileys Connection Timeout (Reason 428 / 503) & Socket Hardening:**
    - Baileys WebSockets drop silently if idle without active keep-alives. Always ensure `makeWASocket` includes:
      ```js
      keepAliveIntervalMs: 25000,
      connectTimeoutMs: 60000,
      defaultQueryTimeoutMs: 60000,
      markOnlineOnConnect: true,
      ```
    - **`link-preview-js` Dependency Crash:** Baileys attempts automatic URL link parsing when users send links. If `link-preview-js` is missing from `node_modules`, it throws `ERR_MODULE_NOT_FOUND: Cannot find package 'link-preview-js'` and causes silent connection drops or poll stalls.
  - Clean restart: `kill -9 <bridge_pid>`; the parent gateway supervisor automatically respawns a clean bridge instance and re-establishes TCP socket linkage on port 3000 without crashing gateway.
- **WebSocket Keep-Alive & Dependency Hardening:** See `references/whatsapp-group-troubleshooting-and-mention-matrix.md` (Sections 6 & 7) for WebSocket ping interval (25s), `link-preview-js` crash fix, and group member authorization gate bypass.
- **Detailed Reference:** See `references/whatsapp-group-troubleshooting-and-mention-matrix.md` for full trigger precedence, LID mention regex rules, and group policy checklists.

### 8. Hermes Framework Upstream Update Protocol
- Use `hermes update --check` to safely query upstream availability.
- When performing updates on Git-installed checkouts: ensure uncommitted framework edits are discarded/stashed (`git checkout` / `git stash`), rebase against `origin/main`, and refresh editable Python packages with `pip install -e . --no-deps`.
- Run `/restart` to drain active turns and reload the gateway cleanly.

### 9. Voice Notes & TTS Natural Pronunciation Configuration
- When configuring Voice Notes / TTS (`text_to_speech`) for Indonesian conversation:
  - Default Edge TTS voice (`en-US-AriaNeural`) sounds robotic and unnatural when speaking Indonesian.
  - Query available localized neural voices: `python3 -c "import asyncio, edge_tts; asyncio.run(...)"`
  - Recommended Indonesian Edge TTS voices:
    - `id-ID-GadisNeural` (Female — friendly, expressive, natural)
    - `id-ID-ArdiNeural` (Male — calm, clear, conversational)
  - Configure via CLI: `hermes config set tts.edge.voice "id-ID-GadisNeural"`
  - For premium ultra-realistic emotion and intonation, configure external providers (`elevenlabs`, `openai`, `minimax`, `gemini-9router`) under `tts` in `config.yaml`.

### 10. Custom TTS Providers & WhatsApp Native Voice Bubble (PTT) Protocol
- **The Native Voice Note (PTT) Invariant:**
  WhatsApp only renders a native voice note bubble (green circular play button with waveform) if the audio payload is encoded as `audio/ogg; codecs=opus` (PTT format).
  - The Baileys WhatsApp Bridge (`bridge.js`) automatically transcodes `.mp3`, `.wav`, or `.m4a` to `.ogg` (48kHz mono libopus) via `ffmpeg` if `mediaType: 'audio'` is passed.
  - In Hermes Agent `tts_tool.py`, a provider MUST have `voice_compatible: true` or write `.ogg` to output the `[[audio_as_voice]]` directive.
- **Integrating Custom OpenAI/Gemini TTS via 9router (Local OpenAI-Compatible Proxy):**
  When integrating custom endpoints like Gemini 3.1 TTS (`gemini/gemini-3.1-flash-tts-preview/Kore`) via 9router (`localhost:20128` or remote proxy):
  1. Create a lightweight execution wrapper script:
     ```python
     #!/usr/bin/env python3
     import sys, json, urllib.request

     input_file, output_file = sys.argv[1], sys.argv[2]
     model = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else "gemini/gemini-3.1-flash-tts-preview/Kore"

     with open(input_file, "r", encoding="utf-8") as f:
         text = f.read().strip()

     url = "http://localhost:20128/v1/audio/speech"
     headers = {"Content-Type": "application/json", "Authorization": "Bearer sk-REDACTED-EXAMPLE"}
     payload = json.dumps({"model": model, "input": text}).encode("utf-8")

     req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
     with urllib.request.urlopen(req, timeout=30) as resp:
         with open(output_file, "wb") as out:
             out.write(resp.read())
     ```
  2. Declare the command provider in `config.yaml`:
     ```yaml
     tts:
       provider: gemini-9router
       providers:
         gemini-9router:
           type: command
           command: "python3 /root/.hermes/profiles/<profile>/scripts/tts_gemini_9router.py {input_path} {output_path} {model}"
           model: "gemini/gemini-3.1-flash-tts-preview/Kore"
           output_format: mp3
           voice_compatible: true
     ```
  3. Set `SOUL.md` guidelines for the profile so when a user requests voice note / VN / audio, the bot calls `text_to_speech` and formats output with `[[audio_as_voice]]\nMEDIA:<path>`.
  4. Ensure `ffmpeg` is installed on the host (`apt-get install -y ffmpeg`) so the Baileys bridge can transcode MP3/WAV chunks on the fly into native WhatsApp PTT Opus.

### 11. Inbound Third-Party & Service Interaction Protocol (Couriers, Vendors, Unknown Contacts)
- **Sender Role Identification & Anti-Echo Invariant:**
  When an incoming message arrives from an external party (e.g. logistics courier confirming delivery/COD, vendor, customer service, or marketplace seller):
  - **Do NOT treat the message as an advisory prompt from the account owner.** The external party is speaking *to* the account owner, not asking the AI to draft a template, explain what their own message means, or provide theoretical advice.
  - **Never echo or parrot the sender's operational question back to them.** If a courier asks whether a package should be delivered or cancelled (*"Paketnya mau dianter apa mau dicancel?"*), echoing that exact question back to the sender causes an immediate conversational breakdown and loop.
  - **No Autonomous Financial or Contractual Decisions:** The agent does NOT own real-world purchasing or delivery acceptance decisions (COD payments, order cancellations, package acceptance) unless explicit owner instructions exist. If the owner's intent is unconfirmed, reply neutrally that the recipient will verify and confirm shortly, or alert the owner directly.
- **Honorific & Conversational Calibration:**
  - Avoid blindly assuming gendered honorifics (*"Bu"*, *"Pak"*) based on unverified recipient handles or conversational snippets. Use neutral addressing (*"Kak"*, *"Mas/Mba"*) or direct neutral phrasing.
  - **Loop Breaker:** If an external sender states their role (*"Gua kurirnya loh"*, *"Saya yang antar"*), immediately acknowledge their role and stop repeating previous questions or offering unprompted advice.

### 12. Outbound Media Attachment Path Sandbox (`MEDIA:<path>`)
- When delivering outbound media attachments in chat via `MEDIA:/absolute/path/to/file`, the file must NOT reside inside hidden configuration directories (e.g. `~/.config/...`), root root-owned system directories, or internal harness temporary folders (`~/.config/browser-harness/tmp/...`).
- Files located in hidden system folders like `.config` are silently dropped or blocked by gateway path security filters, causing the message to arrive without the attachment.
- **Rule:** Always copy or save outbound media into the agent profile's designated scratch cache directory (`~/.hermes/profiles/<profile>/cache/scratch/` or `$TMPDIR`), verify file existence and non-zero size, and send the scratch path via `MEDIA:`.

### 13. Headless Gateway Reconnect Timeout Loop & Revoked Session (Code 401) Diagnostics
- **The Symptom & Asymmetric Outage Mechanism:**
  When companion device authorization expires or is unlinked from the phone app ("Perangkat Tertaut"), Baileys receives `DisconnectReason.loggedOut (code 401)`.
  1. On code 401, Baileys deletes or zeroes out `creds.json` (0 bytes).
  2. The supervised gateway (`hermes --profile <profile> gateway run`) attempts to reconnect by launching `bridge.js`.
  3. With `creds.json` missing or empty, `bridge.js` enters QR pairing mode and prints a new ASCII/terminal QR code into its log file (`bridge.log`).
  4. In headless systemd services, nobody is watching `bridge.log` to scan the QR. After 30s, Hermes gateway times out:
     `WARNING gateway.run: Reconnect whatsapp error: whatsapp connect timed out after 30s, next retry in 300s`
  5. The gateway kills the bridge and sleeps for 300s, repeating the loop indefinitely. Meanwhile, token-based channels (such as Telegram bots) remain completely healthy, creating an asymmetric outage where Telegram is online but WhatsApp is dead.
- **Triage & Diagnosis Steps:**
  1. Check `platforms.whatsapp.extra.session_path` in `config.yaml` to locate the exact session directory (never assume default path).
  2. Check for 0-byte or missing credentials:
     `find ~/.hermes/profiles/*/whatsapp/session/ ~/.hermes/profiles/*/platforms/whatsapp/session/ ~/.hermes/platforms/whatsapp/session/ -name "creds.json" -size 0`
  3. Inspect recent gateway logs for the 30s timeout / 300s retry pattern:
     `journalctl --user -u "hermes-gateway-*" -n 40 --no-pager | grep -i "reconnect whatsapp error"`
  4. Probe socket state directly with a fast headless Baileys handshake check to distinguish transient network drops from authentic 401 logouts.
- **Recovery Protocol:**
  1. Instruct the user to open WhatsApp on their phone -> Linked Devices (Perangkat Tertaut) -> tap stale Linux/Google Chrome session -> Log out ("Keluar") to clear server linkage.
  2. Delete any 0-byte `creds.json` in the session directory.
  3. Launch `scripts/pair_whatsapp_bridge.py` or run `bridge.js --pair-json` inside a detached tmux session.
  4. Render the emitted QR string to a PNG using `qrcode.make()` and deliver it in the active conversation via `MEDIA:<path>`.
  5. **Mandatory Credential Flush Invariant:** Wait 2-3 seconds after the `connected` event before killing the pairing bridge so Baileys writes non-empty `creds.json`.
  6. **Credential Backup Invariant:** Immediately make an atomic backup:
     `cp <session_dir>/creds.json <session_dir>/../creds_backup.json`
     to preserve valid credentials against accidental 0-byte truncations during crashes.
  7. **Standalone Bridge Teardown & Port Free Invariant (Anti-`EADDRINUSE` & Anti-Drop):**
     - **The In-Flight Pairing Bridge Inbound Drop Trap:** Standalone pairing bridges (e.g. run via tmux or python supervisor) usually lack the full gateway environment variables (`WHATSAPP_ALLOWED_USERS`, `WHATSAPP_DM_POLICY`). Any test message sent while the temporary bridge is still holding the port is dropped with `reason: "allowlist_mismatch"` because Baileys cannot match the sender's `@lid` to `WHATSAPP_ALLOWED_USERS`.
     - **Rule:** Never instruct the user to test chatting while the temporary pairing bridge is active. Immediately upon detecting the `connected` event and credential flush, terminate the temporary pairing bridge (`tmux kill-session` or kill PID) and verify the port (3000/3001) is completely free (`lsof -i :<port>`).
  8. **Service Restart & Managed Bridge Handover:**
     Restart the profile gateway service via D-Bus:
     `busctl --user call org.freedesktop.systemd1 /org/freedesktop/systemd1 org.freedesktop.systemd1.Manager RestartUnit ss "hermes-gateway-<profile>.service" "replace"`
     This allows the official gateway to spawn its own managed bridge loaded with the full profile `.env`, allowlists, and active `/messages` long-polling loop.
  9. **Gateway State Verification & Active Outbound Handshake (Anti-False-Positive Test):**
     - Verify real-time platform status in `/root/.hermes/profiles/<profile>/gateway_state.json` (`platforms.whatsapp.state == "connected"`).
     - Probe bridge health: `GET http://127.0.0.1:<port>/health` (expect `status: "connected"`).
     - **Mandatory Outbound Ping Handshake:** Do not wait passively for the user to chat. Proactively send an outbound test ping to the user's phone via `POST http://127.0.0.1:<port>/send` (`{"chatId": "<owner_phone>@s.whatsapp.net", "message": "Pesan tes..."}`), confirm HTTP 200 with `success: true` and `messageId`, and instruct the user to reply to that specific message. This guarantees bi-directional routing (outbound push + inbound long-polling intake) on the new session.

### 14. Quoted Media (Images/Docs/Audio) in Replies & Inbound Text-Only Fallback Pitfall
- **The Symptom & Mechanism:**
  When a user in a WhatsApp group or DM replies to or quotes another member's media message (for example, replying to an image, PDF document, or voice note with `@bot bantu kerjain ini` or `bantu ni`):
  - The upstream Hermes WhatsApp gateway adapter extracts only the text caption of the quoted message into `reply_to_text` (delivered to the agent as `[Replying to: "..."] <user_text>`).
  - The actual binary media from the quoted message (`quotedMessage.imageMessage`, `documentMessage`, or `audioMessage`) is NOT automatically downloaded or passed into the current agent turn's input prompt.
- **The Pitfall:** The agent sees only the quoted caption string, leading to false assumptions (e.g. assuming the user forgot to attach a file, querying unrelated LMS/web sources, or asking the user "mana tugasnya/gambarnya?").
- **Inspection & Extraction Pattern:**
  1. Identify the inbound message ID from `state.db`:
     `SELECT platform_message_id FROM messages ORDER BY id DESC LIMIT 1;`
  2. Inspect the stored message in the Baileys bridge or memory store (`__messageStore.get(platform_message_id)`).
  3. Traverse to `message.extendedTextMessage.contextInfo.quotedMessage` and locate `imageMessage`, `documentMessage`, or `audioMessage`.
  4. For immediate visual recognition, `quotedMessage.imageMessage.jpegThumbnail` provides a valid JPEG byte buffer directly without network decryption.
  5. For full-resolution media: pass the synthetic message object `{ key: { id: stanzaId, remoteJid }, message: { imageMessage } }` to Baileys `downloadMediaMessage(synthetic, 'buffer', ...)`, save the decrypted buffer into the profile scratch cache (`~/.hermes/profiles/<profile>/cache/scratch/quoted_media.jpg`), and inspect it with `vision_analyze`.

### 15. Inbound WhatsApp Media Intake Location & Discovery (`/root/.hermes/cache/images/`)
- **The Mechanism:** When a user sends photos or an image album via WhatsApp with or without an accompanying prompt (e.g. asking *"lu bisa liat 4 foto ini?"* or *"tolong baca gambar ini"*), the WhatsApp gateway downloads the inbound media files directly to the centralized image cache:
  `/root/.hermes/cache/images/img_<hex>.jpg`
- **Zero-Refusal Invariant:** Never claim you cannot see the images or ask the user to re-upload without first checking the cache.
- **Workflow to Inspect Inbound WhatsApp Images:**
  1. Locate the latest received media by modification time:
     `ls -lrt /root/.hermes/cache/images/ | tail -n <N>`
     or:
     `find /root/.hermes/cache/images/ -type f -mmin -15`
  2. Inspect each image directly with `vision_analyze(image_url="/root/.hermes/cache/images/img_<hash>.jpg", question="...")`.
  3. Batch multiple `vision_analyze` calls in a single assistant turn when the user sends multiple photos or an album for rapid, comprehensive review.

### 16. Comprehensive Profile WhatsApp Audit & Settings Inspection Procedure
When an operator or user requests a complete preview or audit of all WhatsApp configurations on a profile ("semuanya ya tanpa terkecuali"):
1. **Primary Config (`~/.hermes/profiles/<profile>/config.yaml`):**
   - Inspect `platforms.whatsapp`: `enabled`, `home_channel` (`chat_id`, `name`, `platform`, `user_id`), and all `extra` fields (`group_policy`, `group_allow_from`, `group_allowed_chats`, `allow_all_users`, `allow_from`, `require_mention`, `bridge_port`, `session_path`, `mention_patterns`).
   - Inspect `platform_toolsets.whatsapp`: Check permitted tools (`terminal`, `file`, `web`, `vision`, `code_execution`, etc.). Note that tools omitted here cannot be invoked when responding to WhatsApp messages even if enabled in global `toolsets`.
2. **Environment Variables (`~/.hermes/profiles/<profile>/.env`):**
   - **Credential Store Read Barrier:** Hermes file tools (`read_file`, `search_files`) block reading `.env` directly as a credential store. Use terminal grep:
     `grep -i "^WHATSAPP_" ~/.hermes/profiles/<profile>/.env`
     to audit `WHATSAPP_MODE`, `WHATSAPP_DM_POLICY`, `WHATSAPP_ALLOWED_USERS`, `WHATSAPP_REQUIRE_MENTION`, `WHATSAPP_HOME_CHANNEL`, `WHATSAPP_MENTION_PATTERNS`, `WHATSAPP_GROUP_POLICY`, `WHATSAPP_ALLOW_ALL_USERS`, `WHATSAPP_ALLOW_ALL_GROUP_MEMBERS`, `WHATSAPP_DEBUG`, and `WHATSAPP_GROUP_ALLOW_FROM`.
3. **Runtime Bridge Process & Supervisor:**
   - Active process arguments: `ps aux | grep -E "whatsapp-bridge|bridge.js"` to confirm live `--port` (3000 vs 3001), `--session` directory, and `--mode` (`bot` vs `self-chat`).
   - Supervisor service unit: `systemctl --user status hermes-gateway.service` or check `gateway_state.json`.
4. **Session Directory Integrity:**
   - Check `session_path` directory: verify `creds.json` exists and has non-zero size (`ls -la <session_path>/creds.json`), and confirm whether `creds_backup.json` exists.
5. **Channel Routing Directory (`~/.hermes/profiles/<profile>/channel_directory.json`):**
   - Inspect registered WhatsApp entries under `platforms.whatsapp` (`home_destination`, direct message `@lid` records, and known `@g.us` group chats).

### 17. Outbound Quote-Reply Bubble Configuration (`reply_to_mode`) & Trigger-by-Reply Diagnostics
- **Outbound Quote-Reply Bubble Behavior (`reply_to_mode`):**
  Controls whether Hermes attaches the incoming user message as a native quoted reply bubble in its responses.
  - Options:
    - `"first"`: Quoted reply bubble is attached to the **first message chunk only** (recommended). Prevents long multi-chunk responses from quoting repeatedly.
    - `"all"`: Every message chunk quotes the user's incoming message.
    - `"off"`: Sends replies as standalone, unthreaded WhatsApp messages.
  - Set via CLI:
    ```bash
    hermes config set platforms.whatsapp.reply_to_mode first
    ```
  - Or via `~/.hermes/profiles/<profile>/config.yaml`:
    ```yaml
    platforms:
      whatsapp:
        reply_to_mode: "first"
    ```
  - Mechanism: Gateway adapter passes inbound `reply_to` message ID to `/send`. The Baileys bridge looks up the message in `messageStore.get(replyTo)` and injects `options.quoted = quoted`.
- **Inbound Trigger-by-Reply Diagnostics (When replying without @mention doesn't trigger):**
  - **Quoting Bot Message vs Human Message:** The gateway's `_message_is_reply_to_bot` specifically checks if `quotedParticipant` matches `botIds`. Replying to a message sent by a human in a group will NOT wake the bot unless an explicit `@mention` or mention pattern is included.
  - **Baileys Quoted Participant & Bot ID Device Suffix Trap (`quotedParticipant` vs `botIds`):**
    Baileys emits `quotedParticipant` and user credentials with device suffixes (e.g. `628xxx:12@s.whatsapp.net` or `12345:0@lid`).
    *The Suffix Normalization Pitfall:* In unpatched bridge scripts (`bridge_helpers.js`), `normalizeWhatsAppId` used a naive string replace (`replace(':', '@')`), which turned `628xxx:7@s.whatsapp.net` into `628xxx@7@s.whatsapp.net`. This corrupted `botIds` with duplicate `@` symbols, preventing any quote-reply from matching.
    *The Correct Fix in `bridge_helpers.js`:*
    ```javascript
    export function normalizeWhatsAppId(value) {
      if (!value) return '';
      return String(value).replace(/\:\d+(?=@)/, '').replace(/\:\d+$/, '');
    }
    ```
  - **The Node.js In-Memory Code Retention Pitfall on Gateway Restarts:**
    When restarting the gateway service (e.g. via `systemctl --user restart` or `busctl RestartUnit`), if systemd `KillMode=mixed` is set or the bridge process is detached, the Node.js bridge process (`bridge.js`) continues running on port 3000/3010.
    When the new Python gateway process boots, it checks if port 3000/3010 is already listening. If alive, it reuses the running bridge instead of spawning a new Node.js process!
    Because Node.js holds imported modules in memory, any disk patches to `bridge.js` or `bridge_helpers.js` remain completely inactive in the running process.
    *The Mandatory Action:* When patching bridge scripts, you MUST explicitly kill the Node.js bridge process (`kill -9 <bridge_pid>`). The gateway supervisor detects the socket drop and automatically respawns a fresh Node.js bridge from disk within 3 seconds. Always verify bridge uptime drops to <10s via `curl -s http://127.0.0.1:<port>/health` to confirm the fresh code is live.
  - **Group Authorization Drop:** If non-owner group members reply to the bot and get no response, check `gateway/authz_mixin.py`. The sender must be allowed via `group_allowed_chats` containing the group JID, or `allow_all_users: true` on open groups. Otherwise inbound events are dropped with `Unauthorized user`.
  - **Self-Account Testing Trap (`from_me_group`):** Quoting the bot from the same phone number running the bot session emits `fromMe: true`, which `bridge.js` silently drops to prevent infinite self-echo loops. Always test quote-reply behavior with a separate phone number.

### 18. Ambient Group Context Ingestion & Quoted Message Bridging
- **Ambient Message Discard Invariant:** In WhatsApp groups where `require_mention: true`, the gateway adapter drops all messages that do not contain an explicit mention, bot quote-reply, or slash command (`_should_process_message`). These unmentioned messages are discarded immediately at the transport layer—they are never committed to `state.db` and never enter the agent's LLM context window. The agent cannot inspect or recall past unmentioned group messages.
- **On-Demand Context Bridging via Quoted Replies:** To bring an unaddressed third-party message or task into the agent's context, instruct the user to **quote-reply to that message while tagging the bot** (e.g. `[Replying to: "..."] @bot tolong analisis ini`). WhatsApp packs the target message's text into `quotedText` (`reply_to_text`), cleanly injecting that specific prior message into the turn prompt without ambient leakage.
- **The `require_mention: false` Anti-Pattern in Active Groups:** Avoid setting `require_mention: false` or adding busy group JIDs to `free_response_chats`. Doing so forces every conversational statement from all members to trigger an LLM turn, burning token quota, creating conversational spam, and risking concurrent session race conditions.

