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
- `share9.service` -> `/mnt/MYvps_partial/sharefile9/indexnew.py` (Bot file share @Aulia66_bot)
- `share10.service` -> `/mnt/MYvps_partial/sharefile10/indexnew.py` (Bot file share @Rendy13_bot)

### Verifying Bot File Share Health (share9 / share10)
When user asks if `share9` or `share10` is dead or not responding:
1. Check service and PID: `systemctl status share9 share10`.
2. Inspect network socket to MTProto: `ss -tanp | grep -E "<PID_share9>|<PID_share10>"`. The status should be `ESTABLISHED` to Telegram DC (`91.108.56.x:443`).
3. If `journalctl -u shareX` is empty or rotated, check bot connection and recent updates directly via Telegram Bot API or Telethon:
   ```python
   import urllib.request, json
   # Check webhook & pending updates
   tok = json.load(open('/mnt/MYvps_partial/sharefile9/config.json'))['bot_token']
   info = json.loads(urllib.request.urlopen(f'https://api.telegram.org/bot{tok}/getWebhookInfo').read())
   updates = json.loads(urllib.request.urlopen(f'https://api.telegram.org/bot{tok}/getUpdates?offset=-5').read())
   ```
4. If process event loop appears stuck or sluggish after config updates, run a fresh restart: `systemctl restart share9 share10`.

**CRITICAL Python Environment:**
Always use `/usr/local/lib/hermes-agent/venv/bin/python3`.
Never execute with `/usr/bin/python3` (system Telethon is 1.25.1; it will fail with `ValueError: too many values to unpack (expected 5)` when reading SQLite `.session` files created by modern Telethon 1.44.0).
For manual shell runs:
```bash
source /usr/local/lib/hermes-agent/venv/bin/activate
python3 index.py +628xxx
```

## Common Customer Issues & Pitfalls
- **"Silent Worker Drop / Zombie Service" (Deceptive `active (running)`):**
  - In `start4.py`, child `index.py` workers run via `await process.wait()` without an auto-restart loop. When an account hits an MTProto connection drop (`[Errno 110] Connection timed out`, server closed connection, or DC reset), `index.py` exits cleanly.
  - Because `start4.py` remains running as long as at least one worker is still connected, systemd reports `custX.service` as `active (running)`, creating a zombie state where the service appears alive but 80–90% of customer bots are dead.
  - **Verification Rule:** NEVER rely solely on `systemctl status custX`. Always verify the total running worker count:
    `ps -ef | grep index.py | grep -v grep | wc -l` (must be exactly 51 total across the 5 instances: 11 in cust1, 10 each in cust2..5).
  - In `systemctl status custX`, healthy units show `Tasks: 21` (or 23 for cust1). A unit showing `Tasks: 5` has dropped all but 2 workers.
  - **Quick Remediation:** Run `systemctl restart cust1 cust2 cust3 cust4 cust5` to respawn all 51 workers cleanly.

- **"Bot Gak Nyebar":**
  1. Check if `state_{phone}.json` has `floodwait_active: true`.
  2. Check if config `cf/cf{phone}.json` was accidentally emptied by customer via `/del 1` and `/del 2`.
  3. Check if customer repeatedly spammed `/restart` in Saved Messages (`me`), which triggers Telegram's anti-flood penalty (can reach 10–13 hours).
  4. Check for Telegram SpamBot restrictions: if journalctl shows `Slot X forward error: You're banned from sending messages in supergroups/channels`, the account has been muted by Telegram SpamBot (account-level restriction, not a code defect).
- **Command Debounce & Outgoing Filter:**
  Commands sent by customer in Saved Messages (`me`) are intercepted by `@client.on(events.NewMessage(outgoing=True, chats="me"))`. A 3-second debounce is in place to prevent multiple responses when commands are rapidly clicked.
- **SQLite Database Lock & Telethon Wildcard Caution:**
  - Before running manual testing with `index.py`, ensure the corresponding `custX.service` (or screen) is stopped to avoid `sqlite3.OperationalError: database is locked`.
  - NEVER pass masked or wildcard strings (e.g. `+628****1234`) to Telethon or `index.py`; Telethon creates dummy SQLite `.session` files with literal asterisks in the session folder.

## Diagnostic & Inspection Commands
```bash
# Verify all 51 workers are running (11 in cust1, 10 in cust2-5)
ps -ef | grep index.py | grep -v grep | wc -l

# Service status & process tree (check Tasks count: 21-23 = normal, 5 = workers dropped)
systemctl status cust1 cust2 cust3 cust4 cust5

# Comprehensive audit probe: running status, FloodWait cooldown, and active paid slots
/usr/local/lib/hermes-agent/venv/bin/python3 -c "
import os, glob, json, time, psutil
running = {p.info['cmdline'][2]: p.info['pid'] for p in psutil.process_iter(['cmdline']) if p.info.get('cmdline') and len(p.info['cmdline']) >= 3 and 'index.py' in p.info['cmdline'][1]}
now = int(time.time())
for res in ['reseller', 'reseller2', 'reseller3', 'reseller4', 'reseller5']:
    base = f'/root/cust/{res}'
    for s in sorted(glob.glob(f'{base}/session/*.session')):
        ph = os.path.basename(s).replace('.session', '')
        cf_path, st_path = f'{base}/cf/cf{ph}.json', f'{base}/state_{ph}.json'
        slots = [f'Slot{k}({round((v.get(\"expired\",0)-now)/86400,1)}d)' for k, v in json.load(open(cf_path)).items() if v.get('expired', 0) > now] if os.path.exists(cf_path) else []
        fw = json.load(open(st_path)).get('floodwait_until', 0) - now if os.path.exists(st_path) and json.load(open(st_path)).get('floodwait_active') else 0
        print(f'{res} | {ph} | PID:{running.get(ph, \"DEAD\")} | FW:{fw}s | Slots:{len(slots)} {slots}')
"

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
