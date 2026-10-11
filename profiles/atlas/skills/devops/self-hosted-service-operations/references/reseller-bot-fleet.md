# Reseller Bot Fleet (cust1–cust5 systemd units)

Unit-level depth for the Telethon reseller bot fleet: `cust1.service`–`cust5.service` running `start4.py`, which spawns `index.py` Telethon workers. Routine restart/bootstrap/status checks are also covered by the manage-server skill.

## Unit template (ExecStartPre login cleanup)

```ini
[Service]
Type=simple
WorkingDirectory=/root/cust/reseller2
ExecStartPre=/usr/local/lib/hermes-agent/venv/bin/python3 /root/cust/reseller2/checklogin.py
ExecStart=/usr/local/lib/hermes-agent/venv/bin/python3 /root/cust/reseller2/start4.py
Restart=always
RestartSec=10
```

`ExecStartPre` runs `checklogin.py` so logged-out sessions are validated and cleaned before startup — on manual restarts and automatic crash recoveries alike.

## Failure modes

- Worker `index.py` exits while `start4.py` keeps running without re-spawning → empty/missing bot slots. Detect with `ps -ef | grep index.py` and verify `/proc/<pid>/cwd` points at the expected `/root/cust/resellerX`.
- `ExecStart` AND inner `asyncio.create_subprocess_exec` calls must both use the exact venv python; a generic `'python3'` in subprocesses causes C-extension/SQLite driver mismatches (e.g. Telethon `ValueError: too many values to unpack (expected 5)`).

## Restore

```bash
systemctl daemon-reload && systemctl restart cust1 cust2 cust3 cust4 cust5
```
