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

## 7. Operational Rate & Percentage Controls (Tripartite Sync Architecture)
- **The Narrow-Preset Anti-Pattern:** Never limit operational rate or percentage controls (such as commission tiers, profit splits, discounts, or margins) to a few hardcoded preset buttons (e.g. only 35%, 40%, 45%, 50%) or force operators to rely solely on manual mobile keyboard typing. Narrow presets block valid operational tiers (e.g. trainee 10-20% or master/specialist 60-70%), while raw inputs slow down counter workflows.
- **Tripartite Synchronized Control Standard:**
  For wide-span operational percentages (e.g. 10% s/d 70%), always bind three synchronized controls to the single source of truth:
  1. **Direct Number Input (`<input type="number">`):** Allows precise manual entry of any integer or decimal value.
  2. **Touch Range Slider (`<input type="range">`):** Provides instant, smooth dragging across the entire span (`min="10" max="70" step="1"`), accompanied by scale labels (`Min 10%`, `Default 40%`, `Max 70%`).
  3. **Responsive Preset Chips Grid:** 1-tap buttons for standard operational tiers (e.g. 10%, 20%, 30%, 35%, 40%, 45%, 50%, 60%, 70%) organized in a responsive grid (`grid-template-columns: repeat(9, 1fr)` collapsing to 5 and 3 columns on mobile).
- **Bi-Directional State Synchronization Invariant:**
  - Dragging the slider immediately updates the number input, calculates formulas in real-time, and lights up the matching preset chip if the value lands on a preset step.
  - Tapping a preset chip moves the slider thumb to the exact tick, sets the input field, updates active class styling, and triggers calculation.
  - Typing in the input field repositions the slider thumb and updates active button highlights when within `min`/`max` bounds.
- **Entity Identity & Themed Accent Styling:**
  In multi-entity or multi-worker dashboards (e.g. Operator 1 vs Operator 2), style the slider thumb (`::-webkit-slider-thumb`) and active button border/glow using each entity's distinct accent color (e.g. Cyan for Worker 1, Purple for Worker 2). This eliminates cognitive confusion and prevents misattributing adjustments on small mobile screens.

## 8. 4-Sector Spatial Crop & Zero-Undefined Visual Inspection Protocol
Never declare a web UI visually passed on macro screenshots alone. For each viewport (Desktop 1920x1080 and Mobile 390x844), systematically crop and verify 4 distinct spatial sectors:
- **Sector 1 (Top-Center):** Fixed headers, glass bars, brand vector SVGs, category filter pills, search omnibox (`Cmd+K`), top metadata badges.
- **Sector 2 (Bottom-Center):** Media player HUD, scrubbers, progress bars, timecodes, mobile bottom navigation docks, footer containment.
- **Sector 3 (Center-Right):** Secondary actions, watchlist toggles, volume/speed selectors, side drawer panels.
- **Sector 4 (Center-Left):** Hero primary CTAs, poster ratios (2:3, 16:9, 3:4), back navigation controls.
- **Zero "undefined" / "null" Invariant:** Automated test suites must assert count of `:text("undefined")` and `:text("null")` == 0 across all states and filter clicks.
- **Standalone Inline SVG Invariant:** Never rely on client-side JS icon replacers (`<i data-lucide="..."></i>`) on dynamic reactive state (Alpine, Vue, dynamic modals); script replacers fail during DOM injection leaving blank voids. Inject 100% standalone inline `<svg>` markup directly into templates. Never use raw Unicode emojis as primary UI icons.

## 9. Utility CSS Completeness & SVG Defense (Preventing SVG Blowup)
- **The SVG Blowup Defect:** Using utility classes (`class="w-3.5 h-3.5"`) when stylesheet lacks utility definitions causes raw `<svg>` elements to inflate to default 100% container width (500px+ raksasa), destroying layout.
- **Global SVG Defense Rule:** Always add defensive base CSS in stylesheet:
  ```css
  svg { flex-shrink: 0; display: inline-block; vertical-align: middle; }
  ```
- **Automated Bounding Box QA:** Test suites must assert rendered SVG dimensions: `boundingBox().width <= 24px` for UI icons.
- **Balanced Contact Hub & Anti-Truncation:** Never use `truncate` on email addresses in cards; use `break-all text-[11px] sm:text-xs font-mono select-all`. Balance 5 cards across 6 columns (Row 1: 3 cards col-span-2; Row 2: 2 cards col-span-3).

## 10. Advanced Micro-Layouts: Accordions, Marquees & Staging
- **CSS Grid Accordion Expansion:** Avoid JS height calculations. Animate grid rows cleanly:
  ```css
  .accordion-content { display: grid; transition: grid-template-rows 300ms ease-out; }
  .accordion-content.open { grid-template-rows: 1fr; }
  .accordion-content.closed { grid-template-rows: 0fr; }
  .accordion-content > div { overflow: hidden; }
  ```
- **Infinite Horizon Marquee & Linear Mask:** Apply edge-fade linear gradient masks to overflow containers:
  `mask-image: linear-gradient(to right, transparent, black 15%, black 85%, transparent);`
  Replicate items 3–4x in a `flex w-max` track running `linear infinite` and pause on hover.
- **Cinematic 3D Spotlight Stage & Chameleon Lighting:** Build central showcases with multi-layer depth parallax (`translateZ`) and spring decay. Backdrops and ambient glows shift their aura dynamically in response to user selection (e.g. emerald to orange to celestial violet).

## 11. Hero Background Stacking & Legacy Template Defect Prevention
- **Inline HTML Background Fallback:** Declare `style="background-image: url('...'); background-size: cover; background-position: center;"` directly on slide elements in HTML. Never rely solely on deferred JavaScript to mount hero imagery.
- **Balanced Overlay Ratios:** Keep dark scrim overlays between `rgba(0,0,0,0.35)` and `rgba(0,0,0,0.65)` to preserve background texture and lighting while maintaining text legibility.
- **Dedicated Hero Header Offset:** Maintain explicit `padding-top: 60px` to `80px` on hero containers to prevent collisions with fixed navbars.

## 12. Client-Side Vault Security & Anti-Inspect Armor
- **Zero-Knowledge Decryption (AES-256-GCM / PBKDF2):** Sensitive vault catalogs must be stored exclusively as encrypted ciphertexts. Derive 256-bit encryption keys mathematically using Web Crypto API with PBKDF2 (100,000 iterations of SHA-256) and AES-GCM. Never store or compare plaintext passwords in source code.
- **Volatile Memory Purge on Lock:** Set decrypted in-memory variables to `null` and clear DOM containers when re-locking vaults. Never persist decrypted plaintext in `sessionStorage` or `localStorage`.
- **Anti-Inspect Armor:** Compress production bundles into single-line dense blocks, mangle identifiers, and intercept `contextmenu` and DevTools shortcuts (`F12`, `Ctrl+Shift+I`). Bind public handler functions to `window` before obfuscation to prevent `ReferenceError`.

## 13. Client-Side Software Download Vault & Hosting Automation
- **Binary Hosting Partitioning:** Host small assets (< 25-50 MB) directly in `public_html/apps/` for direct download URLs. Offload large installer packages (> 50-100 MB) to external object storage (GitHub Releases, Backblaze B2, Google Drive) to preserve shared server bandwidth and inode quotas.
- **Dual Action Software Cards:** Provide both a Direct Download button (`target="_blank"`) and a secondary 1-click Clipboard Share button (`navigator.clipboard.writeText(...)`).
- **cPanel Deployment & AutoSSL:** Run AutoSSL via `cPanel > SSL/TLS Status` and enforce HTTPS redirect via `.htaccess`. For automated deployment, prefer scoped FTP accounts sandboxed to `public_html` (port 21) over cPanel UAPI (port 2083) to avoid cloud datacenter IP drops by hosting firewalls.
