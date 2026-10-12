#!/usr/bin/env python3
"""Per-thread CPU probe for an Android app over adb.

Usage:  probe_thread_cpu.py [serial] <package-or-pid> [seconds]

Finds every PID of the package, snapshots /proc/<pid>/task/*/stat (utime+stime
= fields 14+15) twice N seconds apart, and prints per-thread % of ONE core.
Android HZ is normally 100 -> ticks/second == % of one core; if the numbers
look absurd, verify HZ (`getconf CLK_TCK` on device) before reporting.

Use when a build "runs fine, then the system kills it" (ANR header shows no
culprit inside your lib, exit-info says EXCESSIVE CPU / am_kill says
`excessive cpu`), or whenever you need to name the burner thread before
building anything. A thread at 50-100% while the app should be idle is the
signal; a full-screen game on a 4-8 core phone is normally ~1.5-2 cores TOTAL.
"""
import subprocess
import sys
import time

argv = sys.argv[1:]
serial = None
if argv and ((':' in argv[0]) or argv[0].startswith('emulator-')):
    serial = argv.pop(0)
pkg = argv[0] if argv else None
dur = int(argv[1]) if len(argv) > 1 else 30
if not pkg:
    print(__doc__)
    sys.exit(2)


def sh(cmd, t=60):
    base = ['timeout', str(t), 'adb']
    if serial:
        base += ['-s', serial]
    base += ['shell', cmd]
    return subprocess.run(base, capture_output=True, text=True).stdout


pids = sh(f'pidof {pkg}').split() or ([pkg] if pkg.isdigit() else [])
if not pids:
    print('no process found for', pkg)
    sys.exit(1)
print('pids:', pids)


def snap_all():
    out = {}
    for pid in pids:
        vals, names = {}, {}
        listing = sh(f'ls /proc/{pid}/task/')
        tids = [t.strip() for t in listing.split() if t.strip().isdigit()]
        for tid in tids:
            st = sh(f'cat /proc/{pid}/task/{tid}/stat')
            cm = sh(f'cat /proc/{pid}/task/{tid}/comm').strip()
            r = st.rfind(')')          # comm may contain spaces/parens
            if r < 0:
                continue
            fields = st[r + 2:].split()
            try:
                vals[tid] = int(fields[11]) + int(fields[12])  # utime+stime
                names[tid] = cm
            except Exception:
                pass
        out[pid] = (vals, names)
    return out


s1 = snap_all()
t1 = time.time()
time.sleep(dur)
s2 = snap_all()
dt = time.time() - t1

rows = []
for pid in pids:
    d1, n1 = s1[pid]
    d2, _ = s2[pid]
    for tid, v in d2.items():
        if tid in d1 and v - d1[tid] > 0:
            rows.append(((v - d1[tid]) / dt, tid, pid, n1.get(tid, '')))
rows.sort(reverse=True)

print(f'== delta {dt:.0f}s -- % of ONE core (ticks/s at HZ=100) ==')
for rate, tid, pid, nm in rows[:25]:
    print(f'  {rate:6.1f}%  pid={pid} tid={tid:6s} {nm}')
print(f'  TOTAL ~{sum(r[0] for r in rows):.0f}% of one core')
