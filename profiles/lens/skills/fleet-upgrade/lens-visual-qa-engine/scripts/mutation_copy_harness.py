#!/usr/bin/env python3
"""Data-driven mutation harness: prove an assertion actually fails on the defect it names.

Why: a PASS on the real artifact is only meaningful once the assertion has been shown to
FAIL on a mutated copy. This runs a set of text-substitution mutations against a COPY of
the artifact under test (never the production file), drives a probe against each copy, and
reports the per-mutation verdict PLUS the evidence value that drove it -- so a mutant that
fails for the wrong reason (selector vanished) is distinguishable from one that exercises
the real predicate (an overlap metric crossing zero).

Contract with the probe: the probe must read its input HTML path and output dir from env
vars named by PROBE_ENV_HTML / PROBE_ENV_OUT below (adjust to whatever the probe uses).
If the probe has no such parameters, add them once -- a one-line change -- rather than
editing the probe's logic. Never alter probe logic to make a mutation pass.

Usage: edit SRC_HTML, PROBE, and MUTATIONS for the artifact at hand, then run.
"""
import hashlib
import json
import os
import shutil
import subprocess

# --- configure per artifact --------------------------------------------------
SRC_HTML = os.environ.get("SRC_HTML", "")          # artifact under test (read-only)
PROBE = os.environ.get("PROBE", "")                # probe script to drive
SCRATCH = os.environ.get("SCRATCH", ".")           # where copies + outputs live
PROBE_ENV_HTML = "A3C_HTML"                         # env vars the probe must honour
PROBE_ENV_OUT = "A3C_OUT"
BROWSERS_PATH = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/root/.cache/ms-playwright")

# (name, old_substring, new_substring). Keep each mutation minimal and verify the copy hash
# changes. Mutations should target the PREDICATE under test, e.g.:
#   deletion/absence        -> "<div class=\"marker\">..</div>" -> ""          (tests null branch)
#   present-but-unrendered  -> ".marker{" -> ".marker{display:none;"  (tests area>0 branch)
#   forced occlusion        -> 'left:74%' -> 'left:74%;bottom:calc(30% - 25px)' (tests overlap)
MUTATIONS = json.loads(os.environ.get("MUTATIONS_JSON", "[]"))

def run_probe(html_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    env = dict(os.environ, PLAYWRIGHT_BROWSERS_PATH=BROWSERS_PATH)
    env[PROBE_ENV_HTML] = html_path
    env[PROBE_ENV_OUT] = out_dir
    r = subprocess.run(["/usr/bin/python3", PROBE], capture_output=True,
                       text=True, env=env, timeout=300)
    rep = os.path.join(out_dir, "REPORT.json")      # adjust to the probe's report name
    data = json.load(open(rep)) if os.path.exists(rep) else None
    return r.returncode, data

def main():
    assert SRC_HTML and PROBE, "set SRC_HTML and PROBE env vars"
    mutdir = os.path.join(SCRATCH, "mutation-copies")
    os.makedirs(mutdir, exist_ok=True)
    src = open(SRC_HTML, "rb").read().decode("utf-8")
    src_md5 = hashlib.md5(src.encode()).hexdigest()
    rows = []

    # Control: a byte-identical copy, to confirm the environment reproduces the PASS.
    ctl = os.path.join(mutdir, "control-unmutated.html")
    shutil.copyfile(SRC_HTML, ctl)
    code, data = run_probe(ctl, os.path.join(mutdir, "out-control"))
    rows.append({"mutation": "control_unmutated",
                 "md5": hashlib.md5(open(ctl, "rb").read()).hexdigest(),
                 "probe_exit": code,
                 "all_pass": data.get("all_pass") if data else None})

    for name, old, new in MUTATIONS:
        assert old in src, "%s: anchor substring not found in source" % name
        text = src.replace(old, new)
        assert text != src, "%s: substitution changed nothing" % name
        p = os.path.join(mutdir, name + ".html")
        open(p, "w").write(text)
        m_md5 = hashlib.md5(text.encode()).hexdigest()
        assert m_md5 != src_md5, "%s: copy hash equals source; mutation not applied" % name
        code, data = run_probe(p, os.path.join(mutdir, "out-" + name))
        a3c = (data or {}).get("assertions", {}).get("TARGET_ASSERTION")  # adjust key
        rows.append({"mutation": name, "md5": m_md5, "probe_exit": code,
                     "all_pass": data.get("all_pass") if data else None,
                     "assertion_pass": a3c.get("pass") if a3c else None,
                     "assertion_evidence": a3c.get("evidence") if a3c else None})
        print("%-28s md5=%s exit=%s all_pass=%s assertion=%s" % (
            name, m_md5[:12], code,
            data.get("all_pass") if data else None,
            a3c.get("pass") if a3c else None))

    out = os.path.join(SCRATCH, "MUTATION-RESULTS.json")
    json.dump({"source_md5": src_md5, "rows": rows}, open(out, "w"), indent=2)
    print("\nwrote", out)
    print("VERDICT: control must PASS and every mutation must FAIL, each citing its own evidence value.")

if __name__ == "__main__":
    main()
