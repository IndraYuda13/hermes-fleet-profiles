#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def parse_env_file(path: Path):
    data = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        data[key.strip()] = value
    return data



def redact_env(env: dict, include_secrets: bool):
    secret_keys = {
        "JIRA_API_TOKEN",
        "JIRA_PERSONAL_TOKEN",
        "CONFLUENCE_API_TOKEN",
    }
    if include_secrets:
        return env
    redacted = {}
    for key, value in env.items():
        redacted[key] = "<REDACTED>" if key in secret_keys else value
    return redacted



def main():
    parser = argparse.ArgumentParser(description="Print a ready-to-paste MCP client config snippet.")
    parser.add_argument("--env-file", required=True)
    parser.add_argument("--server-name", default="jira-atlassian")
    parser.add_argument("--include-secrets", action="store_true", help="Include real token values from env file")
    args = parser.parse_args()

    env_file = Path(args.env_file).expanduser()
    env = parse_env_file(env_file)

    config = {
        "mcpServers": {
            args.server_name: {
                "command": "uvx",
                "args": ["mcp-atlassian"],
                "env": redact_env(env, args.include_secrets),
            }
        }
    }

    print(json.dumps(config, indent=2, sort_keys=True))
    if not args.include_secrets:
        print("\n# Tokens are redacted by default.")
        print("# Use --include-secrets only in a trusted local terminal, never in chat.")


if __name__ == "__main__":
    main()
