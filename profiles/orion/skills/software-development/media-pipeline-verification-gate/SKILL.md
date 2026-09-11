---
name: media-pipeline-verification-gate
description: Use when verifying video rendering, QC, or media pipelines.
version: 1.0.0
metadata:
  hermes:
    tags: [media, video, rendering, qc, verification, testing, ffmpeg]
    category: software-development
---

# Media Pipeline Verification Gate

Use when implementing, refactoring, or verifying automated video rendering, audio mastering, speech transcription, or media pipelines (such as AutoShort, auto-clippers, FFmpeg workers).

## Procedure

1. **QC Duration Semantics Separation:**
   - Explicitly parameterize Quality Control into `mode="fixture"` (for fast offline structural tests, e.g. 2–65s) and `mode="production"` (strictly enforcing product duration bounds, e.g. 30.0s to 55.0s).
   - **Never** weaken production QC checks to accommodate short test fixtures.
   - Author boundary unit tests proving:
     - Just below minimum (e.g. 29.9s) fails production QC.
     - Exact minimum (30.0s) passes.
     - Mid-range valid duration (45.0s) passes.
     - Exact maximum (55.0s) passes.
     - Just above maximum (55.1s) fails production QC (unless an explicit, documented pacing exception exists).

2. **Transcriber & Alignment Integrity:**
   - Verify that speech-to-text / word alignment tools only extract the target clip range (`-ss` and `-t` in FFmpeg), never processing multi-hour videos unnecessarily.
   - Verify word-level timestamps are normalized to clip-local time (starting near 0.0s).
   - Ensure temporary audio files are strictly cleaned up in `finally` blocks during both success and exception paths.
   - Ensure alignment failure gracefully degrades to phrase-level or segment subtitles without synthesizing fake per-word interpolated timings.

3. **Renderer Configuration Matrix:**
   - Test all filter and encoding permutations:
     - Subtitles ON (filter present) vs Subtitles OFF (passthrough).
     - Audio mastering ON (highpass, compressor, loudness normalization) vs OFF.
     - Dynamic framing (face-tracked crop) vs fallback framing (blurred 9:16 background).
     - Content-driven effects (punch-in zoom) executed only on plan request.
   - Assert zero invented or random visual effects in default rendering paths.

4. **Failure Pipeline Isolation:**
   - Test and prove:
     - FFmpeg non-zero exit codes raise exceptions and update database status to `failed`.
     - Hard QC failure prevents uploader calls and prevents marking items as `completed`.
     - Visual analysis / speech alignment / LLM plan failures fall back to deterministic safe defaults.

5. **Headless Clean-Venv Verification:**
   - Audit all imports across the codebase.
   - Declare headless-safe packages explicitly in `requirements.txt` (e.g. `opencv-python-headless` instead of GUI `opencv-python`, `onnxruntime`, `numpy`, `pytest`).
   - Create a fresh virtual environment from scratch (`python3 -m venv /tmp/clean_venv && pip install -r requirements.txt`).
   - Run the full test suite (`pytest -v`) inside the clean venv to guarantee zero missing native dependencies or X11/GUI link failures.

6. **Representative Visual Sample Certification & Domain Fidelity:**
   - Automated tests and FFmpeg exit codes only prove syntactic/structural validity, never perceptual or product-level editing quality.
   - **Domain Fidelity Invariant:** Never use music videos, cinematic montages, trailers, gameplay, foreign language content (when target product is locale-bound), or already-edited short-form content for perceptual validation. Music tracks mask voice mastering, singing distorts speech cadence, and source camera cuts make it impossible to isolate the editor's auto-framing and punch-in behavior.
   - Source content must be unedited landscape (16:9) conversational speech: podcasts, interviews, or talking-heads filmed with stable, locked-off camera setups in the target product's designated spoken language.
   - **Dual-Scenario Representative Validation Matrix:**
     * **Scenario A (Single-Speaker Talking Head):** Validates face-aware portrait crop centering, headroom balance, face scale, subtitle safe-zone placement, semantic punch-in timing, and speech audio mastering.
     * **Scenario B (Multi-Speaker / Two-Person Wide Shot):** Stress-tests how the visual framing engine handles competing faces across scene cuts and establishes an empirical baseline for active-speaker or reaction-shot behavior.
   - Each sample must strictly adhere to product duration bounds (e.g. 30–55s) and pass production-mode QC with full FFprobe stream metadata and serialized EditPlan.

7. **Spoken Language Eligibility Gate:**
   - For language-constrained video products, enforce a deterministic language eligibility gate on spoken audio/transcript tokens before clip selection and rendering.
   - Never determine language solely from video title, channel name, country metadata, or description — speech evidence must strictly override contradictory metadata.
   - Support natural regional slang and conversational code-switching (e.g. native syntax with borrowed technical loan words), but reject foreign-dominant speech.
   - Fail safely on empty, unverified, or low-confidence speech rather than defaulting to accepted.
   - Rejected content must immediately exit the pipeline: bypass renderer, bypass social uploader, and mark status as rejected/skipped with an audited rationale.

8. **Scene-Cut Boundary Awareness & Segmented Face Tracking:**
   - **Root Cause of Face Morphing/Melting:** Applying continuous temporal smoothing (e.g. moving average) across camera scene cuts causes the crop coordinates to interpolate/glide between completely different people or camera angles, creating severe visual morphing and motion blur.
   - **Segmented Tracking Timeline:** Detect hard scene cuts (via frame difference or scene detection algorithms) and partition the timeline into discrete, independent scene segments:
     $$\text{SCENE A} \rightarrow \text{face A tracking} \rightarrow \text{HARD CUT} \rightarrow \text{SCENE B} \rightarrow \text{independent face acquisition}$$
   - **Zero Cross-Cut Smoothing:** Enforce temporal smoothing strictly *within* each scene segment. Never interpolate crop center $(x, y)$ or scale across a scene boundary.
   - On scene cuts, the crop window must execute an instantaneous jump (step function) to the new subject's position.
   - If a scene segment lacks a detectable face or confidence falls below threshold, gracefully revert that segment to a safe fallback (e.g. centered blurred-background 9:16) rather than carrying over the previous scene's face trajectory.

9. **Mobile Subtitle Readability & Grammatical Chunking:**
   - In 1080x1920 portrait formats, small default subtitles (< 48pt) are unreadable on mobile devices. Calibrate default styles to `font_size >= 52`, heavy outline (`outline_width >= 5`), and drop shadow (`shadow_width >= 3`).
   - Position vertical safe zones (`margin_v >= 540`, baseline $\approx Y=1380\text{px}$) to avoid collision with bottom platform UI overlays (captions, channel tags, audio badges, action buttons on Shorts/Reels/TikTok).
   - Keep word highlighting calm (active word scale at 100%, high-contrast color swap) without aggressive 108%+ bouncing or scale jitter.
   - Perform grammar-aware linguistic chunking: bind negations directly to their predicates (e.g. "nggak pernah", "tidak mau"), keep prepositions bound to nouns (e.g. "ke kantor", "di rumah"), and start fresh chunks on conjunctions or punctuation pauses.

10. **Broadcast Audio Standardization:**
    - Standardize all final social/short-form media output to AAC, 48,000 Hz, 2-channel stereo (`-ar 48000 -ac 2`), adhering to standard platform ingest specs.
    - Maintain voice-first mastering filterchains: 80Hz highpass filter to eliminate low-end rumble, mild dynamic range compression, and EBU R128 loudness normalization (target -16.0 LUFS, true peak -1.5 dBTP).

11. **Before/After Visual Frame Comparison:**
    - When fixing visual artifacts (such as scene-cut morphing, crop jitter, or subtitle sizing), capture and archive side-by-side comparison frames at identical timestamps (`before_*.jpg` vs `after_*.jpg`).
    - Visual defect closure requires observable image evidence of artifact elimination, not merely successful re-render completion.

12. **Reviewer Artifact Packaging:**
    - Package a lightweight source archive directly from the target commit (`git archive <commit> | tar -x`), strictly omitting `.git`, virtual environments, caches, and stale render outputs.
    - Bundle test suites, runtime models, requirements.txt, and audit artifacts (`audit_artifacts/` containing QC report JSON, raw FFprobe JSON, serialized EditPlan, ASS subtitle, comparison frames, and auditor markdown).
    - Deliver representative rendered video artifacts (`.mp4`) separately alongside the source archive so the reviewer can evaluate visual/audio fidelity without archive bloat.

13. **Keyframe Boundary & Flicker-Free Expression Semantics:**
    - **Root Cause of Boundary Flicker:** Building piecewise FFmpeg crop expressions using disjoint conditions (e.g. `between(t, 0, 1) + between(t, 1, 2)`) or `<` / `>` comparisons leaves micro-gaps or undefined states at exact integer-second or boundary timestamps ($t=1.000s, 2.000s$), causing the renderer to flash back to default background or crop coordinates for exactly 1 frame.
    - **Continuous Nested `if()` Evaluation:** Structure dynamic crop expressions as strictly nested, gapless conditionals:
      `if(lte(t, t_1), crop_1, if(lte(t, t_2), crop_2, ... default_crop))`
    - Verify with dense frame extraction across boundaries ($\pm 2$ frames around $t=1s, 2s, 3s, 4s, 5s$) and assert zero single-frame coordinate jumps or luminance flashes.

14. **Existing Subtitle Protection, Ghost Text Elimination & Subtitle-Aware Framing:**
    - **No-Duplicate Subtitle Invariant:** Before generating Subtitle V2 / ASS tracks, inspect both container streams (`ffprobe` for `EMBEDDED_TRACK`) and visual pixel data (hybrid OCR/edge density for `BURNED_IN`).
    - If existing subtitles are present (`EMBEDDED_TRACK` or `BURNED_IN`), strictly disable new subtitle generation (`GENERATE_NEW_SUBTITLE = false`) to prevent double-caption collisions.
    - **Filtergraph-Level Invariant Assertion:** Never assert subtitle suppression solely through in-memory boolean flags. Inspect the actual compiled FFmpeg filtergraph string and assert that `subtitles=`, `ass=`, and `drawtext=` are strictly absent from the final video filterchain (`ASS_FILTER_COUNT == 0`, `NEW_TEXT_OVERLAY_COUNT == 0`).
    - **Ghost Subtitle Elimination in Blurred Fill:** In `SUBTITLE_SAFE_FULL_WIDTH` or blurred background layouts, never scale/blur the full uncropped frame `[0:v]`. Blurring the lower subtitle band produces legible, smeared "ghost subtitles" in the letterbox bars. Crop out the subtitle band (e.g. `crop=iw:ih*0.70:0:0`) *before* applying `boxblur` and scaling to 1080x1920 so the background fill contains only smooth ambient gradients without text bleed.
    - **Subtitle-Aware Safe Framing:** Wide horizontal 16:9 subtitles will be truncated on the left/right under tight 9:16 portrait cropping. When existing wide subtitles are detected, enforce `SUBTITLE_SAFE_FULL_WIDTH` layout (16:9 foreground fully preserved in width with blurred top/bottom letterbox fill) rather than forcing face-crop over text readability.

15. **Word-Level ASR Mandatory for Generated Subtitles (NOT Segment Clamping):**
    - YouTube API transcript segments have inherently overlapping timestamps between adjacent phrases (e.g. Seg 1: 0.0–5.5s, Seg 2: 1.68–6.16s). Monotonic clamping on these segments produces unnatural timing because the segment end times are inaccurate — they extend well beyond the last spoken word.
    - **Do NOT use phrase/segment-level transcript timing for subtitle generation.** Run clip-local faster-whisper (or equivalent) with `word_timestamps=True, language='id'` on the rendered clip's audio to obtain per-word start/end times.
    - Build caption chunks from ordered word tokens (2-5 words per phrase), splitting at punctuation, natural pauses (gap > 350ms), or max word count.
    - Derive timing from actual word boundaries: `caption.start = first_word.start`, `caption.end = last_word.end + linger(80-150ms)`.
    - **Silence Gap Clearing:** If speech gap >= 300ms between phrases, previous caption must clear before/at that gap. Do not hold subtitle through long silence — "setelah pembicara selesai ngomong, subtitle harus hilang."
    - **Non-Overlapping Timeline Enforcement:** Clamp every event: `event[i].end = min(event[i].end, event[i+1].start - epsilon)` where epsilon ≈ 20ms.
    - **Hard Invariant Assertions before writing ASS:**
      ```python
      assert event[i].start < event[i].end  # valid interval
      assert event[i].end <= event[i+1].start  # zero overlap
      max_simultaneous_events == 1  # one caption lane only
      ```
    - **ASS Timeline QC Validation:** For `subtitle_policy == 'GENERATE'`, validate the authoritative `.ass` file directly (parse Dialogue event timestamps, count overlaps, assert max_simultaneous=1) instead of relying on pixel-level stuck-subtitle heuristics which produce false positives on our own long-duration legitimate captions.

16. **Test Asset Provenance Integrity:**
    - Always verify whether test footage natively contains burned-in subtitles before running validation pipelines.
    - Never chain synthetic preprocessing scripts (such as `drawtext`) on top of source footage that already has native subtitles — contaminating test assets creates artificial double-layer defects that confound pipeline auditing.

17. **Multimodal Visual Director Integration & Probe Discipline:**
    - When adding LLM-based visual intelligence (e.g. via an OpenAI-compatible router such as 9router to Gemini), **never assume direct MP4/video streaming support**.
    - Perform a lightweight, bounded read-only capability probe. If direct video returns prompt-instruction text rather than analysis, fall back to downscaled sampled keyframes (e.g. 6–10 representative JPEG frames).
    - Output must be parsed through a strict typed schema (e.g. Pydantic `VisualDirectorResult`). Reject free-form prose and maintain an autonomous, local deterministic fallback when the router or model times out or returns malformed data.

18. **Review Status Decoupling:**
    - Passing automated tests and QC certifies technical implementation completeness only (`INTERNAL_GATE_PASS`).
    - Never declare "100% verified" or "Product PASS" prior to independent human/reviewer visual assessment. The mission status must remain `AWAITING INDEPENDENT VISUAL REVIEW`.

19. **`SUBTITLE_PRESERVE_COMPOSITE` Layout (Authentic Subtitle Slicing & Subject Magnification):**
    - **The Letterbox Trap of `SUBTITLE_SAFE_FULL_WIDTH`:** Scaling a full 16:9 landscape frame to fit 1080px width on a 9:16 vertical canvas prevents subtitle truncation, but drastically shrinks both the speaker's face and the subtitle text (creating a distant, unengaging letterbox experience on mobile screens).
    - **Dual-Layer Pixel Recomposition:**
      * **Video Layer:** Slice the source frame above the subtitle band (e.g. $y = 0 \dots 0.72 \times ih$). Crop this area to a portrait 9:16 window centered on the speaker using face tracking, then scale to 1080x1920. The subject becomes large, cinematic, and immersive (+60–70% linear dimensions, +180% pixel area).
      * **Subtitle Band Layer:** Slice the lower source band containing native burned-in subtitles (e.g. $y = 0.72 \times ih \dots ih$). Scale it proportionally to 1080px width and overlay it onto the portrait canvas in the comfortable reading zone (e.g. $Y=1480$, safe above platform UI controls).
    - **Two Invariants:**
      1. The Video Layer must strictly crop out the lower subtitle band before scaling, guaranteeing the native subtitle is never shown twice on screen.
      2. No OCR regeneration or fake subtitle retyping — the overlaid band uses 100% authentic source pixels, preserving exact timing and styling without OCR hallucinations.

20. **ASR Quality Guard & Podcast Bleep/Gibberish Filtering:**
    - Speech recognition models (Whisper, YouTube ASR) frequently hallucinate nonsense phonemes when transcribing podcast censorship bleeps or background laughter (e.g. audio bleeps transcribed as "ya kan dib kon tut bip mem tut").
    - **Explicit Locale & Initial Prompt Guidance:** Always supply explicit language codes (`language='id'`) and conversational initial prompts (`initial_prompt='Podcast percakapan bahasa Indonesia santai...'`) with beam search $\ge 5$ to anchor speech decoding.
    - **Gibberish Chunk Filter:** Implement an automated token filter (`is_gibberish_chunk()`) targeting censorship bleep fragments (`dib`, `kon`, `tut`, `bip`, `mem`, `kontut`, `komtut`, etc.) and rapid repetitive non-lexical monosyllables. Strip or drop corrupted segments prior to linguistic chunking and subtitle generation.

21. **Subject Presence Gate, Temporal Hysteresis & Motion Limits (Watchability):**
    - **Scene Cut Valid != Good Edit Cut:** A detected scene cut or keyframe boundary must not automatically trigger an abrupt crop jump. Unjustified camera reframing within the same shot creates a jarring, choppy viewing experience.
    - **Three-State Subject Presence Gate:** Classify each frame as `VALID_SUBJECT`, `TEMPORARY_FACE_LOSS`, or `NO_VALID_SUBJECT`.
    - **Temporal Hysteresis / Grace Period:** When a face detector temporarily misses 1–2 sample frames in an ongoing scene (e.g. head turning, hand gesture, motion blur), **HOLD** the previous valid crop coordinates. Never immediately drop to default center crop or an empty background!
    - **Intra-Shot Motion Clamping:** Enforce a maximum crop displacement per second within the same scene segment (e.g. $\le 0.08$ frame width/sec). Clamp detector jitter so reframing mimics a smooth, deliberate camera pan.
    - **Scene Cut Reacquisition:** Allow an instantaneous crop jump only across genuine hard scene cuts, then immediately stabilize and clamp subsequent motion.
    - **Visual Director Semantic Review:** Integrate semantic continuity assessment (`continuity_risk`, `empty_subject_frames_detected`, `recommended_hold_previous_framing`) into LLM director schemas to audit and flag visual awkwardness.

22. **Subtitle Stuck Detection via Text-Mask Overlap (Not Whole-ROI Diff):**
    - In talking-head video, comparing raw edge maps or diff ratios across the whole subtitle ROI fails because >98% of the area is background or speaker clothing. Natural breathing or compression creates 1–2% edge variation, masking text updates and causing false duplicate flags.
    - Isolate the high-contrast bright text mask (`cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)`), filter contour glyphs, and calculate normalized mask intersection over max non-zero pixels:
      $$\text{overlap} = \frac{\text{count\_nonzero}(M_1 \land M_2)}{\max(\text{count\_nonzero}(M_1), \text{count\_nonzero}(M_2))}$$
    - Assert stuck subtitle only when identical text mask persists across $>4$ consecutive sampled frames ($\text{overlap} > 0.65$ for $>8\text{s}$). Legitimate subtitle changes yield $\text{overlap} < 0.25$.

23. **Safe-Zone Danger Detection with Horizontal Centering Invariant:**
    - Scanning top 15% or bottom 20% danger strips purely by aspect ratio and edge density falsely flags studio background wall decor, light panels, and corner monitors.
    - Real video subtitles are horizontally centered on canvas. Before flagging a safe-zone danger breach, verify horizontal centering:
      $$|x_{\text{center}} - \frac{W}{2}| < 0.25 W$$

24. **Multimodal LLM Proxy SSE Stream Decoupling:**
    - When invoking OpenAI-compatible proxies (e.g. 9router) with image contact sheets, proxies often stream Server-Sent Events (`data: {...}\n\n`) even when `"stream": False` is requested.
    - Code must inspect `response.text.strip().startswith("data:")`, extract and concatenate delta content across chunks, and maintain a local deterministic fallback when the multimodal endpoint times out.

25. **Downscale-First Ambient Blur Filtergraph Optimization:**
    - Applying FFmpeg `boxblur` or heavy spatial filters directly onto full 1080x1920 portrait background layers consumes extreme CPU resources and frequently triggers process timeouts (120s+) on longer clips.
    - For ambient letterbox backgrounds where high-frequency detail is intentionally discarded, downscale the frame prior to blurring:
      `scale=270:480:force_original_aspect_ratio=increase,crop=270:480,boxblur=10:2,scale=1080:1920[bg_blur]`
    - This achieves visually identical soft ambient fill while reducing pixel processing volume by 16x and accelerating render speeds by up to 10x.

26. **Isolated Worktree Lifecycle for Zero-Downtime Pipeline Architecture Resets:**
    - When executing fundamental architecture overhauls on production media pipelines (e.g. AutoShort / video clippers running 24/7 background daemons and dashboards), NEVER edit the active codebase in-place or mutate production databases (`app.db`).
    - Provision a detached git worktree (`git worktree add /path/to/<repo>-v3 -b feature/<branch>`), bind to an isolated test database (`data/app_v3.db`), and route test servers to dedicated non-conflicting ports.
    - Keep active systemd services (`autoshort-web.service`) running uninterrupted while full multi-tier verification and real media benchmarking complete in isolation.

27. **Semantic Direct-Video Multimodal Capability Verification (Probe vs HTTP 200):**
    - When an LLM router (e.g. 9router) claims direct MP4/video streaming support, HTTP 200 alone is NOT proof of video understanding — proxies may swallow video payloads, return empty text, or echo prompt instructions.
    - Author an automated semantic probe using a tiny controlled video with ordered temporal visual states (e.g. 0–2s Red Card "A", 2–4s Blue Card "B", 4–6s Green Card "C").
    - DIRECT VIDEO is verified (`DIRECT_VIDEO_VERIFIED=true`) only if the model identifies ordered temporal events and reads text across timestamps.
    - Standardize payload format: `{"type": "image_url", "image_url": {"url": f"data:video/mp4;base64,{b64_video}"}}` with downscaled, low-bitrate MP4s (<15MB).
    - **Pre-Slice Before Sending:** Full source videos (100-200MB podcasts) exceed API payload limits and cause HTTP 400. Always pre-slice the candidate window (~30-55s) to a lightweight MP4 (<20MB, ultrafast CRF 28) before sending to multimodal endpoints for preflight or QC. Only pre-sliced clips should be base64-encoded.
    - **Explicit Mode Tracking:** Record preflight and QC execution mode as `GEMINI_NATIVE_VIDEO | LOCAL_FALLBACK | FAILED`. Never collapse a fallback into a generic PASS — a fallback path is valid operational behavior but it is NOT native Gemini analysis and must not be reported as such.

28. **Conservative Framing Policy (`SAFE_WIDE` as Stable Default vs Aggressive Portrait Crop):**
    - For talking-head, interview, or educational content, tight 9:16 portrait face cropping is fragile and claustrophobic: it truncates presentation slides, laptop screens, hand gestures, and cuts off faces when speakers turn or lean.
    - Enforce `SAFE_WIDE` as the stable default layout: preserve 100% of the 16:9 source frame centered on 1080x1920 canvas with tasteful downscale-blurred letterbox background.
    - Disable continuous virtual camera tracking and aggressive portrait crop by default in stable mode. Only enable mild zoom (`SAFE_ZOOM` 1.0x–1.25x) after explicit visual verification.

29. **Source Subtitle Preflight & Zero Duplicate Subtitle Layer (Hard Invariant):**
    - Before rendering, execute multimodal visual preflight on the raw candidate clip. If existing burned-in or embedded subtitles are detected, enforce `subtitle_policy = "SOURCE_EXISTING"`.
    - Hard Invariant: strictly suppress generation of any ASS or FFmpeg text overlay (`ASS_FILTER_COUNT == 0`).
    - When `subtitle_policy == "SOURCE_EXISTING"`, decouple local visual QC stuck-subtitle checks: static slide presentations, infographics, or whiteboard text in the source video must not be mistaken for stuck generated subtitles.
    - When `subtitle_policy == "GENERATE"`, validate the authoritative ASS timeline file directly (event overlap count, max simultaneous events, events outside clip duration) rather than pixel heuristics. Pixel-level visual QC remains supplemental but must not be the sole subtitle correctness gate for generated captions.
    - **Do NOT skip QC entirely for GENERATE policy** — generated subtitles themselves can be wrong (overlapping events, lingering text, ASR gibberish). Validate the ASS file timeline as ground truth.
    - If generating clean subtitles (Case 3: no source subtitles), enforce mobile safe-zone geometry (`font_size <= 46`, `MarginL=90, MarginR=90, MarginV=440`) to prevent text from clipping at the bottom UI boundary.
    - **Evidence-Based Detection Hierarchy:** Use explicit states (`NONE | EMBEDDED_TRACK | BURNED_IN | UNKNOWN`), never boolean-only. Decision priority: A) ffprobe embedded stream → EMBEDDED_TRACK. B) Local burned-in detector with HIGH confidence (≥0.7) → BURNED_IN. C) Gemini native video as semantic override when local detector disagrees. D) If ambiguous → UNKNOWN → REJECT candidate. Critical invariant: `UNKNOWN ≠ SOURCE_EXISTING` — never silently suppress subtitle generation on ambiguous detection.
    - **Burned-In False Positive Mitigation:** Canny edge density + morphology detectors produce false positives from studio props (desk monitors, shirt graphics, floor markers, logos). Tighten with: Otsu binarization instead of raw Canny, contour aspect-ratio filtering (text lines are wide+thin, aspect >4.0), horizontal center-alignment assertion (center_x within 15-85% of frame width), and bottom 25% ROI only (not 30%). Use Gemini as semantic tiebreaker when local detector fires but Gemini says no subtitles.

30. **Direct-Video Multimodal Final QC Publishing Gate:**
    - After rendering the final MP4, send the actual rendered video directly to the multimodal LLM (Gemini via 9router).
    - Evaluate overall watchability, subject visibility, framing stability, absence of duplicate subtitles, subtitle safe-zone margins, and audio-visual coherence.
    - Enforce two-key authorization: `LOCAL_TECH_QC_PASS and GEMINI_NATIVE_VIDEO_QC_PASS == UPLOAD`. Local QC runs first to prevent wasting LLM calls on structurally broken artifacts.
    - **Fallback MUST NOT silently approve:** If Gemini QC invocation fails (HTTP 400, timeout, parse error), the fallback must return `passed=False, score=0` with a blocking reason stating QC was unavailable. Silent `passed=True` fallbacks create false confidence and let broken videos through upload gates.

31. **Failed Candidate Archive, No-Sleep Discovery Loop & Cooldown Blacklisting:**
    - If a candidate fails technical, visual, or LLM video QC: DO NOT upload.
    - Archive the failed artifact to `failed/YYYYMMDD_HHMMSS_<video_id>_<clip_id>/` containing `clip.mp4`, `reason.md`, `qc.json`, and `edit_plan.json` as an evaluative dataset.
    - Content-quality failures must **NEVER trigger the normal success sleep (e.g. 300s)**. Immediately restart discovery for a new candidate.
    - Record candidate fingerprint (`<video_id>_<start_sec>_<end_sec>`) into an in-memory or persisted cooldown blacklist to prevent infinite re-harvesting of rejected segments.
    - Pass recent failure summaries into the Search Planner LLM to diversify query generation away from repeating failure modes.

32. **Ranked Candidate Fallback Loop (Boundary Overflow Grace):**
    - When aligning semantic candidate boundaries to sentence/speech pauses, the top candidate's complete thought may naturally overshoot the upper duration ceiling (e.g. 55.0s -> 57.1s).
    - **Do not reject the source video on the first candidate failure.** Iterate through the ranked candidate list (`for candidate in ranked:`): secondary candidates often share near-identical semantic scores (e.g. tied at 86/100) while resolving to ideal durations (e.g. 45–50s).
    - Mark `NO_GOOD_CLIP` only when all candidates in the top tier (e.g. top 3–5) fail boundary alignment or visual preflight.

33. **Local Rotating Proxy, Codec Filter & Cookie Routing for Ingest Extractors:**
    - Media extractors (such as `yt-dlp`) running on cloud or VPS datacenter IPs are aggressively rate-limited or blocked by bot challenges ("Sign in to confirm you're not a bot").
    - Route media download subprocesses through local proxy ports (e.g. `--proxy http://127.0.0.1:31001`) paired with Netscape formatted `cookies.txt` and explicit JS runtime options (`--js-runtimes deno`).
    - **Prefer AVC/H.264 codec:** YouTube increasingly serves AV1 streams in MP4 containers. Servers without hardware AV1 decoding (most VPS) fail silently — OpenCV `cap.read()` returns empty frames with hundreds of stderr warnings. Add `[vcodec^=avc]` to the yt-dlp format selector: `bestvideo[height<=720][vcodec^=avc][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best`.

34. **Fail-Closed Gate Check Enforcement on Social Uploaders:**
    - Social uploader clients must strictly require an explicit, validated `UploadGateCheck` object containing all upstream gate verdicts.
    - If `gate_check is None` or any single prerequisite gate is False, fail-close immediately (`UploadGateRejectedError: ALL_GATES_MISSING`).
    - Standardize default publication privacy status to `private` for automated runs to guarantee human-in-the-loop review before public distribution.

35. **Hybrid Subtitle Accuracy Architecture (Whisper Timing vs Gemini Verbatim Listening):**
    - **Separation of Concerns:** Whisper acoustic word timestamps measure WHEN speech occurs (`start`/`end` ground truth). Multimodal Gemini (via 9router) listens to native video/audio to determine WHAT was actually spoken.
    - **Zero Synthetic Timing Invariant:** Gemini strictly does NOT synthesize or interpolate per-word timestamps. Never map Gemini corrections into microscopic sub-slices (e.g. 0.05s) via naive SequenceMatcher token replacement; chunk ASR word tokens into natural acoustic phrases first (locking `start` and `end` to audio), then apply verbatim text corrections to each phrase.
    - **Multilingual Code-Switching & Slang Preservation:** Direct-video verifier must preserve authentic Indonesian slang (`gue`, `lu`, `nggak`, `banget`) and English code-switching (`who are you`, `what do you want`, `what you can give`, `self love`, `mindset`) verbatim without paraphrasing, formalizing, or censoring.

36. **Fast Stream-Copy Candidate Slicing & Subtitle Phrase Duration Calibration:**
    - **Fast Slicing Invariant:** Pre-slicing candidate windows (~30–55s) from multi-hour source videos (1–2hr podcasts) must strictly use fast stream-copy:
      `ffmpeg -y -ss {start_sec:.3f} -i {video_path} -t {duration_sec:.3f} -c copy -movflags +faststart {tmp_slice}`
      Stream-copy executes in <0.5s (500x speed). Never re-encode with `-c:v libx264` on CPU during candidate extraction, and NEVER fall back to the full unsliced source video when `start_sec > 0` (which causes Whisper to transcribe from second 0.0 of the episode).
    - **Defensive QC Error Schema Parsing:** When multimodal video QC returns structured error lists (`obvious_transcription_errors`), defensively handle both `dict` (`{"shown": ..., "heard": ...}`) and `str` (e.g. `["tidak ada"]`, `["none"]`, raw strings) to prevent fatal `AttributeError: 'str' object has no attribute 'get'`.
    - **Minimum Subtitle Phrase Duration:** Do not split phrases at mid-sentence commas inside short clauses (<0.75s, e.g. "Mas Bilal,"). Flickering 400ms fragments cause visual fatigue and trigger false omission flags in multimodal QC. Merge short sub-phrases within the same clause so captions stay visible for comfortable reading (1.0s–3.0s).

37. **Black-Box Acceptance Testing & Zero-Mutation Contract:**
    - When executing final black-box E2E acceptance tests (`HEAD_BEFORE == HEAD_AFTER` and `git status == CLEAN`), never create test runner scripts, helpers, or temporary files inside the target repository tree (`/root/projects/...`). Write all execution harnesses to `/tmp/`.
    - Never mutate `.gitignore`, source files, prompts, or configuration logic during acceptance. Treat any non-zero source diff as an immediate mission failure.
    - Separate runtime output directories and review packs (`stable_acceptance_review/`) from git tracking.

38. **Datacenter VPS Disk Exhaustion & Multi-Cycle Raw Media Hygiene:**
    - Continuous multi-cycle discovery downloads full 1080p/720p long-form videos (150MB–1.5GB each). On cloud VPS instances with bounded root partitions (e.g. 50–60GB), accumulating 10–15 unpruned raw video downloads quickly causes `database or disk is full` crashes in SQLite and FFmpeg.
    - Slicing pipelines must immediately purge raw downloaded media (`downloads/*.mp4`) once candidate extraction or rendering finishes, or implement an automated LRU disk budget check before initiating new downloads.

39. **Defensive Audit Packaging & Multimodal QC Transcription Discrepancy Gate:**
    - Multimodal video QC (via direct MP4 base64 streaming to Gemini) actively listens to spoken phonemes against on-screen ASS subtitles to reject subtle hallucinations (e.g. hearing "apaan lah" while subtitle shows "Apem lah!").
    - Ensure rejected artifacts are quarantined to `failed/<timestamp>_<video_id>_<clip_id>/` with `reason.md` without halting the discovery loop.
    - In audit packaging scripts, access object properties defensively using `getattr(obj, "attr", default)` or `.get("key", default)` rather than direct attribute lookup on Pydantic schemas, ensuring report generators never crash on schema variations or missing keys.

40. **Strict Three-Way Subtitle Decision & Zero Guessing Gate:**
    - Detect source subtitle presence before render using multimodal preflight and local OCR/edge analysis.
    - Enforce explicit policy branching:
      * `SOURCE HAS SUBTITLES` -> `SOURCE_EXISTING` -> Strictly 0 new ASS / subtitle overlay filters generated (`ASS_FILTER_COUNT == 0`).
      * `SOURCE HAS NO SUBTITLES` -> `GENERATE` -> Invoke word-level Hybrid Subtitle Accuracy Engine.
      * `UNKNOWN` / Detection Conflict -> **Hard Reject Candidate**. Never guess or silently fall back to `GENERATE` or `SOURCE_EXISTING`.
    - On final rendered MP4, execute multimodal video QC with an explicit double-subtitle assertion: if both native source subtitles and generated subtitles appear simultaneously, immediately mark `FAIL`, abort upload, and archive to `failed/`.

41. **Natural Sentence Ending Verification & Duration Ceiling Boundary Extension:**
    - Automated video clippers must never truncate speech mid-sentence or mid-thought (e.g. cutting on conjunctions, incomplete clauses, or hanging phrases like "waktu itu masih...", "jadi hidup...", "karena sebenarnya...", "currency yang...").
    - Inspect transcript terminal punctuation, word-level ASR end times, audio silence gaps, and multimodal semantic ending checks.
    - **Boundary Extension Protocol:** If a candidate ends prematurely while the speaker is continuing the thought, attempt extending the end timestamp to the sentence completion boundary (`new_end = sentence_end`), strictly enforcing `new_end - start <= max_allowed_duration` (e.g. <= 55.0s).
    - **Hard Overflow Rejection:** If extending the boundary to complete the thought exceeds the duration ceiling, strictly reject the candidate and advance to the next ranked candidate or fresh search. Never force an incomplete ending to satisfy target duration.
    - **Natural Pause vs Sentence Boundary:** Do not mistake natural conversational pauses (laughter, breathing, brief reflection) for sentence termination via naive silence thresholds (`pause > 300ms`). Verify grammatical and semantic completeness.
    - **Final Multimodal QC Ending Assertion:** The final rendered MP4 must be independently evaluated by multimodal QC for `ending_complete == True` and `ending_natural == True`. Videos ending abruptly must fail QC and be blocked from publication.

42. **Shorts Upload Packaging & Surgical Metadata Generation Gate:**
    - **Surgical Isolation Invariant:** Metadata restoration/tuning (title, description, hashtags) must strictly isolate changes to post-QC metadata generation and uploader call-sites (`TARGET <= 3 FILES`). The entire video pipeline (search, candidate selection, boundary refiner, transcription, rendering, QC) must remain 100% frozen with zero source code mutations.
    - **No-Raw-Transcript Title Rule:** Never use raw ASR transcript strings or naive character truncations (e.g. `transcript[:80]`) as video titles. They produce trailing conjunctions, dangling prepositions, and unreadable fragmented sentences.
    - **Multi-Candidate Self-Ranking:** Generate at least 5 distinct title candidates using multimodal/LLM completion. Rank candidates systematically across *clarity, curiosity, relevance, naturalness, truthfulness, and Shorts appeal*. Clamp selected titles to $\le 85$ characters with an ethical curiosity gap, zero deceptive clickbait, zero ALL CAPS spam, and zero emoji overload.
    - **Contextual 1-3 Paragraph Description Architecture:** Reject raw title echoes, transcript dumps, or generic promotional boilerplates ("jangan lupa like & subscribe"). Author 1–3 concise paragraphs explaining the discussion premise, speaker context, and core takeaway, paired with 3–6 focused hashtags (`#Shorts`, topic, speaker/brand).
    - **Quality Self-Check & Offline Benchmark Gate:** The metadata generator must self-evaluate output against explicit quality booleans (`title_is_not_raw_transcript`, `title_is_truthful`, `title_has_curiosity`, `description_is_relevant`, `not_clickbait`) with bounded retries before upload.
    - **Offline Comparison Certification:** Prior to live upload publication, generate metadata across 5+ real historical clips without uploading, audit before/after samples in a clear review document, and verify that titles and descriptions demonstrate demonstrable editorial improvement.

43. **Release Promotion & Runtime Privacy Configuration Audit:**
    - Before tagging and deploying a stable release candidate for continuous live execution (e.g. 24h soak tests or public publishing), audit the complete upload and execution call chain for hardcoded operational parameters (such as `privacyStatus`, rate limits, or destination endpoints).
    - **Config-Driven Runtime Decoupling:** Never hardcode deployment modes or privacy states (e.g. `privacy_status: str = "private"`) in function signatures or caller call-sites without an explicit environment variable fallback:
      `privacy_status: str = os.getenv("YOUTUBE_PRIVACY_STATUS", "private")`
    - **Zero-Mutation Release Gate:** If an operational directive (such as switching from private testing to public publishing) encounters a hardcoded value in a frozen release candidate:
      * Halt execution before modifying source code.
      * Report the exact file path, function signature, and caller line numbers.
      * Obtain explicit authorization before applying any surgical patch, preserving release tag integrity and preventing untracked configuration drift.

44. **Dynamic Search Query Planning vs Static Discovery Loops:**
    - Never hardcode a small static set of search queries in unattended continuous daemon runs (e.g. 24-hour soak tests). YouTube API returns the same top candidates for identical query strings, causing repetitive processing of already rejected videos and discovery starvation.
    - Pass `search_queries=None` to allow the LLM `SearchPlanner` to synthesize fresh, diverse search queries adaptively on every cycle based on recent failure categories and rejection feedback.

45. **Zero-Credential Public Upload Verification via YouTube oEmbed:**
    - Production upload tokens scoped strictly to `youtube.upload` cannot read back video privacy status via `videos().list(part="status")` (fails with HTTP 403 `insufficientPermissions`).
    - Query YouTube's public oEmbed endpoint: `curl -s -i "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=<id>&format=json"`.
    - A truly public video returns HTTP 200 with title and author name; a private or unlisted video returns HTTP 401 or 403. This provides deterministic, zero-credential validation of public status without expanding token attack surface.

46. **Daemon Result Schema Access & Defensive Attribute Lookup:**
    - In long-running autonomous loop scripts and monitors, never access convenience attributes on pipeline result models (e.g. `res.upload_url`) without verifying the underlying Pydantic schema (`PipelineResult`). A single missing property raises `AttributeError` after an expensive 10-minute pipeline cycle completes.
    - Always extract fields through documented nested dictionaries (`res.upload_result.get("url")`) or query the authoritative SQLite database (`SELECT url FROM uploads WHERE video_id = ? ORDER BY id DESC LIMIT 1`).

47. **Active Daemon Telemetry Verification & Process Independence Across Version Resets:**
    - When checking or reporting on the running status of automated media clippers/daemons after an architecture reset or versioned worktree migration (e.g. V2 to V3.1), **never assume the legacy systemd unit (e.g. `autoshort.service`) represents current production**.
    - Continuous autonomous soak tests and release-candidate daemons often run via detached runner scripts (e.g. `run_v3_1_soak_daemon.py --mode soak`) executing in dedicated worktrees (`auto-short-generator-v3/`) with localized telemetry (`soak_test_24h/`).
    - Ground operational status reports in 5 live dimensions:
      1. Process & PID liveness via broad process inspection (`ps aux | grep -iE '<keyword>'`), not just systemd.
      2. Current cycle, active stage, and uptime from `daemon_state.json` and active log tail (`soak.log`).
      3. Total successful uploads and live URLs from `uploads_ledger.jsonl` (verified via public oEmbed).
      4. Categorized rejection breakdown from `rejections_ledger.jsonl` (`rejected_visual`, `rejected_language`, `no_good_clip`, `qc_failed`).
      5. VPS disk headroom (`df -h /`) to ensure continuous media downloading and auto-cleanup are operating within safe bounds.

## Pitfalls
- Slicing candidate clips from multi-hour source videos using CPU re-encoding (`-c:v libx264`) instead of fast stream copy (`-c copy`) — CPU encoding times out on 1-hour+ videos, and falling back to the unsliced video path causes Whisper to transcribe from second 0.0 of the episode instead of the candidate window.
- Allowing Gemini or LLMs to synthesize synthetic per-word timing timestamps — interpolating replacement words into microscopic duration slices causes subtitle stacking and timeline collapse; chunk ASR words into natural acoustic phrases first, lock the audio span, and replace phrase text verbatim.
- Blindly assuming `obvious_transcription_errors` from LLM video QC is always a list of dicts — models often return lists of strings (e.g. `["tidak ada"]`); defensively parse both string and dict types to avoid fatal `AttributeError: 'str' object has no attribute 'get'`.
- Splitting subtitle phrases immediately at mid-sentence commas inside short clauses (< 0.7s) — produces flickering 400ms fragments that viewers and multimodal QC models flag as omissions; merge short phrases (<0.75s) within the same clause so captions stay comfortably readable for 1.0–3.0s.
- Setting face/subject presence threshold at 70% for SAFE_WIDE layout — podcasts routinely intersperse B-roll, slides, two-shots, and wide establishing shots where Haar cascade face detectors fail; for SAFE_WIDE (which preserves the full frame anyway), lower to 20% to avoid rejecting valid talking-head content with visual variety.
- Aborting video processing on the first candidate's boundary overflow (>55s) instead of falling back to secondary candidates in the ranked list — secondary candidates often share identical top semantic scores while comfortably fitting within 30–55s bounds.
- Invoking `yt-dlp` from datacenter IPs without proxy or cookies — triggers automated bot challenges; pass local rotating proxies (e.g. `:31001`) and Netscape cookies.
- Allowing social uploader calls without an explicit `UploadGateCheck` object — risks publishing unverified or partially failed artifacts; fail-close when gate_check is None.
- Assuming an LLM router natively supports video streaming because it returns HTTP 200 — proxies often swallow media silently; verify with a semantic temporal probe before claiming direct-video support.
- Forcing tight 9:16 portrait crops on talking-head videos with slides or multi-person interaction — cuts presentation slides and creates claustrophobic viewing; use `SAFE_WIDE` as the stable default.
- Generating new ASS subtitles over source footage that already has visible subtitles — produces unreadable duplicate caption collisions; detect visible subtitles in preflight and enforce `SOURCE_EXISTING` (zero new subtitle filters).
- Skipping subtitle QC entirely for `subtitle_policy == 'GENERATE'` because "we trust our own subtitles" — generated subtitles can have overlapping events, lingering text, or ASR gibberish; validate the ASS timeline file as authoritative ground truth (`OVERLAPPING_EVENT_COUNT == 0, MAX_SIMULTANEOUS_EVENTS <= 1, ASS_DIALOGUE_COUNT > 0`).
- Flagging static presentation slides or diagrams as stuck subtitles in visual QC when `subtitle_policy == "SOURCE_EXISTING"` — source graphics are part of the original footage, not generated caption bugs.
- Sleeping for 300 seconds on content QC rejections — stalls automated pipeline discovery; immediately restart discovery on content failure and reserve backoff sleep strictly for network/API rate limits.
- Reprocessing the exact same failed candidate repeatedly across cycles — wastes compute and API budget; record candidate fingerprints in a cooldown blacklist.
- Sizing generated portrait subtitles too large (>48pt) or setting vertical margins too deep (>500px) — causes bottom clipping on mobile Shorts/Reels interfaces; clamp font size to 46pt and MarginV to 440px.
- Applying FFmpeg `boxblur` directly on full-resolution 1080x1920 canvases without pre-scaling — causes severe CPU exhaustion and encode timeouts (120s+); downscale to 270x480 first before blurring and scaling back up.
- In-place editing of active repositories or production databases during major architecture refactoring — risks corrupting running continuous daemons and dashboards; use isolated worktrees and separate databases.
- Calculating subtitle stuck/duplicate detection on whole-ROI edge maps instead of text-masked pixel overlap — background movement obscures text changes and triggers false duplicate rejections.
- Flagging safe-zone danger breaches in top/bottom strips without asserting horizontal centering — triggers false alarms on studio corner decor and monitors.
- Calling `resp.json()` on multimodal LLM proxy endpoints without checking for SSE `data:` prefixes — causes unhandled `JSONDecodeError` when proxies stream chunks despite `stream=False`.
- Setting horizontal subtitle margins to default 40px in 1080x1920 ASS styles — causes long lines to clip against mobile screen edges; enforce `MarginL=90, MarginR=90`.
- Naively using `SUBTITLE_SAFE_FULL_WIDTH` letterboxing for burned-in subtitles — makes the speaker and text too small on mobile; use `SUBTITLE_PRESERVE_COMPOSITE` to crop the subject prominently while preserving the authentic subtitle band.
- Falling back to default center crop or empty frame on single-frame face detection misses — causes jarring flicker/jumps; use temporal hysteresis to hold previous framing across temporary face loss.
- Allowing unconstrained keyframe crop coordinate shifts within a continuous shot — creates jerky camera movement; clamp displacement per second to smooth out detector jitter.
- Passing raw ASR transcripts containing podcast censorship bleep hallucinations into subtitle generators without a gibberish filtering guard.
- Scaling and blurring the entire video frame without excluding the bottom subtitle region — leaves smeared, legible "ghost subtitles" in the top/bottom letterbox bars.
- Using YouTube/phrase-level transcript segment timing for generated subtitles instead of clip-local word-level ASR — segment timestamps overlap inherently across adjacent phrases, producing 15-20 simultaneous Dialogue events in the ASS file; only word-level faster-whisper timestamps produce correct non-overlapping subtitle timelines.
- Validating generated subtitle timing with pixel-level stuck-subtitle heuristics instead of parsing the authoritative ASS Dialogue event intervals — pixel QC produces false positives on legitimately long-duration phrases and misses actual timeline overlaps that only appear as brief stacking; parse the `.ass` file directly and assert `overlapping_events == 0, max_simultaneous == 1`.
- Holding generated subtitle on screen through speech silence gaps (>300ms) until the next phrase — creates lingering ghost text that confuses viewers; enforce subtitle OFF during pauses by clamping `event.end` to `last_word.end + linger(80-150ms)` and clearing before the gap.
- Adding artificial `drawtext` overlays to test video files that already contain burned-in subtitles, inadvertently creating false double-layer defects.
- Asserting subtitle suppression using in-memory flags alone instead of asserting that `subtitles=`, `ass=`, and `drawtext=` are strictly absent from the compiled FFmpeg filtergraph string.
- Using disjoint `between()` or open inequalities for dynamic FFmpeg expressions — creates 1-frame gaps at boundary timestamps that manifest as periodic flashes.
- Generating new ASS/karaoke subtitles over footage that already has embedded or burned-in subtitles, creating unreadable overlapping captions.
- Cropping tightly to a face in 9:16 when wide burned-in subtitles exist, slicing off words on the left and right edges.
- Assuming an OpenAI-compatible API endpoint natively ingests video files without running a lightweight capability probe first.
- Parsing unstructured LLM responses to drive rendering parameters without strict Pydantic/schema validation and local deterministic fallbacks.
- Smoothing or interpolating face tracking bounding boxes across hard scene cuts — causes severe visual face morphing, smeared frames, and unnatural panning between unrelated subjects.
- Relying on video title, channel, or country metadata for language gating — creators often use English titles for native content or vice versa; spoken transcript tokens must be the authoritative source of truth.
- Allowing continuous face trajectory to persist when a speaker leaves the frame instead of resetting to a segmented timeline and safe blurred fallback.
- Setting mobile subtitles too small (< 48pt) or too low in the 1080x1920 canvas where TikTok/Shorts UI controls obscure the text.
- Arbitrary mechanical word chunking that splits negations or prepositions across lines, breaking speech comprehension.
- Submitting music videos or stylized montages as representative validation — musical accompaniment and rapid source cuts conceal framing flaws and audio mastering defects.
- Declaring "product-quality PASS" from automated tests alone without independent visual inspection of authentic dialogue footage.
- Relaxing production duration constraints in QC code to make a 4-second smoke test pass instead of parameterizing mode/fixture.
- Depending on unpinned or host-ambient Python packages that fail in a fresh virtualenv on headless Linux.
- Skipping audio cleanup in error handlers, causing temporary disk exhaustion.
- Packing the entire repository working tree with bloated test renders, `.git`, or venv into the reviewer handoff instead of using `git archive` plus curated audit artifacts.
- Sending full 100-200MB podcast source videos to multimodal LLM endpoints via base64 — causes HTTP 400 payload size rejection; always pre-slice the candidate window (30-55s, CRF 28 ultrafast, <20MB) before base64-encoding.
- Letting Gemini QC or preflight fallback silently return `passed=True` when the invocation failed — creates false confidence in video quality; fallback must return `passed=False` with blocking reason "QC unavailable".
- Using boolean-only subtitle detection (`has_burned=True/False`) without explicit confidence or state tracking — causes irrecoverable false-positive cascades; use `NONE | EMBEDDED_TRACK | BURNED_IN | UNKNOWN` with numeric confidence.
- Trusting local Canny edge density burned-in detector without center-alignment and aspect-ratio contour filtering — studio desk monitors, shirt logos, and floor markers in the bottom ROI produce persistent false positives; use Otsu + contour analysis + Gemini semantic override.
- Treating subtitle detection UNKNOWN as SOURCE_EXISTING — silently suppresses subtitle generation for videos that need it; UNKNOWN must trigger candidate REJECT, never subtitle suppression.
- Downloading AV1-codec videos on servers without hardware AV1 decoding — OpenCV reads return empty frames with hundreds of stderr warnings but no Python exception; prefer `[vcodec^=avc]` in yt-dlp format selector.
- Running FFmpeg render from full source files without `-t duration` flag — ffmpeg processes the entire 1-2 hour file after seeking, causing 10-minute+ timeouts; always pass `-t clip_duration` even when `-ss` is specified.
- Widening a function signature (adding new kwargs) without searching the test tree for hand-rolled mocks — mocks reimplement the old signature shape and fail with `unexpected keyword argument` on the first real pipeline run.
- Authoring acceptance test harnesses or temporary runner scripts inside the repository working tree during black-box verification — violates the zero-source-mutation invariant and dirties git status; always place acceptance runners in `/tmp/`.
- Leaving multi-hour raw podcast video downloads unpruned in `downloads/` across automated multi-cycle discovery loops — quickly fills VPS root disk to 100% capacity, causing SQLite `database or disk is full` and FFmpeg write failures; enforce aggressive raw media cleanup after clip slicing.
- Accessing Pydantic model attributes directly without `getattr(obj, 'attr', default)` in audit reporting and packaging runners — raises fatal `AttributeError` on minor schema field differences (e.g. `existing_visible_subtitles` vs `existing_subtitles`) and halts unattended black-box test runs.
- Defaulting `UNKNOWN` or ambiguous subtitle detection to `GENERATE` or `SOURCE_EXISTING` — creates either double subtitles (if source had subtitles) or missing subtitles; strictly treat `UNKNOWN` as candidate `REJECT`.
- Cutting candidate video strictly at the target duration ceiling without checking sentence/thought completeness — produces abrupt, hanging endings (e.g. "waktu itu masih..."); inspect sentence boundary and extend if within max duration, or reject candidate if extending exceeds duration cap.
- Treating natural speech pauses (laughter, breathing, brief thinking pause) as automatic sentence endings using naive silence thresholds (e.g. pause > 300ms) — cuts speakers off mid-thought; require terminal grammatical/semantic punctuation or LLM ending verification.
- Allowing rendered videos with double subtitles or hanging endings to pass final QC — final multimodal video QC must explicitly assert `double_subtitles_detected == False`, `ending_complete == True`, and `ending_natural == True`.
- Using raw transcript or subtitle strings as YouTube Shorts titles without ranking candidates — produces fragmented phrases with trailing words and poor viewer retention; generate 5 ranked candidates with ethical curiosity gap (<= 85 chars).
- Relying on generic promotional boilerplates or raw title copies for Shorts upload descriptions — fails to provide editorial context; structure into 1-3 short paragraphs explaining discussion premise and key takeaways with 3-6 focused hashtags.
- Touching video rendering, audio filters, or transcription code during metadata fixes — violates surgical isolation; isolate metadata changes strictly to post-QC generation and uploader call-sites (TARGET <= 3 files).
- Guessing SQLite column names (e.g. `upload_id` vs `id`) in external acceptance runners without inspecting `PRAGMA table_info` — causes fatal `sqlite3.OperationalError` during live unattended runs.
- Hardcoding operational states (e.g. `privacy_status = 'private'`) in function signatures and caller call-sites without `os.getenv` fallbacks — prevents zero-mutation configuration changes during production promotion and forces unapproved code edits on frozen release candidates.
- Creating and pushing git release tags before auditing that all required production runtime parameters (privacy status, proxies, service units) can be configured via environment or flags — forces tag deletion or reassignment if a surgical configuration patch is subsequently needed.
- Hardcoding static search queries across continuous multi-hour discovery loops — exhausts results and repeatedly re-evaluates the same rejected videos; allow the dynamic search planner to adapt queries from recent rejection logs.
- Attempting to verify YouTube video publication privacy status via `videos().list(part="status")` using a token scoped strictly to `youtube.upload` — fails with HTTP 403 `insufficientPermissions`; use the public YouTube oEmbed API (`https://www.youtube.com/oembed?url=...`) which returns HTTP 200 for public videos and HTTP 403 for private ones without extra OAuth scopes.
- Accessing non-existent top-level helper attributes (e.g. `result.upload_url`) on orchestrator `PipelineResult` objects in daemon logging scripts — raises unhandled `AttributeError` and crashes long-running soak test loops right after successful uploads; defensively read from `result.upload_result.get("url")` or database rows.
- Concluding that a media clipper daemon is dead or stopped based solely on `systemctl status <legacy_unit>` after a version migration — autonomous soak tests and newer versioned pipelines (e.g. V3.1) often run via detached runner scripts in separate worktrees (`auto-short-generator-v3/soak_test_24h/`); always inspect `ps aux` for active runners across all project versions before reporting downtime.
