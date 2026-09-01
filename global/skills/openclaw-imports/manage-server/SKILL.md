---
name: manage-server
description: Manage recurring MYvps server operations for reseller bot screens, especially generic restart, bootstrap, and running-status verification for reseller1 to reseller5. Use for restart/start/check tasks. Do not use for new-account login routing or session deletion; those belong to account-login-router or session-cleanup.
---

# Manage Server

Execute recurring server operations consistently and safely.

## Scope Guardrails

- Use this skill for generic restart/bootstrap/status work on reseller bot screens.
- If the request is about adding/logging in a WhatsApp account, prefer `account-login-router`.
- If the request is about deleting/logging out a specific session file, prefer `session-cleanup`.
- Do not delete unrelated files or kill unrelated processes.

## Autoheal Rule

Before manual restart/login/logout-style operations that touch reseller flows, pause the `autoheal.sh` cron first to avoid race/interference. Restore it immediately after the operation is complete.

The relevant cron entry is normally:

```cron
*/5 * * * * /root/MYvps/autoheal.sh >/dev/null 2>&1
```

## Reseller Bot Restart Workflow

Use this when asked to restart reseller bots in screen sessions `reseller1` to `reseller5`.

1. Resolve full session names from `screen -ls` for `reseller1..reseller5`.
2. For each existing reseller session:
   - Send Ctrl+C (`\003`) to stop current script.
   - Run:
     - `clear`
     - `python3 checklogin.py`
3. If the user asks to start bots again, run:
   - `clear`
   - `python3 start4.py`
4. Re-enable autoheal immediately after the manual flow is done.

## Full Bootstrap After VPS Reboot

Use this when the user asks to start everything from zero after VPS restart.

1. Ensure screen sessions exist: `reseller1..reseller5`.
2. If missing, create them.
3. For each reseller screen:
   - `clear`
   - `python3 checklogin.py`
   - `clear`
   - `python3 start4.py`
4. Run health checks after 10-20 seconds:
   - confirm `start4.py` processes exist
   - confirm many `index.py` workers exist
   - check recent screen output for traceback/error lines
5. Return concise status per reseller: `ok`, `warning`, or `failed`.

## Verification Checklist

After restart/start, verify with process list:

- `python3 start4.py` exists for reseller flows
- multiple `python3 index.py +62...` worker processes are running
- missing sessions and recent errors are reported clearly

Suggested command:

```bash
ps -eo pid,cmd --sort=pid | grep -E "python3 (index\.py|start4\.py|checklogin\.py)" | grep -v grep
```

## Failure Handling

- If a reseller screen is missing, report it explicitly.
- If `checklogin.py` or `start4.py` fails, capture latest output via `screen -X hardcopy` and summarize the key error lines.
- If error indicates SQLite/session write issues, flag permission/storage problems clearly.
- Do not add extra `dup.py` verification for login completion flow here; that belongs to the login-specific workflow.

## Communication Style

- Start the response with a short acknowledgment (e.g. "Halo Boskuu! Ada yang bisa dibantu hari ini?") or a quick "ack" if a complex task is requested. For time-consuming tasks, acknowledge first so the user isn't confused, then work and deliver the final result later.
- Confirm exactly what was executed.
- Distinguish between:
  - restarted + checked login only
  - restarted + started bots
  - verified running status
- Keep it short, factual, clear, and relaxed ("santai").
- Do NOT use em dashes (—).
- Do NOT use formal/robotic phrasing.
- If checking LMS or using Playwright/browser tools, acknowledge and proceed with headless execution before reporting back.
