# Geometry Collision, Containment & Clipping Audit

Depth for rendered-geometry claims. Token, typography and motion assertions can all pass while boxes overlap or text is cut off; this is the assertion set that catches that. Use with §7 of SKILL.md.

Run the whole set **per visual state AND per size mode**. One mode passing says nothing about the other: the same element that renders invisibly at a small preview size can paint and be cut at full canvas size.

## 1. The audit set

Do not compare every node. Compare the elements that a human would see as boxes:

```js
const safe = document.querySelector('.safe');           // title-safe frame
const vis = el => {
  const cs = getComputedStyle(el);
  if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) return false;
  const r = el.getBoundingClientRect();
  return r.width > 0 && r.height > 0;
};
const set = [];
for (const el of safe.querySelectorAll('*')) {
  if (!vis(el)) continue;
  const tag = el.tagName.toLowerCase();
  const txt = (el.textContent || '').replace(/\s+/g, ' ').trim();
  if (!txt && tag !== 'svg' && tag !== 'canvas') continue;  // text OR graphic
  set.push(el);
}
```

## 2. Pairwise intersection

```js
const R = set.map(el => el.getBoundingClientRect());
const collisions = [], containment = [];
for (let i = 0; i < set.length; i++) for (let j = i + 1; j < set.length; j++) {
  const A = R[i], B = R[j];
  const ix = Math.max(0, Math.min(A.right, B.right) - Math.max(A.left, B.left));
  const iy = Math.max(0, Math.min(A.bottom, B.bottom) - Math.max(A.top, B.top));
  const area = ix * iy;
  if (area <= 0.5) continue;                                // sub-pixel tolerance
  const nested = set[i].contains(set[j]) || set[j].contains(set[i]);
  (nested ? containment : collisions).push({ a: set[i], b: set[j], area });
}
```

Two rules make the result trustworthy:

- **Ancestor↔descendant overlap is containment, not collision.** Without this split nearly every wrapper registers as a collision and the real finding is buried. Report the containment pair count separately so the reader can see the sets accounted for, then assert **zero** non-nested collisions.
- **Use a tolerance.** Flush borders and adjacent grid cells share an edge; a strict `area > 0` turns rounding into noise.

## 3. Positive control (mandatory)

A zero means nothing from a detector never shown to fire. Trigger it in-memory before reporting the clean run:

1. two absolutely positioned siblings that overlap;
2. one absolutely positioned element extending past the safe frame;
3. one narrow `overflow: hidden` box holding a long unbroken string.

Re-run the identical detector and assert each count *rises*:

```js
const before = await page.evaluate(DETECT);
await page.evaluate(() => { /* append the three probes into .safe */ });
const after = await page.evaluate(DETECT);
// control passes when after.collisions > before.collisions
//              && after.outside > before.outside && after.overflow > before.overflow
```

`counted_elements` rising by the injected count is the secondary check that `vis()` and the text/graphic filter are not silently dropping nodes. State the control result next to the verdict — "0 collisions, and the detector was shown to fire" is a finding; "0 collisions" alone is a claim.

## 4. Laid out vs painted

An element outside the frame is not automatically a visible defect. Compute the fraction that actually paints:

```js
const a = el.getBoundingClientRect(), s = stage.getBoundingClientRect();
const painted = Math.max(0, Math.min(a.bottom, s.bottom) - Math.max(a.top, s.top));
const pct = (100 * painted / a.height).toFixed(0);      // 0% = invisible, 40% = visibly cut
```

Report distance-outside-frame **and** painted percentage. `0%` and `40%` are different findings with different severities; the raw overflow distance cannot tell them apart. Confirm the visible case with a magnified crop of the frame edge — a clipped element proves the clip exists, which is stronger than any number.

## 5. Triage table — real defect vs criterion artifact

| Symptom | Verdict | Test |
|---|---|---|
| `scrollWidth > clientWidth` on a zero/tiny box whose label is a child | artifact (glyph overhang) | compare the **child**, not the parent; pairwise child overlaps = 0 means no visual collision |
| ancestor `scrollHeight` inflated, ancestor's own text is fine | real, but attribute it | an absolutely positioned descendant sits outside the ancestor's box and inflates its scroll size |
| absolutely positioned element past the frame at every size | real defect | offset is not in container units |
| element past the frame at one size only | responsive defect | runs one way at the preview size, another at full size |

**Absolute offsets are outside the ancestor's content flow.** A positioned badge, ack line or tooltip hanging below its parent moves neither the parent's content nor the parent's own text, yet it (a) escapes the safe frame and (b) inflates the parent's `scrollHeight`. Both symptoms usually share that one cause — report the cause once rather than as two unrelated overflow rows.

## 6. Container-unit migration tell

After a `cqw`/`cqh` refactor, an element whose offset is still written in `px` or `em` overflows by the **same absolute distance at every container size** — because a fixed `px`/`em` offset does not scale with the container. That invariance is the fingerprint of a missed conversion and is much faster than eyeballing computed values across modes.

Grep the element family for survivors after a container-unit change:

```bash
search_files pattern='(bottom|top|left|right|margin|padding)[^;]*\b(px|em|vw|vh)\b' path=<file>
```

Prefer container units (`cqw`/`cqh`) for anything that must track a resizable canvas; `vw`/`vh` track the viewport and will look correct only while the canvas happens to equal the viewport.

## 6.5 Effective touch target vs raw control box

A geometry scan that measures every `input[type=checkbox|radio]` flags every native control: a default checkbox renders ~13×13 px inside a much larger clickable label. That is a **false positive**, not a defect — the browser's hit area for a labelled control is the wrapping `<label>` (or the ancestor carrying `for`/role=switch).

Correct predicate: compute the target from the control's nearest label-like ancestor, not the control box.

```js
const box = el => {
  const lbl = el.closest('label') || (el.id && document.querySelector(`label[for="${el.id}"]`));
  const t = lbl || el;
  const r = t.getBoundingClientRect();
  return { w: +r.width.toFixed(1), h: +r.height.toFixed(1) };
};
```

Then corroborate with behaviour, not just geometry: click at the label's far edge and assert the control's `checked` flipped. Geometry says the box is big; the tap says it is *the* target. Report the effective size (`104×48`), never the raw control box, and state that the 13×13 reading was a raw-box artifact rather than a defect.

The inverse also holds: a control whose only ancestor is a 1px wrapper really is a small target — the label-wrap rule rescues genuinely-labelled controls, not bare ones.

## 7. Reporting shape

Per state, per mode: `{ counted_elements, non_nested_collisions, containment_pairs, overflow_elements, outside_safe_elements }`, then the control result, then the itemised lists. File every geometry finding with the element selector, the mode it fails in, the painted fraction, the cause, and an objective acceptance condition. Do not soften a confirmed collision or a confirmed clip into "minor spacing observation".
