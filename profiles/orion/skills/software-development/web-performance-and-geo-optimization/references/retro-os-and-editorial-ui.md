# Interactive Retro Desktop OS UI & Editorial Architecture

## 1. Interactive Retro OS Portfolio Architecture (e.g. harys.space / papiaw.id pattern)
When building interactive browser OS environments (retro desktop, window managers, floating window apps):

### A. Core Architecture Components
1. **Pre-boot / Audio Initialization Gate (`#preboot`)**:
   - Modern browsers block audio context and animations before first user interaction.
   - Use a pre-boot splash overlay ("▶ CLICK ANYWHERE TO START") to simultaneously initialize Web Audio/AudioContext and transition smoothly into the bootloader.
2. **Bootloader (`#boot`)**:
   - Simulated progress bar and terminal log before revealing the main desktop `#desktop`.
3. **Multi-Window Draggable & Resizable Management**:
   - Window structure: `.win` with `.win-bar` (header + controls: min/max/close) and `.win-body`.
   - Track `z-index` dynamically on `mousedown` to bring the active window to front.
   - Maintain window state (minimized, maximized, restored) mapped to taskbar items (`#tb-wins`) and dock icons.
4. **Theme Persistence**:
   - Apply stored theme in `<head>` immediately via `(function(){ const t = localStorage.getItem('theme') || 'dark'; document.documentElement.dataset.theme = t; })();` to prevent FOUC (Flash of Unstyled Content).
5. **Screensaver Daemon**:
   - Reset timer on `mousemove`, `keydown`, `touchstart`. After idle threshold (e.g., 2-3 mins), display retro matrix/terminal screensaver.

---

## 2. Fast Neo-Editorial Media Portal Pattern (e.g. altspace.id / ussfeed.com / afterhours.id)
When building high-speed editorial and digital magazine templates:

### A. Typography & Visual Language
- **Headings**: Geometric Neo-Grotesque / Display Sans (e.g., *Neue Montreal*, *Syne*, *Cabinet Grotesk*).
- **Body & Captions**: Clean high-legibility sans (e.g., *Plus Jakarta Sans*, *Inter*, *Instrument Sans*).
- **Color Accentuation**: Dark surface (`#0B0E14`, `#121824`) paired with Electric Cyan (`#00F0FF`), Neon Amber (`#FFB800`), and Violet (`#B026FF`).

### B. Essential Editorial Modules
1. **Top News Ticker (`.news-ticker-bar`)**: Real-time trending headlines strip.
2. **Asymmetric Hero Editorial Grid**: Large main card (7 cols) + 2 vertically stacked secondary stories (5 cols).
3. **Scorecard Rating Badges (`.review-score-pill`)**: Visual score indicators (e.g., `9.2/10`) for music/gear reviews.
4. **Client-Side Category Switcher**: Zero-reload dynamic filtering for snappy mobile UX.
5. **Reading Progress Bar**: Fixed top progress indicator synchronized with article scroll height.
6. **Deliverable Packaging**: Always provide both uncompressed working directory and downloadable `.zip` for easy deployment.
