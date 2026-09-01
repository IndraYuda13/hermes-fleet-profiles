---
name: account-login-router
description: Route new account login requests on reseller Telethon flows to the best reseller screen by choosing the lowest session count from dup.py, skipping screens that are currently busy logging in, executing checklogin/login.py flow, asking the user for OTP/password when prompted, and restoring start4.py after login success. Use for login/add-account flows, not for generic restart work or session deletion.
---

# Account Login Router

Handle new account login across reseller screens with load balancing and busy-session checks.

## Environment

- Base dir: `~/MYvps/cust`
- Reseller folders and screens:
  - `reseller` -> screen `reseller1`
  - `reseller2` -> screen `reseller2`
  - `reseller3` -> screen `reseller3`
  - `reseller4` -> screen `reseller4`
  - `reseller5` -> screen `reseller5`

## Scope Guardrails

- Use this skill for new-account login/add-account flows only.
- If the request is generic restart/bootstrap/status work, prefer `manage-server`.
- If the request is session deletion/logout, prefer `session-cleanup`.

## Autoheal Rule

Before manual login-related operations on reseller screens, pause the `autoheal.sh` cron first to avoid race/interference. Restore it immediately after the login flow is complete.

The relevant cron entry is normally:

```cron
*/5 * * * * /root/MYvps/autoheal.sh >/dev/null 2>&1
```

## Required Flow

1. Run `python3 dup.py` (or `python3 dup.py <number>`) only at the beginning to read account count / location per reseller directory.
2. Rank reseller targets by the smallest account count.
3. For each candidate screen in order:
   - Check whether the screen is currently in login flow (busy) or available.
   - If busy, skip to the next candidate.
4. If all candidates are busy, report: queue full / all login sessions in use.
5. For the selected screen:
   - Stop runner with Ctrl+C.
   - Run `clear` then `python3 checklogin.py`.
   - Run `python3 login.py <phone>`.
6. During interactive login:
   - Ask the user for OTP code when prompted.
   - If code is rejected, inform the user and request a retry code.
   - If 2FA password is requested, ask the user and submit it.
7. On successful login:
   - Confirm success to the user.
   - Restart runner with `clear` then `python3 start4.py`.
   - Re-enable autoheal immediately after the manual flow is done.
8. Verify process resumed (`start4.py` and related `index.py` present`) and report final status.
9. Do not run extra `dup.py` confirmation again after success just for completion reporting.

## Busy Detection Heuristic

Treat the screen as busy if hardcopy/log tail shows active `login.py` prompt state (waiting OTP/password) or explicit login progress markers.

## Password Fallback Rule

When the user provides primary + fallback password policy:

1. Submit primary password first to all pending login sessions.
2. Re-check each screen prompt state.
3. If still asking password or marked invalid, submit fallback password.
4. If fallback also fails, report failed numbers and ask the user for a new password.

## Safety Rules

- Login only the number explicitly requested by the user.
- Never submit guessed OTP/password.
- Never stop unrelated screens outside reseller1..reseller5 unless asked.
- If uncertain about screen state, ask before forcing takeover.

## Response Style

- Start responses with a relaxed ("santai"), friendly acknowledgment.
- Keep updates short, simple, and sequential.
- Always state the selected reseller and why (lowest load + available).
- Always state final result: success, failed, or queue full.
- Do NOT use em dashes (—).
- Do NOT use formal/robotic phrasing.
