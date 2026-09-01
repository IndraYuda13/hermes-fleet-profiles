# Hermes Desktop Group Chat Architecture & Routing

## Overview
Hermes Desktop group chats coordinate multi-profile conversations within a single shared topic. This reference details how mentions are parsed, how turn order is determined, and loop termination rules.

## Mention Parsing (`parseGroupChatMentions`)
- Case-insensitive matching across member names, display titles, and stripped alphanumeric representations.
- `@all` and `@everyone` are parsed as identical broadcast tokens, triggering `everyone = true`.
- `@user` is ignored as an external client target.
- Individual `@<name>` mentions populate the active responder set for the subsequent round.

## Turn Scheduling & Rotation (`rotateGroupSpeakers`)
- Responders are executed sequentially in round-robin order.
- To prevent first-responder bias across multi-turn sessions, speaker order rotates each round via:
  `shift = round % members.length`
- Before executing a turn, new log entries are narrowed to the specific thread context via watermarks (`thread::memberKey`).

## Execution Caps & Lifecycle
- `GROUP_CHAT_MAX_ROUNDS = 10`: Maximum consecutive rounds per user trigger.
- `GROUP_CHAT_MAX_MESSAGES = 150`: Hard cap on total messages posted per user trigger.
- **Auto-Settling:** If all active responders return `(pass)`, the turn sequence terminates immediately.
