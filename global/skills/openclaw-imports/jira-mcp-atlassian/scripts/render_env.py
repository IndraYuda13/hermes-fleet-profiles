#!/usr/bin/env python3
import argparse
import os
import stat
from pathlib import Path

DEFAULT_OUTPUT = "/root/.openclaw/workspace/state/jira-mcp/mcp-atlassian.env"


def str_to_bool(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "y", "on"}:
        return True
    if lowered in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"invalid boolean value: {value}")



def env_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'



def build_lines(args: argparse.Namespace):
    lines = [
        "# mcp-atlassian env file",
        "# Keep this file private. Do not commit it.",
    ]

    def add(key: str, value):
        if value is None:
            return
        if isinstance(value, bool):
            value = "true" if value else "false"
        else:
            value = str(value)
        lines.append(f"{key}={env_quote(value)}")

    add("JIRA_URL", args.jira_url)
    add("READ_ONLY_MODE", args.read_only)
    add("TOOLSETS", args.toolsets)
    add("JIRA_PROJECTS_FILTER", args.projects_filter)

    if args.mode == "cloud":
        add("JIRA_USERNAME", args.jira_username)
        add("JIRA_API_TOKEN", args.jira_api_token)
    else:
        add("JIRA_PERSONAL_TOKEN", args.jira_personal_token)
        if args.ssl_verify is not None:
            add("JIRA_SSL_VERIFY", args.ssl_verify)

    add("CONFLUENCE_URL", args.confluence_url)
    add("CONFLUENCE_USERNAME", args.confluence_username)
    add("CONFLUENCE_API_TOKEN", args.confluence_api_token)

    return lines



def main():
    parser = argparse.ArgumentParser(description="Render a local env file for mcp-atlassian.")
    parser.add_argument("--mode", choices=["cloud", "server"], required=True)
    parser.add_argument("--jira-url", required=True)
    parser.add_argument("--jira-username")
    parser.add_argument("--jira-api-token")
    parser.add_argument("--jira-personal-token")
    parser.add_argument("--confluence-url")
    parser.add_argument("--confluence-username")
    parser.add_argument("--confluence-api-token")
    parser.add_argument("--read-only", type=str_to_bool, default=True)
    parser.add_argument("--projects-filter")
    parser.add_argument("--toolsets", default="default")
    parser.add_argument("--ssl-verify", type=str_to_bool)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.mode == "cloud":
        if not args.jira_username or not args.jira_api_token:
            parser.error("cloud mode requires --jira-username and --jira-api-token")
    if args.mode == "server":
        if not args.jira_personal_token:
            parser.error("server mode requires --jira-personal-token")

    output = Path(args.output).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)

    if output.exists() and not args.force:
        parser.error(f"output already exists: {output} (use --force to overwrite)")

    content = "\n".join(build_lines(args)) + "\n"
    output.write_text(content, encoding="utf-8")
    os.chmod(output, stat.S_IRUSR | stat.S_IWUSR)

    print(f"Wrote env file: {output}")
    print("Permissions set to 600")
    print("Secrets were written to disk only. Do not paste this file into chat.")


if __name__ == "__main__":
    main()
