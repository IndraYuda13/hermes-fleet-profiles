---
name: telethon-reseller-daemon-operations
description: Operate Telethon reseller services and session backups.
---

# Telethon Reseller Daemon Operations

Operate, troubleshoot, and maintain the 5 Telethon reseller instances (`reseller` s/d `reseller5`) running under Linux systemd services.

## Service Mapping & Runtime Environment
- `cust1.service` -> `/root/cust/reseller/start4.py`
- `cust2.service` -> `/root/cust/reseller2/start4.py`
- `cust3.service` -> `/root/cust/reseller3/start4.py`
- `cust4.service` -> `/root/cust/reseller4/start4.py`
- `cust5.service` -> `/root/cust/reseller5/start4.py`

**CRITICAL Python Environment:**
Always use `/usr/local/lib/hermes-agent/venv/bin/python3`.
Never execute with `/usr/bin/python3` (system Telethon is 1.25.1; it will fail with `ValueError: too many values to unpack (expected 5)` when reading SQLite `.session` files created by modern Telethon 1.44.0).
For manual shell runs:
```bash
source /usr/local/lib/hermes-agent/venv/bin/activate
python3 index.py +628xxx
```

## Common Customer Issues & Pitfalls
- **"Bot Gak Nyebar":**
  1. Check if `state_{phone}.json` has `floodwait_active: true`.
  2. Check if config `cf/cf{phone}.json` was accidentally emptied by customer via `/del 1` and `/del 2`.
  3. Check if customer repeatedly spammed `/restart` in Saved Messages (`me`), which triggers Telegram's anti-flood penalty (can reach 10–13 hours).
- **Command Debounce & Outgoing Filter:**
  Commands sent by customer in Saved Messages (`me`) are intercepted by `@client.on(events.NewMessage(outgoing=True, chats="me"))`. A 3-second debounce is in place to prevent multiple responses when commands are rapidly clicked.
- **SQLite Database Lock:**
  Before running manual testing with `index.py`, ensure the corresponding `custX.service` (or screen) is stopped to avoid `sqlite3.OperationalError: database is locked`.

## Diagnostic & Inspection Commands
```bash
# Service status & process tree
systemctl status cust1 cust2 cust3 cust4 cust5

# Live streaming logs per phone or event
journalctl -u custX -f
journalctl -u custX | grep -E "FLOODWAIT|Terkirim" | tail -n 20
```

## Adding Customer Account & Interactive Login Flow
To log in a new customer account under Hermes:
1. Identify the slot directory (`reseller` to `reseller5`) with the lowest active session count (`ls session/*.session | wc -l`).
2. Run `login.py` in background with PTY enabled:
   `terminal(command="/usr/local/lib/hermes-agent/venv/bin/python3 login.py +628xxx", workdir="/root/cust/resellerX", background=True, pty=True)`
3. Monitor prompt using `process_manage(action='log', session_id=...)` until `"Please enter the code you received:"` appears.
4. When user provides OTP or 2FA password, submit via `process_manage(action='submit', session_id=..., data='<CODE>')`.
5. If user requests a **reseller unique code** ("kode unik N hari/minggu"):
   - Hitung timestamp Unix epoch: `int(time.time()) + (N * 86400)`.
   - Contoh 1 minggu = 7 hari = `now + 604800` (format 10 digit epoch).
6. Jika login butuh kirim ulang kode (resend), kill session aktif via `process_manage(action='kill', session_id=...)` lalu jalankan ulang perintah login baru.
7. **Mengecek Pesan Masuk / Kode Login Baru Telegram (777000):**
   Jika user/pelanggan menanyakan apakah ada kode OTP/login masuk yang baru ke akun yang sudah login di daemon:
   - Gunakan Telethon client one-off di venv Hermes (`/usr/local/lib/hermes-agent/venv/bin/python3`) membaca chat ID `777000` (Telegram Service Notifications).
   - Jalankan script singkat:
     ```python
     from telethon import TelegramClient
     import asyncio

     async def get_otp():
         client = TelegramClient('/root/cust/resellerX/session/+628xxx.session', 1141161, 'cea6e327693f3d9a366822f3b2b13bf2')
         await client.connect()
         msgs = await client.get_messages(777000, limit=3)
         for m in msgs:
             print(f"[{m.date}] ID {m.id}: {m.text}")
         await client.disconnect()

     asyncio.run(get_otp())
     ```
   - Laporkan kode login, waktu masuk (konversi ke WIB), dan isi pesan secara presisi ke user.

## FloodWait & Circuit Breaker Architecture
1. **State Persistence:**
   Each account stores runtime state in `state_{phone}.json` (`last_sent_timestamp`, `last_sent_group_title`, `floodwait_active`, `floodwait_until`, `floodwait_seconds`).
2. **Circuit Breaker on `/restart` & `/input`:**
   When `now < floodwait_until`, customer `/restart` and `/input` commands are safely rejected with cooldown countdown to prevent Telegram from doubling the penalty.
3. **Zero-RPC `/info`:**
   During FloodWait, `/info` does NOT call `client.get_messages("me")`. It reads local state and config to report cooldown status, countdown, and expiry compensation.
4. **Auto-Compensation:**
   Customer slot expiry is automatically extended by the exact duration of the FloodWait penalty.

## Encrypted Private GitHub Backup
All 51 Telethon SQLite `.session` files (~237 MB) are backed up securely in private repo `IndraYuda13/cust-telethon-backup`:
- Backup script: `/mnt/cust-telethon-backup/scripts/backup.sh` (uses `sqlite3 .backup` + `age` asymmetric encryption with SSH Ed25519 key).
- Restore script: `/mnt/cust-telethon-backup/scripts/restore.sh`.
- Run backup: `bash /mnt/cust-telethon-backup/scripts/backup.sh`.
- If the script times out during GitHub push, finish with manual push in `/mnt/cust-telethon-backup`: `git push origin main`.
