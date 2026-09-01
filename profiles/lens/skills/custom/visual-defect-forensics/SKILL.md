---
name: visual-defect-forensics
description: Find visual bugs that escape static code review and functional tests.
version: 2.0.0
metadata:
  hermes:
    tags: [visual-debugging, ui, qa]
    category: custom
---

# Visual Defect Forensics

## Mission

Search specifically for defects that can exist while HTML/CSS/JS compiles and automated functional tests pass.

## Adversarial checks

- resize continuously through suspicious ranges rather than checking only named breakpoints,
- compare optical alignment rather than CSS numbers alone,
- inspect text at realistic and adversarial lengths,
- inspect values with extra digits/currency formatting,
- open dialogs/dropdowns near viewport edges,
- inspect sticky/fixed elements during scroll,
- inspect chart legends/tooltips at narrow widths,
- inspect dark mode for subtle border/elevation failures,
- inspect touch targets and focus rings,
- inspect browser console after interactions,
- check for layout shift and scrollbars appearing/disappearing,
- verify ultrawide max-width and information grouping,
- look for icon metaphors that are technically valid but contextually wrong.

## Reporting

Every issue should contain route/screen, viewport, state, evidence reference, severity, reproducibility, likely layer, and expected behavior.

Do not report subjective taste as P0/P1 without a user-impact reason.
