# MCP & n8n Integration Reference

Depth for wiring external automation — HTTP MCP servers, n8n workflow automation, and local LLM gateway routing — into Hermes or alongside an application backend. See SKILL.md for the always-on rules.

## Adding an HTTP MCP server to Hermes

Hermes config lives at `~/.hermes/config.yaml`. Requires StreamableHTTP transport support (auto-negotiates SSE/JSON-RPC over HTTP):

```yaml
mcp_servers:
  n8n-mcp:
    url: "https://n8n.domain.com/mcp-server/http"
    headers:
      Authorization: "Bearer <token>"
```

## n8n workflow automation via `n8n-mcp`

Build order — each step has its own tool and none are skippable:
1. `get_workflow_best_practices`
2. `get_sdk_reference` (valid `@n8n/workflow-sdk` TypeScript/JS)
3. `validate_workflow` before creating
4. `create_workflow_from_code`
5. `publish_workflow`
6. `execute_workflow` to test-run

### Expression syntax pitfalls
- In `n8n-nodes-base.httpRequest`, pass static/literal JSON payloads in `jsonBody` as plain JSON strings. Wrap in `expr(...)` only when dynamic `{{ $json... }}` expressions are present — static payloads wrapped in `expr(...)` throw `invalid syntax`.
- Telegram webhook URLs (`https://api.telegram.org/bot<token>/sendMessage`) need a valid `<bot_id>:<hash>` token format.

### Workflow version hygiene
Recreating or refactoring workflows from code accumulates draft/duplicate instances in the workspace. `archive_workflow` each superseded `workflowId` so only active/published workflows stay visible in the n8n UI.

### Multi-agent async fan-out pattern
- For 20+ parallel agent workloads in single-instance n8n, use a parent dispatcher emitting job items to sub-workflows with **Wait for Completion: OFF**.
- Map agent model routes (`model_route` in Postgres) to local LLM gateway endpoints for unified multi-agent routing.
- Always write state/results to Postgres **before** evaluating notification gates, so both notified and silent runs remain auditable.

### Docker container → host gateway authentication
When n8n (or any service) runs inside a Docker container, its calls to a gateway on the host present as remote connections — the source IP is the docker bridge (typically `172.20.0.1`), not localhost. A gateway that requires API keys for remote access answers `401 API key required for remote API access`. Options:
1. **Preferred:** supply a valid bearer token.
2. Flip the gateway's `requireApiKey` setting in its SQLite `settings` table, then trigger a daemon reload (e.g. `fuser -k <port>/tcp`).

Avoid killing the daemon unnecessarily — its supervisor auto-restarts it, but a mid-flight reload drops connections.
