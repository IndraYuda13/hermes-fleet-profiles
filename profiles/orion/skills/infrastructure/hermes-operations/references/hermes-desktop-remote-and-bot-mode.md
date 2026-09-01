# Remote Gateway Persistent Authentication & Desktop Bot Mode Architecture

## 1. Remote Gateway Static Session Token Setup

When connecting Hermes Desktop from a local laptop/client to a headless remote VPS running `hermes dashboard` behind a reverse proxy or Cloudflare Tunnel:

1. **Ephemeral vs Static Session Tokens:**
   - By default, `hermes dashboard` generates a transient random token (`secrets.token_urlsafe(32)`) on every startup.
   - When restarted via systemd or crash recovery, the session token changes, causing Hermes Desktop remote connections to immediately fail with `401 Unauthorized` or disconnect.
2. **Injecting Persistent Token via Systemd:**
   - Set `HERMES_DASHBOARD_SESSION_TOKEN` in the environment of `/etc/systemd/system/hermes-dashboard.service`:
     ```ini
     [Service]
     Environment=HERMES_DASHBOARD_SESSION_TOKEN=<strong-secret-token>
     ```
   - Reload and restart:
     ```bash
     systemctl daemon-reload && systemctl restart hermes-dashboard
     ```
3. **Verification:**
   - Probe endpoint with custom header:
     ```bash
     curl -s -o /dev/null -w "%{http_code}\n" -H "X-Hermes-Session-Token: <strong-secret-token>" https://<domain>/api/sessions
     ```
   - Must return `200`.

---

## 2. Hermes Desktop Bot Mode & Group Chat Orchestration

Hermes Desktop (`hermes-bots` plugin) provides a multi-agent roster and group chat room:

1. **Architecture:**
   - Each Bot in the roster maps 1:1 to an independent Hermes profile on the target gateway host (e.g. `orion`, `forge`, `frame`, `lens`, `prism`, `sentinel`).
   - Group Chat runs a **Round-Robin Multi-Session Orchestration** loop (up to 10 rounds max, capped at 150 messages per session).
2. **Delta Feed & Turn Prompt:**
   - The plugin computes unseen message deltas per member and formats a turn payload (`buildGroupChatTurnPrompt`).
   - Members only receive new messages relative to their thread watermark.
3. **The `(pass)` Protocol & Settling:**
   - To prevent infinite token-consuming loops, agent prompts enforce: *"If you have nothing new to add, reply with exactly (pass)."*
   - When all participants in a round pass (`spokeThisRound === 0`), the conversation loop naturally stops ("settles").
4. **Failure Modes & Troubleshooting:**
   - **Premature Stop:** Generic prompts without clear actionable tasks cause agents to pass immediately after 1 round. Use explicit `@mention` chains (e.g. `@forge buat skrip X, lalu lempar ke @lens untuk dicek`).
   - **Turn Polling Cap / Stranded Turns:** Heavy reasoning models or slow APIs may exceed the per-turn polling timeout (`GROUP_TURN_TIMEOUT_MS`). Stranded responses are marked and harvested on subsequent turns rather than lost.
