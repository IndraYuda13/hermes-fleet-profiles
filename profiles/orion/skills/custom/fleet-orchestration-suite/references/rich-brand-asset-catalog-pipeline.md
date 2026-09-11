# Rich Brand Asset & Visual Catalog Pipeline Standard

Architecture and execution protocol for enriching web storefronts and digital top-up platforms with high-density visual assets (official HD logos, 3:4 portrait poster cards, and interactive search thumbnails) while maintaining sub-second rendering, zero cumulative layout shift (CLS), and strict security.

---

## 1. Asset Discovery & Standardization (RADAR)

1. **Asset Matrix & Multi-Format Generation:**
   - **Logo Badges (512×512px):** Transparent WebP & PNG with transparent backgrounds, high-contrast brand monograms, and crisp edge rendering.
   - **Cover Posters (600×800px / 3:4 Ratio):** Standardized portrait game/brand key visual cards featuring hero character art, subtle themed gradient backdrops, ambient lighting, and watermark integration.
   - **Metadata Manifest (`manifest.json`):** Unified metadata mapping brand keys, human-readable labels, category associations, custom theme accent/background hex colors, and relative file paths.

2. **Standard Manifest Schema:**
   ```json
   {
     "brand_code": "mobile_legends",
     "brand_name": "Mobile Legends: Bang Bang",
     "category": "Games",
     "theme": {
       "bg_color": "#1c2a4a",
       "accent_color": "#d4af37"
     },
     "assets": {
       "logo": {
         "webp": "assets/brands/logos/mobile_legends.webp",
         "png": "assets/brands/logos/mobile_legends.png",
         "resolution": "512x512"
       },
       "cover": {
         "webp": "assets/brands/covers/mobile_legends.webp",
         "png": "assets/brands/covers/mobile_legends.png",
         "resolution": "600x800"
       }
     }
   }
   ```

---

## 2. Dynamic Backend Asset Serving & Security (FORGE & ATLAS)

1. **Path Traversal Prevention:**
   - Avoid hardcoded file whitelists that break dynamic catalog expansion.
   - Use strict canonical path resolution to ensure requested paths cannot escape the base directory:
     ```python
     assets_dir = (WEB_SKELETON_DIR / 'assets').resolve()
     target_file = (assets_dir / asset_path).resolve()
     if not target_file.is_relative_to(assets_dir) or not target_file.is_file():
         raise HTTPException(status_code=404, detail='Asset not found')
     ```
2. **Cache Header Optimization:**
   - Static brand assets (`.webp`, `.png`): `Cache-Control: public, max-age=86400`.
   - Manifest metadata (`manifest.json`): `Cache-Control: no-cache, must-revalidate`.
3. **Graceful Reload Invariant (ATLAS):**
   - After updating static routing or service endpoints, execute graceful systemd/process restart and verify HTTP 200 on manifest and binary endpoints before notifying frontend workers.

---

## 3. UI/UX Art Direction & Component Architecture (AURORA)

1. **3:4 Portrait Poster Card Archetype (`.brand-poster-card`):**
   - Visual hierarchy: High-resolution cover artwork fills the 3:4 card container.
   - **Scrim Lighting Overlays:** Multi-stop linear gradient (`rgba(8,8,12,0) 0%, rgba(8,8,12,0.65) 60%, rgba(8,8,12,0.95) 100%`) positioned at the bottom of the card to guarantee pristine legibility of brand titles and pricing pills.
   - **Floating Logo Badge:** 32–40px thumbnail avatar positioned with 8px corner radius and specular 1px border.
   - **Dynamic Ambient Hover Aura:** Subtle radial shadow using the brand's unique `theme.bg_color` upon mouse hover/touch focus (`transform: translateY(-4px) scale(1.015)`).

2. **Spotlight Search Palette Integration (`⌘K`):**
   - High-density 36×36px logo thumbnails displayed on the leading edge of every search item.
   - Keyboard selection highlight (`ArrowUp`/`ArrowDown`) triggers specular accent outline (`var(--brand-primary)`).

3. **Checkout Ledger Hero Banner:**
   - Order confirmation header features a blended 84px cover art backdrop and 48×48px brand logo to eliminate user checkout anxiety (*zero-anxiety confirmation*).

4. **Multi-Layer Fallback & CLS < 0.01:**
   - Always structure markup using `<picture>` elements:
     ```html
     <picture>
       <source srcset="assets/brands/covers/brand.webp" type="image/webp">
       <img src="assets/brands/covers/brand.png" alt="Brand" loading="lazy" onerror="this.parentElement.style.display='none'; this.parentElement.nextElementSibling.style.display='flex';">
     </picture>
     <div class="brand-monogram-fallback" style="display:none; background: #themeColor;">
       <span>MN</span>
     </div>
     ```

---

## 4. Multi-Viewport Responsiveness & QA (LENS)

- **Desktop (≥1280px):** 4-column poster grid.
- **Tablet / Laptop (768px–1279px):** 3-column grid.
- **Mobile (360px–767px):** 2-column grid with touch-target safety (>=44px).
- Verify 0px horizontal overflow across all 7 canonical viewports (`320px` to `1920px`).
