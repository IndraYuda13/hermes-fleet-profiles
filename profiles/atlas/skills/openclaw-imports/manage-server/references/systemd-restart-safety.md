# Reversible systemd prestart bypass

Use only when explicitly authorized to suppress an unsafe prestart for a bounded restart while preserving permanent unit files and application/session/config files.

1. Snapshot `systemctl show UNIT -p ExecStartPre -p DropInPaths -p MainPID -p ActiveState -p SubState -p WorkingDirectory -p ExecStart -p ControlGroup` and inspect `systemctl cat UNIT`. Inventory existing drop-ins; never overwrite them.
2. Create a unique operation-owned file under `/run/systemd/system/UNIT.d/`, using exclusive creation. Its sole contents are:
   ```ini
   [Service]
   ExecStartPre=
   ```
   Choose a filename ordered after existing conflicting drop-ins, then prove the effective result rather than assuming precedence. Track every created file immediately for cleanup.
3. Run `systemctl daemon-reload`, then explicitly query `systemctl show UNIT --property=ExecStartPre --value`. Require successful command completion and an empty value before any restart. Multi-property `show` output can omit an empty execution property, even when requesting all properties; do not treat a missing dictionary key as failure or silently accept it. Query that property directly and retain the empty readout as evidence.
4. Record a timestamp immediately before each `systemctl restart UNIT` or `systemctl start UNIT`. Run units sequentially, checking running state and session-to-worker inventory after each action. Stop advancing if workers are missing, duplicated, or the unit is not running.
5. Allow 20–30 seconds of stabilization after the final startup. Verify fresh PIDs, old PIDs gone, interpreter/cwd/cgroups, and expected identities, not just equal counts.
6. In `finally`, unlink only operation-owned drop-in files and run `systemctl daemon-reload`, including after a failed preflight or action. Do not delete the entire drop-in directory or unrelated files.
7. Read back `ExecStartPre`, `DropInPaths`, and active/running state for every target. Require original effective prestart and drop-in paths to match the snapshot exactly. Removing an override alone is insufficient evidence of restoration.

## Journal attribution

Query `journalctl -u UNIT --since EXACT_ACTION_TIMESTAMP --no-pager -o json` and classify `MESSAGE` internally by `_PID`. Compare against the captured old supervisor/worker PID set. Shutdown `CancelledError` or tracebacks from old processes must not be reported as failures of newly started workers; still report new-process exceptions, rate limits, worker exits, and auth prompts. Export only sanitized classes/counts and PID attribution, not raw message bodies.

## Limits

The bypass prevents the inspected prestart from running; it does not prevent the application from performing its normal session database writes during startup. Do not promise byte-identical session contents. Restoring the original prestart means future automatic restarts may run it again; disclose that residual behavior when material to the requested safety boundary.
