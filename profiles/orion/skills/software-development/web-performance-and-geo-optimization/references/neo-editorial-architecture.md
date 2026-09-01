# Neo-Editorial Magazine & Blog Architecture Guide

This reference documents the architectural patterns developed when creating high-performance, dark-themed digital publications (like AltSpace / AfterHours.id) using full static HTML5 and Bootstrap 5.3 without database overhead.

---

## 1. Core Visual Components
- **Top News Ticker:** High-signal headline ticker placed above the sticky header for breaking news and trending dispatches.
- **Asymmetric Editorial Hero Grid:** A 7-column primary card with heavy gradient overlays paired with two 5-column stacked secondary cards.
- **Review Rating Pill / Scorecard:** Dual-purpose score widgets on both feed thumbnails and in-depth article body sections.
- **Category Filter Tabs:** Dynamic client-side filtering via data attributes (`data-filter="cat-tech"`) without page reload.
- **Reading Progress Bar:** Micro-interaction progress indicator fixed at `top:0` measuring scroll depth through `.post-content-body`.

---

## 2. GEO (AI Overview) Integration
- Direct Answer / Verdict Box placed before the main article headings.
- Native Table of Contents jump links.
- Embedded `Review` + `Article` JSON-LD schema for rich search snippets.
