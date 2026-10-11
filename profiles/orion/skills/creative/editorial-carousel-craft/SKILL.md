---
name: editorial-carousel-craft
description: Generate editorial social carousels and visual flows.
version: 1.1.0
author: Indra Yuda (IndraYuda13), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [carousel, social-media, instagram, linkedin, twitter, threads, excalidraw, visual-craft]
    related_skills: [excalidraw, popular-web-designs]
---

# Editorial Carousel Craft

Framework and templates for generating high-craftsmanship social media carousels (Instagram, LinkedIn, X, Threads) and architectural visual flow cards.

## When to Use

- Designing swipeable carousel presentations or standalone graphic cards for Instagram, LinkedIn, Twitter/X, or Threads.
- Creating educational tech breakdowns, financial simulation cards, system design explainers, and thought leadership decks.
- Combining architectural diagrams (Excalidraw / SVG) with clean editorial typography.
- Exporting slide carousels to multi-page PDF (LinkedIn) or individual high-DPI PNGs (Instagram / X / Threads).

Don't use for:
- Video reels/shorts generation (use `auto-shorts` / `media-streaming-pipeline` instead).
- Standard single-page web landing pages.

## Platform Dimensions & Formats

| Platform | Optimal Dimensions | Aspect Ratio | Max Slides | Delivery Format |
|---|---|---|---|---|
| **Instagram / Threads** | 1080 × 1350 px | 4:5 (Portrait) | 20 | PNG / JPG slides |
| **Instagram Square** | 1080 × 1080 px | 1:1 (Square) | 20 | PNG / JPG slides |
| **LinkedIn** | 1080 × 1350 px | 4:5 (Portrait) | 20+ | Multi-page PDF (auto-renders as carousel) |
| **Twitter / X** | 1200 × 675 px / 1080 × 1080 px | 16:9 or 1:1 | 4 per tweet | PNG / JPG |

*Recommendation:* Standardize on **1080 × 1350 px (4:5)** — it occupies maximum vertical viewport screen real estate on mobile feeds across Instagram, Threads, and LinkedIn.

## The 7-Slide Narrative Architecture

1. **Slide 1: Scroll-Stopping Hook**
   - High visual contrast.
   - Large headline (36–48pt) + categorical badge + author handle.
   - Micro visual preview (e.g. mini architectural diagram or quote).
   - "Swipe →" subtle indicator.
2. **Slide 2: Context & Agitation**
   - Why the status quo is broken, or the root cause of the problem.
3. **Slide 3: Principle / Architecture Overview**
   - The big-picture mental model or high-level architecture diagram.
4. **Slide 4: Deep Dive Part 1**
   - Concrete breakdown, code snippet, or component analysis.
5. **Slide 5: Deep Dive Part 2**
   - Edge cases, anti-patterns, or implementation nuance.
6. **Slide 6: Key Takeaways & Cheatsheet**
   - 3 bullet points summarizing actionable lessons.
7. **Slide 7: High-Conversion CTA**
   - Summary card + clear call to action ("Save for later", "Repost", "Follow @handle").

## Visual Craft Rules

- **Strict Margin Grid:** Keep 80px safe area padding on all four edges so UI elements (slide counter, close button, username watermark) never collide with feed chrome.
- **Font Hierarchy:** Pair an expressive serif for hooks (`Newsreader`, `Playfair Display`) with an ultra-clean sans for body text (`Inter`, `Plus Jakarta Sans`, `Geist`). Monospace (`JetBrains Mono`) for tags, specs, and metrics.
- **Visual Restraint:** Max 2 key ideas per slide. White space / negative space is active design, not empty void.
- **Color Palettes:**
  - *Editorial Dark:* Obsidian `#0a0b0e`, Surface `#12141a`, Accent `#10b981`, Text `#f1f3f7`.
  - *Warm Newspaper:* Cream `#f9f8f4`, Card `#ffffff`, Accent `#d97706`, Text `#1c1917`.
  - *Tech Blueprint:* Deep Navy `#070e1b`, Card `#0e182c`, Accent `#38bdf8`, Text `#e0f2fe`.
- **Vertical Budget & Boundary Safety (Scripted PIL / Canvas):** When generating infographic cards or slides procedurally via PIL/Pillow or script:
  - Dynamically track `y_offset` and calculate total required height before drawing: ensure `y_final + bottom_box_height <= H - padding_bottom` (minimum 60–80px margin) so closing rows or warning strips are never clipped.
  - Constrain headline line widths: measure `font.getlength(text)` and ensure it does not exceed `W - (padding * 2)` to avoid text clipping against the right margin.
  - Perform visual verification with `vision_analyze` on every generated card to catch bottom-edge cropping, overlapping layers, or illegible text before final output.

## HTML/CSS Slide Template Engine

Slides are authored as individual semantic HTML containers and rendered at 1080×1350 via headless Chromium.

```html
<div class="slide slide-dark">
  <div class="slide-header">
    <span class="category-pill">SYSTEM ARCHITECTURE</span>
    <span class="slide-index">01 / 07</span>
  </div>
  <div class="slide-body">
    <h1 class="headline">Why Distributed Locking Breaks Under Heavy Load</h1>
    <p class="subhead">And how to prevent silent split-brain failures in PostgreSQL.</p>
  </div>
  <div class="slide-footer">
    <span class="author">@IndraYuda13</span>
    <span class="action-hint">Swipe →</span>
  </div>
</div>
```

```css
.slide {
  width: 1080px;
  height: 1350px;
  padding: 80px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: #0a0b0e;
  color: #f1f3f7;
  font-family: 'Inter', sans-serif;
  position: relative;
}
.headline {
  font-size: 56px;
  font-weight: 800;
  line-height: 1.15;
  letter-spacing: -0.02em;
  margin-bottom: 24px;
}
.subhead {
  font-size: 26px;
  color: #94a3b8;
  line-height: 1.45;
}
```
