#!/usr/bin/env python3
"""Smoke probes for internal web portals: SQLi, path traversal, unauthenticated mutation.

Stdlib-only and statically re-runnable. Run ONLY against targets you are
authorized to test:

    python3 security_smoke_test.py http://127.0.0.1:8080 --path-prefix /api/v1

Exit code 1 means at least one probe was accepted that should have been
rejected (SQLi/traversal returning 200, or an unauthenticated mutation
returning < 400). The POST probe sends a minimal harmless payload; some
apps return 200 with an error body — treat that as a manual follow-up.
"""
import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

SQLI_PROBES = ["' OR '1'='1", "admin'--", "1; DROP TABLE services;"]
TRAVERSAL_PROBES = [
    "../../../../etc/passwd",
    "..%2F..%2F..%2Fetc%2fpasswd",
    "%2e%2e%2f%2e%2e%2fetc%2fpasswd",
]


def probe(method, url, body=None):
    req = urllib.request.Request(url, data=body, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except urllib.error.URLError:
        return None


def main():
    parser = argparse.ArgumentParser(description="Portal security smoke probes")
    parser.add_argument("base_url")
    parser.add_argument("--path-prefix", default="/api/v1",
                        help="API prefix for detail-style and mutation endpoints")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    failures = []

    for payload in SQLI_PROBES:
        url = f"{base}{args.path_prefix}/services/{urllib.parse.quote(payload, safe='')}"
        status = probe("GET", url)
        if status == 200:
            failures.append(f"SQLi payload accepted with 200: {payload!r}")
        else:
            print(f"ok   SQLi {payload!r} -> {status}")

    for payload in TRAVERSAL_PROBES:
        status = probe("GET", f"{base}/static/{payload}")
        if status == 200:
            failures.append(f"Path traversal accepted with 200: {payload!r}")
        else:
            print(f"ok   traversal {payload!r} -> {status}")

    body = json.dumps({"service_id": "svc_probe", "version": "v0-probe"}).encode()
    status = probe("POST", f"{base}{args.path_prefix}/deployments", body)
    if status is not None and status < 400:
        failures.append(f"Unauthenticated mutation returned {status} (must fail closed)")
    else:
        print(f"ok   unauthenticated deploy -> {status}")

    if failures:
        print("FAILURES:")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print("all probes behaved as expected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
