# Google Search Central Appearance Technical Specifications

This reference provides exact technical thresholds, directives, and mechanics from Google Search Central documentation (`https://developers.google.com/search/docs/appearance`).

---

## 1. Title Links & Rewriting Mechanics

### Title Length & Truncation
- Desktop SERP container width: ~600px (typically 55–65 characters).
- Mobile SERP container width: dynamic, usually truncates earlier (~50–60 characters).
- Delimiter: use standard ASCII separators (` • `, ` - `, ` | `). Our standard is ` • DailyFinance.id`.

### Google Title Rewrite Triggers
Google replaces or alters `<title>` in SERP if:
1. **Half-Empty / Brand-Only**: `<title>DailyFinance.id</title>` on an article page.
2. **Keyword Stuffing**: repeating variants of the same keyword (`Bisnis Kopi, Jual Kopi, Usaha Kopi Rumahan`).
3. **Boilerplate / Template Drift**: generic repeated title across multiple pages.
4. **H1 vs Title Mismatch**: when `<title>` is completely different from the primary visible `<h1>`, Google often replaces the title with the `<h1>` or an anchor text from internal links.
5. **Language Mismatch**: English title on Indonesian body text.

---

## 2. Snippet Controls & Robots Directives

### Mandatory Directives for Rich Snippets & Discover
```html
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
```

### Directive Breakdown:
- `max-image-preview:large`:
  - **Function**: Tells Google that it is permitted to display full-width/large image previews in search results and Google Discover.
  - **Without this**: Google defaults to standard thumbnail sizes or excludes the page from card carousels in Discover.
- `max-snippet:-1`:
  - **Function**: Allows unlimited character count for text snippets.
  - **Crucial for**: Featured snippets (position zero) and full answer paragraphs in AI Overviews.
- `max-video-preview:-1`:
  - **Function**: Allows full video clip previews.
- `data-nosnippet`:
  - Use on specific HTML elements (`<span data-nosnippet>...</span>` or `<div data-nosnippet>`) to exclude sensitive disclaimers, affiliate disclosure boilerplate, or navigation text from appearing in SERP snippets.

---

## 3. Google AI Overviews & AI Mode Mechanics

### Official Indexing Criteria
- **No Proprietary AI Tags**: Google does not support or require `<meta name="google-ai">` or special AI markup.
- **Snippet Dependency**: Eligibility for AI Overviews depends directly on regular indexability and snippet eligibility. If a page uses `nosnippet` or a restrictive `max-snippet`, it is disqualified from AI Overviews.
- **Query Fan-Out**: Google decomposes a complex user query into sub-questions. An article answering the main query AND 3–4 natural adjacent queries (via FAQ and structured sections) captures multiple fan-out branches.

### Content Formatting for LLM Extraction:
- **Direct Answer (BLUF)**: First 100 words must state the explicit answer/data point.
- **Visible DOM Text**: Never hide critical definitions or answers in collapsed accordions that don't render content in the initial HTML DOM.
- **Comparison & Metric Tables**: Semantic `<table>` tags are parsed with high priority by Google's extraction models for structured entity extraction.

---

## 4. Google Discover Requirements

### Image Requirements (Hard Thresholds)
- **Minimum Width**: 1,200 pixels.
- **Minimum Total Pixels**: 300,000 pixels (e.g., 1200 x 250+ or 1200 x 675).
- **Aspect Ratio**: 16:9 widescreen preferred.
- **Directive**: `max-image-preview:large` must be enabled.
- **Content Policy**: Never use a site logo, stock icon, or generic placeholder graphic as the primary `og:image` / article hero.

### Content Criteria:
- Content must demonstrate genuine topical authority and narrative hook without misleading clickbait or hyperbole.
- High mobile usability: clean responsive layout, zero horizontal overflow at 390px viewport, fast Largest Contentful Paint (LCP).

---

## 5. Structured Data Protocol (JSON-LD)

### NewsArticle & Article Specifications
- **Author**: Must use `@type: "Person"` with a valid `name` and optional profile `url`. Multiple authors must be an array of separate Person objects. Do not include corporate titles in `name`.
- **Publisher**: Must reference `@type: "Organization"` with official `name` and `logo`.
- **Date Format**: ISO 8601 with explicit timezone offset (`2026-10-09T14:00:00+07:00`).
- **Image**: Array of URLs covering 16:9, 4:3, and 1:1 aspect ratios, or single high-res 16:9 URL (≥1200px).

### FAQPage Schema
- Every Question/Answer pair in JSON-LD must be 100% visible to human users in the HTML body. Mark up only questions that are answered directly on the page.

---

## 6. Publication Dates & Freshness

- **`datePublished`**: Static date when the article was first made public.
- **`dateModified`**: Only bump when there are substantive editorial changes, updated statistics, or new sections added.
- **Penalty Signal**: Bumping `dateModified` or displaying a fresh date in the visible byline without altering page content triggers freshness spam filters, causing Google to ignore bylines and extract dates from external signals.

---

## 7. Favicon Specifications & SERP Globe Fallback Mechanics

Google displays site favicons next to search results on mobile and desktop SERP. When Google cannot fetch, validate, or process the favicon, it falls back to a generic gray globe icon.

### Technical Requirements for Google SERP Favicon
1. **Supported File Formats (SVG is NOT Supported by Google Search SERP)**:
   - Google Search explicitly supports only: **ICO, PNG, GIF, BMP, JPEG, PPM, and TIFF**.
   - **Critical Pitfall**: Google Search does NOT support SVG for search results favicons! While desktop browsers support `<link rel="icon" type="image/svg+xml">`, Google Search crawler (`Googlebot-Image`) completely ignores SVG icons.
   - If a website only provides an SVG icon or pairs it with a non-standard PNG size (e.g. 32x32), Google Search discards both and permanently defaults to the gray globe icon.
2. **The 48px Multiple Square Rule (≥48px)**:
   - Google guidelines explicitly state: *"Your favicon must be a multiple of 48px square, for example: 48x48px, 96x96px, 144x144px, 192x192px and so on."*
   - A legacy 16×16 or 32×32 PNG icon does NOT satisfy the 48px multiple rule and is rejected by Google Search.
   - Always supply raster PNGs at: `48x48`, `96x96`, `144x144`, `192x192`, `256x256`, and `512x512` px.
3. **Multi-Resolution Root `favicon.ico`**:
   - Always compile root `/favicon.ico` with multi-resolution layers: `(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)` generated from a high-resolution 512px source PNG (`Pillow: im.save('favicon.ico', format='ICO', sizes=[...])`).
4. **Stable URL Contract (No Version Query Strings)**:
   - Google's favicon crawler (`Googlebot-Image` / favicon bot) requires a **stable, permanent URL**.
   - **Strict Anti-Pattern**: Never use version query strings like `<link rel="icon" href="/favicon.ico?v=20261009_02">` or `assets/img/favicon.png?v=...`. Query strings confuse Google's favicon indexing pipeline and cause cache invalidation failures, triggering fallback to the default globe icon.
   - Serve clean canonical paths: `/favicon.ico` (root) and `/assets/img/favicon-*.png`.
5. **Canonical HTML Markup for Google Search**:
   Declare in `<head>` across all pages (especially homepage):
   ```html
   <!-- Favicon & Icons (Google Search & Multi-device Compliant) -->
   <link rel="icon" type="image/x-icon" href="/favicon.ico">
   <link rel="shortcut icon" href="/favicon.ico">
   <link rel="icon" type="image/png" sizes="192x192" href="/assets/img/favicon-192.png">
   <link rel="icon" type="image/png" sizes="96x96" href="/assets/img/favicon-96.png">
   <link rel="icon" type="image/png" sizes="48x48" href="/assets/img/favicon-48.png">
   <link rel="icon" type="image/png" sizes="32x32" href="/assets/img/favicon-32.png">
   <link rel="apple-touch-icon" sizes="180x180" href="/assets/img/apple-touch-icon.png">
   <link rel="icon" type="image/svg+xml" href="/assets/img/favicon.svg">
   ```
6. **Homepage Discovery Dependency & Crawling Schedule**:
   - Google specifically extracts the site favicon definition from the **homepage** (`/`).
   - Neither the homepage nor the favicon image files may be blocked by `robots.txt`.
   - **Crawl Latency & Asynchronous Schedule**: Google's favicon crawler operates on a separate, much slower schedule than regular page indexing (typically taking 1 to 3–4 weeks for a newly indexed domain). When a domain is fresh, Google SERP displays the default globe icon until Googlebot-Favicons completes its background ingestion.
   - **Diagnostic Probe**: Check Google's internal favicon ingestion status:
     `curl -sI "https://www.google.com/s2/favicons?domain=dailyfinance.id&sz=64"`
     - HTTP 404 indicates Google has not yet crawled or processed the domain's favicon.
     - HTTP 200 confirms Google has successfully cached the favicon icon.
   - **Recrawl Trigger**: Because favicon ingestion depends on homepage crawling, after updating favicon files:
     1. Update `<lastmod>` of `https://dailyfinance.id/` in `sitemap.xml`.
     2. Push homepage to Google via Indexing API (`gsc_indexing.push_urls(["https://dailyfinance.id/"])`).
     3. Request manual indexing in Google Search Console URL Inspection for the homepage.
