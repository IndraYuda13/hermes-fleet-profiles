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
See `references/rendered-defect-assertion-power.md` for pixel-geometry assertions on truncated/clipped text, counterfactual proof that a peer's new assertion is not tautological, and remount-window attribution.
See `templates/falsify-dom-assertion.spec.ts` for the copy-and-modify counterfactual probe harness.
See `references/independent-probe-harness-setup.md` for standing up an independent Playwright probe suite against a repo you must not modify, the seed/DOM-accessor boilerplate that keeps probes from failing on their own plumbing, and API-level idempotency/isolation probes.

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

### Truncated / clipped text at narrow viewports (grid track collapse)

Text present and readable in the DOM can still be visually cut off. Assert the **rendered glyph box**, not the element box: a collapsed grid track reports a zero-width cell while its `nowrap` text still overflows the row, so an element-box or visibility assertion passes on a broken layout.

```js
const m = await page.getByRole("link", { name: /<label>/ }).first().evaluate((el) => {
  const cell = el.querySelector("<trailing-cell-class>");
  const range = document.createRange();
  range.selectNodeContents(cell);            // glyphs, not the span box
  const text = range.getBoundingClientRect();
  const row = el.getBoundingClientRect();
  return {
    textWidth: text.width,
    overflowsRow: text.right > row.right + 0.5,
    gridTemplateColumns: getComputedStyle(el).gridTemplateColumns,
    cellWidth: cell.getBoundingClientRect().width,
  };
});
```

Fail when `textWidth === 0` or `text.right > row.right`. The cause is usually the template, not the text: a trailing cell handed only a positional `auto` track can be pushed to zero once the row's implicit children land on it. Fix `grid-template-columns` so the trailing cell keeps an explicit track (`minmax(0, 1fr) auto`). Always print `gridTemplateColumns` next to the geometry so the report names the mechanism instead of guessing, and note that the row's `overflow: hidden` silently swallows the clipped glyphs rather than producing a horizontal scrollbar.

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

## 10. Independent verification of a peer-driven UI fix

A peer reports "fixed X, specs pass, re-verify". You are the independent check; their self-run result is not evidence, and a verdict on the previous revision does not carry over.

1. **Preflight identity before running anything.** `git status --porcelain` empty; `git rev-parse HEAD` equal to the claimed SHA; the build identifier (for Next.js, `.next/BUILD_ID`) equal to the claimed build. A green suite on the wrong revision or a stale build is not a verdict. Re-check all three again after the runs.
2. **Bind a grep marker to the revision, not just to the product.** A feature string often exists in the parent commit too, so a bundle hit proves nothing about which revision was built. Choose a literal introduced by the diff (`git show <rev> -- <file>`) and confirm it is absent at `<rev>~1` before grepping the bundle. If no distinctive literal exists, report the build binding UNVERIFIED instead of implying proof.
3. **Rerun the peer's specs yourself on a staging port pair, then rerun your own affected probes with outputs written to a NEW revision-scoped directory.** Never reuse a prior revision's JSON/PNG as current evidence, and say explicitly that old evidence was discarded.
4. **Prove the peer's new assertion can fail.** An assertion added together with a fix is the easiest thing to make tautological. Run the counterfactual: neutralise the fix and show the assertion fails, restore it and show it passes (harness: `templates/falsify-dom-assertion.spec.ts`). State plainly when an assertion would also pass without the fix.
5. **Classify your own red results before calling them regressions.** Check whether your trigger violates a documented product rule the probe ignored, whether the element was still inside a render/remount window, and whether a locator caught hidden assistive text. A probe that trips a legitimate guard, or reads before hydration settled, is a probe defect, not a product defect. When you correct your own probe mid-session, the corrected run's numbers are the only ones you report; do not present the failed attempt's output as a result.

## 11. Fast re-verification loops on a moving revision

Each new revision invalidates the previous verdict, so make the loop cheap and repeatable rather than re-deriving it.

1. **Freeze what was already verified, then re-derive only the delta.** Preflight identity (section 10 step 1), then `git diff <previous-verified-rev>..HEAD --stat` and read the actual diff. If the touched files are styling or layout only, the functional claims are *expected* to be unchanged but still must be re-run: assert equality of the recorded values against the prior revision's JSON rather than re-reading them by eye. Report "unchanged, values identical" only after observing the same numbers.
2. **Keep a fixed probe corpus and re-run it by name.** Run only the affected probes with `-g "<test name>|<test name>"` so a targeted loop costs seconds, not a full sweep. Every probe already on disk is a regression net; when the delta touches a shared component, add one probe rather than re-running everything.
3. **Write each revision's outputs to its own directory** (`rev2/`, `rev3/`, or revision-named files) and scope artifact paths through an env var read by the probe at run time (`process.env["PNL_PROBE_ART"]`). Hardcoded output paths silently overwrite the previous revision's evidence, which destroys the very trail you built the corpus for.
4. **Prove a visual/layout fix by measuring the control container, not just the label.** For "X is no longer clipped" / "the controls fit", assert the full set: each child's box inside the viewport on both edges, each child not text-clipped (`scrollWidth <= clientWidth + 1` — a `nowrap` label clips without shortening the element), glyph width greater than zero, document `scrollWidth <= innerWidth`, and the intended responsive contract (mobile stacked vs `sm+` single row) as an explicit comparison between widths. A label-only check passes on a control that overflows its container.
5. **Re-state BLOCKERS and the residual limits on every loop.** Carry forward the limits that the delta does not touch (browser coverage, worker count) instead of dropping them, and name the revision your verdict binds to so superseded verdicts are visibly superseded.

