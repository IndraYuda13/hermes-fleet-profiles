import copy
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.sanitize_config import sanitize_identity_config, sanitize_text
from scripts.sanitize_skill_examples import sanitize_text as sanitize_skill_text
from scripts.validate_fleet import (
    Validation,
    validate_canonical_skills,
    validate_runtime_core,
    validate_ui_workflow,
)


class SanitizerTests(unittest.TestCase):
    def test_removes_dashboard_and_connector_secrets(self):
        source = """dashboard:
  basic_auth:
    username: admin
    password_hash: hash-value
    secret: signing-value
  auth: password:plaintext
  host: 0.0.0.0
mcp_servers:
  Postman:
    env:
      POSTMAN_API_KEY: PMAK-secret-value
web:
  FIRECRAWL_API_KEY: fc-secret-value
  backend: firecrawl
"""
        cleaned = sanitize_text(source)
        parsed = yaml.safe_load(cleaned)
        self.assertNotIn("basic_auth", parsed["dashboard"])
        self.assertNotIn("auth", parsed["dashboard"])
        self.assertEqual(
            parsed["mcp_servers"]["Postman"]["env"]["POSTMAN_API_KEY"],
            "${POSTMAN_API_KEY}",
        )
        self.assertEqual(parsed["web"]["FIRECRAWL_API_KEY"], "${FIRECRAWL_API_KEY}")
        self.assertEqual(parsed["dashboard"]["host"], "0.0.0.0")

    def test_redacts_generic_secret_scalar(self):
        cleaned = sanitize_text("provider:\n  api_key: live-secret\n  model: x\n")
        self.assertEqual(yaml.safe_load(cleaned)["provider"]["api_key"], "REDACTED")

    def test_redacts_mcp_bearer_header_to_connector_env(self):
        source = """mcp_servers:
  monetag:
    url: https://example.invalid/mcp
    headers:
      Authorization: Bearer literal-secret-value
"""
        cleaned = sanitize_text(source)
        parsed = yaml.safe_load(cleaned)
        self.assertEqual(
            parsed["mcp_servers"]["monetag"]["headers"]["Authorization"],
            "Bearer ${MONETAG_MCP_TOKEN}",
        )

    def test_removes_chat_identifiers(self):
        source = """platforms:
  whatsapp:
    enabled: true
    extra:
      allow_from: ['6281111111111']
      group_allowed_chats: ['120000000000@g.us']
      mention_patterns: ['@6281111111111', 'AW.ai']
"""
        parsed = yaml.safe_load(sanitize_identity_config(source, "groupbot"))
        extra = parsed["platforms"]["whatsapp"]["extra"]
        self.assertEqual(extra["allow_from"], [])
        self.assertEqual(extra["group_allowed_chats"], [])
        self.assertEqual(extra["mention_patterns"], ["AW.ai"])

    def test_sanitizes_credential_shaped_skill_examples(self):
        sk_example = "sk-" + "123456789012345678901234"
        gh_example = "ghp_" + "123456789012345678901234567890123456"
        source = f"token={sk_example} and {gh_example}"
        cleaned = sanitize_skill_text(source)
        self.assertNotIn(sk_example, cleaned)
        self.assertNotIn(gh_example, cleaned)
        self.assertIn("REDACTED_EXAMPLE", cleaned)

    def test_sanitizes_whatsapp_identifiers(self):
        source = "allow_from: 6281111111111 group: 120000000000@g.us mention: @6282222222222"
        cleaned = sanitize_skill_text(source, Path("skills/whatsapp-platform-operations/SKILL.md"))
        self.assertNotRegex(cleaned, r"\d{10,}")

    def test_removes_nofx_credential_database_bypass(self):
        source = """### Adding/Modifying AI Models
dek = "sensitive-value"
## Known Troubleshooting Pitfalls
### Hyperliquid
- **Direct Database Bypass**: insert credentials
  - api_key: encrypted-key
### AI500 Coin Source Failure
safe content
"""
        cleaned = sanitize_skill_text(source, Path("skills/nofx-operations/SKILL.md"))
        self.assertNotIn("dek =", cleaned)
        self.assertNotIn("Direct Database Bypass", cleaned)
        self.assertIn("supported NOFX UI or API", cleaned)


ROOT = Path(__file__).resolve().parents[1]


class UIWorkflowV4InvariantTests(unittest.TestCase):
    def setUp(self):
        roles_path = ROOT / "governance/roles.yaml"
        self.roles = yaml.safe_load(roles_path.read_text(encoding="utf-8"))["profiles"]
        workflow_path = ROOT / "governance/workflows/ui-prototype.yaml"
        self.workflow_text = workflow_path.read_text(encoding="utf-8")
        self.workflow = yaml.safe_load(self.workflow_text)

    def _validate_with_override(self, modified_workflow, modified_roles=None):
        roles = modified_roles or self.roles
        with tempfile.TemporaryDirectory() as temporary:
            temp_root = Path(temporary)
            gov = temp_root / "governance/workflows"
            gov.mkdir(parents=True, exist_ok=True)
            wf_file = gov / "ui-prototype.yaml"
            wf_file.write_text(yaml.safe_dump(modified_workflow), encoding="utf-8")
            val = Validation()
            validate_ui_workflow(temp_root, roles, val)
            return val

    def test_ui_workflow_passes_on_valid_repository(self):
        val = Validation()
        validate_ui_workflow(ROOT, self.roles, val)
        self.assertEqual(val.errors, [])

    def test_negative_broken_transition_consumes_unproduced_artifact(self):
        wf = copy.deepcopy(self.workflow)
        # Stage 3 visual-spikes consumes an unproduced phantom artifact
        wf["stages"][2]["inputs"].append("phantom-unproduced-spec.json")
        val = self._validate_with_override(wf)
        self.assertTrue(any("consumes unproduced artifact: phantom-unproduced-spec.json" in err for err in val.errors))

    def test_negative_unauthorized_artifact_producer(self):
        wf = copy.deepcopy(self.workflow)
        # Stage 1 discovery (owner aurora) produces frontend-source without permission
        wf["stages"][0]["outputs"].append("frontend-source")
        val = self._validate_with_override(wf)
        self.assertTrue(any("without scope" in err for err in val.errors))

    def test_negative_creator_certifier_violation(self):
        # 1. Aurora certifies its own direction in blind-tournament
        wf = copy.deepcopy(self.workflow)
        wf["stages"][3]["owner"] = "aurora"
        val = self._validate_with_override(wf)
        self.assertTrue(any("AURORA cannot certify its own direction" in err for err in val.errors))

        # 2. Frame certifies its own vertical-slice in vertical-slice-gate
        wf2 = copy.deepcopy(self.workflow)
        wf2["stages"][7]["owner"] = "frame"
        val2 = self._validate_with_override(wf2)
        self.assertTrue(any("FRAME cannot certify its own vertical slice" in err for err in val2.errors))

    def test_negative_infinite_loop_configuration(self):
        # 1. blind-tournament with unbounded or excessive regeneration rounds
        wf = copy.deepcopy(self.workflow)
        wf["stages"][3]["bounds"]["max_regeneration_rounds"] = 10
        val = self._validate_with_override(wf)
        self.assertTrue(any("max_regeneration_rounds <= 2" in err for err in val.errors))

        # 2. remediation stage with excessive cycles
        wf2 = copy.deepcopy(self.workflow)
        wf2["stages"][11]["bounds"]["max_remediation_cycles"] = 5
        val2 = self._validate_with_override(wf2)
        self.assertTrue(any("max_remediation_cycles <= 2" in err for err in val2.errors))

    def test_negative_release_without_dual_pass(self):
        wf = copy.deepcopy(self.workflow)
        # Mutate closure gate to drop PRISM requirement
        wf["stages"][13]["gate"] = [
            "only LENS reports PASS",
            "no unresolved blocker",
        ]
        val = self._validate_with_override(wf)
        self.assertTrue(any("dual PRISM and LENS verification (independent veto)" in err for err in val.errors))

    def test_negative_verifier_git_mutation_violation(self):
        roles = copy.deepcopy(self.roles)
        roles["lens"]["production_write"] = True
        roles["lens"]["allowed_write_scopes"].append("frontend-source")
        val = self._validate_with_override(self.workflow, roles)
        self.assertTrue(any("Verifier lens must have production_write: false" in err for err in val.errors))
        self.assertTrue(any("Verifier lens cannot have frontend-source write scope" in err for err in val.errors))

    def test_canonical_skill_hash_parity_and_negative_drift(self):
        val = Validation()
        validate_canonical_skills(ROOT, val)
        self.assertEqual(val.errors, [])

        # Negative test: drift in profile-local copy
        with tempfile.TemporaryDirectory() as temporary:
            temp_root = Path(temporary)
            shutil.copytree(ROOT / "global", temp_root / "global")
            shutil.copytree(ROOT / "profiles", temp_root / "profiles")
            # Mutate one copy
            drift_target = temp_root / "profiles/frame/skills/custom/anti-ai-slop-web-design/references/anti-ai-slop-universal-principles.md"
            drift_target.write_text("drifted content", encoding="utf-8")
            drift_val = Validation()
            validate_canonical_skills(temp_root, drift_val)
            self.assertTrue(any("checksum drift in profile frame" in err for err in drift_val.errors))

    def test_runtime_core_is_embedded_once_and_prompt_budgeted(self):
        val = Validation()
        validate_runtime_core(ROOT, val)
        self.assertEqual(val.errors, [])

        with tempfile.TemporaryDirectory() as temporary:
            temp_root = Path(temporary)
            (temp_root / "governance").mkdir(parents=True)
            shutil.copy2(
                ROOT / "governance/FLEET_RUNTIME_CORE.md",
                temp_root / "governance/FLEET_RUNTIME_CORE.md",
            )
            for profile in (
                "orion", "atlas", "aurora", "forge", "frame", "lens",
                "nexus", "prism", "quant", "radar", "sentinel",
            ):
                destination = temp_root / "profiles" / profile
                destination.mkdir(parents=True)
                shutil.copy2(ROOT / "profiles" / profile / "SOUL.md", destination / "SOUL.md")
            drift_target = temp_root / "profiles/forge/SOUL.md"
            drift_target.write_text(
                drift_target.read_text(encoding="utf-8").replace(
                    "Optimize for the strongest finished outcome",
                    "Optimize for the first acceptable outcome",
                    1,
                ),
                encoding="utf-8",
            )
            drift_val = Validation()
            validate_runtime_core(temp_root, drift_val)
            self.assertTrue(any("embedded Fleet Runtime Core V2 drift" in err for err in drift_val.errors))

    def test_negative_duplicate_stage_id(self):
        wf = copy.deepcopy(self.workflow)
        wf["stages"][1]["id"] = "discovery"
        val = self._validate_with_override(wf)
        self.assertTrue(any("duplicate stage IDs in UI workflow" in err for err in val.errors))

    def test_negative_invalid_stage_owner(self):
        wf = copy.deepcopy(self.workflow)
        wf["stages"][0]["owner"] = "rogue-agent"
        val = self._validate_with_override(wf)
        self.assertTrue(any("invalid owner 'rogue-agent'" in err for err in val.errors))

    def test_negative_invalid_entry_owner(self):
        wf = copy.deepcopy(self.workflow)
        wf["entry"]["owner"] = "aurora"
        val = self._validate_with_override(wf)
        self.assertTrue(any("UI workflow entry owner must be orion" in err for err in val.errors))

    def test_negative_missing_canonical_lifecycle_stage(self):
        wf = copy.deepcopy(self.workflow)
        # Remove vertical-slice-gate stage
        wf["stages"] = [s for s in wf["stages"] if s.get("id") != "vertical-slice-gate"]
        val = self._validate_with_override(wf)
        self.assertTrue(any("UI workflow stages must strictly match canonical lifecycle" in err for err in val.errors))

    def test_negative_checkpoint_producer_not_frame(self):
        roles = copy.deepcopy(self.roles)
        roles["frame"]["production_write"] = False
        val = self._validate_with_override(self.workflow, roles)
        self.assertTrue(any("FRAME must have production_write: true to create git checkpoints" in err for err in val.errors))

    def test_negative_rollback_authority_not_orion(self):
        wf = copy.deepcopy(self.workflow)
        wf["stages"][11]["gate"] = [
            "every change maps to defect ID",
            "FRAME arbitrates rollback and reset",
        ]
        val = self._validate_with_override(wf)
        self.assertTrue(any("ORION must be explicit authority for PROMOTE / KEEP_CURRENT_BEST / ROLLBACK" in err for err in val.errors))


if __name__ == "__main__":
    unittest.main()
