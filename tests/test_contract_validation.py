import copy
import json
import unittest
from pathlib import Path

import yaml

from scripts.validate_contracts import (
    validate_contract_documents,
    validate_json_instance,
    validate_repository_contracts,
)


ROOT = Path(__file__).resolve().parents[1]


class FleetContractValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roles = yaml.safe_load(
            (ROOT / "governance/roles.yaml").read_text(encoding="utf-8")
        )
        cls.runtime = yaml.safe_load(
            (ROOT / "governance/runtime-smoke.yaml").read_text(encoding="utf-8")
        )
        cls.workflow = yaml.safe_load(
            (ROOT / "governance/workflows/ui-prototype.yaml").read_text(encoding="utf-8")
        )
        cls.gauntlet = yaml.safe_load(
            (ROOT / "governance/gauntlets/ui-prototype.yaml").read_text(encoding="utf-8")
        )
        cls.schema = json.loads(
            (ROOT / "governance/schemas/evidence-manifest.schema.json").read_text(
                encoding="utf-8"
            )
        )

    def validate_mutation(self, *, roles=None, runtime=None, workflow=None, gauntlet=None, schema=None):
        return validate_contract_documents(
            copy.deepcopy(roles if roles is not None else self.roles),
            copy.deepcopy(runtime if runtime is not None else self.runtime),
            copy.deepcopy(workflow if workflow is not None else self.workflow),
            copy.deepcopy(gauntlet if gauntlet is not None else self.gauntlet),
            copy.deepcopy(schema if schema is not None else self.schema),
        )

    def test_repository_contracts_pass(self):
        self.assertEqual(validate_repository_contracts(ROOT), [])

    def test_quality_floor_drift_fails_closed(self):
        gauntlet = copy.deepcopy(self.gauntlet)
        gauntlet["quality_contract"]["ui_acceptance_floor"]["minimum_weighted_total"] -= 1
        errors = self.validate_mutation(gauntlet=gauntlet)
        self.assertTrue(any("UI acceptance floors drift" in error for error in errors))

    def test_missing_machine_readable_quality_contract_is_rejected(self):
        workflow = copy.deepcopy(self.workflow)
        del workflow["quality_policy"]
        errors = self.validate_mutation(workflow=workflow)
        self.assertTrue(any("quality_policy must be a non-empty mapping" in error for error in errors))

    def test_remediation_cannot_drop_original_verifier_retest(self):
        runtime = copy.deepcopy(self.runtime)
        runtime["orchestration_quality_contract"]["remediation"][
            "original_verifier_retest_required"
        ] = False
        errors = self.validate_mutation(runtime=runtime)
        self.assertTrue(any("original verifier retest" in error for error in errors))

    def test_missing_proof_escalation_must_fail_closed(self):
        gauntlet = copy.deepcopy(self.gauntlet)
        gauntlet["quality_contract"]["escalation"]["missing_required_proof"] = "PASS"
        errors = self.validate_mutation(gauntlet=gauntlet)
        self.assertTrue(any("must fail closed as BLOCKED" in error for error in errors))

    def test_viewport_contract_drift_is_rejected(self):
        gauntlet = copy.deepcopy(self.gauntlet)
        gauntlet["required_screenshots"][-1]["width"] += 1
        errors = self.validate_mutation(gauntlet=gauntlet)
        self.assertTrue(any("viewport contract drift" in error for error in errors))

    def test_missing_quality_artifact_is_rejected(self):
        gauntlet = copy.deepcopy(self.gauntlet)
        gauntlet["required_artifacts"].remove("DESIGN_CONTRACT.md")
        errors = self.validate_mutation(gauntlet=gauntlet)
        self.assertTrue(
            any(
                "required_artifacts omits mandatory quality-contract outputs" in error
                and "DESIGN_CONTRACT.md" in error
                for error in errors
            )
        )

    def test_boundary_probe_cannot_escape_staging_workspace(self):
        runtime = copy.deepcopy(self.runtime)
        runtime["boundary_probes"]["frame"]["artifact"] = "../outside.txt"
        errors = self.validate_mutation(runtime=runtime)
        self.assertTrue(any("artifact is not a safe relative path" in error for error in errors))

    def test_gauntlet_true_field_must_exist_as_boolean_in_schema(self):
        gauntlet = copy.deepcopy(self.gauntlet)
        gauntlet["manifest_required_true_fields"][
            "evidence/manifests/lens-rendered.json"
        ].append("imaginary_quality_gate")
        errors = self.validate_mutation(gauntlet=gauntlet)
        self.assertTrue(
            any("imaginary_quality_gate" in error and "non-boolean" in error for error in errors)
        )

    def test_evidence_instance_enforces_nested_quality_proof(self):
        manifest = {
            "mission_id": "UI-TEST",
            "task_id": "task-lens",
            "owner": "lens",
            "verifier": "lens",
            "revision": "abcdef123456",
            "method": "rendered inspection",
            "result": "PASS",
            "gate_verdict": "PASS",
            "timestamp": "2026-09-15T06:00:00Z",
            "gate_id": "rendered-verification",
            "attempt": 1,
            "acceptance": {
                "hard_gates_passed": True,
                "thresholds_met": True,
                "blocking_findings": 0,
                "weighted_score": 91,
                "minimum_dimension_score": 8.5,
                "criteria": [
                    {
                        "id": "visual-hierarchy",
                        "status": "PASS",
                        "evidence": ["evidence/screenshots/home-desktop.png"],
                    }
                ],
            },
            "artifact_proof": [
                {
                    "kind": "screenshot",
                    "locator": "evidence/screenshots/home-desktop.png",
                    "sha256": "a" * 64,
                    "criterion_ids": ["visual-hierarchy"],
                }
            ],
        }
        self.assertEqual(validate_json_instance(manifest, self.schema), [])

        invalid = copy.deepcopy(manifest)
        invalid["timestamp"] = "not-a-date"
        invalid["acceptance"]["weighted_score"] = 101
        invalid["acceptance"]["criteria"][0]["evidence"] = []
        invalid["artifact_proof"][0]["sha256"] = "bad"
        invalid["unexpected"] = True
        errors = validate_json_instance(invalid, self.schema)
        self.assertTrue(any("date-time" in error for error in errors))
        self.assertTrue(any("maximum=100" in error for error in errors))
        self.assertTrue(any("minItems=1" in error for error in errors))
        self.assertTrue(any("required pattern" in error for error in errors))
        self.assertTrue(any("unexpected property 'unexpected'" in error for error in errors))

    def test_uncalibrated_ui_floor_cannot_authorize_absolute_benchmark_claims(self):
        workflow = copy.deepcopy(self.workflow)
        workflow["quality_policy"]["ui_acceptance_floor"]["absolute_benchmark_claim_allowed"] = True
        errors = self.validate_mutation(workflow=workflow)
        self.assertTrue(any("UI acceptance floors drift" in error for error in errors))

        runtime = copy.deepcopy(self.runtime)
        gauntlet = copy.deepcopy(self.gauntlet)
        for document, path in (
            (runtime, ("orchestration_quality_contract", "ui_acceptance_floor")),
            (workflow, ("quality_policy", "ui_acceptance_floor")),
            (gauntlet, ("quality_contract", "ui_acceptance_floor")),
        ):
            target = document[path[0]][path[1]]
            target["absolute_benchmark_claim_allowed"] = False
            target["calibration_status"] = "CALIBRATED"
        errors = self.validate_mutation(runtime=runtime, workflow=workflow, gauntlet=gauntlet)
        self.assertTrue(any("must be labeled UNCALIBRATED_HEURISTIC" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
