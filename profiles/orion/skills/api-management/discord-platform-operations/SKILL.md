---
name: discord-platform-operations
description: "Use when operating Discord servers or bot REST APIs."
version: 1.0.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    category: api-management
    tags: [discord, moderation, bot-api, rest-api, remote-control, guild-management]
    related_skills: [whatsapp-platform-operations, telegram-bot-development]
---

# Discord Platform Operations

## Architecture & Mode Selection

When interacting with Discord from Hermes Agent, distinguish two operational modes:
1. **On-Demand Remote Control (Direct REST API v10):**
   - Ideal when the user wants to execute actions directly from chat ("mau ngapain aja lewat sini") such as kick/ban members, send announcements, timeout users, create channels, or inspect server stats.
   - **No persistent daemon required.** Execute stateless HTTP requests via `httpx` or `curl` using the Bot Token. Fast, resilient, and zero background resource consumption.
2. **Persistent Gateway / Interactive Bot (`discord.py` / `discord.js`):**
   - Required only when listening for real-time inbound chat events, reactions, message interactions, slash commands inside Discord, or voice audio streaming.

## Required Credentials & Setup Checklist

To control a Discord server via REST API:
- `DISCORD_BOT_TOKEN`: From [Discord Developer Portal](https://discord.com/developers/applications) -> Bot tab -> Reset Token.
- `DISCORD_GUILD_ID`: Server ID (obtained via Discord Developer Mode -> Right-click server name -> Copy Server ID).
- **Privileged Gateway Intents:** Ensure **Server Members Intent** and **Message Content Intent** are enabled in Developer Portal if querying member lists or searching users.
- **Bot Permissions & Role Hierarchy:**
  - Bot must have required permissions (e.g. `KICK_MEMBERS`, `BAN_MEMBERS`, `MANAGE_MESSAGES`, `ADMINISTRATOR`).
  - **The Hierarchy Rule:** In Server Settings -> Roles, the Bot's role MUST be placed above the roles of any members it needs to moderate. Discord strictly forbids bots from kicking, banning, or muting members with equal or higher roles.

## Core REST Operations (On-Demand Execution)

Base URL: `https://discord.com/api/v10`  
Standard Headers:
```python
headers = {
    "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": "DiscordBot (HermesPlatform, 1.0)",
}
```

### 1. Moderation: Kick Member
- **Method / Endpoint:** `DELETE /guilds/{guild_id}/members/{user_id}`
- **Audit Reason:** Pass `X-Audit-Log-Reason: <encoded_reason>` in headers.
- **Python Snippet:**
  ```python
  import httpx, urllib.parse

  url = f"https://discord.com/api/v10/guilds/{guild_id}/members/{user_id}"
  req_headers = dict(headers)
  req_headers["X-Audit-Log-Reason"] = urllib.parse.quote(
      "Dikeluarkan via remote command"
  )
  resp = httpx.delete(url, headers=req_headers)
  # 204 No Content = Success
```

### 2. Moderation: Ban & Unban Member
- **Ban:** `PUT /guilds/{guild_id}/bans/{user_id}`
  Payload (JSON): `{"delete_message_seconds": 0}` (or up to 604800 for 7 days).
- **Unban:** `DELETE /guilds/{guild_id}/bans/{user_id}`

### 3. Moderation: Timeout / Mute Member
- **Endpoint:** `PATCH /guilds/{guild_id}/members/{user_id}`
- **Payload:** `{"communication_disabled_until": "2026-10-01T12:00:00Z"}` (ISO 8601 timestamp in the future; pass `None` to remove timeout).

### 4. Member Lookup & ID Resolution
Users rarely know raw Snowflake user IDs. Search by username or nickname:
- **Search Members:** `GET /guilds/{guild_id}/members/search?query={username}&limit=5`
- Returns list of member objects with `user.id`, `user.username`, `user.global_name`, and `nick`.

### 5. Messaging & Announcements
- **Send Message:** `POST /channels/{channel_id}/messages`
  Payload: `{"content": "Pengumuman...", "embeds": [...]}`
- **Delete Message:** `DELETE /channels/{channel_id}/messages/{message_id}`

### 6. Server Inspection
- **Get Guild Details:** `GET /guilds/{guild_id}` (retrieves name, owner_id, member counts, channels).
- **List Channels:** `GET /guilds/{guild_id}/channels` (retrieves channel names, IDs, types).

## Common Pitfalls & Invariants

1. **User Intent Disambiguation:**
   - When a user asks *"kamu bisa gak bikin bot discord yang bisa kick orang"*, do not immediately assume they want sample code for a standalone bot.
   - Clarify or identify if they want the assistant in this active chat to remote-control Discord on-demand.
2. **HTTP 403 Forbidden (Missing Permissions vs Role Hierarchy):**
   - HTTP 403 when kicking/banning almost always stems from the Bot's role being positioned below the target user's role in Discord's server settings, or attempting to act on the server owner.
   - Explain the Role Hierarchy clearly: move the Bot's role higher in Server Settings -> Roles.
3. **HTTP 401 Unauthorized:**
   - Bot token invalid, revoked, or prefixed incorrectly (must include `Bot ` prefix in `Authorization` header).
4. **Member Search Empty (Intent Missing):**
   - Searching members via API requires `Server Members Intent` enabled in Developer Portal. Without it, searches return 0 results or 403.
5. **Rate Limits (HTTP 429):**
   - Discord enforces per-route rate limits. Check response header `Retry-After` if making rapid sequential calls. For single on-demand user commands, rate limits are rarely an issue.
