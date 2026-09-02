#!/usr/bin/env python3
"""Fail-closed repository policy checks for the Hermes fleet."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

import yaml

FLEET = ("orion", "atlas", "aurora", "forge", "frame", "lens", "nexus", "prism", "quant", "radar", "sentinel")
ALL_PROFILES = set(FLEET) | {"groupbot"}
PLACEHOLDERS = {"", "REDACTED", "CHANGEME", "NOT_COMMITTED"}
SECRET_KEY = re.compile(r"(?:^|_)(?:api_key|token|secret|password|password_hash|client_secret)$", re.I)
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b"),
    re.compile(r"\bPMAK-[A-Za-z0-9-]{30,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
)
BANNED_TRACKED = (
    re.compile(r"(?:^|/)skills/\.hub/"),
    re.compile(r"(?:^|/)hermes-index\.json$"),
    re.compile(r"(?:^|/)\.archive/"),
    re.compile(r"\.log$"),
    re.compile(r"\.jsonl$"),
)


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def scalar_items(value: Any, path: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from scalar_items(child, path + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from scalar_items(child, path + (str(index),))
    else:
        yield path, value


def tracked_files(root: Path) -> list[str]:
    try:
        output = subprocess.check_output(
            ["git", "ls-files"], cwd=root, text=True, stderr=subprocess.DEVNULL
        )
        return [line for line in output.splitlines() if line]
    except (OSError, subprocess.CalledProcessError):
        return [str(path.relative_to(root)) for path in root.rglob("*") if path.is_file()]


def validate(root: Path) -> Validation:
    result = Validation()
    manifest_path = root / "governance/roles.yaml"
    result.require(manifest_path.is_file(), "missing governance/roles.yaml")
    if not manifest_path.is_file():
        return result

    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    roles = manifest.get("profiles") or {}
    result.require(set(roles) == ALL_PROFILES, "role manifest must contain exactly the 11-profile fleet plus groupbot")

    configs: dict[str, dict[str, Any]] = {}
    for name in sorted(ALL_PROFILES):
        path = root / "profiles" / name / "config.yaml"
        result.require(path.is_file(), f"missing {path.relative_to(root)}")
        if not path.is_file():
            continue
        try:
            config = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            result.errors.append(f"invalid YAML {path.relative_to(root)}: {exc}")
            continue
        configs[name] = config
        role = roles.get(name) or {}

        result.require((config.get("model") or {}).get("default") == role.get("model"), f"{name}: model differs from role manifest")
        root_tools = set(config.get("toolsets") or [])
        platform_tools = {tool for tools in (config.get("platform_toolsets") or {}).values() for tool in (tools or [])}
        allowed_root = set(role.get("allowed_root_toolsets") or [])
        allowed_platform = set(role.get("allowed_platform_toolsets") or [])
        forbidden = set(role.get("forbidden_toolsets") or [])
        result.require(root_tools <= allowed_root, f"{name}: root tools outside policy: {sorted(root_tools - allowed_root)}")
        result.require(platform_tools <= allowed_platform, f"{name}: platform tools outside policy: {sorted(platform_tools - allowed_platform)}")
        result.require(not ((root_tools | platform_tools) & forbidden), f"{name}: forbidden tools enabled: {sorted((root_tools | platform_tools) & forbidden)}")
        result.require((config.get("approvals") or {}).get("mode") == "smart", f"{name}: approvals.mode must be smart")

        if name != "groupbot":
            result.require((config.get("moa") or {}).get("enabled") is False, f"{name}: automatic MOA must be disabled")
            result.require((config.get("delegation") or {}).get("orchestrator_enabled") is False, f"{name}: hidden delegation must be disabled")

        for key_path, value in scalar_items(config):
            key = key_path[-1] if key_path else ""
            if SECRET_KEY.search(key):
                safe = value is None or str(value).strip() in PLACEHOLDERS or str(value).startswith("${")
                result.require(safe, f"{name}: committed secret-like value at {'.'.join(key_path)}")
        dashboard = config.get("dashboard") or {}
        result.require("basic_auth" not in dashboard, f"{name}: dashboard.basic_auth must live in .env")
        result.require(not str(dashboard.get("auth", "")).startswith("password"), f"{name}: plaintext dashboard auth committed")

    for name in FLEET:
        config = configs.get(name) or {}
        role = roles.get(name) or {}
        port = (((config.get("gateway") or {}).get("platforms") or {}).get("a2a") or {}).get("extra", {}).get("port")
        result.require(port == role.get("a2a_port"), f"{name}: A2A port mismatch")
        peers = set(config.get("a2a_agents") or {})
        result.require(peers == set(FLEET) - {name}, f"{name}: A2A peers are not exact full mesh")

    groupbot = configs.get("groupbot") or {}
    result.require("a2a_agents" not in groupbot, "groupbot must remain outside A2A")
    result.require("terminal" not in groupbot, "groupbot terminal config must not exist")
    groupbot_extra = (((groupbot.get("platforms") or {}).get("whatsapp") or {}).get("extra") or {})
    for identifier_key in ("allow_from", "group_allow_from", "group_allowed_chats"):
        result.require(groupbot_extra.get(identifier_key, []) == [], f"groupbot: {identifier_key} must remain runtime-local")
    for sensitive_profile in ("groupbot", "orion"):
        sensitive_text = (root / "profiles" / sensitive_profile / "config.yaml").read_text(encoding="utf-8")
        result.require(not re.search(r"\d{10,}|@g\.us|@lid", sensitive_text), f"{sensitive_profile}: channel/user identifier committed")
    orion = configs.get("orion") or {}
    result.require((orion.get("kanban") or {}).get("review_dispatch") is True, "orion: review_dispatch must be enabled")

    workflow = yaml.safe_load((root / "governance/workflows/ui-prototype.yaml").read_text(encoding="utf-8"))
    owners = [stage.get("owner") for stage in workflow.get("stages", [])]
    result.require(owners[:4] == ["aurora", "aurora", "aurora", "frame"], "UI workflow must begin AURORA design -> FRAME implementation")
    result.require("lens" in owners, "UI workflow requires independent LENS verification")

    runtime_pack_path = root / "governance/runtime-smoke.yaml"
    result.require(runtime_pack_path.is_file(), "missing governance/runtime-smoke.yaml")
    if runtime_pack_path.is_file():
        runtime_pack = yaml.safe_load(runtime_pack_path.read_text(encoding="utf-8")) or {}
        result.require(
            tuple(runtime_pack.get("a2a_profiles") or ()) == FLEET,
            "runtime smoke pack must contain the ordered 11-profile A2A fleet",
        )
        probes = runtime_pack.get("boundary_probes") or {}
        result.require(
            set(probes) == set(FLEET),
            "runtime smoke pack must define one boundary probe per A2A profile",
        )
        for name in FLEET:
            if name == "atlas":
                expected_effect = "require-kanban-authorization"
            else:
                expected_effect = "allow-scoped-write" if roles[name].get("production_write") else "deny-production-write"
            actual_effect = (probes.get(name) or {}).get("effect")
            result.require(
                actual_effect == expected_effect,
                f"{name}: runtime probe effect {actual_effect!r} differs from production_write policy",
            )

    gauntlet_path = root / "governance/gauntlets/ui-prototype.yaml"
    result.require(gauntlet_path.is_file(), "missing governance/gauntlets/ui-prototype.yaml")
    if gauntlet_path.is_file():
        gauntlet = yaml.safe_load(gauntlet_path.read_text(encoding="utf-8")) or {}
        expected_owners = set((gauntlet.get("expected_owners") or {}).values())
        result.require(
            gauntlet.get("entry_profile") == "orion",
            "UI gauntlet must enter through ORION",
        )
        result.require(
            {"aurora", "frame", "prism", "lens", "orion"} <= expected_owners,
            "UI gauntlet must bind artifacts to AURORA, FRAME, PRISM, LENS and ORION",
        )
        screenshot_widths = {
            item.get("width") for item in (gauntlet.get("required_screenshots") or [])
        }
        result.require(
            screenshot_widths == {320, 390, 768, 1440, 1920},
            "UI gauntlet must require all five canonical viewport widths",
        )

    files = tracked_files(root)
    for relative in files:
        if any(pattern.search(relative) for pattern in BANNED_TRACKED):
            result.errors.append(f"tracked runtime/cache artifact: {relative}")
        path = root / relative
        if not path.is_file() or path.stat().st_size > 2_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                result.errors.append(f"credential signature found in {relative}")
                break
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.repo_root.resolve()
    result = validate(root)
    for warning in result.warnings:
        print(f"WARN: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}")
    if result.errors:
        print(f"Fleet policy: FAIL ({len(result.errors)} error(s))")
        return 1
    print("Fleet policy: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
