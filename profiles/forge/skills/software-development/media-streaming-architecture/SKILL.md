---
name: media-streaming-architecture
description: "Use when designing video streaming backends or HLS/MSE."
---

# Media & Video Streaming Architecture

Guide and proven patterns for building production-grade video/audio streaming backends, web players, Range proxies, and media pipelines.

## Core Architectural Trade-offs

When serving split video/audio streams (e.g. DASH, Bstation, YouTube) or high-volume video to web clients:

### 1. Delivery Models Comparison

| Approach | CPU / Memory | Disk I/O | Seeking (HTTP 206) | Reliability & Scalability |
| :--- | :--- | :--- | :--- | :--- |
| **Client MSE + Stateless Proxy** (Recommended) | ~0% CPU, <64KB RAM/conn | 0 Byte | Ultra-fast (<100ms native) | Stateless, highly scalable |
| **On-the-Fly Piped FFmpeg** (`pipe:1`) | High context switch, 30-60MB/conn | 0 Byte | Broken / High latency | Rawan zombie process & OOM |
| **HLS On-Demand Packaging** | High transcoding/muxing CPU | Ekstrem (ratusan chunk .ts) | Medium (chunk interval) | Rawan ENOSPC (disk full) |

### 2. The Piped FFmpeg Process & Seek Pitfalls
- **Root cause:** Output stdout pipe FFmpeg (`pipe:1`) tidak memiliki `Content-Length` pasti dan tidak seekable secara acak.
- **Symptom:** Saat user scrubbing/seeking di browser, browser memutus koneksi dan mengirim header `Range: bytes=X-Y`. Piped FFmpeg tidak bisa melompat ke offset byte tersebut tanpa restart proses.
- **Failure mode & Seeking:** Backend harus men-kill proses lama dan spawn FFmpeg baru dengan parameter `-ss`.
- **Stderr Pipe Buffer Deadlock (64KB Buffer):** Jika subprocess di-spawn dengan `stderr=asyncio.subprocess.PIPE` tetapi stderr tidak pernah di-drain (hanya membaca `stdout.read()`), buffer pipe Linux OS (default 64KB) akan penuh saat FFmpeg memunculkan log warning/demuxer error. Syscall `write()` FFmpeg akan ter-block permanen, membekukan proses FFmpeg dan membuat stream video client macet total. Solusi: Gunakan `stderr=asyncio.subprocess.DEVNULL` atau buat coroutine background untuk men-drain stderr ke bounded ring buffer.
- **Zombie / Orphan Process Leak (`kill` without `wait`):** Memanggil `proc.kill()` saat client disconnect mengirim `SIGKILL`, tetapi jika backend tidak memanggil `await proc.wait()`, kernel Linux mempertahankan entri proses dalam status `<defunct>` (zombie) di process table. Solusi: Selalu jalankan `await asyncio.wait_for(proc.wait(), timeout=2.0)` di dalam blok `finally`.
- **Subprocess Redundancy vs URL Cache (TTFB Penalty):** Endpoint streaming jangan memanggil ulang extractor/yt-dlp jika direct stream URL sudah tersimpan di cache metadata. Ekstraksi subprocess baru pada setiap seek/play menambah 2-4 detik latency TTFB yang tidak perlu.
- **Multi-Worker Memory Cache Isolation:** Jika service dijalankan dengan multi-worker Uvicorn (`--workers > 1`), cache in-memory Python (`dict`/`OrderedDict`) terisolasi per worker process. Cache hit di Worker A tetap menjadi cache miss di Worker B, memicu extraction berulang. Gunakan shared cache tier (file-backed SQLite cache atau IPC/Redis) untuk stream metadata & direct URLs.
- **Keyframe Alignment & PTS Normalization (`-avoid_negative_ts make_zero`):** Pada fast seeking (`-ss <offset>` sebelum input `-i`), video H.264 dengan struktur piramida B-frame dapat menghasilkan packet presentation timestamp (PTS) yang offset atau berbeda dari stream audio. Selalu sertakan flag `-avoid_negative_ts make_zero` pada output pipe fragmented MP4 agar initial packet PTS dinormalisasi ke 0 tanpa audio-video desync.

### 3. Recommended: Client-Side MSE + Stateless Range Proxy
- Gunakan player web modern berbasis Media Source Extensions (MSE) seperti **Shaka Player** atau **Dash.js**.
- Inisialisasi 2 `SourceBuffer` sinkron: 1 untuk video (`video/mp4; codecs="..."`) dan 1 untuk audio (`audio/mp4; codecs="..."`). Browser HTML5 engine menangani sinkronisasi audio-video secara hardware-accelerated.
- Backend hanya berfungsi sebagai stateless HTTP 206 passthrough proxy.

## Stateless HTTP 206 Range Proxy Pattern

Untuk streaming dari CDN pihak ketiga yang memerlukan header khusus (seperti Referer atau custom User-Agent) tanpa membocorkan kredensial:

1. **Header Forwarding:** Teruskan header `Range` dan `If-Range` dari client ke upstream. Teruskan `Content-Range`, `Content-Length`, `Accept-Ranges`, dan `Content-Type` dari upstream ke client.
2. **Zero Disk Buffering:** Jangan simpan chunk video di disk server. Konfigurasikan reverse proxy (Nginx) dengan `proxy_buffering off;`.
3. **Client Disconnect Abort:** Pasang listener pembatalan koneksi client (misal `request.is_disconnected()` di FastAPI atau `req.on('close')` di Node.js). Segera batalkan koneksi ke upstream CDN saat browser memutus request (seek / tutup tab) untuk mencegah pemborosan bandwidth VPS.

## Security & Anti-Abuse (SSRF & Hotlinking)

Endpoint proxy video rawan disalahgunakan sebagai open proxy atau SSRF vector. Terapkan pertahanan berlapis:

1. **HMAC-SHA256 Signed Tokens:**
   - Jangan terima URL mentah di query param (`?url=https://...`).
   - Generate token signed berumur pendek (TTL 2-4 jam): `HMAC-SHA256(secret_key, canonical_url + ":" + exp + ":" + session_id)`.
   - Gunakan constant-time comparison (`hmac.compare_digest`) saat verifikasi.
2. **Strict Hostname Whitelist:**
   - Parse URL dengan native URL parser (`urllib.parse` / `new URL()`).
   - Tolak port non-standar dan URL dengan credentials (`user:pass@`).
   - Validasi hostname dengan akhiran dot-suffix resmi (contoh: `.bilivideo.com`, `.bilivideo.cn`).
   - Nonaktifkan automatic redirect (`allow_redirects=False`) agar upstream tidak bisa redirect ke IP loopback/private.
3. **Decouple Authentication Cookies:**
   - Kredensial akun (cookies login, SESSDATA) hanya boleh ada di backend resolver.
   - Node CDN streaming umumnya tidak memerlukan cookies akun, hanya memerlukan CDN query signature dan header Referer. Jangan pernah meneruskan cookies akun ke CDN atau client.

## Streaming Feed Resilience & Anti-Poisoning Caching

Home and discovery feeds (e.g., featured spotlight, popular shelves) require strict resilience guarantees to prevent blank homepages on upstream disruption:

1. **Avoid Serial Upstream Live Searches in Request Path:**
   - Melakukan loop pencarian judul upstream (misal 8-16 query `search_v2` sekuensial) di handler request menyebabkan latensi O(N), menghabiskan connection pool, dan sangat rentan terpicu WAF/rate-limit (HTTP 412).
   - **Solusi (Catalog Slice First):** Bangun single source of truth berupa in-memory catalog store (`build_full_catalog` via category harvester `items_v2`). Handler `/api/featured` dan `/api/popular` cukup membaca, memfilter, dan mengurutkan data langsung dari memory catalog store (sub-millisecond latency).

2. **The "Never-Cache-Empty" Guard (Anti-Poisoning):**
   - **Pitfall:** Menyimpan empty list `set_cache(key, [], ttl=3600)` saat upstream search mengembalikan 0 hasil akibat WAF/schema drop. Hal ini mengunci frontend dalam kondisi blank hero/empty shelf selama 1 jam penuh meskipun upstream sudah pulih.
   - **Rule:** Pasang guard `set_cache_safe(key, data, min_items=1)` yang menolak menimpa cache valid dengan data kosong atau berukuran di bawah ambang batas minimal.

3. **4-Tier Graceful Degradation Hierarchy:**
   - **Tier 1 (LRU Memory Cache):** Fast path sub-millisecond untuk hit non-empty.
   - **Tier 2 (Dynamic Catalog Slice):** In-memory filtering/ranking dari store katalog aktif yang dipanen periodik.
   - **Tier 3 (Seasonal Timeline Fallback):** Ambil rilis anime musiman aktif dari endpoint timeline dengan short TTL (300s).
   - **Tier 4 (Guaranteed Static Seed):** Hardcoded fallback constant berisi 4-8 judul terverifikasi (season_id, title, cover CDN valid) dengan micro-TTL (60s) agar frontend dijamin tidak pernah blank.

## Streaming Web UI & Discovery Guardrails (Zero-Void Contract)

Frontend streaming web apps must handle upstream feed anomalies gracefully without rendering zombie UI states or broken interactions:

1. **Hero Multi-Tier Fallback Cascade:**
   - Jangan biarkan Hero Spotlight kosong jika `/api/featured` me-return `[]`.
   - Pasang cascade bertingkat: `featured` -> `seasonal.slice(0, 5)` -> `popular.slice(0, 5)`.
   - Jika seluruh sumber data kosong total: sembunyikan hero (`heroSpotlight.hidden = true`) dan bersihkan carousel interval timer.

2. **Action Button Guardrails (No Hardcoded Dummy IDs):**
   - **Pitfall:** Menggunakan hardcoded dummy season ID saat metadata hero tidak lengkap. Mengklik tombol memicu router ke endpoint episode yang tidak ada atau melempar dialog error playback ("Aliran video terputus").
   - **Rule:** Jika `!item || !item.season_id`, tombol "Nonton Sekarang" & "Detail" wajib dinonaktifkan (`disabled = true`, `aria-disabled="true"`, `onclick = null`, title "Konten belum tersedia"). Hanya aktifkan dan bind click routing jika `season_id` valid.

3. **Carousel Timer Lifecycle Guard:**
   - Jalankan `startHeroTimer()` hanya jika `slides.length > 1`.
   - Jika slide <= 1 atau kosong, selalu panggil `clearInterval(state.heroTimer)` dan sembunyikan dots pagination.

4. **The Zero-Void Shelf Principle (Streaming Rail Pattern):**
   - Shelf tidak boleh dirender jika jumlah item bernilai 0 (contoh: teks "0 Judul Populer" di atas row kosong).
   - Jika list kosong setelah deduplikasi: coba fallback ke sisa anime dari shelf lain (misal `seasonal.slice(6)`). Jika tetap 0, sembunyikan seluruh kontainer shelf (`popularBlock.hidden = true`).

## Subtitle Parsing (ASS to WebVTT)

Banyak upstream menyediakan subtitle dalam format Advanced SubStation Alpha (`.ass`). Browser `<track>` membutuhkan WebVTT (`RFC 8216`).
- Konversi cue timestamp dari format ASS `h:mm:ss.cs` ke WebVTT `hh:mm:ss.mmm`.
- Strip formatting tags seperti `{\b1}`, `{\pos(...)}`, dan ganti newline marker `\N` menjadi newline biasa.
- Simpan hasil konversi di cache lokal dengan key hash URL dan kirim header `Cache-Control: public, max-age=604800, immutable`.
- Script utilitas tersedia di `scripts/ass_to_vtt.py`.

## HTML5 Player & Subtitle Runtime Pitfalls

### 1. Piped fMP4 Infinite Duration (`empty_moov`)
- **Gejala:** Progress bar / scrubber timeline tidak bergerak (terkunci di 0%) atau scrubbing bernilai `Infinity`.
- **Root cause:** Stream fragmented MP4 chunked via `pipe:1` dengan flag `-movflags empty_moov` tidak memuat header durasi global di box `mvhd`. Browser mengklasifikasikan stream sebagai unbounded live stream (`video.duration === Infinity`).
- **Solusi:** Jangan pernah mengecek durasi dengan `!isNaN(video.duration) && video.duration > 10` karena `!isNaN(Infinity)` dan `Infinity > 10` keduanya bernilai `true`. Selalu gunakan validasi ketat `Number.isFinite(video.duration) && video.duration > 0`, dengan fallback ke durasi metadata katalog (misal 1440s untuk episode anime standar).

### 2. Subtitle Overlap / Dobel (Browser Automatic Track Selection)
- **Gejala:** Saat user memilih subtitle non-English (misal Indo) lalu seek atau ganti episode, subtitle English ikut muncul tertimpa di layar (dobel).
- **Root cause:** Menaruh beberapa tag `<track>` sekaligus di DOM lalu menyetel `track.mode = 'disabled'` secara sinkron langsung setelah `appendChild` adalah race condition. Tag `<track>` di-fetch secara asynchronous. Saat WebVTT selesai di-parse, algoritma browser W3C *Automatic text track selection* mencocokkan `srclang="en"` dengan `navigator.language` (umumnya `en-US`) dan secara otomatis mengubah mode track English kembali menjadi `showing`.
- **Solusi (Single-Track DOM Injection Pattern):** Render seluruh opsi bahasa di UI/menu kustom player, namun **hanya inject 1 elemen `<track>` ke dalam tag `<video>` DOM** (yaitu bahasa yang sedang aktif dipilih). Saat user mengganti bahasa atau seek, bersihkan track lama dan append hanya track bahasa terpilih. Ini mengeliminasi race condition browser dan menghemat bandwidth WebVTT yang tidak ditonton.

### 3. Spacebar Keyboard Shortcut vs HUD Button Focus Conflict
- **Gejala:** Saat menekan tombol `Space` untuk pause/play, terjadi aksi ganda yang berbenturan (misal video pause DAN tombol mute berubah).
- **Root cause:** Guard keyboard shortcut hanya mengecek `INPUT` dan `TEXTAREA`. Ketika pengguna baru saja mengklik tombol HUD player (seperti mute, settings, atau subtitle), elemen tombol tersebut tetap mempertahankan native focus. Menekan `Space` memicu native click pada button yang focused, bersamaan dengan listener hotkey `Space`.
- **Solusi:** Tambahkan pelepasan focus (`activeEl.blur()`) jika elemen yang aktif adalah tag `BUTTON` sebelum mengeksekusi toggle play/pause player.

### 4. Mobile Autoplay Rejection on Asynchronous Auto-Next
- **Gejala:** Hitungan mundur 5 detik menuju episode berikutnya selesai, tetapi pemutaran episode baru macet/pause dan melempar error `NotAllowedError`.
- **Root cause:** Kebijakan strict autoplay browser mobile (khususnya Safari iOS dan Chrome Android) menolak `video.play()` yang dipanggil secara asynchronous dari timer `setTimeout` tanpa didahului user gesture langsung pada tick event tersebut.
- **Solusi:** Bungkus pemanggilan `video.play()` dalam promise catch handler. Jika terjadi penolakan `NotAllowedError`, transisikan overlay countdown menjadi tombol interaksi langsung (misal "Tap untuk Putar Episode Berikutnya") agar gesture pengguna memicu pemutaran dengan valid.

## Supporting Files

- `references/anime-streaming-api-contract.md`: Skema payload API riil, struktur endpoint (featured, search, episodes, subtitles, items_v2 catalog harvesting & proxy regional override, catalog content type separation & type_counts, blockbuster anime seed discovery harvester, serta direct routing fallback season_info), dan density layout.
- `references/split-stream-mse-proxy.md`: Detail arsitektur proxy FastAPI async dan konfigurasi Nginx reverse proxy.
- `references/short-video-pipeline-patterns.md`: FFmpeg 16:9 to 9:16 blurred background filtergraph, vertical UI safe zones, Hormozi/MrBeast dynamic karaoke ASS formatting, datacenter YouTube cookies anti-bot bypass, youtube-transcript-api v1.2.4+ quirks, dynamic AI query discovery, Selection Core (zero-download discovery, Indonesian language gate, isolated window word alignment, pause boundary windowing, self-contained semantic scoring, OpenCV/Gemini dual vision, and 30-55s boundary snapping), Stable Editing Core (scene-static portrait framing, single/multi-speaker rules, subtitle policy classification, broadcast voice mastering -16 LUFS zero SFX, clean multi-segment concat & punch-in filtergraph), Three-Tier Quality Control Gate (ffprobe stream integrity, OpenCV local visual sampling, YuNet face/headroom/stuck subtitle guards, 3x3 contact sheet, Gemini Visual Director via 9router, max 1 repair loop), State Machine & Production Pipeline (11 happy + 6 terminal reject states, uploading guard invariant, 8-gate Strict Upload Gate, and clipped subtitle relative timestamp normalization), Hybrid Subtitle Accuracy Engine V3.1 (Whisper WHEN vs Gemini WHAT division, faster-whisper large-v3 CPU INT8 runtime and HF_HOME storage routing, dedicated Gemini native-video verbatim verifier via 9router, transcript fusion without synthetic timing, zero-overlap ASS timeline invariants, and strict Gemini Video QC gate), Double Subtitle Prevention (SOURCE_EXISTING vs GENERATE vs strict UNKNOWN rejection, conflict detection, and QC double subtitle gate), Natural Sentence Ending Engine (dangling clause detection, 55s boundary extension vs ranked candidate fallback, natural pause preservation, force_extend preflight repair, and Gemini ending QC gate), Surgical Shorts Metadata Generator (5 ranked candidates, <=85 char curiosity gap, raw-transcript overlap detection & retry guard, contextual description, and hashtag normalization), and TikTok/YouTube upload specs.
- `templates/catalog_feed_endpoints.py`: Boilerplate implementasi feed `/api/featured` & `/api/popular` berbasis in-memory catalog store, double-checked locking, negative cache guardrail, dan 3-tier fallback.
- `scripts/ass_to_vtt.py`: Skrip konversi deterministik format ASS ke WebVTT standar.
