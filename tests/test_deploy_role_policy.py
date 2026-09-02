import socket
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.apply_role_policy import render_policy
from scripts.deploy_role_policy import (
    backup_configs,
    changed_policy_fields,
    listening_ports,
    parse_profile_selection,
    restore_backup,
    verify_policy,
)


class SurgicalPolicyDeploymentTests(unittest.TestCase):
    def setUp(self):
        self.role = {
            "model": "ag-opus-pool",
            "production_write": False,
            "allowed_root_toolsets": ["kanban", "memory"],
            "allowed_platform_toolsets": ["a2a", "kanban"],
            "forbidden_toolsets": ["terminal", "delegation"],
            "a2a_port": 9901,
        }

    def test_render_preserves_runtime_owned_secret_and_identity_fields(self):
        source = """model:
  default: ag-opus-pool
custom_providers:
  - name: private
    api_key: runtime-secret
platforms:
  whatsapp:
    extra:
      allow_from: ['private-id']
toolsets: [kanban, terminal, delegation]
platform_toolsets:
  a2a: [a2a, kanban, terminal]
  telegram: [a2a, kanban, terminal]
terminal:
  backend: local
moa:
  enabled: true
delegation:
  orchestrator_enabled: true
approvals:
  mode: off
kanban:
  review_dispatch: false
"""
        rendered = render_policy(source, self.role, "orion")
        parsed = yaml.safe_load(rendered)
        self.assertEqual(parsed["custom_providers"][0]["api_key"], "runtime-secret")
        self.assertEqual(
            parsed["platforms"]["whatsapp"]["extra"]["allow_from"], ["private-id"]
        )
        self.assertEqual(parsed["toolsets"], ["kanban", "memory"])
        self.assertEqual(parsed["platform_toolsets"]["a2a"], ["a2a", "kanban"])
        self.assertFalse(parsed["moa"]["enabled"])
        self.assertFalse(parsed["delegation"]["orchestrator_enabled"])
        self.assertTrue(parsed["kanban"]["review_dispatch"])

    def test_groupbot_removes_terminal_but_preserves_allowlists(self):
        role = dict(self.role)
        role.update({
            "model": "gemini-flash",
            "allowed_root_toolsets": ["web"],
            "allowed_platform_toolsets": ["web"],
        })
        source = """model: {default: gemini-flash}
toolsets: [web, terminal]
platform_toolsets:
  whatsapp: [web, terminal]
platforms:
  whatsapp:
    extra:
      group_allowed_chats: ['private-group']
terminal: {backend: local}
approvals: {mode: off}
"""
        parsed = yaml.safe_load(render_policy(source, role, "groupbot"))
        self.assertNotIn("terminal", parsed)
        self.assertEqual(parsed["platforms"]["whatsapp"]["extra"]["group_allowed_chats"], ["private-group"])

    def test_change_report_contains_only_policy_fields(self):
        before = "toolsets: [terminal]\ncustom: one\n"
        after = "toolsets: [kanban]\ncustom: two\n"
        self.assertEqual(changed_policy_fields(before, after), ["toolsets"])

    def test_backup_and_restore_round_trip(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "profiles" / "orion" / "config.yaml"
            config.parent.mkdir(parents=True)
            config.write_text("toolsets: [before]\n", encoding="utf-8")
            rendered = {"orion": (config, "toolsets: [before]\n", "toolsets: [after]\n")}
            backup, _manifest = backup_configs(rendered, root / "backups")
            config.write_text("toolsets: [broken]\n", encoding="utf-8")
            restore_backup(rendered, backup)
            self.assertEqual(config.read_text(encoding="utf-8"), "toolsets: [before]\n")

    def test_listening_port_detection(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        try:
            port = server.getsockname()[1]
            self.assertEqual(listening_ports({"x": {"a2a_port": port}}), [port])
        finally:
            server.close()

    def test_verifier_rejects_model_or_tool_drift(self):
        config = {
            "model": {"default": "wrong"},
            "toolsets": ["terminal"],
            "platform_toolsets": {"a2a": ["terminal"]},
            "approvals": {"mode": "off"},
            "moa": {"enabled": True},
            "delegation": {"orchestrator_enabled": True},
            "kanban": {"review_dispatch": False},
        }
        errors = verify_policy(config, self.role, "orion")
        self.assertGreaterEqual(len(errors), 5)

    def test_targeted_profile_selection(self):
        expected = {"orion", "frame", "lens"}
        self.assertEqual(
            parse_profile_selection("orion, lens", expected),
            {"orion", "lens"},
        )
        self.assertEqual(parse_profile_selection(None, expected), expected)
        with self.assertRaises(ValueError):
            parse_profile_selection("unknown", expected)


if __name__ == "__main__":
    unittest.main()
