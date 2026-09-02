# Digital License & SaaS Subscription Marketplace UX Patterns

Standardized patterns for high-converting digital license, app subscription, and software voucher web stores with in-place micro-configurators and express QRIS fulfillment.

---

## 1. Inline Micro-Variant Product Card Configurator

### The Problem
Traditional digital product stores force users into deep product detail pages (PDP) or heavy multi-step modal dialogs just to see pricing for different durations (e.g. 1 Bulan vs 1 Tahun) or account types (Private vs Shared), killing browse-to-buy velocity.

### Standardized Solution
Embed interactive variant selectors directly on catalog cards:
* **Duration Chips:** 3-4 compact pill buttons (`1 Bulan`, `3 Bulan`, `1 Tahun`, `Lifetime`) with active spring states.
* **Account Type Toggle:** Segmented toggle (`Private (Email Pribadi)` vs `Shared (Hemat)`).
* **Instant In-Place Recalculation:**
  * Active price string (`JetBrains Mono` with `tabular-nums`) smoothly transitions via opacity + scale shift.
  * Crossed-out original price and dynamic discount badge (`HEMAT 40%`) update without DOM re-renders.
  * Stock availability badge (`Ready 18 Akun` vs `Sisa 2 Akun`) updates live based on selected variant.
* **Direct Express CTA:** Clicking `[ ⚡ Beli Kilat ]` captures the exact active variant state directly into the 1-page checkout drawer.

---

## 2. 4-Stage Simulated QRIS Fulfillment State Machine

### Flow Architecture
```
[ STAGE 1: ORDER SUMMARY & QRIS DISPLAY ]
        │
        ▼ (Dynamic QR code generated with 3-digit unique fee + 5:00 countdown)
[ STAGE 2: WAITING FOR QRIS SCAN ]
        │
        ▼ (Simulated / Webhook trigger)
[ STAGE 3: VERIFYING MUTATION & ALLOCATING ENCRYPTED VAULT ]
        │
        ▼ (2.5s simulated laser scan + DB pool claim)
[ STAGE 4: LICENSE DELIVERED & CREDENTIALS VAULT ]
```

### Stage Specifications:
1. **Waiting for Payment:**
   - Visual dynamic QRIS code with official badge.
   - Exact payment total with unique code (e.g. `Rp 45.312`).
   - Countdown timer in `JetBrains Mono`: `04:58` with pulsing amber warning ring when `< 02:00`.
   - Demo Mode Trigger: `[ ⚡ Simulasikan Pembayaran QRIS (Demo) ]` for instant automated/reviewer verification.
2. **Verifying & Allocating:**
   - Laser scanner overlay across QR code.
   - Monospace telemetry log ticker:
     ```text
     > Mutasi QRIS BCA/GOPAY Terdeteksi... [OK]
     > Verifikasi nominal Rp 45.312... [VALID]
     > Mengambil license key dari encrypted vault...
     ```
3. **License Delivered & Credentials Vault:**
   - Confetti burst / celebratory emerald checkmark.
   - Monospace Invoice ID with 1-click copy: `#INV-20260902-8842`.
   - **Credential Vault Box:**
     - User ID / Email: `user@domain.com` (1-click copy)
     - Password / License Key: `AURA-PRO-9842-X781` (1-click copy + toggle show/hide)
     - Expiration & Warranty Date.
     - Login & Setup Guide accordion.
   - Dual actions: `[ 📋 Salin Semua Akun & Lisensi ]` + `[ 💬 Kirim Backup ke WhatsApp ]` (direct API link).

---

## 3. Brand-Derived Ambient Radial Glows
* Each product card features a subtle, hardware-accelerated top-right radial glow corresponding to genuine vendor branding:
  - OpenAI ChatGPT: `rgba(16, 163, 127, 0.15)`
  - Anthropic Claude: `rgba(217, 119, 87, 0.15)`
  - Midjourney: `rgba(129, 140, 248, 0.15)`
  - Cursor AI: `rgba(56, 189, 248, 0.15)`
  - Netflix: `rgba(229, 9, 20, 0.15)`
  - Spotify: `rgba(29, 185, 84, 0.15)`
* Use `contain: paint; pointer-events: none;` on glow overlays to prevent GPU memory bloat or hit-test interception.

---

## 4. Mobile Bottom Pill Dock Ergonomics
* Viewports `< 768px` render a fixed capsule dock (`fixed bottom-4 left-1/2 -translate-x-1/2 z-40`):
  - `[ 🏠 Katalog ]` (Smooth scroll anchor)
  - `[ ⚡ Cek Pesanan ]` (Launches order lookup modal)
  - `[ 💬 Bantuan WA ]` (Direct WhatsApp CS link)
* Ensure catalog body has `padding-bottom: 7rem` (`pb-28`) so bottom cards are never covered by the dock.
