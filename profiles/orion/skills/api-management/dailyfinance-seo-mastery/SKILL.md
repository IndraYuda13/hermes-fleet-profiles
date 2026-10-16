---
name: dailyfinance-seo-mastery
description: "Use when writing Dailyfinance.id SEO blog articles."
version: 1.33.0
author: ORION
license: proprietary
metadata:
  hermes:
    tags: [seo, dailyfinance, google-search-central, content-publishing, ai-overview, threads, social-media, trending-engine, dark-mode]
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
- Operating and synchronizing the dynamic trending engine (`ranking_engine.py`), the automated business & innovation curation engine (`business_engine.py`), and analytics beacon tracker (`track.php`).
- Managing the 'Peluang Bisnis & Inovasi' auto-curation section on `index.html`.
- Enforcing strictly sequential numbering (1..N) on the popular articles sidebar widget (`.tab-posts-widget`).
- Designing, operating, and auditing community forum features ('Ratapan Pinjol' / anonymous debt crisis venting).
- Authoring authentic user-generated / community confessions (avoiding formal/sterile AI patterns, ensuring human netizen voice, varied personas, drama, natural typos/slang).
- Implementing, operating, or debugging sitewide Dark/Light Mode systems (Zero-FOUC inline scripts, color tokens, and 3-point toggle access).
- Designing, streamlining, or copywriting media kit and advertising pages (`pasang-iklan.html`) with punchy, high-impact offerings.
- Placing prominent utility/community links in desktop navigation bars without disrupting editorial hierarchy.
- Creating high-engagement social media posts (Threads, X) or visual simulation cards promoting Dailyfinance.id utilities (kalkulator bunga pinjol, rute Transjakarta).
- Designing, streamlining, or auditing viral social landing funnels (e.g. "Claim Dana Kaget" / `jajan-gratis.html`).
- Auditing social media giveaway/bounty respondents to filter serial beggars ("ngemis online") and select authentic recipients.
- Handling sensitive emotional personal finance topics (e.g. debt crisis, pinjol confessions, family budgeting conflicts).
- Authoring, auditing, or expanding debt collector response templates, dispute scripts, and copy-pasteable negotiation tools.
- Authoring in-app fintech onboarding, merchant registration (QRIS, DANA Bisnis, e-wallet merchant), and procedural step-by-step guides.
- Sitewide header, banner, or compliance disclaimer removals and bulk synchronization to cPanel.

## 0. Linked Technical Reference

- [Google Search Central Appearance Specifications](references/google-appearance-specs.md): Full technical thresholds for Title Links, Snippet controls (`max-image-preview`, `data-nosnippet`), AI Overview query fan-out mechanics, Discover image dimensions (≥1200px, 300k px), JSON-LD entity author rules, and Google SERP Favicon specifications (stable URLs, multi-res ICO, globe fallback avoidance).
- [Competitive Advantage & Content Moat](references/competitive-advantage-and-content-moat.md): Strategic differentiation, Utility-First Media architecture, and practical finance query targeting.

## 1. End-to-End Publication Procedure

Follow these steps in strict sequence for every new article or major update:

### Step 1: Content Planning & Query Fan-Out
1. Formulate a high-CTR title:
   - **Standard Commercial / Educational Guides**: `[Angka/Fakta Spesifik] + [Manfaat Utama] + [Tahun 2026] + [Bonus/Kurikulum]`.
   - **High-Distress / Financial Crisis & Dispute Queries (Office Harassment, Galbay, Debt Collection)**: `[Masalah Spesifik: Kata Kunci Utama] + [Pattern-Interrupt / Reassurance Emosional: "Jangan Resign!" / "Tanpa Takut SP" / "Amankan Karir"] + [Angka Solusi: 5 Cara/Trik] + [Bonus Aset Praktis: + Skrip HRD / + Format Surat]`. Searchers in acute financial distress suffer from panic and career anxiety; a dry informational title gets skipped, whereas an immediate pattern-interrupt hook addressing their worst fear dramatically spikes SERP CTR.
   - **Viral Social / Public Policy News Adaptation (Instagram Reels / Threads Hooks)**: `[Entitas Sasaran: Warga RI / Debitur] + [Isu Viral Spesifik: Bakal Dapat HP Gratis? / Terancam Sanksi?] + [Verifikasi & Manfaat: Cek Fakta, Syarat & Rekening Bansos]`. The first 30–35 characters must deliver the core curiosity hook so mobile searchers immediately recognize the trending social topic before SERP ellipsis cutoff.
   - **Breaking Legal Enforcement, Anti-Corruption (KPK/Polri/Gakkum) & Disasters**: `[Aksi Penindakan: KPK Tahan 5 Tersangka / Gakkum Segel Puluhan Konsesi] + [Nama Kasus/Lembaga: OTT BNPB / Karhutla Kalimantan] + [Barang Bukti/Sanksi Spesifik: Sita Rp 3,3 Miliar & Logam Mulia / Ancaman Penjara 10 Tahun]`. Breaking legal and crime news demands concrete verified metrics (suspect counts, exact cash amount, seized precious metals or crypto) in the headline; vague phrasing ("Diduga Korupsi, Sejumlah Pejabat Ditangkap") lowers CTR on Google Discover and SERP News carousels.
   - Length: 55–68 characters. Keep the core keyword phrase in the first 24–40 characters to avoid mobile SERP truncation.
   - Suffix ` • DailyFinance.id` is automatically appended by `publisher_engine.py`.
2. Craft a unique 140–160 character meta description. Summarize actionable data (modal, profit margin, payback time, concrete steps) as a SERP pitch.
3. Identify 3–4 sub-intent queries to answer in the FAQ section to capture Google AI Overview query fan-out branches.
4. When adapting source material from social media (Instagram infografis, X threads), direct curl and yt-dlp frequently fail due to Meta auth walls. Use `browser_exec` to navigate to the post, extract `document.body.innerText`, and query DOM images (`document.querySelectorAll('article img, div img')`) to extract high-resolution (1080x1350) CDN assets. Cross-reference with primary corporate investor relations, regulatory filings (OJK/BI), or official press releases to obtain exact verified metrics (CASA, NPF, CoF, YoY growth) required for EEAT credibility.
5. **Thematic Topic Cluster Siloing & Sister Article Cross-Linking**: Identify existing articles within the same thematic silo (e.g., when publishing a gig-economy side job guide like ojol/ShopeeFood, locate the regulatory article `perpres-potongan-ojol-maksimal-8-persen-kemenhub-resmi-berlaku-juli-2026.html`). Interlink between cluster siblings in addition to site utilities (`kalkulator-bunga-pinjol-ojk.html`, budgeting tools). This internal semantic linking cements topical authority and keeps crawl paths dense.

### Step 2: Editorial Drafting & On-Page Assembly
1. **Direct Answer / BLUF Box**: Open within the first 100 words with a dark gradient card (`<div class="p-4 rounded-4 mb-4 text-white" style="background: linear-gradient(...)">`) featuring a 3-column metric summary (Modal, BEP/Margin, Kunci Sukses).
2. **Data & Comparison Tables**: Provide at least 1–2 native semantic `<table>` elements with explicit headers (`<thead>`, `<th>`) for costs, specifications, or schedules.
3. **Images, Attribution & Discover Readiness**:
   - Hero and content images must be minimum 1,200px wide, 16:9 ratio, WebP format (~800px-1200px, quality 80–85).
   - **Indonesian Media CDN Parameter Probing (Detik/CNN Indonesia)**: When user provides image URLs from media portals like Detikcom or CNN Indonesia (`akcdn.detik.net.id/visual/...`), the raw link often embeds thumbnail parameters such as `?w=650&q=90` (rendering only 650x366 px). Never accept low-resolution thumbnails or perform artificial upscaling; probe changing parameters to `?w=1200&q=90` or `?w=1280&q=90`. The CDN dynamically serves crisp native 1280x720 HD 16:9 imagery meeting Google Discover criteria immediately.
   - **EXIF Orientation Auto-Normalization**: Always execute `from PIL import ImageOps; img = ImageOps.exif_transpose(img)` immediately after opening candidate image files before cropping, resizing, or converting to WebP. User-contributed photography from Wikimedia Commons or smartphone uploads often embed EXIF Orientation metadata (e.g. orientation 6 or 8); converting them without transposing causes browsers to render images sideways (90° rotated) or upside down on the live page.
   - **Distinct & Relatable Image Assets**: Never re-use the hero/featured image inside the body text. Every body image slot must be a unique asset illustrating an operational step, product, or sub-topic. Choose relatable, visually appealing compositions (warm flat-lays, colorful objects, authentic tools) that make people actually want to read, rather than cold, sterile spreadsheets or generic stock photos.
   - **Cultural & Contextual Authenticity**: Ensure imagery matches Indonesian cultural reality (e.g. genuine Indonesian rupiah currency, local planners/equipment) instead of ambiguous foreign stock photos of unidentified people or currencies that break reader trust.
   - **Editorial Hero vs. Product Card Separation**: The hero/featured image must ALWAYS be an authentic editorial or lifestyle photograph (e.g. human hands setting an AC remote, an authentic room setup, or an editorial problem-solving scene). NEVER use commercial marketing banners, brand ambassador posters, or promotional graphics with sale badges and marketing slogans ("SUPER FAST COOLING", logos, retail pricing) as the article hero or homepage thumbnail. Commercial product photography belongs strictly INSIDE the article body within the mid-content affiliate product card.
   - **Subject Framing & Active Zone Cropping**: Wide landscape stock photos (e.g. parks, playgrounds, commercial streets) often place the relevant activity or equipment in a small fraction of the frame. Crop tightly to the active subject zone (e.g. sandbox play area, operational tools) before resizing to standard 960–1,200px WebP; uncropped wide scenery gets visually interpreted by readers and Discover algorithms as generic landscape, diluting topical relevance.
   - **Caption Fidelity to Verified Visuals**: Ensure `<figcaption>` copy precisely matches what is inspectably visible in the image. If a photo captures an ambient playground sandbox rather than a clear close-up of a specific mechanical digger, describe it accurately (e.g. "Area bermain pasir anak di taman rekreasi &mdash; konsep yang menginspirasi wahana rental excavator mini") instead of over-claiming unverified equipment details that visual inspection will contradict.
   - **Image Sourcing & Resolution**: Sourced images must be minimum 960px to 1,200px wide (StockSnap 960w, Flickr high-res CC, Openverse, or Shopee CDN `@resize_w1200_nl`), WebP format, quality 80–85. When fetching from StockSnap CDN, always pass a desktop browser User-Agent to avoid 403 Cloudflare/CDN blocks. When sourcing from Wikimedia Commons, include an informative User-Agent (`User-Agent: DailyFinanceBot/1.0`) and avoid burst requests to prevent HTTP 429 rate limiting. For company-story articles, a brand-owned upload on Commons (PT upload under CC BY-SA) is the most credible hero/body source; credit it with the author/uploader line and license exactly as shown on the file page.
   - **Wikimedia Commons API Thumbnail Resolution**: Never guess or construct arbitrary thumbnail URLs (e.g. `.../2560px-....jpg`) on Wikimedia Commons CDN paths; doing so returns `HTTP 400 Bad Request`. Always query the MediaWiki API: `https://commons.wikimedia.org/w/api.php?action=query&titles=File:...&prop=imageinfo&iiprop=url&iiurlwidth=1920&format=json` to fetch the authorized `thumburl` or use the direct original `url`.
   - **Mandatory Source Attribution Standard**: Every image (hero and body) must feature a centered source credit specifying platform, author/creator, and exact license: `<figcaption class="text-center text-muted fst-italic small mt-2">Deskripsi visual relevan. Foto: [Platform] ([Nama Kreator/Dokumentasi], lisensi [CC0/CC BY/...])</figcaption>`. Generic tags like "Dok. Pribadi" on external photos are strictly forbidden.
   - **Scratch Workspace Isolation & Test Crop Purging**: Never download raw candidate images, generate test crops, or dump scraped HTML directly into `/root`. Isolate all intermediate image downloads, crop iterations, and DOM scrapes in a designated scratch directory (`/root/.hermes/profiles/orion/cache/scratch/` or `$TMPDIR`), and delete temporary test crops after final WebP generation. Save ONLY the final, validated WebP asset to `/root/dailyfinance_web/assets/img/` or `assets/img/blog/`. Keep one-off publishing scripts in `/root/dailyfinance_web/scripts/` rather than loose in `/root`.
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
     <button class="btn btn-sm btn-outline-secondary py-1 px-3" onclick="copyTemplate('tmp1', this)">📋 Salin Template</button>
     ```
     With lightweight vanilla JS supporting visual feedback (`✅ Tersalin!` reverting after 1.6s). Always pass `this` to preserve the button element reference across asynchronous `navigator.clipboard.writeText().then(...)` callbacks (where `event.target` or `window.event` is detached/undefined), and implement a synchronous `fallbackCopy(text, btn)` using a temporary `textarea` + `document.execCommand('copy')` so copy functionality still works in headless browsers or non-HTTPS contexts.
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
     1. Obtain each shortlink as text from the source (copy/paste or a text export). Never transcribe short-link codes from a screenshot by vision alone.
     2. Probe each code: `curl -sL -A "WhatsApp/2.23.20.0" -o /tmp/x.html -w "%{url_effective}" https://s.shopee.co.id/<code>`. Dead = final URL `https://shope.ee/error_page`; live = an `og:title` meta tag is present.
     3. Confirm the `og:title` product matches the article promise. On mismatch, report it to the user before publishing.
     4. For a dead link, substitute a Shopee search fallback and tell the user which links were replaced and why.
   - Limit product cards to 4–8 relevant recommendations with distinctive call-out badges.
9. **Numbered List & Review Architecture ("N [Items]" Title Contract)**:
   - **Exact Count Delivery**: When a title or headline promises a specific count (e.g., "Review 7 Pinjol Legal Bunga Terendah", "5 Langkah Bebas Galbay"), every single item from 1 to N must be fully authored with an individual evaluation card, official credentials, pros, cons, and operational terms. Never stop after item #1 or leave the remaining items truncated.
   - **Grounding in Internal Database (`fintech-db.js`)**: For all fintech/P2P lending evaluations, strictly cross-reference company names, official OJK licenses, categories, interest caps, and operational limits against `assets/js/fintech-db.js` (95 verified entries).
   - **Strict Sub-Category Alignment with Search Intent**: When authoring consumer personal loan ("pinjol") roundups, filter `fintech-db.js` strictly by `Multiguna Konsumtif`. Never mix in business/SME financing platforms (`Produktif UMKM`).
   - **Synchronized Count Adjustments Across All Surfaces**: If an item is added or removed from a numbered list, update every single surface in lockstep: `<title>`, breadcrumb active item, `<h1>`, meta description, introductory lead copy, table headings, and card IDs.
   - **Unified Semantic Comparison Table**: Every comparative review article must provide a consolidated `<table>` benchmarking all N entries across critical decision dimensions.
   - **Utility Retention Bridge**: Embed an action card directly below the comparison table guiding readers into `kalkulator-bunga-pinjol-ojk.html`.
10. **Internal Linking**: Embed ≥3 contextual internal links pointing to Dailyfinance utilities.
11. **App-Based Fintech & Merchant Onboarding Architecture (Prerequisite Tiers & UX Flow)**:
   - Always highlight prerequisite account tiers (e.g. Akun Premium, KYC Level 2) in a distinct alert box before tutorial steps.
   - Mirror the official in-app navigation hierarchy in chronological order without inverted steps.
12. **Business Opportunity & Commercial Equipment Architecture ('Paket Usaha' & Rental Guides)**:
   - Unit cost and margin modeling (HPP per Unit).
   - Three-tier operational scenarios (Sepi / Sedang / Ramai) based on monthly operating days (26 days).
   - Concrete payback period (BEP) in BLUF box.
   - Mandatory operational risk alert box covering durability, spare parts, and venue compliance.

### Step 3: Automated Publishing & Site Synchronization
Run `publisher_engine.publish_article()` via Python (using `/usr/local/lib/hermes-agent/venv/bin/python` to ensure all `bs4`, `PIL`, and `cryptography` dependencies are present):
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

#### Dynamic Trending & Business Curation Engine Execution (`ranking_engine.py` & `business_engine.py`)
After publishing new articles:
1. `ranking_engine.py`: Recalculates time-decay popularity scores across the 4 content pillars for "Berita Pilihan Hari Ini".
2. `business_engine.py`: Automatically triggered by `publisher_engine.py` to curate the "Peluang Bisnis & Inovasi" 2-column section on `index.html`.
3. Numbering Guard: `publisher_engine.py` enforces strictly sequential numbering `1..10` on `.tab-posts-list .tab-post-num`.
Upload both `index.html` and `public_html/data/trending.json` to cPanel.

### Step 4: Server Deployment & Live Verification
1. **Deploy HTML & Synchronize Secondary Images**:
   - Secondary images AND affiliate product card images referenced in `body_html` must be explicitly uploaded to cPanel `public_html/assets/img/`.
   - Use `cpanel_pinjolresmi.upload_file(remote_dir, remote_filename, content, content_type=...)` with parameter `remote_filename` (NOT `filename`).
   - Use `ThreadPoolExecutor(max_workers=5)` for bulk file uploads (>10 files) to prevent terminal timeouts.
   - Set terminal timeout ≥180s for multi-article batches.
   - Trigger auto-indexing via `auto_index.run([url])`.
2. **Inspect Live HTTP Status**: Verify HTTP 200 on HTML and all images.
3. **Inspect Robots Meta**: Confirm `max-image-preview:large`.
4. **Headless Visual & Mobile Viewport Audit**:
   - Check at 1280px (desktop) and 390px (mobile) for `scrollWidth <= clientWidth`.
   - Scroll page progressively before verifying `naturalWidth > 0` on `loading="lazy"` images.
   - Calculate absolute document coordinates (`pos - offset`) for targeted component screenshots.
   - Verify visible FAQ presence via DOM count.
5. **Asset Replacement Routine**: When replacing images, update all 5 surfaces (HTML `<img>`, `alt`, `og:image`, `og:image:width/height`, index.html, blog.html).
6. **Post-Publication Title Mutation**: When updating headlines, synchronize all 5 surfaces (article HTML, index.html hero grid/ticker, blog.html, feed.xml, GSC submission).

### Step 5: Google Indexing API Push & Live Indexing Status Triage
1. Submit URLs via `gsc_indexing.push_urls()`.
2. Differentiate Stage 2 (Submitted/Queued) from Stage 3 (Indexed/Live in Google Index).
3. Query URL Inspection API with `siteUrl: "sc-domain:dailyfinance.id"`.
4. Verify slug registration in `gsc_indexing.py` `ALL_PAGES` between `ALL_PAGES = [` and `]` with import assertion.

### Step 6: Social Media Syndication & Interactive Utility Promotion
- Extract verified calculations from `assets/js/main.js`.
- Produce 1080×1350 px (4:5) simulation cards with calculated vertical heights.
- State explicit non-lender educational disclaimer.
- Structure viral funnels as unclaimed legal funds (BSU, JHT) rather than free giveaways.

### Step 7: Interactive Directory & Search Utility Architecture
- Dual search execution: reactive `input` filtering + explicit "Cari" button + Enter key handler + clear (✕) button.
- Bump cache-busting version strings (`?v=YYYYMMDD_XX`) on utility scripts.

### Step 8: Brand Identity, Legal Pages, & cPanel Service Management
- DailyFinance.id strictly operates on 4 pillars: News, Finance, Bisnis, Lifestyle.
- Never render compliance warning banners (`<aside style="background: #fff1f2; ...">`) at the top of pages.
- When creating cPanel email accounts via UAPI, replace credentials with `[REDACTED]`. Never output raw passwords in chat.

### Step 9: Community Forum Architecture & Authentic Venting Storytelling ("Ratapan Pinjol")
- Author authentic, human, non-sterile confessions: colloquialisms (`gw`, `bgt`, `udh`, `skrg`), emotional punctuation (`..`, `😭😭`), diverse personas (Gen Z FOMO, spouse gambling betrayal, fake freelance task scam, factory worker borrowed KTP, street vendor child threats, recovery story).
- UI/UX: collapsible truncation (>300 chars with `Baca Selengkapnya ▾`), dynamic character counter, floating toast notifications, mobile FAB (`✍️ Tulis Curhat`), deep-link permalinks (`?id=xxx`).
- SQLite on cPanel: checkpoint WAL transactions (`PRAGMA wal_checkpoint(TRUNCATE);` and `VACUUM;`) after updating `.db` files, enforce `no-cache` headers, and append `&_t=${Date.now()}` on fetch requests.

### Step 10: Sitewide Dark/Light Theme Engineering (Zero-FOUC & 3-Point Toggle Pattern)
1. **Zero-FOUC Protocol**: Disallow deferred or DOMContentLoaded theme application. Embed an un-deferred synchronous script in `<head>` right before CSS links:
   ```html
   <script>
     (function(){
       try {
         var t = localStorage.getItem('df_theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
         document.documentElement.setAttribute('data-theme', t);
       } catch(e) {}
     })();
   </script>
   ```
2. **Color Token System (Deep Obsidian Slate)**:
   - Base background: `#0b0f19` (Obsidian Navy).
   - Elevated cards & widgets: `#151d30` (Dark Slate).
   - Navbar & Surfaces: `#111827` (Slate 900).
   - Primary text: `#f8fafc`; Secondary text: `#cbd5e1`; Muted: `#94a3b8`.
   - Borders: Subtle `#1e293b`, Strong `#334155`.
3. **3-Point Access Pattern**:
   - Desktop Top-Line: Circular icon button beside social icons (`#theme-toggle-btn-desktop`).
   - Mobile Header: Dedicated 1-tap button beside the hamburger menu (`#theme-toggle-btn-mobile-header`) for instant night switching without opening menus.
   - Mobile Drawer: Interactive row inside navigation drawer (`#theme-toggle-btn-drawer`) with live status label ("Mode Gelap" / "Mode Terang").
4. **Mandatory Cache-Buster Bump**: Any update to theme tokens in CSS/JS requires updating `?v=` across all host HTML files and `publisher_engine.py`.

### Step 11: Concise Media Kit & Advertising Architecture (`pasang-iklan.html`)
1. **Concise Copywriting Model (Follow Pontianak Prime standard)**:
   - Do not author verbose multi-section essays or repetitive cards on commercial inquiry pages.
   - Structure the page into 4 concise elements:
     1. Punchy Hero: "Elevate Your Brand with DailyFinance.id" + 1 strategic paragraph.
     2. 3 Premium Offerings:
        - Pemasangan Banner & Iklan Strategis (desktop & mobile).
        - Content Placement & SEO Backlink (digital reputation & authoritative search ranking).
        - Kemitraan Promosi Kustom (tailored creative campaigns).
     3. Direct Callout: "Jadilah Bagian dari Ekosistem Informasi Kami" + official business email (`partnership@dailyfinance.id`).
     4. Compact Quick Form: 4 essential fields (Brand/Company, Representative Name, Business Email, Desired Service) for 1-click submission.
2. Ensure full Dark/Light theme adaptability and zero horizontal overflow on mobile viewports (360–390px).

### Step 12: Desktop Navbar Utility Placement (`💔 Ratapan Pinjol`)
1. **Positioning Standard**: Sitewide community and utility links must be placed at the far right of the desktop navigation bar (`.navbar-nav-hm`), immediately AFTER "Semua Artikel ▾" and right before the search form (`.search-box-hm`).
2. **Visual Contrast**: Style with explicit inline color and weight (`style="color: #ef4444 !important; font-weight: 800;"`) and top/bottom active borders so the link stands out as an actionable community anchor without breaking the editorial dropdown hierarchy.

## 2. Hard Quality Gates & Evidence Checklist

Before declaring any publishing or SEO task complete, provide the following verifiable evidence:
1. **Robots Meta Verification**: Exact grep proof showing `max-image-preview:large, max-snippet:-1` on the live URL.
2. **Schema Validity**: JSON-LD block parsed via `json.loads()` with zero syntax errors.
3. **HTTP Status**: Live URL and all referenced body images and affiliate product card images return 200 OK.
4. **Distinct Image Assets & Orientation**: Zero duplicate re-use of hero image within inner body sections, and all sourced images pass EXIF orientation transposition check (`ImageOps.exif_transpose`).
5. **GSC Indexing & Sitemap Inclusion Proof**: Output showing `0 failed` from `gsc_indexing.push_urls()`, confirmation of the URL in live `sitemap.xml`, confirmation of local file existence before URL Inspection query, and verified registration in `gsc_indexing.py` `ALL_PAGES`.
6. **Editorial Integrity**: Attribution credits present on all images with explicit source tags (`Foto: Dok. ...`), affiliate disclosure box present above product cards with `rel="sponsored nofollow"`.
7. **Mobile Responsiveness & CTA Ergonomics**: Clean 390px viewport render with zero horizontal overflow (`scrollWidth <= clientWidth`); primary affiliate CTA buttons span full width (≥300px, height ≥40px).
8. **Promised Artifact Integrity ("Title Contract" & Numbered Count)**:
   - If the title promises a specific count, verify via grep or DOM count that all N distinct items exist as fully realized cards.
   - If the title contains '+ Template', '+ Format', '+ Kalkulator', verify actual copyable templates with working copy buttons (`copyTemplate`).
9. **Mobile Share Bar Visibility**: Verify Threads share button occupies the first position in `.share-buttons-list`.
10. **Interactive Directory & Search Ergonomics**: When deploying directory search inputs, verify (1) explicit 'Cari' button triggers search, (2) clear (✕) button resets results, (3) Enter key submits query, and (4) script tags carry fresh cache-busting strings.
11. **Visible FAQ Card Rendering**: Confirm DOM presence of rendered FAQ cards (`document.querySelectorAll('.accordion-faq-static .card').length > 0`).
12. **Onboarding & Tutorial Step Sequence Integrity**: Verify prerequisite account tiers appear in an alert box before numbered steps, and step sequence matches official app navigation flow.
13. **Asset Replacement Synchronization Gate**: When replacing an image asset, confirm `alt` text describes the new visual across article, `index.html`, and `blog.html`, `og:image:width/height` match exact dimensions, and caption includes photo attribution.
14. **Favicon Integrity & SERP Globe Fallback Prevention Gate**: Confirm multi-res layers up to 256×256 in root `/favicon.ico`, unversioned icon link tags, and homepage `<lastmod>` updated in sitemap.
15. **Batch Image Visual Gate**: Review all candidates via vision before upload; reject masked/obscured faces, dim frames, or mismatched subjects.
16. **Dynamic Trending Engine Gate**: Verify `ranking_engine.py` ran successfully and updated `index.html` and `public_html/data/trending.json`.
17. **Clean Header & Sitewide Banner Removal Gate**: Confirm top header renders without compliance warning banners, and `builder_hotmagazine.py` generates clean headers without `<aside style="background: #fff1f2; ...">`.
18. **Sitewide Dark/Light Theme Gate**: Confirm (1) zero-FOUC script present in `<head>`, (2) desktop, mobile header, and drawer toggles switch theme dynamically, (3) `localStorage.getItem('df_theme')` persists across page reloads, and (4) all 102+ production pages render with valid text/background contrast.
19. **Desktop Navbar Utility Placement Gate**: Confirm `💔 Ratapan Pinjol` is rendered at the end of `.navbar-nav-hm` after "Semua Artikel" across all site pages and `builder_hotmagazine.py`.
20. **Media Kit & Advertising Conciseness Gate**: Confirm `pasang-iklan.html` follows the concise 3-service model (Banner, Content/SEO, Kemitraan Kustom) with direct email contact and compact form, free from verbose text bloat.

## 3. Pitfalls & Anti-Patterns (Rule + WHY)

- **Probe and replace dimension query parameters (`?w=1200&q=90`) on Indonesian news portal CDNs (Detik/CNN Indonesia) before converting or upscaling — media CDN links often default to 650px (`?w=650&q=90`), but dynamically serve native 1280x720 HD 16:9 WebP/JPEG assets.** Blindly using the default 650px URL fails Google Discover's minimum width threshold of 1,200px, and digital upscaling softens facial features and badges, whereas probing `w=1200` or `w=1280` on the CDN returns crisp native photography immediately.
- **Never call `.get('status')` on `cpanel_pinjolresmi.list_files()` — the function returns a raw Python `list` of filenames/items, not a response dictionary.** Invoking dict methods like `.get()` on the return value of `list_files()` throws an immediate `AttributeError: 'list' object has no attribute 'get'` and halts verification scripts. Check `isinstance(res, list)` and `len(res)` directly.
- **Always invoke `publisher_engine.py` using the dedicated project virtualenv (`/usr/local/lib/hermes-agent/venv/bin/python`) rather than system `python3` — system Python often lacks `bs4`, `PIL`, or `cryptography`.** Running publishing scripts with bare `python3` triggers fatal `ModuleNotFoundError` for BeautifulSoup or PIL, aborting compilation before HTML generation or cPanel synchronization begins.
- **Extract social media news material (Instagram/X) using `browser_exec` DOM evaluation when `curl` and `yt-dlp` hit login walls or bot blockers — headless browsers render full post text and expose high-resolution CDN images in `<img>` tags.** Meta aggressively blocks datacenter CLI scrapers on `/p/<id>` links, but headless browser sessions allow JavaScript extraction of caption text and high-res image sources (1080x1350) for immediate caching.

- **Never allow dark mode switching without a synchronous Zero-FOUC script in `<head>` — deferred or DOMContentLoaded theme application causes a jarring white flash on page transitions.** Executing theme scripts on `DOMContentLoaded` lets the browser paint the default white body background before JavaScript swaps the attributes, blinding nighttime readers on every navigation. The theme script must run inline in `<head>` before the DOM renders.
- **Always bump CSS/JS `?v=` version tags across all HTML files and `publisher_engine.py` whenever theme tokens are modified — mobile and desktop browsers cache stylesheets aggressively.** Updating CSS rules on the server without bumping the version string leaves returning visitors executing cached stylesheets, producing mismatched text colors (e.g. dark text on dark backgrounds) and broken toggle styles.
- **Never place primary desktop navigation utility links before main editorial dropdowns — positioning utilities after 'Semua Artikel' right before the search box preserves natural editorial reading hierarchy while giving the utility immediate visual prominence.** Placing a standalone community tool in the middle of editorial categories confuses visitors scanning for news rubrics; placing it at the far right right before the search box acts as a natural high-visibility anchor.
- **Avoid verbose multi-page essays on commercial media kit pages (`pasang-iklan.html`) — prospective advertisers and agencies scan for capabilities in seconds; verbose walls of text cause high bounce, whereas a punchy 3-service framework (Banner, Content/SEO, Kemitraan Kustom) with direct email drives higher conversion.** Media buyers require clear deliverables, contact emails, and quick inquiry forms; academic explanations of advertising theory create friction and delay lead generation.
- **Never author community venting stories in formal or sterile journalistic grammar — real debt distress posts require authentic netizen voice, emotional punctuation, colloquialisms, and diverse backgrounds.** Clean, polite AI prose reads as synthetic corporate fiction and fails to build emotional solidarity; authentic posts feature colloquial abbreviations (`gw`, `bgt`, `udh`, `ampe`), natural typos, and visceral emotional conflicts (judol spouse betrayal, fake Telegram jobs, school threats, collection terror).
- **Always checkpoint SQLite WAL mode transactions (`PRAGMA wal_checkpoint(TRUNCATE);` and `VACUUM;`) after updating SQLite database files on cPanel — uploading a new `.db` file does not overwrite active WAL transactions if `-wal` and `-shm` exist.** In SQLite WAL mode, readers query the active `-wal` journal; overwriting only the base `.db` file leaves old records serving from the journal, creating phantom rollbacks or stale content.
- **Never duplicate numbering in the popular articles widget (`.tab-posts-widget`) — numbers must strictly be sequential 1..N.** In `index.html`, prepending new entries without re-indexing creates jarring duplicate numbers in `.tab-post-num`. Always maintain strict sequential order (1 to 10), enforced automatically by `publisher_engine.py`.
- **Always trigger `business_engine.update_business_section()` when publishing tips, usaha, or bisnis articles.** Failing to update the "Peluang Bisnis & Inovasi" section leaves the right column on `index.html` showing stale, unrelated news from weeks ago rather than featuring the newest business and micro-enterprise guides.
- **Never leave compliance warning banners (`<aside style="background: #fff1f2; ...">`) in `builder_hotmagazine.py` or article headers.** Sitewide compliance disclaimer banners at the top of pages signal a defensive credit-broker or legal watchdog stance that degrades editorial aesthetic and prompts reader distrust.
- **Use `ThreadPoolExecutor(max_workers=5)` for bulk cPanel file uploads — never upload tens of files sequentially in a single thread.** Uploading 80+ HTML files sequentially takes 3–5 minutes and frequently trips the 60s/180s terminal command timeout, leaving the live site in an inconsistent half-updated state. A pool of 5 workers uploads 80+ files in under 50 seconds reliably.
- **Query Wikimedia Commons API with `iiurlwidth` for thumbnail URLs — never hand-craft arbitrary width prefixes on CDN paths.** Hand-crafting width prefixes directly on `upload.wikimedia.org` triggers `HTTP 400 Bad Request` and breaks automated downloads mid-batch. Always query the API with `prop=imageinfo&iiprop=url&iiurlwidth=1920&format=json`.
- **Set terminal timeout ≥180s when executing multi-article publishing scripts.** Sequential cPanel uploads, asset synchronizations, and API index pings across 2–3+ articles easily exceed the default 60s timeout, causing the shell to SIGKILL the runner and leaving later articles in an un-uploaded 404 state on production.
- **Always run `ranking_engine.py` and upload `data/trending.json` after publishing breaking articles.** Omitting the ranking engine update leaves the homepage "Berita Pilihan Hari Ini" section showing stale, lower-engagement stories rather than elevating freshly published breaking news across the 4 content pillars.
- **Enforce strict minimalism on static contact and inquiry pages (`kontak.html`) — never invent operational phone numbers or street addresses.** Keep contact forms strictly minimal and editorial communication limited to verified official email channels (`redaksi@dailyfinance.id`, `partnership@dailyfinance.id`). Invented operational metadata damages journalistic E-E-A-T credibility.
- **Use `auto_index.run([url])` or `push_indexnow()` for search engine discovery — `submit_indexnow` does not exist.** Invoking `auto_index.submit_indexnow()` triggers an `AttributeError` that halts the post-publish discovery sequence mid-run.
- **Pivot immediately to Wikimedia Commons archives when Indonesian government portals ('.go.id') geoblock datacenter IPs.** When authoritative public service imagery is required, do not waste tool calls retrying direct browser captures of `.go.id` pages; immediately query Wikimedia Commons archives for verified headquarters photography or state wire documentation.
- **Never pass `filename=...` to `cpanel_pinjolresmi.upload_file()` — the parameter name is `remote_filename`.** Always pass `remote_filename` as the second argument; passing `filename` triggers a fatal `TypeError` and aborts file transfers to cPanel.
- **Always resolve e-commerce affiliate shortlinks with `WhatsApp/2.23.20.0` User-Agent to extract canonical titles and clean CDN images.** Shopee blocks datacenter IPs for desktop browsers, but serves full Open Graph metadata (`og:title`, `og:image`) to WhatsApp crawlers, yielding verified product titles and clean images.
- **Always update all 5 surfaces when revising an article title for higher CTR.** Update article HTML, `index.html` hero grid/ticker, `blog.html` card, and `feed.xml` RSS title before uploading to cPanel and resubmitting to GSC.
- **In interactive 1-click clipboard functions (`copyTemplate`), pass `this` explicitly.** Always declare `onclick="copyTemplate('id', this)"` and implement a synchronous `fallbackCopy(text, btn)` using a hidden textarea to preserve visual feedback across detached event contexts.
- **Never transcribe affiliate short-link codes from a screenshot by vision alone** — glyph confusions produce invalid codes; probe every code as text before embedding it.
- **Verify product-to-topic alignment on every affiliate card** — a link resolving to the wrong product type breaks the article's title promise and reader trust.
- **Scan long AI-drafted articles for garbled phrases and repeated figures before the builder runs** — long drafts accumulate mid-sentence corruption; catch them before upload.
- **Normalize units and typographic characters in a dedicated pass before publishing** — `m2`/`m3` must be `m²`/`m³`, `Rp6 miliar` spacing kept consistent, and en-dashes used in numeric ranges.
- **Sitewide element removal must key on a unique signature, not a visible label.** Locate elements by exact href/query target and leave lookalike text inside article bodies untouched.
- **Bulk `?v=` cache-busting bumps must be verified by count.** Replace the full token across every HTML page and verify with live grep.
- **Always normalize EXIF orientation via `ImageOps.exif_transpose()` before converting or cropping image candidates** — converting raw uploads to WebP without transposing causes images to display 90° sideways or upside down on the live website.
- **Explicitly upload affiliate product card images alongside body images to cPanel** — `publisher_engine` only transfers the hero image; omitting explicit upload leaves broken 404 images inside product cards.
- **Perform a complete progressive scroll with settling pauses before asserting `naturalWidth > 0` on lazy-loaded images** — off-screen lazy images report zero width and incomplete status until scrolled into view.
- **Calculate absolute document coordinates before capturing targeted component screenshots for visual audit** — compute `getBoundingClientRect().top + window.scrollY` and pause for settlement before snapping.
- **Never rely on unbounded token replacement (`replace(']', ...)`) or optimistic print logs when mutating registry files (`gsc_indexing.py`)** — bound insertion between `ALL_PAGES = [` and `]`, and verify via runtime import assertion.
- **Always programmatically auto-detect `og:image` dimensions from the actual asset file via PIL** — pass the local image path to `Image.open().size` in `publisher_engine.py` to prevent incorrect Open Graph aspect ratios.
- **Never append query parameters (`?v=...`) to favicon `<link>` tags** — Google's favicon crawler requires a stable, permanent URL; query strings disrupt Google's favicon indexing pipeline.
- **Always compile root `favicon.ico` with multi-resolution layers (16/32/48/64/128/256 px)** — Google Search guidelines explicitly require site favicons to be multiples of 48px square or SVG.
- **Always update homepage `lastmod` and trigger recrawl when changing favicons** — Google extracts the site favicon strictly from the root homepage (`/`).
- **Always verify the target URL exists before interpreting `URL is unknown to Google` in URL Inspection** — an invalid or typo URL deceptively mimics crawl-queue behavior.
- **Always synchronize `alt` text and image dimensions across all surfaces when replacing an image asset** — rewrite `alt` descriptions and sync `og:image` dimensions to prevent stale metadata.
- **Never omit photo source attribution (`Foto: ...`) when adopting user-provided or third-party images** — publishing external photography without credit diminishes Google EEAT trustworthiness.
- **Never publish wide uncropped landscape photos where the focal subject is lost in the background** — crop tightly to the active subject zone before converting to WebP.
- **Never attribute specific technical features or equipment in image captions that are not clearly visible** — accurately describe the broader visible scene to maintain factual transparency.
- **Always pair 'paket usaha' revenue projections with operational equipment risk warnings** — analyze durability, spare parts, and venue compliance alongside gross revenue.
- **Never conflate Indexing API submission success with actual Google SERP indexing** — `push_urls()` returning `0 failed` only confirms crawler queue receipt. Check URL Inspection API for actual indexing status.
- **Never omit prerequisite verification tiers in app-based onboarding guides** — highlight requirements like Akun Premium or KYC Level 2 before numbered steps.
- **Strictly mirror the official in-app navigation hierarchy in procedural guides** — never invert navigation steps.
- **Always interlink newly published guides with sister articles in the same thematic cluster** — build contextual depth across related articles.
- **Never rely solely on reactive 'input' event filtering without an explicit 'Cari' button and Enter key handler** — provide explicit submission controls for mobile users.
- **Never mix productive/business lending platforms into consumer "pinjol" review roundups** — keep consumer personal loan reviews aligned with personal borrower intent.
- **Never conflate distinct corporate brands or bank products with unrelated fintech entities** — verify entity precision against `fintech-db.js`.
- **Always synchronize title, meta, H1, breadcrumb, intro text, and table headers when adjusting numbered list counts** — update all surfaces in lockstep.
- **Never publish or leave a numbered list article with a truncated item count** — deliver all promised items from 1 to N in full.
- **Never ship an article promising "+ Template" without exhaustive, copy-pasteable script blocks and 1-click copy buttons** — provide complete, ready-to-use scripts.
- **Always position the primary social share button (Threads) first in the share list** — prevent wrapping cutoffs on narrow mobile screens.
- **Always include `max-image-preview:large` and `max-snippet:-1` in meta robots** — enable high-visibility cards and generative snippet extraction.
- **Never duplicate the hero/featured image inside inner article sections** — use distinct assets for inner slots.
- **Always add `rel="sponsored nofollow"` and a visible editorial disclosure on affiliate links** — maintain Google AdSense and search compliance.
- **Never future-date articles or update `dateModified` without substantive revisions** — avoid freshness manipulation flags.
- **Maintain exactly one `<h1>` that mirrors the `<title>`** — preserve clear topical entity signals.
- **Ensure hero images are at least 1,200px wide and 16:9 aspect ratio** — meet Google Discover eligibility criteria.
- **Randomize view counters per article** — avoid uniform numbers that read as fabricated social proof.
- **Never allow visible marketplace brand names in any CTA button across the page** — keep button copy curiosity-driven and neutral (`🛒 Cek Spesifikasi & Harga Terbaru →`) with marketplace links restricted strictly to `href` + `rel="sponsored nofollow"`.
