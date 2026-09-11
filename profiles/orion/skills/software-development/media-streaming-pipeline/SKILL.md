---
name: media-streaming-pipeline
description: Build low-latency media streaming and remuxing pipelines.
---

# Media Streaming Pipeline

Workflows and patterns for building media streaming architectures, handling demuxed adaptive streams, zero-reencode live remuxing, proxy egress boundaries, and WebVTT subtitle conversions.

## 1. Split Demuxed Stream Handling
Modern video platforms (Bilibili/Bstation, YouTube, DASH streams) frequently deliver audio and video in separate streams:
- Video-only tracks (AVC/H.264, HEVC/H.265).
- Audio-only tracks (AAC, Opus).

### Instant Remuxing via FFmpeg Copy (`-c copy`)
Do not download the entire episode to disk or transcode with re-encoding (`-c:v libx264`), which spikes CPU and introduces multi-minute delay before playback starts.
Instead, use FFmpeg stream copy with fragmented MP4 flags to stream directly into HTTP stdout pipe:
```bash
ffmpeg -headers "Referer: https://target.com/\r\nUser-Agent: Mozilla/5.0\r\n" -i "$VIDEO_STREAM_URL" \
       -headers "Referer: https://target.com/\r\nUser-Agent: Mozilla/5.0\r\n" -i "$AUDIO_STREAM_URL" \
       -c:v copy -c:a copy \
       -movflags frag_keyframe+empty_moov+default_base_moof \
       -f mp4 pipe:1
```
- Starts delivery in ~1-2 seconds.
- Near 0% CPU consumption.
- Directly playable in native HTML5 `<video>` elements.

## 2. CDN Egress & Proxy Scoping
- **Metadata/Extraction Phase:** When regional geo-restrictions exist (e.g. SEA/Indonesia for Bstation), the initial API handshake and `yt-dlp` metadata resolution MUST route through regional residential/VPN proxies (e.g. SOCKS5 node).
- **Proxy Node Geo-Licensing Discrepancies (SG vs TH/PH):**
  - Upstream anime licensors (Bstation/Bilibili OGV) impose different catalog availability per country IP even within Southeast Asia.
  - Singapore (`SG`) proxy nodes frequently suffer strict OGV licensing blackouts: `/search_v2` returns only `ugc` modules (0 official anime), and `/ogv/timeline` returns `null` cards across all days, leading to an apparently completely empty website catalog.
  - Thailand (`TH`, e.g. port 32007) and Philippines (`PH`, e.g. port 32012) nodes retain full licensed OGV catalogs (80+ active seasonal anime cards, official franchise modules like Naruto/One Piece/Demon Slayer, and working Akamai UPOS CDN stream extraction). Note: Thailand may occasionally trigger WAF HTTP 412 during high-volume query bursts; Philippines (port 32012) remains stable and unthrottled.
  - When catalog or search suddenly yields 0 anime, test upstream OGV availability across multiple proxy egress nodes immediately before assuming API failure.
  - In code, protect search endpoints against WAF/upstream non-200 spikes by catching non-200 status codes gracefully rather than letting `r.raise_for_status()` trigger unhandled HTTP 500 errors.
- **Video Delivery Phase:** Signed CDN URLs often authorize directly based on URL token parameters and HTTP `Referer` headers. Test direct CDN fetching (`requests.head(url, headers={'Referer': ...})`) — if HTTP 200 is returned, CDN bandwidth can bypass the proxy node entirely, preventing proxy bandwidth bottlenecks.

## 3. WebVTT Subtitle Conversion for HTML5 `<track>`
Browsers only natively render WebVTT (`.vtt`) in `<track kind="subtitles">`. Platforms often return SubRip (`.srt`) or ASS.
Convert SRT to WebVTT on-the-fly:
```python
import re

def srt_to_webvtt(srt_text: str) -> str:
    # Normalize line endings
    text = srt_text.replace('\r\n', '\n').replace('\r', '\n')
    # WebVTT requires '.' instead of ',' for millisecond separators
    text = re.sub(r'(\d{2}:\d{2}:\d{2}),(\d{3})', r'\1.\2', text)
    return "WEBVTT\n\n" + text.strip() + "\n"
```
Serve this with `Content-Type: text/vtt; charset=utf-8` and CORS header `Access-Control-Allow-Origin: *`.

## 4. FastAPI StreamingResponse Pipe Integration
When streaming FFmpeg stdout via FastAPI, yield chunks using `StreamingResponse`:
```python
import subprocess
from fastapi.responses import StreamingResponse

def stream_generator(video_url: str, audio_url: str):
    cmd = [
        "ffmpeg", "-re",
        "-headers", "Referer: https://www.bilibili.tv/\r\nUser-Agent: Mozilla/5.0\r\n",
        "-i", video_url,
        "-headers", "Referer: https://www.bilibili.tv/\r\nUser-Agent: Mozilla/5.0\r\n",
        "-i", audio_url,
        "-c:v", "copy",
        "-c:a", "copy",
        "-movflags", "frag_keyframe+empty_moov+default_base_moof",
        "-f", "mp4",
        "pipe:1"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10**6)
    try:
        while True:
            chunk = proc.stdout.read(64 * 1024)
            if not chunk:
                break
            yield chunk
    finally:
        proc.kill()
        proc.wait()

@app.get("/api/stream")
def get_stream(v: str, a: str):
    return StreamingResponse(
        stream_generator(v, a),
        media_type="video/mp4",
        headers={"Accept-Ranges": "bytes", "Content-Disposition": "inline"}
    )
```
- Ensure subprocess termination (`proc.kill()`) is guaranteed inside `finally` block to prevent orphaned FFmpeg processes on client disconnect.
- **Client Disconnect Lifecycle Guard:** In asynchronous FastAPI (`async def`), check `await request.is_disconnected()` in the generator loop. If true, break immediately and terminate/kill the process so FFmpeg does not linger in memory.
- **FFmpeg Stream Resilience:** Add `-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5` to FFmpeg input parameters to prevent upstream CDN drops or transient socket timeouts from terminating the stream mid-episode.

## 5. Bstation API v2 Metadata Nuances
- `season_info` endpoint (`/ogv/play/season_info?season_id=...`) only returns the `season` metadata object (title, synopsis, covers, views), NOT the episode list.
- Episode list MUST be fetched separately via `/ogv/play/episodes?season_id=...`, which returns a `sections` array containing episode objects (`episode_id`, `title_display`, `short_title_display`, `cover`).
- Subtitles are requested via `yt-dlp --write-subs --skip-download`, producing `.srt` files that are dynamically converted to WebVTT before delivery.

## 6. Fast Seeking Engine on Fragmented MP4 Streams
Fragmented MP4 pipes from standard live stdout do not natively support browser seek requests without byte-range table headers.
To enable instantaneous seeking to arbitrary timestamps (e.g. 5m, 12m):
- Accept a query parameter `?t=SECONDS` on the streaming endpoint.
- Inject `-ss <SECONDS>` before `-i` for both video and audio input streams in FFmpeg:
  ```bash
  ffmpeg -headers "..." -ss 180 -i "$VIDEO_URL" \
         -headers "..." -ss 180 -i "$AUDIO_URL" \
         -c copy -movflags frag_keyframe+empty_moov+default_base_moof -f mp4 pipe:1
  ```
- Because FFmpeg resets output stream Presentation Time Stamps (PTS) to 0 at the seek offset, frontend timeline players must track `seekOffset = t` and calculate `displayedTime = seekOffset + video.currentTime` while maintaining true overall duration.

### Pitfall: `Infinity` Duration on Chunked Streaming Pipes & Scrubber Freeze
- **Akar Masalah:** Chunked transfer encoding / remuxed pipe tanpa `Content-Length` membuat browser HTML5 video menganggap stream sebagai siaran langsung (`video.duration === Infinity`).
- **The JavaScript `Infinity` Trap:** Validasi naif seperti `if (!isNaN(video.duration) && video.duration > 10)` mengevaluasi `Infinity > 10` sebagai `true`! Dampaknya:
  - Scrubber progress `(currentTime / Infinity) * 100` selalu menghasilkan `0%` (scrubber macet di detik 0).
  - Dragging scrubber menghitung `pos * Infinity` = `Infinity`, memicu seek ke `?t=Infinity` yang menyebabkan backend FFmpeg hang/crash.
  - UI player terjebak dalam status buffering / live stream loading terus-menerus.
- **Solusi:**
  - Wajib gunakan `Number.isFinite(video.duration)`.
  - Simpan durasi eksak dari metadata API backend (misal `episode.duration` dalam detik). Jika `video.duration` bernilai `Infinity` atau tidak finite, fallback ke durasi eksak metadata tersebut.

### Pitfall: Fragmented MP4 Initial Chunk Duration Collapse (The 5s–15s Glitch)
- **Akar Masalah:**
  - Saat browser HTML5 `<video>` memutar fragmented MP4 (`-movflags frag_keyframe+empty_moov+default_base_moof`) via HTTP chunked stream, browser membaca header fragment awal (`moof`/`traf`).
  - Browser kemudian menyetel `video.duration` bernilai finite kecil sesuai durasi chunk pertama (biasanya hanya 5 hingga 15 detik), BUKAN durasi total video.
- **The Finite Glitch Trap:**
  - Jika kode frontend hanya mengecek `if (Number.isFinite(video.duration) && video.duration > 10)`, durasi chunk 15 detik ini akan lolos validasi dan menimpa durasi metadata!
  - **Dampak Fatal:**
    1. Dalam 15 detik pertama pemutaran, scrubber progress `(currentTime / 15s) * 100` langsung meluncur ke 100% (efek visual bar putih berjalan cepat ke kanan seolah loading terus-menerus).
    2. Waktu durasi di player mengecil menjadi `00:10` atau `00:15`.
    3. User tidak bisa melakukan seeking/skip ke menit berapapun saat video sedang jalan, karena scrubber hanya mengalikan posisi klik dengan 15 detik.
- **Solusi (Duration Lock Engine & Scrubber Hitbox):**
  - **Backend Stream Meta Duration Provider:** Endpoint `/api/stream/meta/{season_id}/{episode_id}` mengembalikan durasi riil episode (diperoleh via `ffprobe` direct CDN URL atau timestamp cue terakhir dari WebVTT subtitles, misal 1435.02 detik / 23:55).
  - **Frontend Locked Duration State:** Frontend menyimpan `state.lockedDuration` dari metadata episode dan stream meta.
  - **Duration Hierarchy Precedence:**
    ```javascript
    function getEffectiveDuration() {
      // 1. Prioritas tertinggi: durasi locked finite dari backend / meta (>300s)
      if (state.lockedDuration && Number.isFinite(state.lockedDuration) && state.lockedDuration > 300) {
        return state.lockedDuration;
      }
      if (state.currentEpisodeDuration && Number.isFinite(state.currentEpisodeDuration) && state.currentEpisodeDuration > 300) {
        return state.currentEpisodeDuration;
      }
      // 2. Video element duration HANYA dipercaya jika finite dan > 600s (menolak fragment chunk 5s..15s)
      if (video && Number.isFinite(video.duration) && video.duration > 600) {
        return video.duration;
      }
      // 3. Fallback durasi standar anime 24 menit
      return 1440;
    }
    ```
  - **Scrubber Touch Hitbox:** Besarkan wadah sentuh scrubber bar (`.scrubber-container`) minimal 36px (`height: 36px; touch-action: none; -webkit-tap-highlight-color: transparent;`) agar gesture sentuh di HP tidak meleset saat video sedang berputar.

## 7. YouTube Upload OAuth Scopes & Privacy Lifecycle
- **The `youtube.upload` Scope Limitation**:
  - When generating Google OAuth authorization URLs, developers often request only `https://www.googleapis.com/auth/youtube.upload`.
  - **The Scopes Trap**: The `youtube.upload` scope permits *only* inserting new videos (`videos.insert`). It does **NOT** have permission to update video metadata or privacy status (`videos.update`), nor delete videos (`videos.delete`).
  - Attempting to update a video from public to private with only `youtube.upload` triggers:
    `HttpError 403: Request had insufficient authentication scopes. Insufficient Permission`.
  - **Required OAuth Scopes**: Always include both upload and management scopes in `SCOPES`:
    ```python
    SCOPES = [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube",  # Required for videos().update(part="status") and videos().delete()
    ]
    ```
- **Initial Upload Privacy Default Contract**:
  - Never default automated uploader scripts to `"privacyStatus": "public"`.
  - Automated pipelines must default to `"privacyStatus": "private"` (or `"unlisted"`) so the channel owner can review video quality, subtitles, and hook alignment in YouTube Studio before releasing to the public algorithm.

When video seeking is executed via `/api/stream?...?t=X`:
- **The Subtitle Offset Desync Pitfall:**
  - Because `video.currentTime` in HTML5 `<video>` restarts from `0.0s` on stream reload, standard WebVTT tracks with absolute timecodes (e.g. `00:05:10.000`) will fail to render cues matching the new playback position.
  - **Fix:** Subtitle endpoint MUST support dynamic offset shifting: `/api/subtitles/{season_id}/{episode_id}?lang={lang}&offset={seconds}`.
  - Server shifts all cue timestamps: `start = max(0.0, start - offset)`, `end = max(0.0, end - offset)`.
  - Drop all cues where `end <= offset`. Clamp any active cue spanning the offset to `0.000s`. Set `Cache-Control: no-cache` when `offset > 0`.
  - Frontend player must automatically re-request or adjust active textTrack cues with `&offset=${seekOffsetSeconds}` whenever a seek occurs.
- **The HTML5 `TextTrackList` Memory Leak & Ghost Double Subtitle Pitfall:**
  - Menghapus elemen `<track>` dari DOM via `trackEl.remove()` **TIDAK** menghapus track dari objek browser `HTMLMediaElement.textTracks`!
  - Spesifikasi HTML5 menetapkan bahwa objek `TextTrack` tetap hidup di internal browser sepanjang lifecycle elemen video.
  - Jika setiap seek meng-append `<track>` baru dengan parameter `?offset=...`, `video.textTracks` akan menumpuk track lama dan baru. Saat `tt.mode = 'showing'` dijalankan, browser menampilkan track lama dan track baru secara bersamaan, memicu **subtitle dobel multi-bahasa** (misal Indo + English tertimpa sekaligus).
  - **Solusi:**
    ```javascript
    // Purge seluruh textTrack internal browser sebelum mengaktifkan track baru
    for (let i = 0; i < video.textTracks.length; i++) {
      video.textTracks[i].mode = 'disabled';
    }
    // Set strictly 'showing' hanya pada track dengan srclang dan URL aktif saat ini
    ```
    Atau kelola track secara statis (1 track per bahasa) dan manipulasi teks cue / track source langsung tanpa menambah elemen track baru berulang kali.
- **FFmpeg AV Keyframe Alignment & Desync Prevention:**
  - Video stream copy snaps to the nearest preceding Keyframe (I-frame), while audio seeks to exact sample, risking a severe lip-sync drift (e.g. video showing frames from 295s while audio/subs are at 300s).
  - Use `-avoid_negative_ts make_zero` in FFmpeg to enforce clean timeline origin and prevent audio-video drift across seek boundaries.
  - In frontend, provide an explicit Audio/Video Sync Lock indicator (e.g. "Sinkronisasi Audio & Video...") on video `waiting`/`seeking` events until the media pipeline locks and fires `playing`.

## 8. Bstation Search & Catalog API Modules (UGC vs OGV)
- Bstation search API (`/search_v2`) separates content into modules:
  - `ogv_subject`: Major anime franchises (e.g. Naruto, Boruto, Bleach, Dragon Ball). Contains `items[].seasons[]` with individual anime titles and official `season_id`. **MUST be parsed** or franchise searches will return empty results.
  - `ogv`: Standalone official anime series with direct `season_id`.
  - `ugc`: User Generated Content (fan edits, clips, AMVs, reaction videos). **MUST be filtered out** when building official anime catalog/streaming platforms.
- **Defensive Parsing on Upstream Lists (`null` vs `[]`):**
  - The timeline API (`/ogv/timeline?platform=web&s_locale=id_ID`) returns day objects with scheduled anime cards.
  - When a day has no scheduled releases (or when a region has empty listings), upstream returns `"cards": null` instead of an empty list `[]`.
  - Python dictionary retrieval `day.get('cards', [])` **does NOT protect against `null`**, because key `'cards'` exists with value `None`, returning `None`. Iterating `for card in day.get('cards', []):` throws `TypeError: 'NoneType' object is not iterable` and crashes the endpoint with HTTP 500.
  - Similar traps occur on `styles`, `style_list`, `items`, and `modules` from upstream JSON.
  - **Invariant:** Always use defensive chaining `(day.get('cards') or [])`, `(res.get('data') or {}).get('modules') or []`, etc., across all upstream parsing loops.
- **Graceful Error Handling vs `raise_for_status()`:**
  - Upstream Bstation search APIs intermittently return HTTP 412 (Precondition Failed) or rate limits under burst queries.
  - Replace hard `r.raise_for_status()` in search endpoints with structured try-except blocks: log a warning and return empty/cached list instead of failing the request with unhandled HTTP 500.

## 9. Mobile HTML5 Video Player Ergonomics & Fullscreen
- **Mobile Fullscreen Fallback:** On mobile iOS Safari and Android WebKit, calling `requestFullscreen()` on a wrapping `div` container is frequently blocked by security/OS policies. Implement fallback cascading:
  ```javascript
  if (video.webkitEnterFullscreen) {
    video.webkitEnterFullscreen();
  } else if (container.requestFullscreen) {
    container.requestFullscreen();
  }
  ```
- **Mobile Touch Overlays & Viewport Leak:**
  - Control overlays must set `pointer-events: none` on inactive/hidden states and `pointer-events: auto` strictly on interactive buttons.
  - Buffering overlays (`.player-spinner`) must set `pointer-events: none;` so buffering states do not block touch gestures on underlying scrubber bars or control buttons.
  - Interactive touch targets must maintain minimum `48x48px` dimensions.
  - Use `max-width: 100vw; overflow-x: hidden;` on body and video wrappers to eliminate horizontal scrollbar leaks on small viewports (375px/390px).
  - Flyout menus (subtitles/speed) on mobile viewports (<640px) must be rendered as bottom-sheet modals anchored to the bottom edge rather than desktop absolute popups to prevent off-screen clipping.

## 10. Mobile Responsive Shelf Header & Counter Protection
- **The "Counter Badge Wrap" Pitfall (<640px):**
  - When header titles are lengthy (e.g. "Sedang Hangat Musim Ini"), flex headers with default `flex-wrap: nowrap` compress the badge counter (`.shelf-counter`), causing text like "39 Judul" to wrap awkwardly, get clipped, or collide with adjacent slider arrows (`.shelf-controls`).
  - **CSS Fix:**
    ```css
    .shelf-header { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
    .shelf-title-group { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; min-width: 0; flex: 1 1 auto; }
    .shelf-counter { flex-shrink: 0; white-space: nowrap; font-variant-numeric: tabular-nums; display: inline-flex; align-items: center; }
    ```
- **Mobile Double-Tap to Seek (±10s):**
  - Implement native mobile double-tap zones (left 40% = seek -10s, right 40% = seek +10s) with momentary ripple indicators to allow comfortable one-handed scrubbing on smartphones.

## 11. Production Diagnostics & Live Stream Audit Runbook
When verifying or troubleshooting a production media streaming deployment:
1. **Liveness & Workers:** Verify systemd unit and worker process tree (`systemctl status animestr-backend --no-pager`). Ensure Uvicorn workers and spawned FFmpeg remuxer instances are tracked cleanly in cgroups.
2. **API & Extraction Health:** Query the internal `/api/health` endpoint to verify VIP cookies readiness (`cookies_loaded: true`) and proxy egress availability.
3. **Active Pipeline Inspection:** Inspect recent systemd journal logs (`journalctl -u animestr-backend -n 30`) to audit real-time streaming operations:
   - Confirm dynamic subtitle offset shifts (`GET /api/subtitles/...?...&offset=...`).
   - Confirm FFmpeg remuxer spawn on seek (`Spawning FFmpeg remuxer ... seek=...`).
   - Verify client disconnect cleanup (`Client disconnected ... FFmpeg remuxer closed`) to ensure zero subprocess or file descriptor leaks.
4. **Proxy Egress:** Confirm local proxy container / SOCKS5 node is actively listening (`curl -s http://127.0.0.1:<PORT> -I` or `docker ps`).
5. **Edge & Cache-Control:** Check edge response headers (`curl -sI https://...`) to ensure live stream and dynamic subtitle endpoints bypass proxy/CDN caching (`Cache-Control: no-cache, no-store`).

## 12. Upcoming Anime Empty State UX vs System Errors & Dead Retry Button
- **The Empty Episode vs System Error Conflation:**
  - Upstream anime catalog APIs (e.g. Bstation/Bilibili OGV) frequently index officially announced or upcoming anime seasons (e.g. seasonal timeline cards) before their premiere date.
  - Calling `/api/episodes/{season_id}` for upcoming titles returns HTTP 200 with `episodes: []`.
  - **The Error Misdirection Trap:** Naive frontend code that treats `episodes.length === 0` by throwing an exception (`throw new Error('Tidak ada episode yang tersedia')`) triggers a generic system error banner ("Gagal memuat metadata / Aliran video sedang disiapkan"). Users perceive the website or player as broken.
  - **Upstream Dynamic Release Schedule Metadata:**
    - Bstation `/api/season/{season_id}` provides rich dynamic scheduling fields:
      - `player_time`: e.g. `"Starting: Sep 7, 2026"`
      - `player_date`: e.g. `"Sep 7, 2026"`
      - `first_ep_remind`: e.g. `"Sep 7, 2026  20:00"`
      - `update_pattern`: e.g. `"Update at 20:00 every Monday"`
      - `index_show`: e.g. `"Coming Soon"` or `"E1 Segera diperbarui"`
  - **Proper Upcoming Empty State Architecture:**
    - Check if `episodes.length === 0` before attempting playback.
    - Render a dedicated **Upcoming Anime State** (e.g., Calendar/Clock icon, "Segera Hadir / Belum Tayang", displaying dynamic schedule text).
    - Provide clear user actions: "Jelajahi Anime Lain" (route back to catalog) and "Cek Ketersediaan" (retry fetch with loading feedback).
- **The Dead Retry Button Pitfall (State Null NO-OP):**
  - If a player's retry handler depends on active episode state:
    ```javascript
    // BUG: If state.currentEpisodeId is null or state.episodesList is empty, this is a silent NO-OP!
    DOM.errorRetryBtn.onclick = () => {
      const ep = state.episodesList.find(e => e.episode_id === state.currentEpisodeId);
      if (ep) loadEpisode(ep);
    };
    ```
  - When errors occur before an episode is selected (e.g., initial catalog/metadata failure or 0 episodes), clicking "Coba Muat Ulang" does absolutely nothing. The user clicks repeatedly with zero visual feedback.
  - **Fix:** Guard the handler to fall back to a full view re-fetch (`navigateToWatch(state.currentSeasonId)`), resetting error banners and presenting an active loading spinner immediately upon click.

## 13. Hero Spotlight Data Synchronization & Carousel
- **The Hero Static Fallback Desync Trap:**
  - HTML template files often contain placeholder/fallback content for the hero section (e.g., Solo Leveling title, synopsis, and Japanese subtitle hardcoded in `index.html`).
  - If the JS `setupHero()` function only updates SOME fields (e.g., `heroTitle.textContent`) while leaving others (e.g., `heroSubtitle`, `heroSynopsis`) unchanged, the hero displays a Frankenstein mix: new anime's poster/title with old anime's subtitle and synopsis.
  - **Fix:** `setupHero()` must atomically update ALL hero fields (title, subtitle/Japanese name, synopsis, rating, status badge, genre badge, poster image, watch/episode buttons) from a single data source. Never leave any field dependent on static HTML fallback.
  - **Async Fallback for Missing Fields:** If the featured API response lacks `origin_name` or `description`, fetch `/api/season/{season_id}` asynchronously and fill those fields only if still empty (guard with `if (!DOM.heroSubtitle.textContent)`).
- **Hero Carousel for Multiple Featured Anime:**
  - When the featured API returns multiple anime (e.g., 8 titles), a static single-hero feels empty.
  - Implement a carousel: take top 4-5 featured items, auto-rotate every 6 seconds, Apple-style dot indicators (clickable), fade transitions, pause on hover/touch.
  - All hero data (poster, title, subtitle, synopsis, rating, badges, CTA buttons) must swap atomically per slide.

## 14. Anime Card Info Padding & Spacing Pitfall
- **The Zero-Padding Card Trap:**
  - Cards with `.poster-media-wrap` (full-bleed poster) followed by text info (title, rating, genre tags) often have NO padding on the text area, resulting in:
    - `posterToTitle: 0px` — title text touches poster bottom edge
    - `titleLeftPad: 1px` — text nearly touches card left edge
    - `genreToCardBottom: 1px` — last tag nearly touches card bottom edge
  - Looks extremely cramped and unprofessional on mobile.
- **Proper Card Info Spacing:**
  - Wrap text elements in a `.card-info` container with `padding: 10px 10px 12px 10px`
  - Or apply individual margins: `.card-title { margin-top: 10px; }`, bottom padding on last element ≥ 10px
  - Minimum horizontal padding ≥ 8px on both sides
- **Playwright Metrological Measurement Script:**
  ```javascript
  // Measure card spacing precisely via headless Playwright
  const details = page.eval_on_selector_all('.anime-card', `cards => {
    return cards.slice(0, 5).map(c => {
      const cardRect = c.getBoundingClientRect();
      const poster = c.querySelector('.poster-media-wrap');
      const title = c.querySelector('.card-title');
      const posterRect = poster?.getBoundingClientRect();
      const titleRect = title?.getBoundingClientRect();
      return {
        posterToTitle: titleRect && posterRect ? Math.round(titleRect.top - posterRect.bottom) : null,
        titleLeftPad: titleRect ? Math.round(titleRect.left - cardRect.left) : null,
        genreToCardBottom: /* measure last child to card bottom */
      };
    });
  }`);
  ```

## 15. Mobile Navbar Spacing & Command Capsule Density
- **The Zero-Gap Navbar Pitfall:**
  - On mobile viewports (< 640px), frosted glass command capsules that pack logo + route pills + search icon often have zero measured gap between elements (`brandToPills: 0px`, `pillsToSearch: 0px`).
  - Visually looks cramped and the search icon may clip against the right edge.
- **Fix Checklist:**
  - Set explicit `gap` in `.command-capsule` mobile override (≥ 6px)
  - Consider hiding brand text on mobile (show only logo icon) to reclaim space
  - Route pills should use `overflow-x: auto; scrollbar-width: none;` for horizontal scroll on narrow screens
  - Minimum pill font: `0.75rem` with `padding: 4px 8px`
  - Search launcher: fixed `36×36px` with flex-shrink: 0
- **Measurement Script (Navbar):**
  ```javascript
  const nav = page.evaluate(`() => {
    const brand = document.querySelector('.brand-emblem');
    const pills = document.querySelector('.route-pills');
    const search = document.querySelector('.search-launcher-pill');
    return {
      brandToPills: pills.getBoundingClientRect().left - brand.getBoundingClientRect().right,
      pillsToSearch: search.getBoundingClientRect().left - pills.getBoundingClientRect().right,
    };
  }`);
  ```

## 16. Official Bstation OGV Index API vs Brute-Force Search Pitfall
- **The Brute-Force Search & WAF HTTP 412 Trap:**
  - Attempting to build a full catalog by firing parallel batches of broad search keywords (`/search_v2` with alphabet + genres + popular franchise names) triggers Bstation's WAF rate limiter with **HTTP 412 (Precondition Failed)**.
  - This causes silent query drops, leaving the catalog builder with only 31 to 113 titles instead of the full library.
- **The Official OGV Index/Category Endpoints (Discovered via Web Bundle RE):**
  - Bstation web (`/id/category?season_type=1,4`) uses official dedicated gateway endpoints:
    - Catalog Items: `https://api.bilibili.tv/intl/gateway/web/v2/ogv/index/items_v2`
    - Filter Taxonomy: `https://api.bilibili.tv/intl/gateway/web/v2/ogv/index/filters?season_type=1,4`
    - Categories: `https://api.bilibili.tv/intl/gateway/web/v2/ogv/index/categories`
- **Query Parameters & Invariants:**
  - `season_type=1,4` (1 = Japanese Anime [50 titles], 4 = Donghua / OGV Anime [282 titles]).
  - `s_locale=id_ID`, `platform=web`.
  - **Page Size Cap Invariant:** Maximum `ps` is **50**. Requesting `ps > 50` (such as 60 or 100) returns error `code: -400` with empty cards. Always use `ps=50`.
  - **Catalog Paging:** Loop `pn=1` incrementally until `res.data.has_next == False` or `res.data.cards` is empty. In Bstation SEA (id_ID), this yields the complete 100% official licensed anime library (~332 unique titles) across just 7 clean requests.
- **Why User Sees "Ribuan Anime" on Bstation:**
  - Bstation's total library includes Dracin / Short Dramas (`season_type=5`, ~1,448 titles), TV Shows (`season_type=2,3`), and millions of user-generated UGC videos. The official licensed anime library on Bstation Indonesia is specifically 332 titles.
- **Catalog Harvesting Architecture:**
  1. Fetch `ogv/index/items_v2` with `season_type=1,4`, `ps=50`, paging from `pn=1` with 100ms pause between pages.
  2. Merge with weekly schedule (`/ogv/timeline`) to enrich latest episode update strings (`index_show`).
  3. Cache the resulting ~332 titles in memory/Redis with 1-hour TTL.

## 17. SVG Icon Sizing in CTA Buttons — The Unconstrained Icon Pitfall
- **Problem:** Inline SVG icons (e.g., info circle icon in "Daftar Episode" button) without explicit CSS sizing constraints inflate to their intrinsic SVG `viewBox` size.
  - Desktop: icon bloats to 48px, button height stretches to 74px (vs 46px sibling)
  - Mobile: icon overflows button container, collides with adjacent text
- **Fix:** Always constrain inline SVG icons in buttons:
  ```css
  .btn .icon, .btn svg {
    width: 18px;
    height: 18px;
    max-width: 18px;
    max-height: 18px;
    flex-shrink: 0;
  }
  @media (max-width: 639px) {
    .btn .icon, .btn svg { width: 16px; height: 16px; max-width: 16px; max-height: 16px; }
  }
  ```
- **Also set `white-space: nowrap`** on CTA buttons to prevent text wrapping caused by oversized icons stealing horizontal space.

## 18. Git Push Discipline for Multi-Commit Fleet Sessions
- Long fleet sessions (V4.0 through V4.6) can accumulate 10+ commits locally without pushing to remote.
- User expects all commits (backend + frontend) to be pushed to GitHub after work is done.
- Before pushing, clean up the repo:
  - Update `.gitignore` to exclude test scripts (`test_*.py`, `verify_*.py`, `check_*.py`, etc.), QA artifacts (`evidence/screenshots/`, `evidence/manifests/`), and temporary files (`backend/cookies.txt`).
  - `git checkout -- evidence/` to discard modified evidence files that shouldn't be committed.
  - Single cleanup commit before push.
- Always verify with `git log --oneline origin/master..HEAD` to show unpushed commits before pushing.

## 19. Auto Short Video Repurposing, Safe-Zone Subtitling & 5 Viral Hook Engines (Shorts, TikTok, Reels)
- When building automated clipping, viral hook detection, kinetic subtitling pipelines, and retention hook engines from long-form content, see `references/auto-shorts-pipeline-and-subtitling.md`.
- Covers 0-quota YouTube RSS ingestion, two-stage audio/video fetching, faster-whisper word-level timestamp generation, ASS subtitle styling (MrBeast/Alex Hormozi karaoke pop), safe-zone typography (Y=1400px baseline avoiding speaker overlap and mobile UI collision), 5 viral visual hook engines (Camera Stomp Shockwave, Paper Tear Reveal, Breaking News Ticker, Zoom Punch-In, Glitch Tape Rewind), and single-pass FFmpeg compositing without audio-video drift.

## 20. Streaming Subprocess Lifecycle, Pipe Deadlocks & Resilience Audit
When auditing or building production on-the-fly media streaming backends (FastAPI / Uvicorn + FFmpeg):
- **The Stderr Pipe Deadlock Trap (`stderr=PIPE`):**
  - Spawning `asyncio.create_subprocess_exec(*ffmpeg_cmd, stdout=PIPE, stderr=PIPE)` while consuming only `stdout` will inevitably deadlock once FFmpeg outputs >64 KB of warning/log text. In Linux, un-drained pipe buffers block further OS `write()` syscalls, freezing the video stream permanently.
  - **Remediation:** Use `stderr=asyncio.subprocess.DEVNULL` for production remuxers, or drain stderr concurrently via a dedicated background task into a bounded circular ring buffer for forensic logs.
- **Zombie Process Defunct Cleanup (`proc.kill()` vs `proc.wait()`):**
  - Simply calling `proc.kill()` in a `finally` block sends `SIGKILL` but leaves a zombie process entry (`[ffmpeg] <defunct>`) in the Linux process table until reaped.
  - **Remediation:** Always follow `proc.kill()` with `await asyncio.wait_for(proc.wait(), timeout=2.0)`. Set systemd `KillMode=mixed` (not `KillMode=process`) so child subprocesses and workers in the cgroup are guaranteed to be reaped on service reload.
- **Metadata Cache Utilization for Fast Seeking (TTFB Optimization):**
  - If direct video/audio URLs are already resolved and cached in memory/Redis (e.g. `stream_meta:v2`), never spawn a synchronous `yt-dlp` subprocess on subsequent seek requests (`?t=X`).
  - Read direct stream URLs directly from the metadata cache; execute extractor subprocesses only on cache miss or token expiration. This cuts seek TTFB from ~3s down to <500ms.
- **Client Resume Playback & Storage I/O Ergonomics:**
  - Persisting playback progress (`currentTime`) on HTML5 video `timeupdate` (fires every 250ms) causes severe browser `localStorage` I/O thrashing.
  - Throttle storage writes to every 3–5 seconds, on `pause`, and on `beforeunload`. When resuming a fragmented MP4 stream, pass the stored timestamp into the backend seek parameter (`?t=${progressSeconds}`) while dynamically shifting WebVTT subtitle track offsets.

## 21. Third-Party Media Streaming Monetization, Identity Decoupling & Compliance
- **Identity Decoupling Invariant (Domain & Infrastructure):**
  - Never host or monetize third-party scraping/remuxing streams on domains bound to personal verified identities (e.g. `.my.id` or ccTLDs requiring NIK/KTP under PANDI).
  - Unmonetized hobby streaming faces low-priority administrative takedowns/DNS filtering. However, accepting revenue shifts legal classification to commercial copyright infringement (UU Hak Cipta No. 28/2014 Pasal 113, carries criminal penalties and heavy fines).
  - Always decouple streaming infrastructure onto disposable offshore domains (`.to`, `.cc`, `.is`) via privacy-preserving registrars and Cloudflare proxying.
- **Payment Processor AUP & KYC Freeze Traps:**
  - Domestic Indonesian payment gateways (Midtrans, Xendit, Pakasir) and creator tipping platforms (Saweria, Trakteer) operate under Bank Indonesia PJP licensing with strict Intellectual Property Acceptable Use Policies (AUP).
  - Automated merchant web crawling and transaction audits flag scraping/streaming sites, resulting in permanent account bans, national KYC/bank blacklisting, and 90–180 day fund holds.
  - Mitigate via non-custodial cryptocurrency donations (USDT-TRC20/Polygon, Monero) or direct community server-upkeep contributions labeled strictly as voluntary gratuity, never as paid digital access passes.
- **Ad Network Hygiene vs Google Safe Browsing:**
  - Programmatic pop-up ad networks (PopAds, PropellerAds, Adsterra) predominantly serve gambling (judol) and APK injectors in Southeast Asia, creating severe legal liability under Indonesian cyber laws (UU ITE Pasal 27(2)).
  - Deceptive redirects trigger Google Safe Browsing red-screen blocks ("Deceptive site ahead"), destroying >95% of organic traffic and ruining clean UI/UX retention.
  - Monopolize the "ad-free clean UI" moat. If monetizing via ads, use strictly **Curated Direct Affiliate Cards** (VPN partnerships like Surfshark/Mullvad, anime merchandise, figure stores) implemented as static HTML/CSS components with zero external tracking scripts.
- **Supporter Utility Freemium Architecture:**
  - Never paywall core video playback. Keep base streaming (720p/1080p) completely open.
  - Monetize high-value convenience utilities: batch downloading seasons to Telegram via bot, priority low-latency CDN routing during peak hours (19:00–22:00 WIB), and cosmetic player custom styling/badges.

## 22. Empty Cache Poisoning & Frontend Hero Dummy ID Pitfalls
- **Empty Array Cache Poisoning (`set_cache(..., [])`):**
  - Endpoints like `/api/featured` and `/api/popular` often query search or curation APIs. If queries return 0 items (e.g. WAF 412 or keyword returning only UGC), executing `set_cache(key, [], ttl=3600)` locks an empty state into cache for an hour, blanking the home page even after upstream recovers.
  - **The Zero-Empty Invariant:** NEVER write an empty array to cache (`if not items: return fallback without set_cache`). Always maintain hardcoded in-memory `_STALE_FEATURED_FALLBACK` / `_STALE_POPULAR_FALLBACK` dictionaries to guarantee the backend never delivers an empty array to the client.
  - **Sourcing Featured/Popular from Harvested Catalog Store:** Never rely on static search queries (`execute_pure_ogv_search`) for home spotlight or popular shelves. Instead, slice and rank directly from the already-harvested OGV catalog store (`get_or_build_catalog_store()`) and seasonal timeline, sorting by view count and rating.
- **The Dummy Season ID Trap (`const seasonId = item?.season_id || '2097863'`):**
  - Fallbacks using hardcoded dummy season IDs cause the Hero CTA button ("Nonton Sekarang") to route users to non-existent metadata (`#/watch/2097863`), causing the video player to crash into an alarming stream error ("Aliran Video Sedang Disiapkan: Aliran data video terputus").
  - **Fix:**
    1. Remove all dummy season IDs.
    2. Disable CTA buttons (`disabled = true`, `onclick = null`) if `season_id` is missing.
    3. Implement a 3-tier Hero fallback cascade: `featured -> seasonal.slice(0, 5) -> popular.slice(0, 5) -> hide`.
    4. Enforce the Zero-Void Principle on shelves: if `popular.length === 0`, hide the container (`DOM.popularBlock.hidden = true`) rather than rendering "0 Judul Populer".

## 23. Standalone Repository Portability & Core Vendorization Invariant
- **The Sibling Path Insertion Trap (`sys.path.insert(0, "/root/...")`):**
  - When extracting or developing web backends alongside automation bots (e.g. `animeTGStream` Telegram bot and `animestr-web`), developers often shortcut code reuse by inserting absolute host filesystem paths into `sys.path`.
  - **The Portability Defect:** When a user clones the repository on a fresh machine or server (`git clone https://github.com/IndraYuda13/animestr-web`), running the service fails immediately with fatal `ModuleNotFoundError: No module named 'core'`.
  - **Remediation & Packaging Standards:**
    1. **Vendorize Core Modules:** Always copy required domain logic (`bstation_core.py`, `ytdlp_core.py`, `cookie_helper.py`, `stream_probe.py`) directly into the repository structure (e.g. `backend/core/` with `__init__.py`).
    2. **Local Package Imports:** Use dynamic directory resolution (`CURRENT_DIR = Path(__file__).resolve().parent; if str(CURRENT_DIR) not in sys.path: sys.path.insert(0, str(CURRENT_DIR))`) or package-local imports (`from .core.bstation_core import BstationClient`) with zero references to host-specific parent directories.
    3. **Document System CLI Prerequisites:** Explicitly document in `README.md` the external non-pip binaries required in `$PATH` (`ffmpeg` for stream muxing, `yt-dlp` for metadata extraction).
    4. **Credential & Cookie Stubs:** Provide `backend/cookies.txt.example` and clearly document environment variables (`BILI_PROXY_URL`) so cloned environments can be configured and run without code modification. Ensure `.gitignore` explicitly prevents committing live session cookies (`backend/cookies.txt`).
    5. **Up-to-Date Setup & Run Commands in Root README:** Every time project dependencies, modules, or ports change, immediately verify and patch the root `README.md` with explicit, copy-pasteable quickstart instructions (clone -> install dependencies -> setup cookies/proxy -> run backend & frontend) so users cloning the repo can run it with zero friction.

See `references/bstation-and-mobile-player.md` for extended reference notes on Bstation franchise search patterns and mobile player implementation, and `references/streaming-monetization-and-compliance.md` for in-depth compliance and monetization guidelines.

