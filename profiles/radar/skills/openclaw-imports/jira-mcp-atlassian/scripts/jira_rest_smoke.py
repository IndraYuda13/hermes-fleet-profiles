#!/usr/bin/env python3
import argparse
import base64
import json
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path



def parse_env_file(path: Path):
    data = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        data[key.strip()] = value
    return data



def auth_headers(env: dict):
    if env.get("JIRA_USERNAME") and env.get("JIRA_API_TOKEN"):
        raw = f"{env['JIRA_USERNAME']}:{env['JIRA_API_TOKEN']}".encode("utf-8")
        return {"Authorization": "Basic " + base64.b64encode(raw).decode("ascii")}
    if env.get("JIRA_PERSONAL_TOKEN"):
        return {"Authorization": "Bearer " + env["JIRA_PERSONAL_TOKEN"]}
    raise SystemExit("No supported Jira auth found in env file")



def fetch_json(url: str, headers: dict, verify_ssl: bool):
    request = urllib.request.Request(url, headers={**headers, "Accept": "application/json"})
    context = None
    if not verify_ssl:
        context = ssl._create_unverified_context()
    with urllib.request.urlopen(request, context=context, timeout=20) as response:
        body = response.read().decode("utf-8", errors="replace")
        return response.getcode(), body



def main():
    parser = argparse.ArgumentParser(description="Validate Jira credentials with a direct REST smoke test.")
    parser.add_argument("--env-file", required=True)
    args = parser.parse_args()

    env = parse_env_file(Path(args.env_file).expanduser())
    base_url = env.get("JIRA_URL", "").rstrip("/")
    if not base_url:
        raise SystemExit("JIRA_URL missing from env file")

    verify_ssl = env.get("JIRA_SSL_VERIFY", "true").lower() != "false"
    headers = auth_headers(env)
    candidate_paths = ["/rest/api/3/myself", "/rest/api/2/myself"]

    last_error = None
    for path in candidate_paths:
        url = base_url + path
        try:
            status, body = fetch_json(url, headers, verify_ssl)
            data = json.loads(body)
            summary = {
                "ok": True,
                "status": status,
                "url": url,
                "displayName": data.get("displayName"),
                "accountId": data.get("accountId"),
                "emailAddress": data.get("emailAddress"),
                "active": data.get("active"),
                "timeZone": data.get("timeZone"),
            }
            print(json.dumps(summary, indent=2, sort_keys=True))
            return
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            last_error = f"{url} -> HTTP {exc.code}: {body[:400]}"
            if exc.code == 404:
                continue
            print(last_error, file=sys.stderr)
            raise SystemExit(1)
        except Exception as exc:
            last_error = f"{url} -> {exc}"
            continue

    print(last_error or "Smoke test failed", file=sys.stderr)
    raise SystemExit(1)


if __name__ == "__main__":
    main()
