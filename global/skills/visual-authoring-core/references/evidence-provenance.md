# Evidence Provenance & Closure — Recipes

Concrete techniques for verifying a hand-off you did not execute yourself, and for closing
a task honestly when you lack part of the capability. Companion to SKILL.md §5.

---

## 1. Re-deriving an assert count from a report JSON

A probe report often summarizes itself (`{"passed": 208, "total": 208, "failed": []}`) and
separately carries the detail (`asserts: {"390x844:name": true, ...}`). The summary is a claim;
the detail is the artifact. Count the detail.

Gotcha: assert keys contain an internal colon (`"390x844:zero_console_errors"`), so a naive
grep for `": true` over the whole file also matches unrelated booleans and mis-counts. Anchor the
pattern to the colon-keyed shape:

```
# count all assert-shaped booleans
"[^"]*:[^"]*": (true|false),

# count only the failures
"[^"]*:[^"]*": false,

# scope to the known context prefixes
"(390x844|1280x800|412x915|reduced_390x844|reduced_1280x800|touch|prototype_has)[^"]*": (true|false),
```

Then reconcile: `true_count + false_count` should equal the reported total. If the report also has
colon-free keys (e.g. `prototype_has_no_infinite_animation`), add them explicitly — a total that is
1 more than the scoped count is usually exactly this, not a missing assert.

**Rule:** state the count you derived and the method, not the count someone told you.

---

## 2. Rendering vs. static checks — use both, and say which you used

| Claim | Cheapest real check |
|---|---|
| "N asserts pass" | re-count the report JSON (above) |
| "forbidden pattern absent" | regex the source file for the exact pattern |
| "self-contained / no CDN" | regex for `http(s)://`, `src="//`, `cdn.` — then read each hit; a footer *anchor* is a link, not a loaded resource |
| "tokens match the spec" | grep the token names in each artifact and compare values literally |
| "the animation renders mid-flight" | load the PNG with the vision tool and describe what is actually visible |
| "first paint is complete" | load the first-paint PNG and confirm the named elements are present and opaque |
| "the run was isolated" | read the script's own path resolution AND the report's `url`/input field — the fact that a copy exists is not the fact that it was used |
| "the same revision ran" | compare file sizes/hashes across live, isolated, and frozen copies |
| "the corrected predicate is the code that ran" | read the predicate in the *frozen* copy at the line it is defined, not the live file |
| "the predicate discriminates" | confirm it returns the *other* value somewhere in the same report (see §8) |

Load the *key* screenshots with the vision tool rather than only citing their filenames. If you
cannot read pixels in your session, say the render claim is relayed.

---

## 3. Establish that a superseded failure is unreachable

When `.frozen/`, `VOID_*`, or `RERUN_*` artifacts show earlier failures, do not just note them.
Bind each failure to the revision it came from and show the current revision cannot reproduce it:

1. Read the frozen stdout for the failure mode (crash traceback, failed assert name).
2. Read the pre/post hash files to see which revision was under test.
3. Test the failure's *cause* against the current artifact. Example: a crash waiting on
   `locator("#someSelector")` is unreachable if the current script contains no such selector —
   `grep` the current file for the selector and report the hit count (0 = structurally unreachable).
4. Record the resolved chain: old revision → failure → why the current revision cannot hit it.

---

## 4. Closing a card you do not own the run for

If a completion tool refuses because another (or a concurrent) worker holds the live run:

- Diagnose once. The common kern: the close needs an explicit run id or force flag, while your
  tool schema may not expose either (`unknown parameter(s): expected_run_id`, then `task_id is required`).
- Do not retry the same call shape. Either the owning run finalizes on its own, or you hand the
  operator the exact command (e.g. `hermes kanban complete --force <task_id>`).
- Before assuming a claim is unsupported, re-read the artifact: a concurrent worker may have just
  updated it and closed the card with accurate metadata.
- A card left in `todo` is not automatically "stalled by you" — check its *other* parents. A wave
  can be gated by an unrelated upstream blocked card.
- **`unknown task <id>` on a card call usually means wrong board, not a missing card.** Card
  operations (`kanban_show`, `kanban_comment`, and friends) resolve the *active* board by default,
  which may not be the board the card lives on. Retry once with the board slug passed explicitly
  (`board="<slug>"`) before concluding anything; the task id alone was ambiguous, not invalid.
- **`already terminal` on a close means the metadata is now frozen at the older state.** A card that
  an earlier (or concurrent) run already completed will reject your close, and you cannot update the
  stored summary/metadata. The stale number then sits on the card as the authoritative-looking record
  while the artifact has moved on. Post the correction as a **comment** (comments still land) stating
  the current revision, the current result, and explicitly that the card metadata is stale and should
  not be read as current. Tell the downstream consumer which file to read instead. A comment survives
  where a re-close does not.
- **Distinguish "already terminal" from a concurrent live run.** The first is final and only needs a
  correcting comment; the second may still finalize the card accurately on its own. Check the card's
  status and `completed_at` before deciding which you are looking at.

---

## 5. Enumerate every run artifact before accepting "nothing further is needed"

A peer reporting that a task is closed on already-existing evidence has usually enumerated the
runs they *chose*. Enumerate the directory yourself:

1. List every run log in the evidence dir (`run*.log`, isolated/repeat subdirs, the live report JSON).
2. Read the **first few lines of each** — a probe log usually opens with its own summary block
   (`{"failed": [...], "total": N, "passed": M}`). That is each run's own verdict.
3. Check file sizes: a 0-byte log is a dead run, never a pass. Do not count it either way.
4. Read the live report's top-level `summary` block too — it may be bound to a *different*
   revision than any numbered log.

If a numbered log older than the certified pair shows failures the peer did not mention, and the
newest revision is deterministically red, the cited run is history. Surface the delta instead of
repeating the closure.

**Rule:** the cited run's verdict is not the directory's current state.

---

## 6. Diagnosing a gate that has never been green

When an assert fails on every run of every revision, the first question is not "what broke?" but
"was this ever passing?" A gate that was never green is a calibration bug, and calling it a
regression sends the implementer hunting for a defect that does not exist.

Procedure:

1. **Compare the assert across revisions.** Same failure at 226, 236 and 242 total asserts =
   revision-independent -> suspect the predicate, not the artifact.
2. **Read the predicate, then read the recorded frames it judges.** The verbatim per-frame log in
   the run output usually contains the answer. In the observed case the reduced-motion toast log
   showed `[3] cls="toast-message info" opacity=0 dur=1e-06s` followed by
   `[4] cls="...is-in" opacity=1 dur=1e-06s` — the behavior was already instant, and the assert
   was reading the transition's *starting* frame instead of its settled one.
3. **Ask whether the spec itself mandates the state the assert rejects.** If the motion spec says
   "enter via transition + rAF class-add, never a keyframe", then exactly one pre-class frame at
   opacity 0 is *guaranteed by compliance*. An assert that requires all present frames to be opaque
   penalizes the spec it is supposed to protect. Fix the predicate, not the prototype.
4. **Prefer a predicate that excludes the mandated frame by definition** over one that widens a
   tolerance. Scoping a whole-series property to a narrower window does not help if that window
   still *begins* at the mandated pre-class frame — check the window's first element, not just its
   length.
5. **Record the corrected predicate as a derivation, not as a verification.** If you cannot execute
   it, say the predicate is derived from recorded frames and still needs a frozen run to confirm.
   Never dress an unexecuted fix as green.

**Rule:** a gate that has never passed in any run is probe-side until proven otherwise, and the
spec may be the thing the assert violates.

---

## 7. Attachments without a shell

`kanban_attach` needs inline base64 bytes; `kanban_attach_url` accepts only `http(s)://`, so a
`file://` path cannot be attached. If your session has no shell to produce the bytes:

- Do **not** fabricate a payload.
- Do **not** claim the attachment succeeded.
- Record the deliverables by absolute path (and hash when available) in the completion metadata and
  the comment thread, and name the byte-level step for a worker that can do it.

This keeps the task honest and unblocked while still giving downstream workers (which read the same
filesystem) everything they need.

---

## 8. Accepting a corrected predicate: prove it discriminates

A peer reports that the assert you flagged as mis-calibrated (§6) now passes on a frozen run. Do not
close on "it went green." A predicate can pass for three worthless reasons: it is trivially true,
its sampling window excludes every frame it claims to judge, or the reported result was not produced
by the code you fixed. Each has its own check.

**Non-vacuity — the decisive check.** Find the contexts/frames in the same report where the property
genuinely does *not* hold, and confirm the predicate returns the opposite value there. Example shape:
a reduced-motion gate should be `true` in the reduced contexts and `false` in the normal-motion ones.
If it is `true` everywhere, the run proves nothing and the correction is unverified.

Read the discriminator off the recorded series, not off the boolean. A predicate whose whole-series
property is impossible under one mode should *also* be impossible under the other if it is still
reading the wrong frames — so check the raw per-frame log:

| recorded field | normal motion | reduced motion |
|---|---|---|
| first frame carrying the entered-state class | opacity ~0.33 (mid-flight) | opacity 1 |
| interior frames after that class | > 0 | 0 |
| predicate under test | `false` | `true` |

A predicate that reads `true` in both columns is not discriminating. A predicate reading `false`/`true`
as above is doing exactly the job, and the derivation is now confirmed by run rather than asserted.

**Isolation is a claim, not a directory name.** "Ran in an isolated copy" is unverified until you can
show the run *resolved its inputs there*. Read the script's own path resolution (a probe usually
computes its input from its own file location, e.g. `HERE = dirname(abspath(__file__))`) and then
confirm the report's own recorded input URL points into that copy rather than the live file. A copy
sitting next to a script proves nothing about which path the process opened.

**Byte-equality across all three copies.** Compare the live, isolated, and frozen copies of both the
harness and the artifact (sizes, or hashes when available). All three matching is what lets you say
the same revision ran; a size mismatch means you certified a different file than you think.

**Residual claim you cannot verify from artifacts — say so.** A report cannot prove the *absence* of
a concurrent process, so a peer's "no other run was active at launch" is an execution-side statement,
not artifact-verified. Pre/post hash equality (the bytes did not move *under the run*) is the property
that matters for correctness and *is* checkable; keep the quiescence claim in the peer's voice instead
of restating it as fact.

---

## 9. Updating your own docs after a peer supersedes your hedge

When you previously wrote a hedge ("treat this table as bound to the old pair until a frozen run
confirms"), and the confirming run arrives, **edit the hedge out** rather than appending a resolution
below it. A future reader who greps the doc must not find a live "unconfirmed" statement sitting
above the confirmation.

Do all three: (a) replace the hedge text with the confirmed statement, (b) add the new result as its
own row in the summary table so the newer number is visible next to the older one it supersedes,
(c) keep the old result valid *for the pair it names* while stating plainly that it is no longer a
statement about current disk state. Then post the verification to the card thread with the method
column filled in, so the delta from hedge to confirmation is auditable.

---

## 10. Run-execution hygiene while collecting evidence

Small mechanical mistakes here produce evidence that looks valid and is not. Each has been observed.

**Capture the runner's exit status before anything else consumes `$?`.** In a chain like
`probe.py > run.log 2>&1; cp report.json run_report.json; echo "exit=$?"`, the `$?` is **`cp`'s**
status, not the probe's — so a crashed or failed run is recorded as `exit=0`. Read the status into a
variable immediately after the command of interest:

```sh
probe.py > run.log 2>&1; rc=$?; cp -f report.json run_report.json; echo "exit=$rc"
```

This matters most for the claim "N consecutive runs passed": with the broken form that claim could
not have been falsified by the log at all.

**A report JSON can be a stale copy from a previous run.** If the runner crashes before writing its
report, a subsequent `cp` faithfully copies the *previous* run's file and the copy looks fresh.
Detect it by hash: keep the previous run's report and compare. Byte-identical output across two runs
is either a genuine deterministic reproduction *or* a stale copy — so confirm the log's own summary
and the report's `url`/version fields agree before citing it. Crash runs leave this signature
routinely.

**Read the failure mode before summarizing.** If the log opens with `Traceback`, report the traceback
verbatim. A summary block substituted from a stale report over a crash is worse than no summary.
Check for the traceback before quoting any numbers, and treat a zero-byte log as a dead run, never a
pass.

**Do not confuse a missing key with a failed assert.** An assert that indexes a report field directly
(`v["sheetSettled"]["open"]`) aborts the entire run with a `KeyError` when that field was never
added, which reads like a harness failure rather than the one bad predicate it is. Index defensively
(`(v.get("sheetSettled") or {}).get("open")`) so a missing field fails that single check and the rest
of the report still lands. A crash costs a whole run; a false assert costs one row.

**When delegating a run to a peer that keeps timing out, separate the launch from the read.** A
one-shot request that both launches and waits for a long job exceeds the reply window, while a short
launch-only request succeeds. Send the launch alone (detached, returning the PID and pre-hashes),
then request the reads in a separate message. If a peer reports it "did not reply in time", do not
assume nothing happened: check the filesystem for the expected log, exit file and report, which the
launch usually did produce. Verify from the artifact, not from whether the reply arrived.
