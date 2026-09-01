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

## 5. Cloudflare Turnstile Bypass (Turnstile-Solver-NEW + Patchright)
When scraping/automating sites protected by Cloudflare Turnstile or Cloudflare Bot Management (e.g. `accounts.x.ai`):
- Use `Turnstile-Solver-NEW` (`https://github.com/D3-vin/Turnstile-Solver-NEW`) with `patchright`.
- Setup:
  ```bash
  git clone https://github.com/D3-vin/Turnstile-Solver-NEW /root/projects/Turnstile-Solver-NEW
  pip install patchright quart rich psutil
  patchright install
  echo "http://20.192.4.173:33101" > /root/projects/Turnstile-Solver-NEW/proxies.txt
  cd /root/projects/Turnstile-Solver-NEW && python3 api.py
  ```
- Always attach node-1 proxy (`http://20.192.4.173:33101`) to maintain clean IP reputation.
- For in-depth architecture evaluation, Camoufox/Gecko shadow-DOM click fixes, and browser pooling mitigations, see `references/turnstile-solver-architecture-and-mitigations.md`.