# Bstation Streaming Pipeline Reference

Knowledge bank and troubleshooting notes for Bstation/yt-dlp streaming and web architecture.

## 1. Search Module Architecture
- `ogv_subject`: Top-level franchise wrapper. Example: Querying `naruto` returns `modules[type='ogv_subject'].items[0].seasons` which contains `Naruto` (ID: 1005144), `Naruto Shippuden` (ID: 1005195), and `Boruto` (ID: 1005426). Without parsing `ogv_subject`, major franchise searches fail silently.
- `ogv`: Standalone anime titles with direct `season_id`.
- `ugc`: User Generated Content. Must be filtered out to maintain pure official anime catalog.

## 2. Fast Seeking Implementation
Fragmented MP4 live streams cannot seek without offset requests.
- Endpoint: `/api/stream/{season_id}/{episode_id}?t={seconds}`
- FFmpeg Command:
  ```bash
  ffmpeg -headers "$HEADERS" -ss $SEEK_SEC -i "$VIDEO_URL" \
         -headers "$HEADERS" -ss $SEEK_SEC -i "$AUDIO_URL" \
         -c copy -movflags frag_keyframe+empty_moov+default_base_moof -f mp4 pipe:1
  ```
- Client State Tracking:
  - `seekOffset = targetSeconds`
  - `displayedTime = seekOffset + video.currentTime`

## 3. Dynamic Subtitle Offset & AV Sync Pitfall & Fix
- **Problem:** Reloading video `src` with `?t=X` causes `video.currentTime` to be `0.0s`. WebVTT files have absolute timestamps (e.g. `05:20.000`). The browser compares `currentTime` (starting at 0) against cues at 5m+, rendering zero subtitles.
- **Backend Fix:** Implement `shift_webvtt(vtt_text, offset_sec)` in Python:
  ```python
  def shift_webvtt(vtt_text: str, offset_sec: float) -> str:
      if offset_sec <= 0: return vtt_text
      # parse cues, start = max(0.0, start - offset_sec), end = max(0.0, end - offset_sec)
      # drop cues where end <= offset_sec
  ```
- **Frontend Fix:** In `performSeekTo(targetSeconds)`, re-anchor `<track>` elements with `&offset=${state.seekOffsetSeconds}`.
- **FFmpeg AV Sync:** Add `-avoid_negative_ts make_zero` so initial video and audio packets align without negative timestamps.

## 4. Mobile HTML5 Video Fullscreen & Touch Viewport
- **iOS Safari / Android Fallback:**
  ```javascript
  function toggleFullscreen(container, video) {
    if (document.fullscreenElement || document.webkitFullscreenElement) {
      if (document.exitFullscreen) document.exitFullscreen();
      else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
    } else {
      if (container.requestFullscreen) {
        container.requestFullscreen().catch(() => {
          if (video.webkitEnterFullscreen) video.webkitEnterFullscreen();
        });
      } else if (video.webkitEnterFullscreen) {
        video.webkitEnterFullscreen();
      }
    }
  }
  ```
- **Viewport Containment:**
  - `max-width: 100vw; overflow-x: hidden;` on body and video wrappers.
  - Controls overlay: `pointer-events: none` on inactive HUD, `pointer-events: auto` on interactive buttons.
  - Buffering overlays (`.player-spinner`): `pointer-events: none;` to avoid blocking scrubber touches during load.
  - Minimum touch target: `48x48px`.
  - Bottom-sheet drawer for subtitle and speed selection on `<640px` screens to prevent off-screen clipping.
  - Shelf headers on mobile: ensure `.shelf-title-group` has `flex-wrap: wrap` and `.shelf-counter` has `flex-shrink: 0; white-space: nowrap;` so badge counts like "39 Judul" do not break or collide with slider arrows.
  - Mobile double-tap gesture zones: left 40% for seek -10s, right 40% for seek +10s.

## 5. Bstation API Endpoint Availability (Tested Sep 2026)
- **Working endpoints:**
  - `GET /intl/gateway/web/v2/search_v2` — Search with keyword, returns `modules[]` with `ogv_subject`, `ogv`, `ugc` types
  - `GET /intl/gateway/web/v2/ogv/timeline` — Seasonal release schedule, returns `items[]` per day with `cards[].season_id`
  - `GET /intl/gateway/web/v2/ogv/play/season_info` — Season metadata (title, synopsis, cover, rating)
  - `GET /intl/gateway/web/v2/ogv/play/episodes` — Episode list per season
  - `GET /intl/gateway/web/v2/subtitle` — Subtitle data
- **404 / Non-existent endpoints (all tested, all 404):**
  - `/ogv/index`, `/ogv/index/list`, `/ogv/index_v2`, `/ogv/index/params`
  - `/ogv/index/condition`, `/ogv/index/result`
  - `/ogv/filter`, `/ogv/filter/condition`, `/ogv/filter/result`
  - `/ogv/all`, `/ogv/catalog`, `/ogv/view`, `/ogv/discover`
  - `/ogv/genre`, `/ogv/rank`, `/ogv/recommend`
  - `/ogv/home`, `/ogv/tab`, `/ogv/page`
  - `/channel/region`, `/channel/mine`, `/channel/list`
  - `/home/feed`
- **Implication:** There is NO browse/index API for Bstation OGV content. Full catalog must be built via broad search aggregation (see SKILL.md §16).
- **Bstation web page (`bilibili.tv/id/anime`):** Uses Vite SSR (not Next.js — no `__NEXT_DATA__`), JS bundles from `p.bstarstatic.com/fe-static/bstar-web-new/`. No API URLs embedded in page source.
- **Proxy requirement:** API calls from backend must go through regional proxy (e.g., Surfshark SOCKS5 Indonesia) for OGV content. Direct requests from non-SEA IPs return empty/UGC-only results or connection resets.

## 6. Defensive JSON Parsing for Null Collections (`cards: null` Trap)
- Upstream Bstation JSON occasionally returns `"cards": null` or `"items": null` when no scheduled releases exist for a given timeline date or search category.
- **Python `.get()` Trap:**
  ```python
  # BUG: Returns None when "cards" exists with value null!
  cards = day.get('cards', [])
  for card in cards:  # Crashes with TypeError: 'NoneType' object is not iterable (HTTP 500)
  ```
- **Defensive Invariant:**
  ```python
  for card in (day.get('cards') or []):
      ...
  ```
  Apply `(x.get(...) or [])` on all upstream list collections (`cards`, `items`, `modules`, `styles`, `sections`, `subtitles`).

## 7. SEA Proxy Node Geo-Licensing & WAF Behaviors
- **Singapore (`SG`, e.g. port 32001):**
  - Upstream Bstation frequently blacks out OGV licensing on Singapore datacenter/VPN IP blocks.
  - Sits at 0 official anime returned for search and timeline (all days return `cards: null`), while UGC video clips still return.
- **Thailand (`TH`, port 32007):**
  - Full OGV licensing (80+ seasonal cards, Naruto/One Piece franchise hubs).
  - Can occasionally encounter WAF rate limiting / anti-bot challenge (`HTTP 412 Precondition Failed` on `/search_v2`) during high-frequency sequential catalog builds.
- **Philippines (`PH`, port 32012):**
  - Highly resilient, clean SEA OGV licensing (60+ timeline cards, full anime catalog, working 1080p stream extraction via Akamai CDN).
  - Bypasses WAF 412 rate-limiting seen on Thailand IP blocks. Recommended as stable primary proxy egress for Bstation backend services.
- **Graceful Search Exception Handling:**
  - Never let `r.raise_for_status()` directly escape to top-level routes on search APIs.
  - Catch non-200 HTTP responses (like 412 or 429), log warning, and return `[]` to prevent cascading 500 errors on web clients.
