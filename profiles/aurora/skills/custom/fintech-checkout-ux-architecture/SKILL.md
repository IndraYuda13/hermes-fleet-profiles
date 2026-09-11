---
name: fintech-checkout-ux-architecture
description: High-converting fintech checkout and real-time topup UX.
version: 1.2.0
metadata:
  hermes:
    tags: [fintech, checkout, ux-architecture, state-machine, payment-drawer, anti-slop, topup, brand-assets]
    category: custom
---

# Fintech & Digital Top-Up Checkout UX Architecture

Standardized patterns and state machines for building high-conversion, real-time digital cashiers and top-up experiences, synthesized from live multi-peer architecture consultations (Product Design, Backend, Frontend, and Security).

> **Supporting References:**
> - `references/tactile-interactivity-patterns.md` — Dynamic micro-interactions and tactile feedback.
> - `references/macro-composition-gaming-storefront.md` — Macro-composition 3-tier staging, asymmetric Bento storefront grids, CSS 3D parallax, optical haptics, and responsive mobile dock transitions.
> - `references/brand-artwork-integration.md` — 3:4 aspect ratio brand poster cards, spotlight thumbnails, ledger hero banners, and zero-CLS fallback strategies.
> - `references/ingame-items-nominal-cards.md` — In-game item thumbnail box system, glowing pass badges, tabular pricing, and tactile micro-interactions.
> - `references/digital-license-marketplace-patterns.md` — Inline duration/type micro-configurators, 4-stage QRIS state machine, credential vaults, and mobile bottom pill dock ergonomics.

---

## 1. 1-Page Express Configurator with Asynchronous Inquiry

### UX Problem
Multi-step wizards (e.g. 8 steps) cause high mobile drop-off rates, state leakage when switching items, and cognitive fatigue.

### Architecture Standard
* **Unidirectional Single-Page Flow:**
  1. **Product / Brand Selection:** Scoped search and categorized grid.
  2. **Scoped Identity Input:** Per-brand draft preservation in client session memory (`sessionStorage`).
  3. **Live Nickname Inquiry Card:** Avatar, Nickname, and Server confirmation.
  4. **Nominal & Price Matrix:** Buyer-facing price only; never expose modal costs or internal SKUs.
  5. **Action CTA:** Deterministic gating with loading micro-feedback.
* **Non-Blocking Asynchronous Fallback:**
  * Client debounces inquiry input (400ms) with `AbortController` or sequence ID to discard stale responses.
  * Backend caches inquiry results in Redis (TTL 24–72h).
  * If upstream inquiry times out (>1.5s) or fails, **never block checkout**. Display a non-intrusive advisory banner (*"Verifikasi ID sedang lambat, pastikan data Anda sesuai"*) and keep the purchase CTA enabled.
* **Security & Zero-Trust:**
  * Rate-limit public inquiry endpoints (token bucket per IP/device) to prevent user enumeration and scraping.
  * Recompute final price, gateway fees, and inventory at backend from master DB based on SKU; never trust client-supplied price payloads.

---

## 2. Real-Time Payment Drawer & Live Fulfillment Timeline

### UX Problem
Post-payment anxiety occurs when scanning QRIS/e-wallets without instantaneous feedback on payment confirmation and delivery progress.

### Architecture Standard
* **Interactive Slide-over / Bottom Sheet Drawer:**
  * High-contrast QRIS with download button and visual `MM:SS` countdown timer.
  * Amber pulse micro-warning when remaining time < 2 minutes.
  * Modal focus trap and disabled accidental dismiss while payment is pending.
  * **Mobile QRIS "Scan vs Save" Ergonomics:** Since smartphone users cannot scan their own screen, provide a primary 1-tap **"Simpan QRIS ke Galeri"** button (trigger canvas/blob download), a copyable raw QR payload fallback, and a 3-step micro-guide (*1. Unduh QRIS → 2. Buka m-Banking/E-Wallet → 3. Upload dari Galeri*).
* **Live SSE (Server-Sent Events) Stream:**
  * Lightweight, 1-way HTTP/2 stream with native auto-reconnect (more efficient on mobile than WebSocket).
  * 4-Stage visual timeline: `Menunggu Pembayaran` → `Pembayaran Diterima` → `Memproses ke Provider` → `Sukses Terkirim`.
  * Auto-close drawer with celebratory micro-animation on success; seamless transition to digital receipt.
* **Tab-Switch Visibility Re-Sync:**
  * Mobile browsers throttle background JS timers when user switches to m-banking/e-wallet apps to scan/pay QRIS.
  * Register `document.addEventListener('visibilitychange')`: immediately trigger payment status check when `document.visibilityState === 'visible'` to avoid stale timer display upon returning to the tab.
* **Backend & Security Controls:**
  * **Atomic DB Claim Lock:**
    ```sql
    UPDATE orders 
    SET status = 'submitting' 
    WHERE id = :order_id AND status = 'pending_payment';
    ```
    Guarantees zero double fulfillment between webhook callbacks and client polling/SSE listeners.
  * Webhook validation with HMAC-SHA256 signature, timestamp drift checks (<5 min), and Idempotency Keys.
  * SSE endpoint secured with short-lived, high-entropy UUID + token; auto-closed on terminal state.

---

## 3. Frictionless Smart Retention & Cross-Channel Synergy

### UX Problem
Requiring mandatory login before checkout ruins guest conversion, while treating every visitor as a blank slate destroys repeat purchase velocity (LTV).

### Architecture Standard
* **1-Tap Quick Reorder (Saved Account Chips):**
  * Store up to 5 recently successful account identifiers in encrypted local client storage.
  * Render as horizontal chips above the input zone (e.g. `[MLBB] SkyWalker (Zone 2042)`).
  * Single tap auto-populates fields and triggers non-blocking background re-verification.
* **Frictionless Guest Checkout & Post-Purchase Account Conversion:**
  * Never block instant checkout with mandatory registration/login forms (`require_account` before payment). Allow guest purchase with minimal contact (WhatsApp / HP) for invoice delivery.
  * Store guest orders in local browser storage (`localStorage['lt_guest_orders']`) for tracking continuity.
  * Convert guests on the **Post-Payment Success Screen**: pitch 1-tap PIN setup or Telegram binding to protect order history and activate wallet cashback without disrupting the primary purchase funnel.
* **Stateless Telegram Deep-Link Account Binding:**
  * Avoid heavy registration forms. Use 1-tap deep links: `t.me/LemonTopupBot?start=bind_<token>`.
  * Token must be single-use, signed (HMAC-SHA256), and short-lived (5–10 min expiry).
  * Unifies web session and Telegram bot wallet balance / transaction history safely.
* **Universal Guest Order Lookup:**
  * Allow tracking via Order ID or WhatsApp Number across both Web and Telegram Bot interfaces.

---

## 4. Anti-AI Slop & Visual Performance Rules
* **Procedural In-Memory WebGL vs Heavy External GLTF Assets:** For flagship ("MAHAL" / Awwwards-grade) storefronts, avoid heavy multi-megabyte GLTF/GLB models or Draco decoders. Instead, use lightweight **procedural Three.js geometry** (e.g. Crystalline Polyhedron: Icosahedron outer shell + Octahedron relic + Torus nano-rings, <2,200 triangles total) compiled in-memory with zero asset download. Enforce dual culling: `document.hidden` culling via `visibilitychange` and viewport culling via `IntersectionObserver` (pause render loop when user scrolls down to checkout wizard). Clamp device pixel ratio to `Math.min(window.devicePixelRatio, 1.5)` on mobile and `2.0` on desktop.
* **Controlled Specular Sheen vs Macro Tilting:** In fintech checkout and voucher cards, avoid aggressive 3D macro-wobble (>8 deg) that compromises numeric readability. Restrict 3D perspective to micro-tilt ($R < 0.65^\circ$) and focus delight on a sharp specular sheen ray (`mix-blend-mode: overlay`, radial gradient following cursor `--pointer-x`, `--pointer-y`) that sleeps immediately when the cursor idles.
* **Strict Zero-Audio Invariant & Pure Optical Haptics:** Unless explicitly mandated otherwise by the user, consumer storefronts strictly **FORBID audio clicks, beeps, or Web Audio synthesis** (Zero-Audio Invariant). Tactile feedback must be 100% optical: moving specular glints, 1px gold rim highlights, smooth micro-elevations, and Android `navigator.vibrate(6)` if permitted. Zero noise pollution, zero layout shift (CLS = 0.000 via `tabular-nums`), and INP < 8ms.
* **Surface Discipline & Specular Rims:** High-contrast dark surfaces with vibrant citrus accents strictly reserved for active states, CTA, and verified feedback. Replace 4px hard black offset shadows (`box-shadow: 4px 4px 0 #000`) with 1px specular rim borders (`rgba(255, 255, 255, 0.08)`) and layered luminance depth.
* **Zero Jitter via Tabular Numerics:** Enforce `font-variant-numeric: tabular-nums` on all pricing calculations, fee breakdowns, and `MM:SS` countdown timers to eliminate layout shifts during polling updates.
* **Non-Blocking Pointer-Events Discipline:** When embedding interactive 3D WebGL canvases in the hero stage, isolate canvas hitboxes (`pointer-events: none` on ambient overlays, `pointer-events: auto` on canvas bounds) and preserve `z-index: 10` on form inputs, search bars, and cartridge reels to prevent intercepting critical transactional event listeners.
* **5-Layer Stacking Architecture for 3D Hero Spotlight Decks:** When combining procedural 3D WebGL canvases with 2D game cover artwork in a card, never place opaque 2D artwork on top of the 3D canvas wrap (which causes total visual occlusion of the 3D core). Enforce strict depth stacking:
  - *Layer 0 (Aura):* Card Ambient Backlight Halo (`translateZ(0)`).
  - *Layer 1 (Base):* Brushed Dark Obsidian Metallic Base & Specular Sheen (`translateZ(10px)`).
  - *Layer 2 (Media Tint):* Translucent Media Cover (`z-index: 2`, `opacity: 0.25–0.30`, radial scrim mask `radial-gradient(circle at 50% 45%, rgba(9, 10, 14, 0.15) 0%, rgba(9, 10, 14, 0.96) 100%)`).
  - *Layer 3 (Showcase Canvas):* Interactive 3D Canvas Stage (`z-index: 3`, `pointer-events: auto`, explicit raycast cursor feedback: idle `default`, hover `grab`, active drag `grabbing`).
  - *Layer 4 (Tactile HUD):* Floating Badges & Express CTAs (`z-index: 4`, container `pointer-events: none` with interactive buttons `pointer-events: auto`).

---

## 5. Ergonomic Surface & Responsive Layout Engineering
* **Translucent Floating Command Bar:**
  * Use `backdrop-filter: blur(20px)` with hardware layer isolation (`transform: translateZ(0)` / `will-change: transform`) to prevent scrolling compositing lag on mobile WebKit/Android.
  * Always provide fallback: `@supports not (backdrop-filter: blur(20px)) { background: #08080C; }`.
* **Dual-Mode Order Ledger Transformation:**
  * **Desktop (>=1024px):** 2-column split grid with sticky live order ledger on the right rail.
  * **Mobile (<768px):** Transform ledger into a floating bottom action summary bar with a swipeable/tap-to-expand bottom sheet drawer. Never force multi-column stacking beneath the primary wizard.
* **Anti-Silent-Clipping Mobile Layout Rule:** Never use `overflow-x: clip` or `overflow-x: hidden` on root containers (`.app-shell`, `.hero-panel`) to mechanically force zero horizontal scroll. Doing so silently slices off visible headings, body text, and quick tags on 320px–390px viewports. Instead:
  - Use fluid typography with `clamp()` (e.g. `clamp(1.125rem, 4.5vw, 2.25rem)`).
  - Apply `flex-wrap: wrap` on badge rows and status indicators.
  - Wrap quick-filter chips in a horizontal scrolling track (`overflow-x: auto`) with a gradient fade mask (`mask-image: linear-gradient(to right, black 85%, transparent 100%)`).
* **Touch Target & Viewport Floor:**
  * Maintain strict 44x44px minimum hit bounding boxes for all interactive chips, payment channels, and pills.
  * Pad floating mobile action bars with `bottom: calc(12px + env(safe-area-inset-bottom, 0px));` to prevent collision with iOS/Android OS gesture navigation bars.
  * Provide bottom buffer padding on main scroll containers (`padding-bottom: calc(88px + env(safe-area-inset-bottom, 0px));` on mobile, `padding-bottom: 110px` on 768px tablet) to prevent floating docks or cartridge reels from colliding with or occluding sticky action bars.
  * Hide or collapse floating action bars when text inputs are focused (`focusin`/`focusout`) to prevent virtual keyboard occlusion.
  * Wrap all ambient glow and background grids in `overflow: hidden; contain: paint; pointer-events: none;` to eliminate horizontal scrollbar defects on 360px–390px viewports.
