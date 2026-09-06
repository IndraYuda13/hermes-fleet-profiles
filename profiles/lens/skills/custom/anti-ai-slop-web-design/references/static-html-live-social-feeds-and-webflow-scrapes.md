# Static HTML Live Social Feeds & Webflow Scraping Architecture

## 1. Webflow Static Extraction & IX2 Offline Invariants

When cloning or extracting Webflow templates into pure static HTML/CSS/JS:

### The IX2 Opacity:0 Trap
Webflow's Interaction 2.0 (IX2) engine applies initial inline styles such as `style="opacity: 0;"` or `transform: translate3d(0, 50px, 0)` to animated elements. When rendered offline or in headless environments where `webflow.js` does not execute all triggers immediately, the entire page body or hero section remains completely invisible (blank screen).

**Fix Pattern:**
1. Strip initial inline zero-opacity via regex:
   ```python
   content = re.sub(r'style="([^"]*?)opacity:\s*0;?([^"]*?)"', r'style="\1opacity: 1;\2"', content)
   content = re.sub(r'style="([^"]*?)transform:\s*translate3d\([^)]+\);?([^"]*?)"', r'style="\1\2"', content)
   ```
2. Inject a universal fallback visibility rule in `<head>`:
   ```html
   <style>
     [data-w-id], .w-dyn-item, .hero-wrapper, .section, .image-wrapper, .hero-content {
       opacity: 1 !important;
       transform: none !important;
       visibility: visible !important;
     }
   </style>
   ```
3. Parse CSS files to download internal `url(...)` fonts and background images locally.
4. Clean Webflow branding and hire popups:
   ```python
   content = re.sub(r'<a class="w-webflow-badge".*?</a>', '', content, flags=re.DOTALL)
   content = re.sub(r'<div class="hire-popup".*?</div>\s*</div>', '', content, flags=re.DOTALL)
   ```

---

## 2. Pure Static HTML Live Instagram Feed Integration

When integrating live social media feeds (e.g. Instagram `@username`) into a pure static HTML website without a CMS or backend server:

### The Constraints
- **Meta CDN Expiration:** Direct image URLs from Instagram's CDN expire within 24–48 hours.
- **CORS / Login Walls:** Direct client-side `fetch()` requests to `instagram.com` are blocked by CORS and anti-bot systems.

### Recommended Architecture: The Hybrid Resilient Feed
1. **Pre-rendered HTML Markup:**
   Always include a curated, pre-rendered 4–8 card catalog directly in the static HTML markup. This guarantees instant First Contentful Paint (0ms) and zero blank screen even if the visitor has strict adblockers or offline network.
2. **Asynchronous Public CORS Bridge Fetch:**
   Attempt a client-side update via an open CORS bridge (e.g. `https://api.allorigins.win/get?url=...` with `__a=1&__d=dis`). If successful, dynamically hydrate the DOM with recent posts.
3. **Fallback Grace Period:**
   Wrap the fetch in an aggressive timeout (`AbortSignal.timeout(2500)`). If it fails or times out, seamlessly keep the pre-rendered high-res cards without throwing visible errors.
4. **Actionable Conversion CTAs:**
   Every card should feature two distinct action paths:
   - Deep-link booking button (e.g., WhatsApp click-to-chat with URL-encoded service title).
   - Original social post link (`https://www.instagram.com/p/{shortcode}/`).

---

## 3. Third-Party Map & Vessel Tracking Embed Mitigations

Services like MarineTraffic and VesselFinder block direct `<iframe>` embedding via `X-Frame-Options: SAMEORIGIN` / 403 Forbidden on unauthenticated domains.

### Best Practice Solutions
1. **Direct Telemetry Launcher Console:**
   Replace crashing iframes with a high-density launcher card featuring search inputs (Vessel Name/IMO) and quick port jump buttons that open targeted coordinates (`https://www.marinetraffic.com/en/ais/home/centerx:.../centery:.../zoom:...`).
2. **Local Vector GIS Radar (Leaflet.js):**
   Render interactive dark-theme maps locally using Leaflet + CartoDB Voyager tiles and custom vector markers (`L.circleMarker`) for local port zones.
