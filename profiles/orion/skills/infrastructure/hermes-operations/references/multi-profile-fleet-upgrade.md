# Multi-Profile Fleet Upgrade & Architecture V3 Migration Guide

## Overview

When upgrading a Hermes multi-profile fleet across multiple specialist profiles (e.g., ORION, FORGE, ATLAS, FRAME, LENS, SENTINEL, RADAR, PRISM, QUANT, NEXUS, AURORA):

## Conservative Upgrade SOP

1. **Staging & Isolation:**
   - Extract the upgrade bundle to an isolated directory (e.g., `/tmp/hermes_v3_stage/`).
   - Audit all documentation, SOUL files, routing descriptions in `profile.yaml`, and config patch YAMLs.

2. **Full Live State Backup:**
   - Create a timestamped backup before touching live configs:
     ```bash
     rsync -av --exclude=cache --exclude=sessions --exclude=audio_cache --exclude=image_cache --exclude="state.db*" /root/.hermes/profiles/ /root/.hermes/backups/fleet_pre_upgrade_<timestamp>/profiles/
     cp -a /root/.hermes/config.yaml /root/.hermes/auth.json /root/.hermes/.env /root/.hermes/backups/fleet_pre_upgrade_<timestamp>/
     ```

3. **Validation & Dry-Run Diff Inspection:**
   - Run bundle validators (`validate_bundle.py`).
   - Run installer in dry-run mode (`python3 apply_upgrade.py --root /root/.hermes/profiles`).
   - Verify 1-by-1 that primary models, providers, MCP servers, credentials, and custom tools are preserved.

4. **Deep-Merge Patch Application:**
   - Apply non-secret YAML patches using recursive dictionary merge (`merge(dst, patch)`) rather than wholesale file overwrites.
   - Replace role definition files (`SOUL.md` and `profile.yaml`).

5. **Post-Upgrade Integrity & Smoke Testing:**
   - Run `hermes config check --profile <name>` across all fleet profiles.
   - Test orchestrator isolation: verify orchestrator (e.g., ORION) possesses only orchestration toolsets (`kanban`, `memory`, `todo`, `clarify`, `session_search`, `skills`) and delegates implementation.
   - Validate high-concurrency profiles (e.g., LENS with `max_concurrent_children: 8`, FORGE/FRAME with `worktree_isolation: true`).
   - Test LENS route-manifest reconciliation closure: $\text{Missing} = \text{Discovered} - (\text{Tested} \cup \text{N/A} \cup \text{Blocked}) = \emptyset$.
