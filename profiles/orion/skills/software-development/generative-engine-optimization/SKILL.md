---
name: generative-engine-optimization
description: Use when optimizing web pages for Google AI Overviews and diagnosing web performance/indexing blockers.
version: 1.1.0
author: Orion Fleet Lead
license: MIT
metadata:
  hermes:
    tags: [seo, geo, ai-overview, sge, json-ld, schema, web-publishing, pagespeed, web-performance]
    category: software-development
---

# Generative Engine Optimization (GEO) & Web Publishing Strategy

## When to Use

Use this skill when:
1. Designing, writing, or optimizing web pages to appear in **Google AI Overviews (SGE)**, Perplexity citations, and AI search summaries.
2. Auditing website HTML structure, JSON-LD Schema markup, and OpenGraph/canonical metadata for search engines.
3. Troubleshooting static web hosting and subdomain deployment issues (such as 403 Forbidden from missing `index.html` or document root mismatches).
5. Designing or converting legacy corporate/B2B websites (e.g. shipping, logistics, manufacturing) into modern, high-speed Bootstrap 5.3 + semantic SEO landing pages.

---

## 0. Linked Reference Materials
- [Enterprise Corporate & B2B Web Redesign Guide](references/enterprise-corporate-redesign.md): Patterns for full corporate redesigns, schema architecture, and clean bundle packaging.

## 1. Core Mechanics of Google AI Overview (GEO)

AI search engines (Google AI Overview, Perplexity, Bing Copilot) extract information from authoritative, highly structured, and direct-answering pages.

### A. Bottom Line Up Front (BLUF) / Direct Answer Box
* Place a clear, direct answer in the first 100–150 words of the page.
* Avoid filler opening sentences ("In this modern era...", "Choosing a vendor can be hard...").
* Center the outer container symmetrically in the hero/content section (`margin: 25px auto 0 auto; max-width: 780px; width: 100%;`) while keeping internal bullet points left-aligned for high readability.
* Use an explicit answer container:
  ```html
  <div class="geo-quick-summary">
    <p>📍 <strong>Informasi Cepat:</strong><br>
    • <strong>Alamat:</strong> Jl. Contoh No.2A, Jakarta Selatan 12330.<br>
    • <strong>Tarif:</strong> Mulai <strong>Rp 50.000</strong>.<br>
    • <strong>Jam Buka:</strong> Setiap Hari <strong>09.00 – 21.00 WIB</strong>.<br>
    • <strong>Kontak:</strong> WhatsApp <strong>0812-xxxx-xxxx</strong>.</p>
  </div>
  ```

### B. Native HTML Tables for Specifications & Pricing
AI scrapers prioritize HTML `<table>` and semantic `<ul>`/`<ol>` elements when generating structured comparison widgets and price cards:
* Always use `<table>`, `<thead>`, `<th>`, `<tbody>`, and `<td>`.
* Include distinct columns: `Item / Variant`, `Price Range / MOQ`, `Specifications / Material`, `Ideal Use Case`.

### C. Question-Based Heading Hierarchy
* Frame `<h2>` and `<h3>` tags as exact natural language queries matching search intent:
  - `<h2>Berapa Harga Pin Custom?</h2>`
  - `<h2>Perbandingan Bahan: Soft Enamel vs Hard Enamel</h2>`
  - `<h2>Berapa Lama Waktu Pengerjaan?</h2>`

---

## 2. Structured Data (JSON-LD Schema) Protocol

Structured data provides machine-readable context directly to LLM crawlers and search bots.

### Mandatory Schemas:
1. **`Article` or `BlogPosting`**:
   ```json
   {
     "@context": "https://schema.org",
     "@type": "Article",
     "headline": "Judul Artikel yang Spesifik dan Menjawab Masalah",
     "description": "Ringkasan padat isi artikel",
     "author": { "@type": "Organization", "name": "Brand" },
     "publisher": { "@type": "Organization", "name": "Brand" },
     "datePublished": "2026-08-16",
     "dateModified": "2026-08-16",
     "mainEntityOfPage": "https://blog.example.com/"
   }
   ```
2. **`FAQPage`**:
   Ensure all FAQ items displayed visually on the page are mirrored 1:1 inside the JSON-LD `FAQPage` schema.
3. **`LocalBusiness` / `Product` / `AggregateOffer`**:
   Include `priceRange`, `lowPrice`, `highPrice`, and `priceCurrency: "IDR"`.

---

## 3. Metadata Consistency & Common Pitfalls

- **Canonical URL Match**: The `<link rel="canonical" href="..." />` MUST match the live domain and subdomain exactly. Pointing canonicals to staging domains or temporary subdomains (e.g. `card.example.com` instead of `blog.example.com`) prevents search engines from indexing the page.
- **OpenGraph Synchronization**: Ensure `og:url`, `og:title`, `og:description`, and `og:image` match the canonical metadata.
- **Breadcrumb Link Integrity**: Ensure breadcrumb hyperlinks in the HTML body do not contain stale/staging URLs.

---

## 4. Subdomain & Static Hosting Troubleshooting

When a newly deployed subdomain or static site returns **HTTP 403 Forbidden**:
1. **Default Index File**: Ensure the entry point file is strictly named `index.html` or `index.php` (all lowercase). Files named `blog.html`, `home.html`, or `Index.html` result in a 403 error because web servers disable directory listing by default.
2. **Document Root Folder**: Verify the subdomain in the hosting panel points to the exact folder containing the index file (e.g. `public_html/blog/`).
3. **File Permissions**: Folders must be `755` (`drwxr-xr-x`) and files `644` (`-rw-r--r--`).
4. **`.htaccess` Overrides**: Check for restrictive rewrite rules or IP blocklists in the subdomain folder.

---

## 5. Web Performance & PageSpeed Diagnostic Audit

When mobile performance audits (Lighthouse / PageSpeed Insights) show poor scores:
1. **Duplicate HTML Payload Inspection**:
   - Check if the HTML template accidentally duplicated content (e.g. double `<!DOCTYPE html>` or doubled line counts from accidental copy-paste).
   - Probe with: `curl -s -L <url> | grep -n "<!DOCTYPE"` to detect duplicate root elements.
2. **Image Delivery & Rendering**:
   - Add `loading="lazy" decoding="async"` to all below-the-fold images.
   - Set `fetchpriority="high"` on hero/LCP images (e.g. intro carousels or main banners).
   - Prefer modern web formats (`.webp`, `.avif`) over heavy legacy PNG/JPEG files.
3. **Script Execution Strategy & Third-Party Widgets**:
   - Add `defer` to non-critical external JavaScript files in the document body.
   - **Smart Lazy Loader for Analytics & Chat Widgets (0ms TBT)**: Load heavy third-party scripts (Crisp Chat, GTAG, Meta Pixel) dynamically only after the first user interaction (`scroll`, `touchstart`, `mousemove`, `click`, `keydown`) with a fallback `setTimeout` (4s):
     ```javascript
     function initThirdParty() {
       if (window._tp_loaded) return;
       window._tp_loaded = true;
       // inject GTAG / Crisp script elements into document.head
     }
     ["scroll", "mousemove", "touchstart", "click", "keydown"].forEach(e => {
       window.addEventListener(e, initThirdParty, { once: true, passive: true });
     });
     setTimeout(initThirdParty, 4000);
     ```
   - **Instagram Static Media Extraction via OEmbed / API**: Do not load hotlinked external CDN images directly from expired URLs. Use Instagram official OEmbed API (`https://www.instagram.com/api/v1/oembed/?url=...`) to safely pull media metadata and persist images locally (`./assets/images/...`) for permanent, high-speed static delivery without bot-wall blocks.
   - **YouTube Embed Facade Pattern (Save ~2.5 MB & 1.5s CPU per page)**: Native YouTube `<iframe>` elements download heavy player libraries, styles, and fonts on page load even when unplayed. Replace with a responsive thumbnail facade with a play button overlay, replacing the container with an `<iframe>` only on click.
   - Use `font-display: swap` in Google Fonts links (`&display=swap`) with `preconnect` tags (`fonts.googleapis.com` & `fonts.gstatic.com`) to eliminate Flash of Invisible Text (FOIT).
4. **Preservation of Analytics & Conversion Tracking**:
   - When optimizing static HTML bundles, strictly preserve all analytics and verification tags (Google Tag Manager, Google Analytics gtag IDs, Meta Pixel, Webmaster verification meta tags) and ensure dynamic properties (e.g. telephone numbers in schema) match live business contact details.
5. **Server Compression & Browser Caching (`.htaccess`)**:
   - Enable Gzip / Brotli compression (`mod_deflate`) for text, html, css, js, and svg.
   - Configure long-term browser caching (`mod_expires`) with `access plus 1 year` for static assets (images, icons) and `access plus 1 month` for CSS/JS.
