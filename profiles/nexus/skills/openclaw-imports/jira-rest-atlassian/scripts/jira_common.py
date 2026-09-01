#!/usr/bin/env python3
import argparse
import base64
import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

DEFAULT_ENV_FILE = "/root/.openclaw/workspace/state/jira-mcp/mcp-atlassian.env"


def parse_env_file(path: str) -> Dict[str, str]:
    data: Dict[str, str] = {}
    for raw in Path(path).expanduser().read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        data[key.strip()] = value
    return data


def adf_text(text: str) -> Dict[str, Any]:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    content = []
    for idx, line in enumerate(lines):
        if line:
            content.append({"type": "text", "text": line})
        if idx != len(lines) - 1:
            content.append({"type": "hardBreak"})
    if not content:
        content = [{"type": "text", "text": ""}]
    return {
        "version": 1,
        "type": "doc",
        "content": [{"type": "paragraph", "content": content}],
    }


class JiraClient:
    def __init__(self, env_file: str = DEFAULT_ENV_FILE):
        self.env_file = env_file
        self.env = parse_env_file(env_file)
        self.base_url = self.env.get("JIRA_URL", "").rstrip("/")
        if not self.base_url:
            raise SystemExit("JIRA_URL missing from env file")
        self.verify_ssl = self.env.get("JIRA_SSL_VERIFY", "true").lower() != "false"

    def _headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.env.get("JIRA_USERNAME") and self.env.get("JIRA_API_TOKEN"):
            raw = f"{self.env['JIRA_USERNAME']}:{self.env['JIRA_API_TOKEN']}".encode("utf-8")
            headers["Authorization"] = "Basic " + base64.b64encode(raw).decode("ascii")
        elif self.env.get("JIRA_PERSONAL_TOKEN"):
            headers["Authorization"] = "Bearer " + self.env["JIRA_PERSONAL_TOKEN"]
        else:
            raise SystemExit("No supported Jira auth found in env file")
        if extra:
            headers.update(extra)
        return headers

    def request(self, method: str, path: str, *, query: Optional[Dict[str, Any]] = None, payload: Optional[Dict[str, Any]] = None) -> Any:
        url = self.base_url + path
        if query:
            encoded = urllib.parse.urlencode([(k, v) for k, v in query.items() if v is not None], doseq=True)
            if encoded:
                url += ("&" if "?" in url else "?") + encoded
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(url, data=body, headers=self._headers(), method=method.upper())
        context = None if self.verify_ssl else ssl._create_unverified_context()
        try:
            with urllib.request.urlopen(request, context=context, timeout=60) as response:
                raw = response.read().decode("utf-8", errors="replace")
                if not raw:
                    return {"ok": True, "status": response.getcode()}
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    return {"ok": True, "status": response.getcode(), "raw": raw}
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(raw)
            except Exception:
                parsed = raw[:1000]
            raise SystemExit(json.dumps({
                "ok": False,
                "status": exc.code,
                "url": url,
                "error": parsed,
            }, indent=2, ensure_ascii=False))

    def myself(self) -> Any:
        return self.request("GET", "/rest/api/3/myself")

    def project(self, key: str) -> Any:
        return self.request("GET", f"/rest/api/3/project/{urllib.parse.quote(key)}")

    def fields(self) -> Any:
        return self.request("GET", "/rest/api/3/field")

    def search(self, jql: str, limit: int = 50, fields: Optional[str] = None) -> Any:
        query = {"jql": jql, "maxResults": limit}
        if fields:
            query["fields"] = fields
        return self.request("GET", "/rest/api/3/search/jql", query=query)

    def issue_get(self, key: str, expand: Optional[str] = None) -> Any:
        return self.request("GET", f"/rest/api/3/issue/{urllib.parse.quote(key)}", query={"expand": expand})

    def issue_update(self, key: str, fields: Dict[str, Any]) -> Any:
        return self.request("PUT", f"/rest/api/3/issue/{urllib.parse.quote(key)}", payload={"fields": fields})

    def issue_comment(self, key: str, body: str) -> Any:
        payload = {"body": adf_text(body)}
        return self.request("POST", f"/rest/api/3/issue/{urllib.parse.quote(key)}/comment", payload=payload)

    def transitions(self, key: str) -> Any:
        return self.request("GET", f"/rest/api/3/issue/{urllib.parse.quote(key)}/transitions")

    def transition(self, key: str, transition_id: str) -> Any:
        return self.request("POST", f"/rest/api/3/issue/{urllib.parse.quote(key)}/transitions", payload={"transition": {"id": str(transition_id)}})

    def issue_create(self, payload: Dict[str, Any]) -> Any:
        return self.request("POST", "/rest/api/3/issue", payload=payload)


def load_json_arg(value: str) -> Dict[str, Any]:
    if value.startswith("@"):
        return json.loads(Path(value[1:]).read_text(encoding="utf-8"))
    return json.loads(value)


def print_json(data: Any):
    print(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True))


def add_env_arg(parser: argparse.ArgumentParser):
    parser.add_argument("--env-file", default=DEFAULT_ENV_FILE)
