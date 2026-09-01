---
name: web-performance-and-geo-optimization
description: Use when optimizing web speed or Google AI Overview (GEO).
---

# Web Performance & GEO (Generative Engine Optimization)

A class-level guide for achieving high mobile Lighthouse/PageSpeed scores (Core Web Vitals) and structuring web pages for citation in Google AI Overviews and answer engines.

---

## 1. Core Web Vitals & Mobile PageSpeed Optimization

### A. Third-Party Script Optimization (Eliminating TBT - Total Blocking Time)
Heavy third-party widgets (Live Chats like Crisp/Tawk.to, Google Analytics GTAG, Meta Pixel) block the browser main thread during initial load.

**Pattern: Smart Interaction-Driven Loading**
Load third-party analytics and chat widgets on the first user interaction (`scroll`, `touchstart`, `mousemove`, `click`) or after a passive 4-second timeout:
```html
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}

  function initThirdParty() {
    if (window._tp_loaded) return;
    window._tp_loaded = true;

    // 1. Google Analytics
    var g = document.createElement("script");
    g.src = "https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX";
    g.async = true;
    document.head.appendChild(g);
    gtag("js", new Date());
    gtag("config", "G-XXXXXXXXXX");

    // 2. Chat Widget (e.g. Crisp)
    var c = document.createElement("script");
    c.src = "https://client.crisp.chat/l.js";
    c.async = true;
    document.head.appendChild(c);
  }

  var events = ["scroll", "mousemove", "touchstart", "click", "keydown"];
  events.forEach(function(e) {
    window.addEventListener(e, initThirdParty, { once: true, passive: true });
  });
  setTimeout(initThirdParty, 4000);
</script>
```

---

### B. YouTube Embed Facade (Huge LCP & Bandwidth Savings)
Embedding native YouTube `<iframe>` elements downloads ~800KB-1.5MB of JS, CSS, and fonts per video immediately, causing severe TBT and mobile slowdown.

**Pattern: Responsive Facade with On-Demand Iframe Injection**
```html
<!-- Facade Container -->
<div class="yt-facade" data-id="VIDEO_ID" style="position: relative; width: 100%; padding-top: 56.25%; cursor: pointer; background: #000 url('https://i.ytimg.com/vi/VIDEO_ID/hqdefault.jpg') center/cover no-repeat;">
  <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 56px; height: 56px; background: rgba(255,0,0,0.9); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
    <div style="width: 0; height: 0; border-top: 10px solid transparent; border-bottom: 10px solid transparent; border-left: 18px solid #fff; margin-left: 4px;"></div>
  </div>
</div>

<script>
  document.querySelectorAll(".yt-facade").forEach(function(el) {
    el.addEventListener("click", function() {
      var id = this.getAttribute("data-id");
      var iframe = document.createElement("iframe");
      iframe.setAttribute("style", "position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;");
      iframe.setAttribute("src", "https://www.youtube.com/embed/" + id + "?autoplay=1&rel=0&playsinline=1");
      iframe.setAttribute("allow", "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share");
      iframe.setAttribute("allowfullscreen", "1");
      this.innerHTML = "";
      this.appendChild(iframe);
    });
  });
</script>
```

---

### C. Image Loading & Priority Hierarchy
1. **LCP Hero Image (Above the Fold):**
   * MUST have `fetchpriority="high"`.
   * Do NOT add `loading="lazy"` to the main hero/banner image.
2. **Below-the-Fold Images:**
   * MUST have `loading="lazy" decoding="async"`.
3. **Web Fonts:**
   * Always append `&display=swap` to Google Fonts URLs to prevent FOIT (Flash of Invisible Text).
   * Preconnect to `https://fonts.googleapis.com` and `https://fonts.gstatic.com`.

---

## 2. GEO (Generative Engine Optimization) for AI Overviews

Google AI Overviews (SGE) synthesize facts from pages that present clear, structured, and authoritative answers.

### A. The BLUF Answer Box (Bottom Line Up Front)
Place a highlighted summary answer in the first 100–150 words of the article right after the `<h1>` tag:
```html
<div class="key-answer" style="background: #f0faf3; border-left: 4px solid #22b14c; padding: 18px 22px; margin: 20px 0;">
  <p><strong>Harga pin custom mulai dari Rp25.000 per pcs</strong> dengan minimum order 25 pcs. Tersedia pilihan bahan soft/hard enamel, akrilik, logam kuningan, dan name tag magnet...</p>
</div>
```

### B. Clean Native HTML Tables for Fact Extraction
AI crawlers extract pricing and comparison grids cleanly from standard `<table>` markup:
```html
<table>
  <thead>
    <tr><th>Jenis Bahan</th><th>Minimum Order</th><th>Harga Mulai</th></tr>
  </thead>
  <tbody>
    <tr><td><strong>Pin Enamel</strong></td><td>25 pcs</td><td>Rp25.000/pcs</td></tr>
  </tbody>
</table>
```

### C. Structured Data Schema (JSON-LD)
Always include valid `Article` and `FAQPage` or `LocalBusiness` schemas.
Ensure `mainEntityOfPage`, `canonical`, and `og:url` match the exact live canonical URL.

---

## Pitfalls to Avoid
- **Duplicated HTML Body:** Accidental repeated markup during template paste doubles DOM size and crashes performance.
- **Canonical Mismatches:** Stale staging URLs (e.g., `card.domain.com` instead of `blog.domain.com`) prevent Google from indexing the page.
- **Unclosed Section Tags:** Malformed HTML prevents modern browser parser optimizations.
