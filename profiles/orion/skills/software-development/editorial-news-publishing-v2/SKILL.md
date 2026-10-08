---
name: editorial-news-publishing-v2
description: Use when publishing news stories or editorial articles.
version: 1.4.0
author: Orion Fleet Lead
license: MIT
metadata:
  hermes:
    tags: [editorial, news-publishing, journalism, news-paraphrase, photo-attribution, geo, ai-overview, schema-newsarticle, google-indexing-api, auto-publisher, grid-parity, mobile-antara-feed, dual-image-editorial, canonical-footer-sync, sitewide-boilerplate-lock]
    category: software-development
---

# Editorial News Publishing & Content Optimization Architecture

A class-level procedural skill for authoring, paraphrasing, structuring, and deploying high-CTR, high-authority news articles and editorial analyses for digital media portals. Governs journalistic wire rewrites, clean photo attribution credits, Generative Engine Optimization (GEO) answer boxes, contextual conversion callouts, automated multi-surface homepage synchronization, adaptive mobile newsfeed styling (ANTARA News pattern), and rapid search engine indexing.

---

## 1. When to Use

Use this skill when:
1. Converting official press releases or wire service reports (e.g. Antara News, Bloomberg, Reuters, regulatory agencies) into comprehensive editorial articles.
2. Paraphrasing factual news stories while enhancing topical depth with real-sector impact analysis and macroeconomic implications.
3. Formatting featured news imagery and photo captions according to professional journalistic standards.
4. Implementing Generative Engine Optimization (GEO) direct-answer boxes (BLUF) and HTML comparison tables for Google AI Overviews.
5. Embedding contextual, high-converting native utility callouts (calculators, verification tools) without degrading editorial integrity.
6. Deploying news stories via the automated publishing pipeline to ensure instant, synchronized presence across the homepage (`index.html`), archive (`blog.html`), sitemap, cPanel hosting, and Google Indexing API.
7. Implementing or maintaining mobile-first news layouts (e.g. ANTARA News style headline + vertical list feed) while preserving multi-column desktop parity.

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
     - **Opening Featured Image**: Crop to standard 16:9 landscape aspect ratio (800x450), tightly framed on the key subject for above-the-fold hero impact. Convert to WebP (quality 80–85, under 40 KB) to ensure sub-100ms Largest Contentful Paint (LCP).
     - **In-Body Contextual Image**: Use an uncropped or documentary 3:2 aspect ratio (800x533) that reveals full contextual details (e.g., contract papers on desk, pens, badges, background signage). Convert to WebP (under 40 KB).
2. **Photo Caption Attribution Standard**:
   - The `<span class="image-caption">` element positioned beneath the featured image must strictly function as a concise source attribution or press agency credit (e.g., `ANTARA FOTO`, `ANTARA`, `Reuters`, `Foto: Stuart MacFarlane / Arsenal FC via The Times`), not a narrative paragraph summarizing the article.
   - When the user explicitly requests an attribution token (e.g., "di bawah foto tulisan ANTARA" or "jangan lupa buatkan foto ini dari sumber mana"), place that exact credit string inside `<span class="image-caption">[CREDIT]</span>` verbatim (e.g., `Foto: Instagram @[user] / Dok. [Brand] via [Source]` or `Foto: Stuart MacFarlane / Arsenal FC via The Times`), centered directly under the image, without prepending redundant narrative text.
   - For secondary/documentary body images within the article, wrap in `<figure class="my-4 text-center">` and include `<figcaption class="image-caption mt-2 text-muted fst-italic small text-center">` with the exact journalistic attribution and concise moment description (e.g., `Foto: Stuart MacFarlane / Arsenal FC via The Times (Momen Penandatanganan Kontrak Mikel Arteta)`). Every visual asset in the post must carry inspectable source credit.
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
3. **Structured HTML Comparison Tables**:
   - Present numerical comparisons (current period vs. prior period vs. global benchmark) in clean, semantic HTML tables wrapped in `<div class="table-responsive">` to prevent mobile horizontal blowouts.

---

### Step 4: Contextual Native Utility CTAs
- Avoid intrusive popups or unrelated affiliate spam in serious financial or news reporting.
- Embed contextual native callout cards matching user search intent:
  - **Financial Utility**: Simulation calculator or regulatory license checker for business capital.
  - **Risk Mitigation**: Emergency fund checklist or micro-insurance protection guide.

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

### Step 6: Automated End-to-End Publishing & Synchronization Pipeline
Whenever requested to create or publish a blog post, execute the **automated 7-in-1 publishing pipeline** (e.g., via `publisher_engine.py`) so the story immediately reflects across all surfaces in one atomic action:
1. **Compile Single-Post HTML**: Generate `<slug>.html` with the canonical template, optimized WebP visual, exact photo credit token, and Schema.org markup.
2. **Generator & Static Template Invariant**: When modifying sitewide boilerplate (footers, headers, navigations), update the canonical generator engine (`builder_hotmagazine.py` via `get_canonical_footer()`) simultaneously with existing static pages so future articles generated by `publisher_engine.py` never regress to deprecated boilerplate.
3. **Auto-Inject into Homepage (`index.html`)**:
   - **Hero News Grid**: Prepend the story to Slot 1 with featured image, headline, and category badge.
   - **Grid Parity & Item Capping Invariant**: Multi-column responsive containers (e.g. 4 columns on desktop, 2 columns on tablet/wide-mobile) must never hold an odd or non-conforming number of items. In a 4-col/2-col grid, keep the total card count strictly pinned to an exact common multiple (e.g., exactly 8 cards). When auto-injecting a new article, pop the oldest card so the count never becomes odd (e.g. 7 items), which leaves an orphaned card on the left and a large blank/empty space on the right in 2-column view.
   - **HTML DOM & Comment Boundary Integrity**: Always sanitize and validate that all HTML comments (`<!-- ... -->`) are properly closed. A dangling `<!--` tag immediately swallows subsequent section wrappers, headings, and upper cards, causing background bleeding and visual collapse across theme transitions.
   - **Breaking News Ticker**: Insert timestamped headline in the marquee ticker.
   - **Main Article Feed (`Semua Berita Terkini`)**: Prepend card to Slot 1 of the primary grid.
   - **Sidebar Trending Widget (`Artikel Terpopuler`)**: Prepend to top positions.
4. **Auto-Inject into Blog Archive (`blog.html`)**: Prepend the article card to `#articles-grid` with category metadata filter tags.
5. **Auto-Update `sitemap.xml`**: Insert `<url>` entry with today's `<lastmod>` and priority `0.8`.
6. **Auto-Update Indexing Monitor**: Register the URL in the automated indexing script (`gsc_indexing.py`).
7. **Auto-Deploy to Production Hosting**: Concurrently upload the WebP image, new article HTML, `index.html`, `blog.html`, and `sitemap.xml` to cPanel `public_html/`.
8. **Auto-Push to Google Indexing API**: Submit `URL_UPDATED` for the new article URL, `blog.html`, and `index.html`.
9. **Responsive Quality Gate**: Verify that `index.html` maintains zero horizontal scroll/overflow and zero orphan grid slots across desktop (1280px), tablet (768px), and mobile viewports (360px, 390px) following the injection.

---

## 3. Pitfalls & Anti-Patterns

- **Third-Party Heavy Widget Bloat (e.g. TradingView, External Tickers)**: Embedding heavy third-party market widgets (such as TradingView Ticker Tape) triggers 50+ background network requests, pulls >400 KB of chained script chunks, and blocks the CPU main thread running sparkline animations. Crucially, hiding the container with `display: none` on mobile does NOT stop the mobile browser from downloading all JS bundles. On mobile news layouts, top widgets push breaking news and lead headlines below the fold, breaking the ANTARA News pattern. If market data or tickers are required, build a native, lightweight pure CSS/HTML ticker (~2 KB) without third-party dependencies.
- **Generator-Template Drift on Sitewide Boilerplate Changes**: Updating static HTML pages for sitewide elements (e.g., footer copyright line, navigation menus) without updating the article generator/builder template (`builder_hotmagazine.py` via `get_canonical_footer()`) causes future runs of the automated publisher to reintroduce deprecated boilerplate on newly created articles. Always update generator templates in lockstep with static files.
- **Sequential cPanel Deploy Timeouts on Sitewide Sweeps**: Uploading 35+ HTML files sequentially via UAPI/proxy takes ~2–3 seconds per file (~80–120s total) and will exceed default 60s execution timeouts. When performing sitewide deploys, always allocate >= 240s timeout or deploy in prioritized batches.

- **Playwright `networkidle` Timeout on Live News Portals**: Using `page.goto(url, wait_until='networkidle')` during post-deployment audits frequently causes 60s execution timeouts because persistent ad beacons, font CDNs, or real-time analytics retain open sockets. Always navigate with `wait_until='domcontentloaded'` and rely on explicit selector checks (`wait_for_selector`) or small fixed delays.
- **Assumed Selector Fragility in Verification Scripts**: Querying rigid assumed class names (e.g. `.category-badge` instead of template-native `a.category-post`) in post-publish audit scripts triggers Playwright locator timeouts. Use union selectors (e.g. `.category-post, .category-badge`) or inspect live DOM class names before running automated audits.
- **Odd-Number Hero Grid Orphan Bug**: Prepending cards into a responsive 2-column / 4-column grid without maintaining even parity results in an orphan card on the left and an empty blank slot on the right on tablet and wide-mobile screens. Always maintain an exact common multiple (e.g., exactly 8 items) in automated publisher scripts.
- **Dangling HTML Comment Openers (`<!--`) Swallowing Sections**: Leaving an unclosed comment opener tag when cleaning legacy markup swallows downstream DOM elements, causing section containers, headers, and upper cards to vanish and bleeding adjacent container background colors. Always validate comment pairs before pushing to production.
- **Decoupled Single-Post Creation**: Generating `<slug>.html` or updating only `blog.html` without immediately updating `index.html` leaves the homepage stale and gives readers the false impression that the article was not published. Treat article creation and homepage synchronization as a single atomic automated pipeline.
- **Ticker-Only Homepage Updates**: Updating only the marquee ticker without rotating new articles into the homepage's prominent hero grid and latest-news cards leaves primary visual slots occupied by older content. Always synchronize breaking stories across the hero grid, main feed, and popular widget on `index.html`.
- **Neglecting Mobile Layout Audit After Card Rotation**: Inserting new headlines or swapping hero cards in `index.html` without verifying mobile viewport width can introduce text overflow or image misalignment. Always run a headless browser check (e.g., Playwright at 360px and 390px) to confirm zero horizontal overflow before pushing to production.
- **Verbose Narrative Captions**: Writing multi-sentence article summaries inside `<span class="image-caption">` clutters above-the-fold space and duplicates lead content. Keep captions strictly to standard media credit tokens (e.g. `ANTARA FOTO`, `ANTARA`, `Reuters`).
- **Ignoring Explicit Caption Instructions**: When the user specifies an exact caption label (e.g. "ANTARA"), do not overwrite it with generic or narrative captions. Use the requested token verbatim.
- **Single-Source Dependency on Social Media**: Relying solely on Instagram or social media snippets without validating CSPA terms, stock volumes, or company filings leads to inaccurate financial figures. Always cross-reference with official news wires and exchange disclosure reports.
- **Shallow Wire Rewrites**: Merely swapping synonyms without adding analytical depth leaves content vulnerable to search engine thin content penalties. Always contextualize raw wire statistics with downstream industry effects and consumer takeaways.
- **Heavy Uncompressed Featured Images**: Using raw multi-megabyte JPEG/PNG images from source wires severely damages Core Web Vitals (LCP > 2.5s). Always convert to optimized WebP (<50 KB).
- **Missing Viewport Containment on Tables**: Tables comparing economic metrics that lack `<div class="table-responsive">` blow out mobile screen widths and cause mobile usability errors.
- **Neglecting Rapid Indexing on Breaking News**: Waiting for search engines to crawl sitemaps organically causes timely news articles to miss peak search traffic windows. Always push directly to Google Indexing API upon deployment.
- **Inconsistent Taxonomy Across Nav & Breadcrumbs**: Using differing category names between navbar menus and article breadcrumbs confuses readers and dilutes internal topic silo authority. Keep category naming strictly uniform.
