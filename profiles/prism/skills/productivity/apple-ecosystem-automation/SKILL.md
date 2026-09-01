---
name: apple-ecosystem-automation
description: Use when interacting with Apple Notes, Reminders, Messages, or Find My from a macOS host.
version: 1.0.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [apple, macos, notes, reminders, imessage, find-my]
    related_skills: [obsidian]
---

# Apple Ecosystem Automation

## Overview

Use this umbrella for macOS-only personal-data actions through Apple apps and their local CLIs/UI automation. Confirm the destination, content, and side effects before creating reminders, sending messages, or exposing location data.

## Select the surface

| User need | Tooling | Key verification |
|---|---|---|
| Cross-device note | `memo` / Notes.app | Title, folder, and content are correct |
| Personal reminder on Apple devices | `remindctl` | List, due time, and optional alarm are distinct |
| Read or send iMessage/SMS | `imsg` / Messages.app | Recipient and exact message are explicitly approved |
| Locate an Apple device or AirTag | Find My UI + screenshot analysis | User owns/controls the item and visible location is read accurately |

## Notes

Use `memo notes` to list/search, `memo notes -a` to create, `-e` to edit, and `-ex` to export. Notes with attachments may not be editable through the CLI. Prefer an Obsidian workflow for Markdown-native vault work and the agent memory tool for internal facts.

## Reminders

Use `remindctl` for lists, due dates, and completion. `--due` is the due date/time; `--alarm` is the notification time and may intentionally be earlier. Confirm both before creation and use `--json` to verify stored `dueDate` and `alarmDate`. Do not substitute a personal reminder for a Hermes cron alert without confirming the intended channel.

## Messages

Use `imsg chats --json` and `imsg history --json` to resolve a known conversation. Before `imsg send`, confirm the recipient identity, transport if relevant (iMessage/SMS), exact text, and every attachment path. Never bulk-send or send to an unknown number without explicit approval.

## Find My

Find My has no general automation API. On macOS, open the app with AppleScript, capture the window, and use vision analysis to read the displayed location; use `peekaboo` if available for UI targeting. Keep the item view open when observing updates, respect privacy, and track only items the user owns or is authorized to locate.

## Platform and privacy guardrails

- These workflows require macOS, the relevant app/account, and local Automation/Full Disk Access/Screen Recording permissions as applicable.
- Do not attempt them from Linux, Windows, or a headless host; say the capability requires a configured Mac.
- Location and message sending are high-impact personal actions: confirm scope immediately before execution.
