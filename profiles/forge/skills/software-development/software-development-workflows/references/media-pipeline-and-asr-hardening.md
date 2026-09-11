# Media Pipeline, ASR Alignment & Multimodal Video QC Hardening

## 1. Fast Stream-Copy Slicing vs Re-encoding

In automated video clipping pipelines, candidate clips must be extracted before passing them to ASR (Whisper) or multimodal LLM evaluators (Gemini).

### Pitfall: Re-encoding Bottleneck & Silent Full-Video Fallback
- Using `-c:v libx264` to slice a 40-second clip from a 1-hour source takes 30-90 seconds on CPU, frequently hitting subprocess timeouts.
- Catching subprocess timeout and falling back to the original `video_path` causes Whisper to transcribe from second 0:00 of the 1-hour video instead of second 402, throwing all downstream alignments completely out of sync.

### Canonical Rule
1. Always use stream-copy slicing with fastseek:
   ```python
   cmd = [
       "ffmpeg", "-y",
       "-ss", f"{start_sec:.3f}",
       "-i", video_path,
   ]
   if duration_sec is not None and duration_sec > 0:
       cmd.extend(["-t", f"{duration_sec:.3f}"])
   cmd.extend([
       "-c", "copy",
       "-movflags", "+faststart",
       tmp_slice,
   ])
   ```
   This executes in <0.3s (500x speedup) with zero quality loss and preserves keyframe-relative audio-video boundaries.
2. **Fail-Closed on Non-Zero Offset:** If slicing fails and `start_sec > 0`, raise `RuntimeError` immediately. Never fall back to the un-sliced source file.

---

## 2. Whisper `initial_prompt` Prompt-Skipping Quirk

### Mechanism
In OpenAI Whisper and `faster-whisper`, `initial_prompt` is designed as conditioning context representing *previously emitted text* from preceding 30-second windows.

If you pass a verbatim speech transcript or excerpt of the *current* audio slice in `initial_prompt` (e.g. attempting to give Whisper a "hint"):
- Whisper assumes that portion of the audio has already been transcribed in the preceding window.
- Whisper skips forward and suppresses the first N seconds of speech, only beginning transcription from where the prompt excerpt ended.

### Canonical Rule
- In `initial_prompt`, include **only** general style/language hints and isolated proper nouns or hotwords:
  ```python
  # CORRECT:
  initial_prompt = "Percakapan podcast santai bahasa Indonesia. Kata kunci: Mas Bilal, Kak Jeje, self love, muka bumi, nomor tiga."

  # WRONG (causes Whisper to skip the first 15 seconds):
  initial_prompt = "Kutipan: Dan ketika kita berhasil, Mas Bilal, mencintai diri kita sendiri..."
  ```
- Use reference transcripts in the downstream LLM evidence-fusion step (e.g., Gemini native-video verification), never in Whisper's `initial_prompt`.

---

## 3. Worker Cgroup Memory Limits & Execution Strategy

### Mechanism
Hermes background terminal sessions spawned via `terminal(background=true)` run inside transient cgroup scopes (`hermes-worker-*.scope`) with a memory limit (~4GB RSS).
- Loading `faster-whisper` `large-v3` on CPU along with runtime buffers can exceed 4GB RSS, triggering an instant kernel OOM-killer (`exit_code: -9`).
- Synchronous terminal calls also enforce gateway timeouts (420s).

### Canonical Rule
- For heavy local ML models (Whisper large-v3, PyTorch CPU inference), process batch work in granular per-clip items rather than monolithic multi-clip runs.
- Persist intermediate progress/checkpoints to disk after each item completes (`rerender_test_summary.json`), ensuring completed work is never discarded if a subsequent item times out or fails.
