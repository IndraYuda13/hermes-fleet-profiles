# Traffic Sniffing and Session Replay Workflow

## Pattern Overview
When reverse engineering login flows, capturing raw HTTP requests/responses, or inspecting CSRF tokens and Cloudflare Turnstile protected endpoints from headless Linux VPS environments:

### 1. Direct Playwright CDP Event Interception
Instead of configuring MITM proxies or system-wide certs, use Playwright request/response hooks:
```python
import asyncio, json
from playwright.async_api import async_playwright

async def sniff_traffic(url):
    logs = []
    async with async_playwright() as p:
        # Use existing system Chrome binary if ms-playwright browsers are missing
        browser = await p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = await browser.new_page()

        page.on("request", lambda req: logs.append({
            "type": "REQ", "method": req.method, "url": req.url, "headers": req.headers, "data": req.post_data
        }))
        page.on("response", lambda res: logs.append({
            "type": "RES", "status": res.status, "url": res.url, "headers": res.headers
        }))

        # Prefer domcontentloaded over networkidle to avoid timeouts on continuous polling / telemetry
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(3)

        cookies = await page.context.cookies()
        with open("cookies.json", "w") as f:
            json.dump(cookies, f, indent=2)
        await browser.close()
```

### 2. Dual Strategy: Browser vs Pure HTTP
- **Pure HTTP (`curl_cffi`):** Use Chrome TLS fingerprint (`impersonate="chrome124"`) to fetch HTML, parse CSRF hidden inputs (`soup.find('input', {'name': 'token'})`), and send form POST.
- **Browser Playwright:** When Turnstile/Cloudflare challenge requires JavaScript runtime execution, execute form submit in browser and serialize the resulting context cookies to JSON.
