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

## 6. Mock Data & Text Leakage Scanning (Anti-Slop Hardening)

Never apply crude CSS syntax bans (such as banning `linear-gradient` or `backdrop-filter` in source code) during deterministic functional QA. Visual motifs are evaluated perceptually by LENS under taste scoring; PRISM validates data integrity and semantic contracts.

### Rendered DOM Leaf Node Scanning
Scan only visible leaf node `innerText` to prevent false positives on `<script>` tags, inline styles, or defensive JavaScript logic:
```javascript
const leakageFindings = await page.evaluate(() => {
  const issues = [];
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode(node) {
        const parent = node.parentElement;
        if (!parent) return NodeFilter.FILTER_REJECT;
        const tag = parent.tagName.toLowerCase();
        if (tag === 'script' || tag === 'style' || tag === 'noscript') {
          return NodeFilter.FILTER_REJECT;
        }
        return NodeFilter.FILTER_ACCEPT;
      }
    }
  );

  const tokenPatterns = [
    { pattern: /\blorem\s+ipsum\b/i, label: 'Lorem Ipsum placeholder' },
    { pattern: /\bundefined\b/, label: 'Leaked undefined token' },
    { pattern: /\bNaN\b/, label: 'Leaked NaN token' },
    { pattern: /\b\[object Object\]\b/, label: 'Unstringified object token' },
    { pattern: /\bTODO\b/, label: 'TODO marker in production copy' }
  ];

  while (walker.nextNode()) {
    const text = walker.currentNode.nodeValue || '';
    for (const { pattern, label } of tokenPatterns) {
      if (pattern.test(text)) {
        issues.push({ label, snippet: text.trim().slice(0, 80) });
      }
    }
  }
  return issues;
});
```

### Word Boundary & Defensive JS Protection Pitfall
Never use raw substring matches like `text.includes("undefined")` or `text.includes("NaN")`. This causes false positives on defensive code strings (`typeof x !== "undefined"`) or legitimate UI validation messages ("Value cannot be undefined"). Always enforce regex word boundaries `\bundefined\b` and `\bNaN\b` on rendered text nodes only.

## 7. Alpine.js Global Store Pitfalls
- Store objects (`Alpine.store(...)`) do not inherit component lifecycle methods such as `this.$nextTick`.
- Inside store methods, trigger DOM re-scans or icon updates with `setTimeout(() => { ... }, 50)` rather than calling `this.$nextTick()`.

## 8. Fleet Parallel Verification & Handoff Contract (Stage 9)
In multi-agent pipeline verifications where PRISM operates in parallel with LENS:

### Dual-Plane Separation of Responsibilities
- **PRISM (Deterministic Execution Plane)**: State machine transitions, form validation boundaries, route navigation contracts, ARIA/DOM tree accessibility mechanics (focus trapping, tabindex order), mock data leakage regex, and automated regression suites.
- **LENS (Perceptual Rendered Plane)**: Rendered visual quality, taste rubric, macro-diversity, layout metrology, rendered pixel contrast, perceptual anti-slop, and motion feel.

### Mandatory Inputs Required from FRAME
1. `BUILD_MANIFEST.json`: Exact `build_sha`, deterministic preview launch command, typecheck status, and lint status.
2. `INTERACTION_CONTRACT.json`: Stable test selectors (`data-testid` or accessibility roles) and state machine transition tables. Never run tests against brittle Tailwind utility classes.
3. `ROUTE_AND_FIXTURE_MANIFEST.json`: Explicit route map, 404 handling, and realistic fixture datasets (no empty placeholders).

### Outputs Produced for ORION Release Gate
1. `PRISM_VERIFICATION_REPORT.json`: Machine-readable results bound to exact `build_sha` covering all test domains.
2. `PRISM_COVERAGE_MAP.json`: Reconciliation proving 0 unexercised state transitions against `INTERACTION_CONTRACT.json`.
3. `REPRODUCIBILITY_RUNBOOK.md`: Single-line commands and environment seeds allowing identical test reproduction.
4. `DEFECT_LEDGER.json`: Structured defect entries with severity (`BLOCKER`, `HIGH`, `MEDIUM`), failing assertion, target selector, and stack trace (emitted on failure).

### Dual-Gate Independent Veto Invariant
- `RELEASE_GATE = PRISM_PASS && LENS_PASS`. Never calculate an average score across functional and visual gates.
- Defect routing goes to ORION as a structured report for unified dispatch to FRAME or AURORA, never direct conflicting directives between verifiers.

### Concurrency & State Mutation Isolation
- Functional QA is state-mutating (form submissions, error triggering, dialog toggles, local/sessionStorage writes); perceptual QA requires a quiescent DOM baseline.
- When running in parallel, PRISM and LENS must never share a browser context, incognito session, or mutable storage partition. Always launch independent browser instances or isolated contexts with dedicated ephemeral storage.

### Feature-Conditional Checks & Journey Gating (Anti-Goodhart Rule)
- For conditional rules (e.g. "focus trap only if modal/dialog present", "form validation only if forms present"), never pass by omission alone.
- PRISM must cross-reference required components against the journey specifications in `INTERACTION_CONTRACT.json`. If a journey mandates a modal, dialog, or form, but the DOM element is missing, emit `CONTRACT_VIOLATION_FAIL` rather than silently skipping the conditional check.

### Accessibility Division of Labor (Axe-Core vs LENS)
- Automated DOM contrast engines (axe-core) fail or flag false-positive `needs review` warnings on gradient, backdrop-filter, canvas, or semi-transparent composite layers.
- PRISM owns structural, keyboard, and programmatic accessibility: ARIA roles, accessible name computation, focus management/trapping, tabindex ordering, and input labeling.
- Perceptual color contrast over layered or composite backgrounds is formally delegated to LENS rendered metrology. Scope axe-core contrast checks strictly to solid, single-layer backgrounds to avoid deadlocks.

