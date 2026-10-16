---
name: h1-bugbounty-farm
description: "Use when running an automated HackerOne bug-bounty pipeline."
version: 1.0.0
author: Hermes Agent (testing profile)
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [hackerone, bugbounty, automation, recon, cron]
---

# HackerOne bug-bounty farm (draft-only pipeline)

Architecture and the hard-won operational rules for a 24/7 bug-bounty pipeline
that stays inside program policy. Built and verified on the `testing` profile
with the `hackerone-mcp` npm server wired in.

Supporting depth:

- `references/tool-gotchas.md` — every silent-failure form of each recon tool,
  pipeline script and API call, grouped by layer.
- `references/finding-class-exclusions.md` — the class-level taxonomy of what
  programs refuse to pay for, the exact exclusion wording, and how to redeem a
  finding via its conditional clause.
- `references/apk-static-analysis.md` — the read-only recipe for reviewing a
  shipped APK/IPA, from artifact pinning to impact evidence.

## When to use

- Setting up or resuming an automated HackerOne hunting pipeline.
- Any "can you earn money from this 24/7" request.
- Adding programs, targets, or a new scan layer to an existing farm.

## Non-negotiables (these protect the account)

1. **Draft-only by default.** `submit_report` / `submit_report_intent` are never
   called by automation. Every submission is a human decision. Submissions are
   irreversible.
2. **Absence of a ban is not permission.** Default verdict is
   `UNSPECIFIED` → treated as `MANUAL_ONLY` (passive only). A program is only
   `automation_ok` when an allow-phrase was actually read in its policy.
3. **Never defeat bot protection.** If a policy page is behind a Cloudflare
   challenge, record "policy unreadable" and stay manual — do not try to bypass
   it. Getting flagged costs the whole account.
4. **Read per-scope instructions, not just the program policy.** Matomo's
   restriction (`no automated tools`) lives in the scope instruction, not the
   policy. Those scopes are blocked individually.
5. **LLM-generated reports are a real ban risk.** Nextcloud's policy closes
   "AI slop reports" as spam and blocks the researcher. Every draft must be
   manually reviewed and reproduced before submission.
6. **"No automation allowed" means manual testing, not no testing.** When a
   program bans scanners, the subagent still hunts — with individual `curl`
   calls at human speed, reading JS, and tracing logic. Never respond to a
   policy ban by skipping the target.

## Operating mode (user's standing preference)

- **Draft-first, always.** The user explicitly wants results that could be
  submitted delivered to them first, and wants to see demonstrated performance
  before any auto-submit is switched on. Keep `submit_report` /
  `submit_report_intent` out of every automated path until the user says
  otherwise in that conversation.
- **Report performance honestly.** A hunt that finds nothing must come back as
  an honest NOTHING with what was checked. Manufacturing a finding to look
  productive is worse than an empty cycle — and the user asked for visible
  "kinerja", not visible activity.
- **The user wants a hunting system, not a data collector.** When asked to
  build an automated money-making pipeline, deliver parallel subagents with
  real missions against real targets. A passive recon + triage loop that never
  issues a probing request will be judged as "not powerful" and earns nothing.
- **Evolve the machinery natively, without asking.** When you identify a defect
  in your own pipeline — a gate that lets a bad draft through, a status that
  lies, a queue that picks the wrong asset — fix it in the same turn and report
  what changed. Do not offer the repair as one option beside "keep going"; the
  user reads that as stalling. Ask only when the next action would change
  something on a target's production system.

## Parallel-worker ownership (the rule that prevents double-booking)

A ledger status alone **cannot** distinguish "worker died" from "worker is
mid-hunt" — both look identical, and a sweeper that reclaims on a timestamp
alone will steal a target out from under a live subagent.

- Every subagent writes a heartbeat file as its FIRST action and refreshes it
  every few minutes: `briefs/.hunt_<target_id>.alive`.
- The sweeper reclaims a `hunting` target only when **no fresh heartbeat
  exists** (older than ~20 min) AND the row's `last_attempt` is also stale.
  A fresh heartbeat protects the row unconditionally.
- The brief itself must carry the heartbeat command, or the subagent never
  writes it and every target looks dead.
- Capacity accounting (`--max-active-children`) must count protected rows as
  consumed, or the orchestrator over-dispatches.
- `reconcile.py` must clear the heartbeat when it frees the target. A surviving
  `.alive` file makes the sweeper report a finished target as protected forever
  and capacity reads as consumed.

## Layer architecture

```
Layer 0  /mnt/h1-farm/{data,scans,findings,drafts,briefs,logs,scripts}
         ledger.db = programs, scopes, scan_targets, findings, drafts, runlog

Layer 1  passive_recon.sh <handle> <asset>   subfinder → httpx (rate-limited) → gau
Layer 2  triage.py <handle>                  artifacts → candidate leads
Layer 3  validate.py <handle> <candidates>   control+probe requests → verdict + evidence
Layer 4  draft.py <handle> <validated>       CONFIRMED → review-ready draft

Hunting layer (the part that actually finds bugs — this replaced the
passive-only `cycle.py` collector, which produced no findings):
  hunt_brief.py    --pick N | --handle H --asset A   → one self-contained brief per target
  orchestrator.py  --pick N --max-active-children M  → capacity check + dispatch manifest
  reconcile.py                                     → read hunt_*.md reports, update ledger, free targets
  policy_gate.py  --handle H --class C --report R  → may this FOUND become ready_for_human?
  sweeper.py                                       → repair ledger before every cycle
  secret_scan.py    <path>                         → dependency-free secret scanner for cloned repos

Cron  every 45m: agent prompt runs sweeper → orchestrator → delegate_task(2 briefs)
       → subagents hunt in parallel → reconcile → report to the user
```

The brief is the contract with the subagent. It carries program facts, scope
instruction, automation verdict, passive intel, a mission matched to the asset
type, the hard rules, the heartbeat command, and the exact report/evidence paths.
A subagent must be able to hunt from the brief alone — it never shares session
history.

### Mission by asset type (highest ROI first)

| Asset type | Mission | Why |
|---|---|---|
| `SOURCE_CODE` | clone shallow, read auth/authorisation, input sinks, secrets, `git log` on sensitive paths, dependency CVEs; local PoC only | zero infra risk, highest yield, works when automation is banned |
| `URL` / `WILDCARD` | manual web testing: JS files, auth/session, IDOR, injection, business logic, misconfig | needs live requests, so rate caps apply |
| `APPLE_STORE_APP_ID` / `GOOGLE_PLAY_APP_ID` / `HARDWARE` | inspect only if a downloadable artifact exists; otherwise report "not feasible here" | cannot install/run on this host |
| `DOWNLOADABLE_EXECUTABLES` | download + `strings`/embedded endpoints; no dynamic execution | static analysis only |

Mobile and desktop artifacts get the full recipe in
`references/apk-static-analysis.md`.

### Target selection: rotate asset classes, don't hammer the crown jewels

A farm that keeps dispatching the same *kind* of asset burns its budget on the
most-contested surface on the platform and reports NOTHING round after round.
The most-audited assets (a framework's core auth/2FA app, its main web app, its
flagship repository) have had years of researcher attention; a clean negative
there is the expected outcome, not a signal that hunting is broken.

- **Rotate deliberately.** After two consecutive NOTHING rounds on one asset
  class, switch class for the next round rather than picking the next repo of
  the same program. The classes in rough order of contest density:
  core/2FA source code → main web app → desktop/mobile client →
  obscure satellite app → non-web (hardware, desktop binary).
- **Mobile and desktop artifacts are under-hunted relative to their payout.**
  A shipped APK is a complete, static, publicly downloadable attack surface
  that needs no rate limits and no live instance — the single best target when
  a program bans automation.
- **Large programs have many in-scope assets for a reason.** A program with
  100+ scope entries is telling you where it is *not* defended; spend the
  budget there instead of on the one asset everyone already read.
- **A NOTHING round is only worth its cost if it records what was cleared.**
  Require the negative-result section (what was checked, and why each area is
  clean) in every report — that is what stops the next round re-deriving it.
- **Require the severity-deciding question to be named, not buried.** The best
  report this pipeline produced stated the single fact that decides severity
  ("does production override the hard-coded default?") and refused to claim
  beyond it. A brief that only asks for a verdict gets an unqualified High;
  ask explicitly for the open question and the assumption behind the score.
- **Require liveness testing before a secret is called a finding.** A credential
  found in history is a candidate until proven live; test it read-only and
  record the dead ones as dismissed with the reason, so the next run does not
  re-report them.

## Tool gotchas

Every recon tool, pipeline script and API call in this farm has at least one form
that fails silently — exit 0, empty file, plausible-looking wrong answer. The
full verified list, grouped by layer, is in `references/tool-gotchas.md`. The
ones that cost the most time, and the general rule behind each:

- **A sentinel return value on every input means the function is broken, not
  lenient.** `sweeper.age_minutes()` returned `1e9` for every timestamp because
  the guard and the `strptime` format disagreed; when a guard passes but the
  parse still fails, the function lies to every caller. Unit-test it against the
  format the writer actually emits.
- **A manifest parse failure is your own format string first.** `orchestrator.py`
  searched for a 2-space-indented marker while `json.dumps(indent=1)` emitted 1
  space, so seven dispatches wrote briefs, locked targets, and produced zero
  subagents. Grep the raw text for the exact bytes you search for.
- **Scope every UPDATE/DELETE to the row you meant.** `reconcile.py` freed every
  `hunting` row of a program instead of the hunted asset, retiring live hunts.
  Match the asset slug embedded in the report filename.
- **Re-running a reconciler must not duplicate its rows.** Key inserts on the
  report path or `(program_handle, title)` with an upsert, or the drafts table
  grows a row per run and the count the user asks for becomes unanswerable.
- **Silent-empty beats loud-fail.** `gau -o` exits 2 (caught), but a 0-byte
  `urls_*.txt` is indistinguishable from "no archive URLs" — check the run's own
  `urls_total=` log line before believing a scan completed.
- **A packaged tool name is not proof of the real tool.** The npm `trufflehog`
  is an interactive wrapper that dies under `< /dev/null`; when a tool needs a
  TTY, write a small dependency-free script instead of forcing it.
- **A JSON:API document is not a list — and the failure is silent.**
  `all_programs.json` is `{"data": [...]}`. Iterating the dict yields the
  string `"data"`, the comprehension throws, the bare `except: return {}`
  swallows it, and every `policy_gate` run then reports
  `FAIL PAYS: offers_bounties=false` for ALL 596 programs. A loader whose
  output is `{}` on a file you know has 596 entries is broken, not empty —
  assert a non-zero count before trusting it.
- **A `^`-anchored exclusion pattern without `re.M` is invisible.** Programs
  that write exclusions as bare bullets ("* Brute force, DoS, DDoS, ...") need
  `re.I | re.M`; without `re.M` the anchor never matches and the gate passes a
  class the program explicitly excludes. Test every new gate in BOTH
  directions: a fixture that must block AND one that must pass.
- **A marketplace listing page is not a git remote.** Scope assets like
  `https://plugins.matomo.org/developer/matomo-org` produced a brief whose
  "clone URL" was the HTML page, so every child failed on step 1. Resolve the
  org's repos in the orchestrator (`api.github.com/orgs/<org>/repos`) and only
  treat a URL as a clone target when the host is github/gitlab/bitbucket.
- **Read the program's real policy before dispatching, not after.** Matomo's
  policy kills an entire finding class ("Brute force, DoS, DDoS ... out of
  scope") and also demands validation in a real running instance; a locally
  proven ReDoS is therefore `gate_blocked:IN_SCOPE` even with a captured
  CPU-growth curve. Budget the read-up-front cost against a whole wasted round.

## Regex and scanner pitfalls

See `references/tool-gotchas.md` (Secret scanning). The one rule worth
remembering without opening it: a scanner that reports zero findings on a repo
containing a real token is indistinguishable from a broken regex, so validate
every pattern against a fixture with known-good samples.

- **A detector for affirmative proof must be vetoed by an admission.** A pattern
  built to match "confirmed on production" also matched "production
  verification blocked" — the words overlap, so a gate passed a report that
  admitted it was unconfirmed. Test every proof/evidence pattern against the
  report that FAILED to prove it, and let the negative match win whenever both
  fire.
- **A gate that wrongly passes is worse than no gate.** It turns your own
  honesty check into a false endorsement the user then acts on. Verify every new
  gate in BOTH directions — a fixture that must block AND a fixture that must
  pass — or you have built a permanent jam that silently stops all drafts.

## Orchestration: the ledger is the only memory

Every target row carries `status` (`queued`|`hunting`|`done`|`blocked`), `attempts`
and `notes`. The orchestrator selects only from `queued`, so a target being
hunted (or already hunted) can never be double-booked — *provided the state is
true*. These bugs broke that guarantee and all are now fixed:

1. **Stale `hunting` wedges the whole farm.** A dead subagent leaves its row in
   `hunting`; capacity then looks consumed forever and no new work is picked up.
   Fix: `sweeper.py` releases `hunting` rows older than `--stale-minutes`.
2. **The sweeper killed live hunts.** Releasing on `last_attempt` alone fired on
   targets whose subagent was actively working (it writes no timestamp). Fix:
   the heartbeat file above makes a fresh row untouchable.
3. **One report retired a whole program.** Marking every `attempts>0` row of a
   handle `done` silently retired 5 Nextcloud repos nobody had reviewed. Fix: a
   report covers ONLY the asset named in its filename
   (`hunt_<stamp>_<asset-slug>.md`), matched by slug.
4. **Re-running the reconciler duplicated its rows.** ~17 reports produced 60
   `drafts` rows with the same title repeated up to seven times, so "how many
   drafts do we have" had no answer. Fix: upsert on the report path.

Run `sweeper.py` at the start of every orchestrator cycle — it is cheap and
idempotent — and `reconcile.py` after every hunt batch.

## Subagent result JSON is unreliable — trust the disk

One subagent finished 2h10m of real work (161 tool calls, 4 executed PoCs, a
273-line report with CVE analysis) and then reported
`{"verdict":"NOTHING","report_path":"","note":"No work product exists"}`.
The report was on disk the whole time; only the summary JSON was wrong. **Always
verify a subagent's claim against `findings/<handle>/hunt_*.md` before telling
the user nothing was produced.**

- **A subagent can die with `no reply / loop_error` after ~250 API calls and ~77
  minutes** — far past the 25-minute brief budget — while leaving its real work
  product intact on disk. Before concluding a child produced nothing, read
  `findings/<handle>/hunt_*.md` AND `findings/<handle>/evidence/`: a dead child
  with 11 evidence files and a written `00_provenance.json` recording its own
  verdict is a finished hunt whose *summary* was never delivered. Reconstruct
  the report from the evidence (each candidate JSON carries file, lines, commit,
  hypothesis, method, result, assertions_run/passed) and reconcile it normally —
  that is a legitimate close, not a fabrication.
- **Put "write the report file BEFORE your final summary" in every brief.** When
  the model dies mid-summary the report on disk is the only survivor; a brief
  that only demands a final VERDICT line loses the work.
- **A child that returns `cannot_comply` / "no task context" may still have done
  the work.** One child returned exactly that JSON after 251 API calls while its
  tool trace shows it wrote a 15 KB report plus 8 evidence files. Read
  `findings/<handle>/hunt_*.md` and `evidence/` before believing a child produced
  nothing; reconcile from the disk, never from the summary alone.
- **`reconcile.py` can report `freed_targets: 0` and still be correct** — it
  frees targets still marked `hunting`; a target the orchestrator already marked
  `done` in a repair pass reports 0. Verify with
  `SELECT status FROM scan_targets` (columns are `program_handle`, not `handle`)
  rather than trusting the freed count as the dispatch signal.
- **A `VERDICT: FOUND` subagent summary is a claim until you re-execute the PoC
  yourself.** One child reported two Shopify library findings with exact code
  lines; re-cloning the repo at the same commit and re-running the library's own
  functions confirmed both (SSRF delivered a real POST carrying `client_secret`
  + `refresh_token` to a chosen host). Reproduce the strongest claim
  independently before reporting it — and when your own reproduction fails first
  (`network_error`, host never hit), suspect your test rig (the constructed URL
  is `https://` while your capture server was plain HTTP) before doubting the
  child.
- **A brief whose clone URL is a literal wildcard is unusable.**
  `https://github.com/Shopify/*` cannot be cloned; the child must enumerate the
  org first (`curl -s
  'https://api.github.com/orgs/Shopify/repos?per_page=100&sort=pushed'`) and
  pick small tractable repos. Put the enumeration command in the delegate
  context, not just in the brief.

- Put the farm on `/mnt`, not `/` — the root filesystem has only ~7G free.
- `sort -u | head -20000` on gau output; cap subfinder with `timeout 180`.
- Evidence filenames must be deterministic: use
  `hashlib.sha1(url.encode()).hexdigest()[:10]`, never Python's `hash()`
  (PYTHONHASHSEED differs per process).
- Filter doc/marketing paths (`/docs/`, `manual`, `changelog`, `blog`…) out of
  `exposed_path` candidates — otherwise 90% of the list is public documentation.
- Record every run in `ledger.runlog`; a cycle that cannot be audited cannot be
  resumed after compaction.

## Ledger repair (run before every dispatch)

A queue that is never repaired silently stops producing work. Repair these in
order, every cycle, before picking targets:

1. **Stale `hunting` rows** — a subagent that crashed, was stopped, or whose
   session ended leaves its target locked forever. Capacity then reads as full
   and the farm goes quiet with hundreds of targets still queued. Release these.
2. **Protected live rows** — never release a target whose heartbeat is fresh
   (see the ownership rule above). Reclaiming a live target is how two hunters
   end up on one asset.
3. **Already-covered rows still `queued`** — targets with attempts > 0 whose
   asset is named in a reconciled hunt report get marked `done`, not `blocked`:
   a *different* asset of the same program is still fair game.
4. **Policy-banned programs** — any program whose verdict is `banned` /
   `manual_only` has its queued rows moved to `blocked` so they are never
   dispatched as automation targets.

Verify a repair pass by printing status counts before and after. A pass that
changes nothing on a farm with hundreds of queued rows and one `hunting` row
is itself a bug — and a pass that releases a row whose worker is still writing
is a worse one.

## Running batches without fooling yourself

- **Never wrap a target loop in `nohup bash -c '...' &` and treat the completion
  notification as the batch result.** The launcher shell forks, returns instantly
  with exit 0, and the gateway reports "completed normally" while the loop is
  still on target #3. Read the loop's own `### <handle> DONE` marker and check
  `ps -eo pid,etime,cmd | grep -E 'passive_recon|gau'` before reporting progress
  or claiming a target was scanned. This produced a false "batch finished" this
  session; the log ended mid-list with 5 of 9 targets never attempted.
- **A target whose `urls_*.txt` is 0 bytes was NOT scanned** — it means subfinder
  produced no subs, or the run was killed before the gau step. Distinguish that
  from a genuine "no archive URLs" result by checking the run's log for the
  `urls_total=` line; only that line is evidence the layer completed.
- To stop a runaway batch: resolve the child PIDs first
  (`ps -eo pid,cmd | grep passive_recon | grep -v grep`) and `kill` them by PID in
  a short retry loop — the wrapper respawns the next target between iterations.
  On this host `pkill` is denied by an approvals rule; do not retry or rephrase it,
  kill by PID instead.
- Launch bounded multi-target batches with `terminal(background=True, notify=True)`
  running the loop **directly** (no `nohup ... &` indirection) so the notification
  really does mean the batch ended.

## Program selection: audit BEFORE hunting

Auditing all 596 programs takes ~5 minutes and saves days. The fields that
matter, in order:

| Field | Where | Why |
|---|---|---|
| `offers_bounties` | `GET /v1/hackers/programs` | 290 of 596 pay; 306 do not, whatever the scope page implies. |
| `submission_state` | same | 450 open, 146 paused. `state` is always `public_mode` — never filter on it. |
| `policy` | `GET /v1/hackers/programs/<handle>` | See the trap below. |
| `structured_scopes` | `.../structured_scopes` | `asset_type` decides reviewability: `SOURCE_CODE`, `GOOGLE_PLAY_APP_ID`, `APPLE_STORE_APP_ID` are static-analysis friendly. URL-only scopes need live traffic you may not be allowed to send. |
| per-asset flags | each `structured_scopes` entry | `eligible_for_bounty: false` on an asset means $0 even when the program flag is true, and `max_severity` is a cap, not a payout tier. Read all of `eligible_for_bounty`, `eligible_for_submission`, `max_severity` — not just the program-level `offers_bounties`. |

**The policy trap.** `GET /v1/hackers/programs/<handle>` returns a single
JSON:API *object*, not an array. Writing `d['data'][0]['attributes']['policy']`
raises or silently yields empty, and every program then scores 0 — an audit that
concludes "all 220 clean" is broken, not good news. Fetch it as
`d['attributes']['policy']` and assert the non-empty count before scoring.

Four classifications decide everything:

1. **`BANNED`** (9/220 paying) — policy says no automated tools; a scanner report
   is closed N/A. Vimeo, Algolia, Razorpay, Braze, PayPal, Udemy, Kayak, Meesho,
   Compass. Exclude entirely.
2. **Finding-class exclusions** (6/220) — some programs exclude exactly what we
   produce. Basecamp: hardcoded keys from APK/IPA out of scope unless chained to
   cross-user impact. Reddit: mobile hardcoded secrets (Sentry/Firebase/Branch)
   out of scope. MoonPay, Ripio, OKG, Netflix similar. Two further shapes now
   kill a code-review finding outright: "reports based solely on code analysis /
   automated tools / AI output without demonstrated exploitability" and
   "anything already public in our open-source code is out of scope" (Matomo).
   The full taxonomy and the exact wording live in
   `references/finding-class-exclusions.md`.
3. **`offers_bounties` can still mean $0** — Nextcloud is the canonical trap: pays
   nothing, every asset carries `eligible_for_bounty: false`, and AI-generated
   reports are closed as Spam with researcher suspension. Always read the policy
   header; never trust the scope table alone. (Same trap on
   `com.nextcloud.talk2`, whose `max_severity: medium` read like a payout tier.)
4. **`ALLOWED_WITH_LIMITS`** (10/220) — the sweet spot. PortSwigger
   ($100-$15,000), MercadoLibre ($200-$9,460), eero, Twilio, Audible, Ring,
   Amazon VRP, Slack, Wells Fargo, Flutter UK&I. Automation permitted if
   throttled and identified by the required User-Agent.

Best fit for a static/manual-review approach: **Exodus** (7 SOURCE_CODE + 5
mobile assets, 61 scopes, $100-$100,000), **Snapchat**, **Plaid** (5 source
repos incl. plaid-link-android), **OPPO** (100 scopes, 14+18 mobile).
Strict-signal programs (`neon_bbp`) gate submissions on a HackerOne-calculated
signal score — high risk until the account has reputation.

## Report format: match the form, not a document

HackerOne has no fixed report structure, only separate form fields: `title`
(<150 chars), `vulnerability_information`, `impact`, `severity_rating`,
`weakness_id`, `structured_scope_id`. A single `.md` file is an internal
artifact; the submitted body is the text of those fields, with Markdown used
only as formatting.

Per-program rules override generic quality advice. Nextcloud demands: the
product/app version (missing = closed N/A), your own reproduction with
screenshots, manual validation, LLM-use disclosure, no leaking the report to
external AI services, and short concise reports. Basecamp explicitly bans
scanner output and theoretical impact. Notion, Deribit, Chainlink, Ping and
Neon all require one vulnerability per report and full reproduction details.

## The `ready_for_human` gate: a finding is not a draft until it survives four checks

Several rows reached `ready_for_human` in one night and **none was actually
submittable** — one program pays nothing, one excluded the finding class as
phishing, one had no production evidence. `VERDICT: FOUND` plus a well-written
report is not the same thing as a report that can be submitted. `reconcile.py`
now runs `policy_gate.py` on every FOUND before it may set that status:

1. **PAYS** — `offers_bounties` AND a policy header that does not contradict it
   AND `submission_state=open`. Nextcloud is the standing example: flag set,
   policy says no monetary reward at any severity. Read the policy text, never
   the flag alone, and check the per-asset `eligible_for_bounty` too.
2. **IN_SCOPE** — the finding class is not excluded. Match the weakness against
   the program's out-of-scope list *before* drafting. Open redirect is excluded
   as phishing by WordPress; hardcoded keys from APK/IPA by Basecamp unless
   chained to cross-user impact; mobile hardcoded secrets (Sentry, Firebase,
   Branch) by Reddit; "already public in our open-source code" by Matomo. A
   finding inside an exclusion is a NOTHING for that program no matter how
   cleanly it reproduces.
3. **PROVEN** — the report itself carries production evidence, not only a local
   PoC. A finding proven only locally, whose production path sits behind bot
   protection, is labelled "locally proven, production unverified", the blocked
   attempt is saved as evidence, and it is never presented as confirmed.
4. **NOT_HOSTILE** — the policy does not treat AI/LLM-generated or unvalidated
   reports as spam.

Gate failures are recorded, never fatal: the report is still written, the target
still moves to `done`, and the draft status becomes `gate_blocked:<reason>` (or
`needs_human_check:<reason>` when only one check is inconclusive rather than
failed). Retro-gate the existing `ready_for_human` rows after installing the
gate — the stale ones do not fix themselves.

A well-documented negative is worth more than a draft that gets closed as spam
and costs reputation. But when a finding DOES pass all four checks, the report
is the asset: keep the single open question that decides severity in the open
rather than resolving it by assumption.

### Driving a blocked finding to submittable

A finding blocked only by check 3 usually needs one authorised request against
the live asset — e.g. submitting the recovered default credential to the
exposed endpoint. That request changes state on someone else's server, so it is
not a step the pipeline takes on its own: name the exact request, the two
possible outcomes, and what each means for severity, then let the human
authorise it.

## Reporting the pipeline honestly

- A candidate is a LEAD. Report it as a finding only after a control+probe pair
  proves the behaviour difference and the artifacts are saved.
- Keep RULED_OUT results — they are the evidence that the target was actually
  tested, and they stop the next cycle repeating the same probe.
- **Say plainly when the pipeline has produced nothing yet.** An honest "5
  targets covered, no findings, here is what was checked" is required — never
  pad the report with candidate counts that are only documentation pages.
- **Verify the pipeline's own machinery before trusting a round's output.**
  A round that reports "dispatched N briefs" may have dispatched zero
  subagents. Cross-check the ledger's `hunting` count against live processes
  and against the `hunt_*.md` reports on disk — a `hunting` row with no
  heartbeat, no report, and no process is a bug, not a hunt. Likewise a `done`
  row with no report behind it is false coverage, not a completed hunt.
- **Report the payout reality, not the severity label.** A "medium" finding on a
  program that pays nothing is worth $0; say so in the same breath as the
  finding. The user is optimising for money, not for CVSS.

## Related skills

- `mcp-server-integration` — wiring the HackerOne MCP server into a Hermes
  profile (audit → probe → register → apply → verify) and the `hermes mcp add`
  TTY prompt fix.
- `pentest-run-discipline` — caps, the handoff template, and the plain-language
  handoff for anything that keeps running after the turn ends.
