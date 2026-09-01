---
name: web-scraping-workflows
description: Workarounds and lightweight patterns for extracting Markdown from URLs when native web_extract is unavailable or blocked.
---

# Web Scraping & Markdown Extraction Workflows

When the native `web_extract` tool fails (e.g., due to search-only backends like SearXNG) or when you need lightweight URL-to-Markdown conversion without heavy browser automation, use these lazy, efficient patterns.

## 1. The One-Line Fallback (Jina Reader)
The simplest and most effective way to extract clean, LLM-ready Markdown from any URL without an API key or complex setup.
```bash
curl -s https://r.jina.ai/https://target-url.com
```
- **Pros:** Fast, handles some dynamic content, zero setup.
- **Cons:** Free-tier rate limits apply for heavy bulk usage.

## 2. Python Content Extractor (Trafilatura)
Best for extracting clean article text and stripping out navigation, footers, and ads without running a headless browser.
```bash
# Requires pip install trafilatura
trafilatura -u "https://example.com"
```

## 3. Microsoft MarkItDown (Python)
Use this when the target URL might resolve to a document (PDF, Excel, Word, PPTX) rather than just HTML.
```bash
# Requires pip install markitdown
markitdown https://example.com
```

## 4. Heavy Local Scraper (Firecrawl Self-Hosted)
Do not reach for this unless explicitly requested or dealing with extremely hostile sites.
- Self-hosted Firecrawl is free (AGPL-3.0) but requires substantial infrastructure (Redis, Postgres, Playwright instances).
- Lacks the managed proxies and advanced Cloudflare bypass of their cloud version.
- **Docker Compose Interpolation Bug:** The official `docker-compose.yaml` uses bash-specific interpolation (`${NUQ_BACKEND:+/var/fdb/fdb.cluster}`) which breaks standard `docker compose up` and chokes on `$$`. Fix: `sed -i 's/${NUQ_BACKEND:+[^}]*}/""/g' docker-compose.yaml` before running.
- **Proxy Support:** Add `PROXY_SERVER=ip:port`, `PROXY_USERNAME=...`, and `PROXY_PASSWORD=...` to `.env` (no `http://` in `PROXY_SERVER`).
- **Auth Bypass Crash:** Set `USE_DB_AUTHENTICATION=false` in `.env` to avoid Supabase errors.
- **Decision:** Stick to `r.jina.ai` or `curl` for one-off tasks.

## 5. Cloudflare Turnstile & Interstitial Clearance Solver API
When scraping or automating sites protected by Cloudflare Turnstile or Cloudflare Interstitials (IUAM, Under Attack Mode, Managed Challenge, JS Challenge):
- Use `turnstile-solver-api` with Patchright/Camoufox on Quart.
- **Endpoints:**
  - `GET /turnstile?url=...&sitekey=...[&action=...&cdata=...&proxy=...]`: Solves Turnstile widgets using synthetic fast-path route interception (`build_route_html`, `route_glob`) in ~2-3s, with automatic fallback to full realpage solver.
  - `GET /cf_clearance?url=...[&proxy=...]`: Solves Cloudflare Interstitial challenges and extracts complete session bundle (`cf_clearance` cookie, full cookies list, user_agent, headers).
  - `GET /result?id=<taskId>`: Polls solve status (`processing`, `ready`, or error).
- **Core Architecture & Anti-Detection Strategies:**
  - **Zero Cold-Start Worker Pool:** Uses persistent browser instances in an `asyncio.Queue` pool with ephemeral contexts (`new_context()`), eliminating browser startup latency.
  - **Safe Route Handler Lifecycle:** Wraps fast-path route interception in `try...finally` unroute cleanup, preventing lingering handler contamination during realpage fallbacks.
  - **Bounding-Box Physical Mouse Clicks:** Calculates exact viewport coordinates `(box.x + 30, box.y + box.h/2)` and executes `page.mouse.click` with human-like jitter to penetrate Shadow DOM / cross-origin iframe security.
  - **Subshell/Container Launch Safety:** Passes `--no-sandbox`, `--disable-setuid-sandbox`, `--disable-dev-shm-usage`, and auto-discovers `PLAYWRIGHT_BROWSERS_PATH` for crash-free headless runs.
  - **SQLite WAL Mode Persistence:** Ensures concurrency safety and sub-millisecond writes for background solver tasks.
  - **Dynamic Client Hints:** Matches `User-Agent` and `Sec-CH-UA` headers from a curated pool.
- Detailed architecture reference: see `references/cloudflare_solver_api.md`.