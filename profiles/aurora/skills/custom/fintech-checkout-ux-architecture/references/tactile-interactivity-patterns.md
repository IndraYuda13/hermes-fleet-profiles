# Tactile Physics, Procedural Audio & High-Interactivity Design Patterns

This guide formalizes design architectures for turning static or template-like dashboards into hyper-interactive, living consoles without falling into visual clutter or sluggish performance.

---

## 1. Kinetic Physics & Mass on 2D Canvas

### Hooke's Law & Velocity Damping
Canvas elements (such as topology graph nodes or telemetry cards) should feel tangible rather than locked to rigid coordinate grids.
* **Euler Integration:**
  $$v_{t+1} = (v_t + \frac{F_{spring}}{mass}) \times \text{damping}$$
  $$x_{t+1} = x_t + v_{t+1}$$
* **Parameters:**
  * Spring stiffness: `0.10` - `0.15`
  * Velocity damping: `0.80` - `0.85` (ensures fast settlement within 250-400ms without endless oscillation)
  * Rest threshold: Velocity $< 0.01\text{px/frame}$ disables calculation to conserve battery/CPU.

---

## 2. Visual Cause & Effect (Cascading Shockwaves)

Actions that affect distributed services or system components should demonstrate their blast radius visually:
* **Shockwave Ripple Formula:**
  Expand radial ring from the source coordinate:
  * Radius: $r(t) = r_0 + \Delta r \cdot (1 - e^{-k t})$
  * Alpha: $\alpha(t) = \alpha_0 \cdot \max(0, 1 - \frac{t}{t_{duration}})$
* **Adjacency Traversal:**
  Traverse connected downstream edges with a cascading offset of $80\text{ms} - 120\text{ms}$ per hop. Downstream nodes trigger subtle secondary pulses upon shockwave arrival.

---

## 3. Zero-Asset Procedural Audio (Web Audio API)

Zero external MP3/WAV assets keep the application lightweight, instant-loading, and responsive.

### Audio Context Lazy Initialization & Autoplay Compliance
Browsers block audio context creation before user interaction. Initialize audio on the first `pointerdown` or `click` event:
```javascript
let audioCtx = null;
function getAudioContext() {
  if (!audioCtx) {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (AudioContext) audioCtx = new AudioContext();
  }
  if (audioCtx && audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
  return audioCtx;
}
```

### Sound Recipes
1. **Tactile Button/Node Click (Subtle Pitch Drop):**
   * Oscillator: Sine wave
   * Frequency: $1200\text{Hz} \to 400\text{Hz}$ exponential ramp over $35\text{ms}$
   * Gain: $0.15 \to 0.001$ exponential decay over $40\text{ms}$
2. **Warning / Emergency Alarm Chime:**
   * Oscillators: Dual detuned sawtooth waves ($440\text{Hz}$ and $448\text{Hz}$)
   * LFO: $8\text{Hz}$ amplitude modulation
   * Gain: $0.2 \to 0.001$ over $300\text{ms}$
3. **System Recovery / Success Harmonic Sweep:**
   * Triad major chord arpeggio ($C_5 \to E_5 \to G_5$)
   * Oscillator: Pure sine wave with soft low-pass filter ($2000\text{Hz}$)
   * Duration: $250\text{ms}$ total with decaying envelope

---

## 4. Time-Travel Scrubber & Live Ring Buffers

To enable interactive timeline scrubbing without overloading memory:
* Use a fixed-size circular ring buffer (e.g. 120 slots for 60 seconds at 2Hz updates).
* When scrubbing starts, pause live stream ingestion and freeze the canvas render to the inspected historical timestamp.
* Snap the crosshair to the nearest data point with a floating specular inspector badge displaying multi-metric telemetry.
