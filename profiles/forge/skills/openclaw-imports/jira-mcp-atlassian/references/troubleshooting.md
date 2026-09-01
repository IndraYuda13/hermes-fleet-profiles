# Troubleshooting

## 401 Unauthorized

Common causes:
- wrong Atlassian API token
- wrong email / username
- PAT copied incorrectly
- using Cloud credentials against a Server/Data Center URL

Check:
- URL is correct and has no extra path suffix
- Cloud uses `JIRA_USERNAME` + `JIRA_API_TOKEN`
- Server/DC uses `JIRA_PERSONAL_TOKEN`

## 403 Forbidden

Common causes:
- account can authenticate but lacks project permission
- issue exists but user cannot browse it
- write operation blocked by project role or workflow restriction

Safe response:
- prove read access first with `/myself` or issue search
- narrow project scope and retry
- do not assume the token is invalid if auth succeeds but action is forbidden

## SSL / certificate failures

For internal Jira Server/DC with self-signed or private CA certs:
- set `JIRA_SSL_VERIFY=false` only when needed
- prefer fixing trust properly over disabling verification

## Custom field confusion

Jira field names vary per tenant.
Before update flows:
- list or inspect fields first
- do not guess custom field ids
- confirm whether the target field is editable in that project and issue type

## Rate limits and retries

Atlassian Cloud can rate limit.
- avoid bursty loops
- prefer fewer larger reads
- serialize mutating writes
- back off on repeated 429 or transient 5xx responses

## Current runtime limitation

This skill prepares and validates `mcp-atlassian`, but it does not create native Jira tools inside OpenClaw by itself.

Practical meaning:
- use this skill to generate env/config and validate access
- use an MCP-capable client for real MCP tool calls
- if the user later wants direct Jira actions inside OpenClaw, build a separate bridge or Jira REST skill
