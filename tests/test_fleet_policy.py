import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.sanitize_config import sanitize_identity_config, sanitize_text
from scripts.sanitize_skill_examples import sanitize_text as sanitize_skill_text


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


if __name__ == "__main__":
    unittest.main()
