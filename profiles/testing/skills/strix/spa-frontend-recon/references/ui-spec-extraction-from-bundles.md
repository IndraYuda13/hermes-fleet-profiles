# UI-spec extraction: cloning a product's frontend 1:1 from its bundle

Depth notes for when the user says "make our UI look exactly like <site>", or the
target has sections/features their site lacks. The shipped bundle IS the
specification — every Tailwind class, section order, label string, and hover
behavior sits in the minified chunks. Extract from chunks, not screenshots: the
bundle still works when the live site is Cloudflare-walled, and it carries the
exact values and breakpoints a screenshot cannot.

## 1. Fetch the CURRENT bundle first — hashed chunk names rotate per deploy

- Get the entry bundle from the shell, then the chunk list from the ENTRY
  bundle: `grep -oE 'assets/<PageName>-[A-Za-z0-9_-]+\.js' entry.js | sort -u`.
- A chunk hash stored from an earlier session is dead or, worse, answers with
  the catch-all shell (a 200 whose body is the index HTML). Always re-derive the
  chunk list from today's entry bundle before downloading.
- Download per-component chunks for the page being cloned plus its shared
  pieces: the page file (WatchPage/HomePage/SearchPage), the card component
  (MediaCard), hero, and rail components — page layout lives in the page chunk,
  card geometry in the shared card chunk.

## 2. Extract the spec mechanically

- All classes: `re.finditer(r'className:(`[^`]+`|"[^"]+")', src)`, dedupe in
  order of appearance.
- Labels/section titles/button text: regex title-cased string literals
  (`"More Like This"`, `"Currently Airing Anime"`, `"Up Next"`) — this recovers
  the page's information architecture without reading the minified logic.
- **Landmark-context extraction** is the highest-yield move: `src.find('<known
  label>')` then print ±2–3 KB around it. The enclosing classNames around the
  landmark give that section's true layout (border-top, count badge, header
  row) without decoding the whole file. Do this per section, not once globally.
- Card details come from prop shapes: grep `poster:`, `year:`, `rating:`, and
  the width ladder (`w-[160px] sm:w-[190px] md:w-[210px]`) to recover sizing and
  breakpoints.

## 3. Port Tailwind to the clone's CSS with CONCRETE values

- Do NOT add Tailwind to a vanilla-CSS project. Convert each class explicitly:
  `bg-zinc-950` → `#09090b`, `border-white/[0.05]` → `rgba(255,255,255,.05)`,
  `rounded-2xl` → `16px`, `aspect-video` → `aspect-ratio:16/9`.
- The virtual-surface look comes from the 5–8% white opacity ladder on
  near-black; tokenize it (`--b05/--b06/--b08`) instead of scattering magic rgba.
- Put all clone CSS in ONE new file with a dedicated prefix (e.g. `fx-`), loaded
  after the legacy stylesheet. Grep the legacy CSS for the prefix first; 0 hits
  means the namespace is safe.
- Recreate the responsive ladder exactly (`h-[50vh] sm:h-[48vh] md:h-[46vh]` →
  three media queries). Verifying only on desktop hides the breakpoints the
  target actually uses.

## 4. Wire the clone without breaking the legacy shell

- New pages go in their own module with their own route branch; do not grow the
  legacy page file (keep the old page's unused functions until a grep proves
  nothing calls them).
- Per-route shell suppression: toggle a body class in the route dispatcher
  (`body.classList.toggle('v2-watch', route === 'player')`) and hide the legacy
  nav from CSS. Hiding it globally breaks routes that still rely on it.
- **When the user reports a feature "broken", first check WHICH backend the UI
  calls.** A legacy search modal pointed at an anime-only endpoint while the
  working multi-provider endpoint sat unused — the fix was repointing the
  trigger, not debugging the endpoint. Confirm the API works (curl) before
  touching UI code, then trace the UI's fetch target.
- Bump dynamic-import query strings (`./v2/watch.js?v=1`) when a deploy looks
  stale, and check for a service worker that might be caching.

## 5. Verify per-selector in a real browser

- Install error capture (`window.addEventListener('error'...)` +
  `unhandledrejection`) BEFORE a force-reload — then `Page.reload
  ignoreCache=True` between QA passes. A hash-only navigation does not re-render
  a JS SPA, so "page still shows old state" is usually no-reload, not a bug.
- Assert on specific selectors: hero title/badges/CTA count, rail count + card
  count, modal row count, pagination active page, filter result counts. An empty
  render means read the module error from the mount node first (`app-root`
  usually prints it) instead of re-clicking.
- Interaction checks that catch real regressions: click a rail arrow and read
  `scrollLeft > 0`; open the shortcut modal and count rows; switch a selector
  tab and count cells; confirm a bookmark click writes localStorage.
- Screenshot only as the FINAL proof artifact (desktop + one mobile viewport),
  never as the extraction source.
- **Player proof when the video element cannot render in the harness:** assert
  the state that only a working chain produces — `video.style.display ===
  'block'`, a `blob:` `video.currentSrc` (hls.js attached MSE), the server badge
  text, and the source-option `<select>` row count populated — then screenshot
  the full player chrome (progress bar, subtitle/server controls, breadcrumb).
  Probe on an interval (`poll every 5s up to ~60s`) because the resolve+probe
  chain is slow on cold cache; the title flipping from "Memuat…" to the real
  title IS the success signal.

## 6. Pitfalls that cost time

- **Rail/API payload shape varies** (`{results:[...]}` vs a bare array — both
  observed from the same API family): normalize before `.slice()`/`.map()` in
  one fetch-layer guard; `(items||[]).slice is not a function` in production is
  this bug.
- **Double vertical padding** when a new full-bleed page mounts inside a legacy
  shell that reserves nav height: measure `getComputedStyle(...).paddingTop` on
  both nodes and drop the extra wrapper class from the new page.
- **Legacy search/modal components keep competing entry points.** After
  building the replacement, repoint every trigger (nav pill, capsule button,
  keyboard shortcut) and re-check the label/placeholder text to match the new
  scope — a leftover "Cari anime..." placeholder mislabels a multi-provider
  search and reads as "still broken" to the user.
- **The user's complaint is the test plan.** "Search is incomplete, anime only,"
  or "home is uglier" maps to concrete acceptance checks (result types present,
  pagination works, rails exist X..Y) — convert each complaint into a selector
  assertion and run it before declaring done.
