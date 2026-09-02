#!/usr/bin/env python3
"""Safely apply only fleet-owned policy fields to live Hermes configs.

Dry-run is the default. ``--apply`` refuses while any declared A2A port is
listening, creates a mode-0600 backup, writes atomically, verifies exact policy,
and automatically restores the backup if any write or verification fails.
Runtime-owned fields (credentials, providers, platform identities, plugins,
channel settings, and skill configuration) are preserved byte-for-byte outside
the policy-owned top-level blocks.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import stat
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

try:
    from scripts.apply_role_policy import render_policy
except ModuleNotFoundError:  # direct execution from the scripts directory
    from apply_role_policy import render_policy


POLICY_FIELDS = {
    "toolsets",
    "platform_toolsets",
    "moa",
    "delegation",
    "approvals",
    "command_allowlist",
    "terminal",
    "kanban",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_mapping(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(value, dict):
        raise ValueError(f"expected YAML mapping in {path}")
    return value


def changed_policy_fields(before: str, after: str) -> list[str]:
    old = yaml.safe_load(before) or {}
    new = yaml.safe_load(after) or {}
    if not isinstance(old, dict) or not isinstance(new, dict):
        raise ValueError("policy diff requires YAML mappings")
    return sorted(key for key in POLICY_FIELDS if old.get(key) != new.get(key))


def verify_policy(config: dict[str, Any], role: dict[str, Any], profile: str) -> list[str]:
    errors: list[str] = []
    if (config.get("model") or {}).get("default") != role.get("model"):
        errors.append("model does not match policy")
    root_tools = set(config.get("toolsets") or [])
    expected_root = set(role.get("allowed_root_toolsets") or [])
    if root_tools != expected_root:
        errors.append("root toolsets do not exactly match policy")

    expected_platform = set(role.get("allowed_platform_toolsets") or [])
    platform_sets = config.get("platform_toolsets") or {}
    if profile != "groupbot" and "a2a" not in platform_sets:
        errors.append("A2A platform tool surface is missing")
    for surface, tools in platform_sets.items():
        if set(tools or []) != expected_platform:
            errors.append(f"{surface} platform toolsets do not exactly match policy")

    enabled = root_tools | {
        tool for tools in platform_sets.values() for tool in (tools or [])
    }
    forbidden = set(role.get("forbidden_toolsets") or [])
    if enabled & forbidden:
        errors.append(f"forbidden tools remain enabled: {sorted(enabled & forbidden)}")

    if (config.get("approvals") or {}).get("mode") != "smart":
        errors.append("approvals.mode is not smart")
    if profile == "groupbot":
        if "terminal" in config:
            errors.append("GROUPBOT terminal config remains present")
        if config.get("a2a_agents"):
            errors.append("GROUPBOT has A2A peers")
    else:
        if (config.get("moa") or {}).get("enabled") is not False:
            errors.append("automatic MOA is not disabled")
        if (config.get("delegation") or {}).get("orchestrator_enabled") is not False:
            errors.append("hidden delegation is not disabled")
    if profile == "orion" and (config.get("kanban") or {}).get("review_dispatch") is not True:
        errors.append("ORION review_dispatch is not enabled")
    return errors


def listening_ports(roles: dict[str, dict[str, Any]], timeout: float = 0.15) -> list[int]:
    open_ports: list[int] = []
    for role in roles.values():
        port = role.get("a2a_port")
        if not isinstance(port, int):
            continue
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.settimeout(timeout)
            if client.connect_ex(("127.0.0.1", port)) == 0:
                open_ports.append(port)
    return sorted(open_ports)


def atomic_write(path: Path, content: str, mode: int) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, stat.S_IMODE(mode))
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def backup_configs(
    rendered: dict[str, tuple[Path, str, str]], backup_root: Path
) -> tuple[Path, dict[str, Any]]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = backup_root / stamp
    backup.mkdir(parents=True, mode=0o700, exist_ok=False)
    os.chmod(backup, 0o700)
    manifest: dict[str, Any] = {"created_at": stamp, "profiles": {}}
    for profile, (path, before, after) in rendered.items():
        target = backup / profile / "config.yaml"
        target.parent.mkdir(mode=0o700)
        target.write_text(before, encoding="utf-8")
        os.chmod(target, 0o600)
        manifest["profiles"][profile] = {
            "source": str(path),
            "before_sha256": sha256(before.encode()),
            "after_sha256": sha256(after.encode()),
            "changed_policy_fields": changed_policy_fields(before, after),
        }
    manifest_path = backup / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.chmod(manifest_path, 0o600)
    return backup, manifest


def restore_backup(rendered: dict[str, tuple[Path, str, str]], backup: Path) -> None:
    for profile, (path, _before, _after) in rendered.items():
        source = backup / profile / "config.yaml"
        shutil.copy2(source, path)


def parse_profile_selection(value: str | None, expected: set[str]) -> set[str]:
    if value is None:
        return set(expected)
    selected = {item.strip().lower() for item in value.split(",") if item.strip()}
    if not selected:
        raise ValueError("profile selection is empty")
    invalid = selected - expected
    if invalid:
        raise ValueError(f"unknown profiles: {sorted(invalid)}")
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument(
        "--hermes-home",
        type=Path,
        default=Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")),
    )
    parser.add_argument("--backup-root", type=Path)
    parser.add_argument(
        "--profiles",
        help="Comma-separated profiles for a targeted surgical deployment",
    )
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    hermes_home = args.hermes_home.expanduser().resolve()
    backup_root = (
        args.backup_root.expanduser().resolve()
        if args.backup_root
        else hermes_home / "backups" / "fleet-role-policy"
    )
    roles = load_mapping(repo_root / "governance/roles.yaml").get("profiles") or {}
    expected = {
        "orion", "atlas", "aurora", "forge", "frame", "lens",
        "nexus", "prism", "quant", "radar", "sentinel", "groupbot",
    }
    if set(roles) != expected:
        print("ERROR: manifest does not contain the exact fleet")
        return 1
    try:
        selected = parse_profile_selection(args.profiles, expected)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    rendered: dict[str, tuple[Path, str, str]] = {}
    for profile in sorted(selected):
        path = hermes_home / "profiles" / profile / "config.yaml"
        if not path.is_file():
            print(f"ERROR: missing live config for {profile}: {path}")
            return 1
        before = path.read_text(encoding="utf-8")
        after = render_policy(before, roles[profile], profile)
        rendered[profile] = (path, before, after)

    changed = {
        profile: changed_policy_fields(before, after)
        for profile, (_path, before, after) in rendered.items()
        if before != after
    }
    print("Fleet role-policy plan:")
    for profile in sorted(selected):
        fields = changed.get(profile, [])
        print(f"- {profile}: {'change ' + ', '.join(fields) if fields else 'no change'}")
    print("Runtime-owned providers, credentials, platform identities, plugins, and skills: PRESERVED")

    if not changed:
        print("No policy drift detected.")
        return 0
    if not args.apply:
        print("Dry-run complete. Stop the selected Hermes gateways, then rerun with --apply.")
        return 0

    open_ports = listening_ports({profile: roles[profile] for profile in selected})
    if open_ports:
        print(f"ERROR: refusing apply while A2A ports are listening: {open_ports}")
        return 1

    backup_root.mkdir(parents=True, mode=0o700, exist_ok=True)
    os.chmod(backup_root, 0o700)
    backup, _manifest = backup_configs(rendered, backup_root)
    try:
        for profile, (path, _before, after) in rendered.items():
            current_mode = path.stat().st_mode
            atomic_write(path, after, current_mode)
        verification_errors: list[str] = []
        for profile, (path, _before, _after) in rendered.items():
            errors = verify_policy(load_mapping(path), roles[profile], profile)
            verification_errors.extend(f"{profile}: {error}" for error in errors)
        if verification_errors:
            raise RuntimeError("; ".join(verification_errors))
    except Exception as exc:
        restore_backup(rendered, backup)
        print(f"ERROR: apply failed and configs were restored: {type(exc).__name__}: {exc}")
        print(f"Recovery copy retained at: {backup}")
        return 1

    print("Fleet role policy applied and verified.")
    print(f"Recovery copy: {backup}")
    print("Gateways remain stopped; restart them under their existing supervisor, then run discovery.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
