---
name: lens-visual-qa-engine
description: Use when auditing web UI visual quality, layout, or art.
version: 1.1.0
author: Fleet Architecture & Orion Lead
license: MIT
metadata:
  hermes:
    tags: [ui, visual-qa, lens, automated-testing, fail-fast, metrology, design-contract, fuzzing, mutation-testing]
    category: fleet-upgrade
---

# LENS Visual QA Engine — Strict 5-Gate Fail-Fast Standard

Deterministic, multi-stage visual verification standard for LENS and the fleet. Replaces fragile static screenshot reviews with a strict fail-fast pipeline, runtime design schema assertions, active interaction fuzzing, and mutation-tested calibration.

## When to Use
- Auditing web UI, dashboards, landing pages, mobile interfaces, or design system components.
- Verification Gate on any UI/UX task prior to owner review.
- Regression testing on visual layout, responsiveness, and art direction fidelity.

---

## Core Philosophy: Determinism Over Probabilism
1. **Never use a stochastic tool (VLM) for a deterministic job (geometry, contrast, runtime health).**
2. **Fail-Fast:** Gate N+1 is forbidden from executing if Gate N fails. Zero token waste on broken builds.
3. **Who Watches the Watcher:** LENS must prove its own audit harness is calibrated via Synthetic Mutation Testing before issuing a production verdict.
4. **Design Intent is Explicit:** Contracts are expressed as runtime schemas (`data-ui-*`), eliminating guesswork.
5. **Negative Control Verification:** Before accepting an audit harness, prove the harness detects and flags known baseline defects. A harness that passes an un-remediated baseline is a false-positive pass.

---

## The 5-Gate Fail-Fast Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│ Gate 0: Runtime Health, Telemetry & Lifecycle Settle (< 50ms)          │
│ ├─ 0 console.error / uncaught exceptions                              │
│ ├─ 0 HTTP 4xx/5xx on static assets (fonts, SVGs, images, chunks)      │
│ ├─ document.fonts.ready === true & network idle                       │
│ ├─ Transition Settle Barrier (opacity/transform transitions settled)  │
│ └─ DOM MutationObserver stabilized for >= 200ms                       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (PASS)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Gate 1: DOM & Semantic Integrity (< 100ms)                            │
│ ├─ Context-Aware Banned Token Scanner (excludes <code>/<pre>)         │
│ ├─ Broken Asset Guard (img.naturalWidth > 0, svg has rendered paths)  │
│ ├─ Accessibility Tree Integrity (CDP AXTree: 0 unlabelled controls)   │
│ └─ Zero Viewport Leak (document.documentElement.scrollWidth <= innerW) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (PASS)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Gate 2: Deterministic Metrology & Token Contract (< 200ms)            │
│ ├─ Computed WCAG APCA / 2.1 Contrast Calculation on rendered pixels   │
│ ├─ Runtime Schema Validation (`data-ui-*` vs getComputedStyle)        │
│ ├─ Silent Text Clipping Detector (scrollWidth > clientWidth)           │
│ └─ Minimum Interactive Touch Target (>= 44x44px mobile / 36x36px desk)│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (PASS)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Gate 3: Active Interaction & Viewport Fuzzing (< 2s)                  │
│ ├─ Dynamic Viewport Scrubbing: 320px -> 1920px in 25px steps          │
│ ├─ Extreme Content Fuzzing (200-char string, RTL Arabic, emoji, zero) │
│ ├─ Interactive State Machine Walk (hover, focus-visible, active, open)│
│ └─ Cumulative Layout Shift (CLS < 0.05 via PerformanceObserver)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (PASS)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Gate 4: VLM Macro Aesthetic & Art Direction (Final Tier)              │
│ ├─ Isolated to Macro Evaluation: Visual Hierarchy, Calm, Theme Cohesion│
│ ├─ Anti-Generic-AI Slop Rating (LOW / MEDIUM / HIGH)                  │
│ └─ Verification of 2-5 Signature Elements from DESIGN_DNA.md          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Gate 0: Runtime Health & Network Telemetry
Executed via Playwright / CDP event listeners.
- **Console Gate:** Attach `page.on('console', msg => { if (msg.type() === 'error') record(); })` and `page.on('pageerror', err => record())`. Count must equal `0`.
- **Network Gate:** Intercept `Network.responseReceived`. Any asset (CSS, JS, SVG, WOFF2, PNG/WebP) with status `>= 400` fails Gate 0.
- **Font & Lifecycle Barrier:**
  ```javascript
  await page.waitForLoadState('networkidle');
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => {
    return new Promise(resolve => {
      let timeout;
      const observer = new MutationObserver(() => {
        clearTimeout(timeout);
        timeout = setTimeout(() => { observer.disconnect(); resolve(true); }, 200);
      });
      observer.observe(document.body, { childList: true, subtree: true, attributes: true });
      timeout = setTimeout(() => { observer.disconnect(); resolve(true); }, 200);
    });
  });
  ```

---

## 2. Gate 1: DOM & Semantic Integrity
- **Context-Aware Forbidden Token Scanner:**
  Scans all visible text nodes EXCEPT those inside `<code>`, `<pre>`, `<samp>`, `[data-allow-raw-tokens]`, or developer doc containers.
  Regex: `/\b(undefined|NaN|\[object Object\]|null|Error:|NaNpx|\{\{.*\}\})\b/i`.
- **SVG & Asset Guard:**
  - Every `<img>`: `naturalWidth > 0 && naturalHeight > 0`.
  - Every `<svg>` / icon container: `getBoundingClientRect().width > 0 && height > 0` AND must contain at least 1 visible renderable child (`path`, `circle`, `rect`, `polygon`) with non-empty attributes.
  - Zero tofu characters (`\uFFFD`).
- **Icon Fallback Masking Detector (`G1_FALLBACK_ICON_MASK`):**
  Merely asserting an `<svg>` has non-empty paths is insufficient when icon helper functions silently fall back to a default glyph (such as `info`, `help-circle`, or placeholder) on missing or case-mismatched keys.
  - For all elements declaring `[data-icon]` or interactive buttons (pagination first/prev/next/last, close, search, copy):
  - Assert that the rendered SVG path data does NOT match the known fallback icon fingerprint (`SVG_ICONS.info`).
  - Flag casing discrepancies: icon keys normalized with `.toLowerCase()` when registry keys use camelCase (`chevronsLeft` -> `chevronsleft`) cause 100% of directional controls to render as informational `ⓘ` circles while passing naive SVG dimension checks.
  - **Oracle Calibration Pitfall (Geometric AST over Path Counts):** Never use naive path count heuristics (e.g. asserting `path_count >= 2` for chevrons). Single directional chevrons (`chevronLeft`, `chevronRight`) legitimately contain exactly 1 `<path>` element (`d="M15 18l-6-6 6-6"`), while double chevrons contain 2. An invalid path count threshold produces false negatives that block correct implementer code. Always compare parsed geometry/AST (matching normalized `d` coordinates) and assert negative glyph signatures (`svg.querySelectorAll('circle').length === 0` for chevrons).
  - **DOM Serialization Normalization Pitfall:** Never compare rendered SVG `outerHTML` strings directly against reference templates. Browsers normalize SVG markup (reordering attributes, formatting whitespace, self-closing vs explicit closing tags). Compare parsed attribute sets or geometry trees.
- **Hidden Element Leak Guard (`G1_HIDDEN_LEAK`):**
  Never assume HTML `hidden` attribute or `.slot[hidden]` hides an element from layout.
  - Query all elements with `[hidden]`, `[aria-hidden="true"]`, or `.hidden`.
  - Assert `getComputedStyle(el).display === 'none'` AND `el.getBoundingClientRect().height === 0`.
  - ID specificity trap: Rules like `#gridSkeleton { display: grid; }` or `#panel { display: flex; }` (specificity 1,0,0) override user-agent and class-level `[hidden] { display: none; }` (specificity 0,1,0), causing empty skeleton placeholders or hidden panels to leak 200px+ empty gray blocks into live views even in empty search states.
- **CDP Accessibility (AXTree) Proxy:**
  Fetch `Accessibility.getFullAXTree`. Assert 0 interactive elements (buttons, inputs, links) with empty accessible names.

---

## 3. Gate 2: Deterministic Metrology & Token Contract
- **Design Contract as Runtime Schema (`data-ui-*`):**
  FRAME embeds attributes; LENS validates via `getComputedStyle()`:
  - `data-ui-surface="elevated"` -> assert computed background matches `--surface-elevated` token.
  - `data-ui-min-touch="44"` -> assert `rect.height >= 44 && rect.width >= 44`.
  - `data-ui-overflow="contain"` -> assert `scrollWidth <= clientWidth && scrollHeight <= clientHeight`.
- **Contrast Ratio Metrology:**
  Calculate relative luminance $L = 0.2126R + 0.7152G + 0.0722B$ on computed colors. Assert contrast ratio $\ge 4.5:1$ for normal text, $\ge 3.0:1$ for large text/icons (WCAG AA).
- **Silent Clipping Detection:**
  Scan all containers: if `el.scrollWidth > el.clientWidth` and `getComputedStyle(el).overflowX === 'hidden'` and `textOverflow !== 'ellipsis'`, flag as `DEFECT_SILENT_CLIPPING`.

---

## 4. Gate 3: Active Interaction & Viewport Fuzzing
- **Dynamic Viewport Scrubbing:**
  Loop viewport width from 320px to 1920px in 25px increments. On each step, assert:
  `document.documentElement.scrollWidth <= window.innerWidth` (0 horizontal overflow leaks).
- **Extreme Boundary Content Fuzzing:**
  Temporarily inject into data-binding containers:
  - String 200 chars without spaces (`"WWWWWWWW..."`) -> assert container wraps or truncates with ellipsis.
  - Unicode RTL (`"مرحبا بالعالم"`) & complex emoji (`"👨‍👩‍👧‍👦"`) -> assert no alignment crash.
  - Number `0`, `999999999999`, and negative values -> assert layout stability.
- **Interactive State Walk:**
  Simulate tab traversal through all focusable elements. Assert `:focus-visible` outline is present and element is within visible viewport bounds (not hidden under sticky headers).
- **Cumulative Layout Shift (CLS):** Assert `CLS < 0.05` via `PerformanceObserver`.
- **Scroll-Reveal & Motion Invariant Gate:**
  - *Above-the-Fold First-Paint Invariant:* Assert all hero and above-the-fold content has computed `opacity === '1'` immediately after initial DOM settlement. Elements in the initial viewport must never be hidden at `opacity: 0` waiting for scroll intersection observers.
  - *Observer Lifecycle & Re-Animation Guard:* IntersectionObserver callbacks must unobserve elements once triggered (`observer.unobserve(entry.target)`). Scroll the document down and back up; assert zero re-triggering of entrance animations or layout reflows.
  - *Reduced-Motion Strict Fallback:* Execute with `page.emulate_media(reduced_motion='reduce')`. Assert all transition/animation durations are $\le 1\text{ms}$ or compute to `none`, and all content is immediately legible with zero hidden or mispositioned elements.
  - *Zero Infinite Keyframe Loops:* Grep active stylesheets and computed styles on interactive/informational components for `animation-iteration-count: infinite`. Infinite loops are strictly forbidden outside explicit, isolated ambient loading indicators.

---

## 5. Gate 4: VLM Macro Aesthetic & Art Direction
VLM is executed **ONLY** after Gates 0 through 3 are 100% PASS.
- VLM evaluates high-resolution native 1:1 sector crops (not downscaled full-page).
- Prompt focuses strictly on:
  1. **Visual Balance & Rhythm:** Hierarchy of typography and surface cards.
  2. **Anti-Generic-AI Slop Rating:** Assign `LOW`, `MEDIUM`, or `HIGH`. (`HIGH` = automatic BLOCK).
  3. **Signature Visual Elements:** Verify implementation of the 2-5 unique signature motifs defined in `DESIGN_DNA.md`.

---

## 6. Self-Validation Loop: Synthetic Mutation Testing
Before LENS audits a production build, the harness runs a calibration test in an isolated DOM sandbox:
1. Inject Mutant A: Insert `undefined` text into a heading.
2. Inject Mutant B: Set `margin-left: -100px` on a primary button.
3. Inject Mutant C: Set text color equal to background color (contrast 1:1).
4. Inject Mutant D: Set `overflow: hidden; height: 10px` on a multiline paragraph.
5. Inject Mutant E: Replace an icon SVG with an empty `<svg></svg>`.

**Invariant:** $\text{Mutation Score} = \frac{\text{Mutants Detected}}{\text{Total Mutants}} = 100\%$.
If Mutation Score $< 100\%$, LENS harness is declared **DEFECTIVE / UNCALIBRATED** and cannot issue a production verdict.

---

## Reference Files
- `references/five-gate-pipeline-spec.md` — Detailed failure codes and operational rules.
- `references/runtime-schema-contract.md` — Complete `data-ui-*` attribute specification and CSS mapping.
- `references/mutation-testing-calibration.md` — Calibration harness & mutation operators guide.
- `scripts/lens_audit_harness.js` — Runnable Playwright/CDP evaluation harness with all gate assertions.
