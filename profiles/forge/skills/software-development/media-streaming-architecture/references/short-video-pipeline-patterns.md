# Short-Form Video Pipeline Patterns (FFmpeg, ASR & Platform APIs)

Production-grade patterns for automated video clipping, aspect-ratio conversion, dynamic subtitle rendering, and multi-platform publishing.

---

## 1. FFmpeg 16:9 to 9:16 Blurred Background Filtergraph

When converting standard horizontal (16:9, e.g. 1920x1080 or 1280x720) source video into vertical short-form format (9:16, 1080x1920):

```bash
ffmpeg -y -ss [START_SEC] -t [DURATION] -i input.mp4 \
  -filter_complex "\
    [0:v]split=2[bg_in][fg_in];\
    [bg_in]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,boxblur=5:2,scale=1080:1920:flags=bicubic[bg];\
    [fg_in]scale=1080:-2[fg];\
    [bg][fg]overlay=(W-w)/2:(H-h)/2[merged];\
    [merged]ass='subtitles.ass'[outv]" \
  -map "[outv]" -map 0:a \
  -c:v libx264 -preset veryfast -crf 22 \
  -c:a aac -b:a 192k -movflags +faststart \
  output_short.mp4
```

### Key Engineering Points & Critical Pitfalls:
- **Input Seeking vs Filtergraph Trim Pitfall:** When `-ss [START_SEC] -t [DURATION]` is already provided as input options before `-i`, FFmpeg seeks input timestamps to 0 at demuxing. **DO NOT** add `trim=start=[START_SEC]` in `filter_complex`. Adding `trim=start=[START_SEC]` on an already-seeked stream will discard all frames until another `START_SEC` has elapsed, producing an empty stream or failing with zero output frames (`No filtered frames for output stream`).
- **Downscale-Blur-Upscale (10x Faster CPU Bokeh):** Blurring a full 1080x1920 frame (`boxblur=20:5` or `gblur`) on CPU consumes immense memory bandwidth and crawls at ~0.15x–0.3x speed. Downscale the background slice to 270x480 first, apply `boxblur=5:2`, and upscale back to 1080x1920 (`flags=bicubic`). This cuts pixel processing 16x, speeding rendering to 0.7x–1.2x realtime on CPU with zero perceptible loss in blur aesthetic.
- `split=2`: Clones the input stream into background and foreground without double-decoding.
- `scale=1080:-2`: Scales foreground to exact canvas width while maintaining original aspect ratio and even height (required by H.264).
- `ass='path'`: Burns subtitle directly into the video frame. Escaping note: In FFmpeg filtergraphs, colons `:` and backslashes `\` in Windows/Unix paths must be escaped (`\\:`).

---

## 2. Vertical Short UI Safe Zones (YouTube Shorts & TikTok)

Vertical short-form platforms overlay UI controls directly on top of the video canvas (1080x1920 px):

| Zone | Pixels (Y-axis) | Platform UI Obstruction | Recommendation |
| :--- | :--- | :--- | :--- |
| **Top Zone** | `0 - 280px` | Sound title, search icon, platform navigation | Keep clear of text & key visual focal points |
| **Right Margin** | `X: 920 - 1080px` | Like, comment, share, bookmark, audio disc | Keep clear of right-aligned text |
| **Bottom Zone** | `1520 - 1920px` | Channel handle, video title/caption, sound marquee | Avoid subtitles or titles here |
| **Speaker Boundary (16:9 FG)** | `320 - 1280px` | Center 16:9 video frame containing speaker's face & chest | MarginV=650 (Y=1270) crashes into speaker's chest/chin |
| **Golden Subtitle Zone** | `1320 - 1460px` | Clean corridor below 16:9 video & above YouTube Shorts UI | **Optimal subtitle anchor point (Y ≈ 1380px)** |

### ASS Subtitle Alignment for Golden Zone:
In ASS script styles:
- `Alignment: 2` (Bottom-Center).
- With `PlayResX: 1080` and `PlayResY: 1920`, set `MarginV: 520` (baseline at Y=1380px).
- Font: `Montserrat Black` or `Rubik Black` (avoid generic OS sans fonts like Liberation Sans).
  - **libass Fontname Resolution Pitfall:** When using custom TTF files via `fontsdir`, set `Fontname: Montserrat Black`. If set simply as `Fontname: Montserrat` with `Bold: -1`, fontconfig will prefer system-installed `Montserrat-Bold.otf` rather than the standalone `Montserrat-Black.ttf` from `fontsdir`. Explicitly naming the full style variant ensures exact matching.
- Font size: `44pt` (68pt is excessively oversized for 3-4 word lines and obstructs content).
- Outline: `4px` black outline (`Outline: 4`), `BackColour: &H90000000` (soft shadow 2px).
- Active word highlight: Neon Yellow (`&H0000E6FF`) with 108% scale pop (`{\fscx108\fscy108}`), resetting to white (`&H00FFFFFF\fscx100\fscy100`).
- Pass custom font directory to FFmpeg `ass` filter: `ass='sub.ass':fontsdir='/path/to/assets/fonts'`.

---

## 3. Dynamic Karaoke ASS Subtitle Formatting (Hormozi / MrBeast Style)

### ASS Header & Style Definition
```ini
[Script Info]
Title: Dynamic Viral Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hormozi,Arial,68,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,5,2,2,60,60,650,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
```

### Chunking Logic:
- Never show a wall of text (reduces retention).
- Group words into **2 to 4 words per event line**.
- Force uppercase text (`{\b1}PENGUSAHA SUKSES`).
- Use yellow (`&H0000FFFF`) or high-contrast white with a thick black outline (`Outline: 5`, `Shadow: 2`).

---

## 4. Transcription Hierarchy, Datacenter Anti-Bot & Word Timestamps

To ensure fast processing without bottlenecking CPU/GPU:
1. **Tier 1 (Fast & Free): YouTube Official / Auto Transcript**:
   - Use `youtube-transcript-api` to fetch pre-existing transcripts (`id`, `en`).
   - If available, avoids downloading heavy video and running local neural net transcription.
   - **v1.2.4+ API Signature & Object Model Quirks**:
     - `YouTubeTranscriptApi.list_transcripts(video_id)` is deprecated/removed; use instance method `api = YouTubeTranscriptApi(http_client=session)` and `api.list(video_id)`.
     - Items returned by `transcript.fetch()` are `FetchedTranscriptSnippet` objects, **not subscriptable dictionaries** (calling `snippet['text']` throws `TypeError: 'FetchedTranscriptSnippet' object is not subscriptable`). Always access via attributes or safe fallback: `getattr(entry, 'text', entry.get('text', ''))`.
2. **Datacenter VPS Anti-Bot Bypass (`cookies.txt` & Modern yt-dlp JS Runtimes)**:
   - YouTube blocks datacenter IP ranges with `Sign in to confirm you’re not a bot` or JavaScript challenges.
   - Export browser cookies to Netscape format (`cookies.txt`).
   - **yt-dlp Configuration**:
     - Cookiefile: `ydl_opts["cookiefile"] = "/path/to/cookies.txt"`
     - Format selection: `"format": "18/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"` (itag 18 is pre-muxed 360p/640x360 H.264+AAC for ultra-fast clipping; falls back to split video+audio mp4/m4a, single mp4, or best available stream).
     - **Modern yt-dlp JS Challenge Solver (Deno vs Node)**:
       yt-dlp requires `js_runtimes` with `{runtime: {config}}` dictionary format. Deno (`/usr/local/bin/deno`) is significantly more stable and capable than Node/qjs when solving modern YouTube client challenges.
       ```python
       ydl_opts = {
           "format": "18/bestvideo[ext=mp4]+bestaudio[ext=m4a]/b/best",
           "proxy": proxy_url,  # e.g., rotating proxy pool http://127.0.0.1:31001-31015
           "js_runtimes": {"deno": {"path": "/usr/local/bin/deno"}},
           "remote_components": ["ejs:github"],
       }
       ```
       *Note on yt-dlp Schema Pitfall:* Passing `"js_runtimes": {"node": "/usr/bin/node"}` causes `ValueError: Invalid js_runtimes format, expected a dict of {runtime: {config}}`. The inner value must be a dict containing `{"path": "..."}`.
     - **Local Proxy Pool Rotation & Bot-Check Bypass**:
       - *Root cause of datacenter blocks:* YouTube actively challenges datacenter IP blocks (Azure, AWS, GCP, Hetzner) with `Sign in to confirm you’re not a bot`, even when netscape cookies are attached.
       - *Solution:* Route yt-dlp and transcript traffic through a local rotating proxy pool (e.g. 15 Surfshark WireGuard/HTTP nodes on `http://127.0.0.1:31001` to `31015`).
       - *Format fallback:* `"18/bestvideo[ext=mp4]+bestaudio[ext=m4a]/b/best"` ensures fast retrieval of pre-muxed 360p (itag 18) when available, gracefully falling back to split video+audio MP4/M4A or best stream.
       - *Transcript Proxy Binding:* `youtube-transcript-api` must also receive the proxy via its requests `Session` or it will fail at the metadata stage before yt-dlp is even called:
         ```python
         session = requests.Session()
         session.proxies.update({"http": proxy_url, "https": proxy_url})
         ytt = YouTubeTranscriptApi(http_client=session)
         ```
   - **youtube-transcript-api**: load into session cookie jar:
     ```python
     import http.cookiejar, requests
     cj = http.cookiejar.MozillaCookieJar("/path/to/cookies.txt")
     cj.load(ignore_discard=True, ignore_expires=True)
     session = requests.Session()
     session.cookies = cj
     ytt = YouTubeTranscriptApi(http_client=session)
     ```
3. **Tier 2 (Local Fallback): faster-whisper INT8 & Audio Pre-slicing**:
   - Extract audio only as MP3 (`ffmpeg -vn -acodec libmp3lame -q:a 4 audio.mp3`).
   - **Pre-slicing for Long-form Videos (CPU Bottleneck Prevention):** Long podcasts (1h - 2h+) can stall daemon pipelines for 20-40+ minutes on multi-core CPUs. Slice the first 10-15 minutes (`ffmpeg -y -i audio.mp3 -t 600 -acodec copy slice.mp3`) before running ASR when looking for introductory viral hooks:
     ```python
     if max_transcribe_sec > 0:
         subprocess.run(["ffmpeg", "-y", "-i", audio_path, "-t", str(max_transcribe_sec), "-acodec", "copy", slice_path], check=True)
     ```
   - Run `WhisperModel("base", compute_type="int8", device="cpu")`.
   - Set `word_timestamps=True` to get word-level `start` and `end` times for karaoke highlighting.

---

## 5. Storage Hygiene & Deduplication (SQLite WAL)

- **Atomic Deduplication:**
  ```sql
  CREATE TABLE videos (
      video_id TEXT PRIMARY KEY,
      url TEXT NOT NULL,
      title TEXT,
      status TEXT NOT NULL, -- 'processing', 'completed', 'skipped', 'failed'
      processed_at TEXT NOT NULL
  );
  ```
  Check `SELECT 1 FROM videos WHERE video_id = ? AND status IN ('completed', 'processing', 'skipped')` before initiating any download.
- **Disk Space Protection:**
  Long YouTube videos (30m - 2h) take 200MB - 2GB. Always remove raw source video and audio immediately in a `finally` block once short clips are rendered to prevent `ENOSPC` (Disk Full).

---

## 6. Multi-Platform Publishing Protocols

### YouTube Data API v3 (Resumable Upload)
- Endpoint: `https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status`
- OAuth Scope: `https://www.googleapis.com/auth/youtube.upload`
- Use `MediaFileUpload(..., resumable=True, chunksize=4*1024*1024)` to tolerate network drops.
- Append `#Shorts` in title or description to trigger short-form video shelf indexing.

### TikTok Content Posting API v2
- Endpoint: `POST https://open.tiktokapis.com/v2/post/publish/video/init/`
- Header: `Authorization: Bearer <ACCESS_TOKEN>`, `Content-Type: application/json; charset=UTF-8`
- Payload:
  ```json
  {
    "post_info": {
      "title": "Title max 150 chars",
      "privacy_level": "PUBLIC_TO_EVERYONE",
      "disable_duet": false,
      "disable_stitch": false,
      "disable_comment": false,
      "video_cover_timestamp_ms": 1000
    },
    "source_info": {
      "source": "FILE_UPLOAD",
      "video_size": 12345678,
      "chunk_size": 12345678,
      "total_chunk_count": 1
    }
  }
  ```
- Binary Upload: Take `upload_url` from response and execute HTTP `PUT` with header `Content-Range: bytes 0-(size-1)/size`.

---

## 8. Five Viral Visual Hook Engines (FFmpeg & Vector ASS)

To capture immediate viewer retention in the critical first 1-3 seconds of a short-form video:

### Hook 1: Camera Stomp Shockwave (0.0s - 0.6s)
- **Visual:** Damped mathematical oscillation screen shake in FFmpeg `crop` filter without black border reveal (pre-scaled to 1140x2026):
  ```
  scale=1140:2026,crop=1080:1920:'(in_w-out_w)/2+26*exp(-7*t)*sin(36*PI*t)*lte(t,0.6)':'(in_h-out_h)/2+32*exp(-7*t)*cos(36*PI*t)*lte(t,0.6)'
  ```
- **Audio:** Synthesized 55Hz sub-bass thud SFX via `aevalsrc` mixed into track 0:a via `amix`:
  ```
  -f lavfi -i aevalsrc=sin(2*PI*55*t)*exp(-8*t)*0.85:s=44100:d=0.7
  -filter_complex "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=0[aout]"
  ```

### Hook 2: Paper Tear Reveal (0.0s - 0.8s)
- **Visual:** Two jagged polygon vector halves in ASS (`\p1`) sliding apart to reveal the video underneath:
  - Left half: `{\move(0,0,-920,0,0,800)\p1}m 0 0 l 550 0 l 530 180 ... l 0 1920{\p0}`
  - Right half: `{\move(0,0,920,0,0,800)\p1}m 1080 0 l 550 0 l 530 180 ... l 1080 1920{\p0}`
  - Completely self-contained in ASS; zero external PNG/video asset dependencies.

### Hook 3: Breaking News Style (0.0s - 3.0s)
- **Visual:** Top crimson banner `[ ⚠ BREAKING NEWS ⚠ ]` (Y: 110-220px) + bottom ticker bar `[ 🔴 VIRAL UPDATE • SAKSIKAN SAMPAI SELESAI ]` (Y: 1440-1520px) rendered as ASS vector background boxes + bold text.
- Clean vector layout layered above background and below subtitle safe zone.

### Hook 4: Content Transition & Zoom Punch-In (115% Snap Cut)
- **Visual:** Dynamic FFmpeg `crop` punch-in at 115% (crop 939x1669) for `t <= 1.5s`, snapping cleanly back to 100% (1080x1920), with an optional micro-zoom punchline (108%, 1000x1777) around mid-video:
  ```
  crop='if(lte(t,1.5), 939, if(between(t,5.0,6.2), 1000, 1080))':'if(lte(t,1.5), 1669, if(between(t,5.0,6.2), 1777, 1920))':(in_w-out_w)/2:(in_h-out_h)/2,scale=1080:1920
  ```

### Hook 5: Glitch Tape Rewind (0.0s - 0.6s)
- **Visual:** Chromatic aberration via FFmpeg `rgbashift=rh=-18:bv=18:gh=8:enable='between(t,0,0.6)'` coupled with retro VHS OSD `⏪ REW 00:00:02` and horizontal scanline vector pulses in ASS.

