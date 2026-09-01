---
name: telegram-bot-troubleshooting
description: Troubleshooting steps for Telegram bots that are online but not responding to messages.
---

# Telegram Bot Troubleshooting

Use this when a Telegram bot process starts successfully and runs without crashing, but fails to respond to user messages or commands.

## 1. Verify Chat Privacy Mode (Supergroups)
By default, Telegram bots cannot read messages in Supergroups unless:
- They are mentioned explicitly (e.g., `/command@bot_username`).
- They are made an Admin of the group.
- Privacy Mode is disabled via `@BotFather` (`/setprivacy` -> Disable).
**Action**: Always test the bot in a Direct Message (DM/Private Chat) first to rule out Privacy Mode issues. If it works in DM but not a group, Privacy Mode is the culprit.

## 2. Check Webhook vs Polling Conflicts
If the bot uses polling (`getUpdates`), a lingering webhook will silently steal all updates.
**Action**:
- Check webhook status: `curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"`
- If a webhook URL is set or `pending_update_count` is stuck, delete it and drop pending:
  `curl -X POST "https://api.telegram.org/bot<TOKEN>/deleteWebhook" -d "drop_pending_updates=true"`

## 3. Isolate Handler Hijacking (Framework Specific)
A poorly configured global handler (like a catch-all logger) can consume updates and prevent specific command handlers from executing.
**Action (Pyrogram)**: 
- A bare `@app.on_message()` without a `group` parameter (e.g., `group=1`) can block lower-priority handlers, even if `message.continue_propagation()` is used (known Pyrogram bug).
- If moving loggers to `group=1` fails, delete the global logger entirely.
- If command filters are heavily constrained (e.g. `filters.private`), ensure they explicitly allow group contexts if expected (`filters.private | filters.group`).
- If Pyrogram routing remains broken, migrating message handling to Aiogram is often a faster fix, leaving Pyrogram only for userbot/Voice Chat tasks.

## 4. PyTgCalls & NTgCalls C++ Binding Conflicts (Voice Chat)
When running PyTgCalls alongside a bot framework (Aiogram/Pyrogram), C++ binding crashes often occur (`ImportError: cannot import name 'GroupcallForbidden'` or `ImportError: cannot import name 'InputMode' from 'ntgcalls'`).
**Action**:
- These errors mean the `ntgcalls` C++ library version doesn't match what the wrapper expects, or `py-tgcalls` is trying to hook into an incompatible Pyrogram version.
- **Known Stable Matrix (Python 3.11)**: Downgrade to `py-tgcalls==1.2.9`, `ntgcalls==1.1.2`, and `Pyrogram==2.0.106`.
  ```bash
  pip uninstall pytgcalls py-tgcalls ntgcalls
  pip install py-tgcalls==1.2.9 ntgcalls==1.1.2 Pyrogram==2.0.106
  ```
- **Code Impact**: Note that older `py-tgcalls` versions (v1) use `GroupCallConfig` instead of `GroupCallFactory` and require `MediaStream` imports from `pytgcalls.types`. Modern PyTgCalls (v2/v3) uses entirely different signatures.

## 5. Barebones Verification Script
If the bot still ignores messages, bypass the application's complexity. Write a minimal script to verify the token, network, and Telegram API aren't at fault.
```python
import os, logging
from pyrogram import Client, filters
logging.basicConfig(level=logging.INFO)
# Use a fresh session name to avoid locking main db
app = Client("logs/minimal_test", api_id=int(os.environ['TELEGRAM_API_ID']), api_hash=os.environ['TELEGRAM_API_HASH'], bot_token=os.environ['BOT_TOKEN'])
@app.on_message(filters.all)
async def hello(client, message):
    logging.info(f"Received: {message.text}")
app.run()
```
If the minimal script receives messages, the bug is 100% inside the main application's routing/filtering logic.

## 6. External API Rate Limits (Silent Crashes)
If command handlers trigger external API calls (e.g., Bstation/Cloudflare WAF) and fail to handle HTTP error codes gracefully, the framework handler may abort silently.
- **Symptom**: Handler starts, makes API call, but sends no reply and prints no traceback.
- **Action**: Verify the underlying API call directly in a REPL. For scraping WAFs (like Bstation), ensure `cookies.txt` (Netscape format) is loaded. A dummy cookie file stops `TypeError` on init but will still return HTTP `-509` (Rate Limited).