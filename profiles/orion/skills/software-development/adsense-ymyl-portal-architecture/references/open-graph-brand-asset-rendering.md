# OpenGraph Brand Card & Social Asset Rendering Architecture

Guidelines for authoring, rendering, and deploying high-craftsmanship OpenGraph (OG) identity cards (1200 × 630 px) for financial and news media portals.

---

## 1. Editorial Positioning & Brand Neutrality Protocol

When designing primary social identity assets (meta OG images, Twitter Cards, WhatsApp/Telegram share previews) for financial media portals:
- **Avoid Stigmatized Niche Associations**: Never frame the primary publication identity around high-friction or stigmatized keywords (e.g. avoid labeling the brand card as a "pinjol", "pinjaman online", or "kredit utang" site unless specifically instructed for a single sub-article).
- **Core Editorial Anchor**: Position the publication as an authoritative daily financial news and smart financial literacy portal (e.g., *"Portal Berita Finansial Harian & Literasi Keuangan Terpercaya"*).
- **Pillar Trust Badges**: Use broad, positive, and authoritative categorical trust badges:
  1. `✓ Berita Bisnis & Pasar` (Red/Coral accent)
  2. `✓ Edukasi Finansial Publik` (Sky Blue)
  3. `✓ Gaya Hidup & Mobilitas` (Emerald Green)

---

## 2. High-Fidelity Font Rendering via Headless Playwright

### Pitfall of Naive CLI Rasterizers
CLI rasterization tools such as `rsvg-convert` or Cairo render SVG text using local system fallback fonts (such as basic Arial or DejaVu Sans). Because they cannot fetch Google Fonts CDN stylesheets embedded in SVGs:
- Kerning and font weight (bold/semi-bold) look crude and misaligned.
- Text strings overflow rounded badges or appear off-center.
- The visual output resembles generic low-effort graphics.

### Playwright Headless Rendering Protocol
Always render the 1200 × 630 px PNG card through a lightweight HTML wrapper loaded in headless Chromium:

```python
import asyncio
from playwright.async_api import async_playwright

html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>
    body {{
      margin: 0; padding: 0;
      width: 1200px; height: 630px;
      overflow: hidden;
      background: #0a192f;
      font-family: 'Plus Jakarta Sans', sans-serif;
    }}
  </style>
</head>
<body>
{open(svg_path).read()}
</body>
</html>"""

async def render():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1200, "height": 630})
        await page.goto(f"file://{temp_html_path}")
        await page.wait_for_timeout(1000) # Allow Google Fonts to download and paint
        await page.screenshot(path=output_png_path, clip={"x": 0, "y": 0, "width": 1200, "height": 630})
        await browser.close()
```

---

## 3. Exact Vector Monogram Ingestion Protocol

When embedding the brand monogram or icon box into the 1200 × 630 px SVG card:
1. **Never Hand-Code Approximate Paths**: Do not attempt to hand-code bezier curves or synthetic SVG paths for brand initials (e.g. attempting to approximate "DF"). Minor coordinate errors can inadvertently transform glyphs into lookalike characters (e.g. an initial "DF" reading visually as "R" or "B").
2. **Canonical Vector Extraction**: Extract the exact `<path d="...">` coordinates from the verified brand SVG master (e.g., `test_vector.svg` or primary vector logo).
3. **Mathematical Scaling Matrix**:
   - If the canonical icon viewBox is $512 \times 512$ and the target card logo box is $100 \times 100$:
     - Scale factor is $100 / 512 = 0.1953125$.
     - Center the monogram within the enclosing `<rect>`:
       ```xml
       <g transform="translate(550, 85)">
         <rect width="100" height="100" rx="22" fill="#004aad"/>
         <g transform="scale(0.1953125)">
           <path d="M 112 96 L ... Z" fill="#ffffff" fill-rule="evenodd"/>
         </g>
       </g>
       ```

---

## 4. Social Platform Link Preview Caching & Cache Invalidation

### The Telegram & Social Platform Link Cache Trap
Social platforms (Telegram, WhatsApp, Twitter/X, Facebook, LinkedIn) scrape link metadata on the very first share event and cache the resulting preview card (title, description, and thumbnail image) **indefinitely** on edge CDN servers.
- When a website pivots, updates its brand name, or swaps its `og-image.png`, social apps continue displaying the stale cached card (e.g., displaying legacy keywords or retired graphics).
- Standard browser hard-refresh (`Ctrl+F5`) does not affect social platforms because their crawler proxies do not consult end-user browser state.

### Mitigation & Invalidation Protocol
1. **HTML Cache-Busting Versioning**:
   - Always append an explicit version or timestamp parameter to `og:image` and `twitter:image` tags in the HTML:
     ```html
     <meta property="og:image" content="https://dailyfinance.id/assets/img/og-image.png?v=20261008_02" />
     <meta name="twitter:image" content="https://dailyfinance.id/assets/img/og-image.png?v=20261008_02" />
     ```
   - Social scrapers treat query strings on media assets as unique URLs, forcing immediate bypass of their image CDN cache.
2. **Telegram Global Cache Invalidation via `@WebpageBot`**:
   - Telegram operates an official utility bot for webmasters: **`@WebpageBot`**.
   - Send the target URL (e.g., `https://dailyfinance.id/`) to `@WebpageBot`.
   - The bot triggers an immediate re-scrape across Telegram's crawler cluster and purges the cached preview globally across all chat clients.
3. **Ad-Hoc Ephemeral Parameter Sharing**:
   - For immediate user verification in chat before global caches purge, share the link with an ephemeral query string: `https://domain.com/?v=2` or `https://domain.com/?refresh=1`. This bypasses Telegram's URL-level hash key instantly.
4. **Sitewide Metadata Keyword Sweep**:
   - When updating primary brand identity, perform a regex audit across all secondary static pages (`blog.html`, `kontak.html`, `pasang-iklan.html`):
     - Replace legacy niche keywords in `<meta name="keywords">` and `<meta name="description">`.
     - Harmonize `og:title`, `og:description`, and `twitter:description` across all landing templates.

---

## 5. Dual-Format Synchronized Deployment

1. **Keep SVG and PNG in Strict Lockstep**:
   Whenever the text, headline, or badge in `assets/img/og-image.svg` is modified, immediately re-render `assets/img/og-image.png`.
2. **Deploy Both Files to Production cPanel**:
   Upload both the vector `.svg` (for crisp display on high-DPI landing pages) and raster `.png` (for social media scrapers: WhatsApp, Telegram, Twitter, Facebook) to `public_html/assets/img/`.
3. **Verify HTTP Responses**:
   Execute `curl -sIL https://<domain>/assets/img/og-image.png?v=...` to confirm HTTP 200, Content-Type `image/png`, and cache-control headers.
4. **Immediate Stakeholder Verification via Telegram Media**:
   Deliver the rendered PNG directly to the chat using `MEDIA:<absolute_path_to_png>` so the user can verify text alignment, visual balance, and colors directly on mobile and desktop without opening external browsers.
