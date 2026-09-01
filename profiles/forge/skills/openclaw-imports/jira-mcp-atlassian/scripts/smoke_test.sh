#!/usr/bin/env sh
set -eu

if ! command -v uvx >/dev/null 2>&1; then
  echo '[FAIL] uvx is missing. Install uv/uvx first or switch to a manual Docker flow.' >&2
  exit 1
fi

echo '[OK] uvx found'
if uvx mcp-atlassian --help >/dev/null 2>&1; then
  echo '[OK] uvx mcp-atlassian --help succeeded'
else
  echo '[FAIL] uvx mcp-atlassian --help failed' >&2
  exit 1
fi

echo '[INFO] This only validates local launcher availability.'
echo '[INFO] For credential validation, run jira_rest_smoke.py against the rendered env file.'
echo '[INFO] For real MCP actions, attach the printed config to an MCP-capable client.'
