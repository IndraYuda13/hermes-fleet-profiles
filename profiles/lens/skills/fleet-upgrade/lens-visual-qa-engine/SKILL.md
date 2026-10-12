---
name: lens-visual-qa-engine
description: Use when auditing web UI visual quality, layout, or art.
version: 1.0.0
author: Fleet Architecture & Orion Lead
license: MIT
metadata:
  hermes:
    tags: [ui, visual-qa, lens, automated-testing, fail-fast, metrology, design-contract, fuzzing, mutation-testing]
    category: fleet-upgrade
---

# LENS Visual QA Engine — Strict 5-Gate Fail-Fast Standard

Deterministic, multi-stage visual verification standard for LENS and the fleet. Replaces fragile static screenshot reviews with a strict fail-fast pipeline, runtime design schema assertions, active interaction fuzzing, and mutation-tested calibration.

## When to Use
- Auditing web UI, dashboards, landing pages, mobile interfaces, or design system components.
- Verification Gate on any UI/UX task prior to owner review.
- Regression testing on visual layout, responsiveness, and art direction fidelity.

---

## Core Philosophy: Determinism Over Probabilism
1. **Never use a stochastic tool (VLM) for a deterministic job (geometry, contrast, runtime health).**
2. **Fail-Fast:** Gate N+1 is forbidden from executing if Gate N fails. Zero token waste on broken builds.
3. **Who Watches the Watcher:** LENS must prove its own audit harness is calibrated via Synthetic Mutation Testing before issuing a production verdict.
4. **Design Intent is Explicit:** Contracts are expressed as runtime schemas (`data-ui-*`), eliminating guesswork.

---

## The 5-Gate Fail-Fast Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│ Gate 0: Runtime Health & Network Telemetry (< 50ms)                   │
│ ├─ 0 console.error / uncaught exceptions                              │
│ ├─ 0 HTTP 4xx/5xx on static assets (fonts, SVGs, images, chunks)      │
│ ├─ document.fonts.ready === true & network idle                       │
│ └─ DOM MutationObserver stabilized for >= 200ms                       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (PASS)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Gate 1: DOM & Semantic Integrity (< 100ms)                            │
│ ├─ Context-Aware Banned Token Scanner (excludes <code>/<pre>)         │
│ ├─ Broken Asset Guard (img.naturalWidth > 0, svg has rendered paths)  │
│ ├─ Accessibility Tree Integrity (CDP AXTree: 0 unlabelled controls)   │
│ └─ Zero Viewport Leak (document.documentElement.scrollWidth <= innerW) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (PASS)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Gate 2: Deterministic Metrology & Token Contract (< 200ms)            │
│ ├─ Computed WCAG APCA / 2.1 Contrast Calculation on rendered pixels   │
│ ├─ Runtime Schema Validation (`data-ui-*` vs getComputedStyle)        │
│ ├─ Silent Text Clipping Detector (scrollWidth > clientWidth)           │
│ └─ Minimum Interactive Touch Target (>= 44x44px mobile / 36x36px desk)│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (PASS)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Gate 3: Active Interaction & Viewport Fuzzing (< 2s)                  │
│ ├─ Dynamic Viewport Scrubbing: 320px -> 1920px in 25px steps          │
│ ├─ Extreme Content Fuzzing (200-char string, RTL Arabic, emoji, zero) │
│ ├─ Interactive State Machine Walk (hover, focus-visible, active, open)│
│ └─ Cumulative Layout Shift (CLS < 0.05 via PerformanceObserver)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (PASS)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Gate 4: VLM Macro Aesthetic & Art Direction (Final Tier)              │
│ ├─ Whole-viewport + detail evidence: hierarchy, rhythm, identity       │
│ ├─ Product specificity + default-cluster/effect-off probes             │
│ ├─ Desktop/mobile thesis preservation                                  │
│ └─ Anti-Generic-AI Slop Rating (LOW / MEDIUM / HIGH)                  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Gate 0: Runtime Health & Network Telemetry
Executed via Playwright / CDP event listeners.
- **Console Gate:** Attach `page.on('console', msg => { if (msg.type() === 'error') record(); })` and `page.on('pageerror', err => record())`. Count must equal `0`.
- **Network Gate:** Intercept `Network.responseReceived`. Any asset (CSS, JS, SVG, WOFF2, PNG/WebP) with status `>= 400` fails Gate 0.
- **Font & Lifecycle Barrier:**
  ```javascript
  await page.waitForLoadState('networkidle');
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => {
    return new Promise(resolve => {
      let timeout;
      const observer = new MutationObserver(() => {
        clearTimeout(timeout);
        timeout = setTimeout(() => { observer.disconnect(); resolve(true); }, 200);
      });
      observer.observe(document.body, { childList: true, subtree: true, attributes: true });
      timeout = setTimeout(() => { observer.disconnect(); resolve(true); }, 200);
    });
  });
  ```

---

## 2. Gate 1: DOM & Semantic Integrity
- **Context-Aware Forbidden Token Scanner:**
  Scans all visible text nodes EXCEPT those inside `<code>`, `<pre>`, `<samp>`, `[data-allow-raw-tokens]`, or developer doc containers.
  Regex: `/\b(undefined|NaN|\[object Object\]|null|Error:|NaNpx|\{\{.*\}\})\b/i`.
- **SVG & Asset Guard:**
  - Every `<img>`: `naturalWidth > 0 && naturalHeight > 0`.
  - Every `<svg>` / icon container: `getBoundingClientRect().width > 0 && height > 0` AND must contain at least 1 visible renderable child (`path`, `circle`, `rect`, `polygon`) with non-empty attributes.
  - Zero tofu characters (`\uFFFD`).
- **CDP Accessibility (AXTree) Proxy:**
  Fetch `Accessibility.getFullAXTree`. Assert 0 interactive elements (buttons, inputs, links) with empty accessible names.

---

## 3. Gate 2: Deterministic Metrology & Token Contract
- **Design Contract as Runtime Schema (`data-ui-*`):**
  FRAME embeds attributes; LENS validates via `getComputedStyle()`:
  - `data-ui-surface="elevated"` -> assert computed background matches `--surface-elevated` token.
  - `data-ui-min-touch="44"` -> assert `rect.height >= 44 && rect.width >= 44`.
  - `data-ui-overflow="contain"` -> assert `scrollWidth <= clientWidth && scrollHeight <= clientHeight`.
- **Contrast Ratio Metrology:**
  Calculate relative luminance $L = 0.2126R + 0.7152G + 0.0722B$ on computed colors. Assert contrast ratio $\ge 4.5:1$ for normal text, $\ge 3.0:1$ for large text/icons (WCAG AA).
- **Silent Clipping Detection:**
  Scan all containers: if `el.scrollWidth > el.clientWidth` and `getComputedStyle(el).overflowX === 'hidden'` and `textOverflow !== 'ellipsis'`, flag as `DEFECT_SILENT_CLIPPING`.

---

## 4. Gate 3: Active Interaction & Viewport Fuzzing
- **Dynamic Viewport Scrubbing:**
  Loop viewport width from 320px to 1920px in 25px increments. On each step, assert:
  `document.documentElement.scrollWidth <= window.innerWidth` (0 horizontal overflow leaks).
- **Extreme Boundary Content Fuzzing:**
  Temporarily inject into data-binding containers:
  - String 200 chars without spaces (`"WWWWWWWW..."`) -> assert container wraps or truncates with ellipsis.
  - Unicode RTL (`"مرحبا بالعالم"`) & complex emoji (`"👨‍👩‍👧‍👦"`) -> assert no alignment crash.
  - Number `0`, `999999999999`, and negative values -> assert layout stability.
- **Interactive State Walk:**
  Simulate tab traversal through all focusable elements. Assert `:focus-visible` outline is present and element is within visible viewport bounds (not hidden under sticky headers).

---

## 5. Gate 4: VLM Macro Aesthetic & Art Direction
Use VLM for final macro/art-direction certification only after Gates 0 through 3 pass. Submit rendered screenshots to adversarial vision even during an incomplete audit when required by the review contract, but label this diagnostic falsification, not Gate 4 PASS; pixel review cannot substitute for missing deterministic checks.
- **Evidence set:** provide native-resolution whole-viewport captures for macro judgment **plus** 1:1 sector crops for typography/material/detail. Sector crops alone cannot prove page composition. For responsive work, compare at least one desktop and one mobile capture side-by-side.
- Prompt evaluates these observable questions:
  1. **Product Mechanism & Specificity:** What real product behavior/content/proof visibly generates the composition? Could the shell plausibly belong to many unrelated products unchanged?
  2. **Composition & Rhythm:** Is focal order obvious in a squint/grayscale view? Do topology, repetition, negative space and density follow content priority rather than component-library defaults?
  3. **Typography System:** Are role contrasts, measure, wrapping, data/numeric treatment and font character coherent? Penalize fashionable pairings used as identity without product rationale.
  4. **Color / Material / Effect Budget:** Which regions own color and material? Are glow/blur/gradient/glass/particles bounded and purposeful? Apply the effect-off probe: if removing decoration collapses hierarchy/identity, block high scores.
  5. **Assets & Proof:** Do dominant visual regions carry authentic or declared synthetic proof, or is decorative chrome filling missing content?
  6. **Motion / Interaction Meaning:** When motion evidence exists, does it demonstrate transformation, state, causality or continuity? Stable states must not pulse merely to look alive.
  7. **Responsive Re-authorship:** Does mobile preserve the visual thesis through intentional reorder/reframe/crop/disclosure/interaction changes instead of a mechanical vertical stack?
  8. **Signature Device Fidelity:** Verify the 1-2 functional/memorable devices defined in `DESIGN_DNA.md`; novelty alone earns no score.
- **Default-cluster ledger:** name the dominant shell, type treatment, palette/material treatment, repeated-container pattern and motion pattern. If `>=3` are recognizable category/model defaults without independent product/brief rationale, set `GENERIC RISK: HIGH` regardless of polish.
- **Verdict:** `GENERIC RISK: HIGH` is an automatic visual BLOCK for Depth 2/3. Remediation must change the structural/content cause; token-only recoloring, font swaps, radius edits or weaker glow do not clear the finding.

---

## 6. Self-Validation Loop: Synthetic Mutation Testing
Before LENS audits a production build, the harness runs a calibration test in an isolated DOM sandbox:
1. Inject Mutant A: Insert `undefined` text into a heading.
2. Inject Mutant B: Set `margin-left: -100px` on a primary button.
3. Inject Mutant C: Set text color equal to background color (contrast 1:1).
4. Inject Mutant D: Set `overflow: hidden; height: 10px` on a multiline paragraph.
5. Inject Mutant E: Replace an icon SVG with an empty `<svg></svg>`.

**Invariant:** $\text{Mutation Score} = \frac{\text{Mutants Detected}}{\text{Total Mutants}} = 100\%$.
If Mutation Score $< 100\%$, LENS harness is declared **DEFECTIVE / UNCALIBRATED** and cannot issue a production verdict.

---

## 7. Harness Bootstrap & Sampling Discipline
Rules that apply to EVERY run, before any gate verdict is issued.

**Bootstrap — resolve, do not assume:**
- Resolve Playwright from the candidate project's dependency graph first: use `createRequire(<absolute candidate package.json>)`, then try `require('@playwright/test').chromium` or `require('playwright').chromium`. A pnpm project can expose the test package without exposing `playwright` at its root; do not install another copy merely because the latter lookup fails. Discover an existing browser executable or use the configured browser cache, never hardcode a version. If an existing browser session cannot start, launch an isolated context through the resolved package without killing an unknown profile owner.
- `export PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright` before `chromium.launch()`, or the browser executable is not found.
- If you reach for the Python binding, verify the import resolves on the active interpreter first; do not assume it mirrors the Node install. `python3` on PATH frequently has no `playwright` at all — probe the real interpreters (`for p in /root/.hermes/installs/*/environments/*/venv/bin/python /opt/venvs/*/bin/python; do "$p" -c 'import playwright' 2>/dev/null && echo "$p"; done`) and use the one that imports, with `PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright` exported. Resolve to an existing install; do not pip-install a second copy just to make one run work.

**Time-sampled, never single-instant:**
- Never assert a time-varying quantity from one reading taken after a fixed delay. Sample on an interval across the whole burst window (every ~50 ms from trigger to +900 ms) and report the **peak plus the time series**. A single reading taken after the burst finishes reports `0` and proves nothing about whether motion was excessive or bounded.
- Apply this to `document.getAnimations()` running-counts, layout-shift, CLS accumulation, and any "does it pulse/flicker/loop" claim.
- **Count the unit the contract counts.** A ceiling on concurrent *elements* is not the same number as a count of *animations* (an element with two animations counts once in the first, twice in the second). For elements: `new Set(document.getAnimations().filter(a => a.playState !== 'finished' && a.playState !== 'idle').map(a => a.effect.target)).size`. Naming the wrong unit turns a real breach into a pass, or the reverse. Note `getAnimations()` omits shadow roots, so scope the claim to the light DOM when components are present.
- **Cross-check the artifact's own readout.** When the page self-measures (a debug/status line), read its counting function from source and replicate its exact predicate — including whether delay-phase (`fill: both`) entries count — then report your number, its number, and a match flag. Agreement corroborates the readout; disagreement is a finding about the readout itself. Also verify self-reported *labels* against the underlying value: a readout printing `transform aktif` only tests `transform !== 'none'`, and the value can still be the identity matrix (no net displacement). And check the readout at the moment you quote it: a self-measuring string often switches format as state settles (an immediate short form replaced by a measured long form once the burst ends), so the same readout reads differently at 300 ms and at 1300 ms — know which form your moment lands in before repeating a string as the measurement.

**Bind evidence to a revision:**
- Hash the source under test at run start and stamp the hash plus byte size and mtime into the run manifest and report. After a fix, re-hash: a changed hash means the prior manifest is obsolete — say so, and overwrite the same output names so no stale capture survives under a filename the reviewer will reuse.
- **Hash every code artifact you execute at BOTH run start and run end; a `pre != post` hash is a mid-run mutation, not a stale fixture.** A probe/spec file can be rewritten by a concurrent writer while your run is in flight. Interpreters read the file at process start, so your run executed the **pre** bytes even though the on-disk file has since changed — the run is bound to the pre hash and must be reported as such; do not certify the post revision from it, and if the post revision is the intended fix, say it needs its own run. A stable artifact (`prototype.html`) hash across both checks while the harness/probe hash moves is the tell that the mutation is in the harness, not the artifact. Report the divergence explicitly — a session where the probe moved mid-run is itself a provenance event the owner needs.
- **Check that a delivered artifact is not older than the fix it claims to show.** When handed a shot set as "the final render", compare the PNG mtimes against the source file's mtime *before* inspecting any pixel: an artifact directory timestamped earlier than the source it names predates the fix and cannot evidence it — re-run the render, then re-verify against the fresh hash. A filename encoding a revision (`rev6/`, `-final`, `-v2`) keeps the *label* while the bytes stay stale; the revision label is not proof of freshness, only the hash-plus-mtime pair is. Re-run mutates the shots, so confirm the output hash actually changed before reporting the new pixels.
- **A revision change with byte-identical outputs is a question, not an answer.** Never assume staleness (a cached write) and never assume freshness. Locate the changed content relative to your capture regions: if it sits outside every region you captured — a status line outside the cropped element — or inside a state your capture timing misses, identical bytes are the *correct* result. Confirm with one re-capture plus byte-compare, then state which region would have changed had the fix been in frame. Reporting identical hashes as freshly re-rendered conceals a deliverable that does not carry the change; calling them stale when the chain explains them sends the owner after a phantom.

**Attribute before you accuse:**
- When a computed value contradicts a declared token/contract, do not file it as a defect until the cause is identified. Read the cascade with CDP `CSS.getMatchedStylesForNode`, then falsify by mutating the DOM **in memory only** (e.g. re-parent the element out of the suspected ancestor) and re-reading the computed value. Report cause + reproducing evidence, not just the mismatch number.

**Isolate each size mode — a toggle persists:**
- Measure every size/responsive mode from a fresh page load or browser context. A mode control (a `#boardsize`-style toggle) stays flipped for the rest of the session, so a sequential loop that measures mode A then mode B silently reports mode A's numbers under mode B's label. Fresh context per mode is the cheapest correct fix; re-read the mode flag inside the *same* `evaluate()` that reads the geometry so label and numbers come from one state, and never carry a label forward from a variable you set in a previous step.

**Verify a fix by the artifact, not by the description:**
- A fix report describes intent; confirm the rendered result. For a deleted element, assert absence on the painted surface (`querySelectorAll` count is 0, and the rendered `innerText` no longer contains the copy) and confirm the *replacement* mechanism's computed properties actually hold. Then grep the CSS for rules still targeting the removed selector: a surviving rule is dead code, and it belongs in the report as a low-severity cleanup finding rather than silently passing. When the geometry counter that flagged the defect drops to 0 in every state and mode, say so explicitly — that is the resolution evidence, not the absence of a new finding.

**Run a delegated script verbatim; report its raw verdict as its own axis:**
- When a peer asks you to run a render/measure script unchanged, run the file exactly as written — resolve the interpreter that imports its binding (bootstrap above) and override only the executable pin if it needs one, never the logic. Tee raw stdout/stderr to a file and report the **full stdout and the exit code**, plus whether the declared output artifact exists, with its byte size and hash. A non-zero exit is part of the result, not a footnote.
- Keep three axes separate: (a) **render health** — outputs written, `console_errors`/`page_errors` empty; (b) **the script's own assertions** — quote the failing rows and the selectors they probed; (c) **your independent pixel reading**. A script reporting `all_pass:false` because two moments lacked the selector it greps is a copy/selector finding, not a render crash — say which it is, and never let (b) substitute for actually performing (c).
- **When the requested shape forces you into a contended output dir, re-execute the SAME payload in an isolated copy and say why.** A peer who asks you to run their probe "one command, paste the summary" is asking for *reproducible* evidence, not obedience to a path: if that dir has a concurrent writer, a run there can neither bind its own report nor prove non-interference. Re-executing the identical payload in a frozen copy is the faithful reading of the intent, not a deviation. Do it only when the payload resolves its paths from its own location (`os.path.dirname(os.path.abspath(__file__))`-style) or is path-parameterised — read the source to confirm; otherwise a copy reads the wrong artifact and the run is void. State the substitution explicitly, and offer the literal command if the requester's verification actually depends on that path. Recipes: `references/run-evidence-provenance.md` §11.
- **Run a peer's payload verbatim, but do not rewrite its assertions to make them pass.** Quote an assertion's *purpose* verbatim; never quote its source *text*. When you restate an inherited predicate, name the one substantive way it differs and justify it — otherwise the next reader takes your paraphrase as their code and cannot tell whether the check was weakened.

**Bind evidence to a run you did not wait on; audit the oracle before trusting it:**
- **A detached launch has no waitable handle.** Piping a command into a subshell and backgrounding it (`{ cmd > run.log 2>&1 & } &`) reparents the child to init/systemd the instant the subshell exits, so the PID you report is real but its exit status is unrecoverable — `/proc/<pid>` is reaped before you can read the `exit_code` field, and `wait` fails because it is not your child. Launch so the status is *recorded*: `( cmd > run.log 2>&1; echo $? > run.exit ) &`, or use the terminal tool's tracked-background form with completion notification, and report `run.exit` as the exit status. A bare PID is acceptable only when the requester explicitly asked for launch-and-return.
- **If you never captured the status, do not invent one.** Say it is unobservable. If the script's exit path is readable (`return 1 if report["summary"]["failed"] else 0` under `sys.exit(...)`), you may give the inferred status, labelled `INFERENCE`, alongside the `FACT` that the run reached completion (log + report written, no `Traceback`) — never present the inference as a measurement.
- **Capture `$?` immediately after the command that produced it — never after a `cp` or other cleanup.** In a one-liner `cmd > log 2>&1; rc=$?; cp -f out.json run<N>.json; echo "run<N> exit=$rc"`, the `rc=$?` must sit directly on the probe, *before* the copy: put the `cp` first and a crash reports the copy's `0` and reads as a clean run. Report the echoed `exit=` line **and** any raw status file side by side — when the two disagree in *form* (a bare newline-less `1` in `run<N>.exit` versus a 13-byte `run<N> exit=1` line) that divergence is itself the tell that a chain changed its status-capture path mid-run, so quote both rather than one as the truth. Recipes: `references/run-evidence-provenance.md` §1b.
- **Never read only the end of a script's log and call it the result.** The summary block can sit at the *head* (`{"failed": [...], "total": N, "passed": N}`) while the log's end holds only the last context's detail lines. Read the whole log and report the summary block regardless of which slice was requested, saying plainly when the requested slice omits it.
- **Validate the oracle before you diff against it.** A file named `..._final.txt` handed to you as the stability baseline may itself be an aborted run — a bare `TimeoutError` traceback. A `diff` against it proves nothing about the revision. Check the baseline's shape first (does it contain the summary block? does it contain `Traceback`?) and state outright that the comparison is void if it does not.
- **Audit the freeze directory's provenance before citing any of its numbers.** Bracketing snapshots must bound the run they claim to: a `pre_hashes` file written *after* the report it is meant to bracket, or whose hash differs from the certified revision, means that report is not bound to the revision under test. Check mtime ordering and that pre/post hashes name the same revision before quoting a report as a same-revision baseline.
- **Run-to-run agreement is the claim; a single diff is not.** Compare the summary blocks (`failed`/`total`/`passed`/`skipped`) across every available run for the artifact before asserting stability. Three runs disagreeing (0 vs 1 vs 2 failures) is nondeterminism in the probe, not a stable property — the honest verdict is that the stability claim fails, and you name the timing-sensitive assertions as the cause.
- **A boolean that passes twice is weaker evidence than an observable margin.** When an assertion samples a *window* (a transition, a burst), require the report to carry the sample counts per context (`exitFrames`, `presentFrames`, `logFrames`) and quote the distribution against the guard — `12,12,12,12,12` against a `>=2` guard — rather than `passed: true`. Two green booleans cannot falsify a low-rate race; a stable margin is the property you can actually claim. Ask for the margin when the harness does not already emit it, and keep the word "agreement" rather than "proof of determinism" when that is all you have.
- **A context that reports `null` for a probed field may have no assertion for that field at all.** Diff the per-context assert keys, not just the aggregate. When the reduced-motion contexts return `toastExit=null` and no `reduced_*:toast_exit_*` key exists in the pack, a green `226/226` does not cover that invariant there — say so, and distinguish it from a legitimately collapsed window (reduced motion neutralises transitions to `1e-06s`, so there is no interior to sample). An aggregate total must never absorb a context where the assertion is absent.
- **The uncovered case is not only `null` — a `0` can be N/A-by-construction.** Where the probed series is structurally empty in a context (reduced motion neutralises transitions to `1e-06s`, so a mid-flight frame counter reads a real `0`, not `null`), an assert consuming that counter can never fire there, yet its `0` looks like a measurement. When a pack carries `sheet_reached_settled_open_pose` / `sheet_open_was_midflight` for the animated contexts but has **no `reduced_*` counterpart**, the pose/mid-flight claim is N/A-by-construction under reduced motion: surface it as a coverage gap (add the reduced counterpart, or record it as justified-N/A in the `Discovered = Tested + Justified N/A + Blocked` ledger), and never let the green animated rows absorb it. A context reporting `0` where the series cannot exist and a context reporting `0` because nothing happened are different findings.
- **Reconcile sibling fields that appear to measure the same thing.** A `removed=0` counter alongside `sawRemovalInLog=true` in every context means one of the two is misnamed. State which field the guarding assert actually reads before a reader assumes removal was never observed.
- **Check for an already-running duplicate before you launch a repeat chain.** When asked to launch a repeat/repeatability chain that writes fixed filenames, `ps` for the exact command FIRST — the chain may already be in flight (the requester fired it, then asked you to launch it in a separate message), and a second launch races the same output paths into one interleaved evidence set. Attribute a live instance to its owner via `/proc/<pid>/environ` (`HERMES_HOME`/`HERMES_SESSION`), report its PID plus the artifacts it has already written, and do NOT launch a duplicate.
- **Separate a deterministic failure from a load flake by set algebra, and measure the host floor.** Split the per-run `failed` lists: the INTERSECTION (fails in every repeat) is a deterministic property — a probe-logic mis-calibration reproduces identically regardless of host load; the SYMMETRIC DIFFERENCE (fails in some runs only) is a timing/load flake. Never let one headline `failed` count conflate the two; they dispatch to different fixes (probe logic vs sampling hardening). When repeats are requested for timing purity, sample `/proc/loadavg` + run-queue across the WHOLE window (`scripts/host_load_sampler.py`) and report min/mean/max load1 against `nproc`; if load stays above `nproc` with no probe of yours running, that is the host's ambient floor — there is no clean window to retreat to, say so plainly, and attribute any load-sensitive assertion failing under it to load rather than to a defect. Recipes: `references/run-evidence-provenance.md`.
- **Separate artifact creation from independent verification.** A reviewer who did not implement the application may execute and certify their own revision-bound inspection run; running the browser does not make them the application creator. Label implementation-owned checks as self-check evidence and obtain an independent reviewer when required. Bind every certified claim to that reviewer's actual run identity (`claim_run_id == evidence_run_id`), not to inherited screenshots or creator assertions. Recipes: `references/run-evidence-provenance.md`.

**Scope a section claim to the section, and confirm it by element query:**
- A whole-document scan for a banned token/label false-positives on legitimate prose: the same token (a numbering note in working notes, a cross-reference caption) can live in the body while the label you are clearing is genuinely absent from the surface under test. Scope the scan to the container (`#amendment`) *and* to the exact selector the label lives in (`.gate h5`), then report the scoped result — an unscoped grep that "found it" does not answer the claim, and an unscoped grep that finds nothing does not either.
- Independently re-render the same surface and md5-compare your capture against the delegated script's PNG. Byte-identical output proves you inspected the same DOM the script measured, so agreement between your verdict and its verdict is meaningful corroboration; different bytes with an unchanged source hash means a non-deterministic capture (timing, fonts, motion) that must be resolved before either number is quoted.
- Transcribe a value you must quote verbatim (a label, an id list, a caption) from the DOM — `innerText` at the exact selector — never from a fixed-region crop. A crop whose bounds slice the glyph line returns half-cut text that reads as a *different* string. Crop only for visual judgment; transcribe from the DOM and let the crop corroborate.
- A wrapping claim needs a per-element measurement, not a squint: compare each element's `getBoundingClientRect().height` against its single-line height (`lineHeight`) and report which elements wrap. Wrapping card headings or prose are not defects; clipped text is. Refuse to assert "no wrapping" without the numbers.

**Declare the coverage boundary of a delegated assertion pack:**
- When a delegated script asserts only some of the contract rows, name the rows it does NOT cover and state that they are visually/structurally present but not machine-verified by this pack. A partial pack must never read as full verification, and never fold an uncovered row into an existing verdict by widening that verdict's scope — offer to add it as a separate assertion instead. This is the section-level form of the `Discovered = Tested + Justified N/A + Blocked` ledger: an unexplained gap is not a PASS.

**Falsify a vision-pass anomaly with pixels before reporting it:**
- Screenshot review at reduced resolution invents structure: anti-aliased text on a light ground reads as a solid coloured "band", and a 2px rule reads as thicker or absent. Before filing any anomaly seen only in a downscaled view, confirm it with a per-pixel scan of the full-resolution PNG (scan a fixed column/row for contiguous non-background runs; count and colour each run). A run that breaks at glyph boundaries is text, not a rule — report only what the scan confirms. Recipes: `references/pixel-forensics.md`.
- A rule's identity is its measured **thickness in px and colour**: scan one column for the contiguous dark run and report `y0..y1`, length, and RGB. Confirm an unfamiliar colour against the source stylesheet before calling it broken — a per-moment accent `border-top` in a token colour is intended, not a regression in the header rule.
- An edge-bleed scan that flags pixels at the frame border is usually detecting the container's **own border stroke**, not content escaping the frame. A 1px stroke hugging all four edges, at a constant inset, is the border; a fill consolidated on one edge is content. Assert title-safe geometry from `getBoundingClientRect` when a DOM is reachable and use the raster only as confirmation.

**Capture state and scroll reachability before classifying a defect:**
- Wait for the intended state's visible heading/control and the loading indicator to disappear before capturing; a fixed delay alone can record a transient loading screen and misclassify it as missing content. Keep loading-state evidence separately when it is itself in scope.
- For content apparently covered by fixed navigation, capture the actual viewport, scroll the affected instruction/control into view, and repeat at maximum scroll and keyboard focus. Measure its rectangle against the fixed bar and use hit-testing for actionable controls; an initial below-fold crop does not establish persistent occlusion, while a successful click alone does not establish readable instructions.
- Build the required session/state/viewport checklist before scripting the happy path. Separate inventoried painted controls from exercised controls, and record skipped checks as UNVERIFIED rather than failed0 or PASS; DOM counts do not prove interaction coverage.

**Capture geometry:**
- An element screenshot is the element's box, not the declared viewport. When the element is clamped by an ancestor's `max-width`/padding, the PNG dimensions differ from the requested viewport — label the file and report the actual pixel size instead of repeating the requested viewport as fact.
- To deliver a PNG at an exact declared size, capture with `fullPage: true` and clip at integer coordinates. An element screenshot rounds a fractional box outward (a 1080-tall element at document y 525.75 yields a 1921px-tall PNG), and a `clip` *without* `fullPage` is clamped to the viewport, truncating an element that sits below the fold. Assert the returned dimensions against the requested size, and disclose any sub-pixel rounding you applied.

**Do not let a self-reported label stand in for a value:**
- When a readout, badge, or status string reports a state, read the computed property behind it before repeating the claim. Boolean labels collapse distinct values ("active", "on", "berubah") into one word.

**Assert geometry, not just tokens — collision, containment, clipping:**
- A spec with token, typography and motion assertions but no *geometry* assertion is incomplete: all of those can pass while boxes overlap or text is cut off. Every rendered-surface audit must, per visual state AND per size mode, assert (a) no two visible text/graphic elements overlap, (b) no visible element escapes the title-safe frame, (c) no element silently clips its own rendered text.
- Compute overlaps from `getBoundingClientRect()` intersections and treat ancestor↔descendant pairs as *containment*, not collision — one nesting rule keeps the result readable instead of flagging every wrapper as a collision. Use a sub-pixel tolerance (~0.5 px²) so adjacent borders do not register.
- **A zero is only evidence if the detector has been shown to fire.** Trigger it against a positive control (inject two overlapping siblings + one out-of-frame element + one narrow overflow box) and confirm each assertion count rises before reporting the clean result. Report the control alongside the verdict.
- **A presence check is not a geometry check — assert painted area, not `!== null`.** A predicate like `document.querySelector(sel) !== null` passes for an element that exists but paints nothing (`display:none`, `visibility:hidden`, `opacity:0`, or a zero-size box): `getBoundingClientRect()` returns an all-zero rect, which then satisfies *every* "no overlap" comparison it is meaningless to make. Assert non-zero painted area (`rect.width > 0 && rect.height > 0`, or a stored `area_px2 > 0`) on the element **and on each element it must not cover**, and require the expected child count **exactly** (`=== 4`, never `>= 1` or a `truthy` list) so a missing or hidden label cannot silently shrink the comparison set to nothing. Persist per-element `w`/`h`/`area_px2` in the evidence so a later reader can distinguish a real pass from an unrendered one.
- **Prove an overlap assertion with an *occlusion* mutant, not a deletion.** Removing the element or setting `display:none` exercises only the presence/null branch; it never exercises the overlap branch, so a broken overlap predicate still reads FAIL for the wrong reason and looks fixed. Re-create the exact geometry the assertion forbids (drag/drop the element onto the region it must never cover, e.g. an inline `bottom`/`left` override that straddles the rail) and confirm the overlap metric goes non-zero by the blocked area. Then re-run the whole mutation set against the *hardened* assertion and report the concrete evidence value that drove each FAIL (`null` probe / `area_px2 == 0` / `max_overlap_px2 == 130.68`), not just the boolean — a FAIL with the right number cited is proof; a bare FAIL is not.
- **Mutate a copy, never the artifact under test.** Apply each mutation to a throwaway copy under your own scratch dir and verify the copy's md5 differs from the production hash before running. Path-parameterise the probe once (read the HTML and output dir from env vars) so a single probe file drives every copy; keep the production file read-only throughout.
- Report laid-out vs *painted*: an element can extend past the frame yet paint nothing because an ancestor clips it, or paint partially and be visibly cut. Give the painted fraction, not just the overflow distance.
- Distinguish a real defect from a criterion artifact before filing: a zero/small box whose label is a child element (a `2px` `<div class="tick"><span>-2</span></div>`) trips `scrollWidth > clientWidth` without clipping any glyph, and an absolutely positioned descendant can inflate an ancestor's `scrollHeight` while the ancestor's own content is fine.
- After a container-unit (`cqw`/`cqh`) migration, an element whose offset is still expressed in `px`/`em` overflows by the *same absolute distance at every container size* — that invariance is the tell that it was missed in the refactor. Grep the element family for surviving `px`/`em`/`vw` after a `cq` conversion.

**Zero-request proof:**
- To claim "no external requests", count `page.on('request')` and subtract the entry equal to the page URL; report the remainder as foreign requests. A total of 1 (the document itself) is the pass case, not 0.

**A non-zero computed transform can be a rest pose, not mid-flight:**
- Before reporting "the element was mid-transition", prove it was actually animating. A `[data-reveal="pending"]` element parked at its start pose reads the same non-zero `translate`/`transform` as an element in flight. At the capture instant also read `document.getAnimations()` running count and the element's own `getAnimations().map(a=>a.playState)`; a non-zero value with 0 running animations is the resting start pose, not motion. To prove interpolation, trigger the transition the way a user does (incremental scroll/step, not `scrollTo` jump) and collect the distinct intermediate values while the animation is live.
- **A hidden/`display:none` node is the same trap in reverse — and it corrupts a *counter*.** A node carrying `[hidden]` reports `transform: none` at full `opacity`, which is neither a rest pose nor motion. A per-frame lifecycle recorder that starts *before* the trigger captures those pre-open frames, and a mid-flight counter comparing computed transform against the settled pose counts them as travel: a counter that should read `0` reads `N`, deterministically, failing a `no_intermediate_pose_held`-style assert on a correct artifact. Gate the counter on a `painted` flag recorded per rAF tick (`getClientRects().length > 0 && !hidden`) instead of the computed value alone, and prove the gated counter still FIRES in the contexts that do animate (e.g. `midFlight = 15/11/15` animated vs `0/0` reduced) — a gated counter that reads 0 everywhere is a dead counter, not a clean result, so quote the animated-context population as the positive control. See `references/motion-and-cascade-metrology.md` §1b.
- A jump (`window.scrollTo`) can skip or stall an IntersectionObserver-driven reveal entirely: the observer's callbacks may not run for the skipped band, so a jump-scroll capture shows parked, never-fired elements. Use incremental scroll for reveal evidence.

**Never let a peer-specified output dir be your only copy:**
- When you write into an output directory you do not exclusively own (a shared `evidence/` dir, a run dir a peer also writes to), a concurrent process that reuses the requested filenames will silently clobber your artifacts — including your JSON report. Write the authoritative copy under a producer-namespaced subdir (`<outdir>/<producer>/`) AND best-effort at the requested path; record the sha256 of the authoritative bytes; then verify on-disk hashes match the record after the run. A report whose schema you did not author at the requested path means another producer overwrote it — read it, corroborate if useful, and re-emit under your namespace.
- **Your own repeat runs collide too.** A probe that writes a fixed output filename (`proto_render_report.json`) overwrites the previous run's per-context detail, so when you are asked to run the same probe twice (run N, then run N+1 for a repeatability check) the second run destroys exactly the run-N evidence you will compare it against. Before launching the next run, copy-and-hash the finished run's report to a run-scoped name (`run<N>_report.json`, record its sha256) and tell the requester which file holds which run. Snapshot first, launch second — a green run you cannot diff is a wasted run.
- **A crash plus a `cp -f` fabricates a fresh report.** When a probe aborts before writing its fixed-path report, the `cp` you run anyway carries the **previous** run's report forward under the new run's name — a crash that presents as a completed run with a valid artefact. Detect it by hashing the run-scoped reports and comparing: two consecutive `run<N>_report.json` that are byte-identical while one of those runs exited non-zero means the later file is carry-forward, not fresh evidence. Hash every run-scoped report and quote the pairing in the receipt; never infer freshness from the filename or the exit line. Recipes: `references/run-evidence-provenance.md` §8.

**Report exactly what was asked, with the numbers bare:**
- A delegated render/measurement request wants the artifact manifest (file, pixel size, bytes, md5), the measured values, and the per-state/per-mode verdicts — not design commentary. State a confirmed defect flatly with element, mode and px; do not soften it or reclassify it as a spacing observation.
- When the requester says "report only X" or "no need to repeat the analysis", return that subset and do not re-litigate prior rounds. Withhold design-quality judgment unless it is the assigned question.
- Report a zero only alongside its positive control, and state the resolution evidence for a fixed defect explicitly (the geometry counter that flagged it now reads 0 in every state and mode) rather than implying it from the absence of a new finding.

**Audit integrity and attribute writers before reporting a change (read-only requests):**
- **Prove a certified artifact unmoved by hash equality across every pinned copy, not by mtime.** Hash the live file and `cmp -s` it against each frozen/certified copy in one pass, and read the `%i %w %y %z` tuple: live == frozen == cert-dir copy is the proof, an unchanged mtime is only corroboration. A file preserved-but-rewritten keeps its mtime's *appearance* while ctime/inode move.
- **Absence of an open handle is not absence of a writer.** `lsof +D <dir>` / `fuser` returning no holder (rc=1) only means nothing holds a descriptor now — a finished writer leaves none. Attribute by the 
**session-scoped tool-call log**, not by profile activity: `grep -nE 'tool (write_file|patch) completed' logs/agent.log` carries the session id and completion second; match that second to the file's mtime. A profile that "was active" is not the writer.
- **A "modified externally" warning is frequently the requester's OWN session.** Resolve by session id before suspecting a peer; do not leave a false fork narrative standing.
- **A copy is not a fork; a stale snapshot is not an authority.** Enumerate every copy with size+mtime (`find / -name '<file>' -printf '%TY-%Tm-%Td %TH:%TM %10s %p\n'`) — one live file plus one smaller, older snapshot (an attachment from an earlier revision) is a snapshot, not a second author.
- **"Point me at the file" with no such file is answered by proof of absence, never by description.** Run the search and paste it (`find -iname '*x*'`, plus `-iname '.*x*'`, a `.md` title scan, a content grep), state "no such file on disk", and name the real artifact being mistaken for it. Never describe a document you were asked to point at.
- Honour the read-only constraint literally: no runs, no writes, only reads and the report. Recipes: `references/run-evidence-provenance.md` §13.

---

## Reference Files
- `references/five-gate-pipeline-spec.md` — Detailed failure codes and operational rules.
- `references/runtime-schema-contract.md` — Complete `data-ui-*` attribute specification and CSS mapping.
- `references/mutation-testing-calibration.md` — Calibration harness & mutation operators guide.
- `references/motion-and-cascade-metrology.md` — Peak-vs-instant motion sampling, the in-page rAF lifecycle recorder with an interior-frame predicate (§1b), CDP cascade attribution, capture-geometry and request-forensics recipes.
- `scripts/lens_audit_harness.js` — Runnable Playwright/CDP evaluation harness with all gate assertions.
- `references/geometry-collision-audit.md` — Pairwise collision, title-safe containment and clipping-triage recipes, the positive-control protocol, and the painted-fraction measure.
- `scripts/motion_sampler.mjs` — Re-runnable interval probe: samples distinct animated elements AND running animations across a burst, reports peak + time series per trigger.
- `scripts/motion_paint_classifier.py` — Re-runnable in-page rAF lifecycle classifier: records a node per frame, flags `painted` vs pre-open/`[hidden]` frames, and reports the mid-flight count under both the naive and the corrected (painted-only) predicate. Use to prove a `no_intermediate_pose_held`-style failure is a probe mis-calibration, not a defect.
- `scripts/collision_probe.mjs` — Re-runnable geometry probe: pairwise collisions, title-safe escapes, overflow triage across every trigger in both size modes, with a built-in positive control.
- `scripts/mutation_copy_harness.py` — Data-driven mutation runner: applies text-substitution mutations to COPIES of the artifact, drives a path-parameterised probe against each, and reports per-mutation verdict plus the evidence value (null / area==0 / overlap>0) that drove it. Use whenever you must prove an assertion fails on its own named defect.
- `references/pixel-forensics.md` — Falsifying render claims from raster when you only have PNGs: PNG manifest without a lib, column-scan rule thickness/colour, the anti-aliasing text-vs-band trap, edge-bleed vs container-border, content-bounding-box margins, probe coordinate-space/window bugs, and hue-difference classifiers firing on subpixel text.
- `references/run-evidence-provenance.md` — Post-hoc justification of a delegated run: capturing exit status on a detached launch, distinguishing FACT/INFERENCE/BLOCKED for an unobserved status, validating a baseline oracle before diffing, freeze-directory provenance checks, cross-run stability tabulation, pre-launch duplicate detection, deterministic-vs-flake set algebra and the host load floor, repeat-run report collisions, isolated re-execution of a peer's payload out of a contended dir, margin-over-boolean evidence, the producer-vs-verifier split, and §13 read-only integrity + writer attribution (certified-file-unmoved proof, writer identification by session-scoped tool log, proof-of-absence for a requested-but-missing document, copy-vs-fork).
- `scripts/host_load_sampler.py` — Re-runnable interval sampler of `/proc/loadavg` + run queue to CSV, with a min/mean/max summary. Run it as a tracked background process across a repeat window whenever a "clean timing sample" is claimed.
