---
name: brand-asset-curation
description: Curate official brand logos, icons, covers, and banners.
---

# Brand & Visual Asset Curation

Workflows for discovering, extracting, standardizing, and optimizing official brand visual assets (logos, vector marks, app icons, game covers, and promo banners).

## 1. High-Precision Official Asset Sources

### A. Apple App Store iTunes Search API (High-Resolution App Icons & In-Game Screens)
The iTunes Search API provides unauthenticated, highly reliable access to official 512x512 PNG app icons and 2796x1290 uncompressed screenshots for mobile games, fintech/e-wallets, telcos, and utility apps.
- **Endpoint**: `https://itunes.apple.com/search?term={query}&entity=software&country={country_code}&limit=5`
- **Country codes**: `id` (Indonesia), `us` (Global/US), `sg` (Singapore), `gb` (UK).
- **512x512 HD Icon URL**: `artworkUrl512` in JSON response.
- **Full-Res Artwork / Screenshots**:
  - iTunes returns URLs like: `https://is1-ssl.mzstatic.com/.../cover_2796x1290.jpg/320x480bb.jpg`
  - Strip the thumbnail resize suffix via regex: `re.sub(r'/[0-9]+x[0-9]+bb\.[a-z]+$', '/2796x1290bb.jpg', url)` to fetch raw high-resolution screenshots.

### B. Simple-Icons Vector Repository (Clean Official SVG Logomarks)
For developer, tech, utility, and global platforms (Steam, Spotify, PlayStation, Google Play, Riot Games, Valorant, PUBG, Shopee, Grab):
- **Raw SVG URL**: `https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/{slug}.svg`

### C. Riot Games Official Valorant Agent API (High-Res Transparent Splash & Backgrounds)
Direct endpoint for high-resolution transparent agent portraits and background key art:
- **Endpoint**: `https://valorant-api.com/v1/agents?isPlayableCharacter=true`
- **Fields**: `fullPortrait` (transparent 2048px PNG) and `background` (abstract art).

### D. Steam Store App Details API (Official High-Res PC Game Key Art & Screenshots)
Fetches uncompressed 1920x1080 official screenshots and header key visuals for PC & cross-platform titles (PUBG, Growtopia, Asphalt, etc.):
- **Endpoint**: `https://store.steampowered.com/api/appdetails?appids={appid}`
- **Screenshot field**: `data['screenshots'][0]['path_full']`

### E. Wikimedia Commons & Fandom Wikia MediaWiki APIs
- **Wikimedia Commons API**:
  `https://commons.wikimedia.org/w/api.php?action=query&titles={File:Name}&prop=imageinfo&iiprop=url|size|mime&format=json`
- **Fandom Game Wikis API (MLBB, Genshin, HSR, Call of Duty, etc.)**:
  - Image Info: `https://{game}.fandom.com/api.php?action=query&titles=File:{FileName}&prop=imageinfo&iiprop=url|size|mime&format=json`
  - Image Search: `https://{game}.fandom.com/api.php?action=query&list=search&srsearch={query}&srnamespace=6&format=json`
  - Prefix Index: `https://{game}.fandom.com/api.php?action=query&list=allimages&aifrom={prefix}&ailimit=50&format=json`
- Always supply a custom `User-Agent` header (`BrandAssetCollector/1.0 (+url; contact: email)` or modern browser UA) to avoid HTTP 429/403 rate limits.

### F. Official Game Asset Data Repositories & Currency APIs
- **Riot Valorant Currencies API**: `https://valorant-api.com/v1/currencies` (contains official VP, Radianite, Kingdom Credits large & display icons).
- **Honkai Star Rail Open Data (StarRailRes)**: `https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/icon/item/{id}.png` (e.g. `3.png` for Oneiric Shard, `300101.png` for Express Supply Pass).

---

## 2. Standardization & Multi-Format Processing Pipeline (Pillow + librsvg)

Always generate paired formats (`.webp` and `.png`) to ensure progressive enhancement and maximum browser compatibility.

### Tool Requirements
- `rsvg-convert` (from `librsvg2-bin`) to rasterize SVGs cleanly with transparency:
  `rsvg-convert -w 512 -h 512 -f png -o output.png input.svg`
- Python `PIL` (Pillow) with `WEBP` support.

### Common Standard Dimensions
1. **Logos / App Icons & In-Game Item Badges**: `512x512 px` (PNG 32-bit Alpha + WebP quality=95, method=6).
2. **Portrait Product / Game Cards**: `600x800 px` (Aspect Ratio 3:4).
   - Center crop using `LANCZOS` resampling.
   - Add dark vignette bottom gradient for readable overlay text.
3. **Landscape Banners**: `1200x630 px` (Standard Open Graph / Promo Ratio 1.91:1).

---

## 3. In-Game Items, Currencies & Membership Badges Pipeline

When building item catalogs for top-up stores (MLBB Diamonds, WDP, Starlight, FF Diamonds, Genshin Genesis Crystals, Welkin Moon, HSR Oneiric Shards, Pass):

### A. Item Manifest JSON Standard Structure (`assets/items/manifest.json`)
```json
{
  "version": "1.0.0",
  "updated_at": "YYYY-MM-DDTHH:MM:SS+07:00",
  "total_items": N,
  "total_files": N,
  "base_path": "./assets/items/",
  "items": {
    "item_code": {
      "item_code": "item_code",
      "game": "Game / Brand Display Name",
      "name": "Full Item Name",
      "category": "Currencies" | "Pass / Membership" | "Utilities" | "Telco" | "E-Wallet",
      "png": "assets/items/item_code.png",
      "webp": "assets/items/item_code.webp",
      "width": 512,
      "height": 512,
      "has_alpha": true
    }
  }
}
```

### B. Tier Scaling & Visual FX (Pillow Composition)
To represent different nominal currency tiers (e.g. 60 vs 300 vs 980 vs 6480 Crystals):
- **Single / Small Tier**: Single centered high-res asset (e.g. 260x260 - 320x320) with soft colored outer glow.
- **Medium Tier / Cluster**: Cluster of 2–3 angled assets (rotated ±12°–15°) with depth layering.
- **Large / Treasury Tier**: Base ornate container (chest/pouch/tactical box) overflowing with multiple angled crystals/diamonds.
- **Ambient Glow & Shadow**: Composite blurred alpha layers for drop shadows `(0, 0, 0, 160)` and theme-colored radial glow `(R, G, B, 140–190)` behind transparent sprites.

---

## 4. Brand Asset Manifest & Dynamic Frontend Integration

When building or auditing a catalog of brand assets for web/mini-app frontends, structure metadata into a standardized `manifest.json`:

### A. Manifest JSON Standard Structure
```json
{
  "version": "1.0.0",
  "updated_at": "YYYY-MM-DDTHH:MM:SS+07:00",
  "total_brands": N,
  "base_path": "./assets/brands/",
  "brands": {
    "brand_code": {
      "brand_code": "brand_code",
      "brand_name": "Official Brand Display Name",
      "category": "Games" | "E-Wallet" | "Telco" | "Vouchers" | "Utility",
      "is_game": true | false,
      "app_bundle": "com.developer.app",
      "app_title": "Official App Store Title",
      "logo": {
        "png": "assets/brands/logos/brand_code.png",
        "webp": "assets/brands/logos/brand_code.webp",
        "width": 512,
        "height": 512,
        "has_alpha": true
      },
      "cover": {
        "png": "assets/brands/covers/brand_code_cover.png",
        "webp": "assets/brands/covers/brand_code_cover.webp",
        "width": 600,
        "height": 800
      },
      "banner": {
        "png": "assets/brands/banners/brand_code_banner.png",
        "webp": "assets/brands/banners/brand_code_banner.webp",
        "width": 1200,
        "height": 630
      }
    }
  }
}
```

### B. Fast Disk Integrity Audit Pattern
Audit that 100% of manifest-declared image paths physically exist on disk before completing asset handoffs:
```python
import os, json

with open('assets/brands/manifest.json') as f:
    manifest = json.load(f)

base_dir = '.'
missing = []
for b_id, b_data in manifest.get('brands', {}).items():
    for asset_type in ['logo', 'cover', 'banner']:
        asset_info = b_data.get(asset_type, {})
        for fmt in ['png', 'webp']:
            rel_path = asset_info.get(fmt)
            if rel_path and not os.path.exists(os.path.join(base_dir, rel_path)):
                missing.append((b_id, asset_type, fmt, rel_path))

assert len(missing) == 0, f"Missing {len(missing)} asset files: {missing}"
```

---

## 4. Critical Pitfalls & Solutions

### A. Vignette Math on Normalized Height
When generating smooth power curves on normalized heights `norm = float(y - start_y) / float(height - start_y)`:
- In floating point math near `start_y`, float imprecision can produce negative numbers like `-1.5e-16`.
- In Python, `(-1.5e-16) ** 1.8` returns a **complex number** (`nan + 1.2j`), causing `int()` conversion to fail with `int() argument must be a string... not 'complex'`.
- **Solution**: Always clamp normalized values: `norm = max(0.0, float(y - start_y) / float(height - start_y))`.

### B. Wikimedia Rate Limiting
- Direct downloads of Wikimedia upload URLs without custom User-Agent headers trigger 429 WAF blocks.
- Use iTunes Search API and Simple-Icons raw GitHub endpoints for high-throughput headless automation.
