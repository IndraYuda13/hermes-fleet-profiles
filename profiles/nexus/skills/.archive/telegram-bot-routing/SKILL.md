---
name: telegram-bot-routing
description: Advanced Telegram userbot and bot API routing and troubleshooting
---

# Telegram Bot Routing and Userbots

This skill covers advanced troubleshooting and routing patterns for Telegram bots running via Pyrogram/Telethon, especially when combined with PyTgCalls for Voice Chat Group streaming.

## Pitfalls & Troubleshooting

### 1. Pyrogram Global Loggers Swallowing Messages
If a Pyrogram application uses a global `@app.on_message()` logger with `continue_propagation()`, it can silently drop incoming commands or messages due to handler priority and internal routing bugs.
**Fix:** Remove global empty-filter message handlers, or ensure they are explicitly isolated in a higher group number (e.g., `group=1`) so they do not block standard command handlers (`group=0`).

### 2. Silent Bots (No Response to Commands)
If a bot appears online but ignores commands:
- **Filter Scope:** Ensure command handlers explicitly permit private messages if needed (`filters.command("cmd") & (filters.private | filters.group)`).
- **Webhook Conflicts:** If a bot was previously using webhooks and switched to polling, pending updates can stack up in the Telegram API queue and block new messages.
  - Check: `GET https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
  - Fix: `POST https://api.telegram.org/bot<TOKEN>/deleteWebhook` with `{"drop_pending_updates": True}`.

### 3. Userbot PyTgCalls Setup
Userbots designed for streaming (PyTgCalls) require a valid user session. If the userbot fails to join or stream:
- The session must be initialized locally (`python3 -m userbot.login`).
- `py-tgcalls` versions can be volatile (e.g., v2.2.12 pulled from PyPI). Downgrade to known stable versions (e.g., v2.2.11) if installation fails.

## Routing Isolation
When running an orchestrator that combines a Bot API client and a Userbot client in the same asyncio loop, keep their handlers strictly isolated. Use manual testing scripts (`run_manual.py`) with a minimal `Client` setup to isolate whether routing failures are code-level (app logic) or network-level (Telegram API blocks).