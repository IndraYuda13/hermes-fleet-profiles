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

## 5. Operational Form Ergonomics (Native Date & Time Architecture)
- **Single-Column Time Picker Invariant:** In dense tabular logging forms (such as maritime Statement of Facts, incident chronologies, dispatch logs), never split time entry into dual side-by-side inputs (`<input type="time"> - <input type="time">`) on every row. Dual boxes cause visual clutter, touch targets collision, and operator confusion. Always provide exactly ONE clean `<input type="time">` per row that triggers the native 3-column Chromium flyout (Hours, Minutes, AM/PM). Express time ranges in event descriptions or dedicated optional fields.
- **Native HTML5 Date Picker Standard (`<input type="date">`):** Use native Chromium calendar pickers (`<input type="date">` with `mm/dd/yyyy` placeholder, month grid, "Clear", "Today", and blue active selection) for date entry. Do not substitute HTML `<select>` dropdowns for dates unless explicitly requested. Note that colloquial requests like *"ganti menggunakan select jangan manual"* mean making the value selectable via the graphical calendar picker rather than manually typing text strings like "14th Sept 2026".
- **Decoupled Input vs Output Formatting:** Maintain clean ISO values in form controls (`YYYY-MM-DD` for date, `HH:MM` for time). Use client-side formatting functions (`formatMaritimeDate`) to automatically project these values into formal domain representations (e.g. `14TH SEPT 2026 / 11:10 hrs LT`) in the live WYSIWYG preview, PDF export, and clipboard copy templates. Operators get frictionless point-and-click date/time entry while outputs stay strictly compliant with formal document standards.
- **Click-to-Show-Picker Invariant:** In dark or custom-styled form controls, always bind `onclick="this.showPicker()"` to `<input type="date">` and `<input type="time">`, and invert `::-webkit-calendar-picker-indicator` (`filter: invert(1); cursor: pointer;`). This allows clicking anywhere within the input box to immediately trigger the native calendar or 3-column time flyout without forcing operators to pinpoint the tiny indicator icon.

## 6. Mobile Overlay, Floating Menu & Dropdown Hardening
- **The `* { max-width: 100% }` Dropdown Trap:** Global CSS resets containing `*, ::before, ::after { max-width: 100%; }` clamp `position: absolute` children to their parent's width. When a dropdown card (`.user-dropdown-card`, `.popover-menu`) is nested inside a compact mobile trigger (such as an avatar button with width ~40-68px), `max-width: 100%` overrides `width: 240px;` and squashes the menu to 68px. This crushes text padding and forces labels into single-word vertical gibberish ("Top\nUp\nSaldo\n(QRIS...").
- **Dropdown Invariant Rules:**
  1. All floating menus and dropdowns MUST declare `max-width: calc(100vw - 24px) !important; min-width: 220px; width: 240px;` to escape parent width clamping.
  2. All menu items (`.dropdown-item`) MUST declare `white-space: nowrap;` and `min-height: 44px;` for ergonomic touch targets.
  3. Anchor right-aligned dropdowns with `right: 0;` and verify `rect.left >= 12px` on a 360px viewport.
- **Edge Cache Busting & Asset Freshness Invariant:**
  Never link production CSS/JS with bare paths (`href="/static/css/style.css"`). CDNs (Cloudflare edge) default to `max-age=14400` (`cf-cache-status: HIT`), serving stale, broken layouts to mobile clients long after server-side fixes. Always:
  1. Append deterministic build/version query strings: `href="/static/css/style.css?v=3.1.2"`.
  2. Configure backend static handlers (`NoCacheStaticFiles` in FastAPI/Express) with `Cache-Control: no-cache, no-store, must-revalidate, max-age=0` during development and rapid iteration to bypass CDN retention.
