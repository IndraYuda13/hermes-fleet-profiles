# Video Quality, Continuity & Subtitle Framing Verification Matrix

Use this reference when specifying acceptance criteria or independently auditing automated video re-framing (landscape 16:9 to portrait 9:16), burned-in subtitle preservation, continuity tracking, audio loudness, and ASR transcription quality.

## 1. Subtitle-Preserving Composite Framing & Pixel Provenance

When converting landscape video containing native burned-in subtitles to vertical portrait:
- **Never rely solely on full-width letterboxing (`SUBTITLE_SAFE_FULL_WIDTH`):** It shrinks the speaker/subject and text to unreadable dimensions on mobile devices.
- **Dual-Layer Composite Architecture:**
  1. **Video Layer (Subject / Face):** Crop vertically to 9:16 centered on speaker coordinates, strictly slicing above the subtitle band ($y \in [0, y_{sub\_top}]$). Forbid subtitle text leakage into this layer.
  2. **Subtitle Band Layer:** Crop full source width across the subtitle region ($y \in [y_{sub\_top}, ih]$), scale horizontally to canvas width ($1080\text{ px}$), and overlay in the lower portrait reading safe-zone ($y \approx 1400\text{--}1650$).
  3. **Background / Base:** Clean letterbox or non-repeating fill; strictly exclude subtitle region before blurring to prevent ghost text artifacts.
- **Pixel Provenance & Authenticity Check:**
  - Crop raw coordinate slice from source frame, resize using matching interpolation (`INTER_CUBIC`), and compute mean pixel absolute difference:
    $$\Delta = \frac{1}{N} \sum |P_{\text{composite}} - P_{\text{scaled\_src}}|$$
  - A mean pixel difference within codec quantization noise ($\Delta < 5.0$ for H.264) computationally proves authentic source pixels. Secondary text burn-in or OCR drift inflates $\Delta \gg 20.0$.
- **Verification Metrics:**
  - Subject face bounding box height $\ge 1.5\times$ compared to standard full-width letterbox.
  - Subtitle text height $\ge 36\text{ px}$ on 1080x1920 canvas; side margins $\ge 40\text{ px}$.
  - Vertical safe margins: Subtitles must remain clear of bottom navigation (at least 15% margin) and right rail interaction bars (at least 10% margin).

## 2. Visual Continuity, Subject Presence & Temporal Hysteresis

Face detectors frequently lose detection momentarily due to head turns, hand gestures, motion blur, or compression artifacts.

- **State Model:**
  - `VALID_SUBJECT`: Face detected with confidence $\ge 0.50$. Update tracking position.
  - `TEMPORARY_FACE_LOSS` ($\le 1.5\text{--}2.0\text{ s}$ or $\le 2$ keyframe samples): Hold previous valid crop coordinates (`HOLD_PREVIOUS_FRAMING`). Forbid falling back to default center crop or blurred backgrounds on momentary misses.
  - `NO_VALID_SUBJECT` ($> 2.0\text{ s}$ continuous loss): Transition smoothly to deterministic fallback.
- **Hard Scene Cut Invariant:**
  - Scene cuts immediately invalidate and reset the hysteresis tracker.
  - Forbid carrying over (`HOLD`) crop coordinates across camera cuts; allow instant reacquisition on the new shot.
- **Full-Timeline Empty Frame Scan:**
  - Periodically sample frames across duration (every 1.0–2.0s), run detector inference, and assert zero empty subject frames.
- **Background Blur Ghost Face Suppression:**
  - Coarse background blurs touching canvas edges ($y=0$ or $y+h=H$) trigger false face detections. Filter candidate detections with $\text{conf} \ge 0.55$ and sufficiently downscale/blur background layers before compositing.

## 3. Motion Limits & Displacement Clamping

Prevent unnatural camera wobble or abrupt jumping within the same continuous shot:
- **Intra-Shot Rate Limits:**
  - Rate $\frac{|\Delta x|}{t_2 - t_1} \le 0.08 / \text{sec}$ ($\approx 100\text{ px/s}$ on 1280px width) to guarantee smooth camera gliding.
  - Vertical displacement: Max $\Delta Y \le 0.04$ normalized height/s ($\approx 30\text{ px/s}$ on 720px height).
  - Clamp detector outliers to $X_{prev} \pm \Delta X_{max}$.
- **Inter-Shot (Scene Cuts):** Release clamping at detected scene cut timestamps to allow immediate center-on-speaker framing for the new camera angle.

## 4. Subtitle Timeline, Policy & Quality Guards

- **Acoustic Timing Ground Truth:**
  - Acoustic word alignment timestamps ($t_{\text{start}}, t_{\text{end}}$) from aligners (Whisper word timestamps) are canonical ground truth. LLMs must never synthesize or interpolate timing timestamps.
  - Map LLM text corrections (slang, code-switching) strictly onto corresponding acoustic spans, retaining original start/end bounds.
- **Timeline Non-Overlap & Collision Invariant:**
  - Strictly monotonic non-overlap: $t_{\text{end}}^{(i)} \le t_{\text{start}}^{(i+1)}$ with minimum inter-caption epsilon buffer $\epsilon \ge 0.02\text{s}$ (20ms) to prevent libass collision lanes.
  - Max simultaneous active caption lanes = 1.
  - Silence gap clearing: When pause between spoken phrases exceeds $0.30\text{s}$ (300ms), dialogue event $i$ must close so screen clears during silence. Never let captions linger frozen into the next utterance.
  - Chunk dialogue events into 2–5 word phrases to prevent horizontal overflow.
- **Subtitle Policy Hierarchy & Zero-ASS Filtergraph:**
  - Source clips with embedded subtitle streams or burned-in subtitles strictly map to `SOURCE_EXISTING`. Only confirmed zero-subtitle clips map to `GENERATE`.
  - When policy is `SOURCE_EXISTING`, verify compiled FFmpeg filtergraph contains 0 `subtitles=` and 0 `ass=` filters.
  - Fail closed on detection ambiguity or conflict (< 0.70 confidence): reject immediately (`REJECTED_VISUAL`) rather than guessing.
- **ASR Decoding & Nonsense Filtering:**
  - Explicit language hints (e.g. `language="id"`) and `beam_size >= 5`.
  - Filter audio bleeps/laughter by dropping tokens with probability $< 0.25$ and discarding repetitive monosyllabic bursts before ASS generation.

## 5. Render Optimization & Audio Verification

- **Downscale-Blur-Upscale Optimization:**
  - Multi-pass blur at native 1080x1920 resolution on CPU exceeds subprocess timeouts (>3s per video second).
  - Downscale before blurring, then upscale back (`scale=270:480,boxblur=10:2,scale=1080:1920`).
  - Budget software H.264 encode timeouts at minimum $8\times$ target clip duration.
- **Programmatic EBU R128 Audio Loudness Verification:**
  - Run FFmpeg filter `ebur128=peak=true` and verify:
    - Integrated loudness (I): $-16.0 \pm 1.0\text{ LUFS}$.
    - True peak (Peak): $\le -1.5\text{ dBFS}$.
- **Natural Sentence Ending Verification:**
  - Inspect ending text for dangling conjunctions (`dan`, `karena`, `yang`, `masih`), incomplete phrases, trailing ellipses (`...`), or mid-sentence punctuation.
  - Differentiate natural pauses (>300ms mid-speech silence) from premature sentence cutoffs.
  - Dynamically extend transcript segments up to duration ceiling ($\le 55\text{s}$) or trigger candidate fallback if completion exceeds limit. Hard fail any video cutting off mid-word or mid-thought.
