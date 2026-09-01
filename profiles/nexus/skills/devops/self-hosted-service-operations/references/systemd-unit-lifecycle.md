# Systemd unit lifecycle (VPS)

## When to use
- Failed units cluttering `systemctl --failed`
- User says services are unused and should be deleted
- Cleaning oneshot jobs wired to timers

## Inspect before delete
```bash
for s in unit1 unit2; do
  systemctl cat "$s.service" 2>&1 | head -40
  systemctl show "$s.service" -p FragmentPath -p UnitFileState --no-pager
done
ls /etc/systemd/system/*related-prefix* 2>/dev/null
systemctl list-timers --all --no-pager | rg -i 'related|prefix' || true
```

Note `WorkingDirectory` / `ExecStart` so you can report what was left on disk if only units are removed.

## Remove path (units only)
```bash
# enabled long-running units
systemctl disable --now a.service b.service c.service

# timer-triggered oneshot: kill timer + service
systemctl stop d.timer d.service 2>/dev/null
systemctl disable d.timer 2>/dev/null

rm -f /etc/systemd/system/{a,b,c,d}.service \
      /etc/systemd/system/d.timer \
      /etc/systemd/system/multi-user.target.wants/{a,b,c}.service \
      /etc/systemd/system/timers.target.wants/d.timer

systemctl daemon-reload
systemctl reset-failed
```

## Verify
```bash
systemctl --failed --no-pager
systemctl list-timers --all --no-pager | rg -i 'removed-name' || echo "(none)"
ls /etc/systemd/system/*removed-name* 2>&1 || true
```

## Pitfalls
- **Timer orphan:** delete `.service` without `.timer` → `UNIT not-found failed failed <name>.timer` still shows under `--failed`. Always remove both and `reset-failed`.
- **Static oneshot:** `UnitFileState=static` means no enable symlink; still stop any timer and `rm` the unit file.
- **Scope creep:** user "hapus service" ≠ hapus project tree. Keep data/code unless asked.
- **Sibling units:** same project may leave other timers/services (guard, stabilizer). List them; only remove what was named.
