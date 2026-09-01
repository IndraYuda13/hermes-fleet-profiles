---
name: apple-app-automation
description: Use when working with Apple Notes, Reminders, Messages, or Find My from macOS and the user needs synced Apple-app data or controlled UI automation.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [apple, macos, notes, reminders, imessage, find-my, automation]
    related_skills: [obsidian, hermes-agent]
---

# Apple App Automation

## Overview

Apple apps are useful when the user needs their own iCloud-synced data. Their automation boundaries differ by app: use a supported CLI where available; use visible UI automation only for Find My; confirm before sending messages or creating reminders with meaningful dates.

## When to Use

- Creating, searching, editing, or exporting Apple Notes.
- Adding, listing, completing, or scheduling Apple Reminders.
- Reading or sending iMessages/SMS through Messages.app.
- Checking an owned device or AirTag in Find My.

Do not use this for agent-internal notes, gateway messaging, scheduled agent alerts, or tracking someone else’s property.

## Preflight

1. Confirm macOS, the relevant Apple app, and the required CLI or accessibility permission.
2. Confirm the signed-in Apple account has access to the requested data.
3. For any outgoing communication, reminder with a due date, deletion, or location lookup, confirm target and scope before acting.

## Apple Notes (`memo`)

Use `memo` for iCloud-synced Notes.app content:

```bash
memo notes -s 'query'             # search
memo notes -a 'Title'             # create
memo notes -e                     # interactive edit
memo notes -m                     # move to folder
memo notes -ex                    # export
```

Use Obsidian for Markdown-native vault work and Hermes memory for short agent-internal facts. Notes with attachments may not be editable by `memo`.

## Apple Reminders (`remindctl`)

Use Reminders for tasks that must appear on the user’s Apple devices:

```bash
remindctl today --json
remindctl add --title 'Call Mom' --list Personal --due '2026-05-15 14:00'
remindctl complete <id>
```

`--due` is the task deadline; `--alarm` is an optional earlier notification. Verify an early-nudge request with JSON because the UI can group items by alarm time. Agent-delivered reminders belong in the cron scheduler instead.

## Messages (`imsg`)

```bash
imsg chats --limit 10 --json
imsg history --chat-id <id> --limit 20 --json
imsg send --to '+15555550123' --text 'Message text' --service auto
```

Always confirm the recipient and exact outgoing content. Never use this for bulk or unknown-recipient messaging without explicit user approval. Verify an attachment path before sending it.

## Find My (visible UI automation)

Find My has no general CLI/API. Open the app, capture its visible window, and use vision/UI automation to read the user-owned device or item:

```bash
osascript -e 'tell application "FindMy" to activate'
sleep 3
screencapture -w -o /tmp/findmy.png
```

Keep the app foregrounded for repeated AirTag checks. Do not claim more precision or timeliness than the visible Find My result provides. Respect ownership and privacy boundaries.

## Common Pitfalls

- **Wrong destination:** “remind me” can mean an Apple Reminder or a Hermes cron alert—determine which is intended.
- **Insufficient permissions:** macOS Automation, Full Disk Access, Screen Recording, and Reminders permissions are app-specific.
- **Interactive commands:** use a PTY when the CLI prompts.
- **Unsafe sends or deletes:** confirm irreversible or externally visible actions first.
- **Overclaiming location:** Find My results depend on network updates and visible state; it is not a live tracking API.

## Verification Checklist

- [ ] Correct app, CLI, permissions, and iCloud account were confirmed.
- [ ] User-visible side effects were confirmed before execution.
- [ ] Structured CLI output or a visible UI result verified the operation.
- [ ] Messages, reminders, and locations were reported with only the approved scope.
