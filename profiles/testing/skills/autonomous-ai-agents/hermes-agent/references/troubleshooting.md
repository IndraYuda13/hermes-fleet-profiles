# Troubleshooting

### Voice not working
1. Check `stt.enabled: true` in config.yaml
2. Verify provider: `python -c "import pm; pm.sync_venv(['stt-whisper'], explicit=True)"` or set API key
3. In gateway: `/restart`. In CLI: exit and relaunch.

### Tool not available
1. `hermes tools` — check if toolset is enabled for your platform
2. Some tools need env vars (check `.env`)
3. `/reset` after enabling tools

### Model/provider issues
1. `hermes doctor` — check config and dependencies
2. `hermes auth` — re-authenticate OAuth providers (or `hermes auth add <provider>`)
3. Check `.env` has the right API key
4. **Copilot 403**: `gh auth login` tokens do NOT work for Copilot API. You must use the Copilot-specific OAuth device code flow via `hermes model` → GitHub Copilot.

### Changes not taking effect
- **Tools/skills:** `/reset` starts a new session with updated toolset
- **Config changes:** In gateway: `/restart`. In CLI: exit and relaunch.
- **Code changes:** Restart the CLI or gateway process

### web_extract shows a stale page (result caching)
`web_search`/`web_extract` cache results for 20 minutes (PR #94618) — a
repeat fetch of the same URL within the TTL is served from cache, which
can look like "my website changes aren't showing up."

Automatic carveouts (always fetched live, never cached):
- localhost / 127.0.0.1 / `*.local` / `*.localhost` / single-label LAN
  hostnames / private + link-local IP ranges (dev servers, hot-reload
  builds, chat-GUI artifact previews)
- URLs matched by `security.website_blocklist`
- failed responses and keyless-rescue-served responses

Developing a site tested over the PUBLIC internet (Vercel/Netlify
preview, ngrok/cloudflared tunnel, staging domain)? Public DNS isn't
auto-carved-out — list the host in config.yaml:

```yaml
web:
  cache_exempt_hosts:      # always fetched live; effective immediately
    - mysite.vercel.app
    - "*.ngrok-free.app"
    - mysite.dev           # suffix match: also covers preview.mysite.dev
```

Blunt instruments: `web.cache_ttl_minutes: 1` (min) or
`web.cache_enabled: false` disables both caches entirely.

### Skills not showing
1. `hermes skills list` — verify installed
2. `hermes skills config` — check platform enablement
3. Load explicitly: `hermes -s name` (or the skill's own `/<name>` slash command)

### Gateway issues
Check logs first:
```bash
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail -20
```

Common gateway problems:
- **Gateway dies on SSH logout**: Enable linger: `sudo loginctl enable-linger $USER`
- **Gateway dies on WSL2 close**: WSL2 requires `systemd=true` in `/etc/wsl.conf` for systemd services to work. Without it, gateway falls back to `nohup` (dies when session closes).
- **Gateway crash loop**: Reset the failed state: `systemctl --user reset-failed hermes-gateway`

### Platform-specific issues
- **Discord bot silent**: Must enable **Message Content Intent** in Bot → Privileged Gateway Intents.
- **Slack bot only works in DMs**: Must subscribe to `message.channels` event. Without it, the bot ignores public channels.
- **Telegram bot silent in groups, no logs at all**: `allowed_chats` (non-empty) is a HARD gate for groups — messages from any other chat are dropped before logging, @mentions included, unless `guest_mode: true`; DMs are never filtered by it. `group_policy` is NOT read by the Telegram adapter (own-policy platforms only: WeCom/Weixin/QQBot/WhatsApp/Yuanbao). An unrecognised placeholder there (e.g. a fake `__dm_only__` value — not a real sentinel) silently blocks every group: unset it or list real chat IDs.
- **Telegram group bot receives nothing at all**: check membership with `getChatMember` — a non-member bot (`kicked` / `chat not found`) gets no updates (mentions never arrive); an admin bot receives all messages even with privacy mode on. The Bot API cannot add a bot to a group — `addChatMember` works for humans only and 404s for a bot that is not already a member: the user must add it from the Telegram app, then re-verify with `getChatMember`.
- **Telegram trigger gates, proven offline**: to show WHY a group message was dropped, call the adapter's real `_should_process_message` with the profile's resolved `extra` values — helpers live in the shipped tests (`from tests.gateway.test_telegram_group_gating import _make_adapter, _group_message, _mention_entity`, run under the checkout's venv). It returns processed/dropped with no traffic; a silent group drop writes nothing to the logs, so nothing else surfaces it.
- **A served profile's config/.env change does not reach its already-live adapters**: the multiplex signature watcher notices the edit within ~30s and logs `Re-scanned profile 'x' …`, but the rescan skips platforms whose adapter is already live (never a second poller on one bot) — `(0 adapter(s) connected)` means the old config is still in force. Apply by bouncing just that profile over the control socket (`unserve-profile` → `serve-profile`) — never by restarting the shared gateway; see `references/multiplex-profile-lifecycle.md`.
- **Windows-specific issues** (`Alt+Enter` newline, WinError 10106, UTF-8 BOM config, line endings): see `references/windows-quirks.md`.

### Auxiliary models not working
If `auxiliary` tasks (vision, compression, session_search) fail silently, the `auto` provider can't find a backend. Either set `OPENROUTER_API_KEY` or `GOOGLE_API_KEY`, or explicitly configure each auxiliary task's provider:
```bash
hermes config set auxiliary.vision.provider <your_provider>
hermes config set auxiliary.vision.model <model_name>
```

### "Reset permissions" / auto-approving everything
See `references/security-privacy.md` — wipe the "Always allow" stores, don't touch yolo mode.

