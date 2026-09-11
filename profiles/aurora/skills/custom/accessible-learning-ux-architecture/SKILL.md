---
name: accessible-learning-ux-architecture
description: "Use when designing inclusive or assistive learning UI."
version: 1.0.0
metadata:
  hermes:
    tags: [accessibility, a11y, education, inclusive-design, deaf-hard-of-hearing]
    category: custom
---

# Accessible Learning & Classroom Display UX Architecture

A class-level guide for designing, auditing, and structuring inclusive learning applications, assistive platforms, live captioning/STT tools, and classroom projector displays—especially for Deaf and Hard-of-Hearing (DHH) learners.

---

## 1. Auditory Independence & Multimodal Feedback

- **Never Depend on Auditory-Only Signals:** Avoid `<audio>` cues (such as loop background music or ding sounds) as the sole indicator for state changes, timer urgency, or quiz results.
- **Forbid Ambient Background Music in DHH Tools:** Never include auto-playing or looping background music (`<audio loop>`) in assistive/DHH learning apps. It provides zero semantic value to deaf learners while causing severe acoustic distortion and fatigue for users with hearing aids or cochlear implants.
- **Visual Rhythm / Metronome:** For time-sensitive tasks, substitute audio tempo with a smooth visual rhythm bar (e.g. pulsing 2s gradient bar) or circular SVG countdown ring.
- **Visual Earcons (Edge Vignette):**
  - *Correct / Success:* Soft screen-edge flash (`box-shadow: inset 0 0 40px rgba(34, 197, 94, 0.4)` for 600ms).
  - *Error / Incorrect:* Gentle horizontal wobble on the target card (`transform: translateX(-4px)` for 300ms). Never use rapid full-screen strobes that trigger photosensitive seizures.
- **Speech Amplitude Meter:** Provide a live visual audio-level wave/bar next to microphone status so DHH users can verify speaker activity before text transcription renders.
- **Non-Verbal Ambient Markers:** When transcription is live, display contextual brackets for ambient class events (`[Tawa]`, `[Tepuk Tangan]`, `[Hening]`).

---

## 2. Classroom Projector & Distance Viewing Ergonomics

- **Guard Against the 1024x768 XGA Breakpoint Trap:**
  - Most classroom projectors run at 4:3 1024x768 (XGA) or 720p. Setting mobile collapse at `@media (max-width: 1024px)` collapses two-column layouts into an excessively tall vertical stack (>1200px), hiding sidebars, notes, and quiz controls below the 768px fold.
  - Set the split-column responsive breakpoint at `<=840px` or `<=768px` so 1024px displays retain side-by-side split view.
- **Ambient Light Washout Mitigation:**
  - School projectors with 2000–3500 ANSI lumens under room lighting suffer contrast degradation on light-gray backgrounds.
  - Provide a dedicated **High-Contrast Dark Mode** (`#090D16` base, `#FFFFFF` text at 19:1 contrast, `#FACC15` keyword highlight, `#38BDF8` translation). Pure dark surfaces do not reflect projector beam light, maximizing text edge acuity from the back row.
- **Fluid Typography:**
  - Use CSS `clamp()` (e.g., `font-size: clamp(2rem, 3.2vw + 1.2vh, 4.2rem)`) for live captions instead of static rem/px values to maintain legibility from 5–10 meters away.
- **Text Wrapping Defense:** Always specify `overflow-wrap: break-word` on dynamic transcription containers to prevent silent horizontal clipping when long words or transliterations occur without spaces.

---

## 3. Live Streaming Text & Teleprompter DOM Architecture

- **Interim Token Contrast Invariant:**
  - Never use light-gray or faded colors (e.g. `#9ca3af` on `#ffffff`, which yields ~2.5:1 contrast) to represent streaming/interim words. Projectors and ambient light wash out low contrast instantly.
  - Distinguish interim in-progress tokens from finalized tokens using WCAG-compliant styling: full-contrast text (`>=4.5:1`) paired with a dashed bottom border (`border-bottom: 2px dashed var(--accent)`) or subtle pill background.
- **Zero-Loss Session Auto-Drafting:**
  - Assistive STT sessions must persist real-time sentences continuously to client-side storage (`localStorage` or IndexedDB rolling buffer).
  - Never rely exclusively on a manual "Save" button at the end of class—accidental navigation, browser crashes, or tab closures must restore uncommitted transcript history immediately upon reopen.
- **Mitigate Dual-Gaze Fatigue:**
  - DHH students continuously divide visual attention between the teacher's lips/hands and the screen. Continual re-rendering via `innerHTML` causes text jumping and flicker that disrupts eye tracking.
  - Separate static finalized sentence nodes from live interim tokens (`<span class="token-interim">`). Mutate only the trailing interim node via `textContent`.
- **Jitter-Free Auto-Scroll:**
  - Use CSS `overflow-anchor: auto; scroll-behavior: smooth;`.
  - Apply auto-scroll only when user is within 60-80px of the container bottom. If the user scrolls up to inspect previous phrases, pause auto-scroll and display a floating `↓ Return to Live` pill.
- **Inspection Freeze Mode:**
  - When an inline word is clicked to view definitions or phonetics, temporarily freeze live auto-scroll so the targeted card does not vanish or jump.

---

## 4. Visual Phonetics & Sign Language Integration

- **Pre-Lingual Deaf Phonetic Limitations:**
  - Transliterated phonetic text (e.g. English "how" -> Indonesian "hau") is abstract for learners who lack auditory memory.
  - Accompany phonetic transcriptions with visual articulation:
    - **Visemes:** Display SVG lip/mouth shape sprites (12–14 standard visemes for open vowel, rounded lip, bilabial closure, labiodental).
    - **Sign Language (BISINDO/SIBI):** Provide vector illustrations of gestures and fingerspelling alphabets alongside target vocabulary.

---

## 5. Shared Display Hit Targets & Teacher Ergonomics

- **Interactive Word Hit Targets:**
  - Clickable words within flowing sentences must have explicit padding (`padding: 4px 8px; min-height: 44px; display: inline-block;`) to prevent touch errors on smartboards.
  - Interactive words must have `role="button"`, `tabindex="0"`, and keyboard listeners (`Enter`/`Space`).
- **Wireless Presenter Clicker Shortcuts:**
  - Teachers using sign language cannot constantly return to mouse/trackpad. Support standard presenter keys:
    - `Space` / `Alt+M`: Toggle microphone on/off.
    - `F` / `F11`: Toggle distraction-free fullscreen projector mode.
    - `1`, `2`, `3`, `4`: Select quiz choices A, B, C, D.
    - `Escape`: Dismiss open popups/modals.
- **Distraction-Free Zen Mode:** Automatically hide mouse cursor (`cursor: none`) and technical chrome after 3 seconds of inactivity in presentation mode.
