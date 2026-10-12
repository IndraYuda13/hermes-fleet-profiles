# Motion & Cascade Metrology Recipes

Depth for Gate 2/3 claims that a single reading cannot settle. Use with §7 of SKILL.md.

## 1. Peak-vs-instant animation sampling

A reading taken at a fixed delay after a trigger measures the sampling delay, not the motion. Animations that finish in ~500 ms read `0` at 900 ms — an unremarkable result that looks like a pass.

```js
await page.locator(TRIGGER).click();
const series = [];
const t0 = Date.now();
while (true) {
  series.push({ t: Date.now() - t0,
    running: await page.evaluate(
      () => document.getAnimations().filter(a => a.playState === 'running').length) });
  if (Date.now() - t0 >= 900) break;
  await page.waitForTimeout(50);
}
const peak = Math.max(...series.map(s => s.running));
```

Report `peak` **and** the time series. When the contract states a ceiling (e.g. "<=4 running per screen"), the peak is the value to compare against it; a trailing `0` is context, not the result.

Corollary: because `getAnimations()` also keeps finished entries, `running` drops to 0 while `total` stays constant. Reporting `total` as if it were live motion is wrong — filter on `playState`.

Under a reduced-motion toggle, sample the same way from the same trigger so the two runs are comparable, and confirm the toggle changed the frame (byte-compare the two PNGs — identical bytes mean the control was a no-op).

## 1a. Distinct animated elements vs animations

Two different units, two different numbers for the same moment. When the contract caps concurrent *elements*, count that unit:

```js
const n = await page.evaluate(() => {
  const els = new Set();
  for (const a of document.getAnimations()) {
    if (a.playState === 'finished' || a.playState === 'idle') continue;
    const t = a.effect && a.effect.target;   // a DOM node
    if (t) els.add(t);                        // Set dedupes multi-animation elements
  }
  return els.size;
});
```

`getAnimations().filter(a => a.playState === 'running').length` is the *animations* unit and reads higher whenever one element carries several animations. Pick the unit the stated ceiling is written in; mixing them silently converts a breach into a pass.

Because `fill: both` paints the from-state during a delay, the app may deliberately count delay-phase entries as "animated". Read the artifact's own counting function from source and replicate its predicate exactly rather than choosing your own, then report your number, its number, and a match flag. Agreement corroborates the readout; disagreement is a finding about the readout. Scope the claim to the light DOM: `getAnimations()` does not traverse shadow roots.

**A readout changes format as state settles.** An immediate string written on render (`momen X · kelas Y · gerak nyala · elemen bergerak N`) is commonly replaced by a measured string written once the burst ends (`puncak ... · tata letak tetap · will-change ... · tenang N`). Under reduced motion the page often returns early and keeps the immediate form permanently. So the same readout reads differently at 300 ms and at 1300 ms. Quote it at a stated moment, and know which form your moment lands in before presenting a string as the settled measurement — a short form captured at 300 ms is not a settled report.

## 1b. Recording a short lifecycle in-page (rAF series, not a timed read)

A probe that sleeps a fixed delay and then reads the node ONCE is racing a wall-clock sleep against the artifact's own JS timer. Concretely: the artifact adds `.is-leaving` at t+2600 and removes the node at t+2800, so a read landing past t+2800 finds nothing, records `null`, and the assertion fails — or fails only sometimes. The failure is a race, never a property of the artifact. Record the whole lifecycle *inside the page* and assert on the series:

```js
await page.evaluate(() => {
  window.__log = [];
  const tick = () => {
    const n = [...document.querySelectorAll('.toast-message')].pop();   // LAST match, not first
    window.__log.push(n
      ? { t: performance.now(), present: true, cls: n.className,
          opacity: getComputedStyle(n).opacity, transform: getComputedStyle(n).transform }
      : { t: performance.now(), present: false });
    if (window.__log.length < 600) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
});
```

Derive the boundaries from the series: **enter** = first frame the node exists; **settled** = last frame while `.is-in` holds; **exit** = first frame during `.is-leaving` with `0 < opacity < 1`.

- **Take a strictly interior frame, not the first frame in the new class.** The first `.is-leaving` frame still carries the settled value (opacity ≈ 0.98 in a 200 ms ease) because the transition starts from the settled `1`. Sampling it is a boundary sample, not mid-flight; the strict `0 < opacity < 1` predicate is what makes the claim mean mid-transition.
- **Scope an instant/neutralised assertion to the transition window, never the whole presence window.** Under reduced motion the artifact legitimately holds `opacity: 0` on present frames that are NOT an enter fade: the frame inserted *before* the `.is-in` class lands (the prototype adds it one frame after insertion) and the neutralised `is-leaving` exit frames. So a predicate like "every present frame was opaque" evaluated over the whole presence window is **unsatisfiable by construction** — it can never pass no matter how correct the artifact is, and it will fail identically in every repeat (a deterministic mis-calibration, see §10 of `run-evidence-provenance.md`, not a flake and not a defect). The property that actually holds for an instant enter is **anchored on `.is-in`, not on any present-window**: the strictly-interior enter sample is `None` (no `0 < opacity < 1` frame exists while `.is-in` held), the FIRST `.is-in` frame already reads opaque, and ZERO interior frames follow it. Do **not** re-scope to `first-present -> settled`: that window still contains the pre-`.is-in` insertion frame at `opacity 0`, so an all-present-opaque predicate scoped to it is unsatisfiable for the *same* reason the whole-series form is. The only frame to exclude is the insertion frame, and you exclude it **by definition** (it does not yet carry `.is-in`), never by widening or narrowing a window.
- **Count only PAINTED frames — a `[hidden]` (display:none) node reports a rest pose, not mid-flight.** When you classify a frame as mid-flight by `computedTransform !== settledTransform`, the sheet's closed/pre-open frames inject a false positive: while the node carries `[hidden]` it is `display:none`, so `getComputedStyle` returns `transform: none`, which differs from the settled matrix and satisfies the predicate. The logger started before the trigger records those hidden frames, so a counter that should read `0` under reduced motion reads `N>0` and a `*_no_intermediate_pose_held` assert fails — deterministically, and identically in every repeat. That is a probe mis-calibration (see §10 of `run-evidence-provenance.md`), not a defect, and not a flake. Gate every mid-flight / partial-opacity counter on a `painted` flag recorded **per frame in the same rAF tick**: `painted: !!n && n.getClientRects().length > 0 && !n.hasAttribute('hidden')`, then read `s.get('painted')` inside the count. The FIRST *painted* frame is already at the settled pose and no painted frame holds an intermediate one — that is the invariant that actually holds, and it is what the counter must measure. An opaque-looking `transform: none` on a hidden node is neither travel nor a rest pose; it is unrendered.
- **Show the re-scoped counter still FIRES, or its `0` proves nothing.** A painted-gated mid-flight counter reading `0` in a neutralised context is evidence only if the *same* counter reads `>0` where travel genuinely occurs. Quote both populations side by side from the identical recording path — e.g. `sheetMidFlightFrames = 15 / 11 / 15` across the animated contexts versus `0 / 0` under reduced motion — and state plainly that the reduced `0` is a measurement, not a blanket-zeroed dead counter. Without the animated-context positive control, a `*_no_intermediate_pose_held` pass is indistinguishable from a counter accidentally short-circuited to always zero, which is the exact failure mode a gate on that counter is meant to catch. This is the motion-counter instance of SKILL.md §6's 'prove the detector fires' rule.
- **Prove a re-scoped predicate is satisfiable before trusting it.** Replay the recorded series against BOTH the old and the new form and report that one is deterministically `False` and the other `True` on the *same* frames. A re-scope that is also `False` on the same series renamed the defect rather than fixing it, and it will fail identically in every repeat. Also diff the per-context field the assert consumes (`toastFirstIsInOpaque`, `toastInteriorFramesAfterIsIn`): a renamed key that reads a stale or absent field passes vacuously. When you inherit a fix written by the same author as the assert, treat a green result as unverified until you have replayed this both-forms check on the recorded data.
- **Pick the last match, not the first.** The first `.toast-message` in the layer is the previous toast; sampling it reports a settled `opacity=1, translate=0` with a live `dur`, which reads as "already finished entering" and mis-calibrates the probe.
- **Guard the series, not the boolean.** Assert `exitFrames >= 2` AND that removal was observed in the log, so a degenerate run (recorder never started, window collapsed) cannot pass silently.
- **Report the counts as the evidence.** `exitFrames` / `presentFrames` / `logFrames` per context give a distribution with a visible margin; the pass/fail boolean does not. See the margin rule in SKILL.md §7.
- **`Emulation.setPlaybackRate` slows the CSS timeline but NOT JS timers.** A removal driven by `setTimeout` still fires on the original wall clock, so playback rate cannot slow-motion a JS-scheduled transition. Poll for the artifact's own trigger (`waitForFunction` on the `.is-leaving` class) and screenshot from there (~80 ms inside the window) instead of sleeping a fixed offset. Record the trigger-observed and live-node flags plus the shot's opacity/transform in the report, so a reader can confirm the shot is neither settled nor already flushed.

External interval polling (§1) remains correct for a long multi-element burst; the in-page rAF recorder is for a single element's short lifecycle where per-frame resolution matters and the node can be gone between two polls.

## 2. Computed value contradicts the declared token

A demo stage nested inside a documentation wrapper inherits the wrapper's rules. A wrapper rule like `.doc h1 { font: 800 30px/1.15 var(--font-guru) }` (specificity 0,1,1) outranks a component rule like `.question { font: 700 var(--board-question)/1.2 ... }` (specificity 0,1,0), so the rendered text silently takes the wrapper's size and family while the token still reads its declared value.

Attribute it, do not just report the delta:

```js
const cdp = await ctx.newCDPSession(page);
await cdp.send('DOM.enable'); await cdp.send('CSS.enable');
const { root } = await cdp.send('DOM.getDocument', { depth: -1 });
const { nodeId } = await cdp.send('DOM.querySelector', { nodeId: root.nodeId, selector: SEL });
const { matchedCSSRules } = await cdp.send('CSS.getMatchedStylesForNode', { nodeId });
// matchedCSSRules is already in cascade order: name each selector + its font/size props.
```

Then falsify in memory — confirm the claim is about the cascade and not about the value itself:

```js
const experiment = await page.evaluate((sel) => {
  const el = document.querySelector(sel), parent = el.parentElement;
  document.body.appendChild(el);            // move out of the suspected ancestor
  const cs = getComputedStyle(document.querySelector('.question'));
  const res = { fontSize: cs.fontSize, fontWeight: cs.fontWeight };
  parent.appendChild(el);                    // restore; the file on disk is untouched
  return res;
}, STAGE_SEL);
```

A value that jumps to the declared token once un-nested proves the ancestor rule is the cause. Always disambiguate the selector first (`[...document.querySelectorAll(SEL)].map(...)`) and measure the instance that actually sits in the product surface — a same-named class in the doc chrome is a different element. State whether the failure is in the product component or in the prototype's own demo scaffolding; they dispatch to different owners.

**Viewport-relative units track the viewport, never the container.** For a token like `clamp(56px, 3.4vw, 96px)` that appears to scale with the board, read the resolved value at two container widths (or toggle the container-size mode). If both returns are identical (`0.034 × 1920 = 65.28px` at an 1138px stage *and* at a 1920px stage), the `vw` term is pinned to the viewport and the size does not actually respond to the board. Resolve custom-property expressions by probing `font-size: var(--token)` on a throwaway element; do not hand-evaluate the clamp yourself.

## 3. Capture geometry

Element screenshots are element boxes. A `.stage` clamped by an ancestor `max-width:1180px` minus padding captures at ~1140px wide even though the viewport is 1920px, and a `fullPage` capture at a 1080 viewport is as tall as the document. Report the real pixel dimensions from the file, never the requested viewport. Verify PNGs are real content, not blank, before citing them as evidence.

When the requested deliverable is a PNG at an *exact* declared size and the element's document position is fractional, capture the full page and clip at integer coordinates:

```js
const r = await page.evaluate(() => {          // document-space rect
  const b = document.querySelector(SEL).getBoundingClientRect();
  return { x: b.left + scrollX, y: b.top + scrollY, w: b.width, h: b.height };
});
await page.screenshot({ path: OUT, fullPage: true,
  clip: { x: Math.round(r.x), y: Math.round(r.y), width: 1920, height: 1080 } });
```

- `fullPage: true` is mandatory here: without it the `clip` is clamped to the viewport, so an element whose top sits below the fold (e.g. 525.75 in a 1080-tall viewport) returns a short truncated capture, not the full box.
- An element screenshot rounds the fractional box *outward*: a 1080-tall element at document y 525.75 produces a 1921px-tall PNG. Assert the returned width/height against the requested size and disclose the sub-pixel rounding applied.
- `page.screenshot({ clip })` takes page coordinates (add the scroll offsets); `elementHandle.screenshot()` does not. That is why the two methods disagree by a row — pick one and state which.

## 4. Request forensics

```js
const urls = [];
page.on('request', r => urls.push(r.url()));
// after load:
const foreign = urls.filter(u => u !== pageUrl);
```

For a `file://` document the pass case is `total === 1` and `foreign.length === 0`. Distinguish a self-contained document (no requests beyond itself) from a document whose fonts/images are simply cached — the request list answers only the former. When fonts are deliberately not embedded, say so as a scope limit rather than implying the shipped face was verified.

## 5. Deliverable identity across revisions

After a source fix, a re-run can legitimately return byte-identical PNGs. Resolve which case you are in before reporting either way:

1. **Map the changed content to your capture regions.** A string in the page's console/status bar sits outside the cropped `.stage`, so no element crop *can* change; only a capture that includes the altered region would. A cosmetic-only change (deleting dead CSS, editing a label that no deliverable renders) legitimately produces identical output.
2. **Check the capture epoch.** A full-page shot taken 300 ms into a beat sees the transient readout, not the settled one the fix touched — identical bytes for a correct reason.
3. **Confirm with one re-capture.** Write the fresh file, hash it, compare against the stored one. Equal hashes after a genuine re-render means the change is out of frame, not that the write failed.

Identical bytes are the answer only after that chain. Reporting a set of identical hashes as freshly re-rendered conceals a deliverable that does not carry the change; reporting them as stale when the chain explains them sends the owner chasing a phantom.
