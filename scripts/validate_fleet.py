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


ARTIFACT_SCOPE_MAP: dict[str, str] = {
    "PRODUCT_CONTEXT.md": "research-evidence",
    "CONTENT_MAP.md": "content-map",
    "REFERENCE_LEDGER.md": "research-evidence",
    "CANDIDATE_HYPOTHESES.md": "candidate-hypotheses",
    "spikes-source": "visual-spikes",
    "SPIKE_MANIFEST.json": "spike-manifest",
    "VISUAL_TOURNAMENT.json": "visual-tournament",
    "DESIGN_DNA.md": "design-dna",
    "DESIGN_CONTRACT.md": "design-contract",
    "INTERACTION_CONTRACT.json": "interaction-contract",
    "ASSET_MANIFEST.json": "asset-manifest",
    "vertical-slice-source": "vertical-slice",
    "slice-evidence": "vertical-slice",
    "VERTICAL_SLICE_REPORT.md": "slice-report",
    "frontend-source": "frontend-source",
    "BUILD_MANIFEST.json": "build-manifest",
    "FUNCTIONAL_QA.md": "functional-qa-report",
    "PRISM_VERIFICATION_REPORT.json": "prism-verification-report",
    "VISUAL_QA.md": "qa-evidence",
    "LENS_REVIEW_REPORT.json": "lens-review-report",
    "DEFECT_LEDGER.json": "defect-report",
    "remediated-source": "frontend-source",
    "remediation-ledger": "build-artifacts",
    "RETEST_REPORT.md": "defect-report",
    "CLOSURE_REPORT.md": "closure-report",
    "RELEASE_DECISION_RECORD.md": "release-decision-record",
}


CANONICAL_LIFECYCLE_STAGES: tuple[str, ...] = (
    "discovery",
    "candidate-hypotheses",
    "visual-spikes",
    "blind-tournament",
    "contract",
    "asset-gate",
    "vertical-slice",
    "vertical-slice-gate",
    "implementation",
    "functional-verification",
    "rendered-verification",
    "remediation",
    "retest",
    "closure",
)


def validate_ui_workflow(root: Path, roles: dict[str, Any], result: Validation) -> None:
    workflow_path = root / "governance/workflows/ui-prototype.yaml"
    result.require(workflow_path.is_file(), "missing governance/workflows/ui-prototype.yaml")
    if not workflow_path.is_file():
        return
    try:
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        result.errors.append(f"invalid YAML {workflow_path.relative_to(root)}: {exc}")
        return

    stages = workflow.get("stages", [])
    result.require(len(stages) >= 10, "UI workflow must contain at least 10 stages")

    # Invariant 1: all stage IDs unique and strictly match canonical lifecycle
    stage_ids = [s.get("id") for s in stages if s.get("id")]
    result.require(len(stage_ids) == len(stages), "UI workflow has stages without an id")
    result.require(len(set(stage_ids)) == len(stage_ids), f"duplicate stage IDs in UI workflow: {stage_ids}")
    result.require(
        tuple(stage_ids) == CANONICAL_LIFECYCLE_STAGES,
        f"UI workflow stages must strictly match canonical lifecycle: {CANONICAL_LIFECYCLE_STAGES}, got: {tuple(stage_ids)}",
    )

    # Invariant 2: all stage owners valid
    valid_owners = set(FLEET) | {"original-verifier"}
    for stage in stages:
        owner = stage.get("owner")
        result.require(owner in valid_owners, f"stage {stage.get('id')}: invalid owner {owner!r}")

    # Invariant 3: Entry owner is orion
    result.require(workflow.get("entry", {}).get("owner") == "orion", "UI workflow entry owner must be orion")

    # Invariant 4: Initial stage sequence
    owners = [stage.get("owner") for stage in stages]
    result.require(
        owners[:4] == ["aurora", "aurora", "frame", "lens"],
        "UI workflow must begin AURORA discovery/candidates -> FRAME visual spikes -> LENS blind tournament",
    )

    # Invariant 5: Artifact producer permissions and consumer precedence
    produced_artifacts: set[str] = set()
    stage_by_id = {s.get("id"): s for s in stages}

    for stage in stages:
        owner = stage.get("owner")
        stage_id = stage.get("id")
        outputs = stage.get("outputs", [])

        if owner == "original-verifier":
            owner_scopes = set(roles.get("lens", {}).get("allowed_write_scopes", [])) & set(roles.get("prism", {}).get("allowed_write_scopes", []))
        elif owner in roles:
            owner_scopes = set(roles[owner].get("allowed_write_scopes", []))
        else:
            owner_scopes = set()

        for out in outputs:
            required_scope = ARTIFACT_SCOPE_MAP.get(out)
            if required_scope:
                result.require(
                    required_scope in owner_scopes,
                    f"stage {stage_id} owner {owner} produces {out} without scope {required_scope}",
                )

        inputs = stage.get("inputs", [])
        for inp in inputs:
            result.require(
                inp in produced_artifacts,
                f"stage {stage_id} consumes unproduced artifact: {inp}",
            )

        for out in outputs:
            produced_artifacts.add(out)

    # Invariant 6: Creator != Certifier
    blind_tournament = stage_by_id.get("blind-tournament", {})
    result.require(
        blind_tournament.get("owner") != "aurora",
        "Creator != Certifier violation: AURORA cannot certify its own direction in blind-tournament",
    )
    result.require(
        blind_tournament.get("owner") == "lens",
        "LENS must be the certifier/auditor of blind-tournament",
    )

    vertical_slice_gate = stage_by_id.get("vertical-slice-gate", {})
    result.require(
        vertical_slice_gate.get("owner") != "frame",
        "Creator != Certifier violation: FRAME cannot certify its own vertical slice",
    )
    result.require(
        vertical_slice_gate.get("owner") == "lens",
        "LENS must verify vertical-slice-gate",
    )

    impl_stage = stage_by_id.get("implementation", {})
    result.require(impl_stage.get("owner") == "frame", "FRAME must own implementation")

    # Invariant 7: Verifiers cannot mutate Git / production source
    for verifier in ("lens", "prism"):
        v_role = roles.get(verifier, {})
        result.require(
            v_role.get("production_write") is False,
            f"Verifier {verifier} must have production_write: false",
        )
        for forbidden in ("frontend-source", "backend-source", "infrastructure"):
            result.require(
                forbidden not in v_role.get("allowed_write_scopes", []),
                f"Verifier {verifier} cannot have {forbidden} write scope",
            )

    # Invariant 8: FRAME is checkpoint producer
    result.require(
        roles.get("frame", {}).get("production_write") is True,
        "FRAME must have production_write: true to create git checkpoints",
    )

    # Invariant 9: Dual Independent Release Veto
    closure_stage = stage_by_id.get("closure", {})
    result.require(closure_stage.get("owner") == "orion", "ORION must own closure")
    closure_gate_text = " ".join(closure_stage.get("gate", []))
    result.require(
        "PRISM and LENS" in closure_gate_text or ("PRISM" in closure_gate_text and "LENS" in closure_gate_text),
        "Closure stage must require dual PRISM and LENS verification (independent veto)",
    )
    result.require(
        "identical BUILD_SHA" in closure_gate_text or "identical" in closure_gate_text,
        "Closure stage must require identical BUILD_SHA parity",
    )

    # Invariant 10: Bounded NO_WINNER and REWORK exploration loops
    bt_bounds = blind_tournament.get("bounds", {})
    result.require(
        isinstance(bt_bounds.get("max_regeneration_rounds"), int) and bt_bounds["max_regeneration_rounds"] <= 2,
        "blind-tournament must bound max_regeneration_rounds <= 2",
    )
    result.require(
        isinstance(bt_bounds.get("max_total_tournament_attempts"), int) and bt_bounds["max_total_tournament_attempts"] <= 4,
        "blind-tournament must bound max_total_tournament_attempts <= 4",
    )

    remediation_stage = stage_by_id.get("remediation", {})
    rem_bounds = remediation_stage.get("bounds", {})
    result.require(
        isinstance(rem_bounds.get("max_remediation_cycles"), int) and rem_bounds["max_remediation_cycles"] <= 2,
        "remediation stage must bound max_remediation_cycles <= 2",
    )

    # Invariant 11: ORION authority for rollback/promote
    rem_gate_text = " ".join(remediation_stage.get("gate", []))
    result.require(
        "ORION arbitrates" in rem_gate_text or "ORION" in rem_gate_text,
        "ORION must be explicit authority for PROMOTE / KEEP_CURRENT_BEST / ROLLBACK",
    )


def validate_canonical_skills(root: Path, result: Validation) -> None:
    # 1. visual-authoring-core parity between global and profiles/aurora
    global_vac = root / "global/skills/visual-authoring-core/SKILL.md"
    aurora_vac = root / "profiles/aurora/skills/custom/visual-authoring-core/SKILL.md"
    result.require(global_vac.is_file(), "missing global/skills/visual-authoring-core/SKILL.md")
    result.require(aurora_vac.is_file(), "missing profiles/aurora/skills/custom/visual-authoring-core/SKILL.md")
    if global_vac.is_file() and aurora_vac.is_file():
        result.require(
            global_vac.read_bytes() == aurora_vac.read_bytes(),
            "visual-authoring-core SKILL.md checksum drift between global and aurora",
        )

    # 2. anti-ai-slop-universal-principles parity across all 6 locations
    global_upr = root / "global/skills/anti-ai-slop-web-design/references/anti-ai-slop-universal-principles.md"
    result.require(global_upr.is_file(), "missing global anti-ai-slop-universal-principles.md")
    if global_upr.is_file():
        global_upr_bytes = global_upr.read_bytes()
        for prof in ("aurora", "frame", "lens", "orion", "prism"):
            prof_upr = root / f"profiles/{prof}/skills/custom/anti-ai-slop-web-design/references/anti-ai-slop-universal-principles.md"
            result.require(prof_upr.is_file(), f"missing {prof} anti-ai-slop-universal-principles.md")
            if prof_upr.is_file():
                result.require(
                    prof_upr.read_bytes() == global_upr_bytes,
                    f"anti-ai-slop-universal-principles.md checksum drift in profile {prof}",
                )

    # 3. lens-review-contract parity across all 6 locations
    global_lrc = root / "global/skills/anti-ai-slop-web-design/references/lens-review-contract.md"
    result.require(global_lrc.is_file(), "missing global lens-review-contract.md")
    if global_lrc.is_file():
        global_lrc_bytes = global_lrc.read_bytes()
        for prof in ("aurora", "frame", "lens", "orion", "prism"):
            prof_lrc = root / f"profiles/{prof}/skills/custom/anti-ai-slop-web-design/references/lens-review-contract.md"
            result.require(prof_lrc.is_file(), f"missing {prof} lens-review-contract.md")
            if prof_lrc.is_file():
                result.require(
                    prof_lrc.read_bytes() == global_lrc_bytes,
                    f"lens-review-contract.md checksum drift in profile {prof}",
                )

    # 4. anti-ai-slop-web-design/SKILL.md parity across all 6 locations
    global_slop_skill = root / "global/skills/anti-ai-slop-web-design/SKILL.md"
    result.require(global_slop_skill.is_file(), "missing global anti-ai-slop-web-design/SKILL.md")
    if global_slop_skill.is_file():
        global_slop_bytes = global_slop_skill.read_bytes()
        for prof in ("aurora", "frame", "lens", "orion", "prism"):
            prof_slop = root / f"profiles/{prof}/skills/custom/anti-ai-slop-web-design/SKILL.md"
            result.require(prof_slop.is_file(), f"missing {prof} anti-ai-slop-web-design/SKILL.md")
            if prof_slop.is_file():
                result.require(
                    prof_slop.read_bytes() == global_slop_bytes,
                    f"anti-ai-slop-web-design/SKILL.md checksum drift in profile {prof}",
                )


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

    validate_ui_workflow(root, roles, result)
    validate_canonical_skills(root, result)

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
