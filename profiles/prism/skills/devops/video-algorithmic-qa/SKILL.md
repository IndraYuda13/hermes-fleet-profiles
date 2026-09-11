---
name: video-algorithmic-qa
description: Use when verifying video framing, composites, and subtitles.
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [video, verification, qa, opencv, ffmpeg, subtitles]
    category: devops
---

# Video Algorithmic QA & Verification

Procedural rules and techniques for independent verification of automated video framing, multi-layer composite rendering, subtitle alignment, and visual continuity.

## Core Verification Invariants

When verifying algorithmic video pipelines (such as automated short crop engines or dual-layer subtitle composites), never rely on human visual intuition or single-frame inspection alone. Apply these programmatic verification rules:

### 1. Pixel Provenance & Authenticity Check
To prove a composite layer (e.g. preserved subtitle band or foreground punch-in) is 100% authentic source pixels without synthetic OCR re-burn, hallucination, or ghost bleed:
- Crop the corresponding raw coordinate slice from the source video frame.
- Resize using the exact target filter/interpolation (`INTER_CUBIC` / `flags=bicubic`).
- Extract the rendered output layer at identical timestamps and compute the mean pixel absolute difference:
  $$\Delta = \frac{1}{N} \sum |P_{\text{composite}} - P_{\text{scaled\_src}}|$$
- **Rule:** A mean pixel difference within standard codec quantization noise ($\Delta < 5.0$ for H.264) computationally proves authentic pixel provenance. Any secondary text burn-in or OCR drift immediately inflates $\Delta \gg 20.0$.

### 2. Quantitative Face & Subject Magnification
Never claim "subject is prominent" without baseline bounding box measurements:
- Run a calibrated detector (e.g. YuNet ONNX) on source excerpt frames vs final rendered frames.
- Calculate subject bounding height $H_{\text{out}}$ vs letterbox baseline $H_{\text{base}}$.
- Verify magnification ratio:
  $$\text{Ratio} = \frac{H_{\text{out}}}{H_{\text{base}}} \ge \text{Target (e.g. } 1.5\text{x)}$$
- Require checks across multiple representative timestamps across the timeline.

### 3. Timeline Overlap & Subtitle Collision Audit
When validating subtitle tracks (ASS / SRT / WebVTT):
- Parse all dialogue event intervals $[t_{\text{start}}, t_{\text{end}}]$.
- Assert strict monotonic non-overlap invariant:
  $$t_{\text{end}}^{(i)} \le t_{\text{start}}^{(i+1)}$$
- Enforce minimum inter-caption epsilon buffer $\epsilon \ge 0.02\text{s}$ (20ms) between adjacent dialogue events ($t_{\text{start}}^{(i+1)} - t_{\text{end}}^{(i)} \ge \epsilon$) to prevent libass rendering engines from conflating adjacent events into simultaneous collision lanes.
- Enforce silence gap clearing: When pause between spoken phrases exceeds $0.30\text{s}$ (300ms), dialogue event $i$ must close so screen clears completely during silence. Never allow subtitles to linger frozen until the next utterance (stuck-subtitle defect).
- Flag any overlapping intervals where multiple dialogue events render on screen simultaneously (max simultaneous active caption lane = 1).
- Enforce phrase grouping bounds: Dialogue events should be chunked into 2--5 word phrases to prevent horizontal boundary overflow.

### 4. Intra-Shot Motion Clamping vs Scene-Cut Reacquisition
When auditing camera tracking / panning smoothing:
- Detect scene cuts across the source video.
- For all adjacent keyframe pairs $(t_1, t_2)$:
  $$\text{Rate} = \frac{|\Delta x|}{t_2 - t_1}$$
- **Invariant:** Within the same shot (no intervening scene cut), $\text{Rate} \le \text{Max Clamping Threshold}$ (e.g. $0.08 / \text{sec}$) to guarantee smooth gliding without jarring jumps.
- Across hard scene cuts, instant reacquisition is permitted ($\text{Rate} > \text{Threshold}$ allowed) to prevent cross-cut motion lag.

### 5. Programmatic Full-Timeline Empty Frame Scan
To prove zero empty-subject frames or unintended fallback dropouts:
- Sample video frames across the entire duration at fixed intervals (e.g. every 1.0s or 2.0s).
- Run detector inference and assert $\text{empty\_count} == 0$.

### 6. Background Blur Ghost Face Suppression in Letterbox/Canvas QC
When auditing full-frame letterbox/pillarbox vertical layouts with blurred backgrounds:
- DNN face detectors (e.g. YuNet) will detect enlarged ghost faces in coarse background blurs touching canvas edges ($y=0$ or $y+h=H$), falsely tripping headroom or boundary truncation rules.
- **Rule:** In canvas QC, filter candidate face detections with $\text{conf} \ge 0.55$ (or calibrate against background contrast) and ensure background layers are sufficiently downscaled/blurred before canvas compositing.

### 7. Downscale-Blur-Upscale Optimization & Render Timeout Budgeting
Applying multi-pass blur (`boxblur`/`gblur`) at native vertical canvas resolution ($1080 \times 1920$) across hundreds of frames on CPU causes massive convolution overhead ($>3\text{s}$ per video second), exceeding standard subprocess timeouts ($120\text{s}$).
- **Rule:** Downscale before blurring, then upscale back (`scale=270:480,boxblur=10:2,scale=1080:1920`). This yields $10\text{--}20\times$ faster rendering with indistinguishable perceptual blur.
- Subprocess timeouts for software H.264 encode with two-pass loudnorm must be budgeted at minimum $8\times$ the target clip duration.

### 8. Programmatic EBU R128 Audio Loudness & True Peak Verification
Never certify broadcast audio normalization from filter configuration strings alone:
- Execute FFmpeg's `ebur128` filter with `peak=true` on the rendered container:
  `ffmpeg -nostats -i output.mp4 -filter_complex ebur128=peak=true -f null -`
- Extract `Integrated loudness (I)` and assert target compliance (e.g. $-16.0 \pm 1.0\text{ LUFS}$).
- Extract `True peak (Peak)` and assert ceiling compliance ($\le -1.5\text{ dBFS}$).

### 9. Multimodal Direct-Video Quality Control & Safe-Zone Auditing
When auditing rendered vertical video through multimodal direct-video inspection:
- **Anti-Double-Caption Invariant:** Ensure newly generated subtitle layers never collide with or overlay pre-existing burned-in source subtitles. If source video already has burnt subtitles, verify the pipeline either crops/masks them or suppresses generation.
- **Safe-Zone Compliance:** Subtitle bounding boxes must remain inside mobile vertical safe margins (e.g. at least 15% clear of bottom for title/audio bar, and 10% clear of right rail for like/comment icons).
- **Fail-Closed QC Policy:** Automated multimodal video evaluations must output structured verdicts with an explicit score threshold (e.g. $\ge 70/100$) and itemized blocking defect reasons. Subprocess timeouts, API errors, or unparseable outputs must fail closed and flag review, never silently approve.

### 10. Hybrid ASR-Timing Ground Truth & Verbatim Correction Mapping
When verifying hybrid subtitle pipelines that pair acoustic aligners (e.g. Whisper word timestamps) with LLM verbatim text cleaners:
- **Timing Invariant:** Acoustic word alignment timestamps ($t_{\text{start}}, t_{\text{end}}$) are canonical ground truth. Never allow text LLMs to synthesize or interpolate timing timestamps.
- **Token-to-Span Alignment:** When mapping LLM-corrected words (e.g. slang, proper nouns, code-switching) onto ASR tokens, map corrections strictly onto the corresponding acoustic time spans. Retain original start and end bounds to avoid subtitle drift.

### 11. Strict Subtitle Policy Hierarchy & Zero-ASS Filtergraph Invariant
When auditing pipelines with automated subtitle generation and existing caption detection:
- **Policy Mapping Invariant:** Source clips with embedded subtitle streams (`ffprobe -select_streams s`) or burned-in subtitles (Otsu morphology or multimodal vision) must strictly map to `SOURCE_EXISTING`. Only clips confirmed to have zero subtitles map to `GENERATE`.
- **Zero-ASS Filtergraph Invariant:** When policy is `SOURCE_EXISTING`, verify the compiled FFmpeg filtergraph contains exactly 0 `subtitles=` and 0 `ass=` filters (e.g. `[v_base]null[v_out]`), and zero generated ASS subtitle files are passed to the renderer.
- **Fail-Closed on Ambiguity (Never Guess):** If detection yields `UNKNOWN`, multimodal confidence is low (< 0.70), or local detection conflicts with multimodal inspection (e.g. Local BURNED_IN vs Vision NONE), the candidate must be rejected immediately (`REJECTED_VISUAL`). Never default to generating subtitles when uncertain.
- **QC Gate Double Subtitle Rejection:** Multimodal final QC must enforce `double_subtitles_detected: bool` and `has_double_subtitles: PASS|FAIL`. Any simultaneous appearance of source burned-in subtitles and newly generated captions must trigger immediate hard failure (`passed=False`), quarantine into `failed/`, and block publication.

### 12. Natural Sentence Ending Verification & Dynamic Extension Bounds
When auditing candidate clip boundaries and dialogue endings:
- **Dangling Ending Pattern Detection:** Dialogue ending text must be inspected for dangling conjunctions/connectors (`dan`, `karena`, `yang`, `masih`, `sebenarnya`, etc.), incomplete phrases (`waktu itu masih`, `karena sebenarnya`, `jadi hidup`), trailing ellipses (`...`, `…`), and mid-sentence punctuation (`,`, `;`, `:`, `-`). Any match falsifies sentence completion.
- **Natural Pause Differentiation:** Natural mid-speech pauses (>300ms silence), laughter, or breathing in the middle of dialogue must NOT be misidentified as premature endings if the final thought reaches a complete, terminal conclusion.
- **Bounded Sentence Extension & Candidate Fallback:** When an incomplete ending is detected:
  - Dynamically accumulate subsequent transcript segments up to the next complete sentence boundary.
  - Assert the strict duration ceiling: If $t_{\text{extended}} - t_{\text{start}} \le \text{Max Duration}$ (e.g. 55.0s), apply the extended boundary.
  - If completion requires $> \text{Max Duration}$, strictly reject the candidate and trigger candidate fallback to the next ranked candidate.
  - When multimodal preflight flags an ending on text that appeared complete, pass `force_extend=True` and verify $t_{\text{new\_end}} > t_{\text{clip\_end}}$.
- **QC Gate Mid-Sentence Cutoff Rejection:** Final video QC must enforce `ending_complete: PASS|FAIL` and `ending_natural: PASS|FAIL`. Any audio/visual cutoff mid-word or mid-thought must trigger hard failure (`passed=False`) and quarantine into `failed/`.
