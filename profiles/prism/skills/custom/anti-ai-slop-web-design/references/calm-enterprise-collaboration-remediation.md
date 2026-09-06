# Calm Enterprise Collaboration UI Remediation Patterns

## Background & Lessons Learned
When building enterprise web applications (e.g., chat, team workspaces, incident portals), avoid falling into **Cyberpunk / Tactical Telemetry Slop** (gratuitous monospace uppercase labels `// TACTICAL HUB`, neon telemetry chips, loud audio waveform colors, over-cardification, and fake dashboard aesthetics inside conversation feeds).

## Core Remediation Principles (Calm Enterprise Craft)
1. **Calm Foreground, Quiet Infrastructure**:
   - The primary user activity (e.g., chat message feed, reading stream) must occupy the focal center and flexible width.
   - Telemetry, latency pills, and system health must reside quietly in peripheral chrome (e.g., small status dot in sidebar footer) without competing with conversation content.
2. **Typographic Restraint**:
   - UI sans-serif (`Inter` / `Geist Sans`) for body (`400`), navigation, and headers (`500`).
   - Monospace (`JetBrains Mono`) strictly limited to timestamps, RTT latency numbers, code blocks, and technical IDs.
   - Restrain uppercase badge spam.
3. **Restful Surfaces & Borders**:
   - Dark mode: Obsidian base (`#0A0B0E`), elevated containers (`#101217`, `#161922`), and 1px crisp subtle borders (`rgba(255, 255, 255, 0.07)`).
   - Light mode: Clean neutral contrast (`#FFFFFF`, `#F8FAFC`, `#E2E8F0`) rather than inverted dark neon colors.
4. **Ergonomic Mobile Architecture (<768px)**:
   - Do NOT simply squeeze a 3-column desktop layout.
   - Navigation and right drawers become off-canvas slide drawers / bottom sheets with backdrops.
   - Touch targets must be >=44px, and composer inputs must respect `env(safe-area-inset-bottom)`.
5. **Interactive Polish**:
   - Audio waveform canvas must scale using `window.devicePixelRatio` for razor-sharp rendering on Retina/HiDPI displays.
   - Restrained indigo/slate color scheme for waveforms instead of high-saturation neon cyan.
