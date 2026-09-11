---
name: anti-slop-ecommerce-architecture
description: "Build clean, zero-slop digital catalogs and e-commerce UI."
---

# Anti-Slop E-Commerce & Catalog Architecture

## Core Purpose
Guides frontend engineers (FRAME) and designers (AURORA) in building digital stores and product catalogs that avoid generic AI-slop tropes (neon purple glows, multi-stop gradient blobs, cluttered inline card selectors) and instead deliver sleek, high-converting, benchmark-accurate e-commerce interfaces.

## 1. Two-Tier Card & Interaction Architecture
* **Tier 1 — Clean Catalog Card (Grid View):**
  - **Squircle App Icon:** 52×52px container (`rounded-[22%]`) with official vector SVG logo.
  - **Hierarchy:** App title (bold 14-15px), 2-line clean tagline (`line-clamp-2`), star rating + sales proof (`★ 4.8 · 55.8k terjual`), platform chips (`Web`, `iOS`, `Android`).
  - **Pricing:** Uncluttered row: "Mulai dari", price in `tabular-nums` (`Rp 33.000`), strikethrough original price, terracotta discount tag (`-40%`), and hover micro-interaction indicator (`Pilih →`).
  - **Card Anti-Pattern:** NEVER embed duration buttons (1 Bulan, 1 Tahun), account type toggles (Private, Shared), or direct input forms inside the grid card. This creates visual clutter and layout thrashing.
* **Tier 2 — Interactive Detail Modal / Slide-Over Sheet (On-Click):**
  - Triggered cleanly by clicking any product card.
  - Houses the full package & duration selector, detailed feature list (2-column checkmark grid), device compatibility, direct WhatsApp order button, and instant QRIS checkout tab.

## 2. Benchmark Visual Tokens (Warm Dark / Swiss Minimalist vs Citrus Arcade)
* **Warm Dark / Swiss Minimalist (SaaS & Digital Goods Stores):**
  - Base Canvas: Warm Dark `#111110` (replaces harsh cold blues and pure blacks).
  - Surface Hierarchy: Surface `#1a1a18`, Surface-2 `#222220`, Surface-3 `#2c2c29`.
  - Borders: Subtle `rgba(236, 235, 231, 0.09)` (`--border`) & `rgba(236, 235, 231, 0.18)` (`--border-strong`).
  - Accents: Warm Forest Green / Mint `#3ba07f` / `#12694f` (primary CTA), Terracotta `#d1684f` (discounts), Warm Amber `#e3b45c` (ratings).
* **Citrus Arcade & Obsidian Armor (High-Voltage Instant Fintech / Game Topup):**
  - Base Canvas: Obsidian Void `#08080C`, Surface Card `#101016`, Surface Elevated `#161622`, Surface Sunken `#050508`.
  - Borders: Specular rim highlights (`rgba(255, 255, 255, 0.08)` to `0.12`), eliminating 4px harsh comic-style drop-shadows.
  - Accents: Electric Lemon `#FFE500` (CTA, focus ring, active selection glow), Emerald Laser `#00E599` (success, online badge), Cyan Cyber `#00E5FF` (info, telco), Solar Amber `#FF9900` (timer warnings).
  - Typography Stacks: Display `Sora` (arcade tech), UI `Manrope` (legibility), Monospace `JetBrains Mono` (`font-variant-numeric: tabular-nums` strictly on prices, invoice IDs, and timers).
* **Glassmorphism:** `mat-func` floating pill header and mobile bottom dock (`backdrop-filter: blur(24px) saturate(1.8)` with subtle 1px specular border).

## 3. Macro Layout Principles
* **2-Column Desktop Grid & Left Nav Rail:** 246px-264px sticky/fixed navigation rail on the left (brand mark, primary catalog/route links, and membership CTA) paired with a responsive modular bento canvas or 3-4 column catalog grid on the right.
* **Mobile Navigation Rail Transformation:** On viewports `<= 820px`, transform the left desktop navigation rail into a docked bottom navigation bar (`position: fixed; bottom: 0; left: 0; right: 0; height: 68px-70px;`). Enforce `padding-bottom: calc(76px + env(safe-area-inset-bottom))` on the main scroll container to prevent content occlusion. Hide secondary marketing cards and expand game/category grids into touch-friendly horizontal swipe reels (`scroll-snap-type: x mandatory`).
* **Mobile Ergonomics:** Floating rounded-full bottom dock (`[ Beranda ] [ Aplikasi ] [ Promo ] [ Keranjang ] [ Cari ]`) for one-handed touch navigation.
* **Media & Digital Asset Streaming Integration:** Ensure clean catalog-to-theater view transitions, MediaSession OS metadata binding, accessible volume/scrubber states, and robust proxy/transcode caching when video/audio preview surfaces are embedded (see `references/media-streaming-catalog-integration.md`).
* **Catalog Partition & Action Toolbar Architecture:** When filtering binary or multi-partition catalogs (such as Anime vs Donghua), use 3-state Segmented Frosted Capsules (`Semua` | `A` | `B`) co-located with sort switchers, opposing-corner card badges, and mobile-stacked full-width tap targets to eliminate multi-tap friction and empty-state hazards (see `references/catalog-content-type-filter-patterns.md`).
* **Seamless Infinite Scroll & Continuous Ingestion:** Prevent scroll jumping, duplicate cards, and dropped triggers by combining an `IntersectionObserver` sentinel (`rootMargin: '300px'`) with a throttled passive window scroll listener and double-layer in-memory/DOM deduplication (see `references/seamless-infinite-scroll-catalog-patterns.md`).
* **3D WebGL & Scrollytelling Hero Integration:** When integrating real-time 3D models and kinetic scroll effects into high-converting storefronts, use procedural primitives (<2.5k polygons) to eliminate multi-MB GLTF download delays, clamp mobile DPR to <=1.5, enforce dual-layer render loop culling (`IntersectionObserver` + `visibilitychange`), and protect checkout DOM controls with strict `pointer-events` isolation (see `references/webgl-scrollytelling-catalog-integration.md`).


## 4. Topup & Direct Digital Goods Configurator Architecture (Anti-Friction Rules)
* **1-Page Configurator vs Multi-Step Wizard:**
  - Avoid breaking topup flows into >3 discrete, blank-slate wizard screens (`setStep()`). This fragments client state, triggers unnecessary layout thrashing, and increases drop-off.
  - Structure as a single-page progressive configurator:
    1. *Account & Destination Input:* Game User ID & Zone ID with debounced inline inquiry validation (300ms + `AbortController` to cancel in-flight requests and prevent race conditions; instant feedback badge/nickname below field).
    2. *Nominal Selection Grid:* Product item cards with tabular pricing (`tabular-nums`) and discount badges.
    3. *Payment Method Selector:* Direct QRIS / E-Wallet / Account Balance selector.
    4. *Contact & Receipt Info:* Single WhatsApp / Phone field for delivery receipt with cursor preservation (`setSelectionRange`).
  - See `references/express-topup-configurator.md` for state schema and QRIS helper details.
* **Guest Checkout & Post-Purchase Account Linking:**
  - Never block the primary checkout CTA with a mandatory login/registration dialog.
  - Collect recipient phone/WhatsApp within the single checkout flow and process the payment immediately.
  - Offer optional account registration / claiming on the post-purchase status screen ("Daftar akun untuk menyimpan riwayat & kumpulkan cashback").
* **Mobile Background Lifecycle & Payment Polling:**
  - Mobile browsers freeze `setInterval` when users switch apps to scan QRIS in banking apps (BCA, DANA, GoPay).
  - Always listen to `visibilitychange` and `window.onfocus` to silently trigger an immediate payment status check when the user returns to the browser tab.
  - Provide a dedicated **"📥 Simpan QRIS ke Galeri"** button on mobile viewports since users cannot scan their own phone screens.
  - Ensure fixed bottom action bars include `env(safe-area-inset-bottom)` and container `padding-bottom` offsets to prevent clipping and system gesture collisions.
* **Zero DOM-Mutating Icon Scripts in Reactive SPAs:**
  - Never use client-side DOM-mutating icon libraries (e.g. `data-lucide` with `lucide.createIcons()`) in dynamic storefronts. Re-running global icon mutations during component updates wipes out attached event listeners and triggers layout thrashing.
  - Mandate 100% standalone inline SVGs or an in-memory SVG registry (`SVGS[name]`).
* **Quick-Conversion & Social Proof Modules:**
  - *Quick Nominal Picker ("Top Up Cepat"):* Expose a 3x2 grid of high-velocity nominals for the featured or selected game directly on the dashboard. Clicking a card sets `selectedProduct` and opens the express checkout sheet immediately, bypassing multi-step category drills.
  - *Sanitized Live Purchase Feed ("Transaksi Terbaru"):* Display real-time successful transactions (game icon, masked identifier `0812****890`, item name, green status badge, relative time) with deterministic fallback telemetry when order traffic is quiet to sustain social proof.
  - See `references/express-topup-configurator.md` for SVG registry and live feed integration patterns.
