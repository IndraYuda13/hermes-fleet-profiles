# Phase 0–1 deployment runbook

This PR changes repository declarations only. Merging it does not rotate a
credential, rewrite Git history, restart Hermes or mutate the live fleet.

## Preconditions

- All dashboard and connector credentials found in repository history have been
  rotated by the owner.
- The replacement values exist only in the appropriate runtime `.env` files or
  secret manager.
- Every profile gateway is stopped before replacing configs.
- A recoverable backup of the live Hermes root exists.

Required dashboard values for externally bound dashboard profiles:

```dotenv
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=...
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH=...
HERMES_DASHBOARD_BASIC_AUTH_SECRET=...
```

Connector profiles also require their relevant variables, including
`FIRECRAWL_API_KEY` and `POSTMAN_API_KEY`.

GROUPBOT phone/chat allowlists are intentionally empty in Git. Restore the
approved numbers, group IDs and mention identifiers only in its runtime-local
config after `--replace-config`; never sync those identifiers back to Git.

## Staged deployment

```bash
git pull --ff-only
python3 -m pip install -r requirements-policy.txt
python3 scripts/sanitize_config.py --check profiles/*/config.yaml
python3 scripts/validate_fleet.py
./bootstrap.sh
```

Review the dry-run output. Then, with gateways stopped:

```bash
./bootstrap.sh --apply --replace-config
```

Restart the affected services and run:

```bash
hermes status --deep
```

## Acceptance checks

- All eleven A2A endpoints are healthy on ports 9901–9911.
- Every profile can call ORION and one non-ORION peer with a usable response.
- ORION has no terminal, file, browser, code-execution or delegation tool on
  Telegram, CLI or A2A surfaces.
- GROUPBOT exposes only web, vision and TTS; a terminal request is rejected.
- Automatic MOA and hidden delegation are disabled on every A2A profile.
- A Tier 0 request remains solo.
- A UI mission follows AURORA → FRAME → LENS and binds evidence to one revision.
- A deliberately stale verifier report cannot close the mission.
- A dangerous command triggers smart approval rather than auto-executing.

## Rollback

`bootstrap.sh` prints the exact recovery directory it created. Stop gateways,
restore the affected profile declarations from that directory, restart, then
repeat `hermes status --deep` and A2A smoke checks.

Do not use a forced Git reset as runtime rollback. Git state and live Hermes
state are separate recovery surfaces.

## Remaining owner-controlled containment

Current-tree cleanup is not history cleanup. After rotation and forensic backup,
rewrite the repository history using a reviewed replacement map, invalidate old
clones, and require fresh clones. This step is deliberately outside the PR
automation because it invalidates commit SHAs and affects every collaborator.
