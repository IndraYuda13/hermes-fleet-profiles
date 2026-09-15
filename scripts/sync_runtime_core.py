#!/usr/bin/env python3
"""Synchronize the canonical fleet runtime core embedded in specialist SOULs."""

from __future__ import annotations

import argparse
from pathlib import Path


PROFILES = (
    "orion",
    "atlas",
    "aurora",
    "forge",
    "frame",
    "lens",
    "nexus",
    "prism",
    "quant",
    "radar",
    "sentinel",
)
START = "<!-- FLEET_RUNTIME_CORE_V2:START -->"
END = "<!-- FLEET_RUNTIME_CORE_V2:END -->"


def rendered_soul(text: str, core: str, profile: str) -> str:
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError(f"{profile}: expected exactly one runtime-core marker pair")
    before, remainder = text.split(START, 1)
    _old, after = remainder.split(END, 1)
    return f"{before.rstrip()}\n\n{START}\n{core.strip()}\n{END}{after}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    core = (root / "governance/FLEET_RUNTIME_CORE.md").read_text(encoding="utf-8")
    drift: list[str] = []

    for profile in PROFILES:
        path = root / "profiles" / profile / "SOUL.md"
        current = path.read_text(encoding="utf-8")
        try:
            expected = rendered_soul(current, core, profile)
        except ValueError as exc:
            print(f"ERROR: {exc}")
            return 1
        if expected == current:
            continue
        drift.append(profile)
        if args.apply:
            path.write_text(expected, encoding="utf-8")

    if drift and not args.apply:
        print("Runtime-core drift: " + ", ".join(drift))
        print("Run scripts/sync_runtime_core.py --apply to synchronize SOULs.")
        return 1
    if drift:
        print("Runtime core synchronized: " + ", ".join(drift))
    else:
        print("Runtime core: synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
