# In-Game Items & Nominal Cards Visual Architecture

Best practices for designing high-converting, tactile nominal cards (`.product-card`) in digital gaming top-up funnels.

---

## 1. Tactile Thumbnail Box System
- **Desktop Dimensions:** `44x44px` box with 8px radius (`--radius-sm`), 4px padding.
- **Mobile Dimensions:** `36x36px` box with 8px radius, 3px padding.
- **Surface Elevation:** Background `var(--surface-overlay)` (#1C1C2A), 1px specular rim border `rgba(255, 255, 255, 0.1)`, inset shadow `inset 0 1px 2px rgba(0,0,0,0.5)`.
- **Item Asset Depth:** Apply `filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5))` to PNG/WebP icons for 3D tactile pop-out effect.
- **Image Fallback Chain:**
  1. Primary: `assets/items/{item_key}.webp`
  2. Format Fallback: `assets/items/{item_key}.png`
  3. Brand Fallback: `assets/brands/logos/{brand_code}.webp`
  4. Vector Fallback: Generic Category SVG icon.

---

## 2. Glowing Special Pass Badges
Nominal passes (e.g. Weekly Passes, Subscriptions, Memberships) generate higher repeat purchase rates and LTV. Give them distinct glowing pill badges:

| Pass Type | Gradient Background | Border & Glow Color | Target Products |
|---|---|---|---|
| **Weekly Diamond Pass (WDP)** | `linear-gradient(135deg, rgba(255,229,0,0.25), rgba(0,229,255,0.2))` | Yellow `#FFE500` (Glow 12px) | MLBB WDP, Free Fire Weekly |
| **Starlight / Battle Pass** | `linear-gradient(135deg, rgba(217,70,239,0.25), rgba(99,102,241,0.2))` | Magenta `#F472B6` (Glow 12px) | MLBB Starlight, Twilight Pass |
| **Daily Blessing / Supply** | `linear-gradient(135deg, rgba(56,189,248,0.25), rgba(129,140,248,0.2))` | Cyan `#38BDF8` (Glow 12px) | Welkin Moon (Genshin), Express Supply (HSR) |
| **Level Up Pass** | `linear-gradient(135deg, rgba(234,88,12,0.25), rgba(245,158,11,0.2))` | Amber `#FBBF24` (Glow 10px) | Free Fire Level Up Pass |

---

## 3. Numeric Pricing Discipline
- **Tabular Font Variant:** Enforce `font-variant-numeric: tabular-nums` on all price elements to eliminate horizontal jitter during filtering or responsive rendering.
- **Hierarchical Scale:** Separate the currency symbol (`Rp` at 11px font-mono, 85% opacity) from the numeric value (`24.500` at 16px font-mono bold, Electric Citrus `#FFE500`).
- **Punctuation Standard:** Format Indonesian Rupiah using standard dot thousand separators (e.g., `Rp 150.000`, not `150,000` or raw unformatted numbers).

---

## 4. Micro-Interaction Dynamics
- **Hover:** `translateY(-3px) scale(1.01)` over `200ms cubic-bezier(0.16, 1, 0.3, 1)`. Thumbnail scales `1.06`. Specular rim highlights with 15% brand yellow wash.
- **Active / Tap:** Feedback scale `0.99` with reduced elevation.
- **Selected State:** Border `1px solid var(--brand-primary)` (#FFE500), subtle background tint `rgba(255, 229, 0, 0.08)`, and ambient drop shadow `0 8px 20px -4px rgba(255, 229, 0, 0.25)`.
- **Keyboard Navigation:** Native `:focus-visible` with 2px solid brand accent and 2px offset.
