---
name: fintech-checkout-ux-architecture
description: High-converting fintech checkout and real-time topup UX.
version: 1.1.0
metadata:
  hermes:
    tags: [fintech, checkout, ux-architecture, state-machine, payment-drawer, anti-slop, topup, brand-assets]
    category: custom
---

# Fintech & Digital Top-Up Checkout UX Architecture

Standardized patterns and state machines for building high-conversion, real-time digital cashiers and top-up experiences, synthesized from live multi-peer architecture consultations (Product Design, Backend, Frontend, and Security).

> **Supporting References:**
> - `references/tactile-interactivity-patterns.md` — Dynamic micro-interactions and tactile feedback.
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
* **Avoid Heavy 3D WebGL Heroes:** Replace 300KB+ Three.js canvas backgrounds with SVG vector graphics and GPU-accelerated CSS glow (`contain: strict;`) to keep FCP < 800ms on 4G mobile.
* **Surface Discipline & Specular Rims:** High-contrast dark surfaces with vibrant citrus accents strictly reserved for active states, CTA, and verified feedback. Replace 4px hard black offset shadows (`box-shadow: 4px 4px 0 #000`) with 1px specular rim borders (`rgba(255, 255, 255, 0.08)`) and layered luminance depth.
* **Zero Jitter via Tabular Numerics:** Enforce `font-variant-numeric: tabular-nums` on all pricing calculations, fee breakdowns, and `MM:SS` countdown timers to eliminate layout shifts during polling updates.

---

## 5. Ergonomic Surface & Responsive Layout Engineering
* **Translucent Floating Command Bar:**
  * Use `backdrop-filter: blur(20px)` with hardware layer isolation (`transform: translateZ(0)` / `will-change: transform`) to prevent scrolling compositing lag on mobile WebKit/Android.
  * Always provide fallback: `@supports not (backdrop-filter: blur(20px)) { background: #08080C; }`.
* **Dual-Mode Order Ledger Transformation:**
  * **Desktop (>=1024px):** 2-column split grid with sticky live order ledger on the right rail.
  * **Mobile (<768px):** Transform ledger into a floating bottom action summary bar with a swipeable/tap-to-expand bottom sheet drawer. Never force multi-column stacking beneath the primary wizard.
* **Touch Target & Viewport Floor:**
  * Maintain strict 44x44px minimum hit bounding boxes for all interactive chips, payment channels, and pills.
  * Pad floating mobile action bars with `bottom: calc(12px + env(safe-area-inset-bottom, 0px));` to prevent collision with iOS/Android OS gesture navigation bars.
  * Provide bottom buffer padding on main scroll containers (`padding-bottom: calc(88px + env(safe-area-inset-bottom, 0px));`) to prevent floating dock occlusion over bottom-most receipts or action buttons.
  * Hide or collapse floating action bars when text inputs are focused (`focusin`/`focusout`) to prevent virtual keyboard occlusion.
  * Wrap all ambient glow and background grids in `overflow: hidden; contain: paint; pointer-events: none;` to eliminate horizontal scrollbar defects on 360px–390px viewports.
