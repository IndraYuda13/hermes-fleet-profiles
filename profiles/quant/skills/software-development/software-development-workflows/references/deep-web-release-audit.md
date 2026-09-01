# Deep Web Release Audit

Use this playbook for an independent, read-only audit of a web mockup or frontend before release. It complements ordinary visual QA by proving whether the live behavior, source, security boundaries, and deployment match the UI claims.

## Evidence lanes

Run all lanes; do not infer one from another.

1. **Source and live equivalence**
   - Inventory the actual source files and deployment route.
   - Hash local files and fetched live assets to prove the reviewed source is what users receive.
   - Capture process ownership, bind address, reverse-proxy/tunnel route, service manager unit, restart policy, and health behavior.
   - A running URL is not deployment readiness: detect ad-hoc servers parented by shells, gateways, or temporary sessions.

2. **Visual and responsive baseline**
   - Inspect full-page desktop and mobile screenshots plus a narrow viewport such as 320 px.
   - Record element boxes, document width, horizontal overflow, fold positions, duplicated entry paths, touch sizes, hierarchy, trust cues, and conversion friction.
   - Treat a visual score or screenshot as evidence only for presentation, not function.

3. **Deep functional flow**
   - Exercise every major entry path, not just the canonical wizard: search, popular shortcuts, category browsing, account, support, tracking, legal links, checkout, and payment-specific completion.
   - Test empty, invalid, and cross-category state. Verify that displayed category, product, target, fee, total, payment method, and final instructions remain mutually consistent.
   - Explicitly verify that required fields cannot be skipped and that server-authoritative values are not represented as trusted client state.
   - Probe inline handler names at runtime; an element can look complete while calling an undefined function.

4. **Client security**
   - Trace user/API-controlled values to DOM sinks. For `innerHTML` or string templates, use a harmless execution marker in a controlled audit to prove or disprove DOM XSS; report the exact source-to-sink path.
   - Inspect CSP, HSTS, `nosniff`, referrer policy, permissions policy, frame protection, dependency pinning/SRI, and third-party scripts.
   - Distinguish a clearly labeled prototype from a public UI that presents fake balance, login, QR/payment, or trust claims as real.

5. **Accessibility beyond automation**
   - Automated scores are a floor, not a verdict. Inspect the actual accessibility tree and DOM.
   - Verify that clickable cards are semantic controls and keyboard reachable; labels are programmatically associated; progress and dynamic results are announced; dialogs expose role/name/modal state, trap focus, close on Escape, make the background inert, and return focus.
   - Measure touch targets and inspect focus styles. Test reduced-motion behavior rather than only checking the media query.

6. **Three.js and performance**
   - Compare mobile and desktop Lighthouse results. Large divergence often exposes GPU/main-thread work hidden by desktop hardware.
   - Attribute long tasks and total blocking time. Measure compressed and decoded dependency weight.
   - Check lazy loading, static fallback, DPR cap, render-on-demand, IntersectionObserver/Page Visibility pause, reduced motion, context-loss handling, and disposal of scenes/materials/geometries/listeners/timers.
   - Verify that entering a view repeatedly does not create multiple animation loops or intervals.

## Priority model

- **P0:** exploitable client security issue; transaction integrity failure; broken primary flow; fake or unsafe production behavior.
- **P1:** major conversion, accessibility, mobile performance, state consistency, or deployment-reliability defect.
- **P2:** visual refinement, brand distinctiveness, maintainability, SEO/content, and minor operational hardening.

Every high-priority finding should include: impact, live reproduction, source location, expected vs actual behavior, and a concrete repair direction. Separate facts proven by tools from hypotheses and remaining risks.

## Read-only verification

Before finishing:

- Re-run syntax or static checks without writing project files.
- Record source hashes and mtimes before/after where Git is unavailable.
- State whether live and local assets match.
- State which files were not changed and where temporary audit artifacts were written.
- Do not claim production readiness from Lighthouse, HTTP 200, or a visually successful happy path alone.
