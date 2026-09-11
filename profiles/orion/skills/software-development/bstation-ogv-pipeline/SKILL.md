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
- **Deterministic Type Tagging:**
  - Querying `season_type=1,4` in a single request omits `season_type` on returned cards. Harvest `season_type=1` and `season_type=4` in separate passes and stamp `'type': 'anime'` vs `'type': 'donghua'`.
  - **Zero-Selection Guard:** In UI toggle pills (`[ Anime (50) ]`, `[ Donghua (282) ]`), auto-revert to both active (`all`) if user deselects the lone active pill.

## 2. Platform Parameter Harvesting Expansion (`web` vs `android`)
Endpoint: `https://api.bilibili.tv/intl/gateway/web/v2/ogv/index/items_v2`
- Passing `platform='web'` artificially truncates Japanese anime (`season_type=1`) to exactly **50 titles**.
- Passing `platform='android'` unlocks **78 titles** (+28 major titles including *Demon Slayer*, *BLEACH* movies, *Tonikaku Kawaii S2*, *Black Summoner*).
- Combined `platform='android'` harvest with Donghua (`season_type=4`, 282 titles) expands the baseline official category catalog to **360 titles**. Always pass `platform='android'`.

## 3. Unlisted Blockbuster Franchise Discovery (Search API Seed Crawler)
- Bstation intentionally hides major licensed franchises (*Naruto*, *One Piece*, *Jujutsu Kaisen*, *Attack on Titan*, *Chainsaw Man*, *Demon Slayer*, *BLEACH TYBW*, *Solo Leveling*) from category indices (`items_v2`).
- Discover unlisted titles via:
  `/intl/gateway/web/v2/search_v2?keyword={query}&platform=tv&s_locale=id_ID`
  through local regional proxy (`socks5://127.0.0.1:32012`).
- Filter modules where `module.type` is `ogv` or `ogv_subject` (parse `items[].seasons[]`). Persist discovered `season_id`s in `backend/anime_seeds.json` or SQLite. Combining category items (360) + seed crawler yields **547+ titles (265+ Japanese anime)**.

## 4. Frontend Infinite Scroll & Scrubber Ergonomics
- **IntersectionObserver Sentinel:** Web users expect continuous scrolling. Place a sentinel element observed via `IntersectionObserver` (`rootMargin: '300px 0px'`). Auto-fetch next page when visible while `!isLoading && hasMore`.
- **Deduplication:** Always deduplicate incoming cards by `season_id` using a `Set` before appending to state/DOM to avoid duplicate cards on rapid scroll triggers.
- **Scrubber Finite Duration Lock:** Chunked fragmented MP4 pipes return `video.duration === Infinity` or collapse to initial chunk duration (5s–15s). Always lock duration using backend metadata (`state.lockedDuration`) and validate with `Number.isFinite(video.duration) && video.duration > 600`.

## 5. Metadata Endpoints & Split Stream Handling
- `/ogv/play/season_info?season_id=...` returns ONLY season metadata (title, synopsis, covers).
- Episode list MUST be fetched separately via `/ogv/play/episodes?season_id=...` (`sections[].episodes`).
- Remux demuxed video and audio tracks on the fly with zero transcoding:
  `ffmpeg -i $VIDEO_URL -i $AUDIO_URL -c copy -movflags frag_keyframe+empty_moov+default_base_moof -f mp4 pipe:1`
