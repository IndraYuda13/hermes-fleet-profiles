---
name: headless-render-measurement
description: Render HTML headlessly; measure live DOM geometry.
version: 1.0.0
author: Hermes Agent Curator
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [playwright, chromium, render, screenshot, dom-measurement, visual-qa, evidence]
    category: devops
    related_skills: [fleet-v22-governance, sdlc-review]
---

# Headless Render & Measurement Probe

## When to Use

- A peer lane (design, review, QA) hands over HTML mockups/pages and asks for PNG renders at specific viewports.
- Someone asks a question about layout that must be answered from live DOM numbers: "does it overflow at 390px", "how many product tiles are fully visible above the fold", "what is the `.top` of the first card".
- You need deterministic visual evidence bound to a revision, or you are verifying someone else's rendering claim.

This is the evidence-producing skill, not a visual-design skill. It renders and measures; it does not judge aesthetics.

## Non-negotiables for a read-only evidence job

- Never modify the requester's INPUT files, and never install packages into their project venv. Hash every input before and after the job and paste the identical `sha256sum` lines into the report — identical before/after hashes are what prove the read-only claim.
- When the requester names OUTPUT paths and asks you to re-render in place ("re-render the 6 PNGs at the same paths"), overwriting those named artifacts is the requested deliverable, not a violation. Keep the superseded copies under `<probe-dir>/preview-prev/` so the prior round stays diffable, and put every artifact you were NOT asked to write (reports, JSON, extra probes) in your own evidence directory.
- If a renderer is missing, find one already on the host rather than mutating their environment.
- A browser you did not launch belongs to someone else. Report its identity in the deliverable (the `Browser` string from `/json/version`, the owning `--user-data-dir`, and the target count before and after), create only your own targets, apply `Emulation.*` per attached session so nothing leaks into their tabs, close every target you opened, and never kill the process — other lanes are mid-task in it. A pre-existing target already showing the page you were asked to measure is not yours: list it as pre-existing and leave it.
- Launching your own headless Chrome as root fails with `Running as root without --no-sandbox is not supported`. When you must launch, use `--headless=new --no-sandbox --disable-dev-shm-usage --user-data-dir=<scratch>/chrome` and keep the profile inside the scratch dir so cleanup is a single `rm -rf`.
- Report raw command and probe output. Label anything you did not measure as not verified. An unmet request gets an honest `count: 0` plus the reason, never an invented number.

## Procedure

1. **Locate a working renderer before writing any harness.**
   - Test each candidate interpreter explicitly: `/usr/bin/python3 -c "import playwright; print(playwright.__file__)"`. The interpreter `which python3` resolves to can differ from the one a package was installed for, and a package in one is invisible to the other — probe rather than assume.
   - Playwright's pinned browser build may not be downloaded on the host. Do not block on `playwright install` (it is heavyweight and the host may be disk-constrained). Instead point `chromium.launch(executable_path=...)` at a Chrome that IS present: `/usr/bin/google-chrome`, `/usr/bin/google-chrome-stable`, or `~/.cache/ms-playwright/chromium-<rev>/chrome-linux64/chrome`.
   - Translate a launch flavor the requester NAMES into one this Playwright accepts. `channel` takes a distribution name, not a binary path, so `channel="google-chrome"` aborts with `BrowserType.launch: Unsupported chromium channel "google-chrome"` before any page opens; `channel="chrome"` (resolves the system Chrome on most hosts) and `executable_path="/usr/bin/google-chrome"` are the same binary and both work. Honor the intent with `executable_path`, then state the deviation and the resolved `--version` in the report — the requester named a channel, so silently launching a different one is a fidelity gap they cannot see.
   - Confirm the interpreter/browser pair launches a page and evaluates JS in it before writing the full harness.
   - If NO interpreter has Playwright, do not install anything. Check for a Chrome already listening on the CDP port (`curl -s http://127.0.0.1:9222/json/version`) and drive that browser with `scripts/cdp_measure.mjs`; node >= 22 ships global `fetch` and `WebSocket`, so the harness has zero dependencies. Record which path you used in the report — "tool: CDP over node" is part of the evidence.
2. **Recon the inputs.**
   - Confirm they are self-contained: `grep -o 'https\?://[^"'\'' )]*' file.html`. A `file://` render is only faithful offline if every asset (fonts, CSS, images) is inline. No remote refs means no network dependency and a reproducible render.
   - Enumerate the real DOM hooks before probing: `grep -o 'data-testid="[^"]*"' file.html | sort | uniq -c` and grep the class names the requester named. This is what lets you detect a selector that will match nothing.
  - When the requester names CSS hooks but NOT the file, identify the artefact by grepping the candidate set for those hooks and take the single file that carries them (`grep -c 'sortsel\|catbar\|cta-row' <each candidate>`). Report how the target was identified. A sibling artefact in the same directory can share a generic hook (`.grid`) while only one has the specific ones, so grepping the generic name picks the wrong file.
  - Inventory the scratch path the requester named BEFORE you write and again at the end (`ls -la`). Files that appeared and are not yours belong to another lane working the same directory: leave them intact, name them in the report, and do not clean them up as if they were your temp files.
   - A grep class census is an UPPER bound, not the selector's count: `grep -c 'class="[^"]*\bgrid\b'` also matches `g-grid` and `console-row`, because `\b` treats the hyphen as a word boundary. Confirm every count in-page with `document.querySelectorAll('.grid').length` before printing it, or you report `count: 2` for a selector that matches one element.
   - When the requester narrates which structural edits landed since the last revision ("the paragraph under H1 is hidden, the assure row removed, the chips hidden on mobile"), verify each claim in-page at the stated breakpoint with `getComputedStyle(el).display` before you report. A claimed-hidden element that still computes to `display: block` invalidates the premise of the job, and confirming the edits is what lets you attribute a geometry change to its stated cause instead of emitting a number with no explanation.
3. **Build one harness per job**, parameterized over (file, viewport, deviceScaleFactor, selector). For each artefact: render mobile and desktop in SEPARATE browser contexts, run the probe in the SAME page object as the mobile screenshot, and write one JSON report covering every artefact.
4. **Probe with explicit numbers.** Emit `documentElement.scrollWidth`, `window.innerWidth`, `documentElement.clientWidth`, `scrollHeight`, `innerHeight`, plus `scrollWidth > innerWidth` as a boolean and the overflow in pixels. For each element emit its `getBoundingClientRect()` rounded to 2dp. Compute visibility in-page — never eyeball a screenshot for a number.
5. **Prove the render is not blank.** Decode every PNG and count distinct RGB colours; a count of 1 means a blank/uniform image. Use `scripts/png_stats.py`.
6. **Prove the PNG matches the requested geometry.** Assert stored pixel dimensions: 390x844 at `deviceScaleFactor: 2` must be 780x1688; 1440x900 at DSF 1 must be 1440x900.
7. **Report** compact tables of raw numbers, the input/output hashes, and the fidelity caveats.

## Selector fidelity

- Use the requester's selector verbatim, and when they give a compound description ("the first `.row` with a `.buy` button"), express the filter IN the selector: `.row:has(.buy)`. `querySelectorAll` returns every match, so a parenthetical qualifier belongs in the selector string, not in post-filtering of a possibly different set.
- When a named selector or `data-testid` matches 0 elements, report `count: 0` and the actual hook census from step 2. Never silently substitute a lookalike selector and present its numbers as the answer to their question — flag the mismatch and give both sets.
- Probe the redundant selector too when it is cheap. If two selectors agree on the first element and the count, the finding is robust; if they disagree, you have found a real bug in one of them.

## Overflow and visibility claims

- Horizontal overflow is proven only by `documentElement.scrollWidth > innerWidth`; report both values plus the delta. Counting elements whose `right` exceeds `innerWidth` answers a different question — see the containment rule below.
- Per-element offenders are NOT page overflow. A carousel rail, chip strip, or segmented control with `overflow-x: auto` legitimately holds children past the viewport edge. For each offender walk its ancestors for a non-`visible` `overflow-x` and report those as contained by an internal scroller, separately from real document overflow. A raw offender count over a section that happens to carry a horizontal rail invents a defect the requester will chase.
- Cross-check the overflow conclusion in a plain context (no `is_mobile`, no `--hide-scrollbars`). Mobile emulation and hidden scrollbars can change layout enough to mask or invent an overflow; if the plain context disagrees, the emulated number is not the answer.
- Fully visible, partially visible, and below-fold are three distinct buckets. See `references/dom-measurement-probes.md` for the exact predicates.
- When the requester states the visibility predicate explicitly (e.g. `top >= 0 AND bottom <= vh`), compute THEIR predicate verbatim as the answer and the skill default alongside; report both. They coincide at scroll-top and diverge only for elements sitting above the viewport.
- "Fully visible" ignores occlusion. If the page has a `position: fixed`/`sticky` top or bottom bar, emit the bar's rect and the ids of product elements whose vertical band intersects the bar band, and report that as a separate result. A tile can be fully inside the fold AND covered by the bar — never fold occlusion into the fold buckets silently.
- Enumerate every `position: fixed` / `sticky` element yourself; do not probe only the bar the requester named. The decisive occlusion is often a bar nobody mentioned. Intersect on BOTH axes: the vertical-band test is only valid for a bar spanning the full viewport width.
- **Rect overlap is not content coverage.** A product box whose rect intersects the bar band may have only its padding/border tail under the bar with no ink covered — a card ending at 841 under a bar starting at 832 overlaps 9px while its last text leaf ends at 825, untouched. Descend to text leaves (elements with no element children and non-empty text) and test each leaf rect against the bar band; report `rect-overlap idx` and `content-actually-covered idx` as two separate results. A bar that overlaps a card's box but covers none of its text is not a defect, and calling it one sends the requester chasing padding.
- **Hit-test as the occlusion oracle.** Band arithmetic knows geometry, not stacking. Confirm every occlusion finding with `document.elementFromPoint(x, y)` at the element's center plus four inset corners, and accept the element as unoccluded when every probed point returns the element itself or a descendant. Resolve containment against BOTH the product and the bar: the topmost hit inside a bar band is normally a CHILD of the bar (a `SPAN`/`SMALL` label), so a test comparing only against the bar element reports "not occluded" for every covered product.
- **A fixed bottom bar is only acceptable if what it covers is reachable.** It occludes at the END of the document as well as in the first viewport, and the first-viewport fold test cannot see either. Measure by scrolling to the document bottom and re-reading the last painted content element: it must end above the bar's top. Report the compensating `body` `padding-bottom` alongside but do not accept it as proof — a bar taller than the reserved padding still buries the page tail.

## Fold budget (exact flow sum to an element's top)

A request for a "running sum of (height + vertical margins) from document top to
the selector's top" has no meaning as a flat census over the DOM: a CSS box tree
nests, so summing every element above a point counts each ancestor on top of its
own descendants and overshoots wildly. Compute it on the ANCESTOR CHAIN instead
— per level, the in-flow preceding siblings' `height + vertical margins`, the
parent's leading `padding-top + border-top`, the parent's flex/grid `gap`, plus the
element's own `margin-top` — and PROVE it by closure: the chain total must equal
the element's measured document offset with residual `0.00`. Iterate the addends
until it closes, and publish only the model that closes; if a candidate does not,
keep its numbers as explicitly labelled raw evidence and say why it is invalid
rather than shipping a second inconsistent column. `references/dom-measurement-probes.md`
carries the decomposition JS; `scripts/fold_budget_probe.py` runs the whole pass
and prints the per-selector residual so a non-closing chain is visible, not hidden.

Addends a rect-only sum silently misses, and the traps that come with them:

- Flex/grid `gap` has no rect and no margin — read it from the PARENT and verify it
  against geometry (`help.top - (btn.top + btn.height) == getComputedStyle(row).gap`).
- An ancestor's own `margin-top` is an addend; its `margin-bottom` is not.
- In a multi-column grid or flex row, siblings from an EARLIER line must be replaced
  by that line's row pitch, not summed individually — summing all preceding siblings
  overcounts a 3-column grid by two extra item heights.
- `display: none` siblings contribute nothing and their margins collapse into
  nothing: verify each requested selector's computed `display` in-page, since a
  third of the requested selectors can be `none` and contribute zero budget.
- An element's `rect.top` grows with scroll; convert to a document offset with
  `rect.top + (sum of ancestor scrollTop)` so the number is viewport-independent.

## Override cascade ladder (variant measurement)

A request of the shape "measure this trim cascade: V0 base, V1 (+override A), V2
(+B), V3 (+C), V4 (+D)" is a VARIANT measurement, not an edit. Copy the source once,
hash source and copy to prove they are identical, and write each variant as its own
file in your own scratch dir. Generate the variants by injecting the override
immediately before `</head>` (see `references/dom-measurement-probes.md`), and give
the injected block a self-echoing `console.log` so the page reports the CSS that was
truly applied.

- Attribute the delta per STEP, never as an aggregate. The first step of a ladder
  labelled "trim" can be a REGRESSION: read the rule being overridden out of the
  source (`grep -o '\.name{[^}]*}'`) before interpreting its delta. An override that
  swaps an asymmetric rule for symmetric padding can ADD vertical space, so the box
  grows and everything below it moves down while the edit reads as a reduction.
  Name which step actually carried the reduction.
- A cascade ladder often shows one step contributing almost nothing while the step
  the requester attributed the win to contributed it elsewhere. Report the per-step
  deltas, not just V0 vs Vlast, or the requester re-derives the wrong lever.
- Prove an override is live by a COMPUTED change (a height that moved), never by the
  presence of a style tag: an injected block whose selectors match nothing silently
  measures the base variant again and reads as "no effect".
- Verify it per DECLARATION, not per block. Dump the computed value of every property
  the override touches, per variant, as a table, and print that table: it proves each
  override landed and it exposes a declaration that is a NO-OP because the source
  already computes that value (a `border-radius:14px` override against a base already
  resolving `var(--r-lg)` to 14px contributes 0.00px). Attribute the step's delta to
  the declarations that actually moved something, and say so when the requester named
  the no-op as the cause of the win.
- Make the per-step delta arithmetic CLOSE: print `base - stepA - stepB - stepC ==
  final`. A cascade whose steps do not sum to the observed move has an unmeasured
  addend, and that is how a misattributed lever reaches the contract.
- A "trim" override that adds `white-space: nowrap` + `overflow: hidden` +
  `text-overflow: ellipsis` buys height by DISCARDING copy. Measure the loss instead
  of reporting the gain alone: clone the element off-flow with `whiteSpace:nowrap;
  width:auto; maxWidth:none`, compare natural width against the in-flow box width, and
  report `clippedPx` per affected element. Lead the findings with it, because a variant
  that clears the gate by truncating shipped text is a content regression, not a layout
  win. Check the shipped font-size too: a mobile rule lowering `font-size` shrinks the
  natural width and hides how much a wider viewport would lose.
- Keep the fixed-bar count as a SECOND column beside the fold count, per variant. A
  variant can raise fully-visible elements from 4 to 6 while "fully visible AND clear of
  the fixed strip" stays at 4, because the two new ones render under the strip. Report
  both columns and name which one the gate actually needs; a trim that moves only the
  first number has not solved the problem the trim existed for.
- When a variant instruction has a half the artefact cannot express ("move the help
  line into the sheet body" on a page with no sheet body), report it as UNMEASURABLE on
  this revision and name what would make it measurable. Do not silently measure the
  expressible half and present it as the whole variant.
- Two viewports can return byte-identical numbers for every variant (same layout
  branch, different viewport height). Say so instead of presenting them as
  independent confirmations.
- Re-run the headline variant rows in a fresh context; matching numbers are what
  upgrade the table from one pass to reproducible, and a second fresh-context script
  is cheaper than re-running the whole matrix.
- Session-specific short probes still obey the read-only rules: hash input and copy
  before and after, name the temporary files created, and say no write landed
  outside the scratch dir.
- When the requester asks for a compact table under a line budget, the shape is: one
  header line naming tool + copy + flags, the table, the per-step summary line, the
  echo list, then short numbered findings. No methodology recap.

## Reporting against a stated gate

- When the requester states a pass condition (e.g. `first .top / vh <= 0.60 AND fully-visible >= 2`), emit a per-artefact PASS/FAIL row that computes THEIR expression verbatim, with the raw numbers kept visible beside it. Never let the derived verdict replace the numbers, and never quote a ratio from a different viewport than the one the gate names.
- Report independent secondary failure modes on their own line, not folded into the gate verdict. An artefact can fail the gate and separately fail for another reason (above-fold tiles that pass the fold test but are fully covered by a fixed bar); the non-gate failure is often the more actionable of the two.
- A gate is stated for ONE viewport, and often for ONE element inside it. When another viewport's ratio exceeds the same threshold, or a sibling element behaves differently from the gated one, classify it as pre-existing or regression by diffing against the prior round — a figure byte-identical to the previous revision is pre-existing and explicitly not a regression, which is a different statement from reporting a failure. Keep the two apart in the report rather than letting an out-of-gate viewport read as breakage.
- An absolute pixel gate is usually derived at ONE viewport (`vh - 56` becomes `788` only when `vh == 844`). When the same gate is requested at other viewports, recompute it viewport-relatively in JS (`innerHeight - stripHeight`) and say in the report that you translated it — hardcoding the literal `788` across 667/640 answers a different question at every width.
- When asked to keep the reply short / numbers only, the shape is: hash block, one table per viewport, one verdict line per artefact, and a one-line note for anything the gate does not cover. No narrative, no methodology recap.
- If the requester skips re-rendering PNGs (geometry only), do not run the blank-check or dimension asserts, and say in the report that the visual-fidelity caveats are therefore untested for this revision.
- When the requester labels the blocks themselves ((A)…(F)), answer inside exactly those labels: paste raw command output, and name the tool used for any block you measured. Free text is one line per block — the numbers are the deliverable, not the narration.

## Contrast gates on the page's own palette

A token request ("give me a muted colour that clears 4.5 on all three backgrounds") is a computation, not a judgement. Read the background tokens out of the
page's CSS custom properties, score every candidate against EVERY background,
and report the minimum ratio: the tinted surface binds, and a colour that clears
on `#FFFFFF` routinely fails on the tinted surface beside it. `scripts/contrast_audit.py`
does the scoring; `references/dom-measurement-probes.md` carries the WCAG
formula and the working code.

Score the palette's CURRENT tokens with the same table. "The existing `--muted`
clears 4.56 on white but 4.20/3.94 on the two tinted surfaces" is the finding
that justifies the edit; a bare "fails" does not tell the requester where. Rank
candidates by their minimum ratio and name the best single value. Offer a
two-value split only when no single candidate clears every background, and say
which background each half is for.

**Compute alpha composites against the element's ACTUAL painted backdrop, read from the
source, not against the backdrop the request suggests.** A composite is only meaningful
on the colour it is composited over: a translucent fill declared inside an accent
`.otp-hero` composites over the accent, so scoring it over `--ink` returns a confident
PASS (6.150) for a boundary that actually reads 1.140 against its real base. Grep the
element out of the source, find its containing background token, and when the requested
base disagrees with the source, compute BOTH and say which one is real.

Separate TEXT contrast from NON-TEXT boundary contrast in the verdict:
- A 1px border ring at 2.676:1 fails the 3:1 non-text threshold while the label text
  inside it passes at 18.469:1. Report the two on their own lines so a fix is not aimed
  at the wrong one.
- A translucent tint that is not required to delimit anything (an OTP cell fill inside a
  hero) needs no 3:1 at all if the digits on it clear 4.5. Say that, instead of listing
  it as a failure: raising the alpha may not even reach 3:1 (0.55 alpha reads 1.140, 0.72
  reads 1.190), which proves the separability has to come from the digits and the gap.
- Flag the NEAR-MISS tier explicitly: values that clear 4.5 by under 0.25 (4.604, 4.700)
  and values that clear only 3:1 (4.207 on a tinted surface) are worth a decision line
  even when they pass, because the next palette nudge flips them.

## Pitfalls

- Matching a PRIOR run's PNG dimensions is a two-variable problem: capture mode (full_page vs viewport) and scrollbar mode. New headless Chrome always uses overlay scrollbars, so a legacy capture with a visible classic scrollbar comes out 15px narrower on desktop (1425 vs 1440) and can differ by ~2px in total content height. Before re-rendering an existing artifact set, the cheapest control is an untouched sibling: re-render the byte-identical file and compare pixel dimensions. Also check PNG mtime against HTML mtime, a PNG older than its source is stale evidence no matter what it shows.
- When the prior convention cannot be reproduced (and reproducing it would require launching headed Chrome or a second browser), render at the requested exact viewport, overwriting the named paths, and keep the superseded files under `<probe-dir>/preview-prev/`. Say explicitly in the report that byte-identical PNGs for untouched artifacts are unavailable as the determinism control this round. That limit is about CROSS-CONVENTION comparison only: when the prior round ran the same harness at the same convention, pixel-exact reproduction is expected and is the control to quote.
- Rendering on a different Chrome build than the requester's reference device is a real fidelity gap. Layout numbers from live DOM are exact; font rasterization is not. State this limit instead of implying device-identical output.
- A rect-intersection overlap list is meaningless until you separate ancestor/descendant pairs from sibling pairs. A parent always intersects its children, so a card with 4 children yields 4 trivial "overlaps" that hide whether any two siblings actually collide. Test `a.contains(b) || b.contains(a)` and report sibling collisions as the real signal; report containment separately as structural.
- Proving a CSS declaration is fix-worthy, not accidental, takes one composed test: disable each declaration of the repaired rule one at a time in the live page (save inline styles, mutate, measure, restore, assert restore == baseline) and see which removal reintroduces the defect. Then repeat the measurement at narrower viewports and with a longer injected string for the measured element. A fix that survives only at the exact requested viewport and only for the shipped text is not proven.
- Claiming "verified visually" when you only decoded pixel diversity. Pixel diversity proves non-blank, not correct. Say which of the two you actually did.
- Chrome-driven harnesses print multi-KB pretty-printed JSON. Writing it to stdout and tailing it silently drops the first artefact's block. Redirect harness output to a file and read it back so the report is complete.
- Playwright's sync API is keyword-only: `page.screenshot(path=str(p))`, not `page.screenshot(p)`.
- Launch with `--no-sandbox` in containers/root, and `--disable-dev-shm-usage` when `/dev/shm` is small; otherwise Chrome crashes or the page dies mid-capture.
- Read every per-element metric from `getComputedStyle(el)` for THAT element, never from a style object captured on an ancestor. A `const cs = getComputedStyle(price)` reused inside a child mapper reports the PARENT's `font-size`/`line-height`, so the probe appears to refute a per-child change the requester reported (both spans came back "15px" when they were 10px and 26px). A per-child font or line-height that contradicts the stated edit is a probe bug until proven otherwise; re-read each child's own computed style before writing that finding. `scripts/child_style_probe.py` does this.
- Identical `.top`/`.bottom` on consecutive elements is usually two-column grid siblings, not a double-counted element. Before reporting a product count, prove each element is rendered and distinct — non-`none` display, non-hidden visibility, opacity > 0, non-null `offsetParent`, non-zero `getClientRects().length`, and a distinct `left`. A raw `querySelectorAll().length` is a DOM count, not a rendered-product count.
- When re-probing a repaired revision, diff the new hashes against the prior run to state exactly which artefacts changed, and treat byte-identical PNGs for untouched artefacts as the renderer-determinism control. Compare the prior round's report PNG `sha256` against the fresh ones and report the match per file: a pixel-exact match upgrades "unchanged" from geometry-equal to raster-equal and is the strongest evidence available that the new round measured the same thing the old one did. Only geometry equality is available when the prior round's PNGs were not hashed.
- A requester actively iterating will edit the inputs WHILE you probe. Hash each input immediately before AND after every pass, not once at job start. If a hash drifts mid-job that pass is invalid: discard it, re-run against the frozen revision, and open the report with a revision-churn warning naming the superseded and current hashes. Skipping this ships two mutually inconsistent number sets and a verdict computed from a file that no longer exists.
- State a freeze expectation when you hand the numbers back. A geometry number is only evidence for the exact revision measured, so if the requester edits again the probe expires; saying so up front prevents the result being quoted against a later revision. When the requester asks for FROZEN hashes, hash the set in two passes spaced apart and check that no process holds the files open before calling anything frozen — a single pass cannot tell a settled file from one still being written. Then compare each artifact's mtime against the probe's timestamp: an artifact edited AFTER the probe ran is hash-stable but has no probe coverage for its new content, so report it as stable-but-unprobed and do not let it ride on the frozen set. If prior hashes were not recorded, the prior round's report JSON is the diff basis: reproduce its exact numbers for the artefacts the requester says are untouched. Byte-identical geometry there is what substantiates "untouched" — otherwise it stays an unverified assertion.
- A centre-only hit-test is a false all-clear whenever a bar covers PART of an element. A tile whose centre clears the bar by 25px still has its "buy" band underneath, and `elementFromPoint` at the centre returns the tile's own descendant span, so a centre probe reports unoccluded for a row whose buttons are unreachable. Also probe the element's lower band and the centres of its interactive children (`button`, `a`, `[role=button]`), and report the covered band in pixels plus a percentage of element height: `max(0, min(el.bottom, bar.bottom) - max(el.top, bar.top))`.
- A page that loads no webfont measures identically with the CDN unreachable, so establish webfont presence before calling fold numbers device-faithful: `grep -c 'fonts.googleapis\|@font-face\|@import' <file>` plus in-page `document.fonts.status` and the loaded `FontFace` count. Zero refs means the geometry depends on the fallback, not the shipped family; the moment `--sans` points at a CDN family the fold moves and the measurement expires. State which case the revision is, and re-measure once the font is wired in.
- When the harness cannot await `document.fonts.ready`, sample the metric at increasing settle delays and report it only after two consecutive samples agree. A value that keeps moving is a layout that depends on load timing, and a single sample picks an arbitrary point in that drift.
- When the requester specifies how many items to print ("the first 6 matching line numbers", "the first 25 ids") and the source holds fewer, print the ACTUAL count and all of them. Padding a list to the requested length, or silently reporting `6`, is fabricated evidence — a two-match grep answered as six reads as agreement with a premise that is false.
- A provenance/coverage list the requester asks you to print verbatim (`wrong_list`, `badge_list`) comes from the source artifact, not from a re-derivation: print it as one compact line in source order and do not normalise, sort, or paraphrase the ids.
- A probe field that is CONSTANT across every element and every variant is a probe bug until proven otherwise. A misspelled result key (`selffHit` for `selfHit`) makes its consumer evaluate `undefined` and renders a whole column a confident zero, which reads as a finding ("no tile is hit-testable") rather than as a broken probe. Read the raw per-element rows before the summary, and re-run after any probe edit: the fixed run moved that column 0 -> 4/4/6/6 on identical input.
- Write a multi-line harness to a file and run the file. An inline shell heredoc (`python3 - <<'PY'`) is flagged for approval, and a stalled approval prompt kills a job mid-matrix; `write_file` then `/usr/bin/python3 harness.py` is the same code with no prompt in the path, and it leaves the harness behind as the re-runnable evidence artifact.

## Verification checklist

- [ ] Input hashes recorded before and identical after the job.
- [ ] For a variant/cascade ladder: every variant was generated from a hashed copy (the source itself never edited), and each variant's injected override was echoed back by the page and matched to what was requested.
- [ ] Each ladder step's delta was attributed individually, with the overridden rule read out of the source before the step was labelled a reduction.
- [ ] Every requested viewport has one PNG, and its pixel dimensions match the request exactly.
- [ ] No PNG is blank (distinct-colour count > 1).
- [ ] The probe ran in the same page as the mobile screenshot, at the requested viewport.
- [ ] Selector mismatches reported rather than papered over.
- [ ] Every fixed/sticky element was enumerated and each one's overlap with the product set reported separately from the fold buckets.
- [ ] Any structural edit the requester says landed was confirmed in-page (`getComputedStyle(el).display`) at the stated breakpoint before its effect was attributed to a geometry change.
- [ ] A fixed bottom bar's end-of-scroll reachability was measured (last painted content clears the bar top; reserved `padding-bottom` reported but not treated as proof), not just its first-viewport intersection.
- [ ] Input hashes were re-checked immediately before and after the measuring pass, and any mid-job drift was detected, the stale pass discarded, and the report marked with a revision-churn warning.
- [ ] On a repeat round, the prior round's report JSON was used as the diff basis: which files changed, and whether the untouched artefacts reproduce byte-for-byte (PNG sha256) and numerically.
- [ ] Any artifact reported as frozen was confirmed hash-stable across spaced passes, writer-free, and with an mtime covered by the probe that verified it.
- [ ] Occlusion is reported at two levels — rect-band overlap AND text-leaf coverage — with the `elementFromPoint` hit-test confirming z-order against both the product and the bar's subtree.
- [ ] Per-element `right > innerWidth` offenders were split into contained-by-internal-scroller vs true page overflow, and both counts reported.
- [ ] Product counts are proven rendered-and-distinct, not just the `querySelectorAll().length` (repeated coordinates checked for grid siblings).
- [ ] Every per-child metric (font-size, line-height, white-space) was read from that child's own `getComputedStyle`, not an ancestor's.
- [ ] The overflow conclusion was reproduced in a plain, non-emulated context.
- [ ] Each stated gate condition has an explicit PASS/FAIL computed from the requester's own expression, with raw numbers alongside.
- [ ] The report separates measured facts from unverified fidelity caveats.
- [ ] Any flow/fold budget was proven by closure (chain residual `0.00`); a non-closing model was either refined or reported as unresolved instead of published.
- [ ] Every requested selector's computed `display` was checked, and hidden ones reported as contributing no budget.
- [ ] Outputs and raw evidence JSON live in the task workspace; scratch temp files cleaned.
- [ ] If a browser was attached to rather than launched, its identity, the target counts before/after, and the targets created and closed were reported, and the process was left running.
- [ ] Occlusion was confirmed by hit-test at the element centre AND in the covered band / at its interactive children, with the covered pixel band and percentage reported.
- [ ] Whether the revision loads webfonts was established before fold numbers were called device-faithful.
- [ ] Any palette gate was scored against every background token, reporting the minimum ratio and the page's current tokens.
- [ ] For a variant ladder: the computed value of every property the override touches was dumped per variant, per-declaration no-ops were named, and the per-step delta arithmetic closes to the observed move.
- [ ] No override silently truncates content: any `nowrap`+`ellipsis` in a variant had its clipped pixels measured and reported beside the height gain.
- [ ] Both occlusion columns were reported per variant (fold count AND clear-of-fixed-strip count), and the one the gate needs was named.
- [ ] Alpha composites were computed against the backdrop read from the source, with the requested base cross-checked when it disagreed.
- [ ] Any probe field constant across all elements and variants was investigated as a probe bug before it was reported as a finding.

## Support files

- `references/dom-measurement-probes.md` — probe JS recipe, per-element box shape, visibility predicates, context parameter sets, and the override-cascade ladder recipe (copy generation, self-echoing style injection, per-step delta attribution).
- `scripts/png_stats.py` — stdlib PNG decoder: dimensions and distinct-colour count for the blank check.
- `scripts/geometry_probe.py` — end-to-end probe harness (mobile emulated + plain cross-check + desktop, fold buckets, contained-overflow analysis, fixed/sticky census, parent/child card audit, optional gate verdict). Run it instead of hand-writing the harness for each job.
- `scripts/fold_budget_probe.py` — fold-budget harness: per-viewport document metrics plus a per-selector ancestor-chain flow decomposition with a closure check. Prints the addends and `residual`; residual must be `0.00` before the number is publishable.
- `scripts/child_style_probe.py` — per-child computed style + Escape/line-box audit: each child's own `font-size`/`line-height`/`white-space`, escape past the parent box per side, and `Range` line counts. Run it for "does this row still wrap / does a child escape its box / did the font change land" questions.
- `scripts/occlusion_probe.py` — fixed/sticky bar occlusion in depth: rect-band overlap vs text-leaf coverage, `elementFromPoint` hit-test against the bar subtree, and end-of-scroll tail reachability. Run it alongside `geometry_probe.py` whenever the page has a fixed bar or the requester asks whether a bar hides product content.
- `scripts/cdp_measure.mjs` — Playwright-free CDP harness: attaches to (or launches) a headless Chrome, opens one target per viewport with `Emulation.setDeviceMetricsOverride` + UA override, samples the probe at increasing settle delays, closes every target it opened, and prints the browser identity plus target counts. Run it when no interpreter has Playwright; pass a `probe.js` expression file to reuse the probe JS from `references/dom-measurement-probes.md`.
- `scripts/contrast_audit.py` — WCAG contrast gate: scores a candidate palette against every background token, ranks by minimum ratio, and reports the best single value.
- `references/webfont-selfhost-assets.md` — acquiring Google Fonts `css2` stylesheets and woff2 files for self-hosting: the UA that returns woff2 instead of TTF, axis syntax, per-subset variable/static file counts, URL dedupe, HEAD byte budgeting, and the report shape FRAME needs.
