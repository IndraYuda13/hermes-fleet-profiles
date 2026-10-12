# Run Evidence Provenance & Oracles

Depth for §7 "Bind evidence to a run you did not wait on; audit the oracle before trusting it". Use when you must POST-HOC justify a run whose exit status you did not capture, or when a peer hands you a frozen baseline to diff against.

## 1. Capturing exit status on a detached launch

A detached launch that reparents the child loses the status. Two shapes, one correct:

```sh
# WRONG for status: subshell exits instantly -> python reparents to init/systemd
{ python3 probe.py > run.log 2>&1 & } &      # PID is real, exit status unrecoverable

# RIGHT: the child's status is written to a file you can read later
( python3 probe.py > run.log 2>&1; echo $? > run.exit ) &
echo "PID=$!" > run.pid                       # $! is the subshell; python is its child
```

Why `wait` cannot save the wrong form: `wait <pid>` only works for a PID the *current shell* is the parent of. Once the child is reparented, `wait` returns immediately with "not a child of this shell", and `/proc/<pid>/stat` is gone the moment it is reaped — the `exit_code` field is unreadable even if you poll fast. Polling for a zombie (`STATE == 'Z'`) works only if the parent is still alive and has not reaped; a systemd/init parent reaps immediately, so do not rely on it.

When the requester explicitly asks for "launch detached, return immediately, do not wait", that is a legitimate trade: give the PID and state that the exit status was not observed, or use the writer-side form above so the status lands in `run.exit` for whoever collects it.

### 1b. Foreground inline capture — bind `rc=$?` before any cleanup

A requester may hand you a single *foreground* one-liner and want the raw exit code pasted back. The status assignment must bind to the probe, not to whatever command runs next:

```sh
# RIGHT: rc binds to the probe; the copy happens after
sha256sum probe.py artifact.html > pre_hashes.txt && \
  python3 probe.py > run<N>.log 2>&1; rc=$?; cp -f report.json run<N>_report.json; echo "run<N> exit=$rc"

# WRONG: a probe crash reports 0 (the cp succeeded)
cmd > log 2>&1; cp -f report.json run<N>_report.json; rc=$?; echo "run<N> exit=$rc"
```

Report both status channels when a chain uses them: the echoed `run<N> exit=<rc>` line and any `run<N>.exit` file. If they disagree in *form* — a bare newline-less `1` versus the 13-byte `exit=1` line — the chain changed its status-capture path mid-run; say so rather than quoting one as the truth. An inline `rc=$?` placed after a crash-then-copy reads `0` and is indistinguishable from success, which is exactly why the exit code is the first thing to paste back and why the ordering is the substance of a "paste back the exit line" request.

## 2. Exit status you did not capture

Do not fabricate a number. Rank what you can actually support:

1. `FACT` — the run reached its normal exit path: the declared output artefact and the log were both written, and the log contains no `Traceback`/uncaught-exception text.
2. `INFERENCE` (labelled) — read the script's exit path from source and apply it. A tail line like `return 1 if report["summary"]["failed"] else 0` under `sys.exit(main())` means a non-empty `failed` list implies status 1. Say "inferred 1, not read".
3. `BLOCKED` — neither available; name the concrete reason (reaped before read).

Never present (2) as a measurement. "Exit status: not observable" plus the inference is a correct, complete answer.

## 3. The summary block is wherever the script prints it

A render/measure probe commonly prints its JSON summary *first* and then a per-context detail block per viewport/state. So the log's *head* carries the verdict and its *end* carries only the last context. Read the whole file; report the summary block even when a caller asked only for the end. State the omission plainly rather than letting a caller conclude from silence.

## 4. Validate the oracle before diffing against it

Before running `diff baseline run.log`, confirm the baseline IS the shape you think:

- Does it contain a summary block, or only a `Traceback`? A file named `*_final.txt` that is a bare `TimeoutError` traceback is an aborted run — diffing against it cannot evidence stability, only that the baseline was broken.
- Does the baseline name the same revision as the run? A stdout captured under a different source hash is not a same-revision oracle.

Report `STDOUT_DIFF_EXIT` only alongside this validation; a diff exit code against a void oracle is noise.

## 5. Freeze-directory provenance checks

For each report in a `.frozen/`-style directory you intend to cite:

- **Bracketing order.** `pre_hashes` mtime must precede the report; `post_hashes` must follow. A "pre" snapshot written *after* the report it brackets is anomalous — the bracket is not a bracket.
- **Same-revision binding.** The pre-hash must equal the frozen/certified hash. If pre and post name different revisions, the report straddles a change and cannot be assumed bound to the revision under test.
- **Distinct runs.** A launch receipt naming a different PID/time is a different run — do not fold its report into this one's baseline set.

Only after clearing all three may a frozen report be quoted as a same-revision baseline.

## 6. Stability = agreement across runs

Reproducibility is a cross-run property. Enumerate every available summary for the artefact family and tabulate `failed`/`total`/`passed`/`skipped`:

```
run A  failed=[]                      208/208
run B  failed=['1280x800:toast_exit_midflight']            207/208
run C  failed=['1280x800:...','412x915:toast_exit_midflight'] 206/208
```

Disagreement means nondeterminism, not a stable artifact. Name the timing-sensitive assertions (mid-flight motion samples) as the likely cause, and require a determinism fix on the sampling before any stability claim. A clean single run does not establish stability; a disagreeing set refutes it.

## 7. Producer vs verifier split

If you hashed the revision, launched the run, and then report its result, you are the producer — your output is a self-check artefact, not independent evidence. Label it as such and state that admission to any gate needs a fresh run identity (`claim_run_id == evidence_run_id`) validated from outside your context by a certifier who did not execute the run. Never certify your own run as evidence for a gate you also touched.

## 8. Repeat runs collide on the probe's fixed output path

When the requester wants the same probe run twice (a repeatability check) because the defect under investigation was nondeterminism, note that the probe writes one fixed filename — typically `proto_render_report.json`. The second run silently overwrites the first run's per-context detail, destroying the exact evidence you were about to compare.

Order of operations:

1. Run N finishes. `cp -p proto_render_report.json run<N>_report.json` and record its sha256.
2. Only then launch run N+1.
3. Tell the requester which file holds which run, since the fixed path now names the newer run only.

Snapshot first, launch second. A green run whose report you let be clobbered is a wasted run, and it is the run whose margin numbers the comparison needs.

**A crash collapses the two into one stale artefact.** If run N aborts before writing the fixed-path report (a `KeyError`/`Traceback` inside the probe, exit 1), the `cp -f report.json run<N>_report.json` you run anyway copies the **previous** run's report under the new name. The result is a run-scoped file that exists, parses as valid JSON, and belongs to a different run — the crash is invisible until someone diffs it:

```sh
sha256sum run13_report.json run14_report.json   # equal? -> run14 carried run13 forward
```

Make the freshness check part of collection, not an afterthought: hash every run-scoped report, and treat **hash equality between a non-zero-exit run and its predecessor** as proof the later file is carry-forward. Quote the pairing (`run13 == run14`, `90c9d3...`) in the receipt so the requester can see which report is genuinely fresh. A report you did not watch get written is not evidence, even when its filename is the one that was requested.

**Check for an already-running duplicate before you launch one.** When asked to launch a repeat chain that writes fixed filenames, the first action is `ps` for the exact command, not the launch — the chain may already be in flight (the requester fired it, then asked you in a separate message). A second launch races the same `run<N>.*` paths and interleaves two sequences into one evidence set. Detect, attribute, and report the existing instance rather than duplicating it:

```sh
ps -eo pid,ppid,lstart,etimes,stat,args | grep -F '<script path>' | grep -v grep
# whose chain is it? read the process environment (do NOT print secrets)
tr '\0' '\n' < /proc/<pid>/environ | grep -E 'HERMES_HOME|HERMES_SESSION|AI_AGENT'
```

If a matching live chain exists, do not launch: report its PID, the artifacts and exit files it has already produced, and its pre-hashes. Treat the already-planned runs as the sample and only launch when no live instance owns the output paths.

If the live writer is *not* your duplicate chain but a different worker writing the same fixed paths (a second profile's run, a subdir invocation), do not simply abort: re-execute the payload in an isolated copy of the dir — §11.

## 9. Prefer the margin over the boolean

A repeatability claim built on `passed: true` twice is two observations of agreement, not proof of determinism — two passes cannot falsify a low-rate race. Ask the harness for the per-context sample counts and report the distribution:

```
exitFrames : 12, 12, 12, 12, 12   (guard: >= 2)
presentFrames: 168, 166, 163, 166, 168
```

A stable margin against the guard is the property worth quoting. Say "two observations of agreement" and name the margin; do not upgrade it to a determinism guarantee.

## 10. Deterministic failure vs load flake — split by set algebra, then measure the host floor

A `failed` list tabulated across repeats carries two different kinds of fact. Split it:

- **Intersection** (fails in EVERY repeat at the same assertions) = a deterministic property. A probe-logic mis-calibration reproduces byte-identically regardless of host load; that is the tell that the defect is in the probe, not the artifact or the environment.
- **Symmetric difference** (fails in some runs only) = a timing/load flake in that context. Name the context and the load at that moment.

So `[A,B]` in all three runs plus `[C]` in one run of three is "A and B are deterministic, C is a flake" — two owners, two fixes. Collapsing it to one headline `failed` count sends one owner after the other's bug.

**A "clean timing sample" needs the ambient load as evidence, not as an assumption.** Sample `/proc/loadavg` and the run-queue every ~2 s across the whole window (`scripts/host_load_sampler.py`, launched as a tracked background process) and report min/mean/max `load1` and the run-queue range against `nproc`. Two consequences you must state plainly:

- If `load1` stays above `nproc` for the entire window even with no probe of yours running, the elevated number is the host's ambient floor, not self-inflicted load — and there is no clean window to retreat to. Do not offer a quiet rerun that cannot happen on this host at this time; offer more repeats with an explicit tolerance band instead.
- Attribute each load-sensitive assertion failure to the load measured at that moment before calling it nondeterminism. A lone window assertion failing at `load5 ≈ 7` and passing at rest is a load artifact, not an artifact defect — say which and cite the load.

Guard the sampler's own scope: it can only cover the window it was started for. If it starts after the first run finished, say that the early-run load figures are point-reads, not a continuous trace, rather than presenting them as measured.

## 11. Re-executing a peer's payload out of a contended output dir

A peer asks you to run their probe "one command, then paste the summary" into a shared evidence dir. That request is for reproducible evidence, not obedience to a path. Before launching, check whether the dir is contended:

```sh
ps -eo pid,ppid,lstart,etimes,args | grep -F '<script basename>' | grep -v grep
for p in <pid> ...; do readlink /proc/$p/cwd; readlink /proc/$p/fd/1; done  # who writes what, where
```

Two independent writers can exist at once — one writing the shared default report path, another invoked from a subdir. A probe that writes fixed filenames (`proto_render_report.json`, 60+ PNGs) means a run launched into that dir can neither bind its own report nor prove non-interference; run N+1 silently overwrites run N, and the shared report you collect may be another worker's.

**Isolated re-execution — the faithful reading of "run my payload":**

```sh
SRC=/path/to/shared/dir
DIR=$SRC/iso_$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$DIR"; cp -p "$SRC/probe.py" "$SRC/artifact.html" "$DIR/"; cd "$DIR"
{ sha256sum probe.py artifact.html; } | tee pre_hashes.txt
( /path/to/python3 probe.py > stdout.txt 2>&1; echo $? > run.exit ) &   # status captured (see §1)
```

Conditions — check them, do not assume:

- **The payload must resolve its own paths.** Confirm it derives them from its location (`HERE = os.path.dirname(os.path.abspath(__file__))`) or is path-parameterised (env/argv). A script with relative in-file paths copied elsewhere reads the wrong artifact and the run is void.
- **Changing only the executable pin does not invalidate the run.** Substituting the interpreter for one that imports the binding is the sanctioned §7 override; it must not change the payload logic.
- **Copy, never edit.** If the run needs a scoped change you cannot make without touching a file, stop and ask.
- **State the substitution and offer the literal command** in case the requester's verification genuinely depends on the named path. Say it was for evidence isolation, not to avoid the requested work.
- **Freeze the fresh report** (`cp -p report.json .frozen/<producer>__<revisionhash>__report.json`), record its sha256, and keep a pre/post hash pair in the isolated dir (proves no mutation).

**Do not adopt another worker's report as yours.** A second worker may have already produced a byte-identical summary for the same revision. Cite it only as corroboration with its provenance (`probe_version`, both hashes, the explicit all-asserts-`False` list), and say your number came from your own isolated run — an artefact you did not launch is context, not your evidence.

### 11b. The clobber can land AFTER your run returned — detect the live handle, not just a running name

A contended dir does not become safe when your process exits. A second worker launched *after* your run finished can reopen the requested filename with `>` and truncate it to 0 bytes, destroying evidence you already read and were about to cite. A file that was N KB when you collected it and is 0 bytes when you quote it is not corruption — it is a live writer. So the duplicate check must run twice: before you launch (§8) AND before you report.

Detect the writer by its open descriptor, which a `ps | grep <script>` sweep misses whenever the probe is wrapped in a launcher shell:

```sh
lsof <file>                 # FD 1w / 2w opened on the file == its own stdout/stderr, i.e. the process opened it with '>'
fuser -v <file>
ps -eo pid,etime,args | grep -F '<script basename>' | grep -v grep   # then read the *launcher's* argv
```

A `1w` handle on the file is direct proof that process truncates it, not merely that a same-named script is alive. Attribute: a **different** invocation is identifiable from its launcher argv writing different run-scoped side files (a variant pre-hash name, its own PRE/POST report-hash logic) even though it runs the identical probe — that is a peer's worker, not your duplicate. Practical consequences: (1) `cp` the authoritative artifacts to a producer-namespaced name the moment the run finishes, *before* inspecting them; (2) at report time re-confirm the bytes you are about to quote still exist and hash as recorded (hash the run-scoped copy, not the shared path); (3) recommend per-run output dirs to whoever owns the dir.

## 12. A declaration of coverage is not coverage — replay its own data against the changelog

A completion summary that announces "structurally-unsatisfiable assert X fixed" or "assert pack extended to N" is a claim about the *surface*, not the *substance*. Trust it only after mapping the changelog entries onto the report:

- **Sort the changelog into kinds.** A "fixed" assert must be shown to pass; an "extended" pack must actually contain the new keys; a "superseded" or deliberately-unasserted key is allowed to remain `False` provided nothing consumes it. Report which keys are asserted-vs-informational for this run — an assert count rising (245 vs 242) says nothing about which keys they are.
- **Check whether a claim is self-refuting.** A changelog entry stating an assertion "is un-passable by construction", supplied by the same author who then reports it green, contradicts itself; prefer the run evidence over the prose and say which one you followed.
- **Name any key that is quoted but consumed by no assert.** Good output still counts as self-refuting if the claim depends on a key that no assertion reads.

## 13. Read-only integrity + writer attribution in a shared evidence dir

Use when a peer asks a read-only question: "has my certified artifact moved?", "who is still writing in `<dir>`?", "is my spec still the authoritative copy or has someone forked it?", "give me the path and hash of the cert doc, or point me at it". No runs, no writes — reads and the report only.

### 13.1 Certified artifact unmoved — hash equality, not mtime

An unchanged mtime is corroboration, not proof; a preserved-but-rewritten file can keep it. Hash live and every pinned copy together and read the identity tuple:

```sh
sha256sum prototype.html
cmp -s prototype.html .frozen/prototype__<hash>.html && echo IDENTICAL-frozen
cmp -s prototype.html cert_dir/prototype.html            && echo IDENTICAL-certcopy
stat -c '%n inode=%i birth=%w mtime=%y ctime=%z size=%s' prototype.html
```

Live == frozen == cert-dir copy, with the same inode/birth, is the proof. Report the hash plus the `mtime/ctime/inode/birth` tuple so the requester can bind their claim to a revision. Note whether the file even appears in the dir's recent-by-mtime listing — an untouched artifact is absent from a top-25 `ls -lat` while the hot files lead it.

### 13.2 Writer attribution — no open handle is not "no writer"

`lsof +D <dir>` / `fuser <file>` returning no holder (rc=1) means nothing holds a descriptor *now*; a writer that already finished leaves none. Do not report "nobody is writing" from that alone. Enumerate by working dir and argv rather than by process name — a tool server or viewer naming the dir nowhere in its command line is still bound to it:

```sh
for p in /proc/[0-9]*; do
  cwd=$(readlink "$p/cwd" 2>/dev/null); cmd=$(tr '\0' ' ' < "$p/cmdline" 2>/dev/null)
  case "$cwd$cmd" in *<dir>*) echo "PID=${p#/proc/} cwd=$cwd | $cmd";; esac
done
```

Then attribute by the **session-scoped tool-call log**, which carries both the writer's session id and the completion second:

```sh
grep -nE 'tool (write_file|patch) completed' profiles/<name>/logs/agent.log | tail
# -> 2026-10-12 06:34:05 INFO [<session-id>] agent.tool_executor: tool write_file completed (0.63s, 310 chars)
```

Match that second to the target file's mtime. The session id is the writer's identity; a profile that "was active" is not, and naming a profile without the log line is a guess. Where several profiles are candidates, grep each profile's `agent.log` for the filename as a cross-check.

Characterise the peers you clear, don't just exclude them. A peer whose own `a2a_audit.jsonl` entries show only `sha256sum`/`stat`/`find`/`ps` is *reading* — say so explicitly rather than leaving them as uncleared suspects. Report each peer's live work dir (a playwright/pnpm run elsewhere is activity, not a write into this dir).

### 13.3 Self-modification reads as external modification

A write-guard warning inside the requester's own toolchain ("file X has been modified externally") is frequently the requester's **own worker session** having patched that file in the same turn window. Resolve by session id: if the tool-log session belongs to the requester, say plainly "the file the requester warns about was written by the requester's own session at HH:MM:SS, and no peer touched it". Do not let a false peer-fork narrative stand because the warning sounded external.

### 13.4 A copy is not a fork; a stale snapshot is not an authority

To answer "is my spec still authoritative or has someone forked it", enumerate every copy on disk with size and mtime:

```sh
find / -name '<file>' -not -path '*/browser-profile/*' -printf '%TY-%Tm-%Td %TH:%TM:%TS %10s %p\n' 2>/dev/null
```

One live file plus one **smaller, older** snapshot (a kanban attachment written at an earlier revision) is a snapshot, not a fork. A fork is two live files, both newer than the last handoff. Compare sizes and mtimes, name the stale one as a snapshot, and state which file is authoritative.

### 13.5 "Point me at the file" with no such file — answer with proof of absence

When the requested document does not exist, the deliverable is the **search output that establishes it**, never a description of a file you were asked to point at. Sweep every naming shape and report the negative:

```sh
find <root> -iname '*cert*'                      # any name, any ext
find <root> -iname '*cert*.md'                   # the specific shape asked for
find <root> -name '.*cert*'                      # hidden
find <root> -maxdepth 3 -type f -name '*.md' | while read f; do
  case "$(head -1 "$f")" in *[Cc][Ee][Rr][Tt]*) echo "TITLE: $f";; esac; done
grep -rli 'certification\|certificate' <root>    # content, not just names
```

State "no such file on disk" flatly, and then name the real artifact being mistaken for it: a `*_cert_<HHMMSS>/` directory holding only a pre/post hash pair, a stdout, a report and PNGs is a **hash-pinned copy of a run set**, not a certification document — quote what it actually contains (the two hash lines and their pre==post equality) so the requester sees why it is not the thing they asked for. If the claim came from a mangled transcript, say the claim is **not substantiated by any artifact on disk** and give the nearest unrelated matches with their dates rather than adopting the claim.
