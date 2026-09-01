# Config Snippets

## Atlassian Cloud env example

```env
JIRA_URL="https://example.atlassian.net"
JIRA_USERNAME="user@example.com"
JIRA_API_TOKEN="<TOKEN>"
READ_ONLY_MODE="true"
TOOLSETS="default"
JIRA_PROJECTS_FILTER="ABC,OPS"
```

## Jira Server / Data Center env example

```env
JIRA_URL="https://jira.example.com"
JIRA_PERSONAL_TOKEN="<TOKEN>"
JIRA_SSL_VERIFY="false"
READ_ONLY_MODE="true"
TOOLSETS="default"
JIRA_PROJECTS_FILTER="OPS"
```

## Redacted MCP client config example

```json
{
  "mcpServers": {
    "jira-atlassian": {
      "command": "uvx",
      "args": ["mcp-atlassian"],
      "env": {
        "JIRA_URL": "https://example.atlassian.net",
        "JIRA_USERNAME": "user@example.com",
        "JIRA_API_TOKEN": "<REDACTED>",
        "READ_ONLY_MODE": "true",
        "TOOLSETS": "default",
        "JIRA_PROJECTS_FILTER": "ABC,OPS"
      }
    }
  }
}
```

## Secret-safer local launcher pattern

Prefer this when the client supports calling a local script and you do not want the token duplicated inside JSON config.

Launcher script:

```sh
#!/usr/bin/env sh
set -eu
set -a
. /root/.openclaw/workspace/state/jira-mcp/mcp-atlassian.env
set +a
exec uvx mcp-atlassian
```

Client config:

```json
{
  "mcpServers": {
    "jira-atlassian": {
      "command": "/root/.openclaw/workspace/state/jira-mcp/launch-mcp-atlassian.sh",
      "args": []
    }
  }
}
```

## Safe first-step prompts for an MCP-capable client

- `Find issues assigned to me in project ABC.`
- `Get issue ABC-123 and summarize its current status.`
- `List transitions available for ABC-123.`
- `List fields for project ABC before we touch any custom fields.`

## Write-enabled prompts only after validation

- `Create a bug ticket in project ABC from this incident summary.`
- `Add a comment to ABC-123 with this update.`
- `Transition ABC-123 to Done.`
