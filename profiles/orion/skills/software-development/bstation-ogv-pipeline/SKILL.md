---
name: bstation-ogv-pipeline
description: Use when building or querying Bstation OGV anime catalogs.
---

# Bstation / Bilibili.tv OGV Catalog Architecture & Streaming Engine

Comprehensive operational guide and architecture standard for harvesting official anime catalogs, filtering short-drama spam, seed discovery of hidden franchises, and zero-reencode fragmented MP4 media streaming from Bstation (`bilibili.tv`).

## 1. Upstream Taxonomy & Filtering (Anime vs Donghua vs Dracin)
- **Unified Catalog Model:** On Bstation web (`bilibili.tv/id/category`), Japanese anime (`season_type=1`) and Chinese Donghua (`season_type=4`) are unified under category "Anime" (332–360+ titles). Default catalog views (`type=all`) must combine both streams. Partitioning into Japanese-only by default causes users to perceive 85% of the catalog as missing.
- **Dracin (Short Drama) Infiltration & Fingerprint:**
  - Upstream injects 1,400+ live-action micro-dramas into `season_type=4` (*Aku Melahirkan Sebuah Telur*, *Cahaya Bulan CEO Fu*).
  - *Donghua / Anime:* Metadata includes genres in `style_list` or `styles` (e.g. `['Adaptasi novel', 'Berjuang']`).
  - *Dracin / Micro-drama:* Bstation consistently leaves `style_list: []` (empty array) and `styles: ""` (empty string). Classify and filter dracin out deterministically.
- **A-Z Sorting Trap:** Avoid raw alphabetical sorting (`A-Z`) across unfiltered catalogs; Indonesian translated micro-drama titles (*Aku...*, *Anak...*, *Angin...*) flood page 1 and push Japanese romaji anime to later pages.
- **Deterministic Type Tagging:**
  - Querying `season_type=1,4` in a single request omits `season_type` on returned cards. Harvest `season_type=1` and `season_type=4` in separate passes and stamp `'type': 'anime'` vs `'type': 'donghua'`.
  - **Zero-Selection Guard:** In UI toggle pills (`[ Anime (50) ]`, `[ Donghua (282) ]`), auto-revert to both active (`all`) if user deselects the lone active pill so view is never empty.

## 2. Platform Parameter Harvesting Expansion (`web` vs `android`)
Endpoint: `https://api.bilibili.tv/intl/gateway/web/v2/ogv/index/items_v2`
- Passing `platform='web'` artificially truncates Japanese anime (`season_type=1`) to exactly **50 titles**.
- Passing `platform='android'` unlocks **78 titles** (+28 major titles including *Demon Slayer*, *BLEACH* movies, *Tonikaku Kawaii S2*, *Black Summoner*).
- Combined `platform='android'` harvest with Donghua (`season_type=4`, 282 titles) expands the baseline official category catalog to **360 titles**. Always pass `platform='android'`.

## 3. Unlisted Blockbuster Franchise Discovery & The "Thousands of Anime" Trap
- **The OGV Hidden Library:** Bstation intentionally omits major licensed franchises from `ogv/index/items_v2`. These titles exist as valid streamable OGV seasons (`season_type_enum=1`), but can only be accessed via direct search or specific `season_id` endpoints.
- **Top Blockbuster Seeds Discovered:**
  - *One Piece* (sid `37976` - 1200+ eps + movies `37130`, `37114`, `1017411`, `37120`, `37118`)
  - *Naruto* (`1005144`), *Naruto Shippuden* (`1005195` - 508 eps), *Boruto* (`1005426`)
  - *Jujutsu Kaisen* S1 (`37738`), S2 (`2084055`), *The Culling Game* (`2288197`)
  - *Attack on Titan* S1 (`35044`), S2 (`34521`), S3 P1/P2 (`34611`, `34539`), Final Season (`36297`, `1042594`)
  - *Demon Slayer / Kimetsu no Yaiba* S1 (`34580`), Mugen Train (`1023002`), Entertainment District (`1033760`), Swordsmith Village (`2079053`), Hashira Geiko (`2104174`)
  - *SPY x FAMILY* S1 (`1048837`), S2 (`2090049`), *Frieren* (`2090295`), *Oshi no Ko* (`2080019`), *Solo Leveling* (`2097863`), *Chainsaw Man* (`2069687`), *Mushoku Tensei* (`36690`), *Hunter x Hunter 2011* (`37603`), *Haikyuu!!* S1-S4 (`34475`..`34634`), *BLEACH* (`35278` + TYBW `2069614`..`2414568`), *Tensura* (`34510`, `36689`), *KonoSuba* (`34558`..`2106744`), *Re:Zero* (`35753`..`2114391`), *One Punch Man* (`36279`), *JoJo* (`34791`), *Dr. Stone* (`34604`).
- **Discovery Mechanism:** Query `/intl/gateway/web/v2/search_v2?keyword={query}&platform=tv&s_locale=id_ID` through regional proxy (`socks5://127.0.0.1:32012`). Parse modules where `type` is `ogv` or `ogv_subject` (`items[].seasons[]`), and persist seeds in `backend/anime_seeds.json` or SQLite. Combining category items (360) + seed crawler yields **547+ titles (265+ Japanese anime)**.
- **"Thousands of Anime" User Perception vs Reality:**
  - Users expect "thousands of anime" because Bstation indexes 1,448+ live-action micro-dramas (`season_type=5`) and millions of user-generated clips (UGC).
  - Official licensed OGV anime in Southeast Asia genuinely caps at ~332–360 active titles. Do not attempt to ingest unpartitioned UGC or dracin to inflate numbers; instead, add missing licensed titles via seed harvester.

## 4. Frontend Infinite Scroll & Scrubber Ergonomics
- **IntersectionObserver Continuous Scroll:** Web users expect seamless scrolling without manual "Muat Lebih Banyak" button friction.
  ```javascript
  const observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && !state.isLoading && state.hasMore) {
      state.page += 1;
      fetchAndRenderCatalog(false);
    }
  }, { rootMargin: '300px 0px 300px 0px' });
  observer.observe(DOM.sentinel);
  ```
- **Deduplication:** Always deduplicate incoming cards by `season_id` using a `Set` before appending to state/DOM to avoid duplicate cards on rapid scroll triggers.
- **Scrubber Finite Duration Lock:** Chunked fragmented MP4 pipes return `video.duration === Infinity` or collapse to initial chunk duration (5s–15s). Always lock duration using backend metadata (`state.lockedDuration`) and validate with `Number.isFinite(video.duration) && video.duration > 600`.

## 5. Metadata Endpoints & Split Stream Handling
- `/ogv/play/season_info?season_id=...` returns ONLY season metadata (title, synopsis, covers).
- Episode list MUST be fetched separately via `/ogv/play/episodes?season_id=...` (`sections[].episodes`).
- Remux demuxed video and audio tracks on the fly with zero transcoding:
  `ffmpeg -i $VIDEO_URL -i $AUDIO_URL -c copy -movflags frag_keyframe+empty_moov+default_base_moof -f mp4 pipe:1`
