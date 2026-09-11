---
name: frontend-craft-and-hardening
description: Build tactile, subpixel-aligned, hardened web interfaces.
---

# Frontend Craft, Mathematical Alignment & UI Hardening Standard

Comprehensive engineering rules, subpixel layout invariants, interactive tactile patterns, and mobile GPU hardening for building production web interfaces.

## 1. Zero-Drift Timeline & Spine Geometry Invariant
- **The Drift Anti-Pattern:** Never use negative hardcoded absolute margins (`absolute -left-[31px]`) on bullets against a parent border. Subpixel rounding, zoom (125%, 150%), and text wrapping cause visible drift.
- **Isolated 2-Column CSS Grid Spine:**
  Always isolate the vertical spine track and bullet in a dedicated fixed-width column:
  `grid grid-cols-[32px_1fr] sm:grid-cols-[36px_1fr] gap-x-4`
- **Subpixel Invariant Metrics:**
  - Concentric concentricity: $|bullet.center\_x - line.center\_x| \le 0.5\text{px}$.
  - Vertical center: $|bullet.center\_y - badge.center\_y| \le 1.5\text{px}$.

## 2. Interactive Tactile Web Craft (sceneai.art Benchmark)
- **Pointer-Following Specular Sheen:** Track pointer coordinates per card (`--pointer-x`, `--pointer-y`) via throttled pointer events. Render subtle radial sheen (`radial-gradient(circle at var(--pointer-x) var(--pointer-y), rgba(255,255,255,0.15), transparent 60%)`) with `mix-blend-mode: overlay`. Limit desktop micro-tilt to $\le 3^\circ$.
- **Synthesized Zero-Asset Web Audio Haptics (Preference Rule):**
  - Keep interactive feedback **silent by default** unless explicitly requested by the user ("suara-suara gak jelas" prevention).
  - If explicitly requested, synthesize clicks using native browser `AudioContext` (sine wave ramp 1400 Hz -> 320 Hz in 18ms, peak gain 0.045) + `navigator.vibrate?.(6)`.
- **Segmented Quick-Dial Scrubbers:** Use sliding pill indicators with `cubic-bezier(0.16, 1, 0.3, 1)` and enforce `font-variant-numeric: tabular-nums` to eliminate cumulative layout shift (CLS < 0.005).

## 3. Headless UI Visual Audit & Scroll-Reveal Standards
- **Incremental Scroll Scrubbing Protocol:** When auditing pages using `IntersectionObserver` entrance animations (`FadeInUp`), static screenshots taken immediately after `goto` capture opacity-0 elements. Playwright audit scripts must incrementally scrub the viewport (`window.scrollTo(0, y)` every 400px with 150ms pauses) and wait `transition-duration + 200ms` before capturing screenshots.
- **Dynamic Video Background Contrast:** Overlay dynamic looping background videos with multi-stop linear gradient scrims (`rgba(0,0,0,0.4)` to `rgba(0,0,0,0.85)`). Apply `drop-shadow-[0_2px_8px_rgba(0,0,0,0.8)]` to copy text to guarantee WCAG AA contrast against shifting luminance.

## 4. Mobile GPU & Privacy Hardening Invariants
- **Mobile GPU Blur Composite Glitch:** NEVER use huge blurred DOM elements (`filter: blur(80px)` on 600x600px divs) for atmospheric lighting. On mobile Adreno/Mali GPUs, CSS blur composites into opaque solid rectangular blocks during scroll. Use pure CSS `radial-gradient` backgrounds on `body` instead.
- **Hidden Admin Route Isolation:** Secret/admin routes must feature ZERO public buttons, navigation links, or footer mentions. Access must be exclusively via direct operator URL entry.
- **Zero Tech-Stack Leakage:** Never print internal ports (`PORT 8395`), database engines (`SQLITE WAL`), or backend frameworks in consumer-facing public footers.
- **Hero Stacking Context & Inline Background:** Declare `style="background-image: url('...'); background-size: cover;"` directly on hero slide elements in HTML. Never rely solely on deferred JavaScript to mount hero backgrounds.
