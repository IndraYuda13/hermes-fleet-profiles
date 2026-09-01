# Frontend Redesign: Audit-to-Live Promotion

Use this procedure when a frontend audit turns into an approved redesign, especially when a public preview reads files directly from the working directory.

## 1. Keep the phase boundary explicit

After an audit, say plainly whether files were changed. Do not let a design proposal sound like an implemented redesign.

- **Audit state:** findings, screenshots, and direction only. No source or live changes.
- **Implementation state:** code is changing in an isolated branch/worktree.
- **Promotion state:** merged source has passed tests and the public URL has been verified.

User approval of a direction is the gate to implementation, not evidence that the redesign already exists.

## 2. Protect the live preview before editing

1. Map the public host to its source directory, listener, reverse proxy/tunnel, and process owner.
2. If the project has no Git history, initialize Git and commit the untouched original as a checkpoint.
3. Use an isolated worktree for the redesign. This matters when an ad-hoc static server serves the main directory directly: editing main would otherwise change the live preview immediately.
4. Record the acceptance oracle before coding: target viewports, required flows, console state, accessibility behavior, and live/source equivalence.

Treat a static server parented by a shell, gateway, or temporary agent process as a deployment-reliability finding. It can be acceptable for a mockup, but it is not a managed production service.

## 3. Build regression seams before the rewrite

For a static HTML/CSS/JS mockup, useful low-cost checks include:

- JavaScript syntax with `node --check`.
- No undefined inline handlers. Prefer delegated `data-action` listeners over `onclick`/`oninput` strings.
- Semantic interactive cards use `button`, not clickable `div` elements.
- Native dialog semantics, focus placement, Escape closure, and focus return.
- Buyer-controlled values are escaped or assigned with `textContent`, never interpolated into an unsafe `innerHTML` sink.
- Pure state transitions reset all dependent descendants. Changing category resets brand/type/product/destination/payment; changing brand resets type/product/destination/payment; changing product resets destination/payment.
- Search supports token-wise matching. A query such as `DANA 50` should match a product even when the normalized phrase is not contiguous.
- Required destination data and payment choice block progression when invalid.
- Timer state lives outside render functions so a rerender does not reset countdowns or create duplicate intervals.

Export pure helpers behind a guarded module boundary when useful for Node tests:

```js
if (typeof module !== "undefined" && module.exports) module.exports = exported;
if (typeof document !== "undefined") init();
```

## 4. Verify visual and runtime behavior separately

### Responsive matrix

At minimum test `320`, `375`, `768`, `1024`, and `1440` widths. For each width record:

- `document.documentElement.scrollWidth > innerWidth`
- smallest visible button/link/input box
- hero and cashier fold positions
- sticky/fixed bars obscuring content
- wrapped shortcut/chip rows

Set the viewport **before navigation** for a fresh-load baseline. Also test a desktop-to-mobile resize transition when canvas or JS-set inline dimensions exist; stale inline width can produce overflow that a fresh mobile load does not reveal.

### Deep flow

Exercise every entry path:

- search and keyboard suggestions
- popular shortcuts
- category browsing
- back navigation and changing parent choices
- empty/invalid destination input
- payment selection, fee, total, confirmation, invoice, timer, and final status
- tracking dialog
- account/help dialogs and Escape behavior

Capture screenshots of the home view, mobile view, at least one form view, and payment/status view. A polished landing screenshot is not proof that dynamic subviews are styled.

## 5. Choose the lightest visual technology that serves the concept

Do not keep Three.js merely because the previous mockup used it. For one branded token or decorative object, layered CSS 3D may provide:

- immediate static fallback before JavaScript
- no WebGL context failure
- lower blocking JavaScript
- easier responsive scaling
- simpler reduced-motion behavior

Whether using CSS 3D, Canvas, or Three.js:

- make the object recognizable as the brand/product, not generic geometry
- pause motion with `IntersectionObserver` and Page Visibility
- respect `prefers-reduced-motion`
- limit pointer effects to fine pointers
- avoid restarting loops or timers on rerender

Self-host critical fonts when network timing or third-party dependency meaningfully hurts the preview. Use WOFF2 and `font-display: swap`.

## 6. Treat cache coherence as a release gate

A cache-buster on the **page URL** does not invalidate nested assets if the HTML still requests the old asset URL.

Correct sequence:

1. Change the asset URLs in HTML, preferably to content hashes or a new version token:

```html
<link rel="stylesheet" href="styles.css?v=<new-version>">
<script src="app.js?v=<new-version>" defer></script>
```

2. Merge the new HTML and assets.
3. Navigate to the public page with a fresh document query.
4. Inspect `document.styleSheets` and `document.scripts` to confirm the browser loaded the new nested asset URLs.
5. Hash local assets and the exact fetched live asset URLs. Require byte-for-byte equality.
6. Re-run the public responsive check and full flow. Do not infer rendered freshness from origin hashes alone.

This catches the common failure where origin files are current but Cloudflare or a reverse proxy still serves an older `styles.css?v=old-token` requested by cached HTML.

## 7. Promotion oracle

Promote only after all of these are fresh and green:

- branch/worktree tests and syntax checks
- independent review with findings resolved or explicitly accepted
- visual inspection at desktop and mobile
- no horizontal overflow at the viewport matrix
- no primary touch targets below 44×44 px
- keyboard cards, dialogs, reduced motion, and validation verified
- Lighthouse recorded as supporting evidence, not the sole verdict
- branch merged to main
- tests re-run from main
- public URL returns success
- public console has no new errors/warnings
- exact live/local asset hashes match
- public full transaction mock reaches the expected final state

After promotion, stop temporary preview servers and remove merged worktrees/feature branches. Keep verification notes and final public screenshots in durable artifact paths.