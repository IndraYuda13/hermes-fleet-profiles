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

## 2. Benchmark Visual Tokens (Warm Dark / Swiss Minimalist)
* **Base Canvas:** Warm Dark `#111110` (replaces harsh cold blues and pure blacks).
* **Surface Hierarchy:** Surface `#1a1a18`, Surface-2 `#222220`, Surface-3 `#2c2c29`.
* **Borders:** Subtle `rgba(236, 235, 231, 0.09)` (`--border`) & `rgba(236, 235, 231, 0.18)` (`--border-strong`)
* **Accents:**
  - Primary Action / Focus: Warm Forest Green / Mint `#3ba07f` / `#12694f` (replaces neon purple/indigo).
  - Discount Tag: Terracotta / Coral `#d1684f` / `#b3402a`.
  - Star Ratings: Warm Amber `#e3b45c`.
* **Glassmorphism:** `mat-func` floating pill header and mobile bottom dock (`backdrop-filter: blur(24px) saturate(1.8)` with subtle 1px specular border).

## 3. Macro Layout Principles
* **2-Column Desktop Grid:** 264px sticky filter sidebar on the left (categories with count badges, platform checkboxes, price range slider, rating filters) + responsive 3-4 column catalog grid on the right.
* **Mobile Ergonomics:** Floating rounded-full bottom dock (`[ Beranda ] [ Aplikasi ] [ Promo ] [ Keranjang ] [ Cari ]`) for one-handed touch navigation.
