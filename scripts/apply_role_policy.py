#!/usr/bin/env python3
"""Render machine-readable role policy into profile config tool boundaries."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

TOP_LEVEL = re.compile(r"^(?P<key>[A-Za-z0-9_.-]+):(?:\s.*)?$")


def replace_top_level(text: str, key: str, value: object | None) -> str:
    lines = text.splitlines(keepends=True)
    start = None
    end = len(lines)
    for index, line in enumerate(lines):
        match = TOP_LEVEL.match(line.rstrip("\r\n"))
        if not match:
            continue
        if start is None and match.group("key") == key:
            start = index
            continue
        if start is not None:
            end = index
            break

    replacement = ""
    if value is not None:
        replacement = yaml.safe_dump(
            {key: value}, sort_keys=False, default_flow_style=False, width=1000
        )
    if start is None:
        prefix = text if text.endswith("\n") or not text else text + "\n"
        return prefix + replacement
    return "".join(lines[:start]) + replacement + "".join(lines[end:])


def render_policy(text: str, role: dict[str, object], profile_name: str) -> str:
    """Render policy-owned fields while preserving every runtime-owned field."""
    current = yaml.safe_load(text) or {}

    text = replace_top_level(text, "toolsets", role["allowed_root_toolsets"])
    platform_names = list((current.get("platform_toolsets") or {}).keys())
    if platform_names:
        platform_value = {
            name: list(role["allowed_platform_toolsets"]) for name in platform_names
        }
        text = replace_top_level(text, "platform_toolsets", platform_value)

    if profile_name == "groupbot":
        text = replace_top_level(text, "terminal", None)
    else:
        text = replace_top_level(text, "moa", {"enabled": False})
        text = replace_top_level(
            text,
            "delegation",
            {"orchestrator_enabled": False, "subagent_auto_approve": False},
        )

    approvals = current.get("approvals") or {}
    approvals.update(
        {
            "mode": "smart",
            "denial_breaker_threshold": 2,
            "mcp_reload_confirm": True,
            "destructive_slash_confirm": True,
        }
    )
    text = replace_top_level(text, "approvals", approvals)

    if profile_name not in {"atlas", "forge", "frame"}:
        text = replace_top_level(text, "command_allowlist", [])

    if profile_name == "orion":
        refreshed = yaml.safe_load(text) or {}
        kanban = refreshed.get("kanban") or {}
        kanban["review_dispatch"] = True
        text = replace_top_level(text, "kanban", kanban)

    yaml.safe_load(text)
    return text


def apply_policy(config_path: Path, role: dict[str, object]) -> None:
    text = config_path.read_text(encoding="utf-8")
    text = render_policy(text, role, config_path.parent.name)
    config_path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.repo_root.resolve()
    manifest = yaml.safe_load((root / "governance/roles.yaml").read_text(encoding="utf-8"))
    for name, role in manifest["profiles"].items():
        apply_policy(root / "profiles" / name / "config.yaml", role)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
