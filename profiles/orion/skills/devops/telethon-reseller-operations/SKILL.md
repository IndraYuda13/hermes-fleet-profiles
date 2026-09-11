---
name: telethon-reseller-operations
description: Operate & troubleshoot Telethon reseller daemons.
---

# Telethon Reseller Daemon Operations & Troubleshooting

Standard operating procedure for deploying, operating, diagnosing, and maintaining the 5 Telethon reseller instances (`reseller` through `reseller5`) and bot file shares (`share9`, `share10`) under Linux systemd or screen environments.

## 1. Service Mapping & Runtime Environment
- `cust1.service` -> `/root/cust/reseller/start4.py` (11 workers)
- `cust2.service` to `cust5.service` -> `/root/cust/reseller2..5/start4.py` (10 workers each)
- `share9.service` (`@Aulia66_bot`) and `share10.service` (`@Rendy13_bot`) -> `/mnt/MYvps_partial/sharefile9..10/indexnew.py`
- **Total Worker Target:** Exactly 51 running workers (`ps -ef | grep index.py | grep -v grep | wc -l`).
- **Python Environment Invariant:** Always execute with `/usr/local/lib/hermes-agent/venv/bin/python3`. Never execute with `/usr/bin/python3` (legacy 1.25.1 fails with `ValueError: too many values to unpack (expected 5)` on modern Telethon 1.44.0 SQLite sessions).

## 2. Common Failures & Diagnostic Invariants
- **Silent Worker Drop / Zombie Service:**
  - Child workers exit upon MTProto timeouts (`[Errno 110]`), but `start4.py` keeps running if at least one worker remains. Systemd reports `active (running)` while 80–90% of customer bots are dead.
  - Verification: Check task count in `systemctl status custX` (healthy units show Tasks: 21–23; Tasks: 5 indicates worker drop).
  - Remediation: `systemctl restart cust1 cust2 cust3 cust4 cust5`.
- **"Bot Gak Nyebar" Triage Protocol:**
  1. Check `state_{phone}.json` for `floodwait_active: true`.
  2. Inspect config `cf/cf{phone}.json` — customer may have cleared slots via `/del 1` or `/del 2`.
  3. Inspect Saved Messages (`me`) audit trail: reading the last 20 messages immediately proves whether the customer deleted configs, spammed `/restart`, or entered invalid inputs.
  4. Check SpamBot status: if muted by Telegram SpamBot, account has an account-level restriction, not a code defect.
  5. Clean orphaned `progres{phone}.txt`: if `/input` flow was interrupted, orphaned progress files block subsequent commands. Remove them and write config directly to `cf/`.
- **Safe Live Session Inspection:**
  - Running ad-hoc Telethon scripts directly on active `.session` files causes `sqlite3.OperationalError: database is locked`.
  - Always copy the session file to `/tmp/inspect.session` before running read-only inspection scripts.

## 3. FloodWait & Circuit Breaker Architecture
- Reject `/restart` and `/input` when `now < floodwait_until` to prevent Telegram from compounding the timeout penalty.
- `/info` queries during FloodWait must read local state JSON (zero MTProto RPC calls).
- Automatically extend customer slot expiry by the exact duration of the FloodWait penalty.

## 4. Encrypted GitHub Backup
- Maintain encrypted backups of all 51 `.session` SQLite databases in `IndraYuda13/cust-telethon-backup` using `sqlite3 .backup` snapshots and `age` asymmetric encryption. See `references/telethon-encrypted-backup-sop.md`.
