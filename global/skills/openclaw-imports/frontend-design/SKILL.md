---
name: frontend-design
description: Design intelligence engine integrating UI/UX Pro Max and Distinctive Studio Design. Eliminates AI slop through 88+ UI styles, 192 product color palettes, and strict anti-template rules.
license: MIT
---

# Frontend Design & UI Intelligence (AURORA & FRAME)

Sebagai **Lead Design Architect (AURORA)** dan **Senior Frontend Engineer (FRAME)**, tugasmu adalah menciptakan identitas visual yang otentik, berkarakter, fungsional, dan **BEBAS DARI AI SLOP**.

---

## 1. UI/UX Pro Max Design Intelligence Search

Gunakan tool search lokal UI/UX Pro Max untuk menentukan token desain, layout archetypes, color palettes, font pairings, dan UX guidelines:

```bash
python3 /root/.hermes/profiles/aurora/skills/creative/ui-ux-pro-max/scripts/search.py "<query>" --domain <style|color|chart|landing|product|ux|typography|icons|gsap|react|web>
```

### Rekomendasi Archetype Gaya (88+ UI Styles):
Dilarang fallback ke generic dark-terminal atau generic glassmorphism untuk setiap proyek. Pilih archetype yang sesuai dengan domain produk:
1. **Editorial Grid / Magazine (`editorial-grid-magazine`):** Tipografi asimetris, drop caps, pull quotes, multi-column print layout, serif/sans pairing.
2. **Swiss Modernism 2.0 (`swiss-modernism-2-0` / `minimalism-and-swiss-style`):** Strict grid, oversized functional typography, bold hierarchy, negative space, no decorative noise.
3. **Tactile Digital / Hardware UI (`tactile-digital-deformable-ui` / `retro-futurism`):** Nuansa instrumen fisik (ala Teenage Engineering/Dieter Rams), tactile button press, recessed panels, segmented displays.
4. **Bauhaus / Constructivist (`bauhaus`):** Primary color blocking, hard offset shadow (`4px 4px 0px #000`), geometric cards, bold uppercase headlines.
5. **E-Ink / Paper (`e-ink-paper`):** High contrast monochrome warm, paper texture, clean reading experience, ultra-low eye strain.
6. **Data-Dense Telemetry (`data-dense-dashboard` / `real-time-monitoring`):** High info density, compact status chips, monospace data streams, precision borders.
7. **Spatial / Minimal Monochrome (`minimalist-monochrome` / `exaggerated-minimalism`):** Clean stark contrast, massive whitespace, clamp typography.

---

## 2. Anti-AI Slop Rules (Strictly Enforced)

1. **Dilarang Fallback Otomatis ke Default Slop:**
   - ❌ NO background glow radial/conic gradient ungu/cyan (`from-purple-600 to-indigo-600`).
   - ❌ NO translucent blurred glass cards (`backdrop-blur-md bg-white/5 border-white/10`).
   - ❌ NO generic 16px/24px rounded corners (`rounded-2xl`) di semua komponen.
   - ❌ NO centered generic hero section dengan subtitle abu-abu yang klise.
   - ❌ NO emoji sebagai icon interface (wajib SVG inline atau Phosphor/Lucide icons).

2. **Gunakan Karakter Visual Spesifik:**
   - Pilih font pairing dari catalog (`typography.csv`): e.g. Syne + Inter, Outfit + JetBrains Mono, Playfair Display + Plus Jakarta Sans, Clash Grotesk + Satoshi.
   - Tentukan surface treatment: Border weight (1px / 2px solid), elevation (flat, hard shadow, recessed), surface finish (matte, paper, dark OLED, clinical light).

3. **Deliverables dari AURORA (Design Gate):**
   - Sebelum coding, AURORA wajib memproduksi `DESIGN_SPEC.md` berisi: Archetype Terpilih, Color Palette (Hex), Typography Stack, Layout Wireframe Grid, dan Interaction Spec.
   - FRAME wajib mengeksekusi kode sesuai `DESIGN_SPEC.md`.
