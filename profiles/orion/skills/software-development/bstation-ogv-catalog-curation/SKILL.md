---
name: bstation-ogv-catalog-curation
description: Use when harvesting or filtering Bstation OGV anime APIs.
---

# Bstation OGV Catalog Curation & Upstream Filtering

This skill guides harvesting, filtering, and curating official anime catalogs from Bstation (Bilibili Global / `bilibili.tv`) APIs.

## 1. Upstream Catalog API (`ogv/index/items_v2`)

Endpoint:
```http
GET https://api.bilibili.tv/intl/gateway/web/v2/ogv/index/items_v2
Params:
  season_type: "1,4"
  platform: "web"
  s_locale: "id_ID"
  pn: <page_num>
  ps: 50
```

### Season Type Breakdown
- `season_type=1`: Japanese Anime (~50 titles on the public index).
- `season_type=4`: Chinese OGV content (~282 titles).
- `season_type=5`: Short dramas / micro-dramas (~1400+ titles).

## 2. Pitfall: Short Drama (Dracin) Infiltration in `season_type=4`

When requesting `season_type=1,4`, Bstation bundles both authentic Chinese animations (Donghua) and live-action short dramas (dracin/micro-dramas) under `season_type=4`.

### Symptoms
- Catalog UI is flooded with Indonesian-translated micro-dramas (*"Air Mata Lilin di Dalam Istana"*, *"Aku Melahirkan Sebuah Telur"*, *"Aku Lebih Baik Jadi Pembantu..."*).
- If default catalog sorting is alphabetical (`A-Z`), dracin dominate page 1 because of common Indonesian translated prefixes (*Aku...*, *Anak...*, *Angin...*), pushing Japanese romaji anime to later pages.

### Root-Cause Fingerprint
- **Donghua / Anime:** Metadata always includes genres in `style_list` or `styles` (e.g. `['Adaptasi novel', 'Berjuang']`).
- **Dracin / Short Drama:** Bstation consistently leaves `style_list: []` (empty array) and `styles: ""` (empty string).

## 3. Architecture: Separate Harvesting & Multi-Select Content Type Filter

1. **Deterministic Type Tagging:**
   When requesting `season_type='1,4'` in a single call, Bstation cards omit the `season_type` field. To allow user filtering between Anime and Donghua, harvest `season_type=1` and `season_type=4` in separate passes and stamp `'type': 'anime'` vs `'type': 'donghua'` on each item.
2. **Empty Style Nuance:**
   While the vast majority (169/170) of items without `style_list` are live-action micro-dramas, a tiny handful of 3D sci-fi animations (e.g. *The Age Of Cosmos Exploration*, season_id `2101898`) also lack styles. If keeping Donghua complete, classify all `season_type=4` as `donghua` and let users choose whether to browse Anime-only or Donghua.
3. **Multi-Select Filter API Contract:**
   Expose `?type=all|anime|donghua|anime,donghua` on `/api/catalog` and return `type_counts: {"all": 332, "anime": 50, "donghua": 282}` in the root response.
4. **UI Pattern — Multi-Select Toggle Pills with Zero-Selection Guard:**
   Provide toggle pills `[ Anime (50) ]` and `[ Donghua (282) ]`. If a user clicks the lone active pill to deselect it, auto-revert to both active (`all`) so the catalog view never gets stranded on an empty void.
5. **Default Sorting & Search Fallback:**
   Avoid raw alphabetical title sort (`A-Z`) across the unfiltered combined catalog, as Indonesian translated drama titles (*Aku...*, *Anak...*) flood page 1. Major licensed Japanese anime (*Naruto*, *Boruto*, etc.) not present in `items_v2` must be queried via `/intl/gateway/web/v2/search_v2`.

## 4. Bstation Catalog Size Disparity: Why Only 50 Anime on Web vs Mobile/Search

### The "50 Anime Limit" Phenomenon
Users frequently ask: *"Why are there only 50 anime in the catalog?"*
This is **not a backend bug**; it is an upstream architectural quirk of Bstation:
1. **Public Web Category Index is Artificially Capped:**
   Bstation's web category endpoint (`platform=web`) caps `season_type=1` at exactly 50 titles (1 page of 50 items; page 2 returns `null`).
2. **Mobile/Android Platform Expansion (78 Titles):**
   Querying with `platform=android` or `platform=tv` unlocks 78 anime titles (+28 major titles including *Demon Slayer: Swordsmith Village Arc*, *BLEACH*, *Tonikaku Kawaii S2*, *Black Summoner*, *Spy Classroom*, *Bleach Movie 1–4*, *Bokutachi no Remake*, etc.).
3. **Major Franchise "Search-Only" Policy:**
   Bstation hides massive licensed shonen franchises (*Naruto*, *Boruto*, *Attack on Titan*, *Jujutsu Kaisen*, *One Piece*, *Mushoku Tensei*) from the category browse index entirely. They are only retrievable via Search API (`/intl/gateway/web/v2/search_v2?keyword=...&platform=tv`).
4. **Recommended Expansion Strategy:**
   - Use `platform=android` in `build_full_catalog()` to immediately expand baseline anime from 50 to 78 titles.
   - Seed popular search keywords (*Naruto*, *One Piece*, *Jujutsu Kaisen*, *Chainsaw Man*, *Demon Slayer*, *Tensura*) into a background discovery harvester to merge search-only OGV anime into the catalog store.

## 5. Bstation UI Taxonomy Misconception (Anime vs Donghua)

On official `bilibili.tv/id/category`, the primary category tab is titled **"Anime"** and contains **all 332 animation titles** (both Japanese Anime and Chinese Donghua).
Under that category, Bstation provides a secondary **"Daerah"** (Region) filter:
- `SEMUA` = 332 titles (Default view seen by end users).
- `Jepang` = 47–50 titles (Japanese studios).
- `China` = 282 titles (Chinese studios / Donghua).

When building clone/derivative streaming frontends:
- Setting the default tab or filter to "Anime Only" (meaning strictly Japanese `season_type=1`) causes users to perceive 85% of titles as "missing".
- Always keep the default state at `all` (332 titles) and frame the filter as Region/Type selection (`Semua Animasi`, `Jepang`, `Donghua`).

## 6. Frontend Scroll & Pagination Ergonomics: Infinite Scroll vs Manual Clicks

### The "Bisa di Scroll" Expectation
When users browse streaming catalogs (such as Bstation, Netflix, or YouTube), they instinctively expect **seamless infinite scrolling** (content continuously appends as they scroll down the viewport).

### Common Pitfalls & Traps:
1. **Manual "Muat Lebih Banyak" Button Friction:**
   Requiring users to manually click a button to load the next 24 items breaks browsing flow. If a user scrolls quickly to the bottom expecting auto-load, they perceive the catalog as artificially truncated or broken.
2. **Abrupt List Exhaustion on Narrow Filters:**
   When filtered to a small subset (e.g. 50 Japanese anime items with `pageSize=24`):
   - Page 1 loads 24 cards.
   - One scroll/click loads 24 cards (page 2, total 48).
   - A third scroll reveals only 2 cards and hits the end indicator ("Semua anime telah ditampilkan").
   - Users who know Bstation's web catalog can be scrolled through hundreds of titles will immediately complain that items are missing (*"gak cuma 50, itu bisa di-scroll!"*).

### Standard Implementation Pattern:
- **Default View:** Keep default view on the full unified catalog (332+ titles) so scrolling provides a deep, immersive browsing experience.
- **Automated Infinite Scroll via `IntersectionObserver`:**
  Instead of relying only on button clicks, place a sentinel element (`#katalog-sentinel` or `#katalog-end-indicator`) observed via `IntersectionObserver` with a `rootMargin: '400px'` threshold:
  ```javascript
  const observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && !cs.isLoading && cs.hasMore) {
      cs.page += 1;
      fetchAndRenderCatalog(false);
    }
  }, { rootMargin: '400px' });
  observer.observe(DOM.katalogSentinel);
  ```
- **Fallback Button:** Keep `#katalog-load-more-btn` visible only if JavaScript intersection observation is unassisted or fails, but auto-trigger on natural page scroll by default.

