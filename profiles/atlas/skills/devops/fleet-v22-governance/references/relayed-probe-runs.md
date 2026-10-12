# Relayed Probe Runs

Executing another lane's probe or script on its behalf, when that lane has no shell or its
process runner is wedged, and handing the raw output back. The relay's product is fidelity
plus provenance, not a verdict.

## Procedure

1. **Preflight the stated scope before running anything.** List the named directory, not just the
   script. Confirm every write target the script needs is inside the allowed scope, and note the
   mtimes/sizes of the artefacts the requester will compare against. A sender's scope statement is
   a claim, not a fact.
2. **Read the script's write surface.** Grep its imports and its `open(`, `Path(`, output-dir, and
   path-join lines. Confirm the output root resolves next to the script rather than to an absolute
   path outside the scope. Check the input URL/host: a `file://` target cannot reach production.
3. **Run the requester's command verbatim.** If it embeds a safety gate (a `grep -E` danger scan
   guarding the run), let the gate decide. Do not pre-empt it and do not reorder the commands.
   - **Backgrounding inside a block cannot be pasted inline:** the terminal refuses a foreground
     command that uses `&` backgrounding or `nohup`, and the whole block dies before its first line
     runs. Save
     the block byte-identical to `$TMPDIR/<relay>.sh`, then run
     `bash "$TMPDIR/<relay>.sh" > "$TMPDIR/<relay>.out" 2>&1` as a `background=true` process and
     read the output file. This keeps the requester's exact redirection, detached launcher, and
     `$!` PID line intact instead of hand-rewriting their launcher.
   - **Background exits report their own status, not the block's**, and often return empty stdout
     because the block redirected to a file. Measure the block's runtime against the requester's
     deadline, and when polling a process, wait in <=60s chunks (longer waits are clamped).
4. **Hash-bind the revision at gate time.** `sha256sum` the script and its inputs plus `wc -l`. That
   output is the revision record the requester asked for, and it is what your report is bound to.
5. **Give a browser probe a generous budget.** Playwright rounds run for minutes. Use a foreground
   timeout well above the stated runtime or start it backgrounded and poll, so it is not killed
   early. A nonzero exit from an assert-driven probe is an expected outcome: capture it, do not
   retry, and do not "fix" it into a pass.
6. **Re-hash immediately after the run, then check for writers.** Compare post-run hashes of the
   script and every declared output against step 4. Then look for processes whose cwd is the
   evidence directory and match them to the board's live worker for that task. Any conditional write
   the block asks for runs after this step, so on a non-empty writer list re-evaluate its gate
   conditions against the bytes as they stand now, not as the requester described them.
7. **Report verbatim, bracketed by the integrity finding.** Paste the requested lines exactly
   (gate text, hashes, exit line, full stdout, post-run hashes, directory tail). Put the provenance
   finding before and after that block so the requester cannot mistake the raw output for a
   certified result.

## Concurrency forensics and snapshot custody

A requester who sees an implausible artefact count ("83 files, did two writers overlap?") is asking a
WINDOW question, not a directory question. Answer it with the run window.

1. **Bound the window from the run's own receipts.** The launcher's pid/token file mtime is the
   start, the stdout/report mtime is the end. Every artefact mtime outside that span belongs to a
   DIFFERENT run and must be excluded before counting.
2. **Count only in-window files, then disprove overlap explicitly:** zero duplicate basenames, max
   files sharing any one second, and a per-prefix census. Report the cumulative directory total and
   the in-window count as two separate numbers — a cumulative total accumulates every prior run and
   routinely lands on a number that reads as concurrency when it is only history.
3. **Cross-check the NOW list, not just the artefacts.** An instance alive at your own timestamp is
   a writer no mtime census can see. Report PID, start time, parent, and script path.
4. **Never kill the newer instance to stabilise a run you were told not to mutate.** Report it;
   remediation (freeze, immutable copy) is the requester's call.
5. **Resolve each live PID to its OUTPUT DIRECTORY, not just its script path.** The scoping question
   has two answers and they invert. An instance running the same script from an unrelated path is a
   false skip: name its path, proceed in yours. An instance whose cwd is the directory you were
   asked to run in already owns that directory's report and artefacts, so a second writer's output
   cannot be bound to either run and the skip is substantively correct. Say which case you are in
   and, when the collision is real, say plainly that a clean run is not achievable in that directory
   until the owning instance drains — a fourth concurrent writer does not produce a certifiable
   result, it produces an unattributable one.
6. **Walk the ppid chain to attribute the writers, then name the shared launcher.** Concurrency
   comes in two shapes that look identical in a process list. Print `ps -o pid=,ppid=,etimes=,lstart=,cmd=`
   for each candidate, then follow `ppid` upward. Instances that converge on ONE parent (typically a
   per-session agent runtime under `systemd --user`, e.g. `bash -c` -> `python3 -I -c` -> a worker
   pid) are a single session double-launching: report it as self-overlap owned by that one lane.
   Instances whose chains terminate in different roots are genuinely independent lanes. Say which
   case you are in. Self-overlap is fixed by the peer's own launcher; cross-lane overlap needs a
   freeze request. Do not collapse the two into "multiple writers are active".
7. **Read the live run's emission state before trusting any stable hash.** A run in flight writes
   its own log first and its report last, so mid-run the PREVIOUS report is still on disk with an
   untouched hash while every sibling artefact drifts. Check the in-flight run's log size and
   whether its exit/result receipt exists: a zero-byte log and an absent exit file mean the report
   you are holding belongs to an earlier run and is not covered by the current one. Report it as
   "stable but not the live run's output", not as quiescence.

## Attributing a score delta across two runs

When two runs of one instrument report different totals (243/245 vs 245/245), the number that moved is
a property of the INSTRUMENT until proven otherwise. Diff in this order:

1. **Subject hash first.** `sha256sum` the artefact under test in both runs, or read the frozen copies.
   Byte-identical across both means the product did not change, so any delta came from the probe, the
   harness, or the environment — not from the artefact the requester believes improved.
2. **Assert key sets second.** Compare the symmetric difference and the flipped values:
   `python3 -c "import json;a=json.load(open(A))['asserts'];b=json.load(open(B))['asserts'];print(sorted(set(a)^set(b)));print([(k,a[k],b[k]) for k in set(a)&set(b) if a[k]!=b[k]])"`.
   Equal sizes, an empty symmetric difference, and a handful of value flips is a gate that was EDITED,
   not a subject that improved. An added or removed key is the same finding from the other side: a
   total that moved because the assert set changed measures a different gate.
3. **Probe hash third.** The two reports' `.frozen/probe_<hash>.py` siblings name the revisions that
   ran; a probe hash that moved between runs, beside an unchanged subject hash, closes the case.
4. **Report it as superseding, never as agreement.** One revision's result replaced another's. Two
   green runs of one subject from two probe revisions are one sample of each revision, not two
   independent samples of the same one.
5. **Never line up totals across schema generations.** A summary total from an older generation of the
   report (different probe version, different assert census) is not a smaller version of the newer
   number. Quote each against its own generation and say plainly that the two are not comparable —
   a versioned filename or an attachment label does not make two generations one series.

## Pre-mutation premise gates

Run these before executing any step of the requester's block that writes, copies, or launches. Each
one tests a claim in the plan against the bytes on disk; a single falsified premise is grounds to
withhold that step and report the evaluated predicates.

1. **Existence of the revision a preservation name asserts.** Before `cp <current> <archive-named-for-a-revision>`,
   resolve the named revision: `sha256sum` candidates and `grep -rl <hash-token>` the evidence tree
   (and `grep -rl <hash-token> .` including hidden dirs). If nothing in the tree carries that hash and
   no artefact of that run exists, the copy would label current bytes with an older run's identity.
   Withhold it.
2. **Whether the work is already done.** Read the on-disk report's emitted fingerprint —
   `python3 -c "import json;d=json.load(open('report.json'));print(d.get('probe_version'),json.dumps(d.get('summary')))"`
   — and compare against the summary the requester attributes to their last-known run. Different
   counts or version means a later run already completed; report it and its hash rather than
   overwriting it with a refresh run.
3. **Exact-path collision test.** `test -e <exact-target>` for every file the block would overwrite.
   Two siblings whose names differ only by a revision token are different files; confirm the exact
   path before reporting a step as destructive.
4. **Directory-level quiescence.** Digest the whole directory in two spaced passes, not just the
   named inputs:
   `find . -maxdepth 1 -type f -printf '%T@ %s %p\n' | sort | md5sum`. A two-file hash gate can
   report OK while a sibling (spec, receipt, review note) is still being written. Compare the digests;
   inequality is a movement verdict.
   Size the gap from the writer's own cadence before trusting a clean comparison: build an mtime
   timeline (`find . -maxdepth 2 -mmin -6 -printf '%TH:%TM:%TS %p\n' | sort`) and read the interval
   between consecutive writes of the same file family. A probe emitting one PNG every 2-3s returns
   byte-identical samples across a 10s double-check while it is mid-run, so a narrow window reports
   FALSE quiescence and the requester freezes onto a moving set. The passes must span more than one
   full write cycle AND a process scan at the same instant must show the writer gone; print the
   window length and the observed cadence so a quiet sample is auditable instead of assumed. When a
   run is in flight, the honest verdict is 'not quiesced, do not bind', with the live writer's PID,
   start, parent, and launching wrapper quoted.
5. **Re-resolve liveness at the mutating step.** A writer scan is point-in-time: an artefact can be
   rewritten after the scan passed and before the run starts. Re-scan immediately before launching and
   treat drift observed after an earlier clean scan as the abort condition firing.

**Reporting a withheld step.** Print each predicate with its evaluated value and the raw quantities
behind it (the hash that is absent, the two diverge digests, the two summaries), so the requester can
re-derive the decision and repair their own plan. Foreground the deviation above the raw block when
the step would have destroyed or mislabelled evidence.

## Pitfalls

- **A preservation target can name a revision that exists nowhere.** The name is a claim about
  content, and `sha256sum`/`grep` the tree is how you falsify it; a hash that matches no artefact
  means the copy is an assertion, not an archive.
- **Grep over a report-shaped log without anchoring matches nested keys.** Intended lines such as
  `skipped: {}` sit beside per-assert keys in the same stream, so `grep -n 'skipped'` can return
  entries the label does not mean. Anchor to line start (`grep -n '^skipped'`, `'^Traceback'`) and
  quote the matched line so the requester sees which it was.
- **`cp -p` preserves the timestamp, not the bytes.** A snapshot you copied for a peer is not frozen
  by the act of copying: with a live writer the source can be rewritten between your `sha256sum`
  and your copy, and both can drift afterwards. Hash copy against source per file at the moment you
  report and print `SAME`/`DIVERGED` for each; on any DIVERGED, state which copies still hold the
  requested revision and which are mid-flight. Do not silently re-copy a moving file to "fix" the
  mismatch — that substitutes a later revision for the one the peer asked for.
- **A pid file's content is not necessarily an integer you can hand to `ps -p`.** Launchers differ:
  one writes a bare number, another writes `PY_PID=<n>`. `ps -p $(cat run.pid)` then dies with
  `error: process ID list syntax error`, which reads as a dead process. Extract the numeric token
  (`grep -oE '[0-9]+'`), and treat a mixed set of pid-file formats in one directory as evidence that
  DIFFERENT launchers produced those runs — not as one run.
- **Reconcile a declared total against the report's own key census.** A summary claiming
  `total: 208` is a claim; prove it by censusing the report's assert keys per viewport prefix
  (3 viewports x 59 + 2 reduced x 14 + 2 touch + 1 global = 208). A total you cannot reproduce from
  the keys is either a different revision or a mixed-provenance set.
- **A vacuous assert sample is not a product failure.** A per-assert `false` whose raw sampled value
  is `null`/absent — the node the probe looked for was already gone at sample time — means the
  probe measured nothing, not that behaviour regressed. Read the raw sample beside every `false`
  before letting a fail count imply a product verdict.
- **When the requester's stated acceptance expectation contradicts the emitted report, the
  divergence IS the finding.** Do not reconcile it silently toward their expectation. Quote the
  report's actual value (e.g. `skipped={}` where they expected the touch keys skipped) and, when the
  probe's own calibration doc describes different behaviour for that version, say the skip path was
  not taken in the version that ran. Adjudicate between the two documents only if explicitly asked;
  otherwise hand back both.
- **A results filename proves nothing about which code wrote it.** Versioned names like
  `<probe>_stdout_v3.txt` are written by whoever last saved the script, and the script may have
  been replaced after the run started. Trust the emitted report's own version and schema keys.
- **The requester may be labelling a mid-flight revision as final.** When a probe's failures match
  the probe's own documented calibration defects, the failures are probe artefacts, not product
  defects. Say so explicitly instead of letting the numbers imply a verdict.
- **Another lane editing its own artefact during your run is normal, not an attack.** Identify the
  writer before escalating. Then stop and request a freeze, or run an immutable copy.
- **Re-run the gate on the post-run revision too.** When a file changed under you, gate status
  belongs to each revision separately; state both.
- **Do not silently re-run to "get a clean number".** A second run against a moved artefact produces
  a second, differently-bound revision and destroys the requester's ability to reason about either.
- **A name-based probe gate is path-blind, so a skip verdict can be scoped to the wrong path.**
  `pgrep -af '<script>.py'` matches on the command line, so a copy of the probe running from a
  scratch snapshot (another relay's, or a second session of your own profile) satisfies "a probe is
  running" while the evidence directory itself is idle. Read the live PID's script path and cwd
  (`ps -o args`, `ls -l /proc/<pid>/cwd /proc/<pid>/fd/1`) before letting the gate decide, and name
  the executing path in your reply: report it as "a probe is running from <path>", never as "a probe
  is running". The match set also inflates the count: `pgrep -f -c` counts the invoking harness's own
  `bash -c` wrapper (whose argument text quotes the pattern) and other lanes' polling wrappers for
  the same script name, so a nonzero count is not evidence that any probe runs. Require the match to
  be an interpreter whose argument is the script file, and quote its writing fd when one exists.
- **Derive a live probe's working directory from its invoking wrapper's own arguments.** When you
  have not read `/proc/<pid>/cwd`, the wrapper that launched the probe carries the answer: a
  `bash -lic ... cd <dir>` prefix with the script invoked by BARE NAME means the wrapper's cwd is the
  probe's output directory, while an invocation by ABSOLUTE path shows only where the script lives,
  not where its outputs land. A bare `ps` argv listing shows the shared script name and hides this
  distinction, so two instances of one script read as one writer. Report per PID: script path,
  invocation form, and the directory its artefacts land in.
- **While a writer is live, the newest artefact can be newer than the report that should cover it.**
  A directory can hold freshly written PNGs whose `proto_*` report is still the previous run's
  revision — the live instance has not yet emitted its report. Compare each artefact's mtime against
  the report's mtime and treat anything newer as uncovered by that report rather than as output of
  the run the report describes. Do not hand a stale report back as if it covered the new renders. The
 mirror case reads as the opposite and is just as wrong: a report hash that stays byte-identical
 across every sample while its siblings drift is a report the live run has not yet overwritten, so
 a stable hash there is the signature of an un-emitted run rather than of a quiet directory. Settle
 it by reading the live run's log size and exit receipt, never by the report's own stability.
 - **A `pgrep ... || echo <none>` line inside the requester's own block is not a quiescence gate.**
 It resolves at the instant it runs and the requester will quote it later as proof that nothing was
 writing. In one audit the same block printed `no-probe-running` and two probes for that directory
 were live less than two minutes afterwards, launched by that lane's own session. Re-scan before
 you report, and give the requester the block's timestamp, your later scan, and the writer PIDs
 with their parents so the negative line cannot be recycled as a premise.
 - **A localhost static server makes every hash check pass while the set is moving.** `python3 -m http.server`
 serves from disk per request with no cache, so served bytes equal on-disk bytes even as the file is
 rewritten between your samples. Report `served` vs `local` hashes as evidence that no cache or
 stale copy is in front of the directory, and never as evidence that the bytes are final. When the
 requester started that listener under a `timeout`, also report the PID pair, elapsed/remaining
 seconds and expiry timestamp: the listener's death is a deadline on their attachment window, and
 under a restart-only-if-down constraint you cannot extend it for them.
- **An mtime-delta gate goes stale the moment a third party rewrites either file.** A condition such
  as "the log is newer than the stdout file by more than 60s" is a claim about two files' relative
  history, and a concurrent lane overwriting one of them flips it with no relation to the run the
  requester cares about. Re-derive the same question from per-file hashes and mtimes (which ids are
  identical, which run emitted each file) before honoring the gate, and report the deltas measured.
- **`cmp` both sides of an archive-then-overwrite before treating it as archive-then-adopt.** If the
  source and the intended archive target are byte-identical, the archive step preserves nothing and
  the adopt step only relabels a file; report the duplicate instead of minting a timestamped copy of
  bytes that already exist.
- **Bind a finished run to its writer from the process, not the mtime.** While the PID is alive,
  `/proc/<pid>/fd/1` names the file it is writing, and the pre-launch receipt (PID, start time,
  input hashes) records the revision. Capture both before the PID exits. Afterwards, matching
  stdouts by size and tail signature is the fallback, and it only proves they came from the same
  code shape, never which revision.
- **A spec or token file rewritten beside a hash-stable probe means the directory is still live.**
  In-flight lanes edit surrounding artefacts after the probe settles, so recommend a freeze (or run
  an immutable copy) even when the launch gate itself passed.
- **Verbatim includes the block's own odd line wrapping.** A variable that expands to several
  values unquoted (`echo "... ($P)"` with `P` holding two PIDs) prints across lines, and the
  requester's contract asks for that block as-is. Relay it untouched — tidying the wrap into one
  line, or re-running with a "cleaner" diagnostic, substitutes your rendering for their evidence.
- **Deliver the requester's reply contract first, extra findings after.** Paste the requested lines
  verbatim in the requested order, then a clearly separated appendix for what the block could not
  show: the live probe's real path, the writer identity, which PID produced which log. Burying a
  skip reason inside the raw block, or padding the requested lines with commentary, makes the relay
  harder to trust than the honest partial result does. Paste a conditional step's gate evaluation
  line verbatim even when the outcome is "did not run": an omitted gate line reads as a step that
  passed, making a withheld write indistinguishable from a silent one. Foregrounding the deviation
  above the raw block is expected when the withheld write would have destroyed or duplicated
  evidence.
- **Keep your own notes out of the evidence directory.** Scratch output belongs in `$TMPDIR`;
  anything you leave beside the run artefacts is indistinguishable from a run output to the next
  lane that lists the directory.
