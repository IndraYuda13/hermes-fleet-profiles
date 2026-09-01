---
name: jira-rest-atlassian
description: Direct Jira operations through Atlassian REST from inside OpenClaw using stored Jira credentials. Use when reading Jira projects or issues, searching with JQL, listing fields, updating issue fields, adding comments, transitioning issues, or preparing spreadsheet-driven Jira updates from CSV or Excel files. Prefer this skill when the agent must act on Jira directly in this runtime rather than only preparing an external MCP client.
---

# Jira REST via Atlassian API

## Overview

Use this skill when Jira work must happen directly inside OpenClaw.

This skill assumes Jira credentials already exist in a private env file, by default:
- `/root/.openclaw/workspace/state/jira-mcp/mcp-atlassian.env`

It provides:
- direct Jira read and write operations through REST
- JQL search and field discovery
- safe spreadsheet-driven update preview before apply

## Safe workflow

### 1. Validate identity first

Run a quick read-only check before any mutation:

- `python3 scripts/jira_cli.py myself`
- `python3 scripts/jira_cli.py project --key KAN`
- `python3 scripts/jira_cli.py search --jql "project = KAN ORDER BY updated DESC" --limit 10`

If identity or project access fails, stop and fix credentials first.

### 2. Use the narrowest write possible

Prefer this order:
1. inspect fields
2. inspect target issue
3. preview intended change
4. perform the smallest write
5. re-read the issue if confirmation matters

For field discovery:
- `python3 scripts/jira_cli.py fields --query story`
- `python3 scripts/jira_cli.py fields --query sprint`

### 3. Direct issue operations

Examples:

- Get issue:
  - `python3 scripts/jira_cli.py issue-get KAN-1`

- Add comment:
  - `python3 scripts/jira_cli.py issue-comment KAN-1 --body "Progress updated from Brodayy."`

- Update summary:
  - `python3 scripts/jira_cli.py issue-update KAN-1 --fields '{"summary":"New title"}'`

- List transitions:
  - `python3 scripts/jira_cli.py transitions KAN-1`

- Transition by name:
  - `python3 scripts/jira_cli.py transition KAN-1 --name Done`

### 4. Spreadsheet-driven updates

Use `scripts/jira_excel_sync.py` when the user sends CSV or Excel files.

Default behavior is preview-only.

Preview example:
- `python3 scripts/jira_excel_sync.py --file ./updates.xlsx --sheet Sheet1 --project KAN`

Apply example:
- `python3 scripts/jira_excel_sync.py --file ./updates.xlsx --sheet Sheet1 --project KAN --apply`

Supported spreadsheet columns are intentionally narrow in V1:
- `issue_key` / `key` / `jira_key`
- `summary`
- `description`
- `comment`
- `status` / `transition`
- `priority`
- `labels`

Rows without an issue key are previewed as skipped in V1.

### 5. Be careful with destructive breadth

- Do not run mass updates blind from a spreadsheet.
- Inspect headers and a few sample rows first.
- Keep preview as the default.
- If the spreadsheet is ambiguous, stop and ask one focused clarification.

## Env and credentials

By default the scripts read:
- `/root/.openclaw/workspace/state/jira-mcp/mcp-atlassian.env`

Override with `--env-file` when needed.

Never echo or commit live tokens.

## References

Read when needed:
- `references/commands.md` for command patterns
- `references/spreadsheet-workflow.md` for Excel update discipline
- `references/workbook-import.md` for multi-sheet scrum workbook import rules and exact-39 sprint-only board mode
