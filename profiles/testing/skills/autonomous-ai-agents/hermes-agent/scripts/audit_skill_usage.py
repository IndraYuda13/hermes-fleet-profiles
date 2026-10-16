#!/usr/bin/env python3
"""Read-only audit of a Hermes profile's skill library.

Usage:
    python3 audit_skill_usage.py [SKILLS_DIR]

SKILLS_DIR defaults to $HERMES_HOME/skills (falls back to ~/.hermes/skills).
Reports: used skills (keep evidence), unused bundled defaults, unused
custom/imported skills, tracked-but-never-used and file-mtime flags,
duplicate basenames, and the usage-tracking start date.
"""
import json
import os
import sys
import time
from collections import defaultdict


def norm(s):
    return s.replace("_", "-")


def find_skills(base):
    skills = []
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in (".hub", ".archive", ".trash")]
        if "SKILL.md" not in files:
            continue
        latest, size = 0.0, 0
        for r2, _d2, f2 in os.walk(root):
            for f in f2:
                p = os.path.join(r2, f)
                try:
                    latest = max(latest, os.path.getmtime(p))
                    size += os.path.getsize(p)
                except OSError:
                    pass
        skills.append({
            "rel": os.path.relpath(root, base),
            "name": os.path.basename(root),
            "mtime": latest,
            "size": size,
        })
    return skills


def load_usage(base):
    path = os.path.join(base, ".usage.json")
    if not os.path.exists(path):
        return {}
    try:
        raw = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    # keys are mixed: bare name or path-qualified -> match on basename
    return {norm(k.split("/")[-1]): v for k, v in raw.items()}


def load_bundled(base):
    path = os.path.join(base, ".bundled_manifest")
    names = set()
    if os.path.exists(path):
        for line in open(path, encoding="utf-8", errors="replace"):
            if ":" in line:
                names.add(norm(line.strip().split(":", 1)[0]))
    return names


def d(ts):
    return (ts or "never")[:10]


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")), "skills")
    base = os.path.abspath(base)
    if not os.path.isdir(base):
        sys.exit("not a skills dir: %s" % base)

    skills = find_skills(base)
    usage = load_usage(base)
    bundled = load_bundled(base)

    tracking_start = min((v.get("created_at") for v in usage.values()
                          if v.get("created_at")), default=None)

    for s in skills:
        u = usage.get(norm(s["name"]))
        s["u"] = u
        s["use"] = (u or {}).get("use_count") or 0

    used = sorted([s for s in skills if s["use"] > 0], key=lambda s: -s["use"])
    unused = [s for s in skills if s["use"] == 0]

    print("SKILLS DIR : %s" % base)
    print("TOTAL      : %d skills, %.1f MB" % (
        len(skills), sum(s["size"] for s in skills) / 1e6))
    print("USED >=1   : %d   |   NEVER-USED/UNTRACKED: %d" % (
        len(used), len(unused)))
    if tracking_start:
        print("usage tracking starts %s - older skills may read 0 falsely; "
              "cross-check mtime + .curator_ledger.jsonl" % tracking_start[:10])

    byname = defaultdict(list)
    for s in skills:
        byname[s["name"]].append(s["rel"])
    for name, rels in sorted(byname.items()):
        if len(rels) > 1:
            print("DUPLICATE NAME: %s -> %s" % (name, rels))

    print("\n== USED (keep evidence) ==")
    for s in used:
        print("  use=%-3d last=%-10s %s" % (
            s["use"], d(s["u"].get("last_used_at")), s["rel"]))

    for label, pred in (
        ("UNUSED - BUNDLED DEFAULT (re-obtainable from fresh install)",
         lambda s: norm(s["name"]) in bundled),
        ("UNUSED - CUSTOM/IMPORTED (irreplaceable, review carefully)",
         lambda s: norm(s["name"]) not in bundled),
    ):
        print("\n== %s ==" % label)
        for s in sorted([x for x in unused if pred(x)], key=lambda s: s["rel"]):
            if s["u"]:
                tag = " [tracked, 0 use; created %s]" % d(s["u"].get("created_at"))
            elif s["mtime"]:
                tag = " [untracked; file mtime %s]" % time.strftime(
                    "%Y-%m-%d", time.localtime(s["mtime"]))
            else:
                tag = ""
            print("  %-58s %7.1f KB%s" % (s["rel"], s["size"] / 1e3, tag))

    print("\nRead-only audit - pick targets with the user before deleting anything.")


if __name__ == "__main__":
    main()
