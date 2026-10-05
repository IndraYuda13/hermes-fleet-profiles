# Automated Media Pipeline Quality Control & Verification Standards

Comprehensive verification gates, quality control rules, and failure isolation protocols for automated video clipping, speech alignment, rendering, and publishing pipelines.

## 1. Quality Control Duration Semantics
- **Mode Separation:** Parameterize QC into `mode="fixture"` (offline structural tests, 2–65s) and `mode="production"` (strictly enforcing duration ceiling, e.g. 30.0s to 55.0s). Never relax production bounds to accommodate short test fixtures.
- **Boundary Testing:** Author unit tests asserting that durations below minimum (e.g. 29.9s) or above maximum (55.1s) fail production QC.

## 2. Audio & Speech Alignment Integrity
- **Clip-Local Word-Level ASR:** Run clip-local faster-whisper (`word_timestamps=True`) on the rendered audio to obtain precise word boundaries. Never use raw YouTube API transcript segments directly for subtitles, as adjacent segments overlap and produce timeline stacking.
- **Silence Gap Clearing:** When speech gaps exceed 300ms, clear preceding captions before the silence. Clamp `caption.end = last_word.end + linger(80-150ms)` and clear before the pause.
- **Timeline Overlap Invariant:** Assert zero overlapping Dialogue events in generated `.ass` files:
  $$\text{event}[i].\text{end} \le \text{event}[i+1].\text{start} - 20\text{ms}, \quad \text{max\_simultaneous} = 1$$
- **Gibberish Filtering:** Filter repetitive non-lexical monosyllables and audio bleep hallucinations (`dib`, `kon`, `tut`, `bip`) before linguistic chunking.

## 3. Visual Framing, Scene Cuts & Subtitles
- **Scene-Cut Partitioned Face Tracking:** Detect hard scene cuts and track faces strictly within individual scenes. Never interpolate crop center $(x, y)$ or zoom across a scene boundary — cross-cut smoothing causes visual face morphing. Hold crop coordinates across temporary 1–2 frame detector misses using temporal hysteresis.
- **Zero Duplicate Subtitle Invariant:** Before rendering, probe raw footage for burned-in or embedded subtitles. If detected, enforce `subtitle_policy = "SOURCE_EXISTING"` and assert that `subtitles=`, `ass=`, and `drawtext=` are strictly absent from the compiled FFmpeg filtergraph (`ASS_FILTER_COUNT == 0`).
- **Downscale-First Ambient Blur:** For 9:16 blurred background fills, downscale the frame (e.g. to 270x480) before applying `boxblur` and scaling back to 1080x1920. This accelerates rendering up to 10x and eliminates CPU timeouts. Crop out the bottom subtitle region before blurring to prevent ghost subtitle text in letterbox bars.

## 4. Multimodal Direct-Video QC & Publishing Gate
- **Semantic Capability Probe:** Before relying on LLM direct-video inputs, verify temporal awareness via a multi-color test probe.
- **Pre-Slice Payloads:** Pre-slice candidate windows (30–55s, CRF 28 ultrafast, <20MB) before base64 transmission to avoid HTTP 400 payload rejections.
- **Two-Key Authorization:** Live publishing requires both `LOCAL_TECH_QC_PASS` and `LLM_VIDEO_QC_PASS`. If LLM QC fails or times out, fail closed (`passed=False, score=0`) with a blocking reason — never approve silently on fallback.
- **Sentence Completion Gate:** Inspect transcript terminal punctuation and silence gaps. If speech cuts off mid-sentence, extend boundary if within duration ceiling; otherwise reject the candidate and advance to secondary candidates.

## 5. Extractor Resilience & Infrastructure Hygiene
- **Local Proxy & Codec Selector:** Route `yt-dlp` through local rotating proxies with Netscape cookies to avoid bot challenges. Prefer AVC/H.264 (`[vcodec^=avc]`) to prevent silent AV1 frame decoding failures on CPU VPS.
- **Disk Hygiene:** Purge raw downloaded media (`downloads/*.mp4`) immediately upon candidate extraction to prevent VPS root disk exhaustion.
