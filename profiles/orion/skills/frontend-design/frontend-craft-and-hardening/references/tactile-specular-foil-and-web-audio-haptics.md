# Tactile Specular Foil, Web Audio Haptics & Anti-Slop E-Commerce Patterns

This guide documents proven patterns extracted from building high-craft e-commerce and digital voucher applications (such as LemonTopup 2026), inspired by modern interactive showcases (e.g. `sceneai.art`).

---

## 1. The 5 E-Commerce AI Slop Hallmarks

When auditing or building consumer digital store UIs, eliminate these 5 ubiquitous AI generator tropes:

| Slop Hallmark | Prohibited Cliché | Bespoke Craft Standard |
|---|---|---|
| **1. Vendor Leakage** | Leaking B2B backend provider names (e.g. "Digiflazz Detik Ini", "Stripe API Inside") in hero copy. | Consumer-focused service level copy: `Direct API Fulfillment` or `Proses Otomatis 24 Jam`. |
| **2. Hero Badge Pileup** | Stacking 3+ high-saturation, differently-colored pill badges above H1 (`⚡ TOP UP INSTAN`, `QRIS 24/7`, `0% ADMIN`). | Single integrated micro-telemetry status badge with subtle glowing pulse-dot and unified typography. |
| **3. 3-Card Value Proposition** | 3 bulky feature cards in a row below search (*QRIS Dinamis*, *Otomatisasi Detik*, *Saldo & Garansi*) pushing content below fold. | Inline compact micro-assurance strip (1 thin row with dot separators) directly elevating product catalog above the fold. |
| **4. Redundant Dual Search** | Navbar search button (`Cari ⌘K`) competing visually with a giant hero search bar right below it. | Unified search flow: navbar button invokes command palette modal, hero search input filters instantly with streamlined placeholder. |
| **5. Repetitive Card CTAs** | Repeating explicit text links like `PILIH >` or `BELI >` on every single category/product card. | Entire card is a tactile interactive surface with subtle hover lift (`translateY(-2px)`), 1px specular rim, and clean circular chevron indicator. |

---

## 2. Interactive Specular Sheen & Dynamic Foil Ray Engine

Inspired by high-end design showcases (`sceneai.art`, Apple Card UI, Linear), cards should possess material depth and responsive lighting rather than flat borders or cheap CSS box-shadow blobs.

### CSS Custom Property Setup
```css
.card-specular-target {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--border-subtle, rgba(255, 255, 255, 0.08));
  background: var(--surface-card, #101016);
  border-radius: var(--radius-md, 12px);
  transition: transform 0.18s cubic-bezier(0.16, 1, 0.3, 1),
              border-color 0.18s ease,
              box-shadow 0.18s ease;
  will-change: transform;
}

/* 1px Specular Top Light Catch */
.card-specular-target::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.12), transparent);
  pointer-events: none;
}

/* Dynamic Radial Foil Sheen Layer */
.card-specular-target::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    circle 140px at var(--pointer-x, 50%) var(--pointer-y, 50%),
    rgba(255, 229, 0, 0.14),
    transparent 70%
  );
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease;
}

.card-specular-target:hover::after,
.card-specular-target.is-active::after {
  opacity: 1;
}

/* Subtle 3D Micro-Tilt (Desktop Only: R <= 3 deg) */
@media (hover: hover) and (min-width: 1024px) {
  .card-specular-target:hover {
    transform: perspective(600px)
               rotateX(var(--tilt-x, 0deg))
               rotateY(var(--tilt-y, 0deg))
               translateY(-3px);
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.5), 0 0 16px rgba(255, 229, 0, 0.12);
  }
}
```

### Lightweight Vanilla JS Pointer Engine
```javascript
function attachSpecularSheen(elements) {
  elements.forEach(el => {
    el.addEventListener('pointermove', (e) => {
      const rect = el.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      el.style.setProperty('--pointer-x', `${x}px`);
      el.style.setProperty('--pointer-y', `${y}px`);

      // Micro-tilt calculation (max 2.5 - 3 degrees)
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const tiltX = ((y - centerY) / centerY) * -2.5;
      const tiltY = ((x - centerX) / centerX) * 2.5;
      el.style.setProperty('--tilt-x', `${tiltX.toFixed(2)}deg`);
      el.style.setProperty('--tilt-y', `${tiltY.toFixed(2)}deg`);
    });

    el.addEventListener('pointerleave', () => {
      el.style.setProperty('--tilt-x', '0deg');
      el.style.setProperty('--tilt-y', '0deg');
    });
  });
}
```

---

## 3. Synthesized Zero-Asset Web Audio Haptics

To deliver physical, tactile delight without downloading external MP3/WAV assets (0 KB network payload), synthesize micro-clicks directly using the native browser `AudioContext`.

### Acoustic Signature (Analog Ceramic Switch Click)
- **Waveform:** Pure sine wave (`oscillator.type = 'sine'`).
- **Pitch Ramp:** Swift downward ramp from 1400 Hz down to 320 Hz within 18 milliseconds.
- **Envelope:** Immediate attack (gain ~0.045), followed by rapid exponential decay (`exponentialRampToValueAtTime(0.0001, time + 0.018)`).
- **Physical Feel:** Resembles a high-end analog camera dial or luxury mechanical watch click.

### Complete Synthesizer Implementation with Agency Toggle
```javascript
class TactileHapticEngine {
  constructor() {
    this.ctx = null;
    this.enabled = localStorage.getItem('tactile_audio_enabled') !== 'false';
  }

  initContext() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) this.ctx = new AudioCtx();
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  playClick(freqStart = 1400, freqEnd = 320, duration = 0.018, volume = 0.045) {
    if (!this.enabled) return;
    try {
      this.initContext();
      if (!this.ctx) return;

      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sine';
      const now = this.ctx.currentTime;

      // Frequency drop for tactile click sensation
      osc.frequency.setValueAtTime(freqStart, now);
      osc.frequency.exponentialRampToValueAtTime(freqEnd, now + duration);

      // Gain envelope
      gain.gain.setValueAtTime(volume, now);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + duration);

      // Mobile hardware vibration pairing
      if (navigator.vibrate) {
        navigator.vibrate(6);
      }
    } catch (e) {
      // Graceful fallback on non-supported environments
    }
  }

  toggle() {
    this.enabled = !this.enabled;
    localStorage.setItem('tactile_audio_enabled', this.enabled ? 'true' : 'false');
    return this.enabled;
  }
}
```

---

## 4. Segmented Quick-Dial Scrubber

Instead of dumping dozens of unorganized SKU cards:
1. Provide a **segmented dial bar**: `[ Semua Nominal ] [ Populer 🔥 ] [ Hemat / Best Value ⚡ ] [ Top-Tier / Sultan 👑 ]`.
2. Anchor an animated sliding pill indicator underneath active tab.
3. Filter cards instantly with 120ms stagger fade-in transition.
4. Maintain `font-variant-numeric: tabular-nums` on all price and diamond counters to eliminate Cumulative Layout Shift (CLS < 0.005).
