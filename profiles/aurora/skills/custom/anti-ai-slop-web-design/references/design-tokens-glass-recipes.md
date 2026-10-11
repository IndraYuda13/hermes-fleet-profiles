# Design Token & Glassmorphism Build Recipes

Build-time recipes for engineering modern, distinctive surfaces. (Governance gates, hard checks, and review rubric live in the other reference modules; this file covers how to construct tokens and glass correctly.)

## 1. Three-Layer Token Architecture

```
Layer 1: Primitives (raw values: colors, font sizes, spacing numbers)
   ↓
Layer 2: Semantics (intent-based: --bg-surface, --text-primary, --border-subtle)
   ↓
Layer 3: Components (scoped: --card-bg, --btn-primary-bg, --nav-glass-blur)
```

Components reference semantic tokens, semantics reference primitives; never hardcode raw values in component CSS (Gate 2 flags this as G2_TOKEN_HARDCODED).

## 2. Production CSS Token Starter

```css
:root {
  /* Spacing primitives */
  --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px;
  --space-6: 24px; --space-8: 32px; --space-12: 48px;

  /* Typography: fluid clamp scale — never raw px for text roles */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-serif: 'Newsreader', 'Playfair Display', Georgia, serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --text-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.8125rem);
  --text-sm: clamp(0.875rem, 0.825rem + 0.25vw, 0.9375rem);
  --text-base: clamp(1rem, 0.95rem + 0.25vw, 1.0625rem);
  --text-lg: clamp(1.125rem, 1.05rem + 0.35vw, 1.25rem);
  --text-xl: clamp(1.35rem, 1.2rem + 0.6vw, 1.55rem);
  --text-2xl: clamp(1.75rem, 1.5rem + 1vw, 2.125rem);
  --text-3xl: clamp(2.25rem, 1.85rem + 1.6vw, 3rem);
  --text-hero: clamp(2.75rem, 2.2rem + 2.5vw, 4.25rem);

  /* Dark semantic theme (default) */
  --bg-canvas: #090a0f;            /* deep tinted obsidian, never pure black by default */
  --bg-surface: #10121a;
  --bg-surface-elevated: #161824;
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-hover: rgba(255, 255, 255, 0.16);
  --text-primary: #f2f3f7;
  --text-secondary: #9ea3b5;
  --text-muted: #64697d;
  --accent-primary: #10b981;       /* ONE cohesive accent family, used sparingly */
  --accent-glow: rgba(16, 185, 129, 0.15);
  --radius-card: 14px;
  --radius-btn: 8px;
}
```

For light themes use soft warm off-whites (`#fcfcfd`, `#f8f9fa`) rather than sterile pure white.

## 3. Refined Glassmorphism Recipe

Naive glass (`rgba(255,255,255,0.3)` borders on high-opacity white) renders washed out and illegible. Correct recipe:

1. **Bounded blur:** `backdrop-filter: blur(12–14px) saturate(140–150%)` — more blur is GPU churn, not quality.
2. **Alpha background is mandatory:** `background: rgba(16, 18, 26, 0.65)` — blur alone is not a surface.
3. **Directional edge definition:** 1px border plus an inset highlight mimicking light from the top left.
4. **Fallback for missing support:**

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
@supports not (backdrop-filter: blur(1px)) {
  .glass-card { background: rgba(16, 18, 26, 0.95); } /* solid, not translucent */
}
```

Remember the contextual-motif rule from the universal principles: glassmorphism is a tool, not a default — unmotivated `backdrop-blur-md bg-white/5` everywhere is a hard-check failure.

## 4. Build-Time Slop Traps (the trio that ships most often)

1. **The cliché hero:** pure `#000000` void + radial violet/cyan blobs + centered headline + 3 floating pill badges. Substitute tinted obsidian, one accent family, and a composition justified by the brief.
2. **Artificial glass:** white 0.3-alpha borders, high-opacity white cards, blur without alpha background — see recipe above.
3. **Typography flaws:** body < 14px, low-contrast gray (`#666` on dark), missing proportional line-heights — use the clamp scale and keep WCAG AA contrast (hard check G2_CONTRAST_FAIL).

## 5. Pre-Handoff Checklist (build-side)

- [ ] Contrast >= WCAG AA everywhere (4.5:1 body, 3:1 large headings).
- [ ] No horizontal scrollbar at 360px viewport (fluid sizing, box-sizing discipline).
- [ ] No unmotivated AI tropes (glowing spheres, purple gradient headlines, glass everywhere).
- [ ] Interactive states explicit: hover, active, focus-visible outline, disabled.
- [ ] Typography scale via semantic variables, zero hardcoded px text units.

This checklist is the build-time mirror of the 8 hard checks; LENS verification still gates the final verdict.