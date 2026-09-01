---
name: telethon-reseller-login
description: Manage Telethon reseller logins across multi-screen flows.
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags:
      - Telethon
      - Reseller
      - Telegram
      - Screen
---

# Telethon Reseller Login Management

Automate account checking, session cleanup, load-balanced multi-screen login, OTP/2FA handling, and runner restoration for Telegram Telethon reseller accounts.

## When to Use

- Log in new Telegram customer accounts via `login.py`.
- Run batch session integrity checks using `checklogin.py`.
- Clone or initialize reseller screen directories (`reseller1` to `reseller5`).
- Handle interactive OTP and 2FA password prompts across `cust1`..`cust5` screens.
- Restart process runners (`start4.py`) post-login.

## Prerequisites

- Python 3 with `telethon` package installed in environment.
- Linux `screen` utility installed.
- Repository structure at `/root/cust/reseller` (and `reseller2`..`reseller5`).
- GitHub authentication set up via `gh` CLI for repo extraction.

## How to Run

1. Clone or extract reseller folders via `terminal`.
2. Inspect or send commands to GNU `screen` sessions (`cust1`..`cust5`) via `terminal`.
3. Capture screen buffer using `screen -S custX -X hardcopy` and read output via `terminal` or `read_file`.

## Quick Reference

```bash
# Check session count per directory
ls /root/cust/reseller*/session/*.session | wc -l

# Run checklogin in screen
screen -S cust1 -X stuff $'cd /root/cust/reseller && python3 checklogin.py\n'

# Trigger login for a phone number
screen -S cust3 -X stuff $'python3 login.py +628xxx\n'

# Send OTP code or 2FA password into screen input
screen -S cust3 -X stuff $'12345\n'

# Start process runner after login success
screen -S cust3 -X stuff $'python3 start4.py\n'
```

## Procedure

1. **Setup & Extract Reseller Folders**
   - Extract `cust/resellerX` directories from `MYvps` tarball into `/root/cust/`.
   - Create detached screen sessions: `cust1` (`reseller`), `cust2` (`reseller2`), ..., `cust5` (`reseller5`).

2. **Session Cleanup & Status Check**
   - Kill active runners (`Ctrl+C` via `stuff $'\x03'`).
   - Run `python3 checklogin.py` in each screen to purge expired `.session` files.
   - Count active `.session` files per directory to select the screen with the lowest load.

3. **Account Login Flow**
   - Start login: `screen -S custX -X stuff $'python3 login.py +628xxx\n'`.
   - Read screen log to verify prompt: `screen -S custX -X hardcopy /tmp/screen_custX.log`.
   - When prompted for code, request OTP from user and send: `stuff $'OTP\n'`.
   - If 2FA password is required, prompt user and send: `stuff $'Password\n'`.
   - If user prefers manual 2FA entry, notify screen name (`custX`) and working path.

4. **Runner Restoration**
   - After success message ("Signed in successfully as ..."), launch runner: `stuff $'python3 start4.py\n'`.
   - Verify process status with `ps aux | grep start4.py`.

## Pitfalls

- **Telethon Code Timeout:** OTP codes expire quickly; capture and submit immediately.
- **2FA Capitalization:** 2FA passwords in Telethon are case-sensitive. Verify exact casing with user if login fails.
- **Stuck Screen Input:** If `login.py` hangs on previous input, send `Ctrl+C` twice before retrying `checklogin.py` or `login.py`.
- **Large Repository Archive:** `MYvps` archive is large (~640MB); extract target paths directly using Python `tarfile` module instead of full git clone to avoid timeouts.

## Verification

Check that `start4.py` is active across screens and the new `.session` file exists:

```bash
ps aux | grep start4.py && ls -la /root/cust/reseller*/session/+628*.session
```
