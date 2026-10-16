---
name: manage-server
description: Use when checking or restarting reseller daemon fleets. Inspect the live manager, preserve sessions, and verify every worker.
---

# Reseller Runtime Operations

## Ordered workflow

1. Establish scope: which existing instances to check/start/restart, protected services, and whether login/session/config changes are forbidden. A running instance is restarted only when requested; an inactive instance is started. Never touch unrelated personal daemons or create duplicate supervisors.
2. Discover live ownership before acting. Inspect `systemctl show` and `systemctl cat` for candidate units, `screen -ls`, process cwd/cgroups/interpreters, current cron entries, recent logs, disk and memory. Historical names and paths are hints, not authority. If systemd owns workers, use systemd rather than creating screen sessions.
3. Inspect launcher session enumeration and every prestart/login script. Record session filenames only as private input; derive expected worker identities using the launcher's actual filename rules. Identify deletions, config copies, authentication, and process kills before invoking a prestart. Do not run a login check as a routine restart step when session/config mutation is excluded.
4. Resolve prestart conflicts within the authorization boundary. If a narrowly scoped runtime-only bypass is authorized, use the reversible recipe in [systemd restart safety](references/systemd-restart-safety.md). Otherwise report the conflict and request a decision without stopping healthy services or silently editing units.
5. Pause only an exact, verified live autoheal entry that could interfere. Preserve its original content and restore it in `finally`. If none exists, do not change cron.
6. Start/restart sequentially under the current manager. Record each action's exact timestamp and exit code, then confirm running state and immediate worker inventory before advancing. On failure, stop the sequence, inspect the cause, and restore owned temporary changes. Never enter authentication codes, delete sessions, or alter application/config files to force a green result.
7. After the last startup, wait about 20–30 seconds and verify all instances again. Check fresh main PIDs, disappearance of old supervisor/worker PIDs, correct interpreter/cwd/cgroup, and one worker per expected session identity with no missing or duplicate identities. A supervisor being active does not prove workers are healthy.
8. Inspect journals since each exact action timestamp. Separate old-PID shutdown exceptions from new-PID startup/runtime errors. Report remaining rate limits or errors even when workers remain alive. Do not equate process inventory with end-to-end message delivery.
9. Restore temporary overrides and paused autoheal immediately in `finally`; read back exact restored configuration and final service states. Save sanitized evidence with commands, timestamps, exit codes, before/after PIDs, worker mappings/counts, restoration readbacks, and error classification.

## Screen-only and reboot paths

Use screens only when live evidence shows they own the instances. Resolve full screen names, stop the existing launcher gracefully, and start the inspected launcher with its intended interpreter and cwd. Do not blindly invoke `checklogin.py`. Create missing screens only for a specifically authorized screen-managed bootstrap and after confirming no systemd or orphan supervisor already owns those workers. Apply the same worker-level stabilization checks as for systemd.

## Evidence and privacy

- Map worker arguments against session stems internally; export stable account tags rather than phone numbers or session filenames.
- Sanitize logs before saving or sharing. Prefer exception classes, marker counts, and PID attribution; omit customer messages, credentials, and raw account identifiers.
- Distinguish runtime verification from application smoke verification. Flag SQLite/storage, auth, worker exits, and rate limits precisely; do not delete/relogin as an operational workaround.

## Reporting for this user

Give a quick acknowledgment for lengthy work, then a concise factual Indonesian result without em dashes. Use a per-instance table with before/after state, old/new main PID, session/expected/actual worker counts, and action. Include residual errors, rollback/restoration status, and the absolute sanitized evidence path. State partial completion honestly rather than calling the whole fleet healthy from supervisor state alone.
