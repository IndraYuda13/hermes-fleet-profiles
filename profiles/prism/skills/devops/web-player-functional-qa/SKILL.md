---
name: web-player-functional-qa
description: "Headless functional QA for web UIs -- Puppeteer/Playwright scripts, viewports, ARIA, anti-slop."
version: 1.0.0
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [qa, testing, playwright, puppeteer, headless, responsive, aria, anti-slop]
    category: devops
---

# Headless Functional QA for Web UIs

Use this skill when designing or running automated functional QA suites for web applications -- static prototypes, SPAs, media players, dashboards. Covers Puppeteer and Playwright headless scripting, responsive viewport verification, ARIA role checks, anti-AI-slop scanning, and state transition testing.

See `references/puppeteer-ui-qa-patterns.md` for Puppeteer-specific patterns including IIFE closure workarounds, transient state capture, overlay click-through fixes, and anti-slop scanning.
See `references/functional-qa-manifest-structure.md` for the standard PRISM QA manifest format (10-category test matrix, JSON schema, file layout).

## 1. Headless Browser Setup in Linux Containers

### Playwright (Python)
```python
browser = await p.chromium.launch(
    executable_path='/usr/bin/google-chrome',
    headless=True,
    args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
)
```

### Puppeteer (Node.js)
```javascript
const browser = await puppeteer.launch({
  headless: 'new',
  executablePath: '/usr/bin/google-chrome',
  args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu',
         '--disable-web-security', '--allow-file-access-from-files']
});
```
**Puppeteer install:** `npm install --save-dev puppeteer` -- uses system Chrome, no download needed if `executablePath` is set.
**File URLs:** Add `--disable-web-security --allow-file-access-from-files` for `file://` protocol testing of static prototypes.

### Puppeteer v25+ Breaking Change
`page.waitForTimeout()` was **removed** in Puppeteer v25. Use a standalone delay helper:
```javascript
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
// Then: await delay(300); instead of await page.waitForTimeout(300);
```

### Click-Through-Overlay Pitfall
When a dropdown, modal, or overlay covers an element, `page.click('#target')` throws `"Node is either not clickable or not an Element"`. Solutions:
1. **Close overlays first:** `await page.keyboard.press('Escape'); await delay(200);`
2. **Use JS click (bypasses hit-testing):** `await page.evaluate(() => document.getElementById('target').click());`
Prefer (1) when testing real user flow; use (2) for test setup/teardown steps.

### Local HTTP Server (preferred over file:// URLs)
Serving app files via a local HTTP server avoids CORS issues, favicon 404 noise, and security flag requirements:
```javascript
const http = require('http');
const server = http.createServer((req, res) => {
  let filePath = path.join(APP_DIR, req.url === '/' ? 'index.html' : req.url);
  fs.readFile(filePath, (err, data) => {
    if (err) { res.writeHead(404); res.end('Not Found'); return; }
    res.writeHead(200, { 'Content-Type': mimeType });
    res.end(data);
  });
});
server.listen(0, '127.0.0.1'); // port 0 = OS picks a free port
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

## 4. Multi-Device Viewport & Responsive Layout Verification

### Overflow Falsification
```javascript
document.documentElement.scrollWidth <= window.innerWidth + 1
```

### Breakpoint Test Loop
Iterate over target viewports and verify layout properties at each:
```javascript
const viewports = [
  { width: 320, height: 568, label: 'Mobile S' },
  { width: 390, height: 844, label: 'Mobile' },
  { width: 768, height: 1024, label: 'Tablet' },
  { width: 1440, height: 900, label: 'Desktop' },
  { width: 1920, height: 1080, label: 'Desktop XL' }
];
for (const vp of viewports) {
  await page.setViewport(vp);
  await page.goto(url, { waitUntil: 'domcontentloaded' });
  // Verify flex-direction, element visibility, width ratios
}
```

### Key Checks Per Breakpoint
- **Mobile (<768px):** Verify collapsed nav, hidden desktop elements, mobile filter bars, stacked layout
- **Tablet (768-1023px):** Verify stacked column layout, `flex-direction: column`, max-height constraints
- **Desktop (1024+):** Verify side-by-side split, correct width ratios (CSS % vs max-width conflicts)

**Pitfall:** `max-width` on panes can silently override percentage-based widths at large viewports. Always measure actual pixel widths and compute ratios, don't trust CSS variable values alone.

## 5. ARIA & Accessibility Role Verification
Programmatically verify ARIA roles rather than visual inspection:
```javascript
// Listbox pattern (incident lists, service lists)
await page.$('[role="listbox"]');  // container
await page.$$('[role="option"]');   // items with aria-selected

// Tab pattern
await page.$('[role="tablist"]');
await page.$$('[role="tab"]');      // check aria-selected

// Modal/dialog
await page.$('[role="dialog"][aria-modal="true"]');

// Focus ring CSS
const hasFocusVisible = await page.evaluate(() => {
  for (const sheet of document.styleSheets) {
    for (const rule of sheet.cssRules) {
      if (rule.selectorText?.includes(':focus-visible')) return true;
    }
  }
  return false;
});
```

## 6. Anti-AI-Slop Computed Style Scanning
Scan all DOM elements for design anti-patterns:
```javascript
const antiSlopChecks = await page.evaluate(() => {
  const results = { gradient: false, boxShadow: false, blur: false };
  for (const el of document.querySelectorAll('*')) {
    const s = getComputedStyle(el);
    if (s.backgroundImage?.includes('gradient')) results.gradient = true;
    if (s.boxShadow !== 'none') results.boxShadow = true;
    if (s.backdropFilter !== 'none' || s.filter?.includes('blur')) results.blur = true;
  }
  return results;
});
```
Also scan for placeholder text leakage:
```javascript
const text = await page.evaluate(() => document.body.innerText);
const hasSlop = /lorem|ipsum|placeholder|TODO|undefined/i.test(text);
```

## 7. Alpine.js Global Store Pitfalls
- Store objects (`Alpine.store(...)`) do not inherit component lifecycle methods such as `this.$nextTick`.
- Inside store methods, trigger DOM re-scans or icon updates with `setTimeout(() => { ... }, 50)` rather than calling `this.$nextTick()`.
