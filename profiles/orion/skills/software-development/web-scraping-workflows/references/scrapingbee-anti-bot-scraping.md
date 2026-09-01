# ScrapingBee Anti-Bot & Live Marine Telemetry Scraping Patterns

When target websites strictly block direct scraping, iframe embedding (`X-Frame-Options: SAMEORIGIN`, HTTP 403), or employ complex anti-bot challenges (MarineTraffic, VesselFinder, Cloudflare WAF):
- Use ScrapingBee to run a remote headless Chrome instance with automated residential proxy rotation.

## 1. Key Parameters Reference
- `render_js=true` (Cost: 5 credits): Required for SPAs, interactive maps (Leaflet/Mapbox), or dynamic DOM tables.
- `premium_proxy=true`: Use when standard datacenter proxies trigger Cloudflare Turnstile or CAPTCHA challenges.
- `wait=3000` to `5000`: Wait for map tiles and websocket/AJAX telemetry to hydrate before extraction.
- `block_ads=true` & `block_resources=false`: Block ad networks while keeping tile images/scripts intact.

## 2. Python Scraping Template
```python
import requests

def scrape_hostile_target(target_url: str, api_key: str, wait_ms: int = 3000) -> str:
    params = {
        "api_key": api_key,
        "url": target_url,
        "render_js": "true",
        "premium_proxy": "false",
        "wait": str(wait_ms)
    }
    res = requests.get("https://app.scrapingbee.com/api/v1/", params=params, timeout=30)
    res.raise_for_status()
    return res.text
```

## 3. Dual-Engine Architecture Pattern
When integrating external live data without an official Enterprise API key:
1. Implement a local telemetry vector layer (e.g. Leaflet.js rendering localized port AIS markers).
2. Attach a deep-link bridge redirecting to the official search index (`https://www.marinetraffic.com/en/ais/index/search/all/keyword:...`) for global vessel track verification.
