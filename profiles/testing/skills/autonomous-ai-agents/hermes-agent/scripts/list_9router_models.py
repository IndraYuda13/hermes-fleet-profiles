#!/usr/bin/env python3
"""Inventory models behind a 9router custom provider prefix: router list vs upstream /v1/models.

Read-only, no keys needed (enumeration endpoints are open). Never prints secrets.
Run without --prefix to just map every node: prefix -> baseUrl.

Usage:
  python3 list_9router_models.py
  python3 list_9router_models.py --prefix prof
  python3 list_9router_models.py --prefix prof --router http://127.0.0.1:20128
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import urllib.request


def fetch_json(url: str, timeout: int = 30):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer dummy"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default="/root/.9router/db/data.sqlite")
    ap.add_argument("--router", default="http://127.0.0.1:20128")
    ap.add_argument("--prefix", help="provider node prefix to inventory (e.g. prof)")
    args = ap.parse_args()

    con = sqlite3.connect("file:%s?mode=ro" % args.db, uri=True)
    con.row_factory = sqlite3.Row
    nodes = []
    for row in con.execute("SELECT id, name, data FROM providerNodes"):
        d = json.loads(row["data"])
        nodes.append((row["id"], row["name"], d.get("prefix"), d.get("baseUrl")))

    if not args.prefix:
        print("provider nodes (prefix -> baseUrl):")
        for _nid, name, prefix, base in nodes:
            print("  %-12s %-24s %s" % (prefix, name, base))
        return 0

    match = [n for n in nodes if n[2] == args.prefix]
    if not match:
        print("no node with prefix %r; known: %s"
              % (args.prefix, ", ".join(str(n[2]) for n in nodes)))
        return 2
    nid, name, prefix, base = match[0]
    print("node %s (%s)  prefix=%s  baseUrl=%s" % (nid, name, prefix, base))

    router_ids = sorted(
        m["id"] for m in fetch_json(args.router.rstrip("/") + "/v1/models")["data"]
        if m["id"].startswith(prefix + "/"))
    print("\nrouter exposes %d models under %s/:" % (len(router_ids), prefix))
    for mid in router_ids:
        print("  " + mid)

    if base:
        try:
            upstream_ids = sorted(m["id"] for m in
                                  fetch_json(base.rstrip("/") + "/models")["data"])
            rset = {mid.split("/", 1)[1] for mid in router_ids}
            uset = set(upstream_ids)
            print("\nupstream exposes %d models; diff:" % len(uset))
            print("  router-only:   %s" % (sorted(rset - uset) or "none"))
            print("  upstream-only: %s" % (sorted(uset - rset) or "none"))
        except Exception as exc:  # noqa: BLE001 - report and continue
            print("\nupstream fetch failed (%s); no diff" % exc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
