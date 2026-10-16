---
name: hermes-profile-engineering
description: Use when authoring, porting, or sharing Hermes profiles.
version: 1.0.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [hermes, profile, prompt-adoption, packaging, soul-budget, sharing, migration]
    category: infrastructure
---

# Hermes Profile Engineering: Authoring, Adoption & Sharing

A class-level procedural skill for architecting, sizing, reverse-engineering, packaging, and sharing Hermes Agent profiles and system prompts.

---

## When to Use

Use this skill when:
1. Porting or reverse-engineering modular system prompts and agent skills from external AI agent codebases into Hermes profiles.
2. Calculating SOUL.md capacity limits and preventing silent prompt truncation.
3. Packaging and sanitizing Hermes profiles for distribution, backup, or peer adoption.
4. Structuring profile file trees, `.env.example` templates, and onboarding guides.

---

## 2. Profile Architecture & Tiered Prompt Model

When authoring or adopting complex agent configurations, structure into three distinct tiers:

1. **SOUL.md (Identity & Behavioral Core):**
   - Contains only the primary agent personality, instructions, lifecycle, tool-calling discipline, and posture.
   - Must follow native assembler order and fit strictly within the profile's dynamic context cap:
     $$\text{cap} = \max(20000, \min(\text{context\_length} \times 4 \times 0.06, 500000))$$
   - Exclude environment-contradicting sections (e.g. cloud sandbox paths on a local host) and route them to reference skills.

2. **Modular Skills (Execution Playbooks):**
   - Specialized procedural modules placed under `skills/<category>/<name>/SKILL.md`.
   - Every skill must have non-empty frontmatter with a trigger-first description under 57 characters.

3. **Archive / Reference Skills (`<agent>-prompt-archive`):**
   - On-demand reference skill preserving all conditional variants (alternate modes, postures, approvals), auxiliary prompts (summarization, vision, auto-review), and original source scripts.

---

## 3. Reverse-Engineering & Adopting External Prompts

1. **Audit & Extract Byte-Exact**:
   - Locate the core prompt assembler (e.g. `systemPrompt` or builder function).
   - Parse template literals and multiline strings preserving verbatim contents. Enable multiline regex (`re.DOTALL`) to prevent dropping lines across backslash continuations (`\␊`) and escaped quotes (`\"`, `\'`).
2. **Resolve Interpolations Deterministically**:
   - Replace `${variable}` tokens with target profile parameters rather than leaving broken template strings.
3. **Verify Post-Adoption Capacity**:
   - Run `hermes -p <profile> prompt-size --json` to verify clean parsing, system prompt byte deltas, and enabled skill counts.
   - Verify skill discovery with `hermes -p <profile> skills list`.
   - Ensure a pre-adoption backup of SOUL exists in `<profile>/backups/`.

---

## 4. Profile Packaging, Sanitization & Peer Sharing

When exporting a profile for peer or machine migration:

1. **Native CLI Export vs Clean Sharing Archive**:
   - `hermes profile export <profile> [-o output.tar.gz]` creates an official `.tar.gz` archive and automatically excludes credentials (`.env`, `auth.json`). However, for a *named profile*, it includes `state.db*`, `sessions/`, `logs/`, and caches, which can bloat the archive (20MB+) and leak conversation history.
   - For peer adoption or distribution without chat history, construct a clean package containing only static assets and configuration: `SOUL.md`, `config.yaml`, `skills/`, `assets/`, `bin/`, `.env.example`, and a tailored `README.md`.

2. **Root Directory Encapsulation**:
   - Always archive with a top-level directory named after the profile (e.g. `<profile>/...`) so extracting via `unzip profile.zip -d ~/.hermes/profiles/` lands cleanly without polluting the root.

3. **Mandatory Inclusions**:
   - `SOUL.md`, `config.yaml`, `skills/`, `assets/`, `bin/`, `.env.example`, `README.md`.

4. **Mandatory Exclusions**:
   - Active secrets: `.env`, `auth.json`, plaintext tokens.
   - Runtime databases: `state.db*`, `executions.db*`, SQLite WAL/SHM files.
   - Locks and state: `.jobs.lock`, `.tick.lock`, `ticker_heartbeat`, `cron/output/`, `pairing/`, `terminal-sessions/`, `sessions/`.
   - Dynamic caches: `home/`, `.cache/`, `cache/`, `audio_cache/`, `node_modules/`, `__pycache__/`, `.git/`, `.venv/`.

5. **Staging & Verification**:
   - Write a staging script to disk rather than executing multiline python strings in bash (avoids backtick/quote interpolation errors).
   - Inspect the generated archive to confirm entry count and verify zero `.env` or `.db` leaks.
   - Deliver via `MEDIA:/path/to/archive.zip` for instant chat downloads.

6. Recipient Adoption Checklist:
   - Extract: `unzip profile.zip -d ~/.hermes/profiles/` (or `hermes profile import <archive>` for `.tar.gz`).
   - Configure model: `hermes -p <profile> model` (or `setup` wizard) to replace host-specific local router endpoints with active API providers.
   - Environment: `cp ~/.hermes/profiles/<profile>/.env.example ~/.hermes/profiles/<profile>/.env` and populate API keys.
   - Gateway/Platform check: audit `config.yaml` to ensure platform bots (e.g. Telegram `allow_from`) are either disabled or updated to the recipient's user ID.

---

## 5. Multi-Profile & Multi-Agent Skill Sharing Architecture

In multi-agent fleets (multiple profiles under `~/.hermes/profiles/`), duplicating hundreds of skill directories across each profile creates storage bloat, cache invalidation churn, and sync drift. Hermes provides three native sharing tiers:

1. **Native External Skill Directories (`skills.external_dirs`):**
   - Point each profile's `config.yaml` to shared skill repositories:
     ```yaml
     skills:
       external_dirs:
         - ~/.hermes/skills
         - /root/projects/hermes-fleet-profiles/global/skills
     ```
   - All external skills are automatically indexed, searchable via `skills_list`, loadable via `skill_view`, and available as `/skill-name` commands.
   - Resolution precedence: `project -> local profile -> skills.create_dir -> skills.external_dirs`.

2. **Centralized Skill Creation Hub (`skills.create_dir`):**
   - Configure a shared directory so new agent-authored skills immediately become visible fleet-wide:
     ```yaml
     skills:
       create_dir: /root/.hermes/skills
       external_dirs:
         - /root/.hermes/skills
     ```
   - Agent instructions and tool prompts dynamically render the target creation path, ensuring new procedures land in the shared hub.

3. **Selective Symlinks (`followlinks=True`):**
   - Hermes scans skill directories with `os.walk(followlinks=True)` and verifies `os.path.realpath`.
   - Symlinking specific category folders or individual skill directories into `~/.hermes/profiles/<profile>/skills/` works without warnings or duplicate hashing.

---

## 6. Custom Endpoints: Context Window & Native Vision Overrides

When connecting profiles to local routers (e.g. 9router), proxies, or custom OpenAI-compatible endpoints with large numbers of models:

1. **Two-Tier Context Window Overrides:**
   - **Tier 1 (Explicit per-model override):** `model_overrides.<provider>.<model_id>.context_window` is evaluated in step 0b of `get_model_context_length` (`_override_context_window`). Explicit matches always win over catalog defaults and probes.
   - **Tier 2 (Provider entry fallback):** Setting `context_length: N` at the provider entry level in `custom_providers[]` or `providers.<name>` acts as a blanket fallback in step 0c (`get_custom_provider_context_length`). Unlisted models dynamically added by the endpoint inherit this fallback context.

2. **Native Vision Enforcement:**
   - Set `model.supports_vision: true` at the top level of `config.yaml` so `_supports_vision_override` immediately returns true for the active model.
   - Set `agent.image_input_mode: native` so `decide_image_input_mode` unconditionally routes image attachments directly as native `image_url` parts without lossy OCR or text description fallback.
   - Populate `supports_vision: true` on each model entry under `model_overrides.<provider>.<model_id>` to patch models.dev input modalities.

---

## 7. Pitfalls & Anti-Patterns

- **Custom Endpoint Context Override Precedence**: Setting `_default` under `model_overrides.<provider>` is a fill-gap fallback that applies only on models.dev catalog misses. Early resolution (`_override_context_window`) checks explicit model entries only and skips `_default`. To blanket override context tokens for all models served by a custom router, define explicit entries under `model_overrides.<provider>.<model_id>` and set entry-level `context_length` on the provider definition.
- **Auxiliary Vision Detour in Auto Mode**: Having an explicit `auxiliary.vision` backend configured in `config.yaml` causes `_explicit_aux_vision_override` to detour images to text description when `image_input_mode` is `auto`. Always set `agent.image_input_mode: native` when all endpoint models support native vision.
- **Multi-Profile Skill Duplication Bloat**: Physically copying shared skills into every profile directory wastes disk space and causes silent drift when one agent patches a procedure. Use `skills.external_dirs` pointing to a central directory (`~/.hermes/skills` or fleet repo) instead.
- **Skill Shadow Precedence Confusion**: Precedence is deterministic: `project -> local profile (~/.hermes/skills/) -> skills.create_dir -> external_dirs`. If a local copy exists with the same name, it shadows the external version across all tools and slash commands.
- **Silent Truncation by Cap**: Writing a SOUL.md larger than Hermes's dynamic cap triggers silent head/tail truncation during session initialization. Keep SOUL under $\max(20\text{K}, \min(\text{ctx} \times 4 \times 0.06, 500\text{K}))$.
- **Multiline Regex Continuation Truncation**: Scanners without `re.DOTALL` truncate multiline template literals at the first newline or backslash, silently dropping prompt sections. Always assert resolved lengths against source spans.
- **Flat Zip Extraction Pollution**: Zipping without a root profile directory scatters hundreds of skill files directly into the extraction target. Always wrap entries in `<profile>/`.
- **Red-Flag Keyword Density in SOUL**: Concentrating high-risk terms (`shellcode`, `exploit payloads`, `C2`, `malware`) in SOUL.md increases the prompt's moderation risk score across every turn, triggering provider API blocks even on benign follow-ups. Frame capabilities in factual technical terms.
- **Competing Instructions Cause Safety Fallback**: Mixing safety limits with absolute refusal suppression commands causes model attention to resolve contradictions by falling back to conservative safety behavior. Keep posture directives unified.
- **Host-Bound Local Routes in Shared Profiles**: Exported profiles often configure loopback proxies (`127.0.0.1:20128`) or personal platform allowlists. The onboarding guide must mandate auditing platform settings and running `hermes -p <profile> model` before launching.
