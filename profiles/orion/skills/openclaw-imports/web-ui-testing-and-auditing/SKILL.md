---
name: web-ui-testing-and-auditing
description: Guidelines for visual auditing, deep-flow UI testing, and multi-step verification of web applications to ensure no broken sub-views or dynamic string formatting bugs remain after UI refactoring.
---

# Web UI Testing & Multi-Step Verification

Use this skill whenever verifying web interfaces, refactoring CSS/JS, or auditing web applications.

For GIS map dashboards, Leaflet/Mapbox telemetry visualizations, and GeoJSON sanitization patterns, see `references/gis-map-dashboard-patterns.md`.

## Mandatory Verification Rule

**NEVER declare a web UI complete or fixed based solely on `curl` or server status checks.** 
Always perform real visual inspection & manual browser testing:
1. Capture screenshots for both **Desktop** and **Mobile Viewports (e.g. 375px width)** using `browser_vision` or Playwright + `vision_analyze`.
2. Inspect for visual flaws: text clipping in input fields/placeholders, horizontal overflow/clutter in compact headers, misaligned stat columns, unstyled/raw buttons, and redundant cards.
3. Test interactions manually (clicking options, filling forms, verifying modal/drawer behavior) before making completion claims.
4. **Interactive Mutation & Behavioral Assertions**: Do NOT stop at passive screenshot snapshots. You MUST click every toggle, button, and control, asserting pre- and post-interaction DOM/CSS computed style mutations (e.g., verifying `getComputedStyle(el).backgroundColor` toggles when clicking theme switches, verifying Tailwind CSS v4 `@custom-variant dark` triggers properly, and verifying state changes produce immediate visible effect). Taking time for deep, 100% interactive coverage is always preferred over superficial snapshot speed.

## Key Principles

1. **Exhaustive Interactive Mutation Testing (Never Rely on Static Snapshots Alone)**:
   - Taking screenshots on initial load is insufficient. Every interactive control (Theme toggles, Currency selectors, Privacy blur masks, Filter tabs, Modals, Action buttons) MUST be clicked in Playwright/automation.
   - Assert pre- and post-click states using computed styles and DOM properties (e.g. asserting `getComputedStyle(element).backgroundColor` transitions between dark and light RGB values when clicking theme toggle).
   - Full functional coverage is prioritized over speed: take whatever time is needed to test all buttons and interaction pathways.
   - **Form Submission & Enter-Key Hijacking Prevention:** Verify that pressing `Enter` inside search, chat, or form input fields does not trigger default browser form navigation (`GET /?`) or unhandled page reloads, especially on WebSocket/SPA interfaces.
2. **Modern CSS Framework Pitfalls (e.g. Tailwind CSS v4)**:
   - In Tailwind CSS v4, class-based dark mode (`.dark`) is not enabled by default; it requires explicit declaration `@custom-variant dark (&:where(.dark, .dark *));` in the root CSS file.
   - Always verify that the rendered DOM and computed styles respond to class additions/removals rather than assuming framework legacy behavior.
3. **Anti-AI-Slop & Design Directives**:
   - Avoid generic AI SaaS aesthetics (blurry glassmorphism, muddy purple neon gradients, uniform rounded bubble cards, raw unstyled OS emojis).
   - In production client interfaces, prefer bespoke dual-tone SVG vector icons, curated token palettes (e.g. Cyber-Citrus, Midnight Titanium), and high-contrast WCAG AAA typography.
   - When requested (e.g. Minimalist Neo-Brutalism), apply bold high-contrast borders, solid offset drop shadows (`4px 4px 0px 0px #000`), tactile press displacements, and tabular monospace numbers.
   - **Velocity UX Shortcuts:** Provide direct 1-click shortcuts from popular hero/showcase items straight into the active denomination grid to remove repetitive multi-step friction.
   - **Shared State & DB Cache Isolation:** Ensure automated mock/regression tests do not overwrite production or shared database product cache tables (e.g. replacing a multi-thousand-product cache with a 1-item test dummy). Always isolate test databases or restore shared cache state post-run.
4. **Deep-Flow Verification**: Never limit UI verification to the landing page or initial state. Always click through multi-step wizards, sub-menus, search dialogs, support pages, form fields, and checkout flows.
2. **Dynamic Content Inspection**: Sub-screens generated dynamically via JS (e.g. `$('#stepBody').innerHTML = ...`) frequently contain concatenated text bugs, missing spacing (e.g. `DiamondHarga`), duplicated label texts, or missing card wrappers.
3. **Visual Snapshot Inspection**: Use `browser_vision` on EVERY major sub-view (brand selection, nominal grid, form inputs, help page) to visually confirm padding, alignment, borders, text readability, and color contrast.
4. **Header & Navigation Hygiene**: Check for duplicate buttons in header bars vs content areas, missing back buttons, or broken sticky layout behavior.
5. **Mobile Header & Chip Overflow Prevention**: Mobile viewports (< 768px / 375px) cannot fit wide balance pills, secondary links, or multiple action chips alongside the logo. Hide non-essential header chips (`display: none`) on mobile media queries to prevent horizontal overflow.
6. **Cache-Busting for Live Verification**: Cloudflare Tunnels and reverse proxies aggressively cache static assets. When testing live UI edits, append cache-busting version strings (e.g., `styles.css?v=mobilefix1` or `?v=nocache`) to ensure Playwright/browser captures fresh styles.
7. **Desktop Vertical Space & Footer Anchoring**: Dynamic SPA steps with short content can leave large blank voids at the bottom on desktop. Use Flexbox layout (`body { display: flex; flex-direction: column; min-height: 100vh; }`, `main { flex: 1 0 auto; }`, `.site-footer { margin-top: auto; }`) to anchor the footer cleanly.
8. **Desktop Section Spacing & Redundancy**: Avoid excessive vertical margins between hero, product rails, and wizard containers. Keep padding compact (`padding-y: 1.2rem - 1.5rem`), limit 3D hero canvas height on desktop (~280px), and avoid duplicating identical category cards back-to-back across multiple sections.
9. **GIS & GeoJSON Map Rendering Hygiene**: When visualizing GeoJSON sectors/polygons from external or crowdsourced API feeds on Leaflet/Mapbox, check for outlier/corrupt geometry coordinates (e.g. `dLon > 0.05` or `dLat > 0.05`) and double-encoded JSON string fields (`JSON.parse(JSON.parse(str))`). Sanitize or filter out giant bounding-box outliers before rendering to prevent giant screen-covering polygon artifacts that block the map view.
10. **Collapsible Floating Control Panels**: For GIS/map dashboards or dense data views, implement smooth collapsible sidebars (`transform: translateX(...)` with `opacity` transition) with a clear hide toggle button (`◀`) inside the header and a floating toggle button (`⚡ PANEL RADAR`) in the viewport when collapsed.

## Systematic Audit Checklist

- [ ] **100% Route & Endpoint Catalog**: Extract full list of pages, dynamic tabs, wizard steps, and modals before QA. No step may be left unvisited.
- [ ] **Home / Hero**: Search input, tag pills, CTA buttons, quick denomination jumps.
- [ ] **Wizard Step 1 (Categories)**: Grid alignment, card padding, icon rendering.
- [ ] **Wizard Step 2 (Brands)**: List/grid item spacing, search filter, back button.
- [ ] **Wizard Step 3 (Nominals)**: Currency formatting, price contrast, 2-column grid layout, pagination.
- [ ] **Wizard Step 4 (Input Forms)**: Input field spacing, label contrast, helper text duplication check, long-string overflow stress test.
- [ ] **Account & Modal Dialogs**: Form inputs, auth states, deposit/history tabs, vertical scroll containment, clean backdrop click close.
- [ ] **Support / Bantuan**: Verify contact links are rendered as distinct grid cards, not unformatted merged text blocks.
- [ ] **Header / Navigation**: Ensure no duplicate action buttons exist across topbar and view body.
- [ ] **Multi-Viewport Visual Matrix**: Capture and verify at Desktop (1920x1080, 1440x900), Tablet (768x1024), and Mobile (390x844, 360x800).
- [ ] **Exhaustive Control Mutation**: Exercise every button, tab, and toggle in default, hover, active, and error states. Verify compute styles and layout resilience.
