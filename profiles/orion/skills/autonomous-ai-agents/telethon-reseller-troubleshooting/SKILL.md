---
name: telethon-reseller-troubleshooting
description: Diagnose Telethon reseller bot and broadcast failures.
---

# Telethon Reseller Troubleshooting & "Gak Nyebar" Diagnostics

Use this skill when investigating customer reports where Telethon broadcast accounts (`index.py` in `/root/cust/reseller1..5` under `cust2..5.service`) stop sending messages to LPM groups.

## Common Root Causes

1. **Config Emptied (`{}`) via Manual `/del`:**
   - Customer executed `/del 1` or `/del 2` in Saved Messages (`me`), clearing `cf/cf<phone>.json`.
   - Without active slots, the worker process idles and sends nothing.

2. **Stalled `/input` and `/text` Flow:**
   - When a customer starts `/input <slot> <expired> <delay>`, `progres<phone>.txt` is created.
   - If the worker process event loop drops or misses the subsequent `/text` reply, `progres.txt` remains orphaned and blocks subsequent inputs.
   - Fix: clean up `progres<phone>.txt` and write the slot configuration directly to `cf/cf<phone>.json` and `newcf/cf<phone>.json`.

3. **LPM Random Group Rotation (Apparent Non-Delivery):**
   - The broadcasting script picks up to 15 group dialogs, filters `unread_count >= 5`, runs `random.shuffle(valid_dialogs)`, and sends up to 5 messages per cycle.
   - Customers checking only one specific group link (e.g. `t.me/c/...`) may assume the bot is dead even when it actively broadcasts to other groups in that cycle.
   - Verify all group dialogs before declaring a broadcast failure.
   - Explain to the customer that the bot rotates dynamically through their joined LPMs and does not blast the exact same group repeatedly every minute.

4. **FloodWait from Frequent `/restart`:**
   - Repeated manual `/restart`, `/info`, or chat spam in Saved Messages triggers Telegram FloodWait (from ~500 seconds up to 12+ hours).
   - In `index.py`, FloodWait catches automatically put the worker to sleep and extend `expired` by the wait duration (`expired + e.seconds`).
   - Constant restarting during FloodWait resets or compounds the penalty.

5. **Customer Saved Messages (`me`) Audit Trail:**
   - Saved Messages contains the authoritative timestamped history of all bot interactions (`/del`, `/input`, `/text`, `/restart`, `/info`).
   - When a customer complains that messages aren't being sent, reading the last 20 messages in `me` immediately clarifies whether the customer recently deleted slots, entered wrong parameters, or caused a FloodWait cascade by spamming `/restart`.

6. **Python Environment & Telethon Version Mismatch:**
   - When testing or running `index.py` manually from terminal, NEVER use system `/usr/bin/python3`. System Python contains legacy Telethon (e.g. 1.25.1) which cannot unpack newer SQLite session tables, throwing:
     `ValueError: too many values to unpack (expected 5)`
   - ALWAYS run with the active Hermes virtualenv:
     `/usr/local/lib/hermes-agent/venv/bin/python3 index.py <phone>`
     or `source /usr/local/lib/hermes-agent/venv/bin/activate`.

7. **Encrypted Safe Backup for 49+ SQLite Sessions (GitHub Limitations):**
   - The `/root/cust` directory contains ~231 MB of sensitive SQLite `.session` files (auth keys) across `reseller1..5`.
   - Never commit raw `.session` files loose to git. Frequent commits of binary SQLite bloat the `.git` directory rapidly (>1 GB packfiles) and exceed free Git-LFS limits.
   - Best practice:
     1. Snapshot SQLite sessions via `sqlite3 "$src" ".backup '$dst'"` to avoid corruption during active write locks.
     2. Compress & client-side encrypt with `age` or `gpg` (AES-256): `age -p backup.tar.gz > backup.tar.gz.age`.
     3. Push to a private GitHub repo (`IndraYuda13/<repo>`) via GitHub Releases (`gh release create`) or a single-commit rolling orphan branch.
   - For complete backup script and restore commands, see `references/telethon-encrypted-backup-sop.md`.

## Safe Live Verification Workflow

Active workers hold SQLite file locks on `.session` files. Running ad-hoc Telethon scripts directly on `/root/cust/reseller*/session/<phone>.session` will cause `sqlite3.OperationalError: database is locked`.

Always inspect live sessions safely via a temporary copy:

```python
import asyncio, os, shutil
from telethon import TelegramClient

API_ID = 1141161
API_HASH = 'cea6e327693f3d9a366822f3b2b13bf2'

session_source = '/root/cust/reseller3/session/+6285936703501.session'
temp_session = '/tmp/test_inspect.session'
shutil.copy(session_source, temp_session)

async def inspect():
    client = TelegramClient(temp_session[:-8], API_ID, API_HASH)
    await client.connect()
    me = await client.get_me()
    
    # 1. Check SpamBot status
    async for m in client.iter_messages(178220800, limit=1):
        print('SpamBot:', m.text)
        
    # 2. Check recent broadcast messages across groups
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            async for m in client.iter_messages(dialog.entity, limit=10):
                if m.sender_id == me.id and m.message:
                    print(f'Sent in {dialog.name}: ID {m.id} at {m.date}')
    await client.disconnect()

asyncio.run(inspect())
if os.path.exists(temp_session):
    os.remove(temp_session)
```

## Service Restart & Process Management

### Systemd vs Screen Running Mode
- Standard daemon services: `cust1.service` through `cust5.service`.
- Screen manual interactive mode: When the user requests running manually inside `screen` rather than systemd:
  1. Stop and disable services to prevent dual-process conflicts:
     ```bash
     systemctl stop cust1 cust2 cust3 cust4 cust5
     systemctl disable cust1 cust2 cust3 cust4 cust5
     ```
  2. Spawn each reseller in a detached screen session:
     ```bash
     screen -dmS cust1 bash -c "cd /root/cust/reseller && /usr/local/lib/hermes-agent/venv/bin/python3 start4.py"
     screen -dmS cust2 bash -c "cd /root/cust/reseller2 && /usr/local/lib/hermes-agent/venv/bin/python3 start4.py"
     screen -dmS cust3 bash -c "cd /root/cust/reseller3 && /usr/local/lib/hermes-agent/venv/bin/python3 start4.py"
     screen -dmS cust4 bash -c "cd /root/cust/reseller4 && /usr/local/lib/hermes-agent/venv/bin/python3 start4.py"
     screen -dmS cust5 bash -c "cd /root/cust/reseller5 && /usr/local/lib/hermes-agent/venv/bin/python3 start4.py"
     ```
  3. Verify running screens and child processes:
     ```bash
     screen -ls
     ps aux | grep -E "start4\.py|index\.py \+62" | grep -v grep
     ```
- Attaching to screens: `screen -r cust1` (detach with `Ctrl + A` then `D`).
- Start script: `start4.py` spawns `python3 index.py <phone>` for each `.session` file in `session/`.
- Verify new PIDs:
  ```bash
  ps aux | grep -E "index\.py \+62" | grep -v grep
  ```
