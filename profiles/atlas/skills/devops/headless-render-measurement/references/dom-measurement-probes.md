# DOM measurement probes

Depth for the measuring half of a render job: the in-page JS, the box shape it
returns, and the exact visibility predicates. Number formatting is part of the
contract — the requester compares raw numbers, so round in-page and report the
same values you computed.

## Context parameters

Create a fresh context per (artefact, viewport). Do not resize one page between
captures; a resized page can retain layout state.

| Capture | viewport | device_scale_factor | other | expected PNG px |
|---|---|---|---|---|
| mobile | 390x844 | 2 | `is_mobile=True, has_touch=True` | 780x1688 |
| desktop | 1440x900 | 1 | — | 1440x900 |

Always `full_page=False` unless the requester asks for a full-page capture — a
full-page shot silently changes the output height and breaks dimension asserts.

Launch flags that matter: `--no-sandbox` (root/containers),
`--disable-dev-shm-usage` (small `/dev/shm`), `--hide-scrollbars` and
`--force-device-scale-factor=1` (deterministic layout). Because hidden
scrollbars can themselves suppress an overflow, re-check any overflow finding in
a plain context without those flags.

## The probe JS

Pass `[selector, barSelector]` (bar may be `None`) so one function serves every
artefact and can also measure an occluding fixed bar.

```javascript
([sel, barSel]) => {
  const de = document.documentElement;
  const vh = window.innerHeight, vw = window.innerWidth;
  const out = {
    scrollWidth: de.scrollWidth, innerWidth: vw, clientWidth: de.clientWidth,
    scrollHeight: de.scrollHeight, innerHeight: vh,
    bodyScrollWidth: document.body ? document.body.scrollWidth : null,
  };
  out.horizontalOverflow = de.scrollWidth > vw;
  out.overflowPx = de.scrollWidth - vw;

  const els = Array.from(document.querySelectorAll(sel));
  const boxes = els.map((el, i) => {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return {
      i,
      top: +r.top.toFixed(2), bottom: +r.bottom.toFixed(2),
      left: +r.left.toFixed(2), right: +r.right.toFixed(2),
      h: +r.height.toFixed(2), w: +r.width.toFixed(2),
      display: cs.display, visibility: cs.visibility, opacity: cs.opacity,
      offsetParentNull: el.offsetParent === null,
      clientRects: el.getClientRects().length,
    };
  });

  out.selector = sel;
  out.count = els.length;
  out.firstTop = boxes.length ? boxes[0].top : null;
  out.firstBottom = boxes.length ? boxes[0].bottom : null;
  out.firstBox = boxes.length ? boxes[0] : null;
  // Skill-default predicate (ignores elements scrolled ABOVE the viewport):
  out.fullyVisible = boxes.filter(b => b.top < vh && b.bottom <= vh);
  out.fullyVisibleCount = out.fullyVisible.length;
  // Requester-stated variant top >= 0 && bottom <= vh. Report BOTH; they
  // differ only for elements fully above the fold.
  out.fullyVisibleTopZero = boxes.filter(b => b.top >= 0 && b.bottom <= vh).length;
  out.partial = boxes.filter(b => b.top < vh && b.bottom > vh).length;
  out.belowFold = boxes.filter(b => b.top >= vh).length;
  out.anyRightBeyondViewport =
    boxes.filter(b => b.right > vw + 0.5).length;

  // Rendered-and-distinct: repeated top/bottom is a grid sibling, not a duplicate.
  out.distinctPositions = new Set(boxes.map(b =>
    `${Math.round(b.top)}|${Math.round(b.bottom)}|${Math.round(b.left)}`)).size;
  out.renderedCount = boxes.filter(b =>
    b.display !== 'none' && b.visibility !== 'hidden' && parseFloat(b.opacity) > 0 &&
    !b.offsetParentNull && b.clientRects > 0).length;

  // Occlusion by a fixed/sticky bar. A tile can be inside the fold AND covered.
  out.bar = null; out.barOverlapIdx = [];
  if (barSel) {
    const be = document.querySelector(barSel);
    if (be) {
      const br = be.getBoundingClientRect();
      const bcs = getComputedStyle(be);
      out.bar = {
        sel: barSel, top: +br.top.toFixed(2), bottom: +br.bottom.toFixed(2),
        left: +br.left.toFixed(2), right: +br.right.toFixed(2), h: +br.height.toFixed(2),
        position: bcs.position, zIndex: bcs.zIndex,
      };
      // BOTH axes: a vertical-band-only test is valid only for a full-width bar.
      out.barOverlapIdx = boxes
        .filter(b => !(b.bottom <= out.bar.top || b.top >= out.bar.bottom ||
                       b.right <= out.bar.left || b.left >= out.bar.right))
        .map(b => b.i);
      // The actionable number: fold-visible AND covered by the bar.
      out.foldVisibleThenOccluded = boxes
        .filter(b => b.top >= 0 && b.bottom <= vh)
        .filter(b => out.barOverlapIdx.indexOf(b.i) !== -1)
        .map(b => b.i);
    } else {
      out.bar = { sel: barSel, found: false };
    }
  }

  out.boxes = boxes;
  return out;
}
```

Call it with the requested selector, the bar selector (or `None`), plus any
redundant selector worth cross-checking:

```python
probe = page.evaluate(PROBE_JS, ['.row', None])
buy_rows = page.evaluate(PROBE_JS, ['.row:has(.buy)', None])
```

## Visibility predicates

The three buckets, using `vh = window.innerHeight`:

| Bucket | Predicate | Meaning |
|---|---|---|
| fully visible | `top < vh && bottom <= vh` | Whole element fits the first viewport. |
| partial | `top < vh && bottom > vh` | Starts in view, clipped by the fold. |
| below fold | `top >= vh` | Not in view at all. |

`top < vh && bottom <= vh` — not `bottom <= vh` alone. An element entirely above
the viewport would satisfy the weaker test, and the pair of predicates keeps the
three buckets mutually exclusive and total (`sum == count`).

When the requester states their own predicate (e.g. `top >= 0 && bottom <= vh`),
compute it verbatim as the headline answer and the default alongside; at
scroll-top the two agree, so printing both is cheap and removes the ambiguity.

## Occlusion by a fixed/sticky bar

"Fully visible in the first 844px" is a fold test, not an occlusion test. A
bottom action bar (`position: fixed; bottom: 0`) or a sticky header can sit on
top of a product element that passes the fold test, so the real above-fold count
is the fold-visible count MINUS the occluded ones.

- Measure the bar's own `getBoundingClientRect()`, its `position` and `z-index`,
  and report the ids of product elements whose vertical band intersects the
  bar band: `!(b.bottom <= bar.top || b.top >= bar.bottom)`.
- Report occlusion as its own row, never folded silently into the buckets.
- A fixed element's `getBoundingClientRect()` returns viewport coordinates even
  though it does not scroll, so a bar at `bottom: 0` reports `bottom == innerHeight`.

### Two levels of occlusion: rect band vs text-leaf coverage

A rect-band test answers "does this box intersect the bar", which is not the
question the requester is asking ("is product content hidden"). A card whose
box ends at 841 under a bar starting at 832 overlaps 9px while its last text
leaf ends at 825 — padding and border only. Report both counts and label them.

```javascript
([prodSel, barSel]) => {
  const R = n => +n.toFixed(2);
  const vh = window.innerHeight, vw = window.innerWidth;
  const barEl = document.querySelector(barSel);
  const bar = barEl.getBoundingClientRect();

  // Text leaves: no element children, non-empty trimmed text.
  const leaves = (root) => {
    const out = [];
    const walk = (n) => {
      for (const c of n.children) {
        const cs = getComputedStyle(c);
        if (cs.display === 'none' || cs.visibility === 'hidden') continue;
        if (c.children.length === 0) {
          const t = (c.textContent || '').trim();
          if (t) { const r = c.getBoundingClientRect();
            if (r.height > 0) out.push({ tag: c.tagName,
              cls: (c.className || '').toString().slice(0, 40), text: t.slice(0, 40),
              top: R(r.top), bottom: R(r.bottom) }); }
        } else walk(c);
      }
    };
    walk(root);
    return out;
  };

  const rows = Array.from(document.querySelectorAll(prodSel)).map((el, i) => {
    const r = el.getBoundingClientRect();
    const lv = leaves(el);
    const under = lv.filter(l => !(l.bottom <= bar.top || l.top >= bar.bottom));
    return { i, top: R(r.top), bottom: R(r.bottom),
      foldVisible: r.top >= 0 && r.bottom <= vh,
      rectOverlapPx: R(Math.max(0, Math.min(r.bottom, bar.bottom) - Math.max(r.top, bar.top))),
      contentBottom: lv.length ? Math.max(...lv.map(l => l.bottom)) : null,
      contentUnderBar: under.map(u => `${u.tag}.${u.cls}"${u.text}"@${u.top}-${u.bottom}`) };
  });

  return { vh, vw,
    bar: { top: R(bar.top), bottom: R(bar.bottom), h: R(bar.height),
           position: getComputedStyle(barEl).position, zIndex: getComputedStyle(barEl).zIndex,
           background: getComputedStyle(barEl).backgroundColor },
    rows,
    foldVisibleIdx: rows.filter(r => r.foldVisible).map(r => r.i),
    foldVisibleRectOverlap: rows.filter(r => r.foldVisible && r.rectOverlapPx > 0).map(r => r.i),
    foldVisibleContentCovered: rows.filter(r => r.foldVisible && r.contentUnderBar.length > 0)
                                  .map(r => r.i) };
}
```

`foldVisibleRectOverlap` non-empty with `foldVisibleContentCovered` empty is the
signature of a bar clipping padding, not content. Report it that way.

### Hit-test oracle for stacking

Band arithmetic has no notion of z-order or opaque covering. Confirm every
occlusion finding against `document.elementFromPoint`, which returns the actual
topmost element. Probe the center plus four inset corners; the element counts as
unoccluded when every probed point resolves to itself or a descendant.

```javascript
const within = (root, el) => !!root && (root === el || root.contains(el));
const barEl = document.querySelector(barSel);
const atPoint = (els, x, y) => {
  const el = document.elementFromPoint(x, y);
  if (!el) return { tag: null, ownerIdx: -1, inBar: false };
  return { tag: el.tagName, cls: (el.className || '').toString().slice(0, 40),
           ownerIdx: els.findIndex(e => within(e, el)),
           inBar: within(barEl, el) };
};
// occluded  <=> valid > 0 && selfHits < valid
const occlusion = boxes.map(b => {
  const cx = (b.left + b.right) / 2, cy = (b.top + b.bottom) / 2;
  const ix = Math.min(12, b.w / 4), iy = Math.min(12, b.h / 4);
  const pts = [[cx, cy], [b.left + ix, b.top + iy], [b.right - ix, b.top + iy],
               [b.left + ix, b.bottom - iy], [b.right - ix, b.bottom - iy]];
  const hits = pts.map(([x, y]) => atPoint(b.el ? [b.el] : [], x, y));
  const valid = hits.filter(h => !h.offscreen).length;
  const selfHits = hits.filter(h => h.ownerIdx === b.i).length;
  return { i: b.i, validPoints: valid, selfHits, occluded: valid > 0 && selfHits < valid,
           blockedBy: hits.filter(h => !h.hitSelf).map(h => `${h.tag}.${h.cls}`) };
});
```

Resolve membership against the bar's SUBTREE, not the bar element. The topmost
hit inside a bar band is normally a `SPAN`/`SMALL` label inside the bar, so a
`el === barEl` equality test reports "not occluded" for every covered product —
a false all-clear on the exact finding the requester asked about.

### Reachability at end of scroll

A permanently overlaid page tail is a different defect from above-fold
occlusion. Scroll to the bottom and prove the last content element clears the
bar; a reserved `padding-bottom` is not by itself proof (a bar taller than the
padding still buries the tail).

```javascript
() => {
  const R = n => +n.toFixed(2);
  const de = document.documentElement;
  let prev = window.scrollY;
  window.scrollTo(0, de.scrollHeight);
  const walk = (el) => {                     // last painted element of the page
    let last = el;
    for (const c of el.children) {
      const cs = getComputedStyle(c);
      if (cs.position === 'fixed' || cs.display === 'none') continue;
      if (c.getBoundingClientRect().height > 0) last = walk(c);
    }
    return last;
  };
  const last = walk(document.body).getBoundingClientRect();
  return { maxScrollY: de.scrollHeight - window.innerHeight, scrollY: Math.round(window.scrollY),
    bodyPaddingBottom: getComputedStyle(document.body).paddingBottom,
    lastContentBottom: R(last.bottom), lastContentTop: R(last.top),
    clearanceAboveBarTop: R(window.innerHeight - last.bottom) };
}
```

Run it as a second pass: `goto` -> measure at top -> `scrollTo(bottom)` ->
re-measure. `lastContentBottom` must be less than the bar's top for the tail to
be reachable.
- The same bar also covers the LAST `barHeight` pixels of the document, which is a
  separate defect from first-viewport occlusion and invisible to the fold test.
  Measure it directly: `document.documentElement.scrollHeight`, `body`'s computed
  `padding-bottom`, and each product's absolute bottom
  (`rect.bottom + window.scrollY`). The clean result is no product inside the final
  `barHeight` band AND `padding-bottom >= barHeight`.

## Contained overflow (internal scrollers)

`body *` elements whose `right > innerWidth` are a DIFFERENT finding from
`documentElement.scrollWidth > innerWidth`. Walk each offender's ancestors for a
computed `overflow-x` (or shorthand `overflow`) that is not `visible`; the first
such ancestor is the scroller that contains it by design.

```javascript
() => {
  const vw = window.innerWidth;
  const offenders = [];
  document.querySelectorAll('body *').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.right <= vw + 0.5) return;
    let scroller = null, p = el.parentElement, hops = 0;
    while (p && p !== document.body && hops++ < 12) {
      const cs = getComputedStyle(p);
      if (cs.overflowX !== 'visible' || cs.overflow !== 'visible') {
        scroller = { tag: p.tagName, cls: (p.className || '').toString().slice(0, 40),
                     overflowX: cs.overflowX };
        break;
      }
      p = p.parentElement;
    }
    offenders.push({ tag: el.tagName, cls: (el.className || '').toString().slice(0, 40),
      left: +r.left.toFixed(2), right: +r.right.toFixed(2),
      containedBy: scroller, pageOverflow: scroller === null });
  });
  return { innerWidth: vw, scrollWidth: document.documentElement.scrollWidth,
    horizontalOverflow: document.documentElement.scrollWidth > vw,
    offenderCount: offenders.length,
    pageOverflowCount: offenders.filter(o => o.pageOverflow).length,
    offenders: offenders.slice(0, 40) };
}
```

Report it as: document overflow yes/no, then `offenderCount` / `pageOverflowCount`
and the containing scroller for each. All offenders contained and zero document
overflow = clean; saying otherwise misdirects the fix.

## Fold budget (flow sum to an element's top)

"Running sum of (height + vertical margins) from document top to the selector's
top" is not computable as a flat census: the DOM nests, so summing every element
above a point adds each ancestor on top of its own descendants and overshoots by
hundreds of pixels (measured residuals of -195 to -1049 on a page whose true
budget to the first tile was 442.06). Two models exist; only the second is a
budget.

Model A, flat census — INVALID for a nested DOM, keep only as a labelled upper
bound: collect every non-inline element above the point and sum `height +
marginTop + marginBottom`. Report it as a census, never as the budget.

Model B, ancestor-chain decomposition — the budget. Walk from the element up to
`<html>`; at each level add the in-flow preceding siblings' `height + marginTop +
marginBottom`, the parent's flex/grid `gap`, the parent's leading `padding-top +
border-top`, and finally the element's own `margin-top`. Then assert closure.

```javascript
(sel) => {
  const q = v => Math.round(v * 100) / 100;
  const absTop = el => { let t = 0, n = el;
    while (n) { t += n.scrollTop || 0; n = n.parentElement; } return t; };
  const el = document.querySelector(sel);
  const parts = []; let sum = 0, n = el;
  while (n && n.parentElement) {
    const p = n.parentElement, pc = getComputedStyle(p);
    const sibs = Array.from(p.children), idx = sibs.indexOf(n);
    for (const s of sibs.slice(0, idx)) {
      const sc = getComputedStyle(s);
      if (sc.display === 'none') continue;                       // hidden rows add nothing
      if (sc.position === 'absolute' || sc.position === 'fixed') continue;
      const sr = s.getBoundingClientRect();
      const add = sr.height + (parseFloat(sc.marginTop) || 0) + (parseFloat(sc.marginBottom) || 0);
      if (add) { sum += add; parts.push(`${s.tagName}.${((s.className||'')+'').trim().split(' ')[0]} +${q(add)}`); }
    }
    const gap = parseFloat(pc.gap) || 0;                          // no rect, no margin
    if (gap && idx > 0) { sum += gap; parts.push(`${p.tagName}[gap] +${q(gap)}`); }
    const lead = (parseFloat(pc.paddingTop) || 0) + (parseFloat(pc.borderTopWidth) || 0);
    if (lead) { sum += lead; parts.push(`${p.tagName}[padTop+border] +${q(lead)}`); }
    n = p;
  }
  const own = parseFloat(getComputedStyle(el).marginTop) || 0;
  if (own) { sum += own; parts.push('SELF.marginTop +' + q(own)); }
  const top = q(el.getBoundingClientRect().top + absTop(el));
  return { sel, top, sum: q(sum), residual: q(top - sum), parts };
}
```

Closure is the test of the model, not a formality: `residual` must be `0.00`. A
nonzero residual means an addend is missing (usually the flex `gap`, an ancestor's
own `margin-top`, or a `position: absolute` sibling that must be excluded) or one
box is counted twice — iterate until it closes, or report that selector as
unresolved. Never hand back a column whose residual you did not check: a budget
that overshoots the element it claims to budget is worse than no budget.

Traps that a rect-only sum misses:

- Flex/grid `gap` is a real addend with no rect and no margin; verify it against
  geometry rather than trusting the CSS (`help.top - (btn.top + btn.height)`
  equals the row's `gap`). Query it from the parent, not the child.
- An ancestor's own `margin-top` belongs in the budget (`.console` mt 9); its
  `margin-bottom` does not.
- In a multi-column grid or a flex row, preceding siblings from an EARLIER line
  must be replaced by that line's row pitch (line height + row-gap), not summed
  one by one — summing every preceding sibling overcounts a 3-column grid by two
  extra item heights.
- `display: none` siblings contribute nothing and their margins do not collapse
  into the gap. Verify each requested selector's computed `display` in-page first;
  three of sixteen named selectors were `none` in one measured direction, so a
  third of the budget table was structurally zero.
- An element's `getBoundingClientRect().top` grows with scroll; convert to a
  document offset with `rect.top + (sum of ancestor scrollTop)`, which also equals
  the value measured at scroll-top, so the table is viewport-independent.
- A wrapping span in an `align-items: center` flex row reports `height /
  line-height = 1.999` for two lines; get the line count from
  `Range.getClientRects()`, not from the height ratio.

## Child rect audit (card internals)

When a card is described as "restructured", audit the parent and its named
children in one pass: each rect, descendants that escape the parent box, and
pairwise overlap.

```javascript
([parentSel, childSels]) => {
  const root = document.querySelector(parentSel);
  if (!root) return { parentSel, found: false };
  const rec = el => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
    return { cls: (el.className || '').toString().slice(0, 50),
      top: +r.top.toFixed(2), bottom: +r.bottom.toFixed(2),
      left: +r.left.toFixed(2), right: +r.right.toFixed(2),
      w: +r.width.toFixed(2), h: +r.height.toFixed(2),
      display: cs.display, position: cs.position,
      overflowsViewportRight: r.right > window.innerWidth + 0.5 };
  };
  const rr = root.getBoundingClientRect();
  const children = {};
  childSels.forEach(s => { const e = root.querySelector(s); children[s] = e ? rec(e) : null; });
  const escapees = Array.from(root.querySelectorAll('*')).map(rec).filter(c =>
    c.right > rr.right + 0.5 || c.left < rr.left - 0.5 ||
    c.bottom > rr.bottom + 0.5 || c.top < rr.top - 0.5);
  const named = childSels.filter(s => children[s]);
  const overlaps = [];
  for (let i = 0; i < named.length; i++) for (let j = i + 1; j < named.length; j++) {
    const a = children[named[i]], b = children[named[j]];
    if (!(a.bottom <= b.top || a.top >= b.bottom || a.right <= b.left || a.left >= b.right))
      overlaps.push([named[i], named[j]]);
  }
  return { parentSel, found: true,
    viewport: { w: window.innerWidth, h: window.innerHeight },
    root: rec(root), children, escapees, overlaps,
    childOverflowsViewport: named.filter(s => children[s].overflowsViewportRight).length };
}
```

Overlap means overlap on BOTH axes. Two children whose vertical bands intersect
but whose x-ranges are disjoint (a text block ending at x=255 and a price column
starting at x=265) are adjacent, not overlapping. A vertical-band-only test
manufactures an overlap on every side-by-side flex/grid card layout. Likewise a
"child overflow" is a child crossing the PARENT box or the VIEWPORT edge — say
which of the two you measured.

Named children can all sit inside the card while a DESCENDANT escapes it. After
the named-child check, walk `parentSel *` and report every box crossing the
parent rect — that is where `justify-content: flex-end` on a row wider than its
column pushes a text run out of its own container:

```javascript
// descendant escape census, one level of detail deeper than named children
const rr = root.getBoundingClientRect();
const escapes = Array.from(root.querySelectorAll('*')).map(rec).filter(c =>
  c.right > rr.right + 0.5 || c.left < rr.left - 0.5 ||
  c.bottom > rr.bottom + 0.5 || c.top < rr.top - 0.5);
```

Catching this needs one more level: a child box can report `scrollWidth <=
clientWidth` while its content still paints outside, because an overflowing
flex row reports an inflated `scrollWidth` that matches its own layout, not the
scroll box. Escape-past-the-parent is the reliable signal, not scroll metrics.

**Line boxes, not element boxes, for text wrapping.** `getBoundingClientRect()`
on a wrapping text node's element returns the union of its lines, which looks
like a normal tall box. Use a `Range` over the node's contents to count lines
and get each line box; a single-glyph range rect is also how a clipped or
overhanging line is detected.

```javascript
const rg = document.createRange();
rg.selectNodeContents(el);
const lines = Array.from(rg.getClientRects());   // one rect per line box
// lines.length > 1  => the text wrapped
// compare each rect against el.getBoundingClientRect() for overflow
```

Read each child's computed style from the CHILD (`getComputedStyle(child)`), never
from a style object captured on the parent: a per-child `font-size`/`line-height`
taken from the parent's computed style silently reports the parent's value and can
make the probe look like it disproves the very edit the requester reported. Emit,
per child: rect, escape past the parent box on each of the four sides, own
`fontSize`/`lineHeight`/`whiteSpace`/`fontWeight`, `Range` line count with the line
boxes, and for the parent row `display`/`justifyContent`/`alignItems`/`gap`/
`gridColumn` — the declaration that makes a full-width row work is usually the
grid placement, which no geometry number reveals. `scripts/child_style_probe.py`
produces all of it in one pass.

## Rendered-and-distinct before you count

Consecutive elements with identical `top`/`bottom` are usually two-column grid
siblings, not double-counted elements. Before reporting a product count, prove
each element is rendered AND at a distinct position:

- `display !== 'none'`, `visibility !== 'hidden'`, `opacity > 0`,
  `offsetParent !== null`, `getClientRects().length > 0`.
- `distinctPositions` (unique rounded `top|bottom|left`) should equal `count`
  once you account for intentional grid columns; a lower number with equal
  `left` values is a real duplicate, a lower `top` with different `left` is the
  grid.
- A `querySelectorAll(sel).length` is a DOM count, not a rendered-product count.
  Say which one you reported.

## Contrast scoring against the page's own background tokens

The WCAG relative-luminance/contrast computation, for token questions ("a muted
colour that clears 4.5 on white, canvas and surface-2"). `scripts/contrast_audit.py`
wraps this: it takes `--fg` and `--bg` lists, prints every per-background ratio,
sorts by the MINIMUM ratio, and names the best single value.

```python
def lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def lum(h):
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(ch * 2 for ch in h)
    r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)

def ratio(a, b):
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)
```

Two rules make the table trustworthy:

- Score against EVERY background the token lands on, and headline the minimum.
  A candidate that clears 5.44 on `#FFFFFF` can sit at 4.70 on the tinted
  surface next to it, and an ordered list of nine candidates splits into
  pass/fail by that tinted number, not by the white one.
- Score the page's CURRENT tokens the same way. "`--muted:#6B7785` = 4.56 white
  / 4.20 canvas / 3.94 surface-2" is what turns "the muted text looks weak"
  into a fix with a target; it also shows the token is fine on white and only
  loses on the tinted surfaces.
- Only offer a two-value split (one token per surface family) when no single
  candidate clears all backgrounds. Naming a split when a single value works
  adds a token for nothing, and the split must say which background each half
  is for.

## Reporting shape

One row per (artefact, selector), every number raw:

| dir | selector | n | scrollWidth | innerWidth | h-overflow | first .top | first .bottom | fully visible | partial | below fold |
|---|---|---|---|---|---|---|---|---|---|

Report `documentElement.scrollHeight` alongside, since it tells the requester how
far the content runs past the fold. State the viewport in the table caption so a
number is never quoted without the viewport it came from.

## Selector notes

- `.row:has(.buy)` — filters in-selector. `querySelectorAll('.row')` returns all
  rows including ones with no buy button, so a "rows with a buy button" question
  answered from `.row` alone is a different question.
- `[data-testid="service-tile"]` may be present on an `<article>` that also
  carries a semantic class (`.kartu`). Census both and report when they agree;
  agreement is what makes the count trustworthy.
- A design family may implement the same product row as a `div.row` in one
  direction and a `data-testid`-tagged element in another. Zero matches for a
  requested testid is a finding about the markup, not a reason to substitute.

## Override cascade ladder (variants generated on a copy)

A ladder request ("V0 base, V1..V4 cumulatively") is measured by generating one file
per variant from a COPY, never by editing the source and never by re-rendering in
place. Hash source and copy first: identical hashes are the read-only proof, and the
copy is what the four temp variants are derived from.

Inject the override immediately before `</head>` and make the page echo it, so the
applied CSS is attested by the page rather than by your notes:

```python
BLOCK = ('<style id="trim-override">\n' + css + '</style>\n'
         '<script>console.log("[TRIM-OVERRIDE ' + tag + '] " + '
         'document.getElementById("trim-override").textContent.replace(/\\s+/g," ").trim());'
         '</script>\n')
html = base.replace("</head>", BLOCK + "</head>", 1)
assert 'trim-override' in html      # the anchor must exist and be used once
```

A `<style>` injected at end of `</head>` wins by source order against every rule of
equal specificity, INCLUDING rules inside an earlier `@media` block (media queries
add no specificity). That is what makes a mobile-only rule overridable without
touching the source. Capture the echo with `page.on("console", ...)`, dedupe per
variant, and print the deduped set as the provenance list; V0 has no override, so it
has nothing to echo — say that explicitly rather than printing an empty row.

One JS function serves the whole ladder. Derive every viewport-dependent constant
from `innerHeight` instead of hardcoding the pixel the requester computed at their
reference viewport:

```javascript
() => {
  const q = s => document.querySelector(s);
  const h = el => { const b = el && el.getBoundingClientRect(); return b ? +b.height.toFixed(1) : null; };
  const tiles = [...document.querySelectorAll('[data-testid=service-tile]')]
                  .map(e => e.getBoundingClientRect());
  const vh = innerHeight, lim = vh - 56;      // strip height, NOT the literal "788"
  return { vh, tiles: tiles.length,
    first_top: tiles.length ? +tiles[0].top.toFixed(1) : null,
    in_view: tiles.filter(b => b.top >= 0 && b.bottom <= vh).length,
    clear_strip: tiles.filter(b => b.bottom <= lim).length,
    bar: h(q('.bar')), job: h(q('.job')), console: h(q('.console')),
    catbar: h(q('.catbar')), grid: h(q('.grid')) };
}
```

A ladder is read step by step:

- The first step of a ladder labelled "trim" can be a REGRESSION. An override that
  replaces an asymmetric rule with symmetric padding adds space: `.catbar{padding:6px
  0 6px}` against a base mobile rule of `.catbar{padding:10px 0 0}` gives 12px of
  vertical padding versus 10px, so the bar height grows and everything below moves
  DOWN. `grep -o '\.catbar{[^}]*}' <file>` the rule being overridden before calling
  any step a reduction, and name the step that carried it.
- An override is proven live by a computed change (height moved), not by the style
  tag's presence. A block that matches nothing re-measures the base and reads as "no
  effect".
- `display: none` on a removed section reports height `0.0` in the census; a section
  with height 0 still exists in the DOM, so do not report its children as removed.
- Two viewports can return identical numbers for every variant; that is one layout
  branch measured twice, not two confirmations.
- A `·console·`-style class name also matches `console-row` in a grep census (
  `\b` splits on the hyphen), so confirm the element you measure in-page.

### Per-declaration proof table (required, not optional)

The echo proves the CSS was INJECTED; it does not prove each declaration did
anything. Dump the computed value of every property the override touches, for every
variant, and print it as one table. This is what catches the no-op: an override of
`border-radius:14px` against a base whose `var(--r-lg)` already resolves to 14px
contributes 0.00px, and without the table it gets credited with the step's win.

```javascript
(files) => files.map(f => {
  const cs = s => { const e = document.querySelector(s);
    return e ? getComputedStyle(e) : null; };
  const b = s => { const c = cs(s); return c ? { mt: c.marginTop, pt: c.paddingTop,
    pb: c.paddingBottom, pad: c.padding, radius: c.borderRadius,
    wrap: c.flexWrap, gap: c.gap, display: c.display } : null; };
  return { file: f, job: b('.job'), console: b('.console'), catbar: b('.catbar'),
           grid: b('.grid'), help: b('.console .cta-row .help'),
           sortsel: b('.sortsel'), line1: b('.calc .line1') };
})
```

Read it in two directions: down a column to confirm the variant applied, and across
a row to see which declaration actually changed. Then close the arithmetic —
`base.top - stepA - stepB - stepC` must equal `final.top`. A cascade whose steps do
not sum to the observed move has an unmeasured addend (a margin collapse, a `gap`, a
line-height change) and the misattributed lever reaches the contract.

### Clipping check for a `nowrap`+`ellipsis` override

A trim that adds `white-space: nowrap; overflow: hidden; text-overflow: ellipsis`
buys height by discarding copy. Measure the loss; do not ship the height gain alone.

```javascript
() => {
  const q = v => Math.round(v * 100) / 100;
  const el = document.querySelector('.calc .line1');
  const cs = getComputedStyle(el);
  const r = el.getBoundingClientRect();
  const c = el.cloneNode(true);                       // off-flow natural width
  Object.assign(c.style, { position: 'absolute', visibility: 'hidden',
    whiteSpace: 'nowrap', width: 'auto', maxWidth: 'none', overflow: 'visible' });
  document.body.appendChild(c);
  const natural = c.getBoundingClientRect().width;
  c.remove();
  return { text: el.textContent.trim(), boxW: q(r.width), naturalW: q(natural),
    clippedPx: q(Math.max(0, natural - r.width)), clipped: natural > r.width + 0.5,
    overflow: cs.overflow, textOverflow: cs.textOverflow, whiteSpace: cs.whiteSpace };
}
```

Off-flow clone is the method: an in-flow `scrollWidth` on a nowrap box reports the
content width, but the clone gives the NATURAL width at unconstrained size, which is
what "how much did we cut" means. Report `clippedPx` per affected element, and check
the shipped `font-size` too — a mobile rule lowering it to 13.5px shrinks the natural
width and understates what a wider viewport would lose.

### Two occlusion columns per variant

A variant can raise the fold-visible count while leaving the count that matters flat,
because the newly-visible elements render under a fixed bottom strip. Emit BOTH per
variant and per viewport:

```javascript
() => {
  const tiles = [...document.querySelectorAll('[data-testid=service-tile]')];
  const s = document.querySelector('.sess').getBoundingClientRect();
  return tiles.map((e, i) => {
    const r = e.getBoundingClientRect();
    const inFold = r.top >= 0 && r.bottom <= innerHeight;
    return { i, top: +r.top.toFixed(2), bottom: +r.bottom.toFixed(2), inFold,
      overlapPx: inFold ? +Math.max(0, Math.min(r.bottom, s.bottom)
                                  - Math.max(r.top, s.top)).toFixed(2) : null,
      clearOfStrip: r.bottom <= innerHeight - s.height };   // relative, never the literal
  });
}
```

Report `inFoldIdx`, `stripOccludedIdx`, `clearOfStripIdx` and the band pixels per
variant. "Raised 4 -> 6 fully visible, strip-clear still 4/4" is the finding; a single
fold column reads as a clean win.


## Determinism

- `page.goto(url, wait_until="load")`, then `await document.fonts.ready` plus a
  short settle delay before measuring or capturing. Measuring mid-layout yields
  numbers nobody can reproduce.
- Re-running the whole harness should reproduce identical geometry. If it does
  not, the artefact has time- or random-dependent layout and that belongs in the
  report.
- Hash inputs before and after; a geometry number is only evidence for the
  revision it was measured from.
- **Hash again immediately before and after EVERY pass, not once per job.** A
  requester iterating on the mockups can rewrite a file between the start of your
  run and its end. If a hash moves, the pass is invalid: discard it, re-run
  against the frozen revision, and lead the report with a revision-churn warning
  naming the superseded and current hashes. Otherwise you hand back two
  inconsistent number sets and a verdict computed from a file that no longer
  exists.
- End the report by stating the freeze expectation: these numbers are evidence
  for this exact revision and expire the moment the file is edited again.
- **Prove webfont independence, or admit it is missing.** `grep -c
  'fonts.googleapis\|@font-face\|@import' <file>` plus in-page
  `document.fonts.status` and `[...document.fonts].length`. Zero refs with an
  empty `FontFace` set means the geometry does not depend on the shipped family
  and will not shift when the CDN is blocked; a file that references a CDN
  family measures the FALLBACK when it is offline, which is a different layout
  from the one users get. Say which one the revision is.
- **Sample at increasing settle delays when you cannot await
  `document.fonts.ready`.** Re-evaluate the same metric at ~1s / 2.5s / 5s /
  8s and report a value only after two consecutive samples agree; a metric that
  keeps moving is a layout that depends on load timing, and one sample is an
  arbitrary point inside that drift. Re-running the full harness later must
  reproduce the same numbers.
