---
name: responsive-experience-engineering
description: Engineer intentional responsive compositions across phone, tablet, desktop, and ultrawide layouts.
version: 2.0.0
metadata:
  hermes:
    tags: [responsive, css, layout, frontend]
    category: custom
---

# Responsive Experience Engineering

## Canonical widths

For major pages, account for approximately:
320, 360, 390, 430, 768, 1024, 1280, 1440, 1920, 2560 pixels.

## Boundary testing

Discover meaningful project breakpoints and inspect around each boundary at B-1, B, B+1 when the change is material.

## Intentional adaptation

Responsive behavior may change navigation, ordering, density, grouping, chart strategy, table strategy, interaction patterns, and maximum content width. Do not merely shrink fonts and stack every column.

## Failure modes

Look for horizontal overflow, text collisions, clipped charts, oversized dialogs, awkward tablet no-man's-land, ultrawide stretching, fixed-height truncation, mobile controls below thumb reach, and inconsistent breakpoint transitions.

## Multi-shape rows and grid auto-placement

When one row class is reused with a varying number of cells (icon or none, one trailing cell or two), declare an explicit `grid-template-columns` for every shape.

- Auto-placement drops an unpaired trailing cell into the flexible track: with `auto minmax(0, 1fr) auto` and no icon child, the action lands in the `1fr` track, which absorbs the row and leaves the trailing `auto` track at 0. A `white-space: nowrap` label then overflows and is cut by the container's `overflow: hidden`.
- The rendered symptom is a truncated label, not a scrollbar. Two-cell progress/action rows are the common victim, and a single shared row class means the defect appears on every surface that shape is used on.
- Shape-scope the rule so exactly one template applies per shape, e.g. `.row:not(:has(.row-icon)):not(:has(> :nth-child(3))) { grid-template-columns: minmax(0, 1fr) auto; }`, placed with the other shape rules so a broader shape rule can never win. Keep icon rows (`auto minmax(0, 1fr) auto`) and 4-cell rows on their existing templates.
- Size trailing action/meta cells with `auto` (content) and reserve `minmax(0, 1fr)` for the flexible content cell. Re-verify at the narrowest canonical width, where the flexible track is smallest.

A collapsed track is invisible to overflow checks: the document does not scroll and no scrollbar appears, so `scrollWidth <= innerWidth` still passes. Measure the trailing cell's own geometry and its rendered glyphs — not the cell box alone.

## Measuring a row-shape claim

- Measure rendered text, not the cell box. A collapsed track yields a 0px-wide cell whose `right` still lands inside the row, so a naive `cell.right <= row.right` assertion passes on the broken layout. Wrap the cell's contents in `document.createRange()` + `selectNodeContents()` and assert both `text.width > 0` and `text.right <= row.right + 0.5`.
- Prove an assertion can fail before trusting it to pass. Re-inject the pre-fix rule at runtime (`page.addStyleTag({ content: "<old selector> { <old template> !important" })`), measure the same element again, and require the broken state to miss the bound. If both states pass, the assertion guards nothing.
- Wait for a post-hydration element before measuring. Probes run against server HTML return `null` rects and empty node lists; wait on a role-based locator the client renders before `page.evaluate`.
- Probe text width in the app's own font before choosing a layout: append a hidden `position: absolute; white-space: nowrap` span with `font-family: inherit` at each candidate size and weight, read its width, remove it. Decide whether two labels share a line from measurement, not estimation.
- Trust measurement over a downscaled screenshot when judging an edge or gap: resampling makes a correctly inset control look flush against the container edge. Before "fixing" it, read the cell's own rect and the gap to the container edge; if the numbers are correct, the doubt was an artifact and no change is warranted.
- Assert row shape as a set of booleans from one probe: controls share a row (`abs(topA - topB) < 1`), the counter sits on its own line (`counter.bottom <= button.top`), cells are baseline-aligned (center deltas <= 1px), and each cell is inside the container. A wrap that shifts a control ~100px still passes every overflow check.

Probe recipes with runnable snippets live in `references/rendered-geometry-probes.md`.

## Control rows: counter plus paired buttons

- Fit is a measurement, not a guess: two full-width action labels at base size and `px-5` padding commonly exceed a 360px content box. Size the pair compactly on the narrowest range (`px-2 text-[13px]`) and reset upward (`sm:px-5 sm:text-base`) so mobile keeps one line at the design's normal scale on desktop.
- Two shapes, one DOM order. Mobile wants the counter on its own line with the pair below it; larger ranges want the counter between the buttons. Keep the DOM in the larger-range reading order (prev, counter, next) and move only the counter on mobile via `order-first w-full` / `sm:order-2 sm:w-auto`. Reordering the buttons with `order-*` instead would put tab order out of step with visual order. This holds only while the group is a plain flex/grid container: a plugin that inserts something sticky, fixed, or portal-based breaks it, because CSS `order` does not move that box — keep DOM order equal to visual order for any group containing such a child.
- Push the probe length past the real content while fuzzing, or the layout is never stressed. At the acceptance widths a two-digit field fits on the same row as its counter, so a medium-length value is a configuration smoke test, not an overflow check.

## Responsive overrides and the cascade

- Re-check every responsive override on a container after changing that container's own layout utility. Keeping the base utility and adding a matching `sm:` group puts both declarations in the same cascade layer, where the base one wins by order — so the small-screen override silently stops applying while the markup still reads correctly. Grep the element's own class list for the base group being duplicated before tuning any value.
- A responsive rule that appears to have no effect is usually not losing on specificity. Confirm the declaration still applies at both widths by reading the computed style for that property, then compare against the intended value; only after the declaration is confirmed live is adjusting numbers or adding specificity the right move.
- Removing a wrapper element also removes any spacing utility that was keyed to it. Re-derive the spacing from the parent's own gap or the child's margin, and prefer one owner for a gap over a wrapper that exists only to carry it.
