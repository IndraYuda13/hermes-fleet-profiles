---
name: editorial-news-publishing
description: Use when publishing news stories or editorial articles.
version: 1.0.0
author: Orion Fleet Lead
license: MIT
metadata:
  hermes:
    tags: [editorial, news-publishing, journalism, news-paraphrase, photo-attribution, geo, ai-overview, schema-newsarticle, google-indexing-api]
    category: software-development
---

# Editorial News Publishing & Content Optimization Architecture

A class-level procedural skill for authoring, paraphrasing, structuring, and deploying high-CTR, high-authority news articles and editorial analyses for digital media portals. Governs journalistic wire rewrites, clean photo attribution credits, Generative Engine Optimization (GEO) answer boxes, contextual conversion callouts, and rapid search engine indexing.

---

## 1. When to Use

Use this skill when:
1. Converting official press releases or wire service reports (e.g. Antara News, Bloomberg, Reuters, regulatory agencies) into comprehensive editorial articles.
2. Paraphrasing factual news stories while enhancing topical depth with real-sector impact analysis and macroeconomic implications.
3. Formatting featured news imagery and photo captions according to professional journalistic standards.
4. Implementing Generative Engine Optimization (GEO) direct-answer boxes (BLUF) and HTML comparison tables for Google AI Overviews.
5. Embedding contextual, high-converting native utility callouts (calculators, verification tools) without degrading editorial integrity.
6. Deploying news stories to production hosting, updating internal discovery loops (blog grids, breaking news tickers, sitemaps), and pushing to the Google Indexing API.

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

---

### Step 2: Featured Image Optimization & Caption Attribution
1. **Asset Optimization**:
   - Download the primary news photo or editorial stock asset.
   - Convert to optimized WebP format (typically 800x450 or 1200x630 aspect ratio, quality 80–85, under 50 KB) to ensure sub-100ms Largest Contentful Paint (LCP).
2. **Photo Caption Attribution Standard**:
   - The `<span class="image-caption">` element positioned beneath the featured image must strictly function as a concise source attribution or press agency credit (e.g., `ANTARA FOTO`, `ANTARA`, `Reuters`, `AFP`), not a narrative paragraph summarizing the article.
   - When the user explicitly requests an attribution token (e.g., "di bawah foto tulisan ANTARA" or "ANTARA FOTO"), place that exact credit string inside `<span class="image-caption">[CREDIT]</span>` verbatim, centered directly under the image, without prepending redundant narrative text.
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

### Step 6: Production Deployment & Rapid Indexing Pipeline
1. **Deploy Static Assets**:
   - Upload modified HTML and WebP image files to production hosting (e.g. cPanel `public_html/`).
2. **Update Internal Discovery Channels & Full Homepage Synchronization**:
   - Register the new URL in `sitemap.xml` with current `lastmod` and priority `0.8`–`0.9`.
   - Add the story to the portal's blog archive (`blog.html`) grid cards with the appropriate category badge.
   - **Full Homepage (`index.html`) Content Synchronization**:
     - **Hero News Grid / Headline Slots**: Rotate the newest breaking articles into the top hero grid (Slot 1 and Slot 2) with featured WebP imagery and clear category badges, replacing older featured items.
     - **Semua Berita Terkini / Main Articles Grid**: Prepend the new articles to the top of the general article feed on `index.html`.
     - **Sidebar Trending / Widget Artikel Terpopuler**: Insert high-impact market stories into the #1 and #2 spots of the trending widget.
     - **Breaking News Ticker**: Add a timestamped headline item (e.g., `14:30 WIB Aksi Korporasi Saham BYAN...`).
   - Run a responsive headless audit (e.g., Playwright at 360px and 390px mobile viewports) on `index.html` to guarantee zero horizontal scroll/overflow after card rotation.
3. **Programmatic Google Indexing API Push**:
   - Submit a `URL_UPDATED` notification for the new article, updated blog page, and homepage via the Google Indexing API service account to initiate rapid crawling.

---

## 3. Pitfalls & Anti-Patterns

- **Ticker-Only Homepage Updates**: Updating only the marquee ticker or `blog.html` without rotating new articles into the homepage's prominent hero grid and latest-news cards leaves readers and stakeholders seeing a stale homepage where fresh stories appear invisible. Always synchronize breaking and high-impact stories across the hero grid, main feed, and popular widget on `index.html`.
- **Neglecting Mobile Layout Audit After Card Rotation**: Inserting new headlines or swapping hero cards in `index.html` without verifying mobile viewport width can introduce text overflow or image misalignment. Always run a headless browser check (e.g., Playwright at 360px and 390px) to confirm zero horizontal overflow before pushing to production.
- **Verbose Narrative Captions**: Writing multi-sentence article summaries inside `<span class="image-caption">` clutters above-the-fold space and duplicates lead content. Keep captions strictly to standard media credit tokens (e.g. `ANTARA FOTO`, `ANTARA`, `Reuters`).
- **Ignoring Explicit Caption Instructions**: When the user specifies an exact caption label (e.g. "ANTARA"), do not overwrite it with generic or narrative captions. Use the requested token verbatim.
- **Single-Source Dependency on Social Media**: Relying solely on Instagram or social media snippets without validating CSPA terms, stock volumes, or company filings leads to inaccurate financial figures. Always cross-reference with official news wires and exchange disclosure reports.
- **Shallow Wire Rewrites**: Merely swapping synonyms without adding analytical depth leaves content vulnerable to search engine thin content penalties. Always contextualize raw wire statistics with downstream industry effects and consumer takeaways.
- **Heavy Uncompressed Featured Images**: Using raw multi-megabyte JPEG/PNG images from source wires severely damages Core Web Vitals (LCP > 2.5s). Always convert to optimized WebP (<50 KB).
- **Missing Viewport Containment on Tables**: Tables comparing economic metrics that lack `<div class="table-responsive">` blow out mobile screen widths and cause mobile usability errors.
- **Neglecting Rapid Indexing on Breaking News**: Waiting for search engines to crawl sitemaps organically causes timely news articles to miss peak search traffic windows. Always push directly to Google Indexing API upon deployment.
- **Inconsistent Taxonomy Across Nav & Breadcrumbs**: Using differing category names between navbar menus and article breadcrumbs confuses readers and dilutes internal topic silo authority. Keep category naming strictly uniform.
