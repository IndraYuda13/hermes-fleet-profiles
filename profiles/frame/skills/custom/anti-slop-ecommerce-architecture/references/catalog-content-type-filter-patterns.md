# Catalog Content Type Filtering & Action Toolbar Patterns

## Context & Purpose
Captures zero-slop UX architecture for filtering binary/multi-partition catalogs (such as Anime vs Donghua, Digital Goods vs Subscriptions, Movies vs Series) in streaming and digital content platforms.

## 1. Multi-Select Toggle Pills vs Tri-State Segmented Capsule
When partitioning catalog items where partition subsets sum to 100% of the catalog (e.g. Anime: 50 + Donghua: 282 = 332 total items):

### Option A: Independent Multi-Select Toggle Pills (Set-Based Filter)
When the product spec specifies independent toggles (e.g. `catalogState.types = new Set(['anime', 'donghua'])`):
- **Zero-Selection Safety Guard (Mandatory)**: If a user clicks the sole active filter pill (attempting to turn off everything), never leave the grid in a dead empty void. The interaction must automatically re-activate both pills (`Set(['anime', 'donghua'])`) and reset query to `type=all`.
- **Dynamic Counters**: Place dynamic count badges inside the pills (`#katalog-count-anime`, `#katalog-count-donghua`) updated directly from the API's `type_counts` payload.
- **Accessible State**: Mark each button with `role="checkbox"` and `aria-checked="true|false"`, co-located in a container with `role="group"`.
- **Reset Filter Integration**: The catalog-level "Reset Filter" button must restore both type pills to active state alongside clearing search queries and genre filters.

### Option B: Tri-State Segmented Frosted Capsule
When a single unified capsule selector is preferred:
```text
[ Semua (332) | ✦ Anime (50) | ✦ Donghua (282) ]
```
- **1-Tap Switching:** Switching between partitions requires only a single tap.
- **Single Truth for 'Both':** `Semua` natively models both partitions enabled (`type=all`).
- **Toggle-Reset Behavior:** Tapping an already active partition pill resets to `Semua` (`type=all`).

## 2. Macro-to-Micro Action Toolbar Zoning
Layout hierarchy above the poster grid:
1. **Header:** Title + Total Count Badge + Search Bar.
2. **Controls Sub-Row (`.katalog-controls-row`):**
   - Desktop (`>= 768px`): Split row (`justify-content: space-between`). Left side holds Content Type Bar (`Tipe Konten: [Anime (50)] [Donghua (282)]`), right side holds Sort Capsule (`Urutkan: [A-Z] [Rating] [Terbaru]`).
   - Mobile (`< 640px`): Stacked full-width sub-bars (`flex-direction: column; align-items: stretch`). Each bar justifies label to the left and pills to the right (`justify-content: space-between; width: 100%`) to eliminate horizontal scroll and overflow (`scrollWidth <= clientWidth`).
3. **Thematic Filter:** Genre / Style scrollable pill strip (`overflow-x: auto; scrollbar-width: none`).

## 3. Card Badge Placement & Visual Contrast
- In media poster grids, the top-right corner is typically occupied by dynamic status badges (e.g. `E15 Diperbarui`, `Tamat`).
- Secondary taxonomy badges (e.g. `Anime` vs `Donghua`) must sit at the **top-left** (`.poster-badge-type` or `.poster-badge-top-left`) to prevent visual collision.
- Use soft cinematic color coding with specular rims rather than high-saturation neon:
  - **Anime (Cool Celestial Sky Cyan):** `rgba(14, 116, 144, 0.85)` bg, `#E0F2FE` text, `rgba(56, 189, 248, 0.5)` rim.
  - **Donghua (Warm Imperial Amber):** `rgba(180, 83, 9, 0.85)` bg, `#FEF3C7` text, `rgba(245, 158, 11, 0.5)` rim.
