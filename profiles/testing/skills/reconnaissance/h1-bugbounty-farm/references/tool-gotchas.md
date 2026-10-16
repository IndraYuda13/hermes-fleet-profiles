# Tool gotchas (all verified the hard way)

Every recon tool, pipeline script and API call in this farm has at least one
form that fails silently — exit 0, empty file, plausible-looking wrong answer.
Grouped by the layer they bite.

## Pipeline scripts

- **`orchestrator.py` never parsed its own manifest** — it looked for the literal
  `'{\n  "ok"'` (2 spaces) while `json.dumps(indent=1)` emits 1 space, so every round
  wrote briefs, marked targets `hunting`, then bailed out with "could not parse
  brief manifest". Seven dispatches produced zero subagents. When a manifest
  parse fails, suspect the whitespace of your own format string BEFORE assuming
  the upstream tool failed, and grep the raw text for the marker you search for.
- **`sweeper.age_minutes()` silently returns 1e9 for every timestamp.** The guard
  is `len(ts) < 12` but `ts[:14]` is fed to `strptime("%Y%m%d%H%M%S")`, which
  needs exactly 14 chars. Every `hunting` row therefore looked infinitely stale
  and the real staleness logic never ran. It recurred in a second form:
  `hunt_brief.py` writes `last_attempt` with `strftime("%Y%m%d_%H%M%S")` — 15
  chars WITH an underscore — so the guard passes and `ts[:14]` =
  `20261016_025650` is still unparseable. Normalise the string
  (`ts.replace("_","")`) before slicing, and unit-test the function against the
  *actual* format the writer emits, not the one you remember. Symptom to watch
  for: the sweeper releases a `hunting` row with `"age_min": 1000000000.0` —
  that is the bug announcing itself. A function that returns a sentinel on all
  inputs is broken, not lenient.
- **Reconcile frees the row but does not clear its heartbeat.** After a hunt
  completes, `briefs/.hunt_<id>.alive` survives, so the next round's sweeper
  reports the finished target under `protected_active` forever and capacity
  reads as consumed. Clear the heartbeat file for every target the reconciler
  frees, or delete stale ones at the start of each cycle.
- **`reconcile.py` counted evidence from the wrong directory** — it used
  `dirname(dirname(path))`, resolving to `findings/`, so per-handle evidence
  always read 0. The evidence dir is a sibling of the report:
  `dirname(path)/evidence`.
- **`reconcile.py` missed the verdict** when the report used a markdown
  `## Verdict` section followed by `**NOTHING**`, recording `UNKNOWN` and never
  inserting the draft row. Search the lines *around* the word "verdict", not
  only a strict `VERDICT: X` prefix.
- **`reconcile.py` released EVERY `hunting` row of a program, not just the hunted
  one.** Its update was `WHERE program_handle=? AND status='hunting'`, so
  reconciling a stale report for asset A silently marked the *live* hunt of
  asset B `done` — two subagents on one asset, or a `done` row with no report
  behind it. Fix: match the asset slug embedded in the report filename
  (`hunt_<stamp>_<asset-slug>.md`) against `slug(asset)` and free only that row.
  Verified with fixtures: a report for `matomo-org-innocraft` freed 0 rows while
  `tracker-proxy` was hunting; a report for
  `https-github-com-matomo-org-tracker-proxy` freed exactly that one row.
- **`reconcile.py` must upsert, not insert.** Re-running it over the same report
  appended a second `drafts` row every time, so ~17 reports produced 60 rows
  with the same title repeated up to seven times. Key the insert on the report
  path (or the `(program_handle, title)` pair) with
  `INSERT ... ON CONFLICT DO UPDATE` and add a `UNIQUE` constraint. A drafts
  table with duplicate titles makes "how many drafts do we have" unanswerable —
  exactly the number the user asks for.
- **Never run `orchestrator.py --pick N` just to "check capacity".** `--pick` is
  not a dry-run: it writes briefs and flips rows to `hunting` as a side effect.
  A capacity check that looks harmless created two briefs with no subagents
  behind them; recover by deleting the brief files and restoring the rows
  (`status='queued'`, `notes=NULL`, `attempts-1`). Use
  `SELECT COUNT(*) FROM scan_targets WHERE status='hunting'` for a read-only check.
- **A queue ordered by `priority ASC` is ordered by ROI inverted.**
  `build_queue.py` gives priority 8 to MANUAL_ONLY URL rows and 7 to the
  SOURCE_CODE review queue, so `ORDER BY priority, id` dispatches the
  least-valuable, hardest-to-automate assets first. Sort dispatch by
  bounty-eligibility and asset tractability first, priority second.
- **`/mnt/h1-farm/ledger.db` (root) is not the ledger.** The real DB is
  `data/ledger.db` (`ledger.py` builds `DB = FARM/data/ledger.db`). An accidental
  `sqlite3.connect('ledger.db')` creates a 0-byte file that looks authoritative
  and reports "no such table" — delete it and use the path the module defines.
- **`fetch_submit_ids.py <handle>` prints "no submission-eligible scope found"
  on a 401, not only on an empty scope.** `api()` fails closed with
  `except (URLError, HTTPError, ValueError): return {}`, so a missing
  `H1_API_TOKEN` (cron and subagent shells export no such var) is indistinguishable
  from a program that genuinely has no eligible asset — and the cache is still
  written *without* that handle, so the SUBMITTABLE_IDS gate keeps blocking it
  forever. Symptom: `data/submit_ids.json` regresses to only the handles fetched
  when the token happened to be present. Verify with a direct
  `GET /v1/hackers/programs/<handle>/structured_scopes` and read the HTTP status
  (401 = token missing, 200 + empty list = genuinely ineligible) before believing
  the skip, and skip the cache write when the call was unauthorized.

## Recon tools

- **`gau -o` is not a flag.** This build takes the long form `--o`; `-o` exits 2
  with "unknown shorthand flag" and silently produces an empty file.
- **`gau --blacklist png,jpg` also exits 2.** Bare extension lists are rejected;
  filter static assets in triage instead.
- **Wayback is unusably slow** from this host for large domains (60s+ per fetch,
  buffers until exit). Use `--providers urlscan,otx,commoncrawl`.
- **httpx must be `httpx-pd`**, not the Python HTTP client that owns the bare
  name. Probe with `head -1 $(which httpx)` before wiring any wrapper.

## HackerOne API and MCP

- **A detector for affirmative proof must be vetoed by an admission.** A regex
  written to match "confirmed on production" also matched "production
  verification blocked" — the words overlap, so a gate passed a report that
  admitted it was unconfirmed. Order the checks so the negative pattern wins
  whenever both fire, and test every proof pattern against the report that
  FAILED to prove it.
- **A gate that wrongly passes is worse than no gate.** It converts your own
  honesty check into a false endorsement the user then acts on. Verify every new
  gate in BOTH directions — one fixture that must block and one that must pass —
  or you have built a permanent jam that silently stops every draft.
- **`GET /v1/hackers/programs/{handle}` returns EMPTY attributes.** Program name
  and policy are not there. Get names from the listing endpoint and policies
  from the web page. (See also the policy-object trap in SKILL.md: the endpoint
  returns a single JSON:API object, so `d['data'][0]` silently yields nothing.)
- **HackerOne Hacker API auth is Basic with TWO parts:** token identifier as
  username, token value as password. A token value alone always 401s.
- **Hacktivity searchable fields:** `cwe:`, `substate:`, `severity_rating:`,
  `disclosed:`, plus free text. **Rejected (HTTP 400):** `program:`, `url:`,
  `weakness_id:`, `handle:`, `team_handle:`. A rejected query triggers ~60s of
  rate limiting, so batch dedupe checks.
- **`hermes mcp add` ends in an interactive "Enable all N tools?" prompt.** With
  no TTY it cancels and saves nothing. Pipe `printf 'y\n' |` and put `--args`
  last on the command line.

## Secret scanning

- **Never put `\b` after `=` in a secret pattern.** `=` is a non-word character,
  so a trailing `\b` can never match and the pattern silently matches nothing —
  a scanner that reports 0 findings on a file containing a real token looks
  "clean" instead of "broken". Use a negative lookahead instead:
  `[A-Za-z0-9+/]{39,63}={1,2}(?![A-Za-z0-9+/=])`.
- **Validate a scanner against a fixture file, not just against clean repos.**
  A 0-finding result on real repos is indistinguishable from a broken regex.
  Write a temp file with known-good samples (AWS `AKIA…`, Google `AIza…`,
  `sk_live_…`, `ghp_…`, a 44-char base64 token, plus a `your_api_key_here`
  placeholder) and require: every real secret hits, the placeholder does not,
  and the real repos still report 0.
- **Skip documentation and lockfile extensions in secret scans.** `.md`, `.txt`,
  `.rst`, `package-lock.json`, `go.sum`, `composer.lock` etc. are full of base64
  hashes and version pins; they generate 100% of the false positives and none of
  the findings.
- **An npm package name is not proof of the real tool.** The npm `trufflehog` is
  an interactive wrapper that opens a readline prompt and dies with
  `ERR_USE_AFTER_CLOSE` under `< /dev/null` — it cannot run in a cron or subagent
  context. When a packaged tool needs a TTY, write a small dependency-free
  scanner instead of forcing it.
