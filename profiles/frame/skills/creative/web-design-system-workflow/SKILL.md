---
name: web-design-system-workflow
description: Modern anti-slop web design systems, typography & glass.
version: 1.0.0
author: Indra Yuda (IndraYuda13), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ui-ux, web-design, design-system, glassmorphism, typography, anti-slop]
    related_skills: [ui-ux-pro-max, popular-web-designs]
---

# Web Design System Workflow

Comprehensive workflow for engineering modern, distinctive, anti-slop web interfaces with clean typography scales, robust 3-layer design tokens, and refined glassmorphism surfaces.

## When to Use

- Building or refactoring web interfaces, design tokens, or component libraries.
- Designing high-aesthetic landing pages, dashboards, or SaaS applications.
- Establishing typographic hierarchies and font pairings with strict readability standards.
- Crafting glassmorphism, blur backdrops, and modern shader-inspired surface layers.
- Eliminating AI-generated design slop (generic purple glows on pure black, floating circles, arbitrary border radiuses).

Don't use for:
- Non-visual backend logic, raw API design, or purely command-line utilities.

## Anti-AI-Slop Visual Manifesto

Standard AI-generated web designs suffer from predictable tropes:
1. **The Cliché Hero:** Pure `#000000` void with radial gradient violet/cyan blobs, centered headline with 3 floating pill badges.
2. **Artificial Glass:** Pure white borders (`rgba(255,255,255,0.3)`) on high-opacity white cards looking washed out or illegible.
3. **Typography Flaws:** Body text under 14px with low-contrast gray (#666 on dark backgrounds), lacking proportional line heights.

### The Antidote: Tactile & Considered Craft
- **Nuanced Surfaces:** Never pure black; use deep tinted obsidian (`#07080a`, `#090a0f`, `#0d0f12`) or soft warm off-whites (`#fcfcfd`, `#f8f9fa`).
- **Subtle Layering:** Hairline borders (`1px solid rgba(255, 255, 255, 0.07)` or `rgba(0, 0, 0, 0.06)`), micro-shadows, and deliberate backdrop blurs.
- **Intentional Accent:** Single cohesive accent color family (e.g. Electric Emerald, Precision Cobalt, Warm Ochre) used sparingly for hierarchy.

## 3-Layer Token Architecture

```
Layer 1: Primitives (Raw values: colors, font sizes, spacing numbers)
   ↓
Layer 2: Semantics (Intent-based: --bg-surface, --text-primary, --border-subtle)
   ↓
Layer 3: Components (Scoped: --card-bg, --btn-primary-bg, --nav-glass-blur)
```

### Production CSS Token Starter

```css
:root {
  /* Primitive Scale */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
  --space-12: 48px;

  /* Typography Scale */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-serif: 'Newsreader', 'Playfair Display', Georgia, serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  --text-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.8125rem); /* 12-13px */
  --text-sm: clamp(0.875rem, 0.825rem + 0.25vw, 0.9375rem); /* 14-15px */
  --text-base: clamp(1rem, 0.95rem + 0.25vw, 1.0625rem); /* 16-17px */
  --text-lg: clamp(1.125rem, 1.05rem + 0.35vw, 1.25rem); /* 18-20px */
  --text-xl: clamp(1.35rem, 1.2rem + 0.6vw, 1.55rem); /* 21.6-24.8px */
  --text-2xl: clamp(1.75rem, 1.5rem + 1vw, 2.125rem); /* 28-34px */
  --text-3xl: clamp(2.25rem, 1.85rem + 1.6vw, 3rem); /* 36-48px */
  --text-hero: clamp(2.75rem, 2.2rem + 2.5vw, 4.25rem); /* 44-68px */

  /* Dark Semantic Theme (Default) */
  --bg-canvas: #090a0f;
  --bg-surface: #10121a;
  --bg-surface-elevated: #161824;
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-hover: rgba(255, 255, 255, 0.16);

  --text-primary: #f2f3f7;
  --text-secondary: #9ea3b5;
  --text-muted: #64697d;

  --accent-primary: #10b981; /* Emerald */
  --accent-glow: rgba(16, 185, 129, 0.15);
  --radius-card: 14px;
  --radius-btn: 8px;
}
```

## Refined Glassmorphism Recipe

To prevent fuzzy illegible cards or GPU churn:
1. Keep blur bounded: `backdrop-filter: blur(12px) saturate(140%)`.
2. Always pair with an alpha background: `background: rgba(16, 18, 26, 0.65)`.
3. Edge definition: Use a directional gradient border to mimic light hitting glass from the top left:
   ```css
   .glass-card {
     background: rgba(16, 18, 26, 0.65);
     backdrop-filter: blur(14px) saturate(150%);
     -webkit-backdrop-filter: blur(14px) saturate(150%);
     border: 1px solid rgba(255, 255, 255, 0.08);
     box-shadow: 0 4px 24px -1px rgba(0, 0, 0, 0.35),
                 inset 0 1px 0 0 rgba(255, 255, 255, 0.12);
     border-radius: var(--radius-card);
   }
   ```
4. Always provide an `@supports not (backdrop-filter: blur(1px))` fallback with solid opacity (`rgba(16, 18, 26, 0.95)`).

## Verification & QA Checklist

- [ ] Contrast ratio for all text elements exceeds WCAG AA (4.5:1 for body, 3:1 for large headings).
- [ ] Responsive fluid sizing on mobile (no horizontal scrollbar at 360px viewport).
- [ ] No generic AI template tropes (avoid unmotivated glowing spheres or purple gradient headlines).
- [ ] Interactive states explicit: hover, active, focus-visible outline, and disabled states.
- [ ] Typography scale implemented via semantic variables, not raw hardcoded pixel units.
