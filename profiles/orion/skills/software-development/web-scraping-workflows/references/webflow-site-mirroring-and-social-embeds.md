# Webflow Full-Site Mirroring & Offline Interaction Fixes

When scraping, cloning, or mirroring Webflow websites for static hosting or redesign:

## 1. Webflow Interaction 2.0 (IX2) Blank Hero Pitfall
Webflow uses inline HTML styles for initial animation states before JavaScript executes:
```html
<!-- Webflow initial state in HTML -->
<div data-w-id="abc" style="opacity: 0; transform: translate3d(0, 40px, 0)...">
```
In offline rendering, headless browser screenshots, or environments where `webflow.js` fails or delays, the entire hero section or content cards will render completely invisible (blank/gray background).

### Deterministic Patch:
1. Strip initial zero opacity and translate3d inline styles:
   ```python
   content = re.sub(r'style="([^"]*?)opacity:\s*0;?([^"]*?)"', r'style="\1opacity: 1;\2"', content)
   content = re.sub(r'style="([^"]*?)transform:\s*translate3d\([^)]+\);?([^"]*?)"', r'style="\1\2"', content)
   ```
2. Inject a fallback CSS override in `<head>`:
   ```html
   <style>
     /* Ensure all Webflow interaction elements are visible immediately */
     [data-w-id], .w-dyn-item, .hero-wrapper, .section, .image-wrapper, .hero-content {
       opacity: 1 !important;
       transform: none !important;
       visibility: visible !important;
     }
   </style>
   ```

## 2. Scraping Webflow Asset Dependencies
A full Webflow mirror requires downloading:
- CSS files from `cdn.prod.website-files.com/.../css/...`
- Font icon files referenced inside CSS (`.woff2`, `.eot`, `.ttf`, `.woff`, `.svg`)
- JavaScript bundles (`webflow.js`, `jquery.min.js`, `webfont.js`)
- Responsive image variants in `srcset` (`-p-500.jpeg`, `-p-800.jpeg`, `-p-1080.jpeg`, `-p-1600.jpeg`, `-p-2000.jpeg`)

## 3. Removing Webflow Branding / Watermarks
```python
# Clean Webflow badges and hire popups safely
c = re.sub(r'<a class="w-webflow-badge".*?</a>', '', c, flags=re.DOTALL)
c = re.sub(r'<div class="hire-popup".*?</div>\s*</div>', '', c, flags=re.DOTALL)
```

---

# Instagram Live Feed Integration Patterns for Pure Static HTML

Instagram (Meta) enforces strict CDN expiration (direct photo URLs expire in 24–48h) and anti-bot measures on direct client-side requests.

## 1. Official Instagram Embed (Zero Maintenance, Interactive)
Best for showcasing live video/reels, captions, and official follow buttons without needing any backend server.
```html
<div class="ig-embed-grid">
  <blockquote class="instagram-media" 
    data-instgrm-captioned 
    data-instgrm-permalink="https://www.instagram.com/p/POST_ID/" 
    data-instgrm-version="14" 
    style="background:#181818; border:0; border-radius:8px; width:100%; max-width:480px;">
  </blockquote>
</div>
<script async src="//www.instagram.com/embed.js"></script>
```
- **Pros:** 100% official, will never expire, supports video play and direct likes.
- **Cons:** Higher initial page weight (~1.5MB - 3MB for multiple embeds), taller vertical aspect ratio.

## 2. Pre-Rendered Catalog + Dynamic CORS Bridge Fallback
Best for ultra-fast, luxury custom barbershop/salon dark-mode grids:
- Pre-render high-res photo cards with WhatsApp booking deep-links (`https://wa.me/<number>?text=...`).
- Execute background async fetch via public JSON bridge to attempt real-time update.
- If CORS fails or rate-limits hit, the UI remains 100% styled and functional without breaking.
