---
name: mathematical-ui-alignment-and-anti-slop
description: Build/audit subpixel UI alignment & anti-slop.
version: 1.0.0
author: Orion Fleet Lead
license: MIT
metadata:
  hermes:
    tags: [frontend, ui, alignment, timeline, anti-slop, apple-design, precision]
    category: frontend-design
---

# Mathematical UI Alignment & Anti-AI-Slop Engineering Standard

## When to Use
Use whenever designing, building, or auditing frontend interfaces that require mathematical subpixel alignment (timelines, milestone spines, step wizards, split ledgers) or when elevating web UI above generic AI slop into Apple / Linear-grade precision.

---

## 1. Zero-Drift Timeline & Spine Geometry Invariant

### The Anti-Pattern (Vulnerable to Subpixel Drift & Baseline Shift)
Never use negative hardcoded absolute margins (`absolute -left-[31px]` / `-left-[39px]`) with a parent `border-l pl-8`. These break under browser subpixel rounding, DPI scaling (125%, 150%), font loading baseline shifts, and responsive text wrapping:
```html
<!-- BAD: DO NOT USE -->
<div class="relative pl-6 sm:pl-8 border-l border-zinc-200">
  <div class="relative">
    <div class="absolute -left-[31px] sm:-left-[39px] top-1 w-3.5 h-3.5 rounded-full ..."></div>
    <span>2023 — PRESENT</span>
  </div>
</div>
```

### The Standard Pattern: Isolated 2-Column CSS Grid Spine (`grid-cols-[auto_1fr]`)
Always isolate the vertical spine track and the bullet in a dedicated fixed-width column:
```html
<!-- GOOD: CSS Grid 2-column track guarantees concentric X-alignment (Delta_X = 0.00px) -->
<div class="space-y-0 relative max-w-3xl">
  <div class="timeline-item grid grid-cols-[32px_1fr] sm:grid-cols-[36px_1fr] gap-x-4 sm:gap-x-6 group">
    
    <!-- Spine Track (Column 1: Fixed Width) -->
    <div class="flex flex-col items-center">
      <!-- Bullet Centering Container -->
      <div class="flex items-center justify-center w-7 h-7 sm:w-8 sm:h-8 shrink-0 relative z-10">
        <div class="w-3 h-3 sm:w-3.5 sm:h-3.5 rounded-full bg-white ring-4 ring-white border-2 border-zinc-900 shadow-sm transition-transform duration-200 group-hover:scale-125"></div>
      </div>
      <!-- Continuous vertical spine line (use gradient fade on last item) -->
      <div class="w-px flex-1 bg-zinc-200 group-hover:bg-zinc-300 transition-colors"></div>
    </div>

    <!-- Content Track (Column 2: 1fr) -->
    <div class="pt-0.5 pb-10">
      <div class="flex flex-wrap items-center gap-2 mb-1.5">
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-mono font-medium bg-emerald-50 text-emerald-800 border border-emerald-200/70">
          2023 — PRESENT
        </span>
        <h3 class="text-base font-semibold text-zinc-900 tracking-tight">Full-Stack Systems Consultant</h3>
      </div>
      <p class="text-xs font-mono text-zinc-500 mb-2">Independent Engineering & Technical Contracts</p>
      <p class="text-sm text-zinc-600 leading-relaxed">
        High-throughput automation pipelines, reverse engineering tools, and systems architectures.
      </p>
    </div>

  </div>
</div>
```

### LENS Visual QA Mathematical Invariant
In automated headless browser audits, verify:
- `Delta_X = |bullet.left + bullet.width/2 - line.left - line.width/2| <= 0.5px` (100% Concentric).
- `Delta_Y = |bullet.top + bullet.height/2 - badge.top - badge.height/2| <= 1.5px` (Flawless Vertical Center).

---

## 2. Elevating Beyond Generic "Lazy" AI Slop (Apple / Linear Precision)

To prevent generic AI templates, implement these 7 craft layers:

1. **Interactive Living Engineering Showcases / Simulators (Over Static Text Cards):**
   Instead of passive text descriptions and generic feature cards, transform flagship engineering projects into **living interactive laboratories and simulators** (e.g. live Cloudflare handshake solvers with streaming stage logs, dynamic time-series forecast charts with interactive horizon/quantile sliders, interactive multi-step checkout flows with simulated QRIS payment state transitions, and live multi-node ping sweep telemetry grids). This brings the benchmark of **Apple Product Showcase (apple.com/id/iphone) × Linear/Vercel Lab** to life.

2. **Fluid Apple Squircle Surface Architecture (Anti-Harsh Box Geometry):**
   Eliminate harsh, sharp-cornered isolated boxes. Use continuous-curvature squircle geometry (`rounded-2xl` / `rounded-3xl` / radius 20px–28px) with seamless canvas blending (`#FBFBFD` base, `bg-white/70 backdrop-blur-2xl`, ultra-subtle ambient diffusion shadows `0 20px 40px -15px rgba(0,0,0,0.03)`, and hair-thin specular borders `rgba(15,23,42,0.04)`).
   ```css
   .card-squircle-seamless {
     background: rgba(255, 255, 255, 0.70);
     backdrop-filter: blur(24px) saturate(180%);
     border-radius: 1.5rem; /* 24px squircle */
     border: 1px solid rgba(15, 23, 42, 0.04);
     box-shadow: 
       inset 0 1px 0 0 rgba(255, 255, 255, 0.95),
       0 1px 2px 0 rgba(0, 0, 0, 0.01),
       0 20px 40px -15px rgba(0, 0, 0, 0.03);
   }
   ```

3. **Strict Zero Raw Emoji Invariant (100% Vector SVG Iconography & Standalone Inline Invariant):**
   - Never use raw Unicode emojis (⚡, 🛡️, 🚀, 💻, 🎯, etc.) as primary UI icons or visual badges. Raw emojis look childish, inconsistent across OS platforms, and are an immediate tell of lazy AI slop.
   - Always use clean, dedicated monoline vector SVGs (Lucide / Phosphor style, `stroke-width="1.5"` to `1.75px`, crisp 16/20/24px viewBox).
   - **Standalone Inline SVG Invariant (Anti-Dynamic-Icon-Drop):** Never rely on client-side JS icon replacers like `<i data-lucide="..."></i>` with `lucide.createIcons()` on dynamic reactive state (Alpine.js, Vue, React, dynamic modals/drawers). Script replacers frequently fail during dynamic DOM injection, leaving blank invisible square voids or unrendered `:data-lucide` evaluating to `undefined`. Always inject 100% standalone, inline vector `<svg>` markup directly into template components.

---

## 5. Mandatory 4-Sector Spatial Crop, Zero-Undefined & Visual Inspection Protocol

Never declare a web UI complete or visually passed based solely on full-page macro screenshots or `curl` checks. Macro screenshots disguise missing icons, broken SVG rendering, text clipping, and alignment errors.

For every captured viewport (Desktop 1920x1080 and Mobile 390x844) and major view state (Browse, Player, Modal, Drawer), LENS must systematically crop and verify **4 distinct spatial sectors**:

```
 ┌─────────────────────────────────────────────────────────────┐
 │                SECTOR 1: TENGAH KE ATAS                     │
 │      (Fixed Header, Logo, Search, Filter Pills, Top Badges)  │
 ├──────────────────────────────┬──────────────────────────────┤
 │   SECTOR 4: TENGAH KE KIRI   │   SECTOR 3: TENGAH KE KANAN  │
 │  (Hero CTA, Back Button,     │ (Watchlist, Episode Drawer,  │
 │   Poster Rails, Left Nav)    │  Volume/Speed, Right Rail)   │
 ├──────────────────────────────┴──────────────────────────────┤
 │                SECTOR 2: TENGAH KE BAWAH                    │
 │      (Player HUD Scrubber, Bottom Nav Dock, Footer Spine)   │
 └─────────────────────────────────────────────────────────────┘
```

1. **Sector 1 (Top-Center / Tengah ke Atas):** Fixed headers, glass bars, brand SVG logos, category filter pills, search omnibox/spotlight triggers (`⌘K`), top metadata badges.
2. **Sector 2 (Bottom-Center / Tengah ke Bawah):** Media player controls, 60fps scrubbers, progress bars, timecodes, mobile bottom navigation docks, and footer containment.
3. **Sector 3 (Center-Right / Tengah ke Kanan):** Secondary action buttons, watchlist toggles, volume/playback speed selectors, side episode/details drawers, and right carousel chevrons.
4. **Sector 4 (Center-Left / Tengah ke Kiri):** Hero primary CTAs, poster aspect ratios (2:3 / 16:9), back navigation buttons, and left carousel controls.
5. **Zero "undefined" / "null" DOM Oracle Invariant:** Test suites and visual inspectors MUST assert that `:text("undefined")`, `:text("null")`, and broken string templates count == 0 across all states and filter button clicks.
6. **Icon Integrity Metric:** 100% of icons in all 4 sectors must render as valid vector `<svg>` elements with 0 unrendered icon tags or blank bounding boxes.

## 6. Proactive Cache-Busting & Live Production Reload
When pushing fixes to production:
- Nginx & Cloudflare Tunnel must be cleanly reloaded (`systemctl reload nginx && systemctl restart cloudflared`).
- Always advise operators to perform a **Hard Refresh** (`Ctrl+Shift+R` / `Cmd+Shift+R`) or incognito verification when local browser cache might retain stale assets.

4. **Verified User Identity & Contact Intake First:**
   Never invent or hallucinate user usernames (Telegram handles, emails, phone numbers, domain URLs). Proactively ask via `clarify` or verify against persistent memory before finalizing user-facing contact hubs. Implement dual-action contact components (1-Click Clipboard Copy + Direct URL Launch).

5. **Apple Specular Light Glassmorphism:**
   ```css
   .card-specular {
     background: rgba(255, 255, 255, 0.85);
     backdrop-filter: blur(16px) saturate(180%);
     border: 1px solid rgba(0, 0, 0, 0.08);
     box-shadow: 
       inset 0 1px 0 0 rgba(255, 255, 255, 0.95),
       0 1px 3px 0 rgba(0, 0, 0, 0.02),
       0 8px 24px -4px rgba(0, 0, 0, 0.05);
   }
   ```
6. **Interactive Bento Cards with Live Inspector Tabs:**
   Multi-tab cards (Overview Telemetry | Live Architecture SVG Flow with animated dash streams | Code Snippets) instead of static walls of text.
7. **Hardware-Accelerated Sliding Pills:**
   Floating segmented navigation and filter bars with `cubic-bezier(0.16, 1, 0.3, 1)` smooth transform gliding.

---

## 3. Utility CSS Completeness & SVG Sizing Invariant (Preventing Catastrophic SVG Blowup)

### The Catastrophic Defect
Writing HTML markup with utility classes (e.g. `class="w-3.5 h-3.5 flex grid max-w-5xl rounded-2xl"`) while `style.css` **lacks those utility definitions or Tailwind CSS runtime**.
- **Consequence:** Raw `<svg>` elements without defined CSS dimensions explode to browser default 100% container width (500px+ raksasa), overflowing the viewport and obliterating the entire visual hierarchy.
- **Why Headless DOM Tests Missed It:** Basic automated tests checking `element !== null`, HTTP 200, and 0 console errors will PASS 100% even when the rendered page is completely destroyed visually.

### Mandatory Safeguards:
1. **Explicit Engine Injection:** If writing utility classes, always include Tailwind CDN `<script src="https://cdn.tailwindcss.com"></script>` with `tailwind.config` or bundle full CSS utilities.
2. **Global SVG Defense Rule:** Always add defensive base CSS in `style.css`:
   ```css
   svg {
     flex-shrink: 0;
     display: inline-block;
     vertical-align: middle;
   }
   ```
3. **Automated Bounding Box QA:** Automated test suites must explicitly query rendered SVG dimensions (`boundingBox().width <= 24px` for UI icons) rather than merely checking presence in the DOM.

---

## 4. Balanced 5-Card Grid & Anti-Truncation Contact Hub

1. **Email Anti-Truncation:**
   Never use `truncate` on email addresses in compact cards. Use `break-all text-[11px] sm:text-xs font-mono select-all` so full domains (e.g. `indrayudaadisaputra13@gmail.com`) render completely without `...` ellipsis.
2. **Symmetrical 5-Card Layout:**
   Use a 6-column grid system (`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4`):
   - Row 1 (3 Cards): Telegram, WhatsApp, Email with `lg:col-span-2` (2 + 2 + 2 = 6).
   - Row 2 (2 Cards): LinkedIn, GitHub with `lg:col-span-3` (3 + 3 = 6, perfectly balanced 50:50 split filling the row).
