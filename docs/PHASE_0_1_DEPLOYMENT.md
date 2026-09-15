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

Prefer the surgical role-policy overlay for an existing configured fleet. It
changes only policy-owned tool, MOA, delegation, approval and review fields;
runtime-owned providers, credentials, platform identifiers, plugins and skills
remain untouched.

First run its non-mutating plan while gateways are still online:

```bash
git pull --ff-only
python3 -m pip install -r requirements-policy.txt
python3 scripts/sanitize_config.py --check profiles/*/config.yaml
python3 scripts/validate_contracts.py
python3 scripts/validate_fleet.py
python3 scripts/deploy_role_policy.py --hermes-home "$HOME/.hermes"
```

`validate_contracts.py` is the narrow machine-contract check. It cross-checks
the role/runtime/workflow/gauntlet declarations, evidence-schema capabilities,
quality floors, remediation budget, manifest ownership, revision-parity set,
probe paths and viewport evidence without depending on exact prose. The broader
`validate_fleet.py` also runs these checks, so the standalone command is useful
when diagnosing contract drift in CI or during a governance edit.

Review the field-only plan. Stop every default/profile gateway. The apply mode
will refuse if any declared A2A port is still listening, then create a mode-0600
backup and automatically restore it on failure:

```bash
python3 scripts/deploy_role_policy.py \
  --hermes-home "$HOME/.hermes" \
  --apply
```

For a confirmed drift isolated to one or more profiles, use a targeted plan and
stop only those matching gateways. The deployer checks only the selected A2A
ports while preserving the same backup, atomic-write and verification behavior:

```bash
python3 scripts/deploy_role_policy.py \
  --hermes-home "$HOME/.hermes" \
  --profiles orion

# Stop hermes-gateway-orion.service, then repeat with --apply.
```

Use `./bootstrap.sh --apply --replace-config` only for a deliberate full config
replacement after every runtime environment value and GROUPBOT overlay is
prepared. It is not the normal upgrade path for an already configured fleet.

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
- Machine-readable quality contracts agree on release vetoes, acceptance floors,
  remediation limits and exact-revision proof requirements.
- Evidence fields required by the gauntlet exist with compatible types in the
  canonical evidence schema; workflow viewport requirements match capture widths.

## Rollback

The deployment command prints the exact recovery directory it created. Stop
gateways, restore each `PROFILE/config.yaml` from that directory, restart, then
repeat `hermes status --deep` and A2A smoke checks.

Do not use a forced Git reset as runtime rollback. Git state and live Hermes
state are separate recovery surfaces.

## Remaining owner-controlled containment

Current-tree cleanup is not history cleanup. After rotation and forensic backup,
rewrite the repository history using a reviewed replacement map, invalidate old
clones, and require fresh clones. This step is deliberately outside the PR
automation because it invalidates commit SHAs and affects every collaborator.
