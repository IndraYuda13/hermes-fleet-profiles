---
name: session-cleanup
description: Remove/logout specific WhatsApp bot session files in reseller directories on this server. Use when asked to delete one or more phone-number sessions safely, verify their locations with dup.py, remove the matching .session files, and confirm deletion results. Do not use for new-account login or generic restart tasks.
---

# Session Cleanup

Delete specific bot sessions safely and verifiably.

## Target Environment

- Base path: `~/MYvps/cust`
- Helper checker: `python3 dup.py <phone_number>`
- Session file pattern: `<folder>/session/<phone>.session`
- Common folders:
  - `reseller/session/`
  - `reseller2/session/`
  - `reseller3/session/`
  - `reseller4/session/`
  - `reseller5/session/`

## Scope Guardrails

- Use this skill only for explicit delete/logout session requests.
- If the request is about new login/add-account flow, prefer `account-login-router`.
- If the request is about restart/bootstrap/status, prefer `manage-server`.

## Autoheal Rule

Before manual logout/session-removal operations that affect reseller accounts, pause the `autoheal.sh` cron first to avoid race/interference. Restore it immediately after the cleanup is complete.

The relevant cron entry is normally:

```cron
*/5 * * * * /root/MYvps/autoheal.sh >/dev/null 2>&1
```

## Required Flow

1. For each requested number, run:
   - `python3 dup.py <number>`
2. Identify exact folder(s) that contain the account.
3. Before deleting, report a short deletion plan (number -> file path).
4. Delete matching `.session` file(s), `.session-journal`, and any associated `cf/cf<phone>.json` or `newcf/cf<phone>.json` files across reseller directories. If systemd services (e.g. `cust1`..`cust5`) are active, restart affected services post-cleanup so Telethon runners reload clean state.
5. Re-run `python3 dup.py <number>` to verify account is gone.
6. Restore autoheal immediately after the manual cleanup flow is done.
7. Return a compact result table: number, deleted path, verification status.

## Safety Rules

- Delete only numbers explicitly requested by the user.
- Never use wildcard deletes that can remove unrelated sessions.
- If a file is missing, report it and continue with others.
- If `dup.py` output conflicts with file existence, stop and ask.
- Never delete core scripts or non-session files.

## Useful Commands

```bash
cd ~/MYvps/cust
python3 dup.py +628xxxx
rm -f reseller*/session/+628xxxx.session* reseller*/cf/cf+628xxxx.json reseller*/newcf/cf+628xxxx.json
python3 dup.py +628xxxx
```

## Response Style

- Start responses with a relaxed ("santai"), friendly acknowledgment.
- Keep output factual and short.
- Include final verification per number: `deleted+verified`, `not found`, or `failed`.
- Do NOT use em dashes (—).
- Do NOT use formal/robotic phrasing.
