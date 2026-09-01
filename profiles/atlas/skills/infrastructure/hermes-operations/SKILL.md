---
name: hermes-operations
description: Use when operating, safeguarding, or troubleshooting a Hermes installation's runtime state, backups, dashboard exposure, or memory storage.
version: 1.0.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [hermes, operations, backup, dashboard, memory, recovery]
    related_skills: [hermes-agent]
---

# Hermes Operations

## Overview

Use this umbrella for operational care of a Hermes installation: durable state, backup/restore, dashboard deployment, and storage limits. Read the main Hermes Agent skill for product configuration and commands; use this one when a runtime or data-management concern needs a concrete operational workflow.

## Model Context Limits & Custom Providers

When overriding context window lengths for local LLM proxies (such as 9router or local OpenAI-compatible endpoints) or custom providers in `~/.hermes/config.yaml`:

- **Default Fallback:** Hermes defaults unknown custom provider models to a **256k token** context length if `capabilities.contextWindow` is missing from the endpoint's `/v1/models` response.
- **Overriding Per-Model Limits:** Add explicit entries under `custom_providers.<name>.models.<model_id>.context_length` in `config.yaml`.
- **Global Override:** `model.context_length` sets the default maximum context window for the active main model if not specified per-model.
- **Editing Security-Sensitive Configs:** The file modification guard blocks raw tool `patch` or `write_file` edits to `~/.hermes/config.yaml`. Update values via `hermes config set <key> <val>` or execute Python/script YAML edits when configuring multi-level dictionary blocks like `custom_providers`.

## State and backup

Treat `$HERMES_HOME` (normally `~/.hermes`) as stateful application data. Back up skills, plugins, profiles, config, and selected session state using rsync, rclone, or a separate private Git staging repository. Exclude secrets, databases, logs, and volatile caches when their loss/size risk outweighs restoration value. Test a restore path before calling a backup reliable. See `references/hermes-agent-backup.md` and `references/automated-git-backups.md`.

## Network and Web Proxying

When the host uses a proxy and tools like `web_search` or `web_extract` need it, configure proxy settings at the environment level.

- **Environment variables:** Export `HTTP_PROXY` and `HTTPS_PROXY` (or their lowercase variants) in `~/.hermes/.env`. Python's urllib and the underlying tool HTTP clients will pick these up automatically.
- **Do not use unrecognized config keys:** Setting custom top-level keys like `network.http_proxy` in `~/.hermes/config.yaml` works as an environment bridge, but it generates warnings and is not the native path for the core web tools. Set it in `.env` directly.

## Dashboard exposure

Run a dashboard as a supervised service with a deliberate bind address and authentication boundary. When using a tunnel, verify local HTTP, DNS routing, public HTTP, and WebSocket/PTY behavior separately; host-header rewriting that enables a loopback HTTP origin may not satisfy a public-origin WebSocket. The tunnel umbrella and dashboard references contain the deployment-specific details.

## Memory and large documents

Declarative memory is an index for durable, concise facts—not a document vault. Keep long documents in files and read them on demand; maintain a compact index in memory that points to those files. Do not change an internal storage limit through broad source edits or config guessing. See `references/hermes-memory-limits.md`.

## Recovery checklist

- [ ] Identify the actual `$HERMES_HOME` and service/profile scope.
- [ ] Preserve a copy before destructive recovery or restore actions.
- [ ] Verify backup contents and restore to an isolated location first where practical.
- [ ] Confirm the process/service reaches a healthy state after configuration changes.
- [ ] Keep credentials out of Git logs, command output, and backup repositories.
