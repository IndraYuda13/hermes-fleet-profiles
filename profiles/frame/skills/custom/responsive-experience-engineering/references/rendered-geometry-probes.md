# Rendered geometry probes

Playwright recipes for making a layout claim measurable before and after a fix. Run probes from a throwaway spec file (`tmp-*.spec.ts`) and delete it before the final gate run, so the gates execute on the exact deliverable revision.

## Preconditions

- Boot the real app against the project's own harness and ports; do not hand-build a page fixture. A probe that renders the real route is the only one whose numbers transfer to the shipped surface.
- Wait on a role-based locator the client renders post-hydration before any `page.evaluate`. Reading server HTML returns `null` rects, `0` widths and empty query results, which read exactly like a missing feature.
- Resize with `page.setViewportSize`, then wait briefly: layout, fonts and lazy containers settle a beat after the resize call.

## Probe: rendered text vs cell box

A collapsed grid track reports a zero-width cell. Measuring text width through a Range is what makes the defect visible:

```ts
const box = await link.evaluate((el) => {
  const cell = el.querySelector(".row-action")!;
  const range = document.createRange();
  range.selectNodeContents(cell);
  const text = range.getBoundingClientRect();
  const row = el.getBoundingClientRect();
  return { textWidth: text.width, textRight: text.right, rowRight: row.right };
});
expect(box.textWidth).toBeGreaterThan(0);
expect(box.textRight).toBeLessThanOrEqual(box.rowRight + 0.5);
```

Use this shape for the committed regression assertion. The cell box alone (`cell.getBoundingClientRect().right`) is inside the row even when collapsed, so it cannot fail on the defect it is meant to catch.

## Probe: falsify the assertion against the pre-fix rule

Before trusting a new assertion to guard anything, prove it discriminates. Measure the element in the fixed state, re-inject the old rule with `!important`, measure again, and require the broken state to miss the bound:

```ts
const fixed = await measure(page);
await page.addStyleTag({
  content: ".row:not(:has(.row-icon)):not(:has(> :nth-child(3))) { grid-template-columns: auto minmax(0, 1fr) auto !important; }",
});
const broken = await measure(page);
console.log("PROBE fixed=", JSON.stringify(fixed));
console.log("PROBE broken=", JSON.stringify(broken));
expect(broken.textRight).toBeGreaterThan(broken.rowRight + 0.5);
```

If both states satisfy the bound, the assertion guards nothing and the fix is unproven. `!important` is required because an `addStyleTag` cannot outrank the loaded stylesheet by order alone.

## Probe: text width in the app's own font

Decide fit from measurement, never from estimation. The probe runs in the document, so it inherits the loaded webfont:

```ts
const measure = await page.evaluate(() => {
  const probe = (text: string, size: string, weight: string) => {
    const span = document.createElement("span");
    span.textContent = text;
    span.style.cssText =
      `position:absolute;visibility:hidden;white-space:nowrap;font-family:inherit;font-size:${size};font-weight:${weight}`;
    document.body.appendChild(span);
    const w = span.getBoundingClientRect().width;
    span.remove();
    return Math.round(w * 10) / 10;
  };
  return { label: probe("Label sebelumnya", "16px", "600") };
});
```

Sum the labels plus `2 * padding + gap` and compare against the narrowest content box before committing to a single-row layout.

## Probe: row shape as booleans

Return the whole shape from one `page.evaluate` per width so wrap, ordering and baseline are checked together:

```ts
const center = (r: DOMRect) => (r.top + r.bottom) / 2;
return {
  sameRow: Math.abs(aRect.top - bRect.top) < 1,
  counterOwnLine: counterRect.bottom <= aRect.top + 1,
  baselineAligned:
    Math.abs(center(aRect) - center(counterRect)) <= 1 &&
    Math.abs(center(bRect) - center(counterRect)) <= 1,
  insideRow: aRect.left >= parentRect.left - 0.5 &&
    bRect.right <= parentRect.right + 0.5,
};
```

A control that wraps to the next line keeps every overflow check green while sitting roughly 100px lower, so overflow alone never covers this class of defect.

## Probe: dead space as a delta

To test whether an always-rendered empty element causes a gap, append one to the same parent and diff the parent height:

```ts
const before = root.getBoundingClientRect().height;
const el = document.createElement("p");
root.appendChild(el);
const after = root.getBoundingClientRect().height;
```

An empty element contributes nothing when the parent's `row-gap` or a sibling margin already governs the spacing, which is how a plausible culprit is ruled out instead of patched. A `space-y-*` utility keyed on `> * + *` also ignores a first child and a lone child, so margins on those elements collapse to zero.

## Probe: element inventory at a wide width

For an "element is too wide" report, list every control with its width and nearest label text at that width, plus the container width, instead of eyeballing one suspect:

```ts
[...document.querySelectorAll<HTMLElement>("input, select")].map((e) => ({
  kind: e.tagName.toLowerCase(),
  label: (e.closest("label")?.textContent ?? "").trim().slice(0, 30),
  w: Math.round(e.getBoundingClientRect().width),
}));
```

The outlier that matches the report is then identifiable by comparison rather than by inspection order.
