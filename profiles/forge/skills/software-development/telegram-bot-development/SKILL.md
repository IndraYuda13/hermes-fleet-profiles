---
name: telegram-bot-development
description: "Guidelines, quirks, and pitfalls for developing Telegram bots (Pyrogram, Telethon, Aiogram)."
---
# Telegram Bot Development

## Pyrogram
- **Handler Blocking (Global Catch-alls):** A catch-all handler like `@app.on_message()` without specific filters will consume the update. Subsequent handlers (like commands) will not fire, even if you call `message.continue_propagation()`.
  - **Fix:** Assign global/logging handlers to a different dispatch group: `@app.on_message(group=1)`. (Note: sometimes even this is buggy in older Pyrogram versions; completely removing the global `continue_propagation` handler is the safest fix).
- **Group Privacy Mode (Supergroups):** If a bot works perfectly in DMs but ignores the exact same command in a Supergroup, Telegram's Bot Privacy Mode is likely blocking it. Bots cannot read group messages by default unless mentioned (e.g. `/command@BotName`) or promoted to Admin. Do not rewrite handlers if the bot works in DM; tell the user to tag the bot or change BotFather settings.
- **PyTgCalls and Pyrogram Coupling:** `py-tgcalls` (v2.x) is strictly coupled to Pyrogram internals (e.g., imports `pyrogram.errors.GroupcallForbidden`). 
  - **Pitfall:** You cannot easily mix an `Aiogram` bot client with a `PyTgCalls` userbot in the same Python environment without hitting `ImportError` due to these tightly coupled dependencies. Stick to pure Pyrogram if using PyTgCalls.
- **Private vs Group Commands:** If a bot doesn't respond to commands in private chat (DM), check the handler's filters. A raw `@bot.on_message(filters.command("search"))` might silently drop DMs if the bot's default scope or other middleware expects a group. Explicitly add `& (filters.private | filters.group)` to the command decorator.
- **Session Locks & Running Background Processes:** SQLite session files (`.session`) are strictly single-process locked. When working on reseller Telethon accounts (`/root/cust/reseller*/session/*.session`), running scripts like `index.py` or background runners (`start4.py`) will keep a process-lock on the `.session` file (causing `sqlite3.OperationalError: database is locked` on new script connections). Always check for running background processes holding the session lock via `fuser <path_to.session>` or `ps aux | grep index.py` and terminate them (`kill <PID>`) before executing standalone script tasks (e.g. bulk group cleanup/leaving).
- **Leaving Mass Channels/Groups with Telethon:**
  - **Channels / Megagroups:** Use `client(LeaveChannelRequest(channel_entity))`.
  - **Legacy Small Groups (`tl.types.Chat`):** Using `LeaveChannelRequest` will fail. Using `DeleteChatUserRequest(chat_id=chat.id, user_id='me')` with negative channel IDs (e.g. `-4167400881`) throws `Invalid object ID for a chat`. You MUST pass the absolute positive chat ID: `DeleteChatUserRequest(chat_id=abs(chat.id), user_id='me')`.
- **Asyncio Teardown RuntimeError:** Calling `await app.stop()` or `await userbot.stop()` during shutdown often throws `RuntimeError: Task got Future attached to a different loop`. This is a known issue with Pyrogram's dispatcher teardown.
  - **Fix:** Wrap the `.stop()` call in a `try/except` block and `pass`, or remove it if graceful shutdown isn't strictly required.

## Telethon
- **SQLite Version Mismatch:** `ValueError: too many values to unpack` upon connecting usually means the system's global Python and the venv's Python have different `sqlite3` versions/compilations. 
  - **Fix:** Always run systemd services using the absolute path to the virtualenv python (e.g., `/usr/local/lib/.../venv/bin/python3`), never the global one.
- **Headless Supervisor & Pipe Buffering Verification (`start4.py` / `custX.service`):**
  When a supervisor spawns Telethon child workers with `asyncio.create_subprocess_exec(..., stdout=subprocess.PIPE)`, child stdout is buffered in pipe buffers and will NOT surface in `journalctl` until child exit.
  - **Verification without stdout:**
    1. **Connection:** Check socket state via `ss -tp` or `/proc/<pid>/fd` to confirm ESTABLISHED TLS connection to Telegram DC (`91.108.56.x:443`).
    2. **Active Broadcast:** Trace MTProto packets via `strace -p <pid> -e trace=sendto`. Ongoing message forwards produce periodic 100–650 byte payloads.
    3. **State Timestamp:** Query SQLite session state in read-only mode (`sqlite3.connect('file:<path>.session?mode=ro', uri=True)`): `SELECT max(date) FROM update_state`. An advancing timestamp confirms live event updates without tripping `sqlite3.OperationalError: database is locked`.
  - **Service Reload:** Restart the parent systemd service (`systemctl restart custX.service`). Its `ExecStartPre` runs `checklogin.py` which cleans up stale session lock PIDs via `fuser` and syncs `cf/` to `newcf/`.
- **Dead/Stale GNU Screen Sessions:** When managing Telethon reseller sessions via interactive screens (`cust1`..`cust5`), `screen -ls` may show sessions marked as `(Dead ???)`. Commands sent via `screen -S custX -X stuff` into a dead screen will fail silently. Always check `screen -ls` and run `screen -wipe` followed by recreating the detached screen sessions (`screen -d -m -S custX bash -c "cd /root/cust/resellerX && exec bash"`) before initiating `checklogin.py` or `login.py`.
- **OTP Code Resend & Session Cleanup:** Sending `resend` into an active Telethon `login.py` OTP prompt will fail with "Invalid code". To resend an OTP or retry a stuck login: terminate/quit the screen session (`screen -X -S custX quit`), purge existing `.session` files for that phone number (`rm -f /root/cust/reseller*/session/+628xxx.session*`), then restart `login.py` in a new screen.
- **Account Transfer / Config Migration:** When replacing a customer's phone number, copy existing user config JSON (`cf+628xxx.json`) and progress text files (`progres+628xxx.txt`) to the new number string before logging in so broadcast text/delay/expiry parameters are preserved without re-entry.
- **FloodWait Handling & `/restart` Bypass Pitfall:**
  - **The Cascade Trap:** In broadcast userbots, when a task catches `FloodWaitError` and sleeps (`await asyncio.sleep(e.seconds)`), an un-gated `/restart` command that cancels running tasks (`[t.cancel() for t in tasks]`) and calls `main()` aborts the sleep and immediately fires RPC requests again. Telegram treats this aggressive retry as severe spam, compounding FloodWait exponentially (minutes -> hours) or triggering `PeerFloodError`, SpamBot mutes, and `AUTH_KEY_UNREGISTERED`.
  - **Mitigation & Circuit Breaker:**
    1. **Disable Silent Auto-Sleep:** Set `client.flood_sleep_threshold = 0` to ensure Telethon raises `FloodWaitError` to application code instead of hanging silently.
    2. **Hard Cooldown Gate:** Record `cooldown_until = time() + e.seconds + 15` in persistent state. In the `/restart` handler, check `time() < cooldown_until`; if active, refuse restart, preserve the sleep task, and return the remaining cooldown time.
    3. **Avoid Immediate 'me' Push Alerts:** Do not call `client.send_message('me')` immediately upon catching `FloodWaitError`. Telegram heuristics flag immediate write RPCs following a penalty as automated bot signatures. Prefer pull-based status via `/info` using locally cached text (avoiding extra `get_messages` RPCs) or out-of-band alerts via official Bot API.
    4. **In-Memory Command Debounce:** Debounce commands in userbot event handlers (e.g. max 1 command per 15s) and silently drop spam pulses to prevent cascading flood limits on the control chat.

## Aiogram
- **Polling & API Resilience Logs:** Aiogram 3.x dispatcher automatically handles transient Telegram server glitches (`TelegramServerError: Bad Gateway`) and rate limits (`TelegramRetryAfter: Flood control exceeded on GetUpdates` / `SendMediaRequest flood wait`). These log warnings (`WARNING:aiogram.dispatcher:Sleep for X seconds and try again...`) followed by `Connection established` are normal resilience behavior during network spikes or Telegram API limits, not process crashes.
- **Dockerized Bot Architecture:** Bots deployed via Docker Compose often separate responsibilities across multiple containers (e.g. `bot` for Aiogram polling, `worker` for Celery/Telethon background tasks, `api` for webhooks/Uvicorn). Check status and logs per container (`docker ps`, `docker logs --tail 100 <container_name>`).

## General / Infrastructure
- **Webhook vs Polling Conflict:** If a bot receives no updates locally but throws no errors, a dead webhook might be intercepting them. Clear it: `curl -X POST "https://api.telegram.org/bot<TOKEN>/deleteWebhook" -d "drop_pending_updates=true"`.
- **Media Upload Limits:** Standard Bot API limits uploads to 50MB. For larger files (like Anime HD), either deploy a Local Bot API Server or download lower quality (e.g., `yt-dlp -f worst`).
- **Interactive Logins (Userbots):** Logging into a userbot requires PTY to handle the OTP prompt. Use `terminal(pty=true, background=true)` and `process(action='submit', data=...)` to supply the phone number/token and OTP.
- **PyTgCalls Dependencies:** `py-tgcalls==2.2.12` was yanked from PyPI, causing installation failures. Pin to `py-tgcalls==2.2.11` instead.
- **PyTgCalls & NTgCalls Version Conflict (C++ Bindings):** When mixing PyTgCalls with Pyrogram, upgrading or installing mismatched `ntgcalls` can break bindings (e.g. `ImportError: cannot import name 'InputMode' from 'ntgcalls'`). If you see this, pin exactly to: `Pyrogram==2.0.106`, `py-tgcalls==2.2.11`, `ntgcalls==1.1.2`.
- **API 509 (Cloudflare/WAF):** Scraping APIs heavily WAF-protected (like Bstation) will return HTTP -509 if queried without valid authentication, causing silent errors downstream. Always provide a valid `cookies.txt` (Netscape format) to bypass rate-limiting.
- **Bot Auto-Update / Git Pull Failures:** When Telegram bots feature an in-bot `/update` command executing `git pull`, updates will fail with "Cannot update: there are uncommitted changes" if local files (e.g., `uv.lock`, modified configs) have uncommitted modifications. Fix: check `git status` & `git diff` in the repository, discard local edits using `git checkout <files>` (or `git stash`), and confirm `git status` is clean before re-triggering `/update`.

## Routing, deployment, and voice-operation checks

1. **Prove updates first:** test direct messages, a privacy-mode-compatible supergroup command, and webhook/polling ownership. A dead webhook can be cleared with `deleteWebhook`; do not change handlers before this boundary is understood.
2. **Keep dispatch explicit:** put broad logging/catch-all Pyrogram handlers in `group=-1` (or remove them) so they cannot consume command updates; ensure command filters deliberately include private/group contexts.
3. **Operate the right process:** stop the process holding a `.session` file before restart; run systemd with the absolute virtualenv interpreter; use a PTY for phone/OTP login. Inspect logs, token/session persistence, and network before redeploying.
4. **Voice-stack compatibility:** use the tested v2 tuple `Pyrogram==2.0.106`, `py-tgcalls==2.2.11`, `ntgcalls==1.1.2`; `2.2.12` was yanked. For legacy Python 3.11 integrations, pin `py-tgcalls==1.2.9` plus `ntgcalls==1.1.2` and do not mix the v1 `GroupCallConfig`/`MediaStream` API with v2 `GroupCallFactory` code.
5. **Media and scraping:** Bot API uploads normally cap at 50 MB; use a local Bot API server or lower-quality source where appropriate. Treat WAF errors as an authenticated-cookie/input problem, not a Telegram-handler defect.

Full prior troubleshooting and routing recipes remain available in `references/telegram-bot-troubleshooting-legacy.md`, `references/telegram-pyrogram-bots-legacy.md`, `references/telegram-bot-operations-legacy.md`, and `references/telegram-bot-routing-legacy.md`.

## Verification

- [ ] A minimal bot command receives the intended update in the target chat type.
- [ ] Only one polling/webhook owner and one session-file holder are running.
- [ ] Version pins, service interpreter, and voice API generation match.
- [ ] Restarted processes are validated through logs and a real message/voice action.