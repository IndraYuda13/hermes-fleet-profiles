---
name: hermes-profile-sharing
description: Package, sanitize, and share Hermes profiles with peers.
version: 1.0.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [hermes, profile, export, packaging, onboarding, migration]
    related_skills: [hermes-operations, hermes-agent]
---

# Hermes Profile Sharing & Peer Adoption

Use this skill when packaging, exporting, sanitizing, or sharing an existing Hermes Agent profile for another user or machine to adopt.

## Architecture Contract

When distributing a profile to a peer, the package must be self-contained, sanitized of all private session state and credentials, and ready for immediate onboarding:

1. **Root Directory Encapsulation:** Always archive with a top-level directory named after the profile (e.g. `testing/...`) so extracting with `unzip profile.zip -d ~/.hermes/profiles/` lands cleanly in `~/.hermes/profiles/<profile>/` without polluting the destination.
2. **Required Inclusions:**
   - `SOUL.md`: Persona and system prompt instructions.
   - `config.yaml`: Toolsets, plugins, permissions, and platform configurations.
   - `skills/`: Custom and bundled domain skills.
   - `assets/`: Avatars and media assets.
   - `bin/`: Standalone utilities required by the profile (e.g. `tirith`).
   - `.env.example`: Scaffolding template with empty/placeholder keys.
   - `README.md`: Concrete onboarding instructions.
3. **Mandatory Exclusions:**
   - Active secrets: Live `.env`, `auth.json`, and plaintext tokens.
   - Runtime databases: `state.db*`, `executions.db*`, SQLite WAL/SHM files.
   - Runtime locks & state: `.jobs.lock`, `.tick.lock`, `ticker_heartbeat`, `cron/output/`, `pairing/`, `terminal-sessions/`, `sessions/`.
   - Ephemeral caches: `home/`, `.cache/`, `cache/`, `audio_cache/`, `node_modules/`, `__pycache__/`, `.git/`, `.venv/`.

## Procedure

1. **Stage Clean Artifacts via Disk Script:**
   - Write a staging Python script to disk rather than executing multiline python strings in bash (avoids backtick/quote interpolation failures).
   - Copy non-volatile components (`SOUL.md`, `config.yaml`, `assets/`, `bin/`, `skills/`) into a clean scratch directory.

2. **Generate Onboarding Scaffolding:**
   - Generate `.env.example` documenting all expected LLM provider keys (`OPENROUTER_API_KEY`, `OPENAI_API_KEY`, etc.) and platform variables.
   - Generate `README.md` covering:
     1. Extraction command: `unzip <file>.zip -d ~/.hermes/profiles/`.
     2. Provider setup: Running `hermes -p <profile> model` or `setup` to bind to their own model endpoint.
     3. Setting environment variables: Copying `.env.example` to `.env`.
     4. Launching: `hermes -p <profile>`.

3. **Package & Verify the Archive:**
   - Create the zip archive with `zipfile.ZipFile` ensuring all archive paths are prefixed with the profile name.
   - Inspect archive contents to confirm entry count and verify no live `.db` or `.env` files leaked.

4. **Deliver with Media Syntax:**
   - Send the file via `MEDIA:/absolute/path/to/archive.zip` for instant delivery on chat interfaces.

## Pitfalls

- **Host-Bound Local Routes:** Source profiles often configure loopback proxies (e.g. `127.0.0.1:20128`) or personal platform allowlists (`platforms.telegram.allow_from`). The onboarding guide must mandate running `hermes -p <profile> model` and auditing platform settings before launching.
- **Inline Shell Script Expansion:** Passing multiline Python code containing markdown backticks inside bash `-c "..."` triggers subshell execution errors. Always write the packaging logic to a script file first.
- **Flat Zip Extraction Pollution:** Zipping without a root profile directory scatters hundreds of skill files directly into the extraction target. Always wrap entries in `<profile>/`.
