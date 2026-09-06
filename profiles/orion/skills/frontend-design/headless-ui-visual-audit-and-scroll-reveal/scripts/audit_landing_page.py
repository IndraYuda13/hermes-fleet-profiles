# Headless CDP & Playwright Single-Page Audit Template

Reusable testing script for inspecting dark-mode landing pages with custom scroll-reveal animations, video backgrounds, and sticky navigation states.

```python
import asyncio
from playwright.async_api import async_playwright

async def audit_landing_page(url: str, output_prefix: str = "audit"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)
        page.on("pageerror", lambda err: console_errors.append(f"[pageerror] {err}"))

        await page.goto(url, wait_until="networkidle")
        await asyncio.sleep(0.5)

        # 1. Natural incremental scroll scrub to trigger all IntersectionObservers
        for y in range(0, 4000, 400):
            await page.evaluate(f"window.scrollTo(0, {y})")
            await asyncio.sleep(0.15)
        await asyncio.sleep(1.0)

        # 2. Capture Hero
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.5)
        await page.screenshot(path=f"{output_prefix}_hero.png")

        # 3. Capture Sections individually
        sections = ["#features", "#faq", "#contact"]
        for sec in sections:
            el = await page.query_selector(sec)
            if el:
                await el.scroll_into_view_if_needed()
                await asyncio.sleep(0.8)  # Wait for CSS transitions to finish
                clean_name = sec.replace("#", "")
                await page.screenshot(path=f"{output_prefix}_{clean_name}.png")

        await browser.close()
        return console_errors
```
