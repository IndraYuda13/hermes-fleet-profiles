# Rendered-defect assertions and their power

Depth for SKILL.md sections 4 and 10. Covers proving a *rendered* defect is fixed, and proving the assertion that claims it is not tautological.

## 1. Measure glyphs, not boxes

Three levels of assertion, weakest first:

| Assertion | Passes on a clipped layout? |
|---|---|
| element is visible / `toBeVisible()` | yes |
| element box has `width > 0` | yes, when the cell is `nowrap` and overflows |
| scrollWidth <= innerWidth on the document | yes, if an ancestor is `overflow: hidden` |
| **glyph range box stays inside the row** | no -- this is the one that catches it |

```js
const range = document.createRange();
range.selectNodeContents(cell);
const text = range.getBoundingClientRect();   // actual rendered glyphs
```

`range.getBoundingClientRect()` measures the text run, so it survives a zero-width cell and an `overflow: hidden` ancestor. Compare `text.right` against the row's `row.right` with a half-pixel tolerance for subpixel layout.

## 2. Print the mechanism next to the symptom

Always capture, in the same evaluate: `getComputedStyle(row).gridTemplateColumns`, the cell's own width, and the document `scrollWidth`/`innerWidth` pair. The template string is what names the defect (`"270px 0px 0px"` is self-explanatory; "text is clipped" is not). A row that keeps an explicit trailing track resolves to two values (`"216px 66px"`); a row whose trailing cell lost its track shows a trailing `0px`.

Watch the selector specificity before blaming the template: a fix written as `:not(:has(.icon)):not(:has(> :nth-child(3)))` only covers rows with exactly two children, so sibling rows with three children and no icon are not governed by it. Scope the claim to the shapes actually asserted, and list the uncovered shapes as residual risk rather than implying whole-component coverage.

## 3. Proving an assertion is not tautological (counterfactual harness)

Structure, always in this order, all in one run:

1. measure with the fix in place -> must satisfy the assertion;
2. neutralise the fix -> assertion must fail;
3. restore the fix -> must satisfy again.

Step 3 guards against a probe that fails for an unrelated reason (bad selector, element not present), which would otherwise make step 2 meaningless.

**Neutralising a CSS fix at runtime** is preferred when the change is pure styling, because it touches no repository file:

```js
await page.addStyleTag({ content: `<selector> { grid-template-columns: <pre-fix-value> !important; }` });
await page.waitForTimeout(150);   // let the new template invalidate layout
```

This resolves the same way a pre-fix stylesheet would, so it is equivalent evidence for a grid/geometry claim. Record explicitly that the counterfactual was an override rather than a rebuilt pre-fix bundle, and note which rows it covered.

**Neutralising a non-CSS fix** (logic, data, ordering) cannot be done with a stylesheet: use a frozen checkout of the parent revision (`git archive <parent> | tar -x -C "$FROZEN"`, served on its own port) and run the same measurement there. Do not claim a stylesheet trick proved anything about non-layout behaviour.

## 4. Attribute by render window, not by wall clock

Client routing often commits the URL before the destination component has fetched its data, so an element can be legitimately absent for one render. Capture the window itself instead of guessing whether a missing element is a defect:

```js
await expect(page).toHaveURL(/new-param=/);
const duringWindow = { steps: await steps.count(), loading: await page.getByText("<loading copy>").isVisible() };
await expect(page.getByRole("heading", { name: "<phase heading>" })).toBeVisible();
const afterSettle = await read();
```

A keyed remount (`key={a + ":" + b}`) resets all local state, which is why the indicator disappears and returns. Report it as a transient window with the settling assertion attached; do not report it as a phase lacking the indicator, and do not report it as a defect unless the state is still wrong after settling.

## 5. Distinguish accessibility text from visible text

Components commonly render a visible value plus an `sr-only` prose duplicate of the same fact. `locator(...).innerText()` on the parent returns both concatenated, which breaks exact-equality assertions and hides real mismatches. Target the specific span (`span[aria-hidden]` for the visible value, `span.sr-only` for the prose) and, where both must agree, assert both separately.
