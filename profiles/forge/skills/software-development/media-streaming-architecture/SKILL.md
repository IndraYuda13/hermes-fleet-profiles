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

- `references/anime-streaming-api-contract.md`: Skema payload API riil, struktur endpoint (featured, search, episodes, subtitles), dan density layout.
- `references/split-stream-mse-proxy.md`: Detail arsitektur proxy FastAPI async dan konfigurasi Nginx reverse proxy.
- `references/short-video-pipeline-patterns.md`: FFmpeg 16:9 to 9:16 blurred background filtergraph, vertical UI safe zones, Hormozi/MrBeast dynamic karaoke ASS formatting, datacenter YouTube cookies anti-bot bypass, youtube-transcript-api v1.2.4+ quirks, dynamic AI query discovery, and TikTok/YouTube upload specs.
- `scripts/ass_to_vtt.py`: Skrip konversi deterministik format ASS ke WebVTT standar.
