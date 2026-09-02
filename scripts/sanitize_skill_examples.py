#!/usr/bin/env python3
"""Remove credential-shaped examples from tracked skill documentation."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPLACEMENTS = (
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b"), "ghp_REDACTED_EXAMPLE"),
    (re.compile(r"\bPMAK-[A-Za-z0-9-]{30,}\b"), "PMAK-REDACTED-EXAMPLE"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"), "sk-REDACTED-EXAMPLE"),
)


def sanitize_text(text: str, path: Path | None = None) -> str:
    for pattern, replacement in REPLACEMENTS:
        text = pattern.sub(replacement, text)
    normalized_path = str(path or "").replace("\\", "/").lower()
    if "whatsapp" in normalized_path:
        text = re.sub(r"\b\d{10,}(?::\d+)?@(?:g\.us|lid|s\.whatsapp\.net)\b", "<WHATSAPP_JID>", text)
        text = re.sub(r"\b\d{10,}\b", "<WHATSAPP_ID>", text)
        text = re.sub(r"@\d{10,}", "@<WHATSAPP_ID>", text)
    if normalized_path.endswith("nofx-operations/skill.md"):
        safe_model_section = """### Adding/Modifying AI Models
Use the supported NOFX UI or API. Supply provider credentials through the
container secret environment and never paste `DATA_ENCRYPTION_KEY`, API keys,
wallet addresses, user IDs, or encrypted credential blobs into documentation.
If the UI/API cannot perform the change, stop and repair that control path
instead of writing credential rows directly in SQLite.

"""
        text = re.sub(
            r"### Adding/Modifying AI Models[\s\S]*?(?=## Known Troubleshooting Pitfalls)",
            safe_model_section,
            text,
        )
        text = re.sub(
            r"- \*\*Direct Database Bypass\*\*:[\s\S]*?(?=\n### AI500 Coin Source Failure)",
            "- **Credential safety**: do not bypass the signed authorization flow or insert exchange credentials directly into SQLite. Repair TLS/chain configuration, then retry the supported flow.\n",
            text,
        )
        text = re.sub(r"`0x[a-fA-F0-9]{30,}`", "`<WALLET_ADDRESS>`", text)
    return text


def candidate_files(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".js", ".ts", ".sh"}:
            yield path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("roots", nargs="+", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    dirty: list[str] = []
    for root in args.roots:
        if not root.exists():
            continue
        for path in candidate_files(root):
            original = path.read_text(encoding="utf-8")
            cleaned = sanitize_text(original, path)
            if cleaned != original:
                dirty.append(str(path))
                if not args.check:
                    path.write_text(cleaned, encoding="utf-8")
    if args.check and dirty:
        print("Credential-shaped skill examples:", file=sys.stderr)
        for path in dirty:
            print(f"  - {path}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
