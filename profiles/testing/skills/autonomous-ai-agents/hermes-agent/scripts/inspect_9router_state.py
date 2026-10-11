#!/usr/bin/env python3
"""Read-only summary of a 9router state DB: combos, per-connection thinking mode, nodes.

Secrets (apiKey / password / tunnel url) are masked and never printed.
Scope every query — a blanket dump of `kv` returns megabytes of base64 blobs and the
shell output cap truncates the row you actually wanted.

Usage:
  python3 inspect_9router_state.py
  python3 inspect_9router_state.py --db /root/.9router/db/data.sqlite
"""
from __future__ import annotations

import argparse
import json
import sqlite3

SECRET_KEYS = {"apiKey", "password", "tunnelUrl", "jwtSecret", "machineId", "key"}


def mask(obj):
    if isinstance(obj, dict):
        return {k: ("***" if k in SECRET_KEYS else mask(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [mask(v) for v in obj]
    return obj


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default="/root/.9router/db/data.sqlite")
    args = ap.parse_args()

    con = sqlite3.connect("file:%s?mode=ro" % args.db, uri=True)
    con.row_factory = sqlite3.Row

    print("== combos (alias -> member models) ==")
    for row in con.execute("SELECT name, models FROM combos ORDER BY name"):
        print("  %-16s %s" % (row["name"], row["models"]))

    print("\n== provider nodes (prefix -> baseUrl) ==")
    for row in con.execute("SELECT type, data FROM providerNodes"):
        d = json.loads(row["data"])
        print("  prefix=%-8s apiType=%-10s baseUrl=%s" % (
            d.get("prefix"), d.get("apiType"), d.get("baseUrl")))

    print("\n== thinking mode per provider connection ==")
    try:
        settings = json.loads(con.execute("SELECT data FROM settings WHERE id = 1").fetchone()[0])
    except (TypeError, ValueError):
        settings = {}
    thinking = settings.get("providerThinking") or {}
    overrides = settings.get("providerOverrides") or {}
    for row in con.execute("SELECT id, provider, name, isActive, data FROM providerConnections"):
        d = json.loads(row["data"])
        psd = d.get("providerSpecificData") or {}
        mode = (thinking.get(row["provider"]) or {}).get("mode")
        print("  %-58s prefix=%-6s default=%s" % (
            row["id"], psd.get("prefix"), d.get("defaultModel")))
        print("      thinking.mode=%s  hasProviderOverride=%s  active=%s  testStatus=%s" % (
            mode, bool(overrides.get(row["provider"])), row["isActive"], d.get("testStatus")))
        if d.get("rateLimitedUntil"):
            print("      RATE-LIMITED until %s" % d["rateLimitedUntil"])

    print("\n== providerThinking (raw, masked) ==")
    print(json.dumps(mask(thinking), indent=2))

    print("\nNOTE: the stored mode is mapped to the wire by the router's adapter code, not by name.")
    print("e.g. 9router deepseek case maps xhigh|max -> reasoning_effort='max' (raising xhigh->max is a no-op),")
    print("and several branches force thinking={type:'enabled'} regardless of mode.")


if __name__ == "__main__":
    main()
