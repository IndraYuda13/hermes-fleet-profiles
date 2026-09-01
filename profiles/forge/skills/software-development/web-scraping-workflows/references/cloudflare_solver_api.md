# Cloudflare Clearance & Turnstile Solver API Architecture Reference

This reference documents the backend architecture, fast-path route interception technique, and bounding-box physical click strategies implemented in `turnstile-solver-api`.

## 1. Fast-Path Synthetic Route Interception & Safe Unroute Cleanup
Instead of waiting for heavy third-party assets, CSS, images, and trackers to load, route interception intercepts the document request at the target URL:
```python
route_glob = f"{parsed.scheme}://{parsed.netloc}{parsed.path}*"

async def route_handler(route):
    try:
        if route.request.resource_type == 'document':
            await route.fulfill(
                status=200,
                content_type="text/html; charset=utf-8",
                body=synthetic_html
            )
        else:
            await route.continue_()
    except Exception:
        try:
            await route.continue_()
        except Exception:
            pass

# IMPORTANT: Always wrap route lifecycle in try...finally so handlers never linger into realpage fallback
try:
    await page.route(route_glob, route_handler)
    await page.goto(url, wait_until='domcontentloaded', timeout=5000)
    token = await poll_token(page)
finally:
    try:
        await page.unroute(route_glob, route_handler)
    except Exception:
        pass
    try:
        await page.unroute(route_glob)
    except Exception:
        pass
```
- **Synthetic Stub:** Injects `<div class="cf-turnstile" data-sitekey="..." data-callback="onSuccess">` and pulls `https://challenges.cloudflare.com/turnstile/v0/api.js`.
- **Target Latency:** Solves in 2–3 seconds.
- **Fallback:** If synthetic execution fails or Cloudflare requires full domain context, automatically unroutes cleanly and falls back to full realpage navigation.

## 2. Bounding-Box Physical Mouse Click Strategy
Cloudflare Turnstile often nests its checkbox inside Shadow DOM boundaries or cross-origin iframes where DOM-level `.click()` or selector clicks are ignored or blocked.

**Solution:** Compute physical viewport coordinates and simulate hardware mouse events:
```python
locator = page.locator('iframe[src*="challenges.cloudflare.com"]').first
if await locator.count() > 0:
    box = await locator.bounding_box()
    if box:
        click_x = box['x'] + 30.0 + random.uniform(-3.0, 3.0)
        click_y = box['y'] + (box['height'] / 2.0) + random.uniform(-3.0, 3.0)
        await page.mouse.move(click_x, click_y, steps=5)
        await page.mouse.click(click_x, click_y)
```

## 3. Session Clearance Extraction for Interstitials (`/cf_clearance`)
For IUAM / Under Attack Mode / Managed Challenges:
1. Navigate to target URL.
2. Poll for `#challenge-stage`, `#challenge-form`, or iframe markers.
3. Apply physical click strategy if challenge is pending.
4. Extract `cf_clearance` cookie from `context.cookies()`.
5. Bundle all cookies, `User-Agent`, `sec-ch-ua`, and `Accept-Language` headers for downstream HTTP clients (e.g. `curl_cffi`, `requests`, `httpx`).

## 4. Headless Browser Subshell / Container Hardening
When running Chromium in isolated agent subshells, containers, or CI without a TTY:
- Always pass flags: `['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']`.
- Auto-discover `PLAYWRIGHT_BROWSERS_PATH` across standard cache locations (`/root/.cache/ms-playwright`, `~/.cache/ms-playwright`) if unset.
- Ensure route-blocking handlers (`_block_rendering`, `_unblock_rendering`) are idempotent and ignore errors when unrouting un-registered routes.
