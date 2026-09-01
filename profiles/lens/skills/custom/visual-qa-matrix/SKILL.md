---
name: visual-qa-matrix
description: Audit rendered UI across viewports, states, themes, interactions, and relevant browsers.
version: 2.0.0
metadata:
  hermes:
    tags: [visual-qa, responsive, browser, ux]
    category: custom
---

# Visual QA Matrix

## Hard rule

Code correctness is not visual correctness. Visual approval requires inspection of actual rendered output.

## Evidence channels

Use available browser navigation, DOM/snapshot inspection, browser console, screenshot capture / visual analysis, and viewport/device emulation. Report exactly which evidence channel was actually used.

## Canonical viewport matrix

| Class | Width × Height |
|---|---|
| Compact phone | 320×568 |
| Small phone | 360×800 |
| Modern phone | 390×844 |
| Large phone | 430×932 |
| Tablet portrait | 768×1024 |
| Tablet landscape | 1024×768 |
| Laptop | 1280×800 |
| Desktop | 1440×900 |
| Full HD | 1920×1080 |
| Ultrawide | 2560×1440 |

Not every trivial change needs all ten; major pages/final release review do.

## Breakpoint boundary testing

Discover meaningful CSS breakpoints and inspect approximately B-1 / B / B+1 for important transitions.

## State matrix

Inspect relevant normal, empty, loading, error, single-item, dense-data, long-string, huge-number, validation, modal, dropdown, navigation, sidebar, dark/light, hover, focus, active, disabled states.

## Inspect for

Layout: overflow, clipping, unintended scroll, dead space, crowding, alignment, viewport-edge collisions, ultrawide stretching, weak mobile hierarchy.

Typography: awkward wraps, hierarchy collapse, unreadably small secondary text, truncation of important content, poor numeric formatting.

Icons: wrong semantics, family mismatch, stroke inconsistency, optical misalignment, wrong scale, weak hit targets, broken glyphs, ambiguous neighboring actions.

Components: accidental divergence, inconsistent radius/padding, broken responsive transformation, missing states.

Motion: excessive/jarring transitions, layout shift, misleading state changes, reduced-motion issues where relevant.

Theme: weak contrast, invisible borders, incorrect elevation, chart/icon color failures.

## Severity

P0 — unusable/blocking/destructive/major action ambiguity.
P1 — obvious serious visual or UX defect.
P2 — meaningful polish/consistency problem.
P3 — minor refinement.

Any unresolved P0/P1 = FAIL.

## Visual Craft Score / 100

- originality / product identity: 15
- hierarchy / composition: 15
- typography: 10
- spacing / density: 10
- responsive behavior: 15
- iconography: 10
- interaction / motion: 10
- state completeness: 5
- system consistency: 5
- accessibility / usability: 5

85+ may PASS only with no unresolved P0/P1.

## Remediation loop

1. capture evidence,
2. record viewport/state,
3. observed vs expected,
4. severity,
5. assign remediation to FRAME/AURORA/FORGE,
6. retest changed revision,
7. do not self-certify material changes you made yourself.
