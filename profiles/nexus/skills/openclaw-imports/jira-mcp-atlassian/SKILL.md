---
name: jira-mcp-atlassian
description: Configure, validate, and operate the sooperset/mcp-atlassian MCP server for Jira-centric workflows. Use when setting up Jira MCP access, generating secure env or client-config snippets, validating Atlassian Cloud or Jira Server/Data Center credentials, smoke-testing mcp-atlassian, or preparing Jira issue workflows for an MCP-capable client. Not for generic Jira web automation, and not for pretending OpenClaw already has native Jira/MCP tools.
---

# Jira MCP via mcp-atlassian

## Overview

Use this skill to wrap `sooperset/mcp-atlassian` as a safe Jira setup workflow.

This skill is for:
- preparing Jira MCP credentials and env files
- generating redacted client config snippets
- validating prerequisites and basic access
- guiding Jira issue workflows for an MCP-capable client

This skill is **not** a native Jira tool bridge for OpenClaw. In this runtime, it should be treated as setup + config + smoke-test + workflow guidance.

## Workflow

### 1. Decide the target mode first

Pick the narrowest safe target:
- Jira only, or Jira + Confluence
- Atlassian Cloud, or Jira Server/Data Center
- read-only, or write-enabled
- local stdio MCP, or advanced HTTP/OAuth mode

Default V1 choice:
- Jira only
- Atlassian Cloud if the user uses `*.atlassian.net`
- `READ_ONLY_MODE=true`
- local stdio MCP via `uvx`

Avoid advanced OAuth or remote HTTP mode unless the user explicitly needs them.

### 2. Collect only the minimum secrets

#### Atlassian Cloud
Required:
- `JIRA_URL`
- `JIRA_USERNAME`
- `JIRA_API_TOKEN`

Optional:
- `JIRA_PROJECTS_FILTER`
- `READ_ONLY_MODE`
- `TOOLSETS`
- Confluence credentials if Confluence is also needed

#### Jira Server / Data Center
Required:
- `JIRA_URL`
- `JIRA_PERSONAL_TOKEN`

Optional:
- `JIRA_SSL_VERIFY=false` for self-signed or private CA setups
- `JIRA_PROJECTS_FILTER`
- `READ_ONLY_MODE`

Never paste secrets back into chat after they are provided.

### 3. Prefer safer defaults

Use these defaults unless the user asks otherwise:
- `READ_ONLY_MODE=true`
- `TOOLSETS=default`
- set `JIRA_PROJECTS_FILTER` when the user only needs a few projects
- keep Confluence disabled unless required
- avoid broad write access on first setup

### 4. Generate local config artifacts

Use the bundled scripts from this skill directory:

1. Check prerequisites
   - `bash scripts/check_prereqs.sh`

2. Render an env file
   - Cloud example:
     - `python3 scripts/render_env.py --mode cloud --jira-url https://example.atlassian.net --jira-username user@example.com --jira-api-token TOKEN --read-only true --output /root/.openclaw/workspace/state/jira-mcp/mcp-atlassian.env`
   - Server example:
     - `python3 scripts/render_env.py --mode server --jira-url https://jira.example.com --jira-personal-token TOKEN --ssl-verify false --read-only true --output /root/.openclaw/workspace/state/jira-mcp/mcp-atlassian.env`

3. Print a redacted MCP client config snippet
   - `python3 scripts/print_client_config.py --env-file /root/.openclaw/workspace/state/jira-mcp/mcp-atlassian.env`

4. Validate direct Jira access as a fallback smoke check
   - `python3 scripts/jira_rest_smoke.py --env-file /root/.openclaw/workspace/state/jira-mcp/mcp-atlassian.env`

5. Validate local MCP startup basics
   - `bash scripts/smoke_test.sh`

Store generated env files under `/root/.openclaw/workspace/state/jira-mcp/` and keep file permissions tight.

### 5. Be honest about validation depth

`mcp-atlassian` is an MCP server. In this runtime, there is no generic native MCP invocation tool exposed to the agent.

So validate in layers:
- prerequisite check
- env/config generation
- direct Jira credential smoke test via REST fallback
- MCP binary or server help/startup sanity check
- handoff client config for a real MCP-capable client

Do **not** claim that Jira MCP actions are fully working inside OpenClaw unless a real MCP client bridge is present and tested.

## Practical task patterns

Once the MCP server is wired into an MCP-capable client, these are good first tasks:
- find issues assigned to me in project `ABC`
- get issue `ABC-123`
- add a comment to `ABC-123`
- transition `ABC-123` to Done
- create a bug ticket from this incident summary
- list fields before updating a custom field

Start read-only first. Enable create, update, or transition only after credentials and project scope are confirmed.

## Limitations

- This skill does **not** magically add Jira MCP tools to OpenClaw.
- OAuth, remote HTTP mode, and multi-user proxy setups are intentionally out of scope for V1.
- Jira custom fields vary per tenant, so field lookup is often required before update flows.
- Attachment-heavy flows are not part of the smoke-test path.
- If the user wants true in-OpenClaw Jira execution later, build a dedicated bridge or a separate Jira REST skill.

## References

Read these only when needed:
- `references/config-snippets.md` for redacted env and client examples
- `references/troubleshooting.md` for common auth, SSL, permission, and scope issues
