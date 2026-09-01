---
name: composio-automation
description: Use when automating SaaS tools via Composio.
version: 1.0.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [composio, integrations, tools, oauth, automation, cli]
    related_skills: [n8n-workflow-automation, google-workspace-automation]
---

# Composio Automation & Tool Integration

## When to Use
Use this skill when:
- Connecting or authenticating AI agents with external SaaS services (GitHub, Google Workspace, Slack, Linear, Notion, etc.) using Composio.
- Searching for specific tool actions (`composio search`) or executing external APIs directly (`composio execute`, `composio proxy`).
- Automating workflows across multiple apps with managed OAuth credentials without writing custom auth boilerplate.

## Overview

Composio enables AI agents to connect to and interact with 1000+ SaaS applications and toolkits (GitHub, Google Workspace, Slack, Linear, Notion, Jira, etc.) with managed OAuth authentication, dynamic tool execution, and direct API proxying.

Binary location: `~/.local/bin/composio` (installed bundle at `~/.composio/composio`).

---

## 1. Installation & Authentication Lifecycle

### Installation
```bash
curl -fsSL https://composio.dev/install | sh
export PATH="$HOME/.local/bin:$PATH"
```

### Headless Agent Login Pattern
1. Generate login URL:
   ```bash
   composio login
   ```
   This outputs a dashboard URL containing `cliKey` (e.g. `https://dashboard.composio.dev/?cliKey=...`).
2. Provide the URL to the user to authenticate in browser.
3. Concurrently start background polling:
   ```bash
   composio login --poll
   ```
4. Verify active session:
   ```bash
   composio whoami
   ```
   *Expected output:* `{"account_type":"human","email":"...","current_org_name":"...","enhanced_controls_enabled":true}`

---

## 2. Core Workflows & CLI Commands

### A. Searching Tools & Actions
Search semantically across all toolkits:
```bash
# Semantic search across all apps
composio search "send email" "create github issue"

# Filter by specific toolkit
composio search "list calendar events" --toolkits google_calendar --limit 5

# Human-readable output
composio search "sync spreadsheet" --human
```

### B. Connecting Accounts (OAuth Linking)
Link a third-party service to the current organization:
```bash
composio link github
composio link google_sheets
composio link google_calendar
composio link gmail
composio link linear
composio link notion
```
*Note:* Returns a verification link for the user to authorize OAuth permissions.

### C. Inspecting Schemas & Tool Definitions
```bash
# List available tools in a toolkit
composio tools list github
composio tools list google_sheets

# Inspect input schema for a specific action
composio tools info GITHUB_CREATE_ISSUE
composio execute GITHUB_CREATE_ISSUE --get-schema
```

### D. Executing Actions
Execute tools directly with JSON payloads:
```bash
# Single tool execution
composio execute GITHUB_CREATE_ISSUE -d '{ "owner": "IndraYuda13", "repo": "app", "title": "Automated bug report" }'

# Dry-run validation (validates connection & schema without remote mutation)
composio execute GMAIL_SEND_EMAIL -d '{ "recipient_email": "user@example.com", "subject": "Test" }' --dry-run

# File upload injection
composio execute SLACK_UPLOAD_FILE --file "/path/to/report.pdf" -d '{ "channels": "general" }'

# Parallel execution of multiple tools
composio execute -p \
  GMAIL_SEND_EMAIL -d '{ "recipient_email": "a@b.com", "subject": "Hi" }' \
  SLACK_SEND_A_MESSAGE_TO_A_SLACK_CHANNEL -d '{ "channel": "general", "text": "Hello" }'
```

### E. Authenticated API Proxying
Make direct curl-like API requests through Composio using authenticated connections:
```bash
# GET profile via Gmail proxy
composio proxy https://gmail.googleapis.com/gmail/v1/users/me/profile --toolkit gmail

# POST request via GitHub proxy
composio proxy https://api.github.com/user/repos --toolkit github -X POST -d '{"name":"new-repo"}'
```

### F. Scripted Multi-Step Execution (`composio run`)
Run inline TS/JS (via embedded Bun) with injected helpers (`execute`, `search`, `proxy`):
```bash
composio run '
  const user = await execute("GITHUB_GET_THE_AUTHENTICATED_USER");
  console.log("Logged in as:", user);
'
```

---

## 3. Directory Layout & Artifacts

- `~/.composio/user_data.json` — Authentication state and session tokens.
- `~/.composio/config.json` — CLI runtime configuration.
- `~/.composio/tools.json` / `toolkits.json` — Cached action metadata.
- `/tmp/composio/` — Session-scoped artifacts, downloads, and generated outputs.

---

## 4. Common Pitfalls & Guardrails

1. **PATH Resolution:** Always ensure `export PATH="$HOME/.local/bin:$PATH"` is present when executing commands in non-interactive shells or subshells.
2. **Developer Mode Requirements:** Commands under `composio dev connected-accounts` or `composio dev triggers` require `composio dev init` in the current working directory. For global tool execution, use root commands (`composio search`, `composio execute`, `composio link`).
3. **Destructive Actions Guard:** Disabling triggers or destructive dev actions requires `"developer.destructive_actions": true` in `~/.composio/config.json` and `--dangerously-allow` flag.
4. **Token Polling:** Never block foreground turn execution synchronously on `composio login --poll` without a timeout or background process tracking; always launch in background with notification.
