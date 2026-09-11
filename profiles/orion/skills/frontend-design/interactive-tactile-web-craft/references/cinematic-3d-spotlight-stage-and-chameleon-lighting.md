# Cinematic 3D Spotlight Stage & Chameleon Dynamic Lighting Recipe

This reference captures the production-tested pattern for transforming flat, utilitarian product or digital store landing pages into immersive AAA gaming storefronts inspired by `sceneai.art`, Steam Deck, and Apple Card 3D showcases.

## 1. Problem & Context
When upgrading an e-commerce or digital topup catalog, simply restyling cards or adding micro-sheen is invisible to users ("Gak ada interaktif desain dll, ini masih sama aja kayak sebelumnya"). Users expect distinct visual drama, depth, and kinetic delight when interacting with featured products.

## 2. Architecture of the 3D Spotlight Stage

```
+---------------------------------------------------------------------------------+
| HERO GRID: [ Left: Hero Copy & Search ] | [ Right: 3D Holographic Parallax Card ] |
+---------------------------------------------------------------------------------+
| REEL: [ Horizontal Kinetic Game Cartridge Strip (MLBB, FF, Genshin, Val, PUBG)]  |
+---------------------------------------------------------------------------------+
```

### Layered 3D Card Parallax
The card consists of multiple distinct planes inside a 3D context:
- `perspective: 1000px` on parent container.
- `transform-style: preserve-3d` on the card frame.
- **Layer 0 (Canvas Backdrop):** Blurred ambient halo (`radial-gradient(circle, var(--ambient-glow), transparent 70%)`).
- **Layer 1 (Card Frame):** Brushed dark obsidian surface with a subtle 1px dynamic rim highlight.
- **Layer 2 (Cover Artwork):** High-resolution game or product illustration offset along the Z-axis (`transform: translateZ(30px)`).
- **Layer 3 (Floating Metadata & Badges):** High-contrast neon pills (`translateZ(50px)`), e.g., `⚡ INSTANT 8s`, `⭐ POPULER`.
- **Layer 4 (CTA Action Bar):** Full-width metallic gradient button with drop shadow.

### Pointer Lerp Physics
Instead of instant or jerky rotation, calculate pointer offset relative to card center and apply linear interpolation (lerp) within `requestAnimationFrame`:
```javascript
let currentRotateX = 0, currentRotateY = 0;
let targetRotateX = 0, targetRotateY = 0;

function updateCardPhysics() {
  currentRotateX += (targetRotateX - currentRotateX) * 0.12;
  currentRotateY += (targetRotateY - currentRotateY) * 0.12;
  card.style.transform = `perspective(1000px) rotateX(${currentRotateX}deg) rotateY(${currentRotateY}deg)`;
  requestAnimationFrame(updateCardPhysics);
}
```

## 3. Chameleon Dynamic Ambient Lighting
When switching active products/games via the cartridge reel:
- Update CSS root variables smoothly (`transition: background 400ms cubic-bezier(0.16, 1, 0.3, 1)`):
  - **Mobile Legends:** Emerald Gold (`--ambient-glow: rgba(16, 185, 129, 0.25)`, `--accent-glow: #10B981`)
  - **Free Fire:** Flame Orange (`--ambient-glow: rgba(249, 115, 22, 0.25)`, `--accent-glow: #F97316`)
  - **Genshin Impact:** Celestial Violet (`--ambient-glow: rgba(139, 92, 246, 0.25)`, `--accent-glow: #8B5CF6`)
  - **Valorant:** Radianite Cyan (`--ambient-glow: rgba(6, 182, 212, 0.25)`, `--accent-glow: #06B6D4`)
  - **PUBG Mobile:** Tactical Amber (`--ambient-glow: rgba(245, 158, 11, 0.25)`, `--accent-glow: #F59E0B`)

## 4. Mobile & Responsive Discipline
- On viewports < 768px:
  - Stack the 3D spotlight card below the hero search bar or headline.
  - Disable aggressive gyroscope tilt if it interferes with scroll ergonomics; keep touch-follow and tap-switch snappy.
  - Constrain all widths with `min(100%, ...)` to ensure **0px horizontal overflow**.
