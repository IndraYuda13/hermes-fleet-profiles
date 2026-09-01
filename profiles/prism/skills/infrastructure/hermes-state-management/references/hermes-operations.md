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

## State and backup

Treat `$HERMES_HOME` (normally `~/.hermes`) as stateful application data. Back up skills, plugins, profiles, config, and selected session state using rsync, rclone, or a separate private Git staging repository. Exclude secrets, databases, logs, and volatile caches when their loss/size risk outweighs restoration value. Test a restore path before calling a backup reliable. See `references/hermes-agent-backup.md` and `references/automated-git-backups.md`.

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
