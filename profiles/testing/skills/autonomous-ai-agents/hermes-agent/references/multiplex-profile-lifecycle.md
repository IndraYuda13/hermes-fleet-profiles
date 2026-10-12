# Multiplexed gateway — profile & adapter lifecycle (live apply, bounce, park)

One host gateway serves many profiles (host mode is set in the DEFAULT home's gateway config; this host runs 14 served profiles in one process, PID shared). Everything below follows from that:

- **Never restart the shared gateway to apply a profile change** — a restart kills every served profile's in-flight turns. Bounce only the affected profile.
- Editing `profiles/<x>/config.yaml` or `.env` does NOT rebuild `<x>`'s already-live adapters (rescan trap, below).
- One bot credential = one polling profile: the gateway refuses a duplicate credential claim, and two processes with one token produce Telegram 409 conflicts.

## Control socket — the apply path

The gateway answers JSON verbs on `<default home>/gateway.sock`; query and lifecycle verbs use the same Python API:

```python
import sys; sys.path.insert(0, '/usr/local/lib/hermes-agent')   # the checkout in use
from pathlib import Path
from gateway.control_socket import (identify_gateway, request_unserve_profile,
                                    request_serve_profile_hot, rescan_gateway_profiles)

HOME = Path('/root/.hermes')         # the DEFAULT home that runs the gateway
identify_gateway(HOME)               # {'pid':…, 'served_profiles':[…], 'code_version':…} — ground truth
request_unserve_profile(HOME, 'x')   # tear down + unroute ONLY profile x
request_serve_profile_hot(HOME, 'x') # rebuild x's adapters from its CURRENT config/.env
```

Run with the checkout's venv python (`/usr/local/lib/hermes-agent/venv/bin/python`) and the checkout on `sys.path`. Ready-made: `scripts/multiplex_bounce_profile.py <profile> [gateway-home]` performs the full bounce with polling and prints the pid + served set before/after.

- Verb answers may be `{'pending': True, …}`: the socket handler is bounded at ~5s while teardown/connect keeps running. **Verify by polling `identify_gateway(HOME)['served_profiles']`** for the name to leave, then return — never by trusting one answer.
- `serve-profile` refuses a profile that is already served → the bounce is always unserve → (poll until absent) → serve → (poll until present).
- `rescan-profiles` is the reconcile the periodic watcher also runs: it hot-adds brand-new profiles but does NOT rebuild live adapters.
- A parked profile has a `gateway.parked` marker; `serve-profile` unparks. Parked = installed but not running.

## What a bounce actually does

Teardown per adapter: cancels the profile's background tasks (a wedged network task can log "background-task cancel timed out … forcing continue"), disconnects adapters, evicts the profile's cached agents, releases its `state.db` handles and log handlers. Rebuild: fresh config + secrets for that profile only, new adapters. Expected trail in the DEFAULT home's `logs/gateway.log`:

```
✓ telegram connected (profile: x)
[MULTIPLEX] Now serving profile 'x' (1 adapter(s) connected; control-socket)
```

Expected side effects a future session must warn about when the user asked for "apply without restart": pending text batches on the replaced adapter flush/drop, and an in-flight turn can end as "Transient agent failure … persisting user message so conversation context is preserved on retry" — the queued message stays queued and the new adapter delivers it. Do not bounce a profile whose turn is mid-flight unless the user accepts that turn ending.

## The rescan trap

`_profile_reconcile_watcher` rescans `profiles/` every ~30s (also on demand via `rescan-profiles`) and re-scans a profile whose `config.yaml`/`.env` signature changed — but `_start_one_profile_adapters` **skips platforms whose adapter is already live** ("never a second poller on the same bot"). So this log line is a no-op for the live adapter:

```
[MULTIPLEX] Re-scanned profile 'x' after config/.env change (0 adapter(s) connected)
```

`(0 adapter(s) connected)` = change noticed, running adapter kept the OLD config. This is the #1 false-positive diagnosis for "I changed the config and the bot still behaves the old way". `0 connected` is also normal when only non-credential keys changed — it is not proof of failure by itself, but for a TOUCHED profile it means the bounce is still required.

## Verifying after a bounce

1. Poll `identify_gateway(HOME)['served_profiles']` until the profile is back; the gateway `pid` must be unchanged (proves no restart happened).
2. DEFAULT home `logs/gateway.log`: fresh `✓ <platform> connected (profile: x)` appended.
3. `profiles/<x>/logs/gateway.log`: adapter re-registered (menus/commands), no new errors.
4. Functional proof: exercise the actual behavior — for a messaging bot, the user pings it and you read the new inbound line in `profiles/<x>/logs/gateway.log`. Config-level proof alone is not enough.

## Which profile owns this bot?

Token tails per profile (`for p in ~/.hermes/profiles/*/; do grep -h '^TELEGRAM_BOT_TOKEN=' "$p/.env" | tail -c6; done`) — identical tails = same bot identity across profiles. The LIVE owner is whichever profile's adapter the gateway shows connected (`✓ <platform> connected (profile: x)`); a silent bot often simply is not a member of the chat it is expected to answer in — verify membership from the bot's own token with `getChatMember` before touching config.
