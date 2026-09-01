# Turnstile-Solver-NEW Architecture, Benchmarks & Operational Mitigations

## 1. Overview & Benchmark Baseline (Live Verified)
- **Engine Comparison:**
  - **Chromium (Patchright):** Managed 6.1s, Non-interactive 4.3s, Invisible 3.5s (PASS).
  - **Camoufox (Gecko):** Non-interactive 6.3s, Invisible 6.1s (PASS). Managed fails on direct widget click.
  - **System Chrome:** Managed 6.1s (PASS).
- **Core Mechanism:** Route-interception (`page.route` returning mock HTML embedding Turnstile widget under target origin). Cuts target page asset loading by ~80%.

## 2. Identified Architecture Bottlenecks & Pitfalls

### A. Cold-Start Browser Lifecycle (Performance Drag)
- **Problem:** Default `api.py` launches and closes a fresh browser process per request (`launch_browser` -> `close_browser`).
- **Impact:** Adds 1.5s–3.0s spawn latency per solve, spikes CPU/RAM on concurrent requests, risks zombie processes.
- **Mitigation:** Use a Persistent Browser Singleton and instantiate lightweight ephemeral `BrowserContext` per task (`await browser.new_context(**opts)`).

### B. Gecko / Camoufox Managed Widget Click Failure
- **Problem:** In `turnstile/solve.py`, `_human_click_iframe` uses fixed coordinates `(box['x'] + 30, box['y'] + height/2)` and fallback selectors (`input[type=checkbox]`, `label`, `body`).
- **Root Cause:**
  1. Gecko iframe bounding box coordinates often have offset/DPI translation lag.
  2. Cloudflare Turnstile modern widgets encapsulate the checkbox inside `#shadow-root (open)`. Standard Playwright selector chaining does not penetrate shadow roots cleanly in Gecko frames without explicit locators.
- **Mitigation:**
  - Wait for iframe layout stability before computing coordinates.
  - Use Playwright selector penetrating Shadow DOM: `page.frame_locator('iframe[src*="challenges.cloudflare.com"]').locator('div[id*="cf-stage"] label')` or evaluate click directly in shadow context.

### C. Fingerprint Inconsistency (Chrome 150 Hardcoding)
- **Problem:** `core/browser.py` sets hardcoded User-Agent `Chrome/150.0.0.0` and `sec-ch-ua` version `150`.
- **Impact:** Fraud score elevation on Cloudflare telemetry due to mismatched V8/Blink capabilities vs declared version 150.
- **Mitigation:** Inherit Patchright/Camoufox default native User-Agent or synchronize UA with true binary versions.

### D. Route Interception Subpath Wildcard Misses
- **Problem:** `route_glob` in `core/templates.py` only creates `/**` wildcard if `path in ('', '/')`. Subpaths like `/login?step=2` are passed verbatim.
- **Impact:** If target navigates internally, route match fails and loads full real page.
- **Mitigation:** Use origin-wide pattern: `f"{parts.scheme}://{parts.netloc}/**"`.

### E. Polling Latency vs Event-Driven Callbacks
- **Problem:** Token harvested via polling `input_value('[name=cf-turnstile-response]')` every 1s.
- **Mitigation:** Inject `data-callback="turnstileCallback"` in `build_route_html` and wait on window property `__turnstile_token` via `page.wait_for_function`.
