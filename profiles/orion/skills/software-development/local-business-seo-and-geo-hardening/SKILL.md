---
name: local-business-seo-and-geo-hardening
description: Use when optimizing local business SEO, GEO, and GBP.
version: 1.0.0
author: Orion Fleet Lead
license: MIT
metadata:
  hermes:
    tags: [seo, geo, local-business, google-business-profile, opengraph, meta-cache, json-ld]
    category: software-development
---

# Local Business SEO, GEO & Profile Hardening Standard

## When to Use

Use this skill when:
1. Setting up, auditing, or optimizing local service businesses (e.g. barbershops, clinics, custom merchandise, salons, local agencies) for Google Search, Google Maps (GBP), and AI Overviews / Perplexity (GEO).
2. Creating and synchronizing unified JSON-LD schemas (`LocalBusiness`, `BarberShop`, `hasOfferCatalog`, `FAQPage`, `GeoCoordinates`).
3. Resolving OpenGraph preview cache staleness across Meta platforms (Threads, WhatsApp, Instagram, Facebook).
4. Troubleshooting Google Business Profile (GBP) validation errors (such as false-positive URL detection in descriptions).

---

## 1. Google Business Profile (GBP) Validation & Keyword Rules

### A. URL Detection False-Positive Trap in Descriptions
Google rejects descriptions containing URLs or domains (`URL tidak diizinkan di sini`). However, Google's regex parser frequently flags innocent punctuation as URLs if numbers/letters touch periods without spaces:
* ❌ `Jl. Kesehatan Raya No.2A` ➔ Regex detects `.2A` as a TLD/URL.
  * ✅ **Fix:** Write `Nomor 2A` or `No. 2A`.
* ❌ `09.00 – 21.00 WIB` ➔ Periods in timestamps get flagged as IP/domain notation.
  * ✅ **Fix:** Use standard colon format `09:00 – 21:00 WIB` or `jam 09:00 sampai 21:00 WIB`.
* ❌ Do not write domain names (e.g. `www.example.id`) in the description text.

### B. High-Converting Local Business Description Template (<= 750 Chars)
Structure the first 200 characters to be above-the-fold with strong geographic anchors and price cues:
```text
[Business Name] adalah [Kategori Bisnis] premium di [Kawasan / Sektor], Jalan [Nama Jalan] Nomor [Nomor], [Kota]. Kami menghadirkan [3-4 Layanan Utama] mulai [Harga Awal] ribu rupiah.

Didukung staf profesional berpengalaman, tempat bersih ber-AC, dan suasana nyaman. Melayani pelanggan dari area [Kawasan 1], [Kawasan 2], dan sekitarnya.

Buka Setiap Hari: jam 09:00 sampai 21:00 WIB
Melayani Walk-in dan Reservasi
```

### C. Contact Links Calibration
1. **Primary Website:** Use the exact canonical HTTPS format with `www.` if configured: `https://www.example.id/`.
2. **Direct Menu/Service Link:** Use deep anchor links: `https://www.example.id/#pricing` (enables Google Maps "Lihat Menu/Harga" action button).
3. **Instant WhatsApp Link:** Use `https://wa.me/628xxxxxxxxx`.

---

## 2. Meta Platforms OpenGraph Cache Scraper Flush

When social media platforms (Threads, WhatsApp, Instagram, Facebook) display outdated preview images/titles after HTML changes:
1. Meta stores OpenGraph link previews in an edge cache that does not auto-refresh on file change.
2. Force a server-side cache refresh via **Facebook Sharing Debugger**:
   - URL: `https://developers.facebook.com/tools/debug/`
   - Enter canonical URL (e.g. `https://www.example.id/`) ➔ Click **Debug**.
   - Click **"Scrape Again"** (repeat twice if image does not immediately update).
3. Ignore the non-blocking warning *"Properti yang Diperlukan Tidak Ada: fb:app_id"*.

---

## 3. Local Schema & GEO BLUF Box Layout

### A. Symmetrical BLUF Container Architecture
To ensure clean visual rendering and AI answer extraction:
```css
.geo-quick-summary {
  background: rgba(22, 22, 22, 0.94);
  border: 1px solid rgba(212, 175, 55, 0.45);
  border-left: 4px solid #d4af37;
  border-radius: 8px;
  padding: 16px 20px;
  margin: 25px auto 0 auto; /* Horizontal Center Alignment */
  max-width: 780px;
  width: 100%;
  text-align: left; /* Keep internal bullets left-aligned for scannability */
}
```

### B. Master JSON-LD Structure
Always bundle `LocalBusiness` / `BarberShop`, `hasOfferCatalog`, `geo`, `openingHoursSpecification`, and `FAQPage` in one unified `@graph` block.

---

## 4. Single-File Static Packaging & Asset Integrity

When deploying static client deliverables to cPanel / File Manager where users frequently upload only `index.html` without accompanying asset folders:
- **Base64 Inline Fallback:** For critical gallery cards or hero logos, embed processed image data directly as `data:image/jpeg;base64,...` in `src` attributes. This ensures 100% zero-dependency visual rendering even if the user forgets to extract the `assets/` subfolder.
- **Domain Lookups (crt.sh / crt.name):** Ensure domain names entered into certificate search engines do NOT contain trailing slashes or protocol schemes (`U+002F` / `disallowed rune` error). Strip `https://`, `http://`, and trailing `/` before querying.

### C. Gated E-Catalog vs Instant Download (Anti-Ghosting Funnel)
- **The Price-Shopping Pitfall:** Never provide direct, unauthenticated PDF download buttons on public websites. Visitors will download the price list, compare numbers blindly without understanding material quality differences (e.g. solid plate vs cheap alloy), and ghost the business without leaving contact info.
- **WhatsApp Gated Lead Capture:** Replace direct download buttons with a dedicated WhatsApp trigger: `[ Minta E-Katalog & Price List Lengkap via WhatsApp ]`.
- **Pre-filled Lead Capture Message:** `https://wa.me/628xxxxxxxxx?text=Halo%20PinCustom%2C%20boleh%20minta%20tolong%20kirimkan%20E-Katalog%20PDF%20dan%20Price%20List%20lengkapnya%3F`
- **Follow-up Protocol:** Once the PDF is delivered on WhatsApp, CS engages with the Free Mockup hook within 10–15 minutes: *"Katalognya sudah kami kirim ya kak. Rencana untuk event apa nih kak? Kirimkan logo/desainnya agar kami bantu buatkan digital preview mockup gratis."*

## 5. Headless Chrome PDF Clean Export Standard
When generating client-ready PDFs from HTML via headless Chromium (`google-chrome --headless=new --print-to-pdf=...`):
- **Suppress Browser Headers/Footers:** Always include `--no-pdf-header-footer` in the CLI command. This prevents unwanted timestamps, system dates (e.g. `8/30/26, 11:03 AM`), local `file:///` URLs, and raw page titles from appearing on the generated PDF margins.
- **Command Template:**
  ```bash
  google-chrome --headless=new --no-sandbox --disable-gpu --no-pdf-header-footer --print-to-pdf=output.pdf input.html
  ```

## 6. Hardware Modification & Voltage Step-Down Invariants
When adapting or modifying DC power inputs on local networking hardware (e.g. Fiber Optic Media Converters / HTB rated at 5V–6V using 12V adapters):
- **Direct 12V Danger:** Never connect 12V directly to 5V–6V equipment lacking wide-input switching ICs; linear LDO regulators (e.g. AMS1117-3.3) suffer immediate thermal breakdown and destroy 3.3V optical/PHY chips.
- **Buck Converter Requirement:** Always wire an adjustable DC-DC step-down module (e.g. MP1584 Mini, LM2596) calibrated to 5.0V–5.2V before connecting to the board.

## 7. Dual-Track Revenue Recovery & Emergency Cashflow (SEO vs Paid/Direct)
When a local or custom B2B business experiences a sharp drop in revenue:
- **The Pure-SEO Trap:** Organic SEO fixes (Silo architecture, Google Business Profile optimization, schema markup) have an unavoidable crawler latency of **60 to 180 days** before translating into measurable revenue. Relying solely on organic SEO during an active revenue crisis creates severe cashflow insolvency.
- **The Dual-Track Architecture:**
  1. **Track 1: Quick Cashflow (Days 1–14):**
     - **Database Reactivation:** Filter past 6–18 months of WhatsApp/invoice contacts. Run personalized, conversational follow-ups offering mold-fee waivers or repeat-order incentives (Rp 0 CAC, highest conversion).
     - **WhatsApp Speed-to-Lead SLA (< 3 Minutes):** Enforce strict sub-3-minute response times during business hours with consultative questioning (event date, logo file for free mockup) instead of dumping price list PDFs.
     - **High-Intent Google Ads (Rp 30k–50k/day):** Capture active, urgent orders needing delivery within the week using strict Exact/Phrase match and negative keyword shielding.
  2. **Track 2: Sustainable Organic Foundation (Days 30–90):**
     - Dedicated product sub-landing pages (`/pin-enamel/`, `/pin-kuningan/`, `/corporate-b2b/`).
     - Google Business Profile weekly photo updates, NAP synchronization, and localized review gathering.
     - 10 B2B Sample Boxes shipped proactively to event organizers and procurement teams.

## 8. CSS Stacking Context & Hero Background Image Overlays
When fixing black or missing background photos in hero sliders/carousels:
- **Root Cause of "Black Screen" Hero:** If `.carousel-background img` lacks explicit absolute positioning, `width: 100%; height: 100%; object-fit: cover;`, and an explicit z-index layer, dark overlay pseudoelements (`::before { background-color: #000; }`) will stack over the image container, completely masking the photography.
- **The JS-Deletion Race Condition:** Many legacy carousel scripts (e.g. `BizPage/main.js`) actively execute `$(this).children(".carousel-background").remove()` and convert the `<img>` tag into an inline `background-image: url(...)` on the `.carousel-item` container. If this script is deferred or delayed, the browser renders a jet-black background (`#000`) before JavaScript fires. Furthermore, applying an inline linear gradient on `::before` (e.g. 55%–75% black) on top of the inherited `rgba(0,0,0,0.7)` creates an opaque double-overlay that obliterates background photography on mobile LCD screens.
- **Bulletproof Zero-Blackout Solution:**
  1. Define inline `style="background-image: url('img/...');"` directly on `<div class="carousel-item active">` in the static HTML itself. This guarantees zero-delay image rendering on initial page paint before JS executes.
  2. Maintain a balanced single gradient overlay (`rgba(0,0,0,0.35)` to `rgba(0,0,0,0.65)`) with `pointer-events: none;` so highlights and sparks remain vivid.
  3. Add `padding-top: 60px;` to `.carousel-container` to prevent the fixed header/logo from colliding with the H1 headline.
- **Correct CSS Stacking Structure:**
  ```css
  #intro { position: relative; background: #111; overflow: hidden; }
  #intro .carousel-item {
    width: 100%; height: 100vh; min-height: 560px;
    background-size: cover !important;
    background-position: center center !important;
    background-repeat: no-repeat !important;
    position: relative;
  }
  #intro .carousel-item::before {
    content: '' !important;
    background: linear-gradient(180deg, rgba(0,0,0,0.40) 0%, rgba(0,0,0,0.65) 100%) !important;
    position: absolute; inset: 0; z-index: 2; pointer-events: none;
  }
  #intro .carousel-container {
    position: absolute; inset: 0; z-index: 3;
    display: flex; align-items: center; justify-content: center;
    padding-top: 60px;
  }
  #intro .carousel-background { display: none !important; }
  ```

## 9. Sub-Landing Page Silo Architecture & Asset Resilience
When building targeted product sub-pages (e.g. `/pin-enamel/`, `/pin-kuningan/`, `/corporate-b2b/`):
- **Silo Navigation & Schema:**
  - Build standalone landing pages targeting high-intent local transactional keywords (e.g. `bikin pin enamel jakarta`, `hard enamel pin custom`).
  - Bundle `Product` (AggregateOffer with realistic price tiers) and `FAQPage` JSON-LD schemas into `@graph` to capture Google Rich Snippets.
  - Implement Hard vs Soft Enamel educational comparison sections to lower bounce rate and guide non-technical B2B buyers.
- **Fail-Safe Asset Fallbacks for Nested Directories:**
  - When assets live in the parent root (`/img/portfolio/`, `/img/clients/`), relative paths like `../img/...` frequently break during CDN routing, preview servers, or standalone sub-folder testing.
  - Always implement self-healing image tags with inline fallback handlers:
    ```html
    <img src="/img/portfolio/1.png" onerror="this.onerror=null; this.src='https://www.example.com/img/portfolio/1.png';" alt="...">
    ```
  - For YouTube Shorts embeds in responsive cards:
    - Avoid complex autoplay/playlist query strings (`autoplay=1&mute=1&playlist=...`) which trigger Google iframe origin blocks and render "This video is unavailable".
    - Use clean standard embed URLs: `https://www.youtube.com/embed/<VIDEO_ID>?rel=0&modestbranding=1`.
    - Ensure floating CTA buttons have appropriate z-index and viewport margin so they never obscure video controls or lower text captions on mobile screens.

## 10. Supporting Knowledge Base
- **B2B Scaling, Non-PT Operations & Funnel Repositioning:** See `references/b2b-scaling-and-funnel-repositioning.md` for mathematical blueprints on scaling custom service businesses from Rp 10M retail plateau to Rp 100M/month corporate accounts without requiring a large PT legal entity (operating cleanly as an independent creative studio with SPH/Invoice, 50% upfront DP cashflow rules, and single-price flat catalog structures).
- **Google Ads Low-Cost & Micro-Budget B2B Playbook:** See `references/google-ads-low-cost-b2b-playbook.md` and `references/google-ads-micro-budget-playbook.md` for exact 25-working-day micro-budget allocation models (Rp 500k/month, Max CPC Rp 1.500 cap), 5 golden keyword pairs, negative keyword lists, high-converting RSA copy templates with MOQ pre-filters, and WhatsApp conversion event tracking.
- **Single-Price vs Tiered Wholesale Models & Material Accuracy:** When creating catalogs for manufacturing/workshop owners:
  - Honor the owner's preference for **1 flat price per item (Single Price Edition)** rather than complex multi-tier volume matrices if requested.
  - Verify exact manufacturing methods before writing copy (e.g. distinguishing genuine **solid metal plate press/stamping/etching** from **casting/cor**; never label plate items as casting/cor).
  - Never inject unverified product categories (e.g. medals or lanyards) into client deliverables unless explicitly confirmed in the owner's product line.
- **Email & Social Footprint Triage (Fraud OSINT):** See `references/email-and-social-footprint-triage.md` for MD5 Gravatar lookups, multi-platform username mutation probing (Instagram, Pinterest, TikTok, Telegram), fraud persona classification, and KYC de-anonymization workflows.

