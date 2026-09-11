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

## 7. Selection Core: Discovery, Language Gate, Isolated Alignment & Semantic Curation

Automated short-form clipping pipelines must reject unsuitable long-form source material early and avoid wasteful compute:

### 1. Zero-Download Discovery & Source Filtering
- **Never download the full video at discovery stage.** Use `yt-dlp` with `skip_download: True` (`--skip-download`) or YouTube Data API v3 (`snippet,contentDetails,statistics`) to fetch metadata only.
- **Early Rejection Gates:**
  - `duration < 180s`: Reject immediately (`DURATION_TOO_SHORT`). Videos under 3 minutes are already clips/shorts, not long-form discussion.
  - `duration > 14400s` (4 hours): Reject immediately (`DURATION_TOO_LONG`). Overlong marathon livestreams risk OOM during transcript ingestion and dilute hook density.
  - `is_live` / `is_upcoming` / `is_private`: Reject immediately (`IS_LIVE`, `IS_UPCOMING`, `IS_PRIVATE`). Scheduled premieres and ongoing streams lack static timeline bounds.
  - **Comprehensive Non-Speech Rejection (`NO_CLEAR_SPEECH`):** Regex match combined title and description against:
    * Music / covers: `official music video`, `official (?:audio|mv|video)`, `lyric(?:s)? video`, `full album`, `lofi`, `instrumental`, `karaoke`, `dj remix`, `cover lagu`, `compilation lagu`.
    * Movies / streaming: `full movie`, `film bioskop full`, `film full movie`.
    * No-commentary gameplay: `no commentary`, `gameplay (?:walkthrough )?no commentary`, `no speech`, `no talking`, `walkthrough no voice`.
    * Ambient / sensory: `asmr`, `mukbang asmr`, `ambience`, `white noise`, `relaxing sound`.
  - **Dual-Layer Deduplication (`DUPLICATE_VIDEO`):** Check video ID against both in-memory session cache (`processed_video_ids`) and SQLite database (`SELECT 1 FROM videos WHERE video_id = ? AND status IN ('completed', 'processing', 'skipped')`).
- **Direct Searcher-to-Filter Binding:** Wire `SourceFilter` directly into discovery queries (`search_candidates`, `search_videos(..., filter_eligible=True)`) so downstream ingestors only receive pre-vetted eligible videos.
- **Pydantic Model Interoperability:** When refactoring metadata models (`VideoSourceMeta` vs legacy `VideoMetadata`, `EligibilityResult` vs `SourceFilterVerdict`), use `@model_validator(mode="before")` to bidirectionally sync field aliases (`duration_sec` <-> `duration`, `is_eligible` <-> `accepted`, `channel` <-> `channel_title`) to prevent regressions across existing test harnesses.
- **Circular Import Decoupling:** Decouple `Searcher` and `SourceFilter` circular dependencies by declaring metadata schema models first, or importing `SourceFilter` lazily inside `Searcher.__init__`.

### 2. Spoken Language Gate & Code-Switching Invariants
- **Deterministic Token Lexicon:** Evaluate speech transcript tokens against combined Indonesian formal + colloquial/slang dictionary (`gue`, `lu`, `bang`, `boskuu`, `mantap`, `wkwk`, `anjir`, `cuy`, `nggak`, `gitu`, `bikin`, dll).
- **Natural Code-Switching Allowance:** Do NOT reject conversational Indonesian mixed with English tech/business terms (e.g., *"Gue waktu itu basically belum ngerti PMF dan lagi review pitch deck"*). Qualify content as Indonesian whenever Indonesian tokens outnumber English tokens and meet minimum ratio (`id_ratio >= 0.10`).
- **Strict English / Foreign Dominance Rejection:** Reject if English tokens strictly dominate (`en_ratio >= 0.25` and `en_matches > id_matches`) or if speech matches neither lexicon. Fail-safe reject on empty transcripts.

### 3. Decoupled Transcription & Isolated Window Word Alignment
- **Phrase-Level Longform Ingestion:** Store full long-form transcript at phrase level (`[{"start": 120.4, "end": 124.8, "duration": 4.4, "text": "..."}]`). Use official YouTube captions where available; fallback to `faster-whisper` (Indonesian, INT8 base/small).
- **Compute Optimization (Word Alignment Pitfall):** Never run word-level alignment across a 1-2 hour long-form source video. Word-level alignment is strictly deferred to the single selected candidate window (30-55s). Slice the candidate audio with `ffmpeg -ss [start] -i input.mp4 -t [duration] -vn slice.wav`, run Whisper with `word_timestamps=True`, and re-offset word timestamps by `+ start_sec`.

### 4. Natural Pause Candidate Windowing & Semantic Scoring
- **Silence & Sentence Boundaries:** Slice phrase segments into raw candidate windows (25–70s) using silence gaps (`gap = next.start - current.end >= 0.5s`) and sentence punctuation (`.`, `!`, `?`).
- **The Self-Contained Test (Gemini via 9router):** When scoring viral potential (`hook_score`, `payoff_score`, `overall_score`), LLM must explicitly answer: *"Does this segment make sense without the rest of the video?"*
- **NO GOOD CLIP FOUND Contract:** If all candidate segments rely on missing outside context (`self_contained_score < 70`) or lack a hook, the pipeline must return `NO GOOD CLIP FOUND` and terminate cleanly without rendering low-quality filler.

### 5. Dual-Layer Visual Guard & Strict Duration Refiner
- **Layer 1 (Local OpenCV):** Check scene cuts (histogram difference), blank/black frames (`blank_ratio <= 0.10`), face/subject presence (`presence >= 0.70`), and burned-in subtitle interference (lower 30% Canny edge density).
- **Layer 2 (Multimodal Gemini via 9router):** Downscale 4-5 representative keyframes to 480x270 JPEG base64 and audit visual continuity and subject visibility.
- **Boundary Refiner & Laughter Buffer:** Snap start to speech onset (or adjacent scene cut) with 50ms breath pre-roll. Snap end to completed sentence and add 0.3-0.7s laughter/reaction buffer. Strictly enforce final duration between **30.0s and 55.0s**; reject candidate if boundaries cannot satisfy this target.

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

---

## 9. Stable Editing Core: Scene-Static Framing, Subtitle Policy & Mastering (Phase B)

Production guidelines for deterministic 9:16 portrait framing, subtitle classification, broadcast audio mastering, and clean filtergraph execution:

### 1. Scene-Static Portrait Framing (Zero Continuous Camera Tracking)
- **Why Continuous Tracking Fails:** Moving average smoothing or continuous camera panning produces dizzying micro-jitter, camera drift during subtle body posture shifts, and unnatural float.
- **The Scene-Static Invariant:**
  * Scene 1: Detect face/speaker -> compute optimal 9:16 crop window -> **HOLD CONSTANT** for the entire scene segment.
  * Hard Scene Cut -> Scene 2: Detect face/speaker -> compute new 9:16 crop window -> **HOLD CONSTANT** for Scene 2.
  * Every scene cut segment possesses exactly ONE static crop window (`SceneCrop(scene_start, scene_end, crop_x, crop_y, crop_w, crop_h)`).
- **Single Speaker Framing Rules:**
  * Head + upper torso composition: Keep full source frame height $H$ (`crop_h = H`, `crop_w = round(H * 9 / 16)`).
  * Consistent headroom: Center horizontally around speaker face ($fc_x = fx + fw/2$), with $crop\_y = 0$, ensuring natural headroom without decapitation or slicing the upper torso.
  * Avoid tight face zooms: Never digitally zoom tightly on speaker's face; maintain natural interview/podcast portrait distance.
- **Multi-Speaker Framing Rules:**
  * **Zero Active-Speaker Switching:** Never alternate crop windows back-and-forth between speakers within the same scene.
  * **Safe Two-Person Shot:** If horizontal bounding span of all speakers plus margin fits within 9:16 width (`(max_x - min_x) + margin <= crop_w`), center the 9:16 crop around the group center.
  * **Wide Spread Fallback:** If speakers are seated too far apart to fit in 9:16, fall back to `SAFE_FULL_FRAME` (preserve 100% original 16:9 width with blurred background) or reject the candidate (`REJECT`).
- **Even Integer Coordinate Invariant:** FFmpeg H.264 codecs (`yuv420p`) strictly require even integers for `crop_x, crop_y, crop_w, crop_h`. Always enforce `v = (v // 2) * 2`.

### 2. Subtitle Source Policy Classification (Bab 13)
- **Classification Hierarchy:**
  1. `EMBEDDED_TRACK`: If container has subtitle stream (`ffprobe -select_streams s`), extract track directly (`ffmpeg -i input.mp4 -map 0:s:0 out.ass`) without re-transcribing.
  2. `BURNED_IN`: If bottom 30% of frames have text edge density (Canny + horizontal morphology), **NEVER run OCR and NEVER attempt weird composite masking**. Use `SAFE_FULL_FRAME` layout preserving full frame width so existing burned subtitles remain complete and uncropped; if safe full-frame is disallowed, reject candidate (`REJECT`).
  3. `NONE`: Generate Subtitle V2 in ASS format.
- **Subtitle V2 Formatting Contract:**
  * Clean 2 to 5 words per phrase chunk.
  * 1 to 2 balanced lines per dialogue event (split with `\N`).
  * High-contrast white font (`&H00FFFFFF`) with black outline (`&H00000000`).
  * Bottom safe-zone: `MarginV=520` on 1080x1920 canvas to avoid bottom UI obstruction.

### 3. Voice-First Broadcast Audio Mastering (Zero SFX)
- **Mastering Targets:** AAC, 48 kHz, stereo, target -16.0 LUFS integrated loudness, true peak <= -1.5 dB, LRA = 11.
- **Canonical FFmpeg Filter Chain:**
  ```text
  highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=11,aformat=sample_rates=48000:channel_layouts=stereo
  ```
- **Zero SFX Rule:** No sound effects, whooshes, bell rings, or intrusive background music. Speech clarity and intelligible dynamics are strictly preserved.

### 4. Clean Multi-Segment Concat & Dynamic Punch-in Filtergraph
- **Multi-Scene Cut Concat Filtergraph:**
  For $N$ scene-static cuts, trim, reset PTS, crop, scale to 1080x1920, and concat:
  ```text
  [0:v]trim=start=s0:end=e0,setpts=PTS-STARTPTS,crop=w0:h0:x0:y0,scale=1080:1920[vseg_0];
  [0:v]trim=start=s1:end=e1,setpts=PTS-STARTPTS,crop=w1:h1:x1:y1,scale=1080:1920[vseg_1];
  [vseg_0][vseg_1]concat=n=2:v=1:a=0[v_base]
  ```
- **Punch-In Policy & Zoom Expression:**
  * Policy: Strictly max 0–2 punch-ins per clip, scale 1.04 to 1.08, duration 0.6s to 1.5s, default empty if in doubt.
  * Time-conditional zoom crop expression on 1080x1920 canvas:
    ```text
    [v_base]crop='if(between(t,t1,t2),pw,1080)':'if(between(t,t1,t2),ph,1920)':'(in_w-out_w)/2':'(in_h-out_h)/2',scale=1080:1920[v_punch]
    ```
    where $pw = \text{round}(1080 / \text{scale})$ and $ph = \text{round}(1920 / \text{scale})$ coerced to even integers.

### 5. Implementation & Test Harness Pitfalls
- **Pydantic V2 Field Constraints vs Validator Clamping:** When implementing policy-based clamping in Pydantic V2 (e.g. clamping scale to [1.04, 1.08] or duration to [0.6, 1.5]), do NOT put conflicting `ge` / `le` constraints in `Field(...)` unless `@field_validator(..., mode="before")` is used. Core Pydantic field validators run before default `mode="after"` validators and will fail with `ValidationError` before your clamping logic executes.
- **Input Duration Truncation (`-t` before `-i`) vs Audio Filter Lookahead (`loudnorm`):** When rendering clips with complex audio mastering filtergraphs (`highpass,loudnorm,aformat`), placing `-t [duration]` as an *input option* (before `-i`) prematurely halts demuxer packet feeding at `duration` seconds. Because EBU R128 `loudnorm` requires an internal lookahead measurement buffer (~3s), demuxer cut-off on short test slices (e.g. 2s) causes the audio filter to output zero audio frames before EOF, creating a video-only MP4 container without an audio track (`no_audio_stream`). Placing `-t [duration]` as an *output option* (after `-i` and filtergraph, before the output file path) allows the demuxer to feed sufficient lookahead frames into the filtergraph and cleanly truncates the final multiplexed output container to the exact target duration.
- **FFmpeg `+faststart` Second Pass File Lock / Race in Pytest:** `-movflags +faststart` shifts the `moov` atom to the beginning of the MP4 file in a second pass by re-opening the output file. In automated test suites, never render test outputs to shared static paths like `/tmp/output.mp4` because concurrent test runs or background cleaners will touch/delete the file during the second pass, causing `Unable to re-open output file for shifting data / Error writing trailer: No such file or directory`. Always use pytest's `tmp_path` fixture (`tmp_path / "output.mp4"`) for isolated per-test workspaces.

---

## 10. Three-Tier Quality Control Gate: Technical, Visual & Perceptual (Phase C)

Production short-form video pipelines must never rely solely on container metadata or subjective spot-checks. Automated release gating requires three orthogonal verification layers before media is passed to the platform uploader:

### 1. Tier 1: Technical QC (`TechnicalQC` / Bab 16.1)
- **Container & Stream Spec Invariants:**
  * File existence & size: `file_size > 100 * 1024` bytes (> 100KB). Rejects empty, truncated, or header-only files.
  * Video stream: Codec strictly `h264` (`avc1`), exact vertical resolution `1080x1920`.
  * Audio stream: Codec strictly `aac`, sample rate strictly `48000` Hz (48kHz stereo).
  * Exact duration boundaries: Target [30.0s, 55.0s] with +/- 0.5s tolerance (`29.5s <= duration <= 55.5s`).
- **Bitstream Corruption Validation via Null Muxer:**
  Execute `ffmpeg -v error -xerror -i <file> -f null -`. FFmpeg decodes all video packets without rendering. Any corrupted macroblock, truncated NAL unit, or audio packet loss causes non-zero exit code or stderr output, failing the technical gate before downstream upload attempts.

### 2. Tier 2: Deterministic Local Visual QC (`VisualQC` / Bab 16.2)
- **Periodic Frame Sampling:** Sample across duration at 2.0s intervals with `min_frames = 10`.
- **Blank / Black / White Frames:** Compute grayscale mean pixel intensity $\mu$. Mark blank if $\mu < 5.0$ (black screen freeze) or $\mu > 250.0$ (white blown out). Reject if blank frames detected.
- **Black / White Flash Detection:** Detect single-frame isolated drops ($\mu_i < 5.0$ between normal frames $\mu_{i-1}, \mu_{i+1} > 20.0$) or luminance spikes ($|\mu_i - \mu_{i-1}| > 120$ and $|\mu_i - \mu_{i+1}| > 120$ with $|\mu_{i-1} - \mu_{i+1}| < 60$).
- **Subject Presence & Face Framing:**
  * Detect faces via OpenCV YuNet ONNX (`face_detection_yunet_2023mar.onnx`) with central vertical silhouette contour fallback (central 20%-80% X, 10%-85% Y). Require `subject_present_ratio >= 0.70`.
  * **Face Cut Badly Guard:** Check detected face box $(x, y, w, h)$ on canvas height $H$: reject if top boundary is truncated without headroom ($y \le 0$ or $y < 0.02 H$) or bottom boundary is truncated ($y + h \ge H - 5$).
- **Subtitle Overlap & Stuck Subtitles:**
  * Isolate subtitle band ($Y = 0.55 H$ to $0.85 H$).
  * Check consecutive sampled frames: if subtitle edge map remains unchanged across $> 4$ consecutive samples ($> 8$s of frozen text), flag stuck subtitle.
  * Check multi-line collisions: detect horizontal text contour bounding boxes and flag vertical overlap/collision.
- **Boundary Safe-Zone Enforcement:**
  * Subtitles are strictly forbidden in the **Top 15%** ($Y < 0.15 H = 288$px) and **Bottom 20%** ($Y > 0.80 H = 1536$px) UI danger zones. Detect high-contrast horizontal text bars in these strips; flag `subtitle_safe = False` if text is present.

### 3. Tier 3: Multimodal Perceptual QC (`PerceptualQC` / Bab 16.3)
- **3x3 Contact Sheet Generation:** Extract 9 evenly distributed frames across the clip, resize to 240x426 cells, overlay timestamp badges, and stitch into a single 720x1278 JPEG base64 image.
- **Gemini Visual Director via 9router (`http://127.0.0.1:20128/v1`):** Send contact sheet alongside transcript text, EditPlan contract, and Tier 1 & Tier 2 QC facts.
- **Evaluation Contract:** Returns `publishable: bool`, `score: int` (0-100), `blocking_issues: List[str]`, `notes: str`.
- **Zero-Tolerance Blocking Issue Policy:** If `blocking_issues` contains any item (e.g. "Speaker face decapitated", "Subtitles occluded by bottom UI"), clip is immediately rejected / skipped (`publishable = False, passed = False`) and auto-upload is blocked.
- **Deterministic Repair Budget (Max 1 Attempt):** If blocking issues are repairable (e.g. adjust crop window offset or adjust subtitle vertical margin), allow at most 1 deterministic repair attempt. Re-evaluate once with `repair_attempted = True`; if still failing, permanently reject to prevent infinite repair loops.
- **Offline / Timeout Fallback:** If 9router connection fails or times out, fall back deterministically: approve only if Tier 1 and Tier 2 passed without error; otherwise reject.

### 4. Implementation & CV Pitfalls
- **OpenCV Headless vs CascadeClassifier Pitfall:** In headless Linux server environments, `cv2.CascadeClassifier` may fail with `AttributeError: module 'cv2' has no attribute 'CascadeClassifier'` or miss XML models. Always use `cv2.FaceDetectorYN_create` with the ONNX YuNet model, paired with a central silhouette contour/edge energy fallback.
- **Vertical Canvas Subtitle Density Dilution vs Solid Polygons:** In vertical 1080x1920 canvas, the subtitle ROI ($0.55 H$ to $0.85 H$, ~622,080 px) dilutes the edge density of a single short line of text (~1500 edge px = 0.0024 density). Hardcoding a high threshold like `edge_density > 0.01` causes complete detection misses for valid single-line subtitles. Use a relaxed density threshold (`edge_density > 0.001` or `np.count_nonzero(edges) > 300`) coupled with morphological glyph contour clustering ($8 \le h \le 110$, $4 \le w \le 150$, $\ge 4$ contours). Checking for text glyph clusters rather than raw edge pixel count completely eliminates false positive stuck subtitle errors on solid geometric shapes while reliably detecting single-line text.
- **Test Fixture Media Generation Speedup & Deterministic Caching:** Encoding a 30s 1080x1920 video at 30 fps with FFmpeg libx264 encodes 900 frames and takes 6-15 seconds per test even with `-preset ultrafast`, causing test suite timeouts. Three optimizations keep 20+ media QC tests under 10 seconds:
  1. *Framerate throttling:* Set `rate=10` (or lower) in the lavfi source filter when framerate itself is not being asserted, cutting frame count from 900 to 300 and dropping encode time by ~65%.
  2. *Deterministic disk caching:* Hash generation parameters (duration, resolution, codecs, sample rate, bitrate, filter flags) with MD5 and cache the rendered test MP4 to disk (e.g. `/tmp/synthetic_video_cache/syn_<md5>.mp4`). Sibling test cases copy the cached artifact via `shutil.copyfile` in sub-millisecond time.
  3. *Contact sheet interpolation:* Use `cv2.INTER_LINEAR` instead of `cv2.INTER_AREA` when resizing 1080x1920 frames down to 240x426 cells for contact sheet grids; it is 4-5x faster on CPU with zero perceptible loss in multimodal inspection quality.

---

## 11. Full Auto Production Pipeline, State Machine & Strict Upload Gate (Phase D)

Production-grade automated clipping engines require formal state machines, guard invariants, and multi-gate release policies before side effects:

### 1. 11 Happy Path States & 6 Terminal Rejection States (Bab 18 & 21)
- **Sequential Happy Progression:**
  `discovered` -> `eligible` -> `transcribed` -> `candidates_found` -> `candidate_selected` -> `visual_verified` -> `rendering` -> `rendered` -> `qc_passed` -> `uploading` -> `completed`.
- **6 Domain-Specific Terminal Rejects:**
  * `rejected_language` (from discovered/eligible/transcribed if language gate fails).
  * `no_good_clip` (from candidates_found/candidate_selected if semantic scorer or boundary refiner fails).
  * `rejected_visual` (from candidate_selected/visual_verified if OpenCV or Visual Director rejects).
  * `render_failed` (from rendering if FFmpeg filtergraph fails).
  * `qc_failed` (from rendered if Three-Tier QC fails).
  * `upload_failed` (from uploading if platform upload fails).
- **Terminal Immutability Guard:** Terminal states (`completed` and all 6 reject states) have zero outbound transitions. Any subsequent transition attempt raises `InvalidStateTransitionError`.

### 2. Mandatory Upload Guard Invariant
- **Rule:** Transition to `uploading` is STRICTLY FORBIDDEN unless current state is `qc_passed`.
- **Mechanism:** Direct jumps to `uploading` from `rendered`, `rendering`, or `discovered` violate pipeline safety and must raise `GuardInvariantError`.
- **Bypass Exemption:** A video may transition from `qc_passed` directly to `completed` if `skip_upload=True` or in local-only export mode.

### 3. Strict Upload Gate (8 Orthogonal Preconditions / Bab 17)
- **All-or-Nothing Verification:**
  Evaluate `all_gates_pass(language_gate, semantic_clip_gate, visual_viability_gate, boundary_gate, render_success, technical_qc, visual_qc, perceptual_qc)`.
  If ANY gate evaluates to `False`, immediately raise `UploadGateRejectedError` with a list of failed gates and abort platform publishing.
- **Dry-Run Testing Support:** The uploader must accept a `dry_run` flag. In dry-run mode, validate video file existence, file size (> 100KB), and format the title with `#Shorts`, returning a simulated upload result (`https://youtube.com/shorts/dry_run_<hash>`) without consuming platform API quotas.

### 4. Clipped Subtitle Relative Timestamp Normalization Pitfall
- **Pitfall:** Passing long-form transcript timestamps directly into subtitle generation for a cut clip (`[clip_start, clip_end]`).
- **Mechanism:** In cut video slices, the demuxer or FFmpeg trim resets container presentation timestamps (PTS) to start at `0.0`. If ASS dialogue events retain original timestamps (e.g. `Dialogue: 0,00:04:15.20,00:04:18.50,...`), the ASS renderer will not render any subtitles during the 30-55s clip playback because the dialogue events are scheduled 4 minutes into the future.
- **Rule:** Always normalize dialogue timestamps relative to `clip_start`:
  `start = max(0.0, round(seg.start - clip_start, 2))`, `end = max(0.0, round(seg.end - clip_start, 2))`.

---

## 12. Hybrid Subtitle Accuracy Engine & Multimodal Verifier (Auto Clipper V3.1)

Production patterns for eliminating phonetic hallucinations ("mukabomi" -> "muka bumi", "huayu" -> "who are you", "nama tiga" -> "nomor tiga") while maintaining 100% audio-derived timing:

### 1. Division of Responsibility
- **Whisper (ASR) = WHEN (KAPAN):** Detects exact word-level boundaries and acoustic speech intervals.
- **Gemini (Multimodal LLM via 9router) = WHAT (APA):** Understands true spoken dialogue directly from the candidate MP4 video+audio, resolving slang, proper nouns, and multilingual code-switching without paraphrasing.
- **TranscriptFusion = ALIGNMENT:** Fuses ASR word timestamps with Gemini verbatim corrections into canonical phrase chunks (2–5 words) using sequence matching and audio-derived spans.
- **FFmpeg / libass = RENDER:** Burns subtitles with zero event overlap, single lane, and silence clearance.
- **Gemini Final Video QC = AUDIT GATE:** Evaluates final rendered video directly, rejecting publication if text inaccuracies or subtitle overlaps exist.

### 2. Faster-Whisper CPU Runtime & Storage Partitioning
- **Large-v3 on CPU INT8:** `faster-whisper` large-v3 with `compute_type="int8"`, `cpu_threads=4`, and `vad_filter=True` runs stably on modern 4-core CPUs (~60-80s per 40s clip), dramatically reducing phonetic errors compared to base/small models.
- **Root Filesystem ENOSPC Pitfall (`HF_HOME`):**
  - *Pitfall:* Faster-whisper defaults to downloading weights to `~/.cache/huggingface/hub/` on `/` (root partition). On VPS/cloud environments with small root volumes (<50GB), downloading large-v3 (3GB+) throws `IO Error: No space left on device (os error 28)`.
  - *Rule:* Always point `HF_HOME` or model path to a dedicated persistent high-capacity mount (`/mnt/storage/.../.cache/huggingface`) before initializing `WhisperModel`.
- **In-Memory Whisper Model Caching (Memory Churn & Cgroup Killer Pitfall):**
  - *Pitfall:* Re-instantiating `WhisperModel` inside loop iterations or per candidate clip reallocates 1.5–3.5GB of RAM each time, causing memory fragmentation and triggering background worker cgroup OOM kills (e.g. 4GB memory limits).
  - *Rule:* Store loaded models in a global module-level dictionary `_WHISPER_MODEL_CACHE[(model_path, device, compute_type, cpu_threads)]`. Subsequent clips reuse the already-loaded model instantly, saving 20–30 seconds of model init time per clip.
- **Context & Hotwords Injection (Whisper Prompt-Skipping Pitfall):**
  - *Pitfall:* Passing raw source transcript excerpts or dialogue lines into Whisper's `initial_prompt` causes Whisper's autoregressive decoder to treat the prompt as preceding context that has already been spoken. When audio matches the beginning of the prompt, Whisper skips transcribing the first 10-18+ seconds of audio, producing truncated subtitles that fail QC.
  - *Rule:* Only inject concise topic keywords, channel name, and hotwords (e.g. "Mas Bilal, Kak Jeje, self love, muka bumi, nomor tiga") into `initial_prompt`. Never feed full transcript excerpts.

### 3. Dedicated Gemini Native-Video Transcript Verifier via 9router
- Call model `ag/gemini-3.8-flash-high` through 9router (`http://127.0.0.1:20128/v1`).
- Pass candidate MP4 clip (30-55s) directly as `data:video/mp4;base64,...` alongside ASR words transcript and source captions.
- **Strict Verbatim System Prompt:**
  ```text
  Correct EXACTLY what is spoken.
  Preserve Indonesian slang.
  Preserve English code-switching.
  Do not paraphrase.
  Do not summarize.
  Do not censor.
  Do not invent words.
  Use provided transcripts only as hints.
  Resolve disagreements by listening to the video/audio.
  Format answer strictly as valid JSON.
  ```
- Parse structured JSON output containing `corrected_full_text`, `segments` (`asr_text`, `corrected_text`, `confidence`), and `overall_confidence`.

### 4. Transcript Fusion Without Synthetic Interpolation
- **Zero Synthetic Timing Invariant:** Gemini must never synthesize per-word timing. Artificial interpolation destroys natural speech cadence and creates timing drift.
- **Phrase-First Chunking & Audio-Span Locking (SequenceMatcher Compression Pitfall):**
  - *Pitfall:* Running unconstrained token-level `difflib.SequenceMatcher` replacement directly on ASR word tokens compresses inserted or replaced tokens into synthetic 0.05s intervals. If an inserted word occurs at the very beginning (before index 0 matches), the entire opening speech (0–10s) gets dropped or squished into a fraction of a second.
  - *Rule:* Chunk `asr_words` into natural 2–5 word phrases FIRST using audio boundaries (`_chunk_asr_words_directly`). Every phrase's `start` and `end` timestamps are permanently locked to Whisper's audio timestamps and NEVER shrink or compress. Then map tokens from `corrected_full_text` directly to their owning phrase index via SequenceMatcher opcodes without altering audio time boundaries.
- **Segment Override Deduplication Guard:**
  - *Pitfall:* When applying secondary `segments` or `corrections` overrides on top of full-text aligned phrases, naive substring replacement re-replaces already-corrected words (e.g. turning "Gini, ketika saya ngasih" into "Gini, Gini, ketika saya ngasih").
  - *Rule:* Check whether `clean(fixed)` is already present in `clean(phrase["text"])` before applying regex or substring replacement; skip if already applied.
- **Candidate Window Pre-Slicing for Multimodal Verification:**
  - *Pitfall:* Passing the full source video (100MB–1GB+) into `llm_client.video_completion` or `generate_ass_from_words(media_path)` causes HTTP 400 Payload Too Large and produces absolute timestamps rather than clip-local timestamps (0.0s).
  - *Rule:* If `start_sec > 0` or `duration_sec` is specified, always pre-slice the exact candidate window (`ffmpeg -y -ss start -i input -t duration -c:v libx264 -preset ultrafast -c:a aac tmp_slice.mp4`). Pass `tmp_slice.mp4` to both faster-whisper and Gemini, and unlink in a `finally` block.
- **ASS Multi-line Wrap Assertion Pitfall in Tests:**
  - *Pitfall:* Asserting plain multi-word strings (`assert "who are you?" in ass_content`) fails in automated tests when phrase length $> 3$ words because the formatter wraps lines with the ASS newline separator `\N` (e.g. `who\Nare you?`).
  - *Rule:* Assert distinct constituent tokens (`assert "who" in ass_content and "are you?" in ass_content`) or match the exact `\N` wrapped phrase format.

### 5. ASS Subtitle Timeline Invariants
- **Zero Event Overlap:** Guarantee `ev[i].end <= ev[i+1].start - 0.02` (20ms epsilon). Single caption lane (Layer 0) only; no concurrent overlapping dialogue events.
- **Silence Clearance:** Clear subtitles during speech gaps $> 0.30$s. Clamp linger to 80-120ms without intruding into pauses.
- **Multi-line Balancing:** Split phrases with $> 3$ words into two balanced lines using ASS newline `\N`.
- **Default Style Contract:** Font `Montserrat`, size `46`, `MarginV: 440` (or `520` depending on safe-zone), `MarginH: 90`, `Outline: 4`, `Shadow: 2`.

### 6. Strict Multimodal Video QC Gate (`GeminiVideoQCResult`)
- Inspect final rendered MP4 via Gemini 3.8 Flash before publication.
- Structured schema must explicitly return:
  * `subtitle_timing`: `"PASS"` / `"FAIL"`
  * `subtitle_overlap`: `"PASS"` / `"FAIL"`
  * `subtitle_linger`: `"PASS"` / `"FAIL"`
  * `subtitle_text_accuracy`: `"PASS"` / `"FAIL"`
  * `obvious_transcription_errors`: List of `{"shown": ..., "heard": ..., "approx_time": ...}`
  * `blocking_reasons`: List of strings
  * `score`: integer (0–100)
  * `passed`: boolean
- **Fail-Closed Rule:** If `obvious_transcription_errors` is non-empty or any subtitle sub-check fails, set `passed = False` and abort auto-publishing.
- **Multimodal QC List Parsing Robustness (`str` vs `dict` Items):** Multimodal LLMs often return list items as plain strings (`["word X instead of Y"]`) rather than structured dicts (`[{"shown": "X", "heard": "Y"}]`). Always guard with `isinstance(err, dict)` before calling `.get()`; falling back to `str(err)` prevents unhandled `AttributeError` in the QC gate.
- **Negative Example Hallucination Pitfall in QC Prompts:**
  - *Pitfall:* Including specific target words as negative examples in the system prompt (e.g. "misal 'peren pertama' bukannya 'pertama'") causes multimodal LLMs to recall these exact examples and falsely report that the video subtitle contains them, failing videos whose text is actually 100% correct.
  - *Rule:* Never include specific video words as negative examples in the evaluator system prompt. Keep the prompt instructions purely objective and general.
- **Sans-Serif Font Stroke / Outline Blurring on Lowercase 'i':**
  - *Pitfall:* Heavy bold fonts (Montserrat Bold, 46pt) rendered with thick outlines (Outline >= 4px) expand the black outline on the dot and stem by 4px each, bridging the 2px gap and merging the dot into the stem. When adjacent to 'l' (as in "mengenali"), 'li' visually appears as double 'l' ("mengenall") to downsampled video inspection models.
  - *Rule:* Provide an explicit typography note in the QC prompt ("Catatan tipografi: Huruf 'i' kecil pada font sans-serif memiliki titik di atas garis vertikal pendek dan jangan salah diidentifikasi sebagai 'l'"), inject full reference transcript text without truncation, and use moderate outline (2–2.5px) or add letter spacing (`Spacing: 1`).
- **Transient 503 Server Error Backoff for Native Video Calls:** Direct video completions with 30-55s video base64 payloads to local proxies (9router) can intermittently return HTTP 503 (Server Unavailable) due to upstream rate limits. Implement bounded retries (2-3 attempts with 5s backoff) and set HTTP timeout to at least 240s for video payloads.

---

## 13. Double Subtitle Prevention & Natural Sentence Ending Engine (Auto Clipper V3.1)

Production patterns for preventing duplicate subtitle overlays on pre-captioned footage and eliminating mid-sentence speech truncations in automated short-form clipping:

### 1. The Root Cause of Double Subtitles
- **Detector Disagreement:** Local OpenCV heuristic detectors (Canny edge density, Otsu binarization in bottom 25% ROI) check for sharp horizontal text gradients. Videos with animated subtitles, low-contrast text boxes, non-standard fonts, or subtitles placed mid-screen often report `NONE` locally.
- **The False-Negative Trap:** If the orchestrator assumes `local == NONE` means "clean footage" without consulting multimodal vision models, it generates new ASS subtitles and overlays them directly over the source's pre-existing burned-in subtitles.
- **Strict Evidence-Based Subtitle Policy (Zero-Guessing Invariant):**
  * `HAS_SUBTITLE -> SOURCE_EXISTING`: If ffprobe detects an embedded subtitle stream OR Gemini Native Video preflight confirms visible subtitles on screen, assign `subtitle_policy = "SOURCE_EXISTING"`. Attach exactly ZERO ASS subtitle filters to the FFmpeg filtergraph.
  * `NO_SUBTITLE -> GENERATE`: If both local detector and Gemini Native Video confirm no visible subtitles, assign `subtitle_policy = "GENERATE"` and produce Hybrid Subtitle V3.1.
  * `UNKNOWN / Conflict / Low Confidence (<0.7) -> REJECT`: If Gemini confidence is low (< 0.7), or if local detector reports `BURNED_IN` (conf >= 0.7) while Gemini reports `has_subtitles == False` (conf >= 0.7), or local reports `NONE` (conf >= 0.7) while Gemini reports `has_subtitles == True` (conf >= 0.7), declare `UNKNOWN` and REJECT the candidate immediately. Never guess or provide a hidden default (`UNKNOWN -> GENERATE`).

### 2. Natural Sentence Ending Engine (Anti-Truncation)
- **The Dangling Sentence Problem:** Naive pause-based or duration-based boundary snapping frequently cuts off speech while the speaker is mid-sentence, leaving dangling thoughts (e.g. *"waktu itu masih..."*, *"jadi hidup..."*, *"karena sebenarnya..."*, *"dan kalau..."*, or trailing ellipses/commas).
- **Lexicon & Pattern Completeness Inspection:** Inspect candidate speech transcript tokens at `refined_end` against dangling phrases (`DANGLING_PHRASES`), trailing connectors (`dan`, `atau`, `karena`, `sehingga`, `yang`, `kalau`, `ketika`, `seperti`, `masih`, `sedang`, `akan`, `adalah`), and incomplete punctuation (`,`, `:`, `;`, `-`, `...`).
- **Bounded Sentence Boundary Extension (<= 55.0s Target):**
  * If speech ends on an incomplete thought, scan subsequent transcript segments to identify the next completed sentence boundary.
  * If `(extended_end - start_sec) <= 55.0s`, extend `refined_end` to include the completed thought plus natural laughter/breathing buffer (0.2s).
  * If completing the sentence would exceed the maximum target (55.0s), **REJECT the candidate** immediately. Never force an awkward mid-sentence cut merely to fit a duration window.
- **Preserving Natural Pauses and Laughter:**
  * Speakers naturally take breaths, giggle, hesitate, or pause briefly mid-sentence (e.g. *"Cuma..."* [laugh/pause] *"ketika saya ngeliat dia akhirnya berhasil"*).
  * A mid-clip silence gap > 300ms is NOT a sentence ending. Evaluate the semantic completeness of the final speech segment, not arbitrary internal pauses.
- **False-Complete ASR Trap in Multimodal Preflight Extension (`force_extend`):**
  * *Pitfall:* When downstream multimodal preflight (e.g. Gemini Native Video) detects that a clip ends abruptly (`ending_complete=False` or `ending_natural=False`) and triggers sentence boundary extension, calling `extend_to_sentence_boundary` without a bypass flag causes an immediate false early-return (`True, end_sec, "Sentence ending is already complete"`) if the existing ASR segment happens to end with terminal punctuation.
  * *Failure Mode:* A caller checking only `if can_ext and (new_end - clip_start) <= target_max:` evaluates to `True` because `can_ext == True`, but `new_end == clip_end` (zero actual extension occurred). The orchestrator erroneously clears the preflight blocking issues and marks the candidate usable, allowing a truncated clip to be rendered.
  * *Rule:* Boundary extension helpers must support `force_extend: bool = False`. When `force_extend=True`, bypass the current segment's "already complete" check and actively search subsequent transcript segments for the next completed sentence boundary. In orchestrator repair blocks, enforce strict forward progress (`if can_ext and new_end > clip_end and (new_end - clip_start) <= target_max:`). If `new_end <= clip_end`, treat extension as failed and maintain fail-closed candidate rejection.

### 3. Candidate Fallback Loops
- When evaluating ranked candidates (`ranked_candidates` from semantic scoring), do not abort the entire pipeline if the top-ranked candidate fails visual preflight, ending completeness, or subtitle verification.
- Implement a candidate fallback loop: if candidate #1 fails boundary refinement, sentence extension (>55s), visual director, visual preflight, or subtitle check, record cooldown and advance to candidate #2. Only declare `NO_GOOD_CLIP` or `REJECTED_VISUAL` when all ranked candidates fail.

### 4. Dedicated Multimodal Video QC Gates (Hard Acceptance Rules)
- **Double Subtitle Gate:** Evaluator schema must return `double_subtitles_detected: bool` and `has_double_subtitles: "PASS" | "FAIL"`. If source burned-in subtitles and newly generated ASS subtitles appear simultaneously, hard-fail QC, block upload, and archive to `failed/`.
- **Sentence Ending Gate:** Evaluator schema must return `ending_complete: "PASS" | "FAIL"`, `ending_natural: "PASS" | "FAIL"`, and `ending_reason: str`. If the final video ends mid-thought or abrupt, hard-fail QC.

### 5. Testing Mocks with File Existence Checks
- In video processing pipelines where components (`VisualPreflight`, `GeminiNativeVideoQC`, `CleanRenderer`) check `Path(video_path).exists()`, mock harnesses must write real dummy bytes to temporary paths (`tmp_path / "sample.mp4"`) rather than passing arbitrary non-existent string paths (`"dummy.mp4"`), which fail with file-not-found before calling mocked client methods.
- When mocking `renderer.render`, ensure the mock or fake render callback creates the expected `output_path` file on disk if downstream stages validate container presence.

---

## 14. Surgical Shorts Metadata Generation & Raw-Transcript Overlap Prevention (Auto Clipper V3.1)

Production patterns for generating high-CTR YouTube Shorts metadata (ranked titles with curiosity gap, contextual descriptions, and clean hashtags) while preventing speech transcript leakage:

### 1. The Raw-Transcript Leakage Trap
- **The Problem:** Naively slicing candidate dialogue text (`best_cand.text[:80]`) or prompting an LLM without strict negative constraints causes Shorts titles to look like raw speech fragments (e.g. *"Kau tahu, Gue sampai sempet bilang, ya ampun Tuhan iya sih mempersiapkan tapi ja"*). Pairing this with generic templates (`f"Auto Short from {title}\n\n#Shorts #Indonesia"`) creates spammy, low-CTR uploads.
- **The Goal:** A well-crafted hook title has a strong, truthful curiosity gap (<= 85 characters, natural Indonesian, no ALL CAPS, no emoji spam), accompanied by 1-3 contextual description paragraphs and 3-6 relevant hashtags.

### 2. Multi-Criteria Raw-Transcript Detection & Single-Retry Guard
- **Three-Tier Overlap Detection:**
  1. *Prefix Overlap:* Check if the first 25 characters of the title match the beginning of the candidate transcript (or vice-versa).
  2. *Exact Substring Containment:* Check if the title (length >= 20 chars) is an exact substring inside the transcript.
  3. *Consecutive Word Matching:* Check if 4+ consecutive words from the title appear verbatim in the speech transcript.
- **Quality Self-Check JSON:** Require the LLM to emit structured quality booleans (`title_is_not_raw_transcript`, `title_is_truthful`, `title_has_curiosity`, `description_is_relevant`, `not_clickbait`).
- **Single-Retry Guard:**
  * If Attempt 1 produces a title flagged by the code-level detector or self-check as raw transcript, do NOT crash and do NOT publish the bad title.
  * Trigger an automated single retry with an emphatic editorial warning: *"PERINGATAN EVALUASI: Judul sebelumnya ('...') terdeteksi menyalin transkrip dialog mentah! DILARANG KERAS menyalin ucapan transkrip kata demi kata. Raciklah 5 judul editorial yang memiliki curiosity gap tinggi..."*

### 3. Normalization & Sanitization Contracts
- **Title Length Clamping:** Enforce `<= 85` characters. Mobile YouTube Shorts UI truncates long titles; sanitize quotes, collapse redundant whitespace, and truncate cleanly at word boundaries.
- **Hashtag Formatting:** Ensure `#Shorts` is present and sorted first, clean punctuation/spaces, and clamp to 3-6 tags (e.g. `#Shorts`, `#Indonesia`, `#PodcastIndonesia`, `#TopicTag`).
- **Description Formatting:** 1-3 short paragraphs explaining the conversational context and inviting viewer comments, rather than static single-line templates.

### 4. Robust Fallback Invariant
- **Rule:** If the LLM call times out, returns unparseable output, or the retry attempt fails, fall back to safe editorial metadata derived from `source_title` and `source_channel` (e.g. `clean_source_title[:82]` or `f"Highlight: {clean_source_title}"`).
- **Never Fall Back to Transcript:** Fallback metadata must NEVER use `clip_transcript` as title text.

### 5. Stage H Call-Site Isolation
- Wire the metadata generator into Stage H of the orchestrator right after Three-Tier QC pass and before database record persistence and platform upload (`save_upload` and `upload_short`).
- Keep all upstream video, audio, transcription, framing, and QC pipelines completely frozen.




