---
name: editorial-news-publishing
description: Use when publishing news stories or editorial articles.
version: 2.0.0
author: Orion Fleet Lead
license: MIT
metadata:
  hermes:
    tags: [editorial, news-publishing, journalism, news-paraphrase, photo-attribution, geo, ai-overview, schema-newsarticle, google-indexing-api, auto-publisher, grid-parity, mobile-antara-feed, dual-image-editorial, unit-economics-modeling, canonical-footer-sync, sitewide-boilerplate-lock, affiliate-product-cards, sponsored-nofollow, anti-bot-shortlink-resolution, affiliate-duplicate-distribution, ticker-dynamic-duration, mobile-tap-target-cta, affiliate-link-audit, gsc-post-publish-proof, telegram-og-cache-bust, targeted-scroll-qa, live-browser-retry-loop, sticky-nav-scroll-offset, proactive-four-pillar-report, event-seo, travel-fair, music-festival, triple-schema]
    category: software-development
---

# Editorial News Publishing, Event SEO & Content Optimization Architecture

A class-level procedural skill for authoring, paraphrasing, structuring, and deploying high-CTR, high-authority news articles, time-sensitive commercial event guides, and editorial analyses for digital media portals. Governs journalistic wire rewrites, clean photo attribution credits, Generative Engine Optimization (GEO) answer boxes, contextual conversion callouts, automated multi-surface homepage synchronization, adaptive mobile newsfeed styling (ANTARA News pattern), commercial event SEO, and rapid search engine indexing.

---

## 1. When to Use

Use this skill when:
1. Converting official press releases or wire service reports (e.g. Antara News, Bloomberg, Reuters, regulatory agencies) into comprehensive editorial articles.
2. Paraphrasing factual news stories while enhancing topical depth with real-sector impact analysis and macroeconomic implications.
3. Formatting featured news imagery and photo captions according to professional journalistic standards.
4. Implementing Generative Engine Optimization (GEO) direct-answer boxes (BLUF) and HTML comparison tables for Google AI Overviews.
5. Embedding contextual, high-converting native utility callouts (calculators, verification tools) without degrading editorial integrity.
6. Authoring business, e-commerce, or retail guide articles requiring concrete financial modeling (unit economics: HPP, platform commission fees, promo discounts, and net margin).
7. Deploying news stories via the automated publishing pipeline to ensure instant, synchronized presence across the homepage (`index.html`), archive (`blog.html`), sitemap, cPanel hosting, and Google Indexing API.
8. Implementing or maintaining mobile-first news layouts (e.g. ANTARA News style headline + vertical list feed) while preserving multi-column desktop parity.
9. Publishing content for time-sensitive commercial and entertainment events (airline travel fairs, music festivals & concerts, bank card flash promotions, auto expos) with triple Schema markup (`Event`/`MusicEvent` + `FAQPage` + `Article`).

---

## 2. Core Procedural Workflow

### Step 1: Wire Ingestion & Deep Analytical Paraphrase
1. **Fact Extraction & Multi-Source Triangulation**:
   - Extract raw figures, exact dates, quotes, and primary regulatory/agency entities from the source wire.
   - When the user provides a social media source (Instagram, X) or restricted URL, triangulate transaction details, corporate filings (e.g. CSPA agreements, IDX disclosures), and key figures via web search and public financial news before authoring.
   - Verify core statistics against official primary releases (e.g., central bank statements, ministry reports, corporate disclosures) before writing.
2. **Analytical Expansion Protocol**:
   - Never perform shallow line-by-line synonym substitution; thin rewrites risk search engine devaluation.
   - Synthesize the core factual development in the opening section, then contextualize the findings:
     - **Structural Drivers**: Contrast inward cash flows (e.g., export revenues, sovereign bond issuances, tax receipts) against outward obligations (debt service, foreign exchange interventions). For M&A or equity actions, analyze corporate holdings, ownership percentages, and supply-chain synergies (e.g., hauling infrastructure and port logistics vs. concession assets).
     - **Real-Sector Impact**: Explain tangible downstream effects on specific industries (e.g. how currency stability protects import-reliant manufacturing sectors like pharmaceuticals, food processing, or electronics).
     - **Consumer & Investment Repercussions**: Detail how the news influences retail interest rates, inflation, purchasing power, or capital market yields.
3. **Brand & Identity Consistency**:
   - Strictly respect designated domain brand casing (e.g. `Dailyfinance.id` with lowercase `f` across headers, footer credits, lead text, and publication metadata instead of camel-cased `DailyFinance.id` when specified).
   - **Canonical Sub-Footer & Copyright Uniformity**: Strictly maintain the minimal, modern copyright standard (e.g. `Copyright © Dailyfinance.id`) across the bottom bar (`.footer-bottom-line`). Strip dated calendar years (e.g. `© 2026`) and archaic legal boilerplate (`Seluruh Hak Cipta Dilindungi Undang-Undang`) unless explicitly requested.

---

### Step 2: Featured Image Optimization & Caption Attribution (Dual-Image Strategy)
1. **Asset Optimization & Dual-Image Strategy**:
   - When an article requires both an opening featured image and an in-body figure:
     - **Opening Featured Image**: Crop to standard 16:9 landscape aspect ratio (800x450 or 800x533), tightly framed on the key subject for above-the-fold hero impact. Convert to WebP (quality 80–85, under 65 KB) to ensure sub-100ms Largest Contentful Paint (LCP).
     - **In-Body Contextual Image**: Use an uncropped or documentary 3:2 aspect ratio (800x533) that reveals full contextual details (e.g., mobile screens showing live broadcast UI, contract papers on desk, pens, badges, background signage). Convert to WebP (under 50 KB).
     - **Multi-Asset Deployment Invariant**: When an article includes secondary figures in the body, the deployment pipeline must sync ALL referenced WebP assets to production hosting (`public_html/assets/img/`), not merely the primary featured image.
2. **Photo Caption Attribution Standard**:
   - The `<span class="image-caption">` element positioned beneath the featured image must strictly function as a concise source attribution or press agency credit (e.g., `ANTARA FOTO`, `ANTARA`, `Reuters`, `Foto: Stuart MacFarlane / Arsenal FC via The Times`), not a narrative paragraph summarizing the article.
   - When the user explicitly requests an attribution token (e.g., "di bawah foto tulisan ANTARA" or "jangan lupa buatkan foto ini dari sumber mana"), place that exact credit string inside `<span class="image-caption">[CREDIT]</span>` verbatim, centered directly under the image, without prepending redundant narrative text.
   - For secondary/documentary body images within the article, wrap in `<figure class="my-4 text-center">` and include `<figcaption class="image-caption mt-2 text-muted fst-italic small text-center">` with the exact journalistic attribution and concise moment description. Every visual asset in the post must carry inspectable source credit.
   - Center-align the attribution (`text-align: center`) in italicized muted gray (`#777777` or `#94a3b8`, 12px font size) for clean, unobtrusive presentation.

---

### Step 3: High-CTR Headline, GEO Answer Box & Structured Tables
1. **Headline Hierarchy**:
   - Format `<title>` and `<h1>` under 70 characters with primary keywords, quantifiable metrics, and impact anchors:
     `[Topic / Entity] Capai [Metric] per [Month Year]: [Core Driver] & [Key Impact]`
2. **GEO Bottom Line Up Front (BLUF) Box**:
   - Place an executive summary box within the first 100–150 words of the article body to maximize Google AI Overview citation probability.
   - Include 3–4 bulleted quantitative metrics:
     ```html
     <div class="geo-quick-summary">
       <h4>Ringkasan Eksekutif & Poin Kunci</h4>
       <ul>
         <li><strong>Posisi Terkini:</strong> Angka nominal dan perubahan dari periode sebelumnya.</li>
         <li><strong>Ketahanan Impor:</strong> Rasio cadangan terhadap bulan pembiayaan impor (bandingkan dengan standar IMF).</li>
         <li><strong>Fokus Kebijakan:</strong> Langkah stabilisasi nilai tukar dan pengelolaan likuiditas.</li>
       </ul>
     </div>
     ```
3. **Structured HTML Comparison & Unit Economics Tables**:
   - Present numerical comparisons and financial simulations in clean, semantic HTML tables wrapped in `<div class="table-responsive">` to prevent mobile horizontal blowouts.
   - **E-Commerce & Retail Business Modeling Standard**:
     For retail, social-commerce, and UMKM articles, break down unit economics into four distinct, audited sections:
     1. **HPP Riil (Modal Bersih)**: Bahan baku/grosir + kemasan/packaging (*ziplock/tag*) + upah tenaga kerja packing & lakban.
     2. **Penetapan Harga & Diskon**: Harga coret katalog (*anchor price*) + potongan flash sale/event + voucher toko = Harga bersih dibayar pembeli.
     3. **Beban Platform & Pemasaran**: Komisi kategori platform (misal 5%), biaya layanan gratis ongkir ekstra (3.5%), *payment fee* (1%), dan alokasi iklan *ads buffer* per unit.
     4. **Laba Bersih Tunai (Net Profit Margin)**: Pencairan saldo bersih masuk dikurangi HPP dan iklan = Laba bersih tunai per unit & persentase margin sehat (minimal 20–30% untuk menyerap retur). Include a scaled simulation.

---

### Step 4: Contextual Native Utility CTAs & High-Converting Affiliate Cards
1. **Contextual Native Utility Cards**:
   - Avoid intrusive popups or unrelated spam in serious financial or news reporting.
   - Embed contextual native callout cards matching user search intent (calculators, license checkers, emergency fund checklists).
2. **E-Commerce Affiliate Recommendation Cards Protocol**:
   - When monetizing guide articles via product recommendations, never paste bare URLs into body text.
   - Structure recommendations into dedicated visual cards (`.produk-grid` with `.produk-card`):
     - **Urgency / Trust Badge**: Prominent tag such as `Paling Laris`, `Pilihan Redaksi`, or `Rekomendasi Pemula`.
     - **Product Title & Benefit Spec**: Clear commercial title plus 1–2 sentences highlighting key specs and target audience.
     - **Pricing Anchor Psychology**: Struck-through MSRP (`<small>Rp ...</small>`) placed immediately next to the discounted promo price.
     - **Action-Oriented High-CTR Button**: High-contrast gradient button with an explicit shopping icon, benefit verb, and destination transparency (e.g., `🛒 Cek Harga Termurah di Shopee →`).
     - **Mobile Tap-Target Standard**: On mobile viewports (<= 576px / 390px), `.produk-card` CTA buttons must render full-width with touch height >= 38–44px, generous vertical padding, bold white text, and directional arrow.
   - **Mandatory Link Attributes**: Outbound affiliate links must strictly carry `rel="sponsored nofollow"` and `target="_blank"`. Never use plain `dofollow` links; failing to flag commercial affiliate links violates Google Search Essentials and risks manual penalties.
   - **Mandatory Editorial Disclosure**: Always append an explicit italicized disclosure directly beneath the product grid:
     `Catatan redaksi: Dailyfinance.id dapat menerima komisi dari pembelian melalui tautan di artikel ini tanpa biaya tambahan bagi pembaca.`
   - **Frequency Cap**: Bound recommendation cards to 3–6 curated items per article.
3. **E-Commerce Anti-Bot Shortlink Resolution Protocol**:
   - E-commerce platforms deploy anti-bot defenses that reject automated curl and headless scrapers on shortlinks (`s.shopee.co.id/...`). Never execute repetitive automated scraping loops.
   - Fast Resolution: Either request a simple user mapping (`link_slug -> product name & price`) or slot affiliate links into logical equipment tiers based on the outline.
4. **Duplicate Affiliate Link Allocation & 100% Utilization Strategy**:
   - When user provides batches with duplicate shortlinks, allocate unique product links to visual cards and distribute duplicates to contextual in-text editorial CTAs across the article body so no link is dropped.
5. **Post-Publication Affiliate Link Fidelity & Verification Audit Protocol**:
   - Immediately after compilation and deployment, assert: zero dropped user links, zero foreign links, and 100% `rel="sponsored nofollow"` compliance. Include the four-pillar audit table in the delivery report.

---

### Step 5: Triple Schema.org Markup Protocol
Embed structured JSON-LD in `<head>`:
1. **`NewsArticle`**:
   Include `headline`, `image`, `datePublished`, `dateModified`, `author` (e.g. editorial desk), and `publisher` (organization name and logo).
2. **`BreadcrumbList`**:
   Map hierarchy accurately (`Beranda` &rarr; `[Category]` &rarr; `[Article Title]`).
3. **`FAQPage`**:
   Provide 3–5 common questions addressing the real-world implications of the news event.

---

### Step 6: Commercial Event SEO & Time-Sensitive Indexing Architecture
When authoring content for commercial and entertainment events with tight date windows (airline travel fairs, music festivals, flash promotions, bank card festival discounts, auto expos):
1. **Source Ingestion & Poster Extraction**:
   - Extract operational dates, physical venues (mall halls/floors, convention grounds), organizers, ticketing partners, and lineup/artists.
   - When event details originate from social media (Instagram), use `yt-dlp --dump-json` or Open Graph parsers to extract raw CDN image links without loading full auth-walled desktop browsers.
   - For vertical posters, embed inside dark ambient containers (`#0b0f19` / `#111927`) with `object-position: top center` so festival typography remains crisp and unclipped.
2. **Contextual Destination Hero Asset Caching**:
   - Never use generic fallback images for event guides. Cache high-resolution landscape photography of the core destination (Tokyo, Singapore) or venue layout locally under `assets/img/` in WebP format (<300 KB).
   - Inspect visual pixels to verify true geographic landmarks before writing captions (e.g. Shinjuku skyline vs Tokyo Tower).
3. **Tiered Pricing & Multi-Day Lineup Architecture**:
   - For commercial/travel fairs: lowest round-trip fares across routes, tiered cashback thresholds, and 0% installment terms.
   - For festivals/concerts: daily lineup breakdown (Day 1, Day 2, Day 3), curated stage identities, and ticket tier breakdowns.
4. **`Event` / `MusicEvent` Schema Integration**:
   Combine `@type: "Event"` (or `"MusicEvent"`) with `startDate`, `endDate`, `location` (Place, PostalAddress), `organizer`, and `offers` alongside `FAQPage` and `Article` to secure Google Event carousels and rich snippets.
5. **Urgent Indexing Dispatch**:
   Because events last only 3–5 days, organic crawling is too slow. Push new event URLs immediately via Google Indexing API upon deployment.

---

### Step 7: Automated End-to-End Publishing & Synchronization Pipeline
Whenever requested to create or publish a post, execute the automated 7-in-1 publishing pipeline:
1. **Compile Single-Post HTML**: Generate `<slug>.html` with canonical template, optimized WebP visual, photo credit token, and Schema.org markup.
2. **Generator & Static Template Invariant**: When modifying sitewide boilerplate (footers, headers), update the canonical generator engine (`builder_hotmagazine.py` via `get_canonical_footer()`) simultaneously with existing static pages.
3. **Auto-Inject into Homepage (`index.html`)**:
   - **Hero News Grid**: Prepend story to Slot 1 with featured image, headline, category badge.
   - **Grid Parity Invariant**: Keep total card count strictly pinned to an exact common multiple (e.g., exactly 8 cards) in 4-col/2-col grids. Pop the oldest card so the count never becomes odd (preventing orphan cards and blank slots).
   - **HTML Comment Boundary Integrity**: Validate all HTML comments (`<!-- ... -->`) are properly closed to prevent swallowed downstream markup.
   - **Breaking News Ticker & Dynamic Speed**: Dynamically scale CSS `animation-duration` based on item count (~15–20s per headline, velocity <= 40–50px/sec).
   - **Main Article Feed & Sidebar**: Prepend card to Slot 1 of main grid and top position of trending widget.
4. **Auto-Inject into Blog Archive (`blog.html`)**: Prepend article card with category filter tags.
5. **Auto-Update `sitemap.xml`**: Insert `<url>` entry with today's `<lastmod>` and priority `0.8`.
6. **Auto-Deploy to Production Hosting**: Concurrently upload all WebP images, new HTML, `index.html`, `blog.html`, and `sitemap.xml` to cPanel `public_html/`.
7. **Auto-Push to Google Indexing API**: Submit `URL_UPDATED` for the new article URL, `blog.html`, and `index.html`. Verify and report output (`N submitted, 0 failed`).
8. **Responsive Quality Gate & Playwright Targeted Scroll QA**:
   - Confirm zero horizontal overflow across 1280px, 768px, and 390px viewports.
   - Wrap `page.goto()` in a 3-attempt retry loop with 45s timeout.
   - Offset scroll (e.g. `window.scrollBy(0, -200)`) before snapping QA screenshots to prevent sticky headers from obscuring top badges.
9. **OpenGraph Banner Optimization & Telegram Cache-Busting**:
   - Featured `og:image` must be 1200x630 pixels with explicit width/height meta tags. Append query version parameter (`?v=timestamp`) when sharing in Telegram chat to bust server-side thumbnail cache.

---

## 3. Pitfalls & Anti-Patterns

- **Duplicate Versioned Skills**: Creating `editorial-news-publishing-v2` alongside `editorial-news-publishing` fragments maintenance. Keep all editorial publishing, unit economics, affiliate formatting, and event SEO rules unified under the canonical class-level skill.
- **Generic Fallback Imagery on Event Guides**: Using site logos or fallback graphics instead of destination or venue photography destroys visual relevance for high-intent queries.
- **Relying Solely on Organic Sitemap Crawls for Time-Sensitive Events**: Standard sitemap crawling takes days. For 3–5 day events, always push immediately via Google Indexing API.
- **Unconstrained Lineup Poster Aspect Ratios**: Music festival lineup posters have dense typography. Center-cropping cuts off headliners. Place vertical posters in dark-framed containers with `object-position: top center`.
- **Odd-Number Hero Grid Orphan Bug**: Prepending cards into a responsive 2-column / 4-column grid without maintaining even parity leaves an orphan card and empty blank slot. Always enforce exact multiples (e.g. 8 items).
- **Dangling HTML Comment Openers (`<!--`) Swallowing Sections**: Leaving an unclosed comment opener tag swallows downstream DOM elements, causing sections to vanish. Always validate comment pairs before pushing to production.
- **Unbuffered Element Screenshots Behind Sticky Navbars**: Calling `scroll_into_view_if_needed()` without compensating for fixed headers crops the top of elements behind the nav bar during automated QA. Always add an offset scroll before capturing viewport snapshots.
- **Discarding Duplicate Affiliate Links Provided by Users**: Silently dropping duplicate affiliate shortlinks wastes tracking links. Allocate unique links to visual cards and distribute duplicates to contextual in-text editorial CTAs.
- **Undersized Mobile Affiliate Tap Targets**: Using inline text-sized buttons on mobile product cards lowers conversion. Always enforce full-width, minimum height >= 38px, and bold contrasting CTA styling on mobile.
- **Naked Dofollow Affiliate Links**: Embedding affiliate links without `rel="sponsored nofollow"` violates Google Search Essentials and risks manual penalties.
- **Missing Editorial Affiliate Disclosure**: Publishing sponsored links without explicit disclosure breaches compliance standards and degrades search trust ratings.
- **Heavy Third-Party Widget Bloat**: Embedding heavy external tickers (e.g. TradingView) pulls >400 KB of scripts and blocks CPU. Build native lightweight pure CSS/HTML tickers (~2 KB) instead.
- **Verbose Narrative Captions**: Keep captions strictly to standard media credit tokens (e.g. `ANTARA FOTO`, `ANTARA`, `Reuters`). Use requested tokens verbatim.
- **Single-Source Dependency on Social Media**: Validate transaction details, filings, and figures against official wires and exchange disclosure reports before publishing.
- **Heavy Uncompressed Featured Images**: Raw multi-megabyte images damage Core Web Vitals (LCP > 2.5s). Always convert to optimized WebP (<65 KB).
- **Missing Viewport Containment on Tables**: Tables lacking `<div class="table-responsive">` blow out mobile screen widths and cause mobile usability errors.
