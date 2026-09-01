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
