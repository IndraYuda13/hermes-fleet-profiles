---
name: graphic-logo-generator
description: Generate logo badges and stickers from images via PIL/rembg.
version: 1.0.0
metadata:
  hermes:
    tags: [logo, graphic-design, pillow, rembg, image-generation, badges]
    category: creative
---

# Graphic Logo & Product Marketing Banner Generator

Use this skill when a user provides an image, photo, mascot, or product photo and asks to create a logo, sticker, marketing promo banner, social media poster, or circular emblem.

## Toolchain & Setup

- **Vector Master & Resolution Independence:** For crisp, infinite-scale mascot logos, badges, and commercial emblems, prefer generating structured **SVG** markup and rasterizing via `rsvg-convert` (e.g. `rsvg-convert -w 2000 -h 2000 input.svg -o output.png`).
- **Product Marketing Banners & Social Media Creatives:**
  - **Aspect Ratios:** Feed/Marketplace (4:5, e.g. `1080x1350`), Story/Status (9:16, e.g. `1080x1920`), Square (1:1, `1080x1080`).
  - **Background Removal / Cutout:** Use `rembg` (`u2net`) or dynamic NumPy RGB distance thresholding with Gaussian blur feathering when subject is on studio white background.
  - **Color Harmony:** Warm honey/orange + fresh leaf/forest green + cream gradient for fruits/organic food; deep luxury dark glass for tech/lifestyle.
  - **Hierarchy:** Top Category Pill → Catchy Headline → Enhanced Product Centerpiece + Benefit Badges (Left/Right) → High-converting CTA/Pricing Card at Bottom.
  - **Icon & Glyphs Rendering:** Avoid rendering raw unicode symbols (like `≡`, `✦`, `📦`) if font lacks glyphs; use clean geometric shapes (`draw.rounded_rectangle`), checkmarks (`✓`), or clean text labels to prevent rendering glitches.
- **Graphic Compositing:** Python `Pillow` (PIL) for canvas manipulation, alpha masks, circular emblems, badge borders, and typography rendering.
- **Typography:** Use clean geometric sans or display fonts (`PlusJakartaSans-Bold.ttf`, `Inter`, `Liberation Sans`, or Google Fonts). Use high-contrast strokes and letter-spacing/tracking.

## Commercial Caricature & Mascot Logo Patterns

1. **Facial Feature Translation from Reference Photos:**
   - **Chubby Cheeks & Jawline:** Exaggerate lower cheek width (pear/squircle silhouette) with soft blush ellipses and pill-shaped white reflection dots.
   - **Hair Bangs / Fringe:** Break rigid geometric zigzags into natural curved strand clusters with glossy light-reflection arcs.
   - **Eyes & Catchlights:** Large anime/chibi dark irises with dual circular white catchlights for an approachable, vibrant gaze.
   - **Expression:** Add a friendly curved smile/grin or tongue accent to make commercial mascots welcoming.
2. **Badge Architecture & Visual Assets:**
   - Always include thematic props (e.g. crossed pencils/brushes for art studios, spatulas for food, barber shears for grooming).
   - Multi-ring layered emblems with dashed accent orbits and sparkle stars.
   - 3D curved swallowtail ribbon banners with inner gold borders for the primary brand title.
   - Bottom pill/capsule badge for sub-taglines (`JASA ILUSTRASI & MASCOT`, `OPEN COMMISSIONS`).
3. **Royal Heraldic Crest & Kingdom Coat of Arms Pattern:**
   - **Shield (Escutcheon):** Heater or arched shield with 3D multi-stop metallic gold bevels (`#FFEFA6` -> `#E5B942` -> `#8F6305`) and deep imperial crimson/maroon core.
   - **Imperial Crown (Crest):** Multi-point coronet studded with rubies, sapphires, and emeralds, backed by crimson velvet and an illuminated white ermine fur trim band.
   - **Weapons & Regalia:** Crossed saltire swords with ruby-encrusted pommels, golden sovereign scepters, or imperial axes behind the shield.
   - **Foliage & Motto:** Sweeping 3D laurel wreath branches (victory/prosperity) and an arched Latin motto banner at the top (`REGNUM ET GLORIA SEMPER`).
   - **Monogram Sigil:** Intertwined luxury monogram (e.g. "LA" for Lord Aldi) crowned with radiant 5-point diamond star in the shield's center.
4. **Delivery Package Checklist:**
   - Provide high-resolution PNGs (2000x2000px) delivered via `MEDIA:...`.
   - Provide transparent background versions (`_transparent.png`) for watermarks, merchandise, wax seals, and sticker printing.
   - Provide editable vector SVGs and bundle everything into a downloadable `.zip` archive.
5. **Web & Storefront Deployment:**
   - When deploying a showcase landing page or web calculator, serve static assets via Nginx on an unprivileged loopback port (e.g. 8270) with root directory permissions set to 755/644, mapped cleanly to Cloudflare Tunnel.

## Official ID Photo / Pasfoto Processing (Chroma Key & Dimension Invariants)

When converting formal ID photos / pasfoto backgrounds (e.g. Blue to Red, or Red to Blue) for official Indonesian standards:
1. **Official Color Codes:**
   - **Official Red (Ganjil / Odd years):** RGB `(219, 21, 20)` / `#DB1514` (BGR `(20, 21, 219)` in OpenCV).
   - **Official Blue (Genap / Even years):** RGB `(11, 74, 182)` / `#0B4AB6` (BGR `(182, 74, 11)`).
2. **Deterministic Fast HSV Chroma Keying (Zero Onnx/Model Dependency):**
   - For solid backdrops (studio blue/red), avoid heavy ML models (which can timeout on downloading gigabyte weights).
   - Use OpenCV HSV thresholding:
     - Blue range: `lower_blue = np.array([100, 70, 50])`, `upper_blue = np.array([135, 255, 255])`.
   - Perform morphological ellipse closure (`cv2.MORPH_CLOSE`, `(3,3)`, 2 iterations) to prevent holes in dark hair or batik shirt patterns.
   - Feather mask edges using `cv2.GaussianBlur` with alpha blending (`(3,3)` kernel).
   - **Color Decontamination / Defringing:** Replace edge pixels where background color spills into hair/neck before alpha-blending with target background to prevent blue halos.
3. **Standard Indonesian Pasfoto Aspect Ratios & Dimensions (300 DPI):**
   - **4x6 cm:** `472 x 709 px`
   - **3x4 cm:** `354 x 472 px`
   - **2x3 cm:** `236 x 354 px`
   - Always resample using `Image.Resampling.LANCZOS` and save at high quality (JPEG quality >= 98).

## Key PIL Techniques & Critical Pitfalls

1. **`ImageFilter.MaxFilter(size)`:** 
   - `size` **MUST be an odd integer** (e.g. 21, 31, not 20). Passing an even number raises `ValueError: bad filter size`.
   - Use `MaxFilter` on an alpha channel to generate crisp outer sticker outlines or cutout borders.
2. **Drop Shadow Generation:**
   - Blur expanded alpha channel using `ImageFilter.GaussianBlur(15)` and composite with opacity `(0, 0, 0, 80-120)` beneath the subject.
3. **Badge & Emblem Layout Pattern:**
   - **Outer Rings:** Concentric multi-color rings (e.g., Deep Navy + Gold, Pop Yellow + Orange, Pastel Mint + Cream, Chili Red + Mustard).
   - **Dynamic Depth:** Place the subject popping out of the top/side border of the inner circular mask.
   - **Banner Ribbon:** Place the main title container / pill banner at the bottom third `(y ~ 850)`.
   - **Text Stroke:** Use `stroke_width=4-8` and contrasting `stroke_fill` on title text for maximum readability across light and dark displays.
4. **Font Download & Fallback Handling:**
   - When pulling Google Fonts directly via GitHub raw links, always verify URLs (static subdirectory vs root) or have system fallback fonts (`FreeSansBold.ttf`, `LiberationSans-Bold.ttf`) to avoid script crashes.
   - Odd pixel dimension handling: always convert dimensions to integers `int(...)` before resizing or cropping to prevent PIL TypeError.
5. **Rembg Session & Model Selection:**
   - Default rembg `bria-rmbg-2.0` model weight is >1GB and can time out on slower network/sandboxes.
   - Explicitly specify `session = rembg.new_session('u2net')` (176MB) for faster, reliable background removal downloads.

## Delivery Standard

- Save outputs as lossless PNGs (`/tmp/...png`).
- Deliver native image attachments to the user using `MEDIA:/path/to/image.png`.
- Provide 3–4 distinct thematic variations (e.g. playful pop-art, vintage badge, modern minimalist, bold street food / retail).
