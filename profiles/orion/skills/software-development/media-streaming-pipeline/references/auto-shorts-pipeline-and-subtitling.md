# Auto Shorts Video Repurposing Pipeline & Safe-Zone Subtitling

Guidelines, architecture patterns, and pitfalls for automated short-form video generation (YouTube Shorts, TikTok, Instagram Reels) from long-form content (podcasts, webinars, talkshows).

## 1. Zero-Quota & Low-Quota YouTube Discovery
YouTube Data API v3 enforces a default daily quota of 10,000 units. Calling `search.list` costs 100 units per request (exhausted after 100 queries).

### Dynamic AI Query Generation vs Static Lists:
- **Anti-Pattern:** Hardcoding static search queries in `.env` causes repetitive, stale clipping and limits topic diversity.
- **Dynamic AI Prompting (Full AI Ingestion):**
  - Prompt the LLM (e.g. Gemini 3.8 Flash) at each discovery cycle to generate 8-10 diverse, high-engagement search queries covering:
    - Podcast banter & viral debates
    - Livestreaming funny/epic moment highlights
    - Deep-talk founder & creator interviews
    - Stand-up comedy roasts & specials
    - Mystery & criminal investigative storytelling
    - Gaming culture & creator hangouts
  - Maintain a rolling queue of dynamic queries, using `.env` only as an offline/timeout fallback.

### Safe Ingestion Hierarchy:
1. **RSS Feed Polling (0 API Quota)**:
   - Target channel RSS: `https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}`
   - Yields the 15 newest videos in XML with zero quota usage.
2. **Channel Uploads Playlist (1 Quota Unit per 50 videos)**:
   - Convert `channel_id` from `UCxxxx` to `UUxxxx`.
   - Call `playlistItems.list(playlistId="UUxxxx", maxResults=50)`.
3. **yt-dlp Metadata Scraping**:
   - `yt-dlp --flat-playlist --dump-single-json "https://www.youtube.com/@channel/videos"` to audit catalog without API keys.

### Datacenter IP Bot Detection Defenses (`Sign in to confirm you're not a bot`):
- Cloud VPS providers (DigitalOcean, Hetzner, AWS, Azure) are heavily flag-blocked by YouTube anti-bot heuristics on both `yt-dlp` and `youtube-transcript-api`.
- **Egress Proxy Routing via Local Residential/VPN Node**:
  - Always route `yt-dlp` download commands and transcript scrapers through an active proxy (e.g. local Surfshark proxy at `http://127.0.0.1:31001` or residential node) to bypass datacenter IP reputation blocks.
  - In `yt-dlp` Python options: `"proxy": "http://127.0.0.1:31001"`.
- **yt-dlp Modern Anti-Bot & Challenge Solver Flags**:
  - Recent YouTube rollouts require remote JavaScript challenge solvers (EJS) via Node.js or Deno:
    `--remote-components ejs:github --js-runtimes deno` (install Deno binary in `/usr/local/bin/deno`).
  - In Python `YoutubeDL` options:
    ```python
    ydl_opts = {
        "proxy": "http://127.0.0.1:31001",
        "cookiefile": "/path/to/cookies.txt",
        "js_runtimes": {"deno": {"path": "/usr/local/bin/deno"}},
        "remote_components": ["ejs:github"],
        "format": "18/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
    }
    ```
- **Cookie Session Invalidation & Fresh Export Pitfalls**:
  - YouTube rotates and invalidates session cookies (`__Secure-1PSIDTS`, `__Secure-3PSIDTS`, `LOGIN_INFO`) when exported cookies are shared across drastically different IPs (e.g. residential vs datacenter IP) or when the user continues clicking/browsing in the original tab after export.
  - Converting exported JSON cookies to Netscape format must preserve all 20+ secure keys (`HSID`, `SSID`, `APISID`, `SAPISID`, `__Secure-1PSID`, `__Secure-3PSID`, `LOGIN_INFO`, `SIDCC`).
  - Testing cookie validity: run `yt-dlp --cookies cookies.txt --remote-components ejs:github "https://www.youtube.com/watch?v=..." --get-title`. If it returns `"The provided YouTube account cookies are no longer valid"`, a fresh cookie export is mandatory.
- **Whisper CPU Optimization on Long-Form Content**:
  - Long podcasts (1–2 hours) take extensive compute when transcribing the entire duration on CPU.
  - Optimization pattern: Slice audio to the first 600–900 seconds (10–15 mins) using FFmpeg `-t 600` before feeding into `faster-whisper`. Most podcast hooks, viral introductions, and compelling highlights happen within the first 10–15 minutes, cutting Whisper processing time from 15 minutes down to ~30 seconds.


## 2. Bandwidth-Optimized Media Ingestion (Two-Stage Fetch)
- **Stage 1 (Audio Only)**:
  - Do NOT download full 1080p long-form videos (1-3 GB).
  - Download compressed audio only (`yt-dlp -f "ba[ext=m4a]/ba"`) ~15-30 MB.
  - Run transcription and LLM clip selection on the audio.
- **Stage 2 (Time-Sliced Video Download)**:
  - Once start/end timestamps are decided (e.g. `00:03:12` to `00:04:05`):
    ```bash
    yt-dlp --download-sections "*03:12-04:05" -f "bestvideo[height<=1080]+bestaudio" --merge-output-format mp4 -o "clip_raw.mp4" "VIDEO_URL"
    ```

## 3. Subtitle Generation, Precision Karaoke (ASS Format) & Anti-Overlap Typography
To achieve word-by-word highlight (MrBeast / Alex Hormozi kinetic style), word-level timestamps are mandatory.

### faster-whisper Configuration:
```python
from faster_whisper import WhisperModel

model = WhisperModel("small", device="cpu", compute_type="int8")
segments, info = model.transcribe(
    audio_path,
    word_timestamps=True,
    vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=500),
)
```
- **VAD Filter**: Crucial to prevent Whisper hallucination loops on silent/music segments (repeating "thank you for watching").
- **Subtitle Offset Re-basing**: Subtitle timestamps inside `.ass` must be relative to the clip cut point (`t_rel = t_word - clip_start_sec`), starting strictly from `00:00:00.00`.

### ASS (Advanced SubStation Alpha) Styling & Safe-Zone Typography Contract:
- **The Default Font Size & Face-Collision Pitfall**:
  - Default Linux fonts (Liberation Sans) at 65–70pt placed at standard Y: 1250–1270px (MarginV 650) create huge, ugly blocks of text that directly collide with the speaker's chest, microphone, and face in 16:9 podcast video compositions.
- **Precision Safe-Zone Placement & Typography Fix**:
  - **Font**: Download clean, modern Google Fonts display typefaces: `Montserrat-Bold.ttf` / `Montserrat-Black.ttf` or `Rubik-Black.ttf`. In ASS styles, specify `Fontname: Montserrat` or `Rubik`.
  - **Font Size**: Scale down to **42–46pt** (optimal legibility without visual bloat).
  - **Position & Alignment**: Use `Alignment: 2` (bottom center) with `MarginV: 480` to `520` (anchoring baseline at **Y: 1400–1440px**). This places subtitles neatly in the dark lower blurred letterbox margin, 100% free of speaker collision and safely above YouTube Shorts / TikTok bottom UI.
  - **Word Chunking**: Maximum 3 to 4 words per onscreen dialogue event.
  - **Active-Word Karaoke Highlight**:
    - Inactive words: Pure White (`&H00FFFFFF`) with solid 3–4px Black Stroke (`&H00000000`) and subtle drop shadow (`&H90000000`).
    - Active word: High-contrast Electric Yellow (`&H0000E6FF`) with 108% scale pop:
      `{\c&H0000E6FF\fscx108\fscy108}WORD{\c&H00FFFFFF\fscx100\fscy100}`.


## 4. 5 Viral Visual Hook Engines (0.0s – 3.0s Retention Boosters)
Raw, plain video clips suffer severe scroll-away rates. Injecting dynamic, high-engagement visual hooks in the first 0.6s to 3.0s stops viewer scrolling immediately:

### 1. Camera Stomp Shockwave (0.0s – 0.6s)
- **Effect**: Damped oscillation screen shake simulating an energetic foot stomp or shockwave, paired with a synthesized sub-bass 55Hz thud sound.
- **FFmpeg Filter**:
  ```text
  scale=1140:2026,crop=1080:1920:'(in_w-out_w)/2+26*exp(-7*t)*sin(36*PI*t)*lte(t,0.6)': '(in_h-out_h)/2+32*exp(-7*t)*cos(36*PI*t)*lte(t,0.6)'
  ```
- **Audio SFX Synthesizer**: Use `lavfi` source `-f lavfi -i aevalsrc=sin(2*PI*55*t)*exp(-8*t)*0.85:s=44100:d=0.7` and mix via `amix=inputs=2:duration=first`.

### 2. Jagged Paper Tear Reveal (0.0s – 0.8s)
- **Effect**: Two torn jagged paper sheets rip apart to the left and right, revealing the underlying footage.
- **ASS Vector Graphics**: Render vector drawings using ASS drawing mode (`\p1`) with motion tags:
  - Left sheet: `{\move(0,0,-920,0,0,800)\p1}m 0 0 l 550 0 l 530 180 ...{\p0}`
  - Right sheet: `{\move(0,0,920,0,0,800)\p1}m 1080 0 l 550 0 l 530 180 ...{\p0}`

### 3. Breaking News Urgency Banner (0.0s – 3.0s)
- **Effect**: High-urgency crimson red top banner `[ ⚠ BREAKING NEWS ⚠ ]` with bottom ticker `[ 🔴 VIRAL UPDATE • SAKSIKAN SAMPAI SELESAI ]`.
- **Implementation**: Pure ASS vector rectangle (`\p1 m 0 0 l 960 0 l 960 110 l 0 110 \p0`) positioned at `Y: 110` with high-contrast text overlay, self-expiring cleanly after 3.0 seconds.

### 4. Dynamic Whip Transition & Zoom Punch-In (0.0s – 1.5s)
- **Effect**: 115% camera punch-in on the opening hook line, snapping back to 100% normal view at 1.5s, followed by an optional 108% micro-zoom at the mid-video punchline.
- **FFmpeg Crop Filter**:
  ```text
  crop='if(lte(t,1.5), 939, if(between(t,5.0,6.2), 1000, 1080))':'if(lte(t,1.5), 1669, if(between(t,5.0,6.2), 1777, 1920))':(in_w-out_w)/2:(in_h-out_h)/2,scale=1080:1920
  ```

### 5. Glitch Tape Rewind (0.0s – 0.6s)
- **Effect**: VHS chromatic aberration RGB split combined with scanlines and retro OSD `<< REW 00:00:02`.
- **FFmpeg Filter**: `rgbashift=rh=-18:bv=18:gh=8:enable='between(t,0,0.6)'`.
- **ASS Overlay**: OSD text `{\an7\pos(80,120)}⏪ REW 00:00:02` with flickering horizontal scan lines.


## 5. 9:16 Layout & Platform Safe Zones (1080x1920 Canvas)
Short-form platforms overlay intrusive UI elements (header search, creator handles, sound tracks, engagement sidebars).

### Safe Zones:
- **Top Danger Zone (Y: 0 - 220 px)**: Header tabs, search bars.
- **Right Danger Zone (X: 920 - 1080 px, Y: 700 - 1550 px)**: Like, comment, share, bookmark buttons.
- **Bottom Danger Zone (Y: 1480 - 1920 px)**: Account handle, description, audio marquee.
- **Subtitle Anchor Zone**: Centered horizontally at **Y: 1150 - 1350 px** (safe from lower overlay and upper speaker face).

### FFmpeg Single-Pass Compositing (Ambient Blur + ASS Burn):
```bash
ffmpeg -y -ss {START_SEC} -to {END_SEC} -i input_video.mp4 \
  -filter_complex \
  "[0:v]split=2[bg_raw][fg_raw]; \
   [bg_raw]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,setsar=1[bg]; \
   [fg_raw]scale=1080:-2,setsar=1[fg]; \
   [bg][fg]overlay=(W-w)/2:(H-h)/2[merged]; \
   [merged]ass=filename={SUBTITLE_PATH}.ass:fontsdir=/data/fonts[outv]" \
  -map "[outv]" -map 0:a:0 \
  -c:v libx264 -preset veryfast -crf 22 \
  -c:a aac -b:a 192k -ar 44100 -af "aresample=async=1000" \
  -avoid_negative_ts make_zero \
  output_short_9x16.mp4
```

## 5. Timestamp Drift & Audio Desync Mitigation
- YouTube videos often use Variable Frame Rate (VFR). Slicing video with `-c copy` without re-encoding snaps to the nearest keyframe (I-frame), creating severe lip-sync drift between audio and video.
- **Mandatory Flags**:
  - `-af "aresample=async=1000"` to re-align audio samples.
  - `-avoid_negative_ts make_zero` to reset timestamp presentation time.

## 6. Nonstop Loop Daemon, Post-Upload Auto-Prune & Telemetry Dashboard
- **Systemd Multi-Service Segregation**:
  - `autoshort.service`: Continuous background worker running the pipeline loop (`main.py`).
  - `autoshort-web.service`: Lightweight FastAPI web dashboard on port `8450` serving live telemetry, database statistics, and clips gallery.
- **Post-Upload Memory/Disk Hygiene (The Auto-Prune Invariant)**:
  - Video clips rendered in 1080x1920 take 5–25 MB per short. On a high-throughput 24/7 server, disk space quickly exhausts if all rendered artifacts remain on disk.
  - **Rule**: Upon successful upload confirmation (`upload_result["youtube"]["status"] == "success"`), immediately remove local `short_*.mp4` and `sub_*.ass` artifacts from disk, and record status in the database as `"[UPLOADED_AND_CLEANED]"`.
  - Retain local files ONLY if upload failed or pending, ensuring full auditability while preventing storage bloat.
- **Real-Time Telemetry & Web Dashboard (OLED / Dark Mode)**:
  - Expose `/api/stats` and `/api/stream/sse` via Server-Sent Events (SSE) streaming live logs directly from the daemon log file (`generator.log`).
  - Provide a responsive dark-mode UI with KPI cards (Discovered, Completed, Failed, Uploaded Shorts, Average Hook Score), real-time terminal window with auto-scroll, and interactive video cards linked directly to `https://youtube.com/shorts/{id}`.
- **Cloudflare Tunnel Routing for Dashboards**:
  - Expose internal telemetry dashboards (e.g. port `8450`) to custom subdomains (e.g. `autoshort.domain.com`) by adding an ingress rule before the terminal `404` in `/etc/cloudflared/config*.yml`:
    ```yaml
    - hostname: autoshort.indrayuda.my.id
      service: http://127.0.0.1:8450
    ```
  - Bind DNS route explicitly via `cloudflared --origincert /root/.cloudflared/cert.pem tunnel route dns --overwrite-dns <tunnel-uuid> <hostname>`, then restart `cloudflared.service`.
- **Strict Deduplication (SQLite WAL)**:
  - Store `video_id`, `url`, `status` (`discovered`, `processing`, `completed`, `skipped`), and generated clips in SQLite WAL.
  - Before downloading or analyzing, assert `is_video_processed(video_id)` returns `False`.
  - Graceful upload error handling: If platform credentials (OAuth tokens / API keys) are missing or expired, mark clip status as `skipped: no_credentials` and retain rendered output on disk instead of terminating the continuous loop.
  - Automate cleanups of source downloads in temporary scratch directories after each cycle.

## 7. YouTube Upload OAuth Scopes & Privacy Lifecycle
- **The `youtube.upload` Scope Limitation**:
  - Requesting only `https://www.googleapis.com/auth/youtube.upload` permits *only* inserting new videos (`videos.insert`).
  - It does **NOT** grant permission to update privacy status (`videos.update`) or delete videos (`videos.delete`), returning `HttpError 403: Request had insufficient authentication scopes`.
  - **Required Scopes**: Always authorize both:
    ```python
    SCOPES = [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube",
    ]
    ```
- **Initial Upload Privacy Default Contract**:
  - Automated pipelines must default to `"privacyStatus": "private"` (or `"unlisted"`) so the channel owner can review video quality, subtitles, and hook alignment in YouTube Studio before releasing to the public algorithm. Never default automated uploads to `"public"`.


