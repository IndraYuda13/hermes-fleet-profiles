# Revision-Bound Evidence Runs

## When to use
Any scripted or peer-delegated run that produces an artifact (report JSON, stdout capture, screenshot, log) which someone else will trust as evidence for a specific revision. Also when asked to relay or re-run an evidence job that other agents may be running at the same time.

## Standing rules

1. **Quiescence before any run.** Sample every input: `sha256sum <input>` plus `stat -c '%n | %s | %y' <input>`. Sleep 45s, sample both again. If samples differ, sleep 60 and take a third sample. Still differ -> STOP and report exactly `ARTIFACT STILL BEING WRITTEN - no run attempted`. Never run on bytes you sampled only once.
2. **VOID condition.** Compare the stable pre-run hashes to the post-run hashes of the same inputs. If any input hash changed across the run, that run is VOID regardless of how green its output looks: the artifact does not describe the bytes now on disk. Say so explicitly. Only rerun once, and only if the bytes are then stable (use a distinct output name, e.g. `<name>_forge2.txt`).
3. **Bind the artifact to the revision.** Record input hashes, artifact hash, artifact mtime, and exit code together. A report whose internal version/summary cannot be tied to the current input hash is not evidence.
4. **Pre-check before duplicating.** Before running your own copy of a job that may already be running, check all three: (a) live process, (b) fresh output file (younger than ~30 min), (c) live worker PID. Any present -> poll (up to ~180s) and relay or await the existing run instead of duplicating. Two concurrent probes contend for the same browser/port/GPU and can both fail.
5. **Relay verbatim.** When asked to relay an evidence file, paste the raw output in code blocks with no summarizing, truncating, or reformatting. When you used someone else's run, say `reported existing run, no duplicate`. Give the tee/capture path plus as much raw output as fits only when the reply window is genuinely tight.
6. **Scope fence.** A delegated run authorizes only the named directory. Do not hand-edit files, and do not touch sibling dirs, production, or live sites even when the protocol seems to invite it. Only the probe's own outputs plus a read-only snapshot dir are writable.

## Pitfalls

- A fresh, human-readable output file is not proof of a *valid* run. Check a frozen-dir pre/post hash pair before trusting it; a crash traceback sitting in the "final" stdout file is a failed run, not evidence.
- `pgrep -af <pattern>` matches your own shell wrapper. Filter to the interpreter process (exclude `bin/bash`, `snap-`, `hermes_cli`) or you will falsely conclude a run is active or inactive.
- A double-hash quiescence check on the *inputs* and a VOID check on the *outputs* are different gates. Passing the first does not excuse skipping the second.
- Concurrent agent runs against one shared, still-being-edited probe file make clean binding impossible. The fix is environmental, not procedural: freeze the probe (stop edits), then run once with pre/post hash pinning so the artifact binds.
- HTTP/browser probe failures that look like product defects (`TimeoutError` waiting on a selector, `click` timeouts) are often harness/timing flakes under contention. Run the same revision twice before calling it a defect; identical tests passing on one run and failing on another is flake, not failure.
