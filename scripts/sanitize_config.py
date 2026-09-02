#!/usr/bin/env python3
"""Sanitize Hermes YAML configs without serializing or reordering the document."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

KEY_VALUE = re.compile(r"^(?P<indent>\s*)(?P<key>[A-Za-z0-9_.-]+):(?P<space>\s*)(?P<value>.*)$")
SECRET_KEY = re.compile(
    r"(?:^|_)(?:api_key|token|secret|password|password_hash|client_secret)$",
    re.IGNORECASE,
)
DROP_ENV_KEYS = {
    "FIRECRAWL_API_KEY",
    "POSTMAN_API_KEY",
}


def sanitize_text(text: str) -> str:
    # Reject malformed input before attempting a line-preserving transformation.
    yaml.safe_load(text)

    output: list[str] = []
    top_level = ""
    skipping_dashboard_basic = False

    for raw in text.splitlines(keepends=True):
        bare = raw.rstrip("\r\n")
        match = KEY_VALUE.match(bare)
        if not match:
            if not skipping_dashboard_basic:
                output.append(raw)
            continue

        indent = len(match.group("indent"))
        key = match.group("key")
        value = match.group("value").strip()

        if indent == 0:
            top_level = key
            skipping_dashboard_basic = False

        if skipping_dashboard_basic:
            if indent > 2:
                continue
            skipping_dashboard_basic = False

        if top_level == "dashboard" and indent == 2 and key == "basic_auth":
            skipping_dashboard_basic = True
            continue
        if top_level == "dashboard" and indent == 2 and key == "auth" and value.startswith("password"):
            continue

        # Hermes officially supports these through ~/.hermes/.env. Removing the
        # scalar is safer than committing a fake value that appears functional.
        if key in DROP_ENV_KEYS:
            newline = "\r\n" if raw.endswith("\r\n") else "\n" if raw.endswith("\n") else ""
            output.append(f'{match.group("indent")}{key}: "${{{key}}}"{newline}')
            continue
        if key.lower() == "firecrawl_api_key":
            continue

        if SECRET_KEY.search(key):
            newline = "\r\n" if raw.endswith("\r\n") else "\n" if raw.endswith("\n") else ""
            output.append(f"{match.group('indent')}{key}: REDACTED{newline}")
            continue

        output.append(raw)

    cleaned = "".join(output)
    yaml.safe_load(cleaned)
    return cleaned


def sanitize_identity_config(text: str, profile_name: str) -> str:
    """Remove channel/user routing identifiers from repository declarations."""
    if profile_name not in {"groupbot", "orion"}:
        return text
    data = yaml.safe_load(text) or {}
    platforms = data.get("platforms") or {}
    whatsapp = platforms.get("whatsapp") or {}
    whatsapp.pop("home_channel", None)
    extra = whatsapp.get("extra")
    if isinstance(extra, dict):
        for key in ("allow_from", "group_allow_from", "group_allowed_chats"):
            if key in extra:
                extra[key] = []
        if isinstance(extra.get("mention_patterns"), list):
            extra["mention_patterns"] = [
                value for value in extra["mention_patterns"]
                if not re.search(r"\d{6,}", str(value))
            ]
    if profile_name == "orion" and whatsapp.get("enabled") is False:
        platforms["whatsapp"] = {"enabled": False}
    return yaml.safe_dump(data, sort_keys=False, default_flow_style=False, width=1000)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--check", action="store_true", help="fail when a file is not sanitized")
    args = parser.parse_args()

    dirty: list[str] = []
    for path in args.paths:
        original = path.read_text(encoding="utf-8")
        cleaned = sanitize_identity_config(sanitize_text(original), path.parent.name)
        if cleaned != original:
            dirty.append(str(path))
            if not args.check:
                path.write_text(cleaned, encoding="utf-8")

    if args.check and dirty:
        print("Unsanitized config files:", file=sys.stderr)
        for path in dirty:
            print(f"  - {path}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
