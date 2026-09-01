---
name: "telegram-bot-operations"
description: "Troubleshooting and operating Telegram bots, userbots (Pyrogram/Telethon), and PyTgCalls voice integrations."
category: "devops"
---
# Telegram Bot & Userbot Operations

## Triggers
- Deploying, migrating, or debugging a Telegram bot, userbot, or PyTgCalls integration.
- A Telegram bot is online but not responding to commands.
- Establishing initial session files (`.session`) for headless userbots on a VPS.

## Headless Userbot Authentication
When a script (like `python -m userbot.login`) prompts for a phone number, token, or OTP via `stdin`, you cannot run it in a standard foreground `terminal()` call because it will hang waiting for input.
1. Run it in the background with PTY enabled: `terminal(command="...", background=true, pty=true)`
2. Poll the output to read the prompt: `process(action='poll', session_id='...')`
3. Submit inputs interactively: `process(action='submit', data='<token_or_otp>')`

## Silent Bot Failures (Not Responding)
If a bot doesn't respond to commands, check these before rewriting the routing logic:
1. **Privacy Mode (Groups):** In groups/supergroups, bots cannot see standard messages unless they are Admins, Privacy Mode is disabled via `@BotFather`, or the bot is explicitly tagged (e.g., `/search@Animestrbot`). Always test in DM (private chat) or with a direct mention first.
2. **Stuck Webhooks:** If migrating a bot from webhook to polling, pending updates might block the queue and cause polling to return empty arrays.
   - Verify: `GET https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
   - Fix: `POST https://api.telegram.org/bot<TOKEN>/deleteWebhook` with JSON `{"drop_pending_updates": true}`.
3. **Pyrogram Global Handlers:** An empty `@bot.on_message()` at the top of a Pyrogram script will swallow all messages if it calls `message.continue_propagation()` incorrectly. Move it to a specific group (e.g., `@bot.on_message(group=1)`) or remove it.
4. **Silent Upstream API Errors:** If the bot fetches external data (e.g., Bstation) and hits a WAF limit (like HTTP 509), a poorly wrapped try/except might crash the handler silently. Aiogram logs these better than Pyrogram; ensure upstream clients have necessary auth (like `cookies.txt`).

## PyTgCalls Dependency Hell
`py-tgcalls` is notoriously fragile due to its `ntgcalls` C++ bindings.
- **Yanked Versions:** `2.2.12` is yanked from PyPI. Use `2.2.11` instead.
- **InputMode ImportError:** If you see `ImportError: cannot import name 'InputMode' from 'ntgcalls'`, the environment's Python/C++ compilation conflicts with the installed `ntgcalls` version.
- **Known Stable Fallback:** `pip install py-tgcalls==1.2.9 ntgcalls==1.1.2 Pyrogram==2.0.106`. 
- *(Note: `py-tgcalls` 1.x and 2.x have different API shapes, e.g., `GroupCallFactory` vs `GroupCallConfig` and `MediaStream` locations. Be ready to patch the app code if downgrading).*