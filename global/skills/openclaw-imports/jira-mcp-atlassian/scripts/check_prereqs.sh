#!/usr/bin/env sh
set -eu

status=0

check_cmd() {
  name="$1"
  desc="$2"
  if command -v "$name" >/dev/null 2>&1; then
    printf '[OK] %s found: %s\n' "$desc" "$(command -v "$name")"
  else
    printf '[MISS] %s not found: %s\n' "$desc" "$name"
    status=1
  fi
}

printf 'Checking Jira MCP prerequisites...\n'
check_cmd python3 "Python 3"
check_cmd sh "POSIX shell"
check_cmd uvx "uvx (preferred mcp-atlassian launcher)"

if command -v node >/dev/null 2>&1 && command -v npx >/dev/null 2>&1; then
  printf '[OK] Node.js + npx found: %s | %s\n' "$(command -v node)" "$(command -v npx)"
else
  printf '[WARN] Node.js or npx missing. MCP Inspector testing may be unavailable.\n'
fi

if command -v docker >/dev/null 2>&1; then
  printf '[INFO] Docker available: %s\n' "$(command -v docker)"
else
  printf '[INFO] Docker not found. That is fine if you use uvx.\n'
fi

printf '\nRecommended happy path:\n'
printf '  1. Install uv/uvx if missing\n'
printf '  2. Render env with render_env.py\n'
printf '  3. Validate credentials with jira_rest_smoke.py\n'
printf '  4. Run smoke_test.sh\n'

exit "$status"
