---
name: dailyfinance-seo-mastery
description: "Use when writing Dailyfinance.id SEO blog articles."
version: 1.23.0
author: ORION
license: proprietary
metadata:
  hermes:
    tags: [seo, dailyfinance, google-search-central, content-publishing, ai-overview, threads, social-media]
    related_skills: [editorial-news-publishing-v2, generative-engine-optimization, editorial-news-publishing, editorial-carousel-craft]
---

# Dailyfinance.id SEO Mastery (Google Search Central Standard)

## When to Use

Load this skill whenever the task involves:
- Writing or publishing a new blog article on Dailyfinance.id.
- Optimizing existing pages for Google Search, AI Overviews, or Google Discover.
- Auditing and repairing broken, cut-off, or incomplete legacy articles (e.g. truncated product reviews, missing template sections).
- Authoring numbered review articles ("N Pinjol Legal", comparison tables, vetting against `fintech-db.js`).
- Auditing and optimizing interactive site directories and verification utilities (e.g. OJK P2P lending directory `cek-legalitas-pinjol-ojk.html`, `kalkulator-bunga-pinjol-ojk.html`).
- Auditing on-page SEO (title links, snippets, schema, robots directives, image sizing, favicon declarations).
- Diagnosing and remediating SERP display issues, including generic gray globe favicon fallback in Google Search results.
- Executing the publication pipeline (`publisher_engine.py` / `builder_hotmagazine.py`).
- Creating high-engagement social media posts (Threads, X) or visual simulation cards promoting Dailyfinance.id utilities (kalkulator bunga pinjol, rute Transjakarta).
- Designing, streamlining, or auditing viral social landing funnels (e.g. "Claim Dana Kaget" / `jajan-gratis.html`).
- Auditing social media giveaway/bounty respondents to filter serial beggars ("ngemis online") and select authentic recipients.
- Handling sensitive emotional personal finance topics (e.g. debt crisis, pinjol confessions, family budgeting conflicts).
- Authoring, auditing, or expanding debt collector response templates, dispute scripts, and copy-pasteable negotiation tools.
- Authoring in-app fintech onboarding, merchant registration (QRIS, DANA Bisnis, e-wallet merchant), and procedural step-by-step guides.

## 0. Linked Technical Reference

- [Google Search Central Appearance Specifications](references/google-appearance-specs.md): Full technical thresholds for Title Links, Snippet controls (`max-image-preview`, `data-nosnippet`), AI Overview query fan-out mechanics, Discover image dimensions (≥1200px, 300k px), JSON-LD entity author rules, and Google SERP Favicon specifications (stable URLs, multi-res ICO, globe fallback avoidance).
- [Competitive Advantage & Content Moat](references/competitive-advantage-and-content-moat.md): Strategic differentiation, Utility-First Media architecture, and practical finance query targeting.

## 1. End-to-End Publication Procedure

Follow these steps in strict sequence for every new article or major update:

### Step 1: Content Planning & Query Fan-Out
1. Formulate a high-CTR title adhering to: `[Angka/Fakta Spesifik] + [Manfaat Utama] + [Tahun 2026] + [Bonus/Kurikulum]`.
   - Length: 50–65 characters. Keep core hook in the first 50 chars to prevent mobile SERP truncation.
   - Suffix ` • DailyFinance.id` is automatically appended by `publisher_engine.py`.
2. Craft a unique 140–160 character meta description. Summarize actionable data (modal, profit margin, payback time, concrete steps) as a SERP pitch.
3. Identify 3–4 sub-intent queries to answer in the FAQ section to capture Google AI Overview query fan-out branches.
4. When adapting source material from social media (Instagram infografis, X threads), cross-reference with primary corporate investor relations, regulatory filings (OJK/BI), or official press releases to obtain exact verified metrics (CASA, NPF, CoF, YoY growth) required for EEAT credibility.
5. **Thematic Topic Cluster Siloing & Sister Article Cross-Linking**: Identify existing articles within the same thematic silo (e.g., when publishing a gig-economy side job guide like ojol/ShopeeFood, locate the regulatory article `perpres-potongan-ojol-maksimal-8-persen-kemenhub-resmi-berlaku-juli-2026.html`). Interlink between cluster siblings in addition to site utilities (`kalkulator-bunga-pinjol-ojk.html`, budgeting tools). This internal semantic linking cements topical authority and keeps crawl paths dense.

### Step 2: Editorial Drafting & On-Page Assembly
1. **Direct Answer / BLUF Box**: Open within the first 100 words with a dark gradient card (`<div class="p-4 rounded-4 mb-4 text-white" style="background: linear-gradient(...)">`) featuring a 3-column metric summary (Modal, BEP/Margin, Kunci Sukses).
2. **Data & Comparison Tables**: Provide at least 1–2 native semantic `<table>` elements with explicit headers (`<thead>`, `<th>`) for costs, specifications, or schedules.
3. **Images, Attribution & Discover Readiness**:
   - Hero and content images must be minimum 1,200px wide, 16:9 ratio, WebP format (~800px-1200px, quality 80–82).
   - **EXIF Orientation Auto-Normalization**: Always execute `from PIL import ImageOps; img = ImageOps.exif_transpose(img)` immediately after opening candidate image files before cropping, resizing, or converting to WebP. User-contributed photography from Wikimedia Commons or smartphone uploads often embed EXIF Orientation metadata (e.g. orientation 6 or 8); converting them without transposing causes browsers to render images sideways (90° rotated) or upside down on the live page.
   - **Distinct & Relatable Image Assets**: Never re-use the hero/featured image inside the body text. Every body image slot must be a unique asset illustrating an operational step, product, or sub-topic. Choose relatable, visually appealing compositions (warm flat-lays, colorful objects, authentic tools) that make people actually want to read, rather than cold, sterile spreadsheets or generic stock photos.
   - **Cultural & Contextual Authenticity**: Ensure imagery matches Indonesian cultural reality (e.g. genuine Indonesian rupiah currency, local planners/equipment) instead of ambiguous foreign stock photos of unidentified people or currencies that break reader trust.
   - **Editorial Hero vs. Product Card Separation**: The hero/featured image must ALWAYS be an authentic editorial or lifestyle photograph (e.g. human hands setting an AC remote, an authentic room setup, or an editorial problem-solving scene). NEVER use commercial marketing banners, brand ambassador posters, or promotional graphics with sale badges and marketing slogans ("SUPER FAST COOLING", logos, retail pricing) as the article hero or homepage thumbnail. Commercial product photography belongs strictly INSIDE the article body within the mid-content affiliate product card.
   - **Subject Framing & Active Zone Cropping**: Wide landscape stock photos (e.g. parks, playgrounds, commercial streets) often place the relevant activity or equipment in a small fraction of the frame. Crop tightly to the active subject zone (e.g. sandbox play area, operational tools) before resizing to standard 960–1,200px WebP; uncropped wide scenery gets visually interpreted by readers and Discover algorithms as generic landscape, diluting topical relevance.
   - **Caption Fidelity to Verified Visuals**: Ensure `<figcaption>` copy precisely matches what is inspectably visible in the image. If a photo captures an ambient playground sandbox rather than a clear close-up of a specific mechanical digger, describe it accurately (e.g. "Area bermain pasir anak di taman rekreasi &mdash; konsep yang menginspirasi wahana rental excavator mini") instead of over-claiming unverified equipment details that visual inspection will contradict.
   - **Image Sourcing & Resolution**: Sourced images must be minimum 960px to 1,200px wide (StockSnap 960w, Flickr high-res CC, Openverse, or Shopee CDN `@resize_w1200_nl`), WebP format, quality 80–85. When fetching from StockSnap CDN, always pass a desktop browser User-Agent to avoid 403 Cloudflare/CDN blocks. When sourcing from Wikimedia Commons, include an informative User-Agent (`User-Agent: DailyFinanceBot/1.0`) and avoid burst requests to prevent HTTP 429 rate limiting. For company-story articles, a brand-owned upload on Commons (PT upload under CC BY-SA) is the most credible hero/body source; credit it with the author/uploader line and license exactly as shown on the file page.
   - **Mandatory Source Attribution Standard**: Every image (hero and body) must feature a centered source credit specifying platform, author/creator, and exact license: `<figcaption class="text-center text-muted fst-italic small mt-2">Deskripsi visual relevan. Foto: [Platform] ([Nama Kreator/Dokumentasi], lisensi [CC0/CC BY/...])</figcaption>`. Generic tags like "Dok. Pribadi" on external photos are strictly forbidden.
   - Save local assets to `/root/dailyfinance_web/assets/img/` or `assets/img/blog/`.
   - **User-Supplied Photo Below 1,200px**: Check `Image.open(path).size` before converting. Below 1,200px, upscaling only meets the Discover threshold on paper; small text (logos, plates) softens at high DPI. Tell the user the source size and ask for a high-resolution original before publishing. Use the upscale only as a documented stopgap and say so in the reply.
4. **Emotional & Sensitive Personal Finance Architecture (Debt, Crisis, Family)**:
   - **Empathetic Non-Judgmental Tone**: Avoid lecturing or moralizing; write as a calm, pragmatic advisor who understands the emotional weight and stigma of financial distress.
   - **Copy-Pasteable Dialogue Scripts**: In articles addressing conversations with parents, spouse, or creditors, provide verbatim conversational templates inside distinct semantic cards/blockquotes (`<blockquote>`). Stressed readers search specifically for *what exact words to say* to defuse conflict. Provide tailored scripts for different counter-parties (e.g. Orang Tua vs. Pasangan).
   - **Constructive Visual Progression**: Avoid sensational distress shots (crying, despair, panic) or piles of cash. Use a three-stage constructive narrative: (1) Warm interpersonal conversation hero (e.g. two coffee mugs on a table symbolizing honest dialogue), (2) Methodical debt inventory (e.g. notebook checklist showing organized calculations), (3) Actionable resolution roadmap (e.g. writing repayment commitments).
   - **Integrated Utility Funnel Progression**: Anchor emotional topics in practical site utilities sequentially:
     1. Pre-conversation calculation: Link to `kalkulator-bunga-pinjol-ojk.html` to establish factual total obligations.
     2. Legal verification: Link to `cek-legalitas-pinjol-ojk.html` to separate regulated entities from illegal operations.
     3. Conflict & debt collector mitigation: Link to `panduan-galbay-pinjol-ojk.html` and quote statutory legal rights (UU Pelindungan Data Pribadi / SEOJK).
   - **Support & Crisis Disclaimer**: Conclude sensitive debt/stress articles with a mental health support note alongside the standard regulatory disclaimer.
5. **Actionable Template & Script Architecture ("+ Template" Title Contract)**:
   - Whenever an article title or description promises templates (`+ Template`, `+ Contoh Pesan`, `+ Format Surat`), provide an exhaustive, ready-to-copy library covering the full lifecycle of scenarios (minimum 6–8 distinct situations):
     1. First response demanding identity and collector credentials (SPPI/AFPI).
     2. Tenor restructuring requests to reduce monthly installments.
     3. Proposing small weekly or staggered installments.
     4. Promising post-payday settlement with a condition against emergency contact harassment.
     5. Demanding written-only communication to halt disruptive repetitive calls.
     6. Formal reprimand against illegal collector intimidation/doxxing (citing UU PDP No. 27/2022 & POJK No. 22/2023).
     7. Official violation reporting script for OJK 157 and Satgas PASTI with evidence submission.
     8. Requesting an itemized official billing breakdown before making any payment.
   - House each template in a styled background block (`background: #f8fafc`, distinct colored left border) with standardized placeholder bracket tokens (`[Nama]`, `[Nomor Pinjaman]`, `[Jumlah]`).
   - Equip each template block with a native 1-click clipboard button:
     ```html
     <button class="btn btn-sm btn-outline-secondary py-1 px-3" onclick="copyTemplate('tmp1')">📋 Salin Template</button>
     ```
     With lightweight vanilla JS supporting visual feedback (`✅ Tersalin!` reverting after 1.6s).
6. **Social Share Button Architecture & First-Position Placement**:
   - In both top and bottom `.share-buttons-list` blocks, position **Threads** as the **first item** (`.share-btn-threads`), preceding WhatsApp, Telegram, X, Facebook, and Salin Link.
   - On mobile screens (≤390px), horizontal button lists wrap into two rows. Placing Threads further down in the sequence pushes it to the second row or past screen boundaries, leading users to believe the Threads integration is missing.
   - Encode article title and canonical URL cleanly in the share target: `https://www.threads.net/intent/post?text=[EncodedTitle]%20[EncodedURL]`.
7. **FAQ Section**: Build 4 Q&As with self-contained, 40–60 word direct answers. Pass them to `faqs` in `publisher_engine.publish_article()`. The engine automatically injects both the `FAQPage` JSON-LD schema AND the pre-rendered visible `<div class="accordion accordion-faq-static">` cards directly into the page DOM. Ensure strict opening and closing tag symmetry (`<h4>...</h4>`, never closed with mismatched tags like `</h2>`).
8. **High-CTR / High-Conversion Affiliate Integration (AdSense-Safe)**:
   - Mark every commercial link with `rel="sponsored nofollow"` and `target="_blank"`.
   - Insert an explicit editorial disclosure box («Catatan Redaksi: Link terafiliasi...») before the first product showcase.
   - Embed at least two conversion touchpoints:
     1. One mid-content featured product card (`.card`) placed right after explaining the practical necessity or equipment requirement.
     2. One closing action card before the FAQ.
   - **Mobile Button Ergonomics**: Ensure affiliate CTA buttons span full-width (`w-100` / width ≥300px, height ≥40px) on mobile viewports with bold actionable copy and directional glyphs (`🛒 Cek Harga... →`) for seamless thumb tapping.
   - **Never expose marketplace brand names in visible CTA copy** (user decision 2026-10): button labels must read `🛒 Cek Harga Terbaru →` / `🛒 Lihat Pilihan Kolam →` / `🛒 Cek Harga M135H →` / `🛒 Cek Harga Jaketnya →` / `🛒 Cek Harga & Stok Mesinnya →` WITHOUT the word "Shopee". Visible "di Shopee" text makes the page read as obvious affiliate content and primes readers to distrust the recommendation. Keep the marketplace only inside the `href` + `rel="sponsored nofollow"` (legal/SEO compliance) while the visible copy stays neutral and curiosity-driven. The only allowed visible "Shopee" mentions are factual editorial comparisons (e.g. "SPinjam Shopee" in a fintech review, "ShopeeFood" in a gig economy guide) and legal trademark lists in disclaimer.html.
   - **Affiliate Link Validation Gate (before any link enters HTML)**:
     1. Obtain each shortlink as text from the source (copy/paste or a text export). Never transcribe short-link codes from a screenshot by vision alone: `q`/`g`, `8`/`6`, `l`/`1` are routinely misread. If only an image exists, ask the user for the text.
     2. Probe each code: `curl -sL -A "WhatsApp/2.23.20.0" -o /tmp/x.html -w "%{url_effective}" https://s.shopee.co.id/<code>`. Dead = final URL `https://shope.ee/error_page`; live = an `og:title` meta tag is present (`grep -o 'og:title" content="[^"]*' /tmp/x.html`).
     3. Confirm the `og:title` product matches the article promise (e.g. a "planner keuangan" article must not silently link a generic notebook). On mismatch, report it to the user before publishing.
     4. For a dead link, substitute a Shopee search fallback and tell the user which links were replaced and why.
   - Limit product cards to 4–8 relevant recommendations with distinctive call-out badges.
9. **Numbered List & Review Architecture ("N [Items]" Title Contract)**:
   - **Exact Count Delivery**: When a title or headline promises a specific count (e.g., "Review 7 Pinjol Legal Bunga Terendah", "5 Langkah Bebas Galbay"), every single item from 1 to N must be fully authored with an individual evaluation card, official credentials, pros, cons, and operational terms. Never stop after item #1 or leave the remaining items truncated.
   - **Grounding in Internal Database (`fintech-db.js`)**: For all fintech/P2P lending evaluations, strictly cross-reference company names, official OJK licenses (`KEP-xx/D.05/xxxx`), categories (multiguna vs. produktif), interest caps (0.1%/day vs 0.3%/day), and operational limits against `assets/js/fintech-db.js` (95 verified entries). Never invent license numbers or cite obsolete pre-SEOJK 19/2023 regulations.
   - **Strict Sub-Category Alignment with Search Intent**: When authoring consumer personal loan ("pinjol") roundups, filter `fintech-db.js` strictly by `Multiguna Konsumtif`. Never mix in business/SME financing platforms (`Produktif UMKM`, e.g. Amartha) into a consumer personal loan list—their borrower requirements (business legality, financial statements, PO analysis) and multi-day disbursement make them irrelevant to consumer borrowers looking for personal loans.
   - **Entity & Brand Precision**: Never conflate distinct corporate entities or associate one brand's product with an unrelated P2P lender (e.g. Tunaiku belongs to Bank Amar Indonesia, not PT Amartha Mikro Fintek).
   - **Synchronized Count Adjustments Across All Surfaces**: If an item is added or removed from a numbered list (e.g. 7 down to 6), update every single surface in lockstep: `<title>`, breadcrumb active item, `<h1>`, meta description, introductory lead copy ("Ketujuh" → "Keenam"), table headings, and card IDs. Never leave mismatched count numbers on any surface.
   - **Unified Semantic Comparison Table**: Every comparative review article must provide a consolidated `<table>` benchmarking all N entries across critical decision dimensions (Platform, Izin OJK, Suku Bunga Maksimal, Plafon Pinjaman, Tenor, Kecepatan Pencairan). This gives readers the immediate scannable comparison expected from review roundups and feeds structured table data to Google AI Overviews.
   - **Utility Retention Bridge**: Embed an action card directly below the comparison table guiding readers into `kalkulator-bunga-pinjol-ojk.html` ("Hitung Total Biaya dengan Kalkulator OJK sebelum memutuskan") so visitors can verify real repayment numbers before submitting loan applications.
   - **Practical FAQ Friction Resolution**: Provide 4 targeted static FAQ entries resolving real user concerns (e.g., reasons why approved interest rates exceed advertised starting rates, methods for detecting cloned/fake apps on app stores, data protection and harassment protections under UU PDP).
10. **Internal Linking**: Embed ≥3 contextual internal links pointing to Dailyfinance utilities (e.g., Transjakarta route explorer, kalkulator, or related financial guides).
11. **App-Based Fintech & Merchant Onboarding Architecture (Prerequisite Tiers & UX Flow)**:
   - When authoring step-by-step guides for in-app financial features or merchant services (e.g. DANA Bisnis, QRIS usaha, GoPay Merchant, bank digital onboarding):
     - **Prominent Prerequisite Tier Alert**: Never bury account tier prerequisites (e.g. Akun Premium, KYC Level 2, e-KTP validation). Highlight them in a distinct alert box (`<div class="alert border-0 rounded-4 p-4 my-4" style="background: #fff7ed; border-left: 5px solid #f97316 !important;">`) positioned immediately before or adjacent to the tutorial steps. Explain why: without the verified/premium tier, the merchant/business tab is either hidden or inaccessible, causing reader drop-off and confusion.
     - **Strict UX Navigation Alignment**: Mirror the official in-app navigation hierarchy in chronological order: (1) Buka aplikasi (versi terbaru), (2) Masuk menu navigasi utama (misal tab "Saya"), (3) Verifikasi status akun (badge PREMIUM aktif), (4) Pindah/toggle ke profil Bisnis, (5) Mulai formulir pendaftaran ("Daftar Sekarang"), (6) Input legalitas/data usaha & lokasi, (7) Unggah foto tempat usaha & produk, (8) Submit & verifikasi.
     - Never reverse steps (e.g. instructing users to check account status before instructing them to open the app or enter the menu); instructions must match what users experience on screen step by step.
12. **Business Opportunity & Commercial Equipment Architecture ('Paket Usaha' & Rental Guides)**:
   - When covering micro-business equipment packages or service enterprises (e.g. rental RC excavator, mesin es kristal, booth usaha, jasa fotocopy):
     - **Unit Cost & Margin Modeling (HPP per Unit)**: For service/production micro-enterprises (fotocopy, percetakan, laundry, cuci motor), provide an explicit unit cost table breaking down raw materials, consumables (toner/tinta/kertas), electricity, and maintenance/depreciation against unit selling price (e.g. HPP Rp 145/lembar vs harga jual Rp 200 -> margin Rp 55/lembar atau 27,5%).
     - **Three-Tier Operational Scenarios (Sepi / Sedang / Ramai)**: Provide a native comparison table modeling three realistic scenarios based on standard monthly operating days (e.g. 26 hari kerja), calculating daily volume, gross monthly revenue, total operational expenses, net monthly profit, and exact payback period (BEP).
     - **Concrete Payback Period (BEP)**: State explicit BEP expectations (e.g. 4–16 bulan) directly in the BLUF box and lead copy, grounding the investment thesis in achievable numbers matching the title claim.
     - **Mandatory Operational Risk Alert Box**: Always dedicate a red/warning alert box (`<div class="alert border-0 rounded-4 p-4 my-4" style="background: #fef2f2; border-left: 5px solid #ef4444 !important;">`) to 3 non-negotiable operational checkpoints:
       1. Mechanical & electrical durability (motor power, duty cycle, and battery life under continuous child use).
       2. Spare parts availability (motors, batteries, and gears are high-wear items that require accessible replacements).
       3. Location licensing & venue compliance (mall management permits, CFD registration, crowd safety rules).
     - **Ecosystem Cross-Linking**: Guide readers from business revenue generation into internal personal finance discipline (`8-alat-disiplin-keuangan...`, budgeting sticky notes, modal pencatatan) to foster responsible micro-enterprise management.

### Step 3: Automated Publishing & Site Synchronization
Run `publisher_engine.publish_article()` via Python to assemble and sync:
```python
import sys
sys.path.insert(0, '/root/dailyfinance_web')
import publisher_engine

article = publisher_engine.publish_article(
    slug="slug-artikel-terbaru-2026",
    title="Judul Lengkap Sesuai Formula 2026",
    category="Bisnis & Usaha", # or Gaya Hidup, Finansial
    read_time="6 menit baca",
    hero_image="assets/img/blog/hero-image.webp",
    meta_desc="Deskripsi padat 140-160 karakter dengan angka konkret.",
    keywords="keyword1, keyword2, keyword3",
    body_html=body_content,
    faqs=[("Pertanyaan 1?", "Jawaban 1 ringkas padat 50 kata."), ...],
    author_name="Tim Redaksi DailyFinance",
    date_str="09 Oct 2026"
)
```
The engine automatically:
- Inspects actual pixel dimensions from the hero image asset on disk (using PIL) and injects accurate `og:image:width` and `og:image:height` metadata.
- Generates `NewsArticle`, `BreadcrumbList`, and `FAQPage` JSON-LD schemas.
- Injects visible `<div class="accordion accordion-faq-static">` cards directly into the rendered article HTML before the funnel section (auto-rendering Q&A for human readers and Google AI Overview query fan-out extraction without manual HTML markup).
- Injects the mandatory robots meta: `index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1`.
- Injects the article into `index.html` (hero grid) and `blog.html` (paginated list).
- Updates `sitemap.xml` with current date and priority 0.8.
- Registers the new slug into `gsc_indexing.py` `ALL_PAGES` by strictly bounding search between `ALL_PAGES = [` and its matching `]`, followed by an immediate import/membership assertion.

### Step 4: Server Deployment & Live Verification
1. **Deploy HTML & Synchronize Secondary Images**:
   - `publisher_engine.publish_article()` only pushes the declared hero image.
   - Any secondary/body images AND affiliate product card images (e.g. `assets/img/mesin-...webp`) referenced in `body_html` must be explicitly uploaded to cPanel `public_html/assets/img/` using `cpanel_pinjolresmi.upload_file()`. If omitted, body illustrations and mid-content product cards will render as broken 404 images on production.
   - **Upload With Retry & Read-Back**: Call `cpanel_pinjolresmi.upload_file(remote_dir, filename, data, content_type, overwrite=True)` and check `status == 1`. Use `remote_dir="public_html/assets/img"` for images and `"public_html"` for HTML. Wrap each call in 3 attempts with a short sleep, since the cPanel connection intermittently times out mid-handshake while the local file is already changed. Confirm each remote file with `curl` afterward; a local success print does not prove the remote copy.
2. **Inspect Live HTTP Status**:
   - Verify the article and every image (hero + body) returns HTTP 200:
     ```bash
     for img in hero.webp body-1.webp; do
       curl -sL -o /dev/null -w "%{http_code}\n" "https://dailyfinance.id/assets/img/$img"
     done
     ```
3. **Inspect Robots Meta**:
   ```bash
   curl -sL -A "Mozilla/5.0 (compatible; Googlebot/2.1)" "https://dailyfinance.id/<slug>.html" | grep -o 'max-image-preview:large'
   ```
4. **Headless Visual & Mobile Viewport Audit**:
   - Audit at desktop (1280px) and mobile (390px). Verify zero horizontal overflow (`scrollWidth <= clientWidth`).
   - When inspecting `loading="lazy"` images via Playwright, execute a complete vertical scroll sequence across the full document height (`for y in range(0, totalHeight + 800, 700): window.scrollTo(0, y); await page.wait_for_timeout(150)`) before verifying `naturalWidth > 0`; lazy images outside the initial viewport report zero width and incomplete status until scrolled into view.
   - **Targeted Component Screenshots for Visual AI Audits**: When capturing specific elements (affiliate cards, comparison tables, FAQ) for visual verification via 9router or vision tools, dynamically query the element's absolute position (`el.getBoundingClientRect().top + window.scrollY`), scroll directly to `pos - offset` with a settling pause (`wait_for_timeout(700)`), and verify `window.scrollY` before capturing to ensure the targeted component is centered in the screenshot.
   - Verify visible FAQ presence deterministically via DOM inspection: `document.querySelectorAll('.accordion-faq-static .card').length` must equal the number of FAQs passed.
   - Ensure category badge containers wrap (`flex-wrap: wrap`) and compliance disclaimers retain horizontal padding (`px-3`) so text does not bleed to the screen border.
   - Downscale screenshots to compact JPEG (width ≤450px for desktop, ≤320px for mobile, quality 80) via PIL before submitting to `vision_analyze` to prevent tool timeouts on high-resolution full-viewport renders.
   - **DOM Layout Fallback**: When external vision APIs hit rate limits (Cloudflare HTTP 429/503), use Playwright DOM bounding box inspection (`getBoundingClientRect()`, button widths/heights, `offsetParent !== null`) for deterministic, zero-token layout verification.
5. **End-to-End Asset Replacement Routine (When Revising Live Articles)**:
   - When requested to replace or update an image in an already published article, complete the entire pipeline in one continuous pass—never halt after merely discovering or downloading candidate files:
     1. Download and convert the replacement image to WebP (`assets/img/`), recording its exact pixel dimensions (width × height).
     2. Update all occurrences in the article HTML:
        - `<meta property="og:image">` and Twitter card image.
        - `<meta property="og:image:width">` and `<meta property="og:image:height">` (update to match the replacement asset's actual dimensions, e.g. 750×500 instead of stale dimensions).
        - JSON-LD schema `"image"` URL.
        - The `<img>` tag `src` AND rewrite its `alt` text to accurately describe the new visual subject.
        - `<span class="image-caption">` or `<figcaption>` source credit with explicit attribution (`Foto: Dok. [Sumber]`) and a faithful description of what is actually visible.
     3. Update `index.html` (homepage hero grid/card thumbnails) and `blog.html` (archive grid) where the old image was referenced: rewrite both `src` AND `alt` text so stale descriptions do not linger on listing cards.
     4. Upload the new WebP file + updated article HTML + updated index.html + updated blog.html to cPanel (`public_html`).
     5. Verify live: confirm HTTP 200 on the new asset URL, confirm 0 occurrences of the old image filename AND old alt text strings in live HTML, and verify visual rendering.
     6. **Bypass Browser Cache Before Visual Check**: A browser session that loaded the page before the upload keeps serving old HTML and images, so a DOM check there reports the stale hero even when `curl` shows the new one. Verify with `curl` first, then reload with a unique query string (`?fresh=<n>`) and disable the cache via CDP (`Network.setCacheDisabled`) before reading the hero's `src` and `naturalWidth`. Treat a curl/browser mismatch as a cache artifact until proven otherwise.

### Step 5: Google Indexing API Push & Live Indexing Status Triage
1. **Push Priority Crawl Notification**:
   Submit all touched URLs (article, index, blog) immediately:
   ```python
   import sys
   sys.path.insert(0, '/root')
   import gsc_indexing

   urls = [
       "https://dailyfinance.id/",
       "https://dailyfinance.id/<slug>.html",
       "https://dailyfinance.id/blog.html"
   ]
   gsc_indexing.push_urls(urls)
   ```
2. **Verify Submission vs. Live Indexing Status (Answering "Apakah Sudah Terindeks?")**:
   - Differentiate **Stage 2 (Disubmit/Queued)** from **Stage 3 (Terindeks/Live in Google Index)**.
   - Pushing via `gsc_indexing.push_urls()` only queues the URL into Googlebot's priority pipeline (Stage 2). It does NOT mean the page is instantly in Google's search index.
   - **CRITICAL — Bounded Targeting & Read-Back Verification for Indexing Registries**: When registering URLs into `gsc_indexing.py`, locate the exact variable marker `ALL_PAGES = [` and find its closing bracket; never use global string replacement (`replace(']', ...)`), which hits top-of-file usage examples or docstrings. Immediately follow every registration with an import assertion (`python3 -c "import gsc_indexing; assert slug in ' '.join(gsc_indexing.ALL_PAGES)"`).
   - **Slug & URL Existence Pre-Validation**: Always confirm the URL returns HTTP 200 on production and matches a valid local file before querying URL Inspection API. Typo slugs return `verdict: "NEUTRAL"`, `coverageState: "URL is unknown to Google"`, which falsely mimics normal crawl-queue behavior for a file that does not actually exist.
   - To inspect actual live indexing status (Stage 3), query the URL Inspection API with `siteUrl: "sc-domain:dailyfinance.id"` (domain property format, not URL prefix):
     ```python
     # POST https://searchconsole.googleapis.com/v1/urlInspection/index:inspect
     payload = {"inspectionUrl": target_url, "siteUrl": "sc-domain:dailyfinance.id"}
     ```
   - **Triage Result Interpretation**:
     - Newly published articles (<24–48 hours) will report `verdict: "NEUTRAL"`, `coverageState: "URL is unknown to Google"`, `lastCrawlTime: null`. This is normal crawl queuing.
     - Established indexed articles report `verdict: "PASS"`, `coverageState: "Submitted and indexed"`, with a valid timestamp in `lastCrawlTime`.
   - When reporting status to stakeholders, present a comparison showing newly submitted URLs alongside an established indexed article on the domain to prove the indexing pipeline is healthy and active.
   - **Sitemap Freshness Check**: Inspect `sitemap.xml` status via GSC API (`GET /webmasters/v3/sites/sc-domain%3Adailyfinance.id/sitemaps`). If `lastDownloaded` is earlier than newly published article timestamps, trigger an immediate re-fetch by submitting via `PUT /webmasters/v3/sites/sc-domain%3Adailyfinance.id/sitemaps/https%3A%2F%2Fdailyfinance.id%2Fsitemap.xml` (returns HTTP 204, sets `isPending: true`).

3. **Batch Sitemap Refresh**: after publishing any batch, resubmit the sitemap unconditionally: `PUT https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Adailyfinance.id/sitemaps/https%3A%2F%2Fdailyfinance.id%2Fsitemap.xml` (HTTP 204), then read back `GET .../sitemaps` and confirm `lastSubmitted` is the current time. Do not wait for `lastDownloaded` to lag first.
4. **Property Preflight**: the shared helper `/root/gsc_client.py` hardcodes `SITE_URL` to a different domain property. For dailyfinance.id, confirm the identifier from `GET /webmasters/v3/sites` and pass `siteUrl: "sc-domain:dailyfinance.id"` explicitly on every inspection call. A 403 from the default property looks like a permission failure but is a property mismatch.

### Step 6: Social Media Syndication & Interactive Utility Promotion (Threads & X)
When crafting social posts or promotional threads for Dailyfinance interactive tools (such as `kalkulator-bunga-pinjol-ojk.html` or the Transjakarta route finder):
1. **Extract Verified Numbers from the Production Engine**:
   - Never eyeball or invent financial calculations. Either extract the formula directly from `assets/js/main.js` (`calculateLoan()`) or run a headless Playwright evaluation on the live page to compute exact figures:
     - Principal loan amount.
     - Upfront admin fee deduction (e.g. 5% = -Rp 150.000).
     - Net disbursement received in account (e.g. Rp 2.850.000).
     - Daily interest rate within OJK guidelines (e.g. 0.3%/day × 30 days = Rp 270.000).
     - Total repayment due (e.g. Rp 3.270.000) and net gap (e.g. Rp 420.000).
2. **Structure the Contrast Shock Hook**:
   - Open with the stark mathematical discrepancy between gross loan requested, net cash received, and total repayment due.
   - Contrast official OJK regulatory caps (0.3%/day for consumer loans, 0.1%/day for productive loans, max total fee cap 100%) against illegal loan offerings (e.g. 0.8%/day) to spark conversation and utility awareness.
3. **Generate 1080×1350 (4:5) Graphic Simulation Cards**:
   - Produce vertical portrait cards (1080×1350 px) optimized for mobile feeds.
   - Maintain a minimum 72px safe padding around all four edges.
   - **Vertical Layout Budget**: When stacking dynamic rows, callout boxes, and warning badges via PIL, calculate cumulative heights (`sum(row_heights) + margins <= H - bottom_pad`). Ensure the lowest row or warning strip does not clip against the bottom canvas boundary.
   - Run visual inspection (`vision_analyze`) on every generated graphic card to audit layout, legibility, and clipping before delivery.
4. **Mandatory Educational Non-Lender Disclaimer**:
   - Always state clearly that Dailyfinance.id is an independent financial education and simulation platform, not an OJK-registered peer-to-peer lender or financial institution, preventing regulatory and platform policy violations.
5. **Single-Flow Interactive Assessment Architecture ("Claim Dana Kaget" Funnels)**:
   - When building landing pages for viral social hooks (e.g. "Claim Dana Kaget"), collapse complex benefit matrices into a singular, high-intent interactive diagnostic (3 quick status clicks: employment status, BPJS participation, income bracket) instead of an overwhelming static multi-program list.
   - **Clean Question Hierarchy Without Number Badges**: Present diagnostic questions directly (e.g. "Apa status kerjamu sekarang?") without prepending emoji digits (`1️⃣`, `2️⃣`, `3️⃣`) or numbered badge icons. Card borders, spacing, and progression indicators already establish separation; numbered emoji badges introduce visual noise, reduce heading legibility on mobile viewports, and cheapen the editorial aesthetic into looking like an informal chat forward.
   - Zero PII footprint: Run 100% client-side in vanilla JS without storing data or requiring phone numbers/NIK on our site, preserving user trust and eliminating privacy liability.
   - Dynamic matched outcomes: Sum the potential statutory benefit values into an immediate headline estimate ("sampai Rp 8.800.000") and render only the specific matched programs with outbound links to verified `.go.id` portals.
   - Downstream retention: End the result section with an educational bridge leading into internal site tools (`kalkulator-bunga-pinjol-ojk.html` or budgeting guides) so viral visitors stay on-site.
6. **Ultra-Minimalist Viral Landing Page Architecture (Zero Friction)**:
   - When refining viral landing pages driven by social links (e.g. `jajan-gratis.html`), aggressively remove secondary explanatory sections such as "Cara Kerjanya" step cards and broad static comparison tables ("Daftar Lengkap Sumber"). Social traffic has a sub-5-second attention span; instructional steps and static tables create cognitive drag that dilutes the primary diagnostic action.
   - Maintain strictly a single high-conversion path: Hero → Brief Intro → 60-Second Interactive Diagnostic → Matched Benefit Cards → 🛡️ Anti-Fraud Rules → Internal Utility Retention Bridge (`kalkulator-bunga-pinjol-ojk.html`) → FAQ.
7. **Social Media Bounty & Giveaway Auditing Protocol (Filtering Serial Mendicants)**:
   - When selecting recipients for interactive engagement bounties (e.g. dinner fund giveaways on Threads):
     - Scrape respondent handles via headless browser (`playwright`).
     - Inspect candidate profile timelines (`threads.com/@username`) to filter out disingenuous participants.
     - **Negative Signals (Immediate Disqualification / "Ngemis Online")**:
       - Public e-wallet drops: Accounts posting GoPay/DANA numbers with solicitation copy ("biar GoPay-ku bunyi terus").
       - Serial donor tagging: Timelines filled with repetitive gratitude posts thanking random online benefactors.
       - Giveaway jargon & hunting: Accounts using beggar/giveaway slang like "jumber" (Jumat Berkah hunting) or pinning giveaway entries from unrelated accounts.
       - Spam / affiliate risk: Feeds dominated by AI content farms or suspicious affiliate hooks ("geser kak geser").
     - **Positive Selection Signals (High Authentic Synergy)**:
       - Authentic personal context: Everyday life moments, genuine family necessities (e.g. buying eggs/groceries for children), zero history of begging.
       - Working micro-entrepreneurs (UMKM): Profiles striving to sell products (culinary, snacks, crafts) with pride ("larisin jualanku biar bisa jajan") rather than requesting handouts.
       - Organic amplification value: Favor genuine accounts with modest engaged followings (500–2,000 followers) whose authentic public gratitude or quote-thread provides exponential social proof and credibility for Dailyfinance.id.

### Step 7: Interactive Directory & Search Utility Architecture (Zero User Friction)
When maintaining or building interactive client-side search tools (such as `cek-legalitas-pinjol-ojk.html` searching `fintech-db.js`):
1. **Dual Search Execution Pattern (Live Filter + Explicit Action Button)**:
   - While reactive instant-filtering on `input` provides immediate feedback, ordinary mobile users conditioned by traditional forms expect an explicit visual action button ("Cari") or keyboard Enter trigger to confirm execution.
   - Always nest an explicit primary button (`<button id="...-search-btn" class="btn btn-primary fw-bold px-4">Cari</button>`) and a clear button (`✕`, toggled visible when query length > 0) inside the input group.
   - Bind four synchronized event listeners:
     - `searchInput.addEventListener("input", ...)` for instant dynamic filtering and toggling the clear button.
     - `searchBtn.addEventListener("click", ...)` to explicitly trigger search, update result count, and retain input focus.
     - `searchInput.addEventListener("keydown", ...)` capturing `Enter` (`e.preventDefault(); renderSearchResults(...)`).
     - `clearBtn.addEventListener("click", ...)` resetting input value, restoring default directory state, and hiding the clear button.
2. **Reassuring Helper Copy**:
   - Place explicit guidance text immediately below the search group: `<p class="small text-muted mb-0 mt-2">💡 Hasil juga muncul otomatis saat kamu mengetik &mdash; atau tekan tombol <strong>Cari</strong>.</p>`. This bridges modern reactive instant-filtering with traditional search mental models.
3. **Deterministic Cache-Busting Versioning on Utility Scripts**:
   - Whenever updating client-side directory logic in `assets/js/main.js` or `fintech-db.js`, always bump cache-busting query strings across all host HTML files: `<script src="assets/js/main.js?v=YYYYMMDD_XX">`. Mobile browsers aggressively cache static `.js` assets, causing users to execute stale scripts where newly added buttons lack event bindings.

## 2. Hard Quality Gates & Evidence Checklist

Before declaring any publishing or SEO task complete, provide the following verifiable evidence:
1. **Robots Meta Verification**: Exact grep proof showing `max-image-preview:large, max-snippet:-1` on the live URL.
2. **Schema Validity**: JSON-LD block parsed via `json.loads()` with zero syntax errors.
3. **HTTP Status**: Live URL and all referenced body images and affiliate product card images return 200 OK.
4. **Distinct Image Assets & Orientation**: Zero duplicate re-use of hero image within inner body sections, and all sourced images pass EXIF orientation transposition check (`ImageOps.exif_transpose`). Run the duplicate check BEFORE publishing: center-crop each final WebP to the same aspect ratio, downscale to 16x16 grayscale, and compare the pixel bytes against the hero file; identical bytes means the figure re-uses the hero and must be replaced. Verify each `<img src>` maps to the candidate you intended by the same hash comparison, not by filename.
5. **GSC Indexing & Sitemap Inclusion Proof**: Output showing `0 failed` from `gsc_indexing.push_urls()`, confirmation of the URL in live `sitemap.xml`, confirmation that target URL exists locally and returns HTTP 200 before querying URL Inspection API, and verified registration of the full URL in `gsc_indexing.py` `ALL_PAGES` via runtime import assertion (`python3 -c "import gsc_indexing; assert '<slug>' in ' '.join(gsc_indexing.ALL_PAGES)"`), never raw grep which falsely matches comments or docstrings.
6. **Editorial Integrity**: Attribution credits present on all images with explicit source tags (`Foto: Dok. ...`), affiliate disclosure box present above product cards with `rel="sponsored nofollow"` on all external shopping links.
7. **Mobile Responsiveness & CTA Ergonomics**: Clean 390px viewport render with zero horizontal overflow; primary affiliate CTA buttons span full width (≥300px, height ≥40px).
8. **Promised Artifact Integrity ("Title Contract" & Numbered Count)**:
   - If the title promises a specific count ('7 Pinjol', '7 Trik Cicilan', '5 Cara', '10 Rekomendasi'), verify via grep or DOM count that all N distinct items exist as fully realized cards or sections. Never close work with truncated entries.
   - If the title contains '+ Template', '+ Format', '+ Kalkulator', or '+ Checklist', verify that the rendered DOM contains actual complete copyable templates or interactive components with working copy buttons (`copyTemplate`), not just abstract summary bullets.
9. **Mobile Share Bar Visibility**: Verify Threads share button occupies the first position in `.share-buttons-list` so it renders immediately visible without wrapping cutoff on 390px screens.
10. **Interactive Directory & Search Ergonomics**: When deploying or maintaining directory search inputs (`#ojk-search-query`), verify via browser interaction tests that (1) an explicit 'Cari' button is visible and triggers search on click, (2) the clear (✕) button resets results on click, (3) pressing Enter submits the query, and (4) script tags carry fresh cache-busting version strings (`?v=...`).
11. **Visible FAQ Card Rendering**: Confirm DOM presence of rendered FAQ cards (`document.querySelectorAll('.accordion-faq-static .card').length > 0`) verifying that `publisher_engine.py` successfully rendered visible accordions alongside FAQPage JSON-LD.
12. **Onboarding & Tutorial Step Sequence Integrity**: For in-app registration or procedural guides, verify that (1) prerequisite account tiers (e.g. Akun Premium) appear prominently in an alert box before the steps, and (2) the numbered step sequence matches official app navigation flow in chronological order without inverted steps.
13. **Asset Replacement Synchronization Gate**: When replacing an existing image asset, confirm (1) `alt` text describes the new visual across article, `index.html`, and `blog.html` (zero instances of previous alt text remaining), (2) `og:image:width` and `og:image:height` match the exact dimensions of the replacement asset, and (3) image caption includes explicit photo source attribution.
14. **Favicon Integrity & SERP Globe Fallback Prevention Gate**: Confirm (1) root `/favicon.ico` contains multi-resolution layers up to 256×256 (`(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)`), (2) all `<link rel="icon">` and `<link rel="apple-touch-icon">` tags across all pages use clean, unversioned URLs (zero `?v=...` query strings), (3) all icon assets return HTTP 200 on live production, and (4) homepage `<lastmod>` in `sitemap.xml` is updated and pushed via Indexing API / GSC request after any icon change.
15. **Batch Image Visual Gate**: build one contact sheet of all hero and body candidates and review it with vision before upload. Reject masked or obscured faces, dim frames, branded product shots in lifestyle body slots, and subjects that do not match the paragraph they illustrate. Openverse: query without the `extension` filter; with it, most queries returned zero results.

## 3. Pitfalls & Anti-Patterns (Rule + WHY)

- **Never transcribe affiliate short-link codes from a screenshot by vision alone** — glyph confusions (`q`/`g`, `8`/`6`) produce codes that look valid and fail only at probe time; probe every code as text before embedding it.
- **Verify product-to-topic alignment on every affiliate card** — a link that resolves to the wrong product type breaks the article's title promise and reader trust even though the link works.
- **Scan long AI-drafted articles for garbled phrases and repeated figures before the builder runs** — long drafts accumulate mid-sentence corruption and the same statistic in two sections; catching these after upload costs a re-patch and a re-publish. Specifically grep for: stray redaction/label tokens leaked into body copy (e.g. `JT Revista`), mojibake-free unit notation (`m2` vs `m²` — always render square metres as `m²`), and any figure repeated in two sections.
- **Normalize units and typographic characters in a dedicated pass before publishing** — `m2`/`m3` must be `m²`/`m³`, `Rp6 miliar` spacing kept consistent, and en-dashes used in numeric ranges (`2,8–6 tahun`). Readers and AI Overviews treat `m2` as a typo and it weakens perceived editorial quality on a finance domain.
- **Sitewide element removal must key on a unique signature, not a visible label.** Locate the element by its exact href / query string (e.g. the full `wa.me/...?text=` or `tel:` target), grep every page AND the builder/template before editing, and leave lookalike text inside article bodies untouched, since the same number or word can be editorial content. After removing a widget, confirm no empty wrapper remains and sibling items still render. Keep emergency-help boxes unless the user explicitly asks to remove them.
- **Bulk `?v=` cache-busting bumps must be verified by count.** Replace the full token (`name.css?v=OLD`) across every HTML page, including pages that reference a `.min.css` variant. Afterwards, live-grep for the old token (must be 0) and the new token (must match the page count). A filter keyed on a substring silently leaves one variant on the old version and users keep seeing stale CSS.
- **Keep the final status message compact** — publish sessions accumulate large context, and a long final table can hit the output-token limit and get cut off mid-answer. Lead with live URLs and open items only.

- **Always normalize EXIF orientation via `ImageOps.exif_transpose()` before converting or cropping image candidates** — raw uploads from Wikimedia Commons or mobile phone cameras frequently embed EXIF orientation tags (e.g. orientation 6 or 8); converting to WebP without transposing ignores the orientation tag in many browsers, causing images to display 90° sideways or upside down on the live website.
- **Explicitly upload affiliate product card images alongside body images to cPanel** — `publisher_engine.publish_article()` only synchronizes the hero image; omitting explicit upload of the product card photo leaves a broken 404 image inside the high-conversion affiliate card.
- **Perform a complete progressive scroll with settling pauses before asserting `naturalWidth > 0` on lazy-loaded images** — images using `loading="lazy"` below the initial viewport report `naturalWidth == 0` and `complete == false` during headless checks; asserting image health without a full progressive scroll triggers false positive failure alerts.
- **Calculate absolute document coordinates before capturing targeted component screenshots for visual audit** — guessing viewport scroll positions or taking screenshots immediately after a rapid scroll sequence often captures blank white space or adjacent unrelated sections, causing visual QA models (9router/Gemini) to falsely report missing elements; always compute `getBoundingClientRect().top + window.scrollY` and pause for scroll settlement before snapping.
- **Never rely on unbounded token replacement (`replace(']', ...)`) or optimistic print logs when mutating registry files (`gsc_indexing.py`)** — matching unanchored syntax tokens hits the first match in the file (often docstrings or usage examples), silently stranding entries in comments while the runtime list remains untouched; furthermore, successful real-time API pushes (`push_urls`) mask registry corruption because the real-time and batch maintenance paths are decoupled. Always bound the insertion between `ALL_PAGES = [` and its closing `]`, and verify via runtime import assertion (`python3 -c "import gsc_indexing; assert slug in ' '.join(gsc_indexing.ALL_PAGES)"`) rather than trusting script console printouts.
- **Always programmatically auto-detect `og:image` dimensions from the actual asset file via PIL** — hardcoding static dimensions (e.g. 1200×675) or omitting dynamic inspection when using images of different aspect ratios (e.g. 1200×800) writes inaccurate Open Graph metadata, causing social platforms and search engines to miscalculate image ratios or crop previews awkwardly; pass the local image path to `Image.open().size` in `publisher_engine.py`.
- **Always verify all promised count items and calculations in financial articles ("Title Contract")** — when a title promises "7 Trik Cicilan Kendaraan 2026: Hemat Bunga...", deliver all 7 tricks in full and cross-verify regulatory figures (e.g. POJK 35/2018 DP tiers, 30% debt-service ratio, flat vs effective interest discrepancy) so claims withstand reader and regulatory scrutiny.
- **Never append query parameters (`?v=...`) to favicon `<link>` tags** — Google's favicon crawler (`Googlebot-Image`) strictly requires a stable, permanent URL; appending version query strings disrupts Google's favicon indexing pipeline and cache invalidation, causing Google SERP to fall back to the generic gray globe icon.
- **Always compile root `favicon.ico` with multi-resolution layers (16/32/48/64/128/256 px)** — Google Search guidelines explicitly require site favicons to be multiples of 48px square (48×48, 96×96, etc.) or SVG; a legacy 16×16/32×32 ICO is sub-optimal for modern high-DPI desktop and mobile Google SERP, prompting fallback to the default globe icon.
- **Always update homepage `lastmod` and trigger recrawl when changing favicons** — Google extracts the site favicon strictly from the root homepage (`/`); modifying favicon files on disk or server without triggering a recrawl of the homepage leaves Google unaware of the updated assets, prolonging the fallback globe display for weeks.
- **Always verify the target URL exists (HTTP 200 on live server / matched in sitemap.xml) before interpreting `URL is unknown to Google` in URL Inspection** — an invalid or typo URL also returns `verdict: NEUTRAL` and `coverageState: "URL is unknown to Google"`, which looks deceptively identical to a newly published valid article in the crawl queue; inspecting a typoed URL gives false confidence that non-existent content is merely waiting in queue when in reality the real article was never inspected.
- **Check `lastDownloaded` on GSC sitemap status when articles remain unknown to Google** — if the sitemap's `lastDownloaded` timestamp in GSC precedes the publication timestamp of recent articles, Googlebot has not yet fetched the updated URL set; resubmit the sitemap via API (`PUT /sitemaps/...`) to reset `isPending: true` and prompt a fresh download rather than passively waiting.
- **Always synchronize `alt` text and image dimensions across all surfaces when replacing an image asset** — updating only the image `src` or filename leaves stale `alt` text (e.g. describing an old sandbox photo instead of the new RC excavator arena) in the article body, `index.html`, and `blog.html`, which confuses screen readers, degrades Google Image search ranking, and misrepresents the visual content; always rewrite the `alt` description and sync `og:image:width`/`height` metadata to the new asset's exact dimensions.
- **Never omit photo source attribution (`Foto: ...`) when adopting user-provided or third-party images** — publishing external photography without explicit credit undermines editorial credibility and violates standard publication ethics; always add a descriptive caption with clear attribution (e.g. `<span class="image-caption">... Foto: Dok. [Kreator/Penjual/Sumber]</span>`) directly under the image.
- **Never publish wide uncropped landscape photos where the focal subject is lost in the background** — wide shots of parks, streets, or playgrounds get visually interpreted as generic scenery rather than specific business equipment or activities; crop tightly to the active subject zone before converting to WebP so the thumbnail and hero immediately convey the article's core topic.
- **Never attribute specific technical features or equipment in image captions that are not clearly visible in the image** — claiming a photo shows a specific mechanical toy, digger, or machine when the resolution only confirms an area of sand or general play structure damages editorial credibility upon close inspection; accurately describe the broader visible scene (e.g. "Area bermain pasir anak di taman rekreasi — konsep yang menginspirasi wahana...") to maintain strict factual transparency.
- **Always pair 'paket usaha' revenue projections with operational equipment risk warnings** — highlighting only gross weekend revenue creates unrealistic expectations; commercial rental gear operated by children experiences heavy mechanical wear and tear, battery exhaustion, and location licensing hurdles that must be explicitly analyzed to preserve authoritative EEAT financial guidance.
- **Never conflate Indexing API submission success with actual Google SERP indexing** — `push_urls()` returning `0 failed` only confirms Google's crawler queue received the ping (Stage 2); claiming to stakeholders that the page is "already indexed in Google" based solely on submission output is inaccurate. Always check the URL Inspection API with `siteUrl: "sc-domain:dailyfinance.id"`: newly published pages will show `verdict: NEUTRAL` / `coverageState: "URL is unknown to Google"` awaiting crawler visit, while established pages show `verdict: PASS` / `coverageState: "Submitted and indexed"`. Provide an established indexed URL as comparison proof to show the pipeline is healthy.
- **Never omit prerequisite verification tiers in app-based onboarding guides** — many fintech applications restrict merchant or business features (such as DANA Bisnis QRIS) strictly to verified/premium accounts (KYC Level 2); omitting this requirement leaves readers stranded when they cannot find the business menu or toggle in their app, resulting in frustration and high bounce rates.
- **Strictly mirror the official in-app navigation hierarchy in procedural guides** — ordering steps out of sequence (such as checking profile status before instructing the user to open the app or enter the menu) causes cognitive friction and contradicts the visual sequence shown in official in-app help documentation.
- **Always interlink newly published guides with sister articles in the same thematic cluster** — relying exclusively on generic utility links misses the opportunity to form tight topic clusters (e.g. linking a gig-economy side job guide directly to a recent ojol regulation piece); topic clusters establish contextual depth that search engines rely on to evaluate domain authority in specific niches.
- **Never rely solely on reactive 'input' event filtering without an explicit 'Cari' button and Enter key handler** — ordinary mobile users expect a tangible action button or Enter key to execute search; omitting a visible 'Cari' button leads users to believe the search function is incomplete or impossible to submit after typing.
- **Always append deterministic cache-busting query strings when modifying utility scripts in static HTML** — mobile browsers cache `.js` files aggressively across sessions; modifying interactive logic in `assets/js/main.js` without updating `<script src="assets/js/main.js?v=...">` in host HTML leaves returning mobile visitors running stale scripts where new search buttons or UI controls lack functional event listeners.
- **Never mix productive/business lending platforms into consumer "pinjol" review roundups** — readers searching for personal/emergency pinjol seek fast personal cash; including SME/business financing platforms (which require business permits, tax IDs, and days of invoice underwriting) is completely irrelevant to the reader's intent and prompts immediate user rejection.
- **Never conflate distinct corporate brands or bank products with unrelated fintech entities** — bandwidth and entity precision matters: associating a digital bank product (e.g. Tunaiku from Bank Amar) with a different P2P entity (e.g. Amartha) destroys editorial credibility and invites questions about data authenticity.
- **Always synchronize title, meta, H1, breadcrumb, intro text, and table headers when adjusting numbered list counts** — modifying the number of items without updating the `<title>`, breadcrumbs, intro text, or comparison table heading creates conflicting claims across SERP and page elements.
- **Never publish or leave a numbered list article with a truncated item count** — if the headline promises "Review 7 Pinjol Legal", rendering only 1 entry (e.g. Kredivo) and truncating the remaining 6 directly violates the headline promise, destroys user trust, creates a jarring half-finished reading experience, and leads users to report that the page is broken.
- **Always synchronize fintech reviews with the site's internal registry (`fintech-db.js`)** — pulling fintech facts from generic online search risks citing revoked licenses, outdated daily rate caps (pre-SEOJK 19/2023), or inconsistent company names; relying on `fintech-db.js` ensures all 95 licensed entities match the data displayed in the site's interactive directory and verification tools.
- **Never ship an article promising "+ Template" without exhaustive, copy-pasteable script blocks and 1-click copy buttons** — readers facing acute stress (debt collection, dispute, complaints) search specifically for verbatim words to send; delivering only high-level conceptual bullet points violates the title contract, drives immediate bounce, and prompts user complaints about missing templates.
- **Always position the primary social share button (Threads) first in the share list** — on mobile screens under 400px width, flex/list containers wrap across multiple rows; secondary or tertiary button placements get pushed to the second row or cut off, leading readers to believe the button does not exist.
- **Always include `max-image-preview:large` in meta robots** — omitting it restricts Google Search and Discover to low-resolution thumbnail previews and disqualifies the page from high-visibility card carousels.
- **Never omit `max-snippet:-1` on informational articles** — bounded snippet lengths truncate text extracted by Google's generative models, preventing the article from answering queries in AI Overviews and featured snippets.
- **Never duplicate the hero/featured image inside inner article sections** — re-displaying the same hero graphic inside the body creates redundant visuals and wastes an opportunity to showcase secondary process steps or equipment details.
- **Always visually inspect external or Wikimedia image candidates for specialized subjects** — public repository filenames frequently misidentify biological specimens or technical gear (such as tilapia fry mislabeled as gourami fry), which destroys editorial credibility if published.
- **Always explicitly upload secondary/body images referenced in `body_html` to cPanel** — `publisher_engine` only transfers the designated hero image, leaving embedded article images as broken 404 assets on the live server.
- **Always attach explicit source attribution captions to every editorial and company image** — uncredited photography diminishes Google EEAT trustworthiness scores and risks removal from Google News and Discover feeds.
- **Ensure mobile affiliate buttons span full-width (`w-100` / ≥300px width)** — small inline links or undersized buttons on touchscreens suffer high mis-tap rates and drastically lower CTR compared to prominent, thumb-friendly CTA buttons.
- **Use programmatic DOM layout inspections when vision models are throttled** — DOM property tests (`getBoundingClientRect()`, `scrollWidth`, `naturalWidth`) provide instant, token-free layout validation during external vision API rate-limit periods.
- **Scroll the page during headless visual audits of `loading="lazy"` images** — off-screen lazy images do not trigger network downloads until scrolled into view, falsely presenting as failed or broken assets in initial DOM checks.
- **Wrap category badge containers with `flex-wrap: wrap`** — long composite badges (e.g., category plus quarterly reporting tags) overflow or touch the right boundary on 390px mobile viewports.
- **Always keep FAQ answers pre-rendered in the visible DOM** — accordions that defer text rendering or hide content via JavaScript prevent Googlebot from extracting answers for query fan-out passages.
- **Always add `rel="sponsored nofollow"` and a visible editorial disclosure on affiliate links** — unflagged commercial links trigger Google Search unhelpful content penalties and violate Google Ads / AdSense publisher guidelines.
- **Never future-date articles or update `dateModified` without substantive content revisions** — artificial date bumping triggers freshness-manipulation algorithms, causing Google to overwrite byline dates with historical crawl timestamps.
- **Maintain exactly one `<h1>` that mirrors the `<title>`** — competing top-level headings confuse topical entity extraction and trigger Google to rewrite title links using random internal anchor text.
- **Ensure hero images are at least 1,200px wide and 16:9 aspect ratio** — Google Discover strictly filters out articles with images under 1,200px width or sub-300,000 total pixels.
- **Always downscale full-page screenshots to ≤450px width JPEG before passing to `vision_analyze`** — full-resolution headless PNGs frequently trigger API timeouts and payload truncation.
- **Always cross-reference social media infografis with primary regulatory filings or corporate press releases** — social graphics frequently simplify or omit critical operational indicators (CoF, CASA, NPF) needed for authoritative EEAT reporting.
- **Randomize view counters per article — never ship identical numbers** — a site where every article shows the same view count (e.g. "1,500 Dilihat") reads as fabricated social proof and undermines trust. `publisher_engine.py` generates a unique random count per publish (`view_count = f"{random.randint(780, 6850):,}"`) and injects it into both the article page and the homepage hero card. When back-filling existing articles in bulk, assign unique values from a seeded RNG, avoid round hundreds, and keep article-page and index-card values consistent for the same slug.
- **Extract Threads post content via browser render, not curl** — `curl` on a threads.com post returns only the `<title>` fragment (first ~250 chars of the post) plus obfuscated React payloads; the full threaded replies (which often contain the substantive tips) only appear after JS render. Use the browser tool with `document.body.innerText` to capture the complete post + author replies. Instagram post captions are readable from the browser's rendered text. Carousel slides sit behind a login popup and are absent from the embed HTML, so cap slide enumeration at a few attempts; when it fails, take the caption as the material seed and source body images from official or licensed uploads (see Image Sourcing) instead of spending more calls on slides.
- **Resolve Shopee product/affiliate links with the WhatsApp crawler UA** — Shopee blocks datacenter IPs with traffic-verification walls for normal browsers and Googlebot, but `curl -A "WhatsApp/2.23.20.0"` on a `s.shopee.co.id/xxx` affiliate shortlink returns the OG meta block (title, description, product image URL) revealing the exact product behind the link (e.g. Uwinfly M135H). Use this to identify affiliate products and pull their canonical Shopee CDN image for editorial use; normal browser sessions redirect to `shopee.co.id/verify/traffic/error` and API endpoints return error 90309999.
- **Always validate heading tag symmetry before publishing** — closing subheadings like `<h4>` with mismatched tags like `</h2>` breaks DOM hierarchy and damages semantic extraction.
- **Avoid culturally or contextually disconnected stock photos for local finance topics** — using ambiguous foreign imagery (e.g. crowds handling unidentified non-rupiah banknotes) feels alien to Indonesian readers and signals low editorial effort. Use authentic, culturally grounded assets (like verified Indonesian rupiah currency, local equipment) or clean, universally recognizable lifestyle flat-lays.
- **Always format image attribution captions with platform, creator, and license** — citing just "Foto: Internet" or leaving off the creator name and license violates Creative Commons terms and damages Google News/Discover EEAT trustworthiness. Always format as `<figcaption class="text-center text-muted fst-italic small mt-2">Deskripsi visual. Foto: [Platform] ([Kreator], lisensi [Lisensi])</figcaption>`.
- **Supply a browser User-Agent header when fetching StockSnap CDN assets** — direct headless curl or basic Python requests to `img.stocksnap.io` receives HTTP 403 Cloudflare blocks without a standard desktop browser User-Agent.
- **Use Openverse API or Flickr CC search when articles require relatable lifestyle visuals** — Wikimedia Commons primarily catalogs taxonomic, documentary, or historical specimens and often lacks modern, attractive lifestyle flat-lays that entice readers to read personal finance content.
- **Never use promotional commercial banners or e-commerce marketing posters as the article hero image** — posters with brand ambassadors, discount badges, or marketing slogans ("SUPER FAST COOLING", store logos) make the article look like a paid advertisement on homepage grids and Google Discover, triggering banner blindness and killing editorial trust and click-through rates. Keep branded product graphics inside mid-body affiliate cards and use genuine editorial/lifestyle photography for the hero.
- **Attribute the source material explicitly for news-derived articles** — when paraphrasing from Indonesian media (Kompas, detik, CNBC, ANTARA) or social posts, state the source in the lead (`Catatan sumber:` / `Sumber materi:`) and again in the closing disclaimer with outlet name, headline, and timestamp (e.g. "Kompas.com, 10 Oktober 2026, 13:21 WIB"). This satisfies editorial transparency and EEAT while making the paraphrase-vs-source distinction clear.
- **Verify critical copy (titles, rupiah amounts, dates) against live HTML, never from vision of downscaled screenshots** — compact JPEG screenshots (≤320px) frequently make vision models misread digits/years (e.g. "BSU 2025" instead of "BSU 2026"). Confirm headlines and key figures by grepping the live page source (`<title>`, `<h1>`, specific strings) before reporting; treat vision as layout evidence only.
- **Never halt an asset replacement task at candidate selection** — finding an image candidate is only reconnaissance; an image replacement task is not executed until the file is converted to WebP, all references (og:image, JSON-LD, body `<img>`, index.html, blog.html) are rewritten, uploaded to cPanel, and verified live with zero remaining references to the old asset.
- **Always extract calculation figures directly from the live code engine when creating promotional posts** — estimating or hand-calculating loan numbers risks discrepancy with what users see when they open the live tool, damaging credibility.
- **Calculate cumulative vertical bounds when rendering infographic cards via PIL** — incrementing hardcoded `y` offsets across headlines, number cards, rows, and warning strips easily exceeds 1350px canvas height, clipping critical bottom rows; compute cumulative vertical heights before drawing and inspect rendered output before delivery.
- **Rely on `publisher_engine.publish_article()` auto-rendering visible FAQs — the engine now auto-generates `<div class="accordion accordion-faq-static">` directly from `faqs`** — Google AI Overview query fan-out extraction requires Q&A text pre-rendered in the visible DOM. While previous iterations required manual HTML injection of visible FAQ cards, `publisher_engine.py` now automatically compiles both the `FAQPage` JSON-LD schema AND the visible accordion cards directly into the page output. Verify live presence via `document.querySelectorAll('.accordion-faq-static .card').length`.
- **Never publish loan calculator copy on social media without an explicit non-lender disclaimer** — financial regulatory policies (OJK) and social platform terms penalize accounts that appear to offer unauthorized direct lending services.
- **Frame Threads traffic funnels as "money that is legally yours but unclaimed", never as free-money giveaways** — wording like "dana kaget" or "jajan gratis" posts that imply free cash read as scams to Threads users, driving mass reports that ban the account and risk Google misinformation flags on the landing page. Reframe identical hooks around real verifiable programs (BSU, JHT, JKP, THR) — same viral tension, zero scam perception, plus EEAT gain.
- **Threads posts cannot carry clickable links — the bio is the only traffic door** — design every Threads-to-site funnel as: hook post (text + image) → "cek bio" → 5 clickable bio links → dedicated landing page with UTM parameters for attribution. Never paste raw URLs in post copy; they are dead weight and lower reach.
- **Build Threads landing pages from the calculator-page template, not article templates** — utility pages (jajan-gratis.html) need: hero graphic (1200×675 PIL/Montserrat), 3-metric BLUF, a golden-rules anti-fraud box (official channels end in .go.id, never pay upfront), one card per program (syarat + cara + official .go.id link rel=nofollow + internal link), CTA into the calculator funnel, 4 FAQs, and an explicit non-government/non-lender disclaimer.
- **When designing viral social landing pages, use a single interactive diagnostic funnel rather than a static multi-item catalog** — presenting visitors arriving from high-urgency social hooks ("Claim Dana Kaget") with a 7-item wall of text triggers cognitive overload and high bounce; a 3-question, 60-second interactive diagnostic with zero PII delivers an instant personalized benefit estimate and keeps bounce rates low while safely routing users to legitimate .go.id channels.
- **Do not prepend interactive form questions with numbered emojis or sequential digit badges** — card borders and vertical layout hierarchy already demarcate questionnaire steps; prepending `1️⃣`, `2️⃣`, `3️⃣` to question headings clutters narrow mobile viewports, degrades clean editorial typography, and makes the diagnostic appear like an informal social chat broadcast rather than a trusted financial tool.
- **Provide verbatim dialogue scripts in blockquotes for debt confession topics rather than generic advice** — readers facing severe financial anxiety specifically seek exact conversational phrases to reduce confrontation with family or spouse; verbatim templates dramatically improve time-on-page, bookmarking, and editorial utility.
- **Avoid sensationalized despair or cash-pile imagery for debt crisis articles** — crying faces or luxury cash stacks look cheap and alienate distressed readers; use a calm, constructive visual narrative (intimate conversation coffee flat-lay → debt calculation checklist → written recovery roadmap) to establish hope and methodical problem solving.
- **Always funnel emotional debt articles to concrete utility calculators and statutory rights** — pure emotional empathy leaves readers stranded; seamlessly guide them through calculation (`kalkulator-bunga-pinjol-ojk.html`), legal entity verification (`cek-legalitas-pinjol-ojk.html`), and debt collection rights under privacy law (`panduan-galbay-pinjol-ojk.html`).
- **Strip informational step cards and large static tables from viral social landing pages** — visitors arriving from high-urgency social hooks (Threads/X) bounce when met with multi-step reading material or static reference catalogs; keep the page focused strictly on the single interactive diagnostic.
- **Audit giveaway respondents' public profiles for serial mendicancy before awarding engagement bounties** — awarding funds to professional beggars or giveaway hunters (characterized by public e-wallet drops, "jumber" jargon, or pinned giveaway feeds) alienates genuine followers and wastes the organic amplification potential of rewarding authentic users or hardworking micro-entrepreneurs.
- **Never allow visible marketplace brand names in any CTA button across the page** — while mid-body product cards may be properly sanitized, closing action cards and auxiliary buttons frequently slip through with labels like "Beli di Shopee →"; visible marketplace names undermine editorial impartiality, trigger ad blindness, and erode user trust. Always audit every single button label to use neutral, curiosity-driven copy (`🛒 Cek Spesifikasi & Harga Terbaru →`) with marketplace links restricted strictly to `href` + `rel="sponsored nofollow"` attributes.
- **When confirming GSC submission to stakeholders, verify all three indexing touchpoints** — merely claiming "already pushed" without inspectable proof invites follow-up questions; always verify (1) `push_urls()` returns `0 failed`, (2) the slug is confirmed in live `sitemap.xml`, and (3) the slug is registered in `gsc_indexing.py` `ALL_PAGES` for recurring bulk indexing runs.
