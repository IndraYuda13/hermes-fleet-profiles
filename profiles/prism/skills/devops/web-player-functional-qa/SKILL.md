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
See `references/motion-and-scroll-reveal-verification.md` for verifying scroll-reveal, mid-animation, reduced-motion, and idle-animation claims.
See `references/runtime-data-integrity.md` for immutable backend SQL gates and standalone IndexedDB upgrade probes.

## Bounded functional/data gate rules

- Choose the minimum probes that can falsify the requested invariants, plus relevant existing regressions; do not duplicate another verifier's full security or visual suite. Report concise results, exact commands/exits, critical repros, and explicit residual gates.
- Separate backend, storage, and integrated UI evidence. When the shared frontend is changing, execute backend probes from an immutable revision outside the shared checkout; do not certify the moving UI from those results. Carry evidence forward only after comparing the relevant file digests. Read the actual build identifier separately from Git HEAD: unchanged source does not establish the claimed build or running artifact. On a mismatch, retain verified source-bound results but leave build/runtime certification UNVERIFIED until the runtime owner reconciles identity.
- Exercise persisted SQL/RPC behavior when server algorithms own the result; TypeScript unit tests or parity of unrelated checkers cannot certify a different server generator.
- Bind each probe log to the exact probe bytes as well as product revision. If assertions are added after a successful run, rerun that probe or mark the additions UNVERIFIED; an earlier log does not cover the edited script.
- Verify summary truth, not only numerical correctness: distinguish absent evidence, unavailable loading, insufficient evidence, and existing-but-not-comparable results. A fallback that labels an excluded valid result as “no result” is a functional data-truth defect, not harmless cosmetic copy.
- Inspect creator test assertions and raw current-revision logs before deciding to rerun them. Reuse coverage that answers the criterion, but reject empty-state assertions that also accept an error screen as proof of genuine emptiness; keep independent UI and backend certification separate.

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

Never apply crude CSS syntax bans (such as banning `linear-gradient` or `backdrop-filter` in source code) during deterministic functional QA. Visual motifs are judged perceptually by the visual-QA plane's taste scoring; functional QA validates data integrity and semantic contracts.

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

## 8. Verifying Peer-Supplied Probes & Reported Failures

When you are asked to execute someone else's probe script, or to review its reported failures, you are the independent verifier. Do not accept its verdict, and do not "fix" the product to make the probe green.

1. **Read the script before running it.** Confirm it is read-only with respect to protected paths, that it writes only where it claims, and that it needs no network or server. Snapshot the artifacts it will overwrite plus the hash of any file it claims not to touch.
2. **Capture evidence verbatim, into your own scratch.** Redirect stdout and stderr separately, record the exit code separately, and re-hash the protected paths (working file, `git status`, HEAD) after the run. A probe's own summary line is not your evidence trail, and stale builds or truncated child output are incomplete evidence, not a soft pass.
3. **Classify every failed assertion before reporting it.** Never conflate the three classes:
   - **product defect** — the app really misbehaves;
   - **probe defect** — the assertion string, the targeting, or the timing is wrong so it can never pass;
   - **environment defect** — the harness/browser/setup differs from what the probe assumed.
   A peer report listing N failures is a claim about the app only if each failure survives classification.
4. **Reproduce each failure with your own probe**, in your own file, and try to *falsify* it: vary the reproduction path (instant jump vs incremental scroll vs keyboard vs smooth), vary the viewport, and test whether the failure is reachable through a real in-product action rather than only the probe's synthetic sequence. A defect reachable only by the probe's exact synthetic steps is usually a probe defect.
5. **Do not edit the probe or the artifact to make it pass.** Report the classification plus the corrected assertion/targeting, routed to the probe's owner.

**Computed-value assertions are the most common probe defect.** Browsers reserialize computed values, so literal-string comparison silently can never match:
- `transition-duration: 0.001ms` computes to `"1e-06s"`, not `"0.001s"`.
- `transform` rests as `"none"` on one element and `"matrix(1, 0, 0, 1, 0, 0)"` on another; `translate` as `"0px"` vs `"none"`.
Print the real computed value first, then assert on what the engine actually reports (or normalize/parse numerically) instead of hardcoding a human-readable literal.

**Shared evidence directories have concurrent writers.** Other agents may overwrite the same artifacts mid-run. Keep your captured output outside the shared dir and attribute every artifact to your run by mtime window; never present whatever is currently on disk as your run's evidence without checking its timestamp.

## 9. Fleet Parallel Verification (Functional + Perceptual QA)

When deterministic functional QA runs in parallel with a perceptual/visual QA agent:

- **Independent veto, never averaging:** `RELEASE_GATE = FUNC_PASS && VISUAL_PASS`. Never average scores across the two gates. Route defects to the release-gate dispatcher as a structured report; never issue direct directives between verifiers.
- **State-mutation isolation:** functional QA mutates state (forms, dialogs, storage writes); perceptual QA needs a quiescent DOM. Never share a browser context, incognito session, or storage partition — launch isolated contexts with dedicated ephemeral storage.
- **Anti-Goodhart gating:** a conditional rule (focus trap only if a modal is present, form validation only if forms exist) never passes by omission. Cross-reference mandated components against the journey contract; a required-but-missing element is `CONTRACT_VIOLATION_FAIL`, not a skipped check.
- **Selector discipline:** test against stable selectors (`data-testid` or accessibility roles) from the interaction contract, never brittle styling classes.
- **Accessibility division of labor:** automated DOM contrast engines false-positive on gradients, composites, and canvas — scope axe-core contrast to solid single-layer backgrounds and delegate layered perceptual contrast to rendered metrology. Structural/keyboard accessibility (ARIA roles, name computation, focus trapping, tab order) always stays with functional QA.
- Fleet role manifests, artifact schemas (verification report, coverage map, defect ledger, runbook), and the full handoff contract: `references/fleet-qa-handoff-contract.md`.

