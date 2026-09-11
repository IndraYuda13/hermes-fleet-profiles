---
name: bstation-ogv-streaming-engine
description: Use when building Bstation anime streaming catalogs & bots.
---

# Bstation (bilibili.tv) OGV Streaming Engine & Catalog Architecture

This skill captures architectural knowledge, upstream API behavior, content taxonomy, and proven workflows when integrating or developing web streaming applications powered by Bstation (`bilibili.tv`).

## 1. Bstation Content Taxonomy: OGV vs UGC vs Dracin
Bstation maintains distinct content categories that are frequently confused:
- **OGV (Official Generated Video):**
  - Serialized anime with structured `season_id`, individual `episode_id`s, official subtitles (ASS/JSON converted to WebVTT), and multiple resolution streams (360p up to VIP 1080p).
  - Web applications require OGV structure for multi-episode players.
- **UGC (User-Generated Content):**
  - Standalone video uploads created by users with `aid` / `bvid`.
  - The perception of "thousands of anime" on Bstation comes largely from UGC re-uploads, clips, and AMVs, rather than official OGV seasons.
- **Short Drama / Dracin (Live-Action Micro-Dramas):**
  - Bstation mixes hundreds of vertical/horizontal micro-dramas into the OGV database (`season_type=4`).
  - Key identifying hallmark: `styles: []` and `style_list: []` are empty, with origin `Chinese Mainland`.

## 2. Upstream Category Harvesting (`items_v2`)
The official category index endpoint is:
`https://api.bilibili.tv/intl/gateway/web/v2/ogv/index/items_v2`

### Regional & Platform Limits:
- **`platform='web'`:**
  - Artificially truncates Japanese anime (`season_type=1` or `area_id=2`) to exactly **50 titles** (`total=50`, `has_next=false`).
- **`platform='android'`:**
  - Expands `season_type=1` to **78+ titles** (unlocking titles like *Demon Slayer: Swordsmith Village Arc*, *BLEACH* series & movies, *Tonikaku Kawaii*, *Spy Classroom*, etc.).
- **Donghua (`season_type=4` or `area_id=1`):**
  - Returns **282 titles** across both web and mobile platforms.
  - Combined `platform='android'` harvest yields **360+ unique titles**.

## 3. Unlisted Anime & Deep Search Discovery
Major licensed anime (e.g. *Naruto* `sid: 1005144`, *Naruto Shippuden* `sid: 1005195`, *Boruto* `sid: 1005426`) are often unlisted from the `items_v2` category index.
- To harvest beyond the 360 category titles, implement a seed crawler using:
  `https://api.bilibili.tv/intl/gateway/web/v2/search_v2?keyword={query}&platform=tv&s_locale=id_ID`
- Filter modules where `module.get('type') == 'ogv'` and extract `season_id`.
- Store discovered seasons in a local SQLite database for persistent catalog expansion.

## 4. Seamless Infinite Scroll Implementation
Do not force users to click a manual "Load More" button for large catalogs:
- Use `IntersectionObserver` on a sentinel wrapper element placed directly below the poster grid (`rootMargin: '300px 0px 300px 0px'`).
- Auto-invoke `fetchAndRenderCatalog(false)` whenever the sentinel enters view while `!isLoading && hasMore`.
- Provide a throttled `window.addEventListener('scroll', ...)` fallback (150ms throttle) in case `IntersectionObserver` is delayed.
- Ensure strict deduplication by `season_id` using a `Set` before appending new cards to the DOM.
- Display a dedicated micro-spinner while fetching and a clear end indicator when `hasMore` is false.
