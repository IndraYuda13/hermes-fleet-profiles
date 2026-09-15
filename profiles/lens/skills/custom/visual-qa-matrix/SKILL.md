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

For art-direction claims, capture **whole viewports** at native resolution for macro hierarchy and pair them with detail crops for typography/material craft. A crop cannot prove page composition. Major responsive review must compare desktop and mobile evidence together so identity preservation is judged directly.

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

Composition: squint/grayscale hierarchy, focal order, reading/task path, section rhythm, repetition model, cardification/container debt, relationship between content and media/proof.

Typography: role contrast, measure, awkward wraps, hierarchy collapse, unreadably small secondary text, truncation of important content, numeric/data formatting, fashionable pairings that carry no product rationale.

Color/material: spatial color ownership, semantic roles, contrast anchors, material coherence, and effect budget. Glow/blur/gradient/glass/particles/3D must be bounded and purposeful; hierarchy must survive an effect-off probe.

Assets/proof: dominant visual regions should show authentic or declared synthetic product/content evidence. Flag decorative chrome, generic mockups or fake telemetry filling a region that needs real proof.

Icons: wrong semantics, family mismatch, stroke inconsistency, optical misalignment, wrong scale, weak hit targets, broken glyphs, ambiguous neighboring actions.

Components: accidental divergence, inconsistent radius/padding, broken responsive transformation, missing states.

Motion: excessive/jarring transitions, layout shift, misleading state changes, reduced-motion issues where relevant, ambient loops with no causality, identical section entrances, stable status that animates continuously.

Theme: weak contrast, invisible borders, incorrect elevation, chart/icon color failures.

Anti-generic: name the dominant shell, type treatment, palette/material treatment, repeated-container pattern and motion pattern. Run logo-off/copy-swap and effect-off probes. `>=3` unexplained category/model defaults => `GENERIC RISK: HIGH` => visual FAIL for Depth 2/3 regardless of craft score. Token-only recoloring/font/radius/effect edits do not clear a structural finding.

Responsive identity: inspect what reorders, reframes/crops, collapses/discloses, changes interaction, or simplifies. Mechanical desktop stacking is a defect when it loses the visual thesis or task priority.

## Severity

P0 — unusable/blocking/destructive/major action ambiguity.
P1 — obvious serious visual or UX defect.
P2 — meaningful polish/consistency problem.
P3 — minor refinement.

Any unresolved P0/P1 = FAIL.

## Visual Craft Score / 100

- originality / product identity: 20
- hierarchy / composition: 20
- typography: 10
- color / material / effect discipline: 10
- assets / product proof: 10
- responsive behavior: 10
- interaction / motion: 8
- state completeness: 5
- system consistency (including iconography): 4
- accessibility / usability: 3

85+ may PASS only with no unresolved P0/P1 and no `GENERIC RISK: HIGH`. Accessibility and deterministic failures remain hard gates elsewhere; a high aesthetic score cannot compensate for them.

## Remediation loop

1. capture evidence,
2. record viewport/state,
3. observed vs expected,
4. severity,
5. assign remediation to FRAME/AURORA/FORGE,
6. retest changed revision,
7. do not self-certify material changes you made yourself.
