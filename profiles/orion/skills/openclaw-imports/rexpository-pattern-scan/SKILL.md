---
name: rexpository-pattern-scan
description: Use RExpository-style regex catalog scanning during reverse engineering, source audits, APK/webapp triage, leaked secret hunts, config review, log analysis, git history review, or detection engineering. Trigger when looking for API keys, credentials, password hashes, auth tokens, config secrets, suspicious URLs, encoded blobs, or high-signal string patterns in decompiled code, source trees, extracted APK assets, logs, or repositories. Complements reverse-engineering; it is a fast triage lane, not proof by itself.
---

# RExpository Pattern Scan

Fast regex-catalog triage for RE and automation targets.

Source idea: `JaimePolop/RExpository`, a curated regex catalog for hashes, API keys, credentials, and miscellaneous security patterns.

## When to use

Use this as an early or mid-stream triage lane when a target has text-like artifacts:
- decompiled APK output, smali, jadx sources, assets, resources
- web bundles, JS chunks, config files, env files
- logs, packet dumps, HAR exports, captured responses
- git repositories or extracted git history
- binary strings output

Do not use this as the only RE method. Hits are leads. Prove important findings with xrefs, runtime traces, request replay, or downstream behavior.

## Default workflow

1. Run a high-signal scan first, excluding noisy false-positive-marked patterns:

```bash
python3 ~/.openclaw/workspace/skills/rexpository-pattern-scan/scripts/rex_scan.py /path/to/target --summary --json-out /tmp/rex_hits.json
```

2. If the target is small or the high-signal pass is too quiet, include noisy patterns:

```bash
python3 ~/.openclaw/workspace/skills/rexpository-pattern-scan/scripts/rex_scan.py /path/to/target --include-fp --summary --json-out /tmp/rex_hits_fp.json
```

3. For git history, scan generated logs rather than cloning through the original Go client:

```bash
git -C /path/to/repo log -p -n 1000 --since='5 years ago' > /tmp/target-gitlog.patch
python3 ~/.openclaw/workspace/skills/rexpository-pattern-scan/scripts/rex_scan.py /tmp/target-gitlog.patch --include-fp --summary
```

4. Promote only actionable hits into the active RE notes:
- exact file/path and pattern name
- surrounding boundary: auth, signing, config, payment, reward, WebView, JNI, parser, etc.
- whether the hit is hard evidence, weak indicator, stale test data, or false positive
- next proof step

## Interpretation rules

- A regex hit is not proof of a valid secret or algorithm.
- False-positive-marked patterns are useful only as broad sweeps or when correlated with names, paths, or xrefs.
- Prefer hits near boundary code: request builders, headers, env loading, SDK init, wallet/payment code, captcha/ad/reward endpoints.
- For APKs, run after `jadx`/`apktool` and also scan `strings` output from native libs.
- For web bundles, scan minified chunks and source maps if present.
- For logs/HARs, redact sensitive values before reporting to chat.

## References

- For scanner details and field meanings, read `references/scanner-notes.md`.
