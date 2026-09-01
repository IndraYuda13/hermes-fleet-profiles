---
name: web-player-functional-qa
description: Verify web media players, storage state, and UI viewports.
version: 1.0.0
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [qa, testing, playwright, video-player, localstorage, responsive]
    category: devops
---

# Web Player & UI State Functional QA

Use this skill when designing or running automated functional QA suites for web applications featuring HTML5/HLS media players, client-side store persistence, search modals, and multi-device responsive viewports.

## 1. Playwright Headless Setup in Linux Containers
When executing Playwright scripts in server/container environments where the default Playwright cache browser may not be present:
- Target the system Chrome binary directly: `executable_path='/usr/bin/google-chrome'`
- Pass essential flags: `args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']`

```python
browser = await p.chromium.launch(
    executable_path='/usr/bin/google-chrome',
    headless=True,
    args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
)
```

## 2. LocalStorage Persistence & Rehydration Verification
To verify state persistence without false positives:
1. Mutate state via client-side store / UI interactions (e.g. `store.toggleWatchlist(id)`, `store.saveWatchProgress(...)`).
2. Directly assert the serialized payload in `localStorage.getItem(key)`.
3. Force a complete page reload: `await page.reload(wait_until="networkidle")`.
4. Assert that the reloaded store rehydrates and dynamically synchronizes derived UI elements (e.g. Continue Watching rows).

## 3. Video Player Controls & HUD Test Matrix
Always verify the full control and accessibility surface:
- **Playback**: Play/pause buttons, video element click, and keyboard shortcuts (`Space`, `KeyK`).
- **Seeking**: UI skip buttons (`+10s`/`-10s`), keyboard shortcuts (`KeyL`/`KeyJ`, `ArrowRight`/`ArrowLeft`), and scrubber click/drag tracking.
- **CSS Custom Properties**: Verify 60fps continuous scrubber updates via `document.documentElement.style.getPropertyValue('--played-percent')`.
- **Volume & Muting**: Slider synchronization, stepping via `ArrowUp`/`ArrowDown`, and mute toggle via button and `KeyM`.
- **Rate Switcher**: Verify cyclic speed switches (`[0.5x, 0.75x, 1.0x, 1.25x, 1.5x, 2.0x]`) and ensure numeric strings format properly (`1.0x` vs `1x`).
- **Canvas Ambient Bleed**: Verify toggle state controls canvas visibility and does not throw unhandled cross-origin canvas security errors.

## 4. Multi-Device Viewport Overflow Falsification
Check all target breakpoints (Desktop 1920x1080, Tablet 768x1024, Mobile 375x812) for horizontal layout blowout:
```javascript
document.documentElement.scrollWidth <= window.innerWidth + 1
```

## 5. Alpine.js Global Store Pitfalls
- Store objects (`Alpine.store(...)`) do not inherit component lifecycle methods such as `this.$nextTick`.
- Inside store methods, trigger DOM re-scans or icon updates with `setTimeout(() => { ... }, 50)` rather than calling `this.$nextTick()`.
