# Video Quality, Continuity & Subtitle Framing Verification Matrix

Use this reference when specifying acceptance criteria or independently auditing automated video re-framing (landscape 16:9 to portrait 9:16), burned-in subtitle preservation, continuity tracking, and ASR audio transcription quality.

## 1. Subtitle-Preserving Composite Framing

When converting landscape video containing native burned-in subtitles to vertical portrait:
- **Never rely solely on full-width letterboxing (`SUBTITLE_SAFE_FULL_WIDTH`):** While it avoids horizontal text truncation, it shrinks the speaker/subject and text to unreadable dimensions on mobile devices.
- **Dual-Layer Composite Architecture:**
  1. **Video Layer (Subject / Face):** Crop vertically to 9:16 centered on speaker coordinates, strictly slicing above the subtitle band ($y \in [0, y_{sub\_top}]$). Forbid subtitle text leakage into this layer.
  2. **Subtitle Band Layer:** Crop full source width across the subtitle region ($y \in [y_{sub\_top}, ih]$), scale horizontally to canvas width ($1080\text{ px}$), and overlay in the lower portrait reading safe-zone ($y \approx 1400\text{--}1650$).
  3. **Background / Base:** Clean letterbox or non-repeating fill; strictly exclude subtitle region before blurring to prevent ghost text artifacts.
- **Verification Metrics:**
  - Subject face bounding box height $\ge 1.5\times$ compared to standard full-width letterbox.
  - Subtitle text height $\ge 36\text{ px}$ on 1080x1920 canvas; side margins $\ge 40\text{ px}$.
  - Zero synthetic subtitle overlay or duplicate rendering when source already contains subtitles.

## 2. Visual Continuity, Subject Presence & Temporal Hysteresis

Face detectors frequently lose detection momentarily due to head turns, hand gestures, motion blur, or compression artifacts.

- **State Model:**
  - `VALID_SUBJECT`: Face detected with score above confidence threshold ($\ge 0.50$). Update tracking position.
  - `TEMPORARY_FACE_LOSS` ($\le 1.5\text{--}2.0\text{ s}$ or $\le 2$ keyframe samples): Hold previous valid crop coordinates (`HOLD_PREVIOUS_FRAMING`). Forbid falling back to default center crop or blurred backgrounds on momentary misses.
  - `NO_VALID_SUBJECT` ($> 2.0\text{ s}$ continuous loss): Transition smoothly to deterministic fallback.
- **Hard Scene Cut Invariant:**
  - Scene cuts immediately invalidate and reset the hysteresis tracker.
  - Forbid carrying over (`HOLD`) crop coordinates across camera cuts; allow instant reacquisition on the new shot.

## 3. Motion Limits & Displacement Clamping

Prevent unnatural camera wobble or abrupt jumping within the same continuous shot:
- **Intra-Shot Displacement Limits:**
  - Horizontal displacement: Max $\Delta X \le 0.08$ normalized width/s ($\approx 100\text{ px/s}$ on 1280px width).
  - Vertical displacement: Max $\Delta Y \le 0.04$ normalized height/s ($\approx 30\text{ px/s}$ on 720px height).
  - Clamp detector outliers to $X_{prev} \pm \Delta X_{max}$.
- **Inter-Shot (Scene Cuts):** Release clamping at detected scene cut timestamps to allow immediate center-on-speaker framing for the new camera angle.

## 4. Subtitle ASR & Quality Guards

- **Forced Language & Decoding Configuration:**
  - Pass explicit language hints (e.g. `language="id"` for Indonesian) and `beam_size >= 5`.
- **Nonsense / Bleep Audio Filtering:**
  - Audio bleeps, background laughter, or low-SNR segments cause autoregressive ASR models to emit repetitive hallucinated monosyllables (e.g. repeated bleep/tut/mem tokens).
  - Enforce word-level confidence filtering (flag or drop tokens with probability $< 0.25$).
  - Scan for repetitive monosyllabic patterns and discard nonsense bursts before ASS event generation.
- **Interval Overlap Invariant:**
  - Strictly enforce $\max(start_i, start_j) < \min(end_i, end_j) = \text{False} \quad \forall i \neq j$. Subtitle dialogue lines must have zero temporal collision across the entire render.
