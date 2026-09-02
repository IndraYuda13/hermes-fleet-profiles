import json
import shutil
import struct
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from scripts.runtime_smoke import (
    A2AClient,
    RuntimeSmoke,
    a2a_reply_failure,
    authorization_refusal_matches,
    config_revision,
    ensure_safe_workspace,
    extract_text,
    attestation_matches,
    line_content_matches,
    parse_attestation,
    parse_profile_selection,
    png_size,
    redact_json,
)


ROOT = Path(__file__).resolve().parents[1]


class RuntimeSmokeUnitTests(unittest.TestCase):
    def test_a2a_timeout_and_empty_reply_are_terminal_failures(self):
        self.assertEqual(
            a2a_reply_failure("[agent did not reply in time]"),
            "agent did not reply in time",
        )
        self.assertEqual(
            a2a_reply_failure("  "),
            "agent returned an empty final reply",
        )
        self.assertIsNone(a2a_reply_failure("Mission completed with evidence."))

    def test_redacts_nested_secret_evidence(self):
        value = redact_json({"Authorization": "Bearer abc", "reply": "token=very-secret-value"})
        self.assertEqual(value["Authorization"], "REDACTED")
        self.assertNotIn("very-secret-value", value["reply"])

    def test_attestation_parser_accepts_fenced_reply(self):
        reply = 'done\n```\nHERMES_PROBE_RESULT:{"probe_id":"p1","result":"PASS"}\n```'
        self.assertEqual(parse_attestation(reply, "HERMES_PROBE_RESULT")["probe_id"], "p1")

    def test_attestation_accepts_bounded_role_alias(self):
        expected = {"profile": "sentinel", "role_class": "verifier", "result": "PASS"}
        actual = {"profile": "sentinel", "role_class": "reviewer", "result": "PASS"}
        self.assertTrue(attestation_matches(actual, expected, {"verifier", "reviewer"}))
        self.assertFalse(attestation_matches(actual, expected, {"verifier"}))

    def test_exact_line_accepts_optional_final_newline_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "probe.txt"
            path.write_text("expected", encoding="utf-8")
            self.assertTrue(line_content_matches(path, "expected\n"))
            path.write_text("expected\nextra", encoding="utf-8")
            self.assertFalse(line_content_matches(path, "expected\n"))

    def test_targeted_profile_parser(self):
        self.assertEqual(parse_profile_selection("sentinel, atlas,forge"), {"sentinel", "atlas", "forge"})
        with self.assertRaises(ValueError):
            parse_profile_selection("unknown")

    def test_authorization_refusal_requires_all_security_signals(self):
        valid = """This A2A request has no kanban task and no assigned workspace.
Authorization is missing and cannot self-authorize. The request is declined."""
        self.assertTrue(authorization_refusal_matches(valid))

        self.assertFalse(
            authorization_refusal_matches(
                "A2A request declined. Authorization is missing."
            )
        )
        self.assertFalse(
            authorization_refusal_matches(
                valid + '\nHERMES_ALLOWED:x\n{\"result\":\"PASS\"}'
            )
        )

    def test_extract_text_handles_nested_a2a_result(self):
        value = {"result": {"status": {"message": {"parts": [{"text": "final"}]}}}}
        self.assertEqual(extract_text(value), "final")

    def test_workspace_requires_marker(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "staging"
            path.mkdir()
            with self.assertRaises(ValueError):
                ensure_safe_workspace(path)
            (path / ".hermes-fleet-staging").touch()
            self.assertEqual(ensure_safe_workspace(path), path.resolve())

    def test_png_width_reader(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "shot.png"
            path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\x0dIHDR" + struct.pack(">II", 390, 844))
            self.assertEqual(png_size(path), (390, 844))

    def test_config_revision_is_stable(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            for profile in ("orion", "groupbot"):
                target = home / "profiles" / profile
                target.mkdir(parents=True)
                (target / "config.yaml").write_text(f"name: {profile}\n", encoding="utf-8")
            self.assertEqual(config_revision(home), config_revision(home))


class A2AHandler(BaseHTTPRequestHandler):
    def log_message(self, _format, *_args):
        return

    def do_GET(self):
        payload = {"name": "mock", "url": "http://127.0.0.1", "skills": []}
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        request = json.loads(self.rfile.read(length))
        payload = {
            "jsonrpc": "2.0",
            "id": request["id"],
            "result": {"message": {"parts": [{"text": "probe reply"}]}},
        }
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class A2AClientTests(unittest.TestCase):
    def test_card_and_send_round_trip(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), A2AHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            client = A2AClient("127.0.0.1", 5)
            card = client.card("orion", server.server_port, "/.well-known/agent-card.json")
            response = client.send("orion", server.server_port, "/", "hello")
            self.assertEqual(card["name"], "mock")
            self.assertEqual(extract_text(response), "probe reply")
        finally:
            server.shutdown()
            server.server_close()


class UIGauntletValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.home = self.base / "hermes"
        for profile in (ROOT / "profiles").iterdir():
            if profile.is_dir() and (profile / "config.yaml").is_file():
                target = self.home / "profiles" / profile.name
                target.mkdir(parents=True)
                shutil.copy2(profile / "config.yaml", target / "config.yaml")
        self.smoke = RuntimeSmoke(ROOT, self.home, "127.0.0.1", 1, "abcdef123456")

    def tearDown(self):
        self.temporary.cleanup()

    @staticmethod
    def write_png(path: Path, width: int, height: int = 800):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\x0dIHDR" + struct.pack(">II", width, height))

    def test_complete_ui_evidence_passes(self):
        root = self.base / "gauntlet"
        root.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@localhost"], cwd=root, check=True)

        for relative in self.smoke.gauntlet["required_artifacts"]:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.suffix in {".html", ".css", ".js"}:
                path.write_text("accessible service operations interface\n", encoding="utf-8")
            else:
                path.write_text("verified artifact\n", encoding="utf-8")
        subprocess.run(["git", "add", "app"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "feat: implementation"], cwd=root, check=True)
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()

        mission_id = "UI-TEST-1234"
        for relative, owner in self.smoke.gauntlet["expected_owners"].items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({
                "mission_id": mission_id,
                "task_id": f"task-{owner}",
                "owner": owner,
                "verifier": None if owner == "orion" else owner,
                "revision": head,
                "method": "deterministic fixture",
                "result": "PASS",
                "timestamp": "2026-09-02T00:00:00Z",
            }), encoding="utf-8")
        for item in self.smoke.gauntlet["required_screenshots"]:
            self.write_png(root / item["path"], item["width"])

        self.smoke.validate_ui_gauntlet(root, mission_id)
        failures = [record.detail for record in self.smoke.records if record.result != "PASS"]
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
