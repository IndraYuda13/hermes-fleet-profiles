---
name: firecrawl-self-hosted
description: Use when setting up, fixing, or modifying a self-hosted Firecrawl instance.
---

# Firecrawl Self-Hosted Setup & Fixes

Firecrawl can be self-hosted locally and exposed via cloudflared tunnels.

## Setup Requirements & Modifications
- **YAML Compatibility:** The host environment uses modern docker-compose YAMLs that heavily feature interpolation (`${VAR:+value}`). The legacy `docker-compose` (v1) binary fails to parse these files correctly. Always use `docker compose` (v2 plugin) for deploying or manipulating services.
- **Database Authentication:** The `.env` template sets `USE_DB_AUTHENTICATION=true` by default which requires Supabase. When self-hosting without Supabase, `USE_DB_AUTHENTICATION` MUST be set to `false`.
- **Cloudflared Tunnel:** Expose local deployments via tunnels (see Cloudflared Tunnel conflict section).
- **LLM Extraction Failures with Custom Models**: If using a custom LLM provider (like 9router) for the `extract` feature via `OPENAI_BASE_URL`, Firecrawl expects a strict, non-streaming JSON block in the format of OpenAI's Tool Calling / Structured Output. Models that return SSE streams (even when not requested) or embed reasoning tokens (like some Gemini variants routed via 9router) will cause `UNKNOWN_ERROR` (502) and "Invalid JSON response" in the `extract-worker` logs. Use a strictly compliant model (e.g., `gpt-4o-mini`) if extraction fails.
- **Localhost API Connections from within Container**: When configuring `OPENAI_BASE_URL` in `/tmp/firecrawl/.env`, do not use `http://localhost:<port>` if the LLM provider is running on the host server. The container will try to connect to itself (ECONNREFUSED). Use the Docker Gateway IP (e.g., `http://172.17.0.1:<port>`) or a public domain URL routed back to the host (e.g. `https://9router.indrayuda.my.id/v1`).
- **Client-Side Rendering (SPA) limits:** Even with high `waitFor` delays (e.g. 10s), Firecrawl's JSON extraction can fail to capture deep DOM structures dynamically rendered by SPA frameworks (like Gradio apps, e.g., LMArena). If extraction returns incomplete metadata instead of the target data, fall back to native API inspection or manual browser automation.
- **Antibot Triggers:** Even simple extractions (`formats: ["markdown", "html"]`) using the Firecrawl API/MCP can trigger Cloudflare `document_antibot` blocks (e.g., on `arena.ai`). If the same API request passes in Postman but fails via MCP/CLI, it is due to an IP/Header/Cookie profile mismatch, and you may need to configure proxy rotation or Stealth settings.

## Proxy Integration
- Firecrawl supports authenticated proxy input via the `.env` format. Do not use HTTP URL prefixes. Set them explicitly:
  ```env
  PROXY_SERVER=ip:port
  PROXY_USERNAME=user
  PROXY_PASSWORD=pass
  ```
- Always restart the `api`, `playwright-service`, and (if present) `worker` containers to apply proxy changes (`docker compose restart api playwright-service`). Note: some deployments omit the `worker` service entirely.
- In Hermes Agent, when `FIRECRAWL_API_URL` is set to self-hosted Firecrawl, all `web_search` and `web_extract` calls route through this self-hosted instance and inherit its `.env` proxy configuration.

## Postman / API Usage
Self-hosted Firecrawl uses standard bearer token auth. If deploying without Supabase (`USE_DB_AUTHENTICATION=false`), the bearer token is simply the value set in the environment or passed openly. Use `Authorization: Bearer <key>`.
- **Scrape:** `POST /v1/scrape` (Synchronous, single URL).
- **Map:** `POST /v1/map` (Synchronous, find all links).
- **Crawl:** `POST /v1/crawl` (Asynchronous, returns Job ID).
- **Crawl Status:** `GET /v1/crawl/<job_id>`.

If the user needs a Postman collection, generate it locally (`Firecrawl_Local.postman_collection.json`) and share it via `MEDIA:/path` rather than relying on the Postman Cloud API (which often lacks valid CLI keys).

## Cloudflared Tunnel & cPanel 404 Routing Conflict
If you expose a Firecrawl instance via a Cloudflare Tunnel but receive a 404 Not Found response featuring a cPanel/WebMaster logo:
- **Root Cause:** The `firecrawl.yourdomain.com` DNS record already exists in the Cloudflare Dashboard as an A or CNAME record pointing directly to the cPanel hosting server IP. The Cloudflare Edge network prioritizes this standard record over the dynamically injected Cloudflared Tunnel DNS route, causing traffic to be routed to cPanel (which doesn't know about Firecrawl) instead of the local tunnel.
- **Resolution:**
  1. Do NOT assume restarting the `cloudflared` service will fix this.
  2. The user MUST manually log into the Cloudflare Web Dashboard.
  3. Navigate to DNS -> Records.
  4. Find the conflicting `firecrawl` A or CNAME record that points to the hosting IP.
  5. Delete the old record so the tunnel's CNAME can take over.