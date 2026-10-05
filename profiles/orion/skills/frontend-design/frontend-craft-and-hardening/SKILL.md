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
- **Production-Denial & Fixture Harness Leakage Invariant (Metadata, Linked Assets & Verifier Rigor):**
  - *Root Layout Metadata Neutrality:* Never declare test, mock, or fixture harness metadata (`title`, `description`, open-graph tags) in the global root layout (`src/app/layout.tsx`). In Next.js App Router and SSR frameworks, the default `notFound()` error boundary renders inside the root layout and inherits root metadata, causing production 404 denial responses to leak internal fixture names and markers even when route access is denied. Keep root layout metadata strictly neutral and production-safe; isolate development fixture metadata into route-group layouts (`src/app/(fixtures)/layout.tsx`) or local page metadata.
  - *Linked CSS & Shared Asset Isolation:* Never import fixture-, mock-, or admin-specific component styles in global stylesheets (`src/app/globals.css`). Bundlers compile global CSS into shared chunks linked by `_not-found.html`, allowing unauthenticated clients probing 404 endpoints to inspect linked stylesheets and discover internal selectors (`fixture-page`, `identity-boundary`, `payment-record`, `admin-boundary`). Isolate fixture styling into dedicated stylesheets imported exclusively behind development/test guards or route-group shells.
  - *Fail-Closed Denial Verifier Standard:* Build-time denial verifiers must never rely solely on flat, hardcoded static HTML checks or substring scans. Verifiers must:
    1. Recursively discover and reject any `.html` artifact under fixture route paths, case-insensitively.
    2. Parse route and prerender manifests (`routes-manifest.json`, `prerender-manifest.json`) strictly as JSON, requiring dynamic route registration and rejecting any static or prerendered entries for fixture routes.
    3. Parse `<link rel="stylesheet">` and script tags in generated denial HTML (`_not-found.html`), resolve same-origin paths within the build root (fail-closed on traversal, external, or unresolvable URLs), recursively traverse `@import` references, and scan every reachable asset for prohibited markers and internal selectors.
  - *Copied-Artifact Verifier Self-Testing:* Validate the verifier itself using isolated negative regression suites that mutate temporary copies of the build output (injecting lowercase/nested fixture HTML, manifest alterations, and linked CSS containing state markers or forbidden selectors) to prove the verifier exits non-zero on every falsifying case before accepting a build.
- **Hero Stacking Context & Inline Background:** Declare `style="background-image: url('...'); background-size: cover;"` directly on hero slide elements in HTML. Never rely solely on deferred JavaScript to mount hero imagery.

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
- **The HTML-Inline Event Handler Mangling Trap (`ReferenceError`):**
  AST obfuscators (e.g. `javascript-obfuscator`) wrap scripts in isolated scopes or rename top-level functions into hexadecimal identifiers (`_0x4b12`).
  - *Mechanism:* Any function invoked directly from HTML attributes (`onclick="generatePDF()"`, `onchange="..."`, `onsubmit="..."`) resolves against `window` at runtime. If mangled or unexported, clicking UI elements immediately crashes with `Uncaught ReferenceError: func is not defined`.
  - *Rule:* Before AST obfuscation, parse all inline HTML event handlers (regex `(?:on\w+)\s*=\s*["']([^"']+)["']`), extract invoked function names, and append explicit window exports (`window[name] = name;`) or pass them to `reservedNames`.
- **Multi-Vector DevTools Freeze & Infinite Debugger Trap:**
  - Merely blocking `contextmenu` and shortcuts (`F12`, `Ctrl+Shift+I/J/C`, `Ctrl+U`, `Ctrl+S`) is bypassed if DevTools is opened via browser application menu or docked by default.
  - Active DevTools freezing requires recurring constructor debugger traps:
    `setInterval(() => { (function(){}).constructor("debugger")(); }, 100);`
    The instant DevTools opens, execution hits breakpoints 10x/sec, freezing DOM inspection and JavaScript execution. Pair with `setInterval(() => { console.clear(); }, 1000);`.
- **AST Hexadecimal Obfuscation & Control Flow Flattening Profile:**
  Obfuscate scripts using: `compact: true`, `controlFlowFlattening: true` (threshold 0.75), `deadCodeInjection: true` (threshold 0.4), `stringArray: true`, `stringArrayEncoding: ['base64']`, `splitStrings: true` (chunkLength 5), `identifierNamesGenerator: 'hexadecimal'`.
- **Exact Single-Line Production Packing:**
  Strip all newlines, tabs, and indentation between HTML tags, CSS rules, and script blocks. Production HTML must measure exactly **1 line**, frustrating naive "View Source" inspection.
- **cPanel Fileman API Payload & Timeout Rules:**
  When deploying large obfuscated single-line HTML bundles (300KB-500KB+) via cPanel UAPI (`/execute/Fileman/save_file_content`) over HTTP proxies:
  - URL-encoded POST bodies expand payloads by 25-35%.
  - Standard 15-30s timeouts will abort or drop the connection. Set HTTP client timeout $\ge 120$s.
- **Reference Implementation:** See `references/anti-inspect-armor-and-ast-obfuscation.md` for the complete pre-build event handler parser, infinite debugger traps, AST obfuscator profile, single-line packager, and cPanel deployer.

## 13. Client-Side Software Download Vault & Hosting Automation
- **Binary Hosting Partitioning:** Host small assets (< 25-50 MB) directly in `public_html/apps/` for direct download URLs. Offload large installer packages (> 50-100 MB) to external object storage (GitHub Releases, Backblaze B2, Google Drive) to preserve shared server bandwidth and inode quotas.
- **Dual Action Software Cards:** Provide both a Direct Download button (`target="_blank"`) and a secondary 1-click Clipboard Share button (`navigator.clipboard.writeText(...)`).
- **cPanel Deployment & AutoSSL:** Run AutoSSL via `cPanel > SSL/TLS Status` and enforce HTTPS redirect via `.htaccess`. For automated deployment, prefer scoped FTP accounts sandboxed to `public_html` (port 21) over cPanel UAPI (port 2083) to avoid cloud datacenter IP drops by hosting firewalls.

## 14. Mobile Bottom-Dock Occlusion & Terminal Pointer Clearance
- **The Floating Dock Occlusion Trap:** Fixed bottom navigation bars (`.mobile-dock`, sticky cart bars) floating over page content frequently occlude terminal interactive controls (e.g. "Lihat semua pesanan", submit buttons, terms links, order details) and bottom metrics. Even when scrolled to the very bottom, insufficient bottom padding leaves these elements underneath the dock overlay.
- **The Trailing Disclosure & Explanatory Note Occlusion Trap:**
  When an interactive action button (e.g. `Tambah +`) is followed by an informational disclaimer, capacity notice, or transactional disclosure (e.g. "Pilihan ini belum membuat reservasi atau tagihan. Keranjang hanya tersimpan pada browser saat ini."), audits often verify only that the *button* clears the fixed dock. In visible-scrollbar mobile views, multi-line text wraps and pushes trailing glyphs into the dock (`y=773..833`).
  - Never repair this by hiding, truncating, putting disclosures into accordions/tooltips, or relocating the notice away from the CTA.
  - The parent scroll container MUST reserve the full occupied dock height plus safe area and note clearance in normal document flow (`padding-block-end` and `scroll-padding-block-end`).
- **Footer Heading & Link Occlusion on Short/Medium/Denial Viewports:**
  On pages where total content height is close to viewport height (home/catalog) OR on short, sparse, placeholder, or access-denial routes (e.g. `/account/sign-in`, `/sign-in` redirect, `/admin`, empty/error states), the shared layout appends `.site-footer` immediately beneath the short content card. Without explicit layout clearance, the footer's merchant information, copyright, and disclaimers land directly in the initial unscrollable viewport (`y=773..833` at 390x844 or `y=497..557` at 320x568), resting underneath the fixed floating dock.
  - Layout wrappers (`min-h-screen flex flex-col justify-between`) and `.site-footer` must guarantee normal-flow document clearance (`padding-bottom: calc(var(--dock-occupied-height) + 24px)`) so that across EVERY route, footer headings, links, and legal copy either scroll completely above the dock or start fully beneath it.
- **Exhaustive Route-Manifest Audit Invariant (`discovered == audited`):**
  Audits that sample only 3–5 primary happy-path routes (`/`, `/products/:id`, `/cart`) silently mask footer and control occlusions on secondary, empty, auth-placeholder, and denial routes. Automated test suites MUST discover or declare an exhaustive route manifest of all reachable application endpoints (`routes-manifest.json` / dynamic route list), asserting `discovered_routes === audited_routes`. Every route must pass text-glyph range and interactive-control bounding-box dock intersection checks at both native visible-scrollbar viewports (outer 390 client 375, outer 375 client 360, compact 320 client 305).
- **Pointer Hijack Defect:** When a user taps or clicks the terminal button, `document.elementFromPoint(centerX, centerY)` resolves to the floating dock element above it (e.g. an unintended bottom navigation link like `/#catalog`), hijacking navigation away from the intended destination.
- **Universal Page-Surface Dock Clearance:** Dock space reservation (`padding-block-end` and `scroll-padding-block-end`) MUST be declared on all mobile scrollable page surfaces across the entire application (e.g. cart drawer/page, order history, checkout, settings, dashboard), not just on the home catalog or dashboard. Secondary action links (e.g. "Tambah layanan lain", "Kembali ke beranda") placed near the bottom of scrollable views will otherwise be clipped or occluded by `.mobile-dock`.
- **The Visible Scrollbar vs `--hide-scrollbars` Audit Trap:**
  - Auditing mobile responsiveness with `--hide-scrollbars` artificially keeps `clientWidth` equal to `window.innerWidth` (e.g. 390px).
  - In real browsers with visible scrollbars, the CSS `clientWidth` shrinks by the scrollbar width (e.g. 390px down to 375px), wrapping content lines, increasing element heights, and pushing bottom controls 20–40px further down directly into the fixed dock's bounding box.
  - Verification suites must probe at both full width and visible-scrollbar width (e.g. 390x844 and 375x844), never using `--hide-scrollbars` as the sole mobile pass criterion.
- **Ephemeral Chrome Profile Hygiene in Continuous Headless QA:** Headless Chrome instances downloading Widevine CDM, WASM engines, and ML models consume ~200MB per profile dir in `/cache/scratch/`. Automated test scripts must use ephemeral scratch directories and clean them up upon exit to prevent disk space exhaustion (`100% full`) that triggers task deadlocks and lost worker locks.
- **Dock Clearance & Safe-Area Invariant Rules:**
  1. Scroll containers with fixed bottom navigation MUST declare:
     ```css
     :root {
       --dock-content-height: 58px;
       --dock-occupied-height: calc(var(--dock-content-height) + env(safe-area-inset-bottom, 0px));
     }
     .scroll-container {
       padding-block-end: calc(var(--dock-occupied-height) + 24px) !important;
       scroll-padding-block-end: var(--dock-occupied-height);
     }
     .mobile-dock {
       padding-block-end: env(safe-area-inset-bottom, 0px);
     }
     ```
     Reserve the dock's occupied height explicitly on scroll containers and count `env(safe-area-inset-bottom)` exactly once. Never double-count the safe area or use arbitrary large spacers that leave excessive blank trailing space.
  2. **Initial Viewport Metric Clearance:** Verify that informative dashboard metric cards (e.g. "Status akun", "Saldo") do not render behind the dock in the initial viewport before scrolling.
  3. Automated visual/interaction QA must assert pointer hit accuracy:
     ```javascript
     const el = document.querySelector('[data-testid="terminal-action"]');
     const rect = el.getBoundingClientRect();
     const hit = document.elementFromPoint(rect.left + rect.width / 2, rect.top + rect.height / 2);
     assert(el === hit || el.contains(hit), 'Terminal control occluded by floating dock');
     ```

## 15. Ultra-Compact (320px) Button Anatomy & Anti-Detached-Arrow Invariant
- **The 320px Action Box Overflow Defect:** On narrow screens ($\le 360\text{px}$), grouping an action button with an inline icon or placing multiple action buttons side-by-side inside narrow columns forces text glyphs and SVGs outside the button box (`scrollWidth > clientWidth`), causing silent text clipping and visual overflow.
- **The Detached-Arrow Anti-Pattern:** Pairing an Add button with an anonymous, detached square arrow icon button (`->`) creates visual ambiguity and fails accessibility (unlabeled target, unknown destination, cognitive confusion).
- **Compact Action Rules:**
  1. On viewports $\le 360\text{px}$, stack primary and secondary actions as full-width blocks (`flex-col w-full min-h-[44px]`), never forcing side-by-side buttons in sub-60px widths.
  2. Never use isolated arrow icons for secondary navigation; provide an explicit accessible text label (`Buka detail` with supplementary chevron) and maintain full ergonomic touch bounds ($\ge 44 \times 44\text{px}$).
  3. Enforce `scrollWidth <= clientWidth` on all button elements across the 320px-390px sweep.

## 16. Root Static Asset & Favicon Telemetry Invariant (Zero Console 404)
- **The Browser Auto-Favicon Probe Trap:** Browsers automatically issue an HTTP GET `/favicon.ico` on initial navigation to any route. If the application root lacks a valid favicon or metadata icon file, the server returns HTTP 404, logging an unhandled console error: `Failed to load resource: the server responded with a status of 404 (Not Found)`.
- **Zero-Console-Error Compliance:** Even when application JavaScript executes cleanly, a missing favicon 404 immediately breaks strict zero-console-error invariants (Gate 0 / Hard Check 7).
- **Rule:** Every web project must supply a valid static `favicon.ico` or framework app icon (`src/app/favicon.ico` or `public/favicon.ico`) before submitting builds to visual QA, ensuring clean HTTP 200 telemetry on clean browser profiles.

## 17. Mobile Discovery Ticket Geometry vs Generic Mini-Cards (The 184–208px Invariant)
- **The Mini-Card Anti-Pattern:** On mobile viewports ($\le 480\text{px}$), laying out two-up discovery items as standalone rectangular cards with perimeter borders, loose internal margins, and buttons pasted on the bottom causes them to balloon to 220–240px+ in height. They read as generic SaaS widget cards rather than structured service tickets.
- **Service Ticket Anatomy (184–208px Target):**
  1. Eliminate individual perimeter card borders; use a shared discovery-pair surface with a central dividing rule or field partitions.
  2. Structure the top 60–72px as a tight identity block: `title (max 2 lines) -> compact detail line (e.g. 5 kredit · Rp1.500) -> factual fulfillment label (e.g. Akses digital)`.
  3. Anchor an explicit action zone at the bottom containing two contained, fully labeled $\ge 44\text{px}$ actions (`Tambah +` primary filled, `Buka detail ->` secondary outlined/quiet) separated by 6–8px.
  4. Total ticket height must strictly measure 184–208px across 320px and 390px viewports without shrinking typography or clipping text. If copy cannot fit within 208px, fall back to single-column ledger rows.

## 18. Desktop Ledger Scanability & Touch Target Invariant
- **The 36px Desktop Target Trap:** Developers frequently shrink desktop category options or filter pills to 36px (`min-height: 36px` or `padding: 6px 12px` totaling 36px) to achieve visual compactness, violating the universal $\ge 44\text{px}$ touch and click accessibility target.
- **Ledger Density Standards:**
  1. All interactive toolbar controls, category filters, and selection options must maintain $\ge 44 \times 44\text{px}$ targets even on desktop viewports ($\ge 768\text{px}$).
  2. Desktop ledger/roster rows must measure 132–152px in height, maintaining aligned field columns (`service -> variant -> route -> action`) so at least 3 full service records are visible above the fold at 1280x720 without scrolling.
  3. Focus outlines must use the active action color with a 2px canvas offset (`outline: 2px solid var(--action-color); outline-offset: 2px;`) to guarantee high-contrast visibility across dark/light themes without colliding with component borders.

## 19. Elimination of Redundant Availability & Stock Status Pills
- **The Decorative Stock-Pill Anti-Pattern:** Adding repeated `Tersedia`, `In Stock`, green dots, or circular status badges alongside product pricing is redundant template clutter. When catalog context, active `Tambah` buttons, or product variants already communicate availability, decorative status chips look like boilerplate AI slop.
- **Factual Context Over Status Pills:**
  1. Never render generic `Tersedia` badges or green status pills on purchasable items.
  2. Communicate product reality through concrete fulfillment facts (e.g. `Pengiriman otomatis`, `Proses 1-5 menit`) and action states.
  3. Unavailable items must be separated structurally as quiet, view-only records with all Add/Plus controls completely removed, rather than relying on an `Habis` status pill inside an otherwise identical card.

## 20. Accessible Modal Drawer & Sheet Keyboard Containment (`role="dialog" aria-modal="true"`)
- **The Pseudo-Modal Leak Anti-Pattern:** Rendering a slide-over drawer or bottom sheet with `role="dialog"` and `aria-modal="true"` while leaving keyboard focus on the opening trigger or background page allows `Tab` and `Shift+Tab` to traverse underlying catalog cards, inputs, and footers. Merely applying `backdrop-blur` or pointer-events disabling in CSS does NOT satisfy modal accessibility or keyboard containment.
- **Three-Phase Focus Management Contract:**
  1. **Opener Capture & Immediate Focus Entry:** When opening via trigger (e.g. `[data-testid="cart-trigger"]`), immediately store `document.activeElement`. Move focus inside the dialog (prefer the explicit close button or drawer heading with `tabIndex={-1}`) as soon as the drawer mounts.
  2. **Strict In-Drawer Focus Trapping:** On `keydown` for `Tab`:
     - Collect all enabled, visible focusable elements within the modal container (`a[href]`, `button:not([disabled])`, `input:not([disabled])`, `select:not([disabled])`, `textarea:not([disabled])`, `[tabindex]:not([tabindex="-1"])`).
     - If `Shift+Tab` and active element is the first focusable: prevent default and wrap focus to the last focusable element.
     - If `Tab` (forward) and active element is the last focusable: prevent default and wrap focus to the first focusable element.
     - Never allow background page controls to appear in sequential Tab steps while the modal is open (verify $\ge 10$ forward and reverse Tab cycles).
  3. **Guaranteed Opener Restoration on Dismiss:** On all dismissal paths (Escape key, overlay/backdrop click, explicit close button, or routing away), verify the dialog unmounts and restore focus cleanly to the original stored opener trigger.

## 21. Client-Side Document Export (PDF & DOCX) and Web Media Embedding
- **Retina HTML-to-PDF Invariants (`html2pdf.js`):** Configure `html2canvas: { scale: 2, useCORS: true }` for sharp, printable typography. Set `pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }` and place `html2pdf__page-break` elements between logical sections. Await `document.fonts.ready` before rasterizing to prevent fallback font metrics from clipping headings.
- **Client-Side DOCX Generation (`docx.js`):** Use `WidthType.PERCENTAGE` for table columns, define explicit border objects on cells, and trigger downloads via `Packer.toBlob()` + `saveAs()`.
- **Resilient Video Embeds & Error 153 Avoidance:** Never render a raw empty iframe for restricted YouTube Shorts. Build a 9:16 showcase card with thumbnail poster (`https://i.ytimg.com/vi/<ID>/hqdefault.jpg`), glowing Play SVG overlay, and fallback direct link (`target="_blank"`).
- **Hardened Single-Line Packaging:** Use `templates/build_armor.py` to AST-obfuscate client scripts, inject anti-inspect traps, and minify HTML/CSS into a single distribution line.

## 22. AI-Assisted UI Composition & Google Stitch MCP Workflows
- **Stitch MCP Transport:** Connect via Model Context Protocol (`https://stitch.googleapis.com/mcp`) using `X-Goog-Api-Key` header and 180s timeout.
- **Composition Analysis Over Template Cloning:** Use Stitch screens (`get_screen`, `list_screens`) as structural and composition anchors (typography scale, whitespace rhythm, layout density), implementing production components in semantic Tailwind rather than copying raw generated code.

## 23. WebGL 3D Creative Engineering & GPU Lifecycle
- See `references/webgl-3d-creative-engineering.md` for multi-scene SPA lifecycle teardown, safe WebGL context factories, procedural WebAudio reactivity, balanced showcase grids, and headless SwiftShader test validation.

## 24. Silent Fallback Anti-Pattern & Action State Legibility (The "Nothing Happened" Defect)
- **The Silent Fallback Trap:** When an interactive trigger (e.g. "Minta saran AI", "Sinkronisasi", "Cek kuota") triggers an async action, if an error, authorization rejection, or offline condition causes the component to quietly fall back to a default/cached static view without an explicit transition, the UI appears completely static. The operator perceives that the button is dead or non-functional ("gak terjadi apa-apa").
- **State Legibility Invariants:**
  1. **Immediate Pending Feedback:** Every interactive trigger MUST immediately register visual feedback (spinner, progress pulse, or label transition such as "Menyusun saran..." with `disabled` attribute) to confirm receipt of the click.
  2. **Unambiguous Fallback Contrast:** A degraded or offline fallback state MUST NOT visually mimic an unexercised or idle state. If an action falls back to static content, display an explicit, styled contextual badge or alert (e.g. amber badge: "Mode Offline · Menampilkan kartu bantuan statis") stating *why* the live action was not executed.
  3. **Prerequisite Gating Over Silent 403:** If an action requires client prerequisites (e.g. an active classroom session must be started before requesting copilot prompts), disable the trigger with an explanatory caption or display an actionable alert dialog guiding the operator to complete the prerequisite first, rather than allowing the button to trigger a silent API rejection.

## 25. Input Masking, Formatting & Native Validation Collision Invariants (The Auto-Hyphen / Regex Lockout Trap)
- **The Auto-Formatting / Native Pattern Collision Trap:**
  When client-side scripts apply auto-chunking or formatting masks (such as inserting hyphens `-` or spaces every 4 digits on phone numbers or customer IDs like `0812-3456-7890`) while the `<input>` element specifies an HTML5 native validation pattern (e.g. `pattern="[0-9]{9,15}"` or `pattern="[0-9]{8,20}"`):
  1. The browser's native `checkValidity()` validates the masked value against the regex pattern. Because hyphens/spaces do not match `^[0-9]+$`, validation fails immediately (`valid: false`, `patternMismatch: true`), blocking form submission with browser errors such as *"Please match the requested format."*.
  2. If the user attempts to delete the formatting characters manually, an `input` event listener that immediately reformats the string will re-insert them, trapping the user in an inescapable validation failure loop where valid numbers cannot be submitted or registered.
  3. Backend schema validation (e.g. `re.fullmatch(r'[0-9]+', value)`) often fails identically if masked values pass through via API, bot, or web forms without server-side normalization.
- **Invariants for Phone & Numeric Field Sanitization:**
  1. **Clean Digits Default:** Unless an explicit custom mask component completely decouples display formatting from the underlying input value, avoid inserting punctuation characters (`-`, spaces) into inputs bound to strict numeric patterns. Enforce clean digits (`\D` stripped).
  2. **Auto-Sanitize Over Re-Formatting:** When listening to `input` or `paste` events, sanitize non-digit characters (`replace(/\D/g, '')`) up to the maximum field length rather than inserting punctuation characters that violate native patterns. Maintain cursor position cleanly on edit.
  3. **Tolerant Schema Normalization:** Backend schemas and form submit handlers must normalize inputs by stripping hyphens and whitespace prior to regex validation (`cleaned = value.strip().replace(' ', '').replace('-', '')` for numeric fields). Never assume the client has stripped all formatting.
  4. **Live Validation Verification Protocol:** Automated browser verification for input forms must assert `input.checkValidity() === true` and `input.validationMessage === ""` across typing, pasting formatted strings (e.g. `0812-3456-7890`), and form submission.

