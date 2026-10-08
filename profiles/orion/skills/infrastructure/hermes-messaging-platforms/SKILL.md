---
name: hermes-messaging-platforms
description: Use when managing messaging gateways and platform toolsets.
version: 1.1.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [hermes, gateway, telegram, toolsets, permissions, voice, calling]
    related_skills: [hermes-operations, hermes-agent]
---

# Hermes Messaging Gateways & Platform Toolsets

## Overview
Use this skill when configuring messaging interfaces (Telegram, Discord, Slack, WhatsApp), user authorizations, platform-specific tool availability, and voice/audio interaction modes.

## Platform Toolsets Scoping
In Hermes Agent, tool availability is partitioned across runtime surfaces:
- `platform_toolsets.<platform>` in `config.yaml` (e.g. `telegram`, `cli`, `whatsapp`) defines the exact allowed toolsets for that interface.
- CLI commands like `hermes tools` target `platform_toolsets.cli` by default. They do NOT update messaging platforms unless the `--platform` flag is passed.
- When an explicit `platform_toolsets.<platform>` block exists, it overrides the top-level `toolsets:` list and drops any toolset not explicitly listed for that platform.

## Procedure to Enable & Inspect Platform Toolsets
Always use the native CLI `--platform` flag instead of hand-editing raw YAML or clobbering JSON array strings via `config set`. The CLI handles toolset filtering, preserves MCP entries, and reconciles `agent.disabled_toolsets` automatically.

1. **Inspect current toolset status per platform:**
   ```bash
   hermes -p <profile> tools list --platform <platform>
   ```
   *(e.g. `--platform telegram`, `--platform whatsapp`, `--platform cli`)*

2. **Enable or disable toolsets for a specific platform:**
   ```bash
   hermes -p <profile> tools enable <toolset> --platform <platform>
   hermes -p <profile> tools disable <toolset> --platform <platform>
   ```

3. **Verify cache invalidation (No gateway restart needed):**
   - Do NOT run `systemctl restart hermes-gateway` merely to apply toolset changes.
   - The Gateway runner computes `_agent_config_signature` by hashing `sorted(enabled_toolsets)` alongside the model and runtime config.
   - On the next user message, the gateway detects the configuration signature change, evicts the cached session agent, and compiles a fresh `AIAgent` with updated tool schemas dynamically without dropping active gateway connections or killing background processes.

## Voice, Audio & Real-time Calling Surface Boundaries
When configuring audio or real-time voice interaction, distinguish platform protocol limits from agent capabilities:

1. **Telegram & WhatsApp Gateways (Voice Note / Asynchronous Audio):**
   - **VoIP Call Limitation:** Telegram Bot API and WhatsApp Bot architectures (Baileys bridge / Meta Cloud API) do NOT provide inbound/outbound 1-on-1 VoIP call events to bot accounts. Do not attempt to configure phone/voice call handlers for bot tokens on these platforms.
   - **Supported Voice Workflow:** Half-duplex Voice Notes (walkie-talkie mode). The gateway receives incoming `.ogg` / `.opus` / voice audio, transcribes it via STT (`stt.provider`), and returns spoken audio via TTS (`tts.provider`) using `[[audio_as_voice]]`.
   - **Voice Reply Toggles:** Managed per-chat via `/voice on` (reply with voice only when user sends voice), `/voice tts` (always reply with voice), and `/voice off` (text only).

2. **Discord Gateway (Real-time Voice Channels):**
   - Discord bot adapter supports joining voice channels (VCs) directly.
   - **Requirements:** Bot requires `Connect`, `Speak`, and `Use Voice Activity` permissions (permission integer `309240908864`), along with `discord.py[voice]`, `PyNaCl`, and `libopus`.
   - **Behavior:** The bot joins the channel, detects active speech, transcribes, and streams audio replies into the voice room in real-time.

3. **Desktop & CLI Surfaces (Live Calling & Full Duplex):**
   - **Hermes Desktop (`hermes desktop`):** Supports live WebRTC voice mode, including full-duplex `gpt-live` mode (listening while speaking, barge-in interruption, delegating tool execution to background Hermes while continuing spoken commentary).
   - **CLI / TUI:** Supports continuous push-to-talk (`Ctrl+B`), VAD silence detection, and wake-word ("Hey Hermes") hands-free looping.

## Delegation Toolset (`delegate_task`) Mechanics
When enabling `delegation` for messaging platforms:
- **Toolset vs Tool:** Toolset is `delegation`; the registered tool is `delegate_task`.
- **Capabilities:** Allows the agent to spawn isolated subagents in the background up to `delegation.max_concurrent_children` (default 10), with live control actions (`list`, `steer`, `stop`).
- **Leaf vs Nested Agents:** Subagents default to `leaf` role (cannot call `delegate_task` or nested delegation). Nested spawning requires both `delegation.orchestrator_enabled: true` and `delegation.max_spawn_depth >= 2` in `config.yaml`.
- **Top-level Intercept:** Top-level delegations are automatically routed to background tasks with heartbeat and progress reporting; subagent orchestrators run synchronously to consume worker returns in-turn.

## User Authorization & Messaging Quirks
- **Allowlist Configuration:** When restricting access (`dm_policy: allowlist`), add user IDs to `platforms.telegram.allow_from` in `config.yaml` AND `TELEGRAM_ALLOWED_USERS` in `.env`. Unauthorized users are blocked with `[Telegram] Blocked unauthorized user: <id> (<name>) from DM`.
- **Pairing Store Sync:** Authorization also synchronizes with SQLite pairing store (`from gateway.pairing import PairingStore; ps = PairingStore(profile=profile_dir); ps._approve_user('telegram', user_id)`).
- **Graceful Gateway Reload:** If live listener adapters do not pick up newly allowed users immediately, reload via `systemctl --user reload hermes-gateway.service`. This sends `SIGUSR1` to the multiplexer process, draining in-flight turns gracefully before supervisor restart without dropping active connections abruptly.
- **Silent /start Commands:** Telegram `/start` commands are treated as silent platform pings and ignored by Hermes Gateway. Users must send a normal text message to start an active turn.

## Post-Reload Health Verification & Startup Lag Pitfall
When recovering or verifying gateway liveness after a restart or reload:
- **Interactive OAuth MCP Startup Stall:** If interactive OAuth MCP servers (e.g. Canva MCP) are configured in `config.yaml`, the gateway blocks startup waiting for external browser authorization until timing out (~60s CancelledError). Prune interactive OAuth MCPs from headless server configurations to prevent gateway polling startup lag.
- **Verification Oracles:** Verify recovery using concrete runtime indicators rather than guessing:
  1. `systemctl --user status hermes-gateway.service` — confirm status is `active (running)` with fresh uptime.
  2. Gateway log check (`~/.hermes/profiles/<profile>/logs/gateway.log`): confirm `[Telegram] Gateway running in polling mode` and WhatsApp bridge connection on port 3001.
  3. LLM provider check: confirm primary/local inference proxy endpoint is accepting completions.

## Multiplexed Profile Gateway Liveness Verification
In multi-profile Hermes setups with gateway multiplexing enabled:
- Satellite profiles (such as `testing`, `atlas`, `aurora`, `forge`, etc.) do not spawn independent gateway processes or write local `gateway.pid` files in their respective profile directories.
- Probing with `hermes -p <profile> gateway status` or querying `systemctl` / `ps` for a profile-specific gateway process will report "stopped" or false negatives even while the profile is actively receiving and dispatching messages.
- The accurate sources of truth for multiplexed profile liveness are:
  1. `hermes profile list` — uses `_served_by_running_multiplexer` to verify whether the profile is covered by the active root gateway multiplexer.
  2. Live multiplexer state in `~/.hermes/gateway_state.json` — verify that the profile is listed in `served_profiles` and check the adapter connection status under the `platforms` map (e.g. `"<profile>:telegram": {"state": "connected"}`).
