# Scanner notes

`rex_scan.py` uses the upstream RExpository `regex.yaml` schema:

```yaml
regular_expresions:
  - name: Category
    regexes:
      - name: Pattern name
        regex: '...'
        example: '...'
        falsePositives: True
        caseinsensitive: True
        extra_grep: '...'
```

Local behavior:
- downloads/caches upstream `regex.yaml` under `.cache/rexpository/regex.yaml` unless `--catalog` is given
- scans files recursively or a single file
- skips common heavy/generated directories by default
- skips binary-looking files
- caps file size by default
- masks match values by default, preserving enough prefix/suffix for triage
- `--show-secrets` prints raw match values only when explicitly requested
- `--include-fp` enables patterns marked `falsePositives: True`
- `--category` can be repeated to restrict categories
- JSON output is safer for artifacts; stdout summary is for quick triage

Good RE uses:
- find SDK tokens and then xref their consumers
- find password/hash formats and then identify auth backend assumptions
- find hidden endpoints/URLs in web bundles
- detect stale hardcoded test credentials
- scan git history patches for removed secrets

Caveats:
- Python `re` is not PCRE. Most RExpository patterns work, but some may fail compile and are reported in `compile_errors`.
- High-entropy generic tokens can be noisy. Treat them as correlation material, not final evidence.
- Scanning huge repos with `--include-fp` can be noisy and slow. Start without it.
