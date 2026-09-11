---
name: interactive-tactile-web-craft
description: "Use when building tactile UIs. Adds foil, haptics & dial."
version: 1.0.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [Frontend, UI, Interactive, WebAudio, SpecularFoil, Haptics, Anti-Slop]
    category: frontend-design
---

# Interactive Tactile Web Craft

This skill provides production-grade recipes and standards for creating magnetic, highly tactile, and responsive dark-mode web experiences inspired by high-end design showcases (`sceneai.art`, Apple Card, Linear) without bloatware, heavy libraries, or generic AI slop.

## When to Use
- When asked to add interactive, engaging, or delightful effects to web components, cards, landing pages, or digital stores.
- When implementing pointer-following lighting, 3D micro-tilt, or holographic specular foil effects.
- When creating zero-download tactile audio feedback using native browser Web Audio API.
- Trigger phrases: "tambahkan sesuatu yang menarik", "interaktif", "specular sheen", "haptic click", "foil effect", "quick-dial".

## Core Techniques

### 1. Pointer-Following Specular Sheen & 3D Micro-Tilt
Rather than static borders or loud CSS hover shadows, interactive surfaces react dynamically to pointer coordinates:
- Update CSS variables `--pointer-x` and `--pointer-y` via throttled/rAF `pointermove`.
- Render a specular sheen using a radial gradient overlay with `mix-blend-mode` or semi-transparent specular highlights.
- Limit desktop micro-tilt to $R \le 3^\circ$ (`perspective(600px) rotateX(...) rotateY(...) translateY(-3px)`) with `will-change: transform`.

### 2. Synthesized Zero-Asset Web Audio Haptics (Audio Caution)
**CRITICAL USER PREFERENCE RULE**:
- Unsolicited audio clicks or sound effects are strictly prohibited unless the user explicitly requests sound/audio features.
- Most users find unexpected sound effects annoying ("suara-suara gak jelas").
- By default, keep all interactive feedback SILENT (visual specular sheen, smooth spring sliding pill indicators, and subtle tactile hover elevations).
- If sound is explicitly requested:
  - Instantiate native browser `AudioContext` on the first user gesture.
  - Synthesize an analog mechanical ceramic switch click: sine wave short ramp (1400 Hz -> 320 Hz within 18ms) with rapid exponential decay (`gain.exponentialRampToValueAtTime(0.0001, now + 0.018)`).
  - Pair with `navigator.vibrate?.(6)` on supported mobile devices.
  - Provide a dedicated topbar/control toggle for user agency with `localStorage` persistence.

### 3. Segmented Quick-Dial Scrubbers
Instead of unorganized product grids:
- Provide an interactive segmented dial bar with an animated sliding pill indicator.
- Apply 120ms stagger transitions on filtering.
- Lock all price/unit counters with `font-variant-numeric: tabular-nums` to preserve zero Cumulative Layout Shift (CLS < 0.005).

### 4. Macro-Compositional Staging Overhauls vs Micro-Cosmetic Traps
**Avoid the "Ini Masih Sama Aja" trap:**
- Never settle for just changing borders, adding subtle 1px glows, or tweaking badge text when the user asks for interactive or "wahh" design. A user will perceive zero change if the fundamental layout remains a conventional form grid.
- **Implement True Interactive Hero Staging:**
  - Build a dynamic centerpiece (e.g. Cinematic 3D Spotlight Stage with multi-layered depth parallax `translateZ` and spring lerp decay).
  - Add **Chameleon Environmental Lighting**: Backdrops and accents dynamically shift their ambient atmospheric aura in response to user selection (e.g. switching game cartridges shifts the ambient glow from emerald to flame orange to celestial violet).
  - Add kinetic horizontal selector reels (cartridge reels) with real brand/game imagery instead of generic icon boxes.

## Verification Checklist
- [ ] 0 external CDN or audio file dependencies added.
- [ ] 0 horizontal overflow across viewports from 320px to 2560px.
- [ ] AudioContext initialized safely on user gesture (zero autoplay console warnings).
- [ ] 60-120 FPS compositor animation performance (`will-change: transform`).
