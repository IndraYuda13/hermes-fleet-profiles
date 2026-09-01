# Brand & Cover Artwork Integration in Fintech Top-Up UI

Techniques and standards for integrating multi-tier visual brand assets (HD Logos 512x512, Cover Posters 600x800, Banner Artworks) into digital cashier and top-up catalogs while preserving Apple/Swiss Grade precision, performance, and Zero CLS.

---

## 1. 3:4 Aspect Ratio Brand Poster Card Architecture

Replacing flat button rows with rich portrait poster cards elevates the product experience from a utilitarian form into an immersive gaming store:

```html
<button class="brand-poster-card" data-key="{brand_code}" type="button">
  <div class="card-glow" style="--brand-glow: {theme.bg_color};"></div>
  <div class="card-media-wrapper">
    <picture>
      <source srcset="assets/brands/covers/{brand_code}.webp" type="image/webp">
      <img src="assets/brands/covers/{brand_code}.png" 
           alt="{brand_name}" 
           class="card-cover-img" 
           loading="lazy" 
           onerror="this.onerror=null; this.src='assets/brands/logos/{brand_code}.png'; this.classList.add('is-fallback');" />
    </picture>
    <div class="scrim-overlay"></div>
    <div class="specular-rim"></div>
  </div>
  <div class="card-header-meta">
    <span class="category-pill">{category}</span>
    <span class="instant-pill">⚡ Instan</span>
  </div>
  <div class="card-footer-info">
    <div class="brand-logo-badge">
      <img src="assets/brands/logos/{brand_code}.webp" alt="" class="logo-thumb-icon" onerror="this.src='assets/brands/logos/{brand_code}.png'" />
    </div>
    <div class="brand-text-block">
      <h3 class="brand-title">{brand_name}</h3>
      <p class="brand-subtitle">{count} Pilihan Nominal</p>
    </div>
  </div>
</button>
```

### Essential Geometry & CSS Tokens:
- **Aspect Ratio:** `3 / 4` (`aspect-ratio: 3 / 4; width: 100%; min-height: 220px;`).
- **Responsive Columns:** 4 cols (≥1280px), 3 cols (768px–1279px), 2 cols (360px–767px).
- **Bottom Scrim:** `linear-gradient(180deg, rgba(8,8,12,0) 0%, rgba(8,8,12,0.4) 40%, rgba(8,8,12,0.95) 100%)`.
- **Micro-Hover Dynamics:** `translateY(-4px) scale(1.015)` with `transition: transform 220ms cubic-bezier(0.16, 1, 0.3, 1)`.

---

## 2. High-Density Spotlight Autocomplete with HD Logos

In keyboard command palettes (`⌘K`) and search bars:
- Use 36x36px logo thumbnails (`border-radius: 8px`, `background: var(--surface-overlay)`, `border: 1px solid rgba(255,255,255,0.08)`).
- `object-fit: contain` with 2px inner padding to prevent clipped logos.
- Active keyboard highlight displays subtle 2px glow matching the brand primary accent.

---

## 3. Order Summary & Sticky Ledger Hero Banner

When a brand/nominal is selected, reinforce identity confirmation at the checkout ledger:
- 84px height hero banner at the top of the order summary card.
- Background cover art masked with a gradient (`mask-image: linear-gradient(to left, black 0%, transparent 100%)` and `opacity: 0.35`).
- Prominent 48x48px logo thumbnail alongside game title and SKU nominal for zero-anxiety verification before payment.

---

## 4. Resilient Fallback & Zero Layout Shift (CLS = 0)

1. **Modern Format Priority:** Always deliver WebP via `<picture>` with fallback to PNG.
2. **Container Reservation:** Always declare fixed aspect ratio or `min-height` on image containers to prevent reflow during image load.
3. **SVG Monogram Fallback:** If both WebP and PNG fail to load, switch to a CSS gradient card using `theme.bg_color` with bold initial letters in Display font (`Sora` / `Inter`) and category vector icon.
