---
name: telegram-pyrogram-bots
description: Patterns, pitfalls, and debugging workflows for Telegram bots built with Pyrogram and PyTgCalls.
---

# Telegram Bot Development (Pyrogram & PyTgCalls)

This skill covers systemic quirks, routing issues, and API behaviors specific to Pyrogram, PyTgCalls, and the Telegram Bot API that commonly cause "silent failures" or event loop crashes.

## 1. The `continue_propagation()` Trap
**Symptom:** Command handlers (`@app.on_message(filters.command(...))`) silently fail to trigger, but `getUpdates` shows the messages arriving.
**Root Cause:** A global logger or catch-all handler (`@app.on_message()`) registered before the command handlers is consuming the event. Even if it calls `message.continue_propagation()`, Pyrogram's router can drop the event if they are in the same dispatch group (default `group=0`).
**Fix:** Assign the global logger to a negative group (e.g., `group=-1`) so it runs first without interfering, or remove it entirely.
```python
@app.on_message(group=-1)
async def global_logger(client, message):
    # log stuff
    message.continue_propagation()
```

## 2. Supergroup Command Privacy (Silent Ignores)
**Symptom:** Bot responds in Private Messages (DM) but completely ignores commands in Groups/Supergroups.
**Root Cause:** Telegram's Bot API "Privacy Mode" is ENABLED by default. The bot will not receive group messages in its `getUpdates` payload unless:
1. It is explicitly mentioned (`/command@botname`).
2. It is given Admin privileges in the group.
3. Privacy Mode is turned OFF via `@BotFather`.
**Fix:** Before rewriting filters, test the bot in the group by explicitly tagging it (`/command@botname`). If it responds, the code is fine; the issue is Telegram's privacy settings.

## 3. Graceful Shutdown `RuntimeError`
**Symptom:** Stopping the bot (`await app.stop()`) throws `RuntimeError: Task ... attached to a different loop`.
**Root Cause:** Pyrogram's dispatcher workers sometimes outlive the main asyncio loop during tear-down, causing future attachment errors.
**Fix:** Wrap the shutdown sequence in a try-except block and suppress the specific runtime error. It is a known quirk in Pyrogram's teardown sequence.
```python
try:
    await app.stop()
except RuntimeError:
    pass # Pyrogram loop attachment bug during teardown
```

## 4. Mixing PyTgCalls with Aiogram
**Symptom:** Attempting to use `aiogram` for the bot router and `PyTgCalls` (which uses Pyrogram for the userbot) causes `ImportError: cannot import name 'GroupcallForbidden' from 'pyrogram.errors'` or asyncio loop conflicts.
**Root Cause:** `pytgcalls` is deeply coupled with Pyrogram's internal types and MTProto client. Using conflicting versions of Pyrogram required by `pytgcalls` alongside a different async router (`aiogram`) in the same process often leads to dependency hell.
**Fix:** If the project uses `PyTgCalls`, use `Pyrogram` for BOTH the Userbot and the standard Bot client to share the event loop and dependencies safely.

## 5. Stable Versions
* `py-tgcalls==2.2.12` was yanked from PyPI. Use `py-tgcalls==2.2.11` alongside `Pyrogram==2.0.106`.