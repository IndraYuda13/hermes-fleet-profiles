#!/usr/bin/env python3
"""Structural validation for fleet governance and runtime evidence contracts.

The checks here validate machine-readable structure and cross-file relationships
instead of snapshotting prose, so policy wording can evolve without weakening
the contract that the runtime and validators depend on.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

import yaml


FLEET = (
    "orion", "atlas", "aurora", "forge", "frame", "lens",
    "nexus", "prism", "quant", "radar", "sentinel",
)
ALL_PROFILES = set(FLEET) | {"groupbot"}
SUPPORTED_CONTRACT_VERSION = 1

ROLE_REQUIRED_FIELDS = {
    "role_class", "model", "a2a_port", "production_write",
    "allowed_write_scopes", "allowed_root_toolsets",
    "allowed_platform_toolsets", "forbidden_toolsets",
}
CORE_LIVE_CHECKS = {
    "exact-model", "exact-root-toolsets", "exact-platform-toolsets",
    "forbidden-toolsets-absent", "automatic-moa-disabled",
    "hidden-delegation-disabled", "exact-a2a-port", "exact-a2a-peer-mesh",
    "agent-card-reachable",
}
CORE_ATTESTATION_FIELDS = {
    "probe_id", "profile", "role_class", "model", "production_write", "result",
}
KERNEL_EVIDENCE_FIELDS = {
    "mission_id", "task_id", "owner", "verifier", "artifact", "revision",
    "method", "environment", "route", "state", "viewport", "result",
    "defect_ids", "limitations", "timestamp",
}
QUALITY_EVIDENCE_FIELDS = {
    "gate_id", "gate_verdict", "attempt", "critic", "previous_revision", "verdict_reason",
    "supersedes", "acceptance", "artifact_proof", "escalation",
}
FINAL_REVISION_OWNERS = {"frame", "prism", "lens", "orion"}
MANDATORY_QUALITY_STAGE_IDS = {
    "discovery", "candidate-hypotheses", "visual-spikes", "blind-tournament",
    "contract", "asset-gate", "vertical-slice-gate", "implementation",
    "functional-verification", "rendered-verification", "closure",
}
CONDITIONAL_LEDGER_OUTPUTS = {"DEFECT_LEDGER.json"}
IMMUTABLE_EVIDENCE_FIELDS = {
    "mission_id", "task_id", "owner", "revision", "method", "result",
}


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(value, dict):
        raise ValueError(f"expected mapping in {path}")
    return value


def load_json_mapping(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object in {path}")
    return value


def _is_unique_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(isinstance(item, str) and item for item in value)
        and len(value) == len(set(value))
    )


def _safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    path = PurePosixPath(value.replace("\\", "/"))
    return not path.is_absolute() and ".." not in path.parts and "." not in path.parts


def _schema_allows_type(schema: dict[str, Any], expected: str) -> bool:
    declared = schema.get("type")
    if isinstance(declared, str):
        return declared == expected
    return isinstance(declared, list) and expected in declared


def _instance_matches_type(value: Any, expected: str) -> bool:
    if expected == "null":
        return value is None
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return True


def _valid_datetime(value: str) -> bool:
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return False
    return parsed.tzinfo is not None


def validate_json_instance(
    value: Any,
    schema: dict[str, Any],
    *,
    path: str = "$",
) -> list[str]:
    """Validate the JSON-Schema subset used by fleet evidence manifests."""

    errors: list[str] = []
    declared_type = schema.get("type")
    if declared_type is not None:
        allowed = [declared_type] if isinstance(declared_type, str) else declared_type
        if not isinstance(allowed, list) or not all(isinstance(item, str) for item in allowed):
            return [f"{path}: schema has invalid type declaration"]
        if not any(_instance_matches_type(value, expected) for expected in allowed):
            errors.append(f"{path}: expected type {allowed}, got {type(value).__name__}")
            return errors

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value {value!r} is outside enum {schema['enum']!r}")

    if isinstance(value, str):
        min_length = schema.get("minLength")
        if isinstance(min_length, int) and len(value) < min_length:
            errors.append(f"{path}: string shorter than minLength={min_length}")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, value) is None:
            errors.append(f"{path}: string does not match required pattern")
        if schema.get("format") == "date-time" and not _valid_datetime(value):
            errors.append(f"{path}: invalid RFC3339/ISO-8601 date-time")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if isinstance(minimum, (int, float)) and value < minimum:
            errors.append(f"{path}: value below minimum={minimum}")
        if isinstance(maximum, (int, float)) and value > maximum:
            errors.append(f"{path}: value above maximum={maximum}")

    if isinstance(value, list):
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(value) < min_items:
            errors.append(f"{path}: array shorter than minItems={min_items}")
        if schema.get("uniqueItems") is True:
            encoded = [json.dumps(item, sort_keys=True) for item in value]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{path}: array items must be unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(validate_json_instance(item, item_schema, path=f"{path}[{index}]"))

    if isinstance(value, dict):
        required = schema.get("required") or []
        if isinstance(required, list):
            for key in required:
                if key not in value:
                    errors.append(f"{path}: missing required property {key!r}")
        properties = schema.get("properties") or {}
        if isinstance(properties, dict):
            for key, child in value.items():
                child_schema = properties.get(key)
                if isinstance(child_schema, dict):
                    errors.extend(validate_json_instance(child, child_schema, path=f"{path}.{key}"))
                elif schema.get("additionalProperties") is False:
                    errors.append(f"{path}: unexpected property {key!r}")
    return errors


def _validate_versions(documents: dict[str, dict[str, Any]], errors: list[str]) -> None:
    versions: dict[str, int] = {}
    for name, document in documents.items():
        version = document.get("version")
        if not isinstance(version, int) or isinstance(version, bool) or version < 1:
            errors.append(f"{name}: version must be a positive integer")
            continue
        versions[name] = version
    if versions and set(versions.values()) != {SUPPORTED_CONTRACT_VERSION}:
        errors.append(
            "governance contract versions must all match supported version "
            f"{SUPPORTED_CONTRACT_VERSION}: {versions}"
        )


def _validate_roles(roles_doc: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    roles = roles_doc.get("profiles") or {}
    if not isinstance(roles, dict):
        errors.append("roles.yaml: profiles must be a mapping")
        return {}
    if set(roles) != ALL_PROFILES:
        errors.append("roles.yaml: profiles must contain the exact fleet plus groupbot")

    ports: list[int] = []
    for profile, role in roles.items():
        if not isinstance(role, dict):
            errors.append(f"roles.yaml: {profile} must be a mapping")
            continue
        missing = ROLE_REQUIRED_FIELDS - set(role)
        if missing:
            errors.append(f"roles.yaml: {profile} missing fields {sorted(missing)}")
        if not isinstance(role.get("role_class"), str) or not role.get("role_class"):
            errors.append(f"roles.yaml: {profile}.role_class must be a non-empty string")
        if not isinstance(role.get("model"), str) or not role.get("model"):
            errors.append(f"roles.yaml: {profile}.model must be a non-empty string")
        if not isinstance(role.get("production_write"), bool):
            errors.append(f"roles.yaml: {profile}.production_write must be boolean")
        for field in (
            "allowed_write_scopes", "allowed_root_toolsets",
            "allowed_platform_toolsets", "forbidden_toolsets",
        ):
            if not _is_unique_string_list(role.get(field)):
                errors.append(f"roles.yaml: {profile}.{field} must be unique non-empty strings")

        allowed = set(role.get("allowed_root_toolsets") or []) | set(
            role.get("allowed_platform_toolsets") or []
        )
        forbidden = set(role.get("forbidden_toolsets") or [])
        overlap = allowed & forbidden
        if overlap:
            errors.append(
                f"roles.yaml: {profile} allows and forbids the same toolsets: {sorted(overlap)}"
            )

        port = role.get("a2a_port")
        if profile == "groupbot":
            if port is not None:
                errors.append("roles.yaml: groupbot.a2a_port must be null")
        elif not isinstance(port, int) or isinstance(port, bool) or not (1 <= port <= 65535):
            errors.append(f"roles.yaml: {profile}.a2a_port must be a valid TCP port")
        else:
            ports.append(port)
    if len(ports) != len(set(ports)):
        errors.append("roles.yaml: A2A ports must be unique")
    return roles


def _validate_quality_contracts(
    roles_doc: dict[str, Any],
    runtime: dict[str, Any],
    workflow: dict[str, Any],
    gauntlet: dict[str, Any],
    roles: dict[str, Any],
    errors: list[str],
) -> None:
    role_quality = roles_doc.get("quality_governance")
    runtime_quality = runtime.get("orchestration_quality_contract")
    workflow_quality = workflow.get("quality_policy")
    gauntlet_quality = gauntlet.get("quality_contract")
    named = {
        "roles.yaml quality_governance": role_quality,
        "runtime-smoke.yaml orchestration_quality_contract": runtime_quality,
        "ui workflow quality_policy": workflow_quality,
        "ui gauntlet quality_contract": gauntlet_quality,
    }
    for name, value in named.items():
        if not isinstance(value, dict) or not value:
            errors.append(f"{name} must be a non-empty mapping")
    if not all(isinstance(value, dict) and value for value in named.values()):
        return

    if any(value.get("creator_may_final_certify") is not False for value in named.values()):
        errors.append("quality contracts: creator_may_final_certify must be false everywhere")
    if role_quality.get("orion_may_substitute_for_verifier") is not False:
        errors.append("quality contracts: ORION may not substitute for an independent verifier")
    if role_quality.get("retest_owner") != "original-verifier":
        errors.append("quality contracts: retest owner must remain original-verifier")
    if role_quality.get("escalation_coordinator") != "orion":
        errors.append("quality contracts: escalation coordinator must remain ORION")

    veto_profiles = role_quality.get("ui_release_veto_profiles")
    runtime_veto = runtime_quality.get("ui_release_veto_profiles")
    if not _is_unique_string_list(veto_profiles) or veto_profiles != runtime_veto:
        errors.append("quality contracts: UI release veto profile lists must match")
    else:
        for profile in veto_profiles:
            role = roles.get(profile) or {}
            if role.get("role_class") != "verifier" or role.get("production_write") is not False:
                errors.append(f"quality contracts: veto profile {profile} must be a non-writing verifier")

    floor_values = [
        runtime_quality.get("ui_acceptance_floor"),
        workflow_quality.get("ui_acceptance_floor"),
        gauntlet_quality.get("ui_acceptance_floor"),
    ]
    if not all(isinstance(value, dict) and value for value in floor_values):
        errors.append("quality contracts: UI acceptance floor must exist in runtime/workflow/gauntlet")
    elif not all(value == floor_values[0] for value in floor_values[1:]):
        errors.append("quality contracts: UI acceptance floors drift across runtime/workflow/gauntlet")
    else:
        floor = floor_values[0]
        if floor.get("schema") != "CALIBRATION_V0":
            errors.append("quality contracts: UI acceptance floor schema must be CALIBRATION_V0")
        if floor.get("calibration_status") != "UNCALIBRATED_HEURISTIC":
            errors.append("quality contracts: CALIBRATION_V0 must be labeled UNCALIBRATED_HEURISTIC")
        if floor.get("absolute_benchmark_claim_allowed") is not False:
            errors.append("quality contracts: uncalibrated UI scores may not authorize absolute benchmark claims")
        if not isinstance(floor.get("minimum_weighted_total"), (int, float)) or floor["minimum_weighted_total"] <= 0:
            errors.append("quality contracts: minimum_weighted_total must be positive")
        if not isinstance(floor.get("minimum_dimension_score"), (int, float)) or floor["minimum_dimension_score"] <= 0:
            errors.append("quality contracts: minimum_dimension_score must be positive")
        if floor.get("all_applicable_hard_checks_true") is not True:
            errors.append("quality contracts: all applicable hard checks must be required")
        if floor.get("maximum_blocking_findings") != 0:
            errors.append("quality contracts: maximum blocking findings must remain zero")

    workflow_functional = workflow_quality.get("functional_acceptance_floor")
    gauntlet_functional = gauntlet_quality.get("functional_acceptance_floor")
    if not isinstance(workflow_functional, dict) or workflow_functional != gauntlet_functional:
        errors.append("quality contracts: functional acceptance floors must match workflow and gauntlet")

    stage_by_id = {
        stage.get("id"): stage
        for stage in (workflow.get("stages") or [])
        if isinstance(stage, dict) and isinstance(stage.get("id"), str)
    }
    remediation_stage = stage_by_id.get("remediation") or {}
    stage_cycles = (remediation_stage.get("bounds") or {}).get("max_remediation_cycles")
    cycle_values = [
        (runtime_quality.get("remediation") or {}).get("max_cycles"),
        (workflow_quality.get("remediation") or {}).get("max_cycles"),
        gauntlet_quality.get("max_remediation_cycles"),
        stage_cycles,
    ]
    if not all(isinstance(value, int) and not isinstance(value, bool) and value > 0 for value in cycle_values):
        errors.append("quality contracts: remediation cycle budgets must be positive integers")
    elif len(set(cycle_values)) != 1:
        errors.append(f"quality contracts: remediation cycle budget drift {cycle_values}")

    runtime_remediation = runtime_quality.get("remediation") or {}
    workflow_remediation = workflow_quality.get("remediation") or {}
    if runtime_remediation.get("mode") != "revise-until-pass-or-escalate":
        errors.append("quality contracts: runtime remediation mode must revise until pass or escalate")
    if workflow_remediation.get("mode") != "revise-until-pass-or-escalate":
        errors.append("quality contracts: workflow remediation mode must revise until pass or escalate")
    if gauntlet_quality.get("revise_until_pass_or_escalate") is not True:
        errors.append("quality contracts: gauntlet must require revise-until-pass-or-escalate")
    retest_flags = [
        runtime_remediation.get("original_verifier_retest_required"),
        workflow_remediation.get("original_verifier_retests"),
        gauntlet_quality.get("original_verifier_retest_required"),
    ]
    if any(value is not True for value in retest_flags):
        errors.append("quality contracts: original verifier retest must be required everywhere")
    revision_flags = [
        runtime_remediation.get("fresh_revision_required"),
        workflow_remediation.get("fresh_revision_each_cycle"),
        gauntlet_quality.get("fresh_revision_per_remediation"),
    ]
    if any(value is not True for value in revision_flags):
        errors.append("quality contracts: every remediation cycle must require a fresh revision")
    if workflow_remediation.get("failed_criteria_plus_invalidated_regressions_rerun") is not True:
        errors.append("quality contracts: remediation retest must include invalidated regressions")

    override_values = [
        role_quality.get("threshold_override_allowed"),
        (runtime_quality.get("escalation") or {}).get("threshold_override_allowed"),
        (workflow_quality.get("escalation") or {}).get("threshold_override_allowed"),
        (gauntlet_quality.get("escalation") or {}).get("threshold_override_allowed"),
    ]
    if any(value is not False for value in override_values):
        errors.append("quality contracts: threshold overrides must be disabled everywhere")

    if role_quality.get("stale_evidence_reuse_allowed") is not False:
        errors.append("quality contracts: roles must forbid stale evidence reuse")
    if runtime_quality.get("stale_evidence_reuse_allowed") is not False:
        errors.append("quality contracts: runtime must forbid stale evidence reuse")
    if workflow_quality.get("stale_evidence_rejected") is not True:
        errors.append("quality contracts: workflow must explicitly reject stale evidence")

    verdicts = workflow_quality.get("gate_verdicts") or []
    if not _is_unique_string_list(verdicts) or not {"PASS", "REVISE", "BLOCKED"} <= set(verdicts):
        errors.append("quality contracts: workflow gate_verdicts must include PASS, REVISE and BLOCKED")

    workflow_proof = workflow_quality.get("artifact_proof") or {}
    gauntlet_proof = gauntlet_quality.get("proof_policy") or {}
    runtime_exact = runtime_quality.get("exact_revision_parity_required")
    if workflow_proof.get("criterion_to_evidence_mapping_required") is not True:
        errors.append("quality contracts: workflow must require criterion-to-evidence mapping")
    if gauntlet_proof.get("criterion_to_evidence_mapping_required") is not True:
        errors.append("quality contracts: gauntlet must require criterion-to-evidence mapping")
    if workflow_proof.get("exact_revision_required") is not True:
        errors.append("quality contracts: workflow proof must bind exact revision")
    if gauntlet_proof.get("exact_revision_required") is not True:
        errors.append("quality contracts: gauntlet proof must bind exact revision")
    if runtime_exact is not True or gauntlet_quality.get("exact_revision_parity_required") is not True:
        errors.append("quality contracts: runtime and gauntlet must require exact revision parity")

    runtime_escalation = runtime_quality.get("escalation") or {}
    workflow_escalation = workflow_quality.get("escalation") or {}
    gauntlet_escalation = gauntlet_quality.get("escalation") or {}
    blocked_escalations = (
        runtime_escalation.get("exhausted_budget"),
        runtime_escalation.get("missing_required_proof"),
        runtime_escalation.get("mandatory_verifier_unavailable"),
        workflow_escalation.get("exhausted_budget"),
        workflow_escalation.get("mandatory_verifier_unavailable"),
        workflow_proof.get("missing_required_proof"),
        gauntlet_escalation.get("exhausted_remediation_budget"),
        gauntlet_escalation.get("missing_required_proof"),
        gauntlet_escalation.get("mandatory_verifier_unavailable"),
    )
    if any(value != "BLOCKED" for value in blocked_escalations):
        errors.append("quality contracts: exhausted budget, missing proof and unavailable verifier must fail closed as BLOCKED")


def _validate_runtime_pack(
    runtime: dict[str, Any], roles: dict[str, Any], errors: list[str]
) -> None:
    if runtime.get("protocol") != "a2a-v1":
        errors.append("runtime-smoke.yaml: protocol must remain a2a-v1 for this harness")
    for field in ("card_path", "rpc_path"):
        value = runtime.get(field)
        if not isinstance(value, str) or not value.startswith("/"):
            errors.append(f"runtime-smoke.yaml: {field} must be an absolute HTTP path")

    profiles = runtime.get("a2a_profiles") or []
    if not _is_unique_string_list(profiles) or tuple(profiles) != FLEET:
        errors.append("runtime-smoke.yaml: a2a_profiles must be the ordered 11-profile fleet")

    live_checks = runtime.get("required_live_checks") or []
    if not _is_unique_string_list(live_checks):
        errors.append("runtime-smoke.yaml: required_live_checks must be unique strings")
    else:
        missing_checks = CORE_LIVE_CHECKS - set(live_checks)
        if missing_checks:
            errors.append(f"runtime-smoke.yaml: missing required live checks {sorted(missing_checks)}")

    probes = runtime.get("boundary_probes") or {}
    if not isinstance(probes, dict) or set(probes) != set(FLEET):
        errors.append("runtime-smoke.yaml: boundary_probes must cover every A2A profile")
        return

    artifacts: list[str] = []
    allowed_effects = {
        "deny-production-write", "allow-scoped-write", "require-kanban-authorization",
    }
    for profile, spec in probes.items():
        if not isinstance(spec, dict):
            errors.append(f"runtime-smoke.yaml: probe {profile} must be a mapping")
            continue
        effect = spec.get("effect")
        if effect not in allowed_effects:
            errors.append(f"runtime-smoke.yaml: probe {profile} has unknown effect {effect!r}")
        artifact = spec.get("artifact")
        if not _safe_relative_path(artifact):
            errors.append(f"runtime-smoke.yaml: probe {profile} artifact is not a safe relative path")
        elif isinstance(artifact, str):
            artifacts.append(artifact.replace("\\", "/"))

        role = roles.get(profile) if isinstance(roles, dict) else None
        if isinstance(role, dict):
            expected = (
                "require-kanban-authorization"
                if profile == "atlas"
                else "allow-scoped-write"
                if role.get("production_write") is True
                else "deny-production-write"
            )
            if effect != expected:
                errors.append(f"runtime-smoke.yaml: probe {profile} effect {effect!r} != {expected!r}")
    if len(artifacts) != len(set(artifacts)):
        errors.append("runtime-smoke.yaml: boundary probe artifacts must be unique")

    attestation = runtime.get("attestation") or {}
    if not isinstance(attestation, dict):
        errors.append("runtime-smoke.yaml: attestation must be a mapping")
        return
    if not isinstance(attestation.get("marker"), str) or not attestation.get("marker", "").strip():
        errors.append("runtime-smoke.yaml: attestation.marker must be non-empty")
    required_fields = attestation.get("required_fields") or []
    if not _is_unique_string_list(required_fields):
        errors.append("runtime-smoke.yaml: attestation.required_fields must be unique strings")
    else:
        missing = CORE_ATTESTATION_FIELDS - set(required_fields)
        if missing:
            errors.append(f"runtime-smoke.yaml: attestation missing required fields {sorted(missing)}")
    allowed_results = attestation.get("allowed_results") or []
    if not _is_unique_string_list(allowed_results) or not {"PASS", "BLOCKED"} <= set(allowed_results):
        errors.append("runtime-smoke.yaml: attestation.allowed_results must include PASS and BLOCKED")
    aliases = attestation.get("role_class_aliases") or {}
    if not isinstance(aliases, dict) or not set(aliases) <= set(FLEET):
        errors.append("runtime-smoke.yaml: role_class_aliases contains unknown profiles")
    elif any(not _is_unique_string_list(value) for value in aliases.values()):
        errors.append("runtime-smoke.yaml: every role_class alias list must be unique strings")


def _validate_evidence_schema(schema: dict[str, Any], errors: list[str]) -> None:
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append("evidence schema: unsupported JSON Schema dialect")
    if schema.get("type") != "object":
        errors.append("evidence schema: root type must be object")
    if schema.get("additionalProperties") is not False:
        errors.append("evidence schema: additionalProperties must be false")
    properties = schema.get("properties") or {}
    if not isinstance(properties, dict):
        errors.append("evidence schema: properties must be an object")
        return
    missing_properties = (KERNEL_EVIDENCE_FIELDS | QUALITY_EVIDENCE_FIELDS) - set(properties)
    if missing_properties:
        errors.append(f"evidence schema: missing contract fields {sorted(missing_properties)}")
    required = schema.get("required") or []
    if not _is_unique_string_list(required):
        errors.append("evidence schema: required must be unique strings")
    elif not {
        "mission_id", "task_id", "owner", "verifier", "revision",
        "method", "result", "timestamp",
    } <= set(required):
        errors.append("evidence schema: core runtime identity fields must remain required")
    result_schema = properties.get("result") or {}
    if not {"PASS", "FAIL", "BLOCKED"} <= set(result_schema.get("enum") or []):
        errors.append("evidence schema: result enum must include PASS, FAIL and BLOCKED")
    gate_schema = properties.get("gate_verdict") or {}
    if set(gate_schema.get("enum") or []) != {"PASS", "REVISE", "BLOCKED"}:
        errors.append("evidence schema: gate_verdict enum must be PASS, REVISE and BLOCKED")
    timestamp_schema = properties.get("timestamp") or {}
    if timestamp_schema.get("format") != "date-time":
        errors.append("evidence schema: timestamp must use date-time format")
    acceptance = properties.get("acceptance") or {}
    acceptance_props = acceptance.get("properties") or {}
    criteria = acceptance_props.get("criteria") or {}
    criteria_item = criteria.get("items") or {}
    if not isinstance(criteria_item, dict) or not {"id", "status", "evidence"} <= set(
        criteria_item.get("required") or []
    ):
        errors.append("evidence schema: acceptance criteria must bind id/status/evidence")
    proof = properties.get("artifact_proof") or {}
    proof_item = proof.get("items") or {}
    if not isinstance(proof_item, dict) or not {"kind", "locator"} <= set(proof_item.get("required") or []):
        errors.append("evidence schema: artifact_proof entries must require kind and locator")


def _validate_workflow_and_gauntlet(
    workflow: dict[str, Any],
    gauntlet: dict[str, Any],
    schema: dict[str, Any],
    roles: dict[str, Any],
    errors: list[str],
) -> None:
    stages = workflow.get("stages") or []
    if not isinstance(stages, list) or not stages:
        errors.append("ui workflow: stages must be a non-empty list")
        return
    stage_by_id: dict[str, dict[str, Any]] = {}
    for stage in stages:
        if not isinstance(stage, dict):
            errors.append("ui workflow: every stage must be a mapping")
            continue
        stage_id = stage.get("id")
        if not isinstance(stage_id, str) or not stage_id:
            continue
        stage_by_id[stage_id] = stage
        gates = stage.get("gate")
        if not isinstance(gates, list) or not gates or any(
            not isinstance(item, (str, dict)) or not item for item in gates
        ):
            errors.append(f"ui workflow: stage {stage_id} must define non-empty gate clauses")

    missing_quality_stages = MANDATORY_QUALITY_STAGE_IDS - set(stage_by_id)
    if missing_quality_stages:
        errors.append(f"ui workflow: missing mandatory quality stages {sorted(missing_quality_stages)}")

    required_artifacts = gauntlet.get("required_artifacts") or []
    if not _is_unique_string_list(required_artifacts):
        errors.append("ui gauntlet: required_artifacts must be unique strings")
        required_artifact_set: set[str] = set()
    else:
        required_artifact_set = set(required_artifacts)
        unsafe = [item for item in required_artifacts if not _safe_relative_path(item)]
        if unsafe:
            errors.append(f"ui gauntlet: unsafe required artifact paths {unsafe}")

    quality_outputs: set[str] = set()
    for stage_id in MANDATORY_QUALITY_STAGE_IDS:
        stage = stage_by_id.get(stage_id)
        if not stage:
            continue
        outputs = stage.get("outputs") or []
        if not _is_unique_string_list(outputs):
            errors.append(f"ui workflow: stage {stage_id} outputs must be unique strings")
            continue
        quality_outputs.update(
            output for output in outputs
            if output.lower().endswith((".md", ".json"))
            and output not in CONDITIONAL_LEDGER_OUTPUTS
        )
    missing_outputs = quality_outputs - required_artifact_set
    if missing_outputs:
        errors.append(
            "ui gauntlet: required_artifacts omits mandatory quality-contract outputs "
            f"{sorted(missing_outputs)}"
        )

    manifests = gauntlet.get("required_manifests") or []
    owners = gauntlet.get("expected_owners") or {}
    if not _is_unique_string_list(manifests):
        errors.append("ui gauntlet: required_manifests must be unique strings")
        manifest_set: set[str] = set()
    else:
        manifest_set = set(manifests)
        unsafe = [item for item in manifests if not _safe_relative_path(item)]
        if unsafe:
            errors.append(f"ui gauntlet: unsafe manifest paths {unsafe}")
    if not isinstance(owners, dict) or set(owners) != manifest_set:
        errors.append("ui gauntlet: expected_owners keys must exactly match required_manifests")
        owners = owners if isinstance(owners, dict) else {}
    invalid_owners = set(owners.values()) - set(roles)
    if invalid_owners:
        errors.append(f"ui gauntlet: unknown manifest owners {sorted(invalid_owners)}")

    preflight = gauntlet.get("model_preflight_profiles") or []
    if not _is_unique_string_list(preflight) or set(preflight) != set(owners.values()):
        errors.append("ui gauntlet: model_preflight_profiles must cover manifest-producing owners")

    parity = gauntlet.get("revision_parity_manifests") or []
    if not _is_unique_string_list(parity) or not set(parity) <= manifest_set:
        errors.append("ui gauntlet: revision_parity_manifests must be a subset of required_manifests")
    else:
        parity_owners = {owners.get(path) for path in parity}
        if parity_owners != FINAL_REVISION_OWNERS:
            errors.append("ui gauntlet: final revision parity must cover FRAME, PRISM, LENS and ORION")

    schema_properties = schema.get("properties") or {}
    true_fields = gauntlet.get("manifest_required_true_fields") or {}
    if not isinstance(true_fields, dict) or not set(true_fields) <= manifest_set:
        errors.append("ui gauntlet: manifest_required_true_fields must reference required manifests")
    elif isinstance(schema_properties, dict):
        for manifest, fields in true_fields.items():
            if not _is_unique_string_list(fields):
                errors.append(f"ui gauntlet: {manifest} required true fields must be unique strings")
                continue
            for field in fields:
                field_schema = schema_properties.get(field)
                if not isinstance(field_schema, dict) or not _schema_allows_type(field_schema, "boolean"):
                    errors.append(
                        f"ui gauntlet: true field {field!r} is absent or non-boolean in evidence schema"
                    )

    required_criteria = gauntlet.get("manifest_required_criteria") or {}
    if not isinstance(required_criteria, dict) or not set(required_criteria) <= manifest_set:
        errors.append("ui gauntlet: manifest_required_criteria must reference required manifests")
    elif any(not _is_unique_string_list(criteria) for criteria in required_criteria.values()):
        errors.append("ui gauntlet: every manifest_required_criteria entry must be unique non-empty strings")

    reconcilable = gauntlet.get("manifest_reconcilable_fields") or []
    if not _is_unique_string_list(reconcilable):
        errors.append("ui gauntlet: manifest_reconcilable_fields must be unique strings")
    elif isinstance(schema_properties, dict):
        missing = set(reconcilable) - set(schema_properties)
        if missing:
            errors.append(f"ui gauntlet: reconcilable fields missing from evidence schema {sorted(missing)}")
        immutable = set(reconcilable) & IMMUTABLE_EVIDENCE_FIELDS
        if immutable:
            errors.append(f"ui gauntlet: immutable evidence fields cannot be reconciled {sorted(immutable)}")

    viewports = workflow.get("minimum_viewports") or []
    viewport_widths: list[int] = []
    viewport_names: list[str] = []
    if not isinstance(viewports, list) or not viewports:
        errors.append("ui workflow: minimum_viewports must be a non-empty list")
    else:
        for viewport in viewports:
            if not isinstance(viewport, dict):
                errors.append("ui workflow: each minimum viewport must be a mapping")
                continue
            name = viewport.get("name")
            width = viewport.get("width")
            if not isinstance(name, str) or not name:
                errors.append("ui workflow: viewport name must be non-empty")
            else:
                viewport_names.append(name)
            if not isinstance(width, int) or isinstance(width, bool) or width <= 0:
                errors.append(f"ui workflow: viewport {name!r} width must be positive integer")
            else:
                viewport_widths.append(width)
        if len(viewport_names) != len(set(viewport_names)):
            errors.append("ui workflow: viewport names must be unique")
        if len(viewport_widths) != len(set(viewport_widths)):
            errors.append("ui workflow: viewport widths must be unique")

    screenshots = gauntlet.get("required_screenshots") or []
    screenshot_widths: list[int] = []
    screenshot_paths: list[str] = []
    if not isinstance(screenshots, list) or not screenshots:
        errors.append("ui gauntlet: required_screenshots must be a non-empty list")
    else:
        for screenshot in screenshots:
            if not isinstance(screenshot, dict):
                errors.append("ui gauntlet: screenshot entries must be mappings")
                continue
            path = screenshot.get("path")
            width = screenshot.get("width")
            if not _safe_relative_path(path):
                errors.append("ui gauntlet: screenshot path must be safe and relative")
            elif isinstance(path, str):
                screenshot_paths.append(path.replace("\\", "/"))
            if not isinstance(width, int) or isinstance(width, bool) or width <= 0:
                errors.append(f"ui gauntlet: screenshot width {width!r} must be positive integer")
            else:
                screenshot_widths.append(width)
        if len(screenshot_paths) != len(set(screenshot_paths)):
            errors.append("ui gauntlet: screenshot paths must be unique")
        if len(screenshot_widths) != len(set(screenshot_widths)):
            errors.append("ui gauntlet: screenshot widths must be unique")
    if viewport_widths and screenshot_widths and set(viewport_widths) != set(screenshot_widths):
        errors.append("UI viewport contract drift: workflow minimum_viewports and gauntlet screenshots differ")


def validate_contract_documents(
    roles_doc: dict[str, Any],
    runtime: dict[str, Any],
    workflow: dict[str, Any],
    gauntlet: dict[str, Any],
    schema: dict[str, Any],
) -> list[str]:
    """Validate already-loaded machine-readable fleet contracts."""

    errors: list[str] = []
    documents = {
        "roles": roles_doc,
        "runtime-smoke": runtime,
        "ui-workflow": workflow,
        "ui-gauntlet": gauntlet,
    }
    _validate_versions(documents, errors)
    roles = _validate_roles(roles_doc, errors)
    _validate_runtime_pack(runtime, roles, errors)
    _validate_evidence_schema(schema, errors)
    _validate_quality_contracts(
        roles_doc, runtime, workflow, gauntlet, roles, errors,
    )
    _validate_workflow_and_gauntlet(workflow, gauntlet, schema, roles, errors)
    return errors


def validate_repository_contracts(root: Path) -> list[str]:
    """Return structural contract errors for a repository checkout."""

    errors: list[str] = []
    paths = {
        "roles": root / "governance/roles.yaml",
        "runtime-smoke": root / "governance/runtime-smoke.yaml",
        "ui-workflow": root / "governance/workflows/ui-prototype.yaml",
        "ui-gauntlet": root / "governance/gauntlets/ui-prototype.yaml",
    }
    documents: dict[str, dict[str, Any]] = {}
    for name, path in paths.items():
        if not path.is_file():
            errors.append(f"missing {path.relative_to(root)}")
            continue
        try:
            documents[name] = load_yaml_mapping(path)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            errors.append(f"invalid {path.relative_to(root)}: {exc}")

    schema_path = root / "governance/schemas/evidence-manifest.schema.json"
    schema: dict[str, Any] = {}
    if not schema_path.is_file():
        errors.append(f"missing {schema_path.relative_to(root)}")
    else:
        try:
            schema = load_json_mapping(schema_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"invalid {schema_path.relative_to(root)}: {exc}")

    if (
        all(name in documents for name in paths)
        and schema
    ):
        errors.extend(
            validate_contract_documents(
                documents["roles"],
                documents["runtime-smoke"],
                documents["ui-workflow"],
                documents["ui-gauntlet"],
                schema,
            )
        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args()
    root = args.repo_root.resolve()
    errors = validate_repository_contracts(root)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"Fleet contracts: FAIL ({len(errors)} error(s))")
        return 1
    print("Fleet contracts: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
