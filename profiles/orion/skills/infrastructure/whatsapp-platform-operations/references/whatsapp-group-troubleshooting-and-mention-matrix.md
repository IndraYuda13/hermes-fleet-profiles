# WhatsApp Group Troubleshooting & Inbound Message Routing Matrix

## 1. Group Inbound Message Routing Precedence

In Hermes WhatsApp platform adapter (`gateway/platforms/whatsapp_common.py`), group messages evaluate the following priority ladder in `_should_process_message`:

```
Inbound Message in Group Chat
           │
           ▼
[ Is Broadcast / Status / Channel? ] ──▶ YES ──▶ DROP (Never processed)
           │ NO
           ▼
[ Is Group Allowed? (group_policy) ] ──▶ NO ───▶ DROP (Policy rejection)
           │ YES
           ▼
[ Is Chat in free_response_chats OR require_mention == False? ] ──▶ YES ──▶ PROCESS
           │ NO (require_mention == True)
           ▼
[ Does message start with '/' (Slash Command)? ] ──▶ YES ──▶ PROCESS (Bypasses mention gate)
           │ NO
           ▼
[ Is message a Reply/Quote to a Bot Message? ] ──▶ YES ──▶ PROCESS
           │ NO
           ▼
[ Does message mention Bot ID / LID / @number? ] ──▶ YES ──▶ PROCESS
           │ NO
           ▼
[ Does message match regex in mention_patterns? ] ──▶ YES ──▶ PROCESS
           │ NO
           ▼
         DROP (Treated as ambient group chatter)
```

### 1.1. Ambient Message Discard vs Quoted Context Bridging
- **Zero-Storage of Ambient Chatter:** In group chats with `require_mention: true`, unaddressed messages evaluate to `DROP` at the bottom of the ladder. They are dropped before session persistence—they are not logged to `state.db`, not stored in transcript history, and cannot be retrieved by the agent later.
- **Bringing Historical Messages into Context:** If a user asks the bot to analyze, summarize, or act on a message sent earlier by another human member, the user must **quote-reply to that message while tagging the bot**. This causes the WhatsApp mobile client to bundle the target message into `contextInfo.quotedMessage`, which Hermes injects into the prompt as `[Replying to: "..."] <instruction>`.
- **The Token & Spam Hazard of `require_mention: false`:** Setting `require_mention: false` in shared groups converts all ambient human conversation into agent turn prompts. This rapidly exhausts API credit, pollutes session memory, and disrupts normal group interactions.

---

## 2. The Mention Format Trap: LID vs Phone Number

In modern WhatsApp groups, users frequently tag contacts by their Linked Identity Device (LID) handle rather than pure phone numbers:
- **Phone JID:** `@<WHATSAPP_ID>`
- **LID Handle:** `@<WHATSAPP_ID>` (e.g. `@<WHATSAPP_ID>AW.ai`)
- **Display Name:** `AW.ai` or `Akun Wa Gpt`

### Recommended Mention Patterns Configuration
Always populate `mention_patterns` in `config.yaml` and `WHATSAPP_MENTION_PATTERNS` in `.env` with a multi-pattern regex array covering both explicit `@` prefixed display names and raw terms:
```ini
WHATSAPP_MENTION_PATTERNS=["@<WHATSAPP_ID>", "@<WHATSAPP_ID>", "AW.ai", "@AW.ai", "Akun Wa Gpt", "\\bOrion\\b", "\\bbot\\b"]
```

### 2.1. Bare Mention & Presence Check Response Discipline
When an inbound message contains solely a mention tag (such as `@<WHATSAPP_ID>`) or an informal presence query (`absen`, `absen bree`, `p`, `ping`, `tes`):
- **Immediate Conversational Acknowledgement:** Treat the message as a simple heartbeat/liveness check. Respond directly with a brief confirmation of readiness.
- **No Background Diagnostics:** Never initiate shell diagnostics, process inspections (`ps aux | grep whatsapp`), or session directory queries to investigate the identifier. Treating an unadorned mention as a technical anomaly stalls message delivery and triggers user interruptions.

---

## 3. The `fromMe` Anti-Loop Drop & Testing Invariants

### The Root Cause:
When an operator tests group responsiveness by sending `@bot halo` from the **exact same smartphone / WhatsApp number that is paired as the bot session**, the underlying Baileys socket marks `msg.key.fromMe = true`.

Inside `scripts/whatsapp-bridge/bridge.js`:
```javascript
if (msg.key.fromMe) {
  if (isGroup || chatId.includes('status')) {
    emitDebugEvent({ stage: 'ignored', reason: 'from_me_group' });
    continue;
  }
}
```
This is an intentional safeguard preventing the bot from replying to its own outgoing group messages and causing an infinite token-consuming recursion loop.

### Strict Testing Protocol:
1. **Never test group interactions from the host account itself.**
2. Test using a **secondary phone number** or ask a group peer/member to tag the bot.
3. Alternatively, test slash commands (`/ping`, `/status`) or direct private messages (DMs).

---

## 4. Policy Configuration Checklist for Open Group Interaction

To enable frictionless bot responses across any new WhatsApp group without hunting JIDs:

1. **`config.yaml` Settings:**
   ```yaml
   platforms:
     whatsapp:
       enabled: true
       extra:
         group_policy: "open"
         allow_all_users: true
         require_mention: false # Allows keyword triggers & slash commands freely
         mention_patterns:
           - "@<WHATSAPP_ID>"
           - "AW.ai"
           - "\\bOrion\\b"
           - "\\bbot\\b"
   ```

2. **`.env` Mirror Settings:**
   ```ini
   WHATSAPP_ENABLED=true
   WHATSAPP_MODE=bot
   WHATSAPP_GROUP_POLICY=open
   WHATSAPP_ALLOW_ALL_USERS=true
   WHATSAPP_ALLOW_ALL_GROUP_MEMBERS=true
   WHATSAPP_REQUIRE_MENTION=false
   ```

---

## 5. Socket Conflict & Long-Polling Queue Diagnostic Workflows

### 5.1. Socket Conflict Recovery (`EADDRINUSE: 3000`)
When restarting the Node.js WhatsApp bridge subprocess:
```bash
# 1. Identify active listener
lsof -i :3000

# 2. Terminate orphaned instance
kill -9 <PID>

# 3. Verify socket release before re-spawning
lsof -i :3000 || echo "Port 3000 is clean"
```

### 5.2. Direct Bridge API Verification & Schema Quirks
- Health inspection: `GET http://127.0.0.1:3000/health`
- Direct outbound test payload:
  - Method: `POST http://127.0.0.1:3000/send`
  - Headers: `Content-Type: application/json`
  - Body: `{"chatId": "<jid/lid>", "message": "<text>"}`
  - *Pitfall:* Do NOT use field names `text` or `recipient` alone; the bridge controller strictly validates `chatId` and `message`.
- Long-poll queue inspection: `GET http://127.0.0.1:3000/messages` (returns pending inbound messages and flushes buffer).

### 5.3. Group JID vs Title Disambiguation
Never guess WhatsApp group JIDs from sender-key timestamps alone. Multiple groups (`Test`, `Afterhours (AOC)`) can update sender keys concurrently. Always query `http://127.0.0.1:3000/chat/<jid>` to verify `name` matches the target group before updating `group_allow_from` or dispatching notifications.

---

## 6. Baileys WebSocket Keep-Alive, Idle Timeouts (428 / 503) & Dependency Crashes

### 6.1. Why WhatsApp Disconnects Intermittently (Reason 428 & 503)
Server-side WhatsApp Web sockets terminate idle TCP connections if no ping/heartbeat occurs within standard timeout windows. By default in Baileys, without explicit keep-alive parameters, long idle periods cause sudden disconnections:
- `Connection closed (reason: 428)` — Precondition Required / Socket Timeout
- `Connection closed (reason: 503)` — Stream Errored Out / Server Unavailable

### 6.2. Socket Hardening Configuration in `bridge.js`
Always instantiate `makeWASocket` with explicit keep-alive and query timeout parameters:
```javascript
sock = makeWASocket({
  auth: state,
  logger,
  printQRInTerminal: false,
  browser: ['Hermes Agent', 'Chrome', '120.0'],
  syncFullHistory: false,
  markOnlineOnConnect: true,
  keepAliveIntervalMs: 25000,      // Sends WebSocket ping every 25 seconds
  connectTimeoutMs: 60000,         // 60s connection timeout
  defaultQueryTimeoutMs: 60000,    // 60s query timeout
  getMessage: async (key) => ({ conversation: '' }),
});
```

### 6.3. Unhandled `link-preview-js` Dependency Crash
When group members send links/URLs, Baileys attempts to generate link metadata preview cards. If `link-preview-js` is missing in `whatsapp-bridge/node_modules`, it throws `ERR_MODULE_NOT_FOUND: Cannot find package 'link-preview-js'` and causes silent connection drops or poll stalls.
**Fix:**
```bash
cd /usr/local/lib/hermes-agent/scripts/whatsapp-bridge && npm install link-preview-js
```

---

## 7. Multi-User Group Authorization Gate (`authz_mixin.py`) & LID Normalization

### 7.1. The Group Member Default-Deny Trap & Owner-Test False Positive
In Hermes `gateway/authz_mixin.py`, `_is_user_authorized` evaluates sender authorization for all inbound messages. If `WHATSAPP_ALLOWED_USERS` contains owner phone numbers but group members send messages:
- The gateway checks if sender is in `allowed_ids`.
- Non-allowlisted group members are rejected as `Unauthorized user: <lid>`.
- **The Owner-Test False Positive:** When an operator tests `@bot test` in a new group from their own account, the bot replies because the operator is allowlisted. This masks the fact that peers/collaborators are blocked.
- **Solution:** Add the group JID to `platforms.whatsapp.extra.group_allowed_chats` in `config.yaml` (which triggers `_chat_scoped_grant()` to authorize any participant in that chat), or ensure `allow_all_users: true` / `WHATSAPP_ALLOW_ALL_USERS=true` is set when running `group_policy: open`.
- **Config Modification Rule:** In-agent file editing (`patch`, `write_file`) of `config.yaml` or `.env` is blocked by Hermes safety guards. Use `hermes --profile <profile> config set <key> <value>` via terminal instead.

### 7.2. LID Device Suffix Stripping & Corrupted `botIds` Pitfall
Baileys emits participant and bot IDs with device suffixes: e.g. `628xxx:12@s.whatsapp.net` or `12345:0@lid`.
- **The String Replace Trap:** Never use `.replace(':', '@')` in JS. It corrupts `botIds` into strings with duplicate `@` symbols (`628xxx@12@s.whatsapp.net`), breaking quote-reply matching permanently.
- **The Correct Python Normalizer:**
```python
def normalize_whatsapp_id(value: str) -> str:
    if ":" in value and "@" in value:
        parts = value.split("@", 1)
        bare = parts[0].split(":", 1)[0]
        return f"{bare}@{parts[1]}"
    return value
```
- **The Correct JS Normalizer (`bridge_helpers.js`):**
```javascript
export function normalizeWhatsAppId(value) {
  if (!value) return '';
  return String(value).replace(/\:\d+(?=@)/, '').replace(/\:\d+$/, '');
}
```
This ensures `@<WHATSAPP_ID>` tags and quoted replies match `botIds` reliably across phone numbers and LIDs.

### 7.3. The Bridge In-Memory Process Retention Pitfall on Gateway Restarts
When restarting the gateway via systemd (`systemctl --user restart` or `busctl RestartUnit`), if `KillMode=mixed` is set or the bridge was detached, the Node.js process (`bridge.js`) continues running on port 3000/3010.
- When the new Python gateway process boots, it checks if port 3000/3010 is responding. If alive, it reuses the running bridge instead of spawning a fresh Node.js process.
- Any disk edits to `bridge.js` or `bridge_helpers.js` remain completely inactive in the running Node process.
- **Rule:** When modifying bridge code, explicitly terminate the Node bridge (`kill -9 <bridge_pid>`). Confirm the newly spawned process has an `uptime` of <10s via `GET http://127.0.0.1:<port>/health`.

---

## 8. Headless Gateway Reconnect Loop & Revoked Session (Code 401) Triage

### 8.1. Failure Mechanism
When WhatsApp unlinks or revokes a companion session, Baileys emits `statusCode: 401` (`DisconnectReason.loggedOut`).
- `creds.json` is wiped to 0 bytes.
- The headless gateway spawns `bridge.js`, which prints a QR code to `bridge.log` waiting for a scan.
- Gateway timeout triggers after 30 seconds:
  `WARNING gateway.run: Reconnect whatsapp error: whatsapp connect timed out after 30s, next retry in 300s`
- The bridge process is killed and gateway enters a 5-minute cooldown loop.
- Telegram bots (HTTP token polling) remain completely operational during this failure, creating an asymmetric outage.

### 8.2. Verification & Rapid Recovery
1. Identify zero-byte creds:
   ```bash
   find ~/.hermes/profiles/*/platforms/whatsapp/session/ ~/.hermes/profiles/*/whatsapp/session/ ~/.hermes/platforms/whatsapp/session/ -name "creds.json" -size 0
   ```
2. Confirm 401 state via quick headless Baileys probe:
   ```bash
   node --input-type=module -e "
   import { makeWASocket, useMultiFileAuthState } from '/usr/local/lib/hermes-agent/scripts/whatsapp-bridge/node_modules/@whiskeysockets/baileys/lib/index.js';
   const { state } = await useMultiFileAuthState('<session_path>');
   const sock = makeWASocket({ auth: state, logger: (await import('pino')).default({ level: 'silent' }) });
   sock.ev.on('connection.update', (u) => {
     if (u.connection === 'close') {
       console.log('Status code:', u.lastDisconnect?.error?.output?.statusCode);
       process.exit(0);
     }
   });
   "
   ```
3. If 401, instruct user to log out stale device on WhatsApp mobile ("Perangkat Tertaut"), remove 0-byte `creds.json`, generate fresh QR via pairing supervisor script, render PNG, and deliver to user for scanning.
4. After pairing, ensure Baileys flushes credentials (wait 2-3s) before restarting gateway service via `busctl`.
