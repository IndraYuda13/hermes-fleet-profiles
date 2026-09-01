---
name: bstation-streaming-bot
description: Known pitfalls and fixes for Bstation/yt-dlp streaming bots on Telegram using PyTgCalls.
---

# Bstation Anime Streaming Bot (animeTGStream)

This skill tracks known issues for the `animeTGStream` repository (and similar yt-dlp + PyTgCalls Telegram stream bots).

## 1. PyTgCalls C++ Binding Conflicts
When migrating these bots to modern versions of Python, Pyrogram, or Aiogram, PyTgCalls can fail with fatal `ImportError` exceptions inside its C++ extensions (`ntgcalls`).
**Symptom:** Silent exits on start, or `ImportError: cannot import name 'InputMode' from 'ntgcalls'` / `cannot import name 'GroupcallForbidden' from 'pyrogram.errors'`.
**Fix:** 
- If sticking to Pyrogram 2.x, use `py-tgcalls==2.2.11` and `Pyrogram==2.0.106` (or `2.0.103`). 
- Do NOT arbitrarily upgrade to `3.0.0.devX` versions of `pytgcalls` without matching the underlying mtproto client framework, as the architecture changed significantly.
- If rewriting the bot router to Aiogram 3.x, you cannot trivially share the PyTgCalls instance with Aiogram if PyTgCalls was initialized using Pyrogram's `MtProtoClient`. Keep the Voice Chat engine strictly isolated in Pyrogram, and let Aiogram handle standard bot messages.

## 2. Ghost Global Loggers (Pyrogram)
If the bot runs but ignores all commands (and the Telegram offset advances), a bare `@app.on_message()` logger is likely swallowing the updates.
**Fix:** Delete the `global_bot_logger` entirely from the codebase, or explicitly assign it to `group=1` (though deletion is safer to guarantee command routing).

## 3. Supergroup Privacy Mode
Bot command filters like `filters.command("search")` may fail in Supergroups if the bot is not an admin.
**Fix:** Tag the bot explicitly (`/search@Animestrbot query`) or disable Privacy Mode in `@BotFather`. Do not assume the bot's code is broken if it answers DMs but ignores group text.