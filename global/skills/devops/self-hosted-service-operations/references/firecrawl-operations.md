# Firecrawl Operations

## Self-Hosted Environment & Limitations

- **Resource Intensity:** Firecrawl self-hosted runs a full Node.js API, Bull queue manager, Playwright microservice (headless Chromium), PostgreSQL, Redis, and FoundationDB (experimental queue backend). It requires significant RAM (4GB+ minimum) to avoid OOM-kills during heavy Playwright scraping.
- **Limitation (Cloud vs Self-Hosted):** The self-hosted version lacks "Fire-engine" (advanced IP unblocking, DataDome/Cloudflare bypasses) available in the cloud version. It relies entirely on standard Playwright fetching and whatever proxy you configure.
- **UI:** The self-hosted version has NO web UI for scraping. It only exposes an API (`/v1/scrape`, `/v1/crawl`) and the Bull Queue manager (`/admin/CHANGEME/queues`).

## Configuration Pitfalls

### Database Authentication (USE_DB_AUTHENTICATION)
The default `docker-compose.yaml` and `.env.example` set `USE_DB_AUTHENTICATION=true`. However, the self-hosted stack currently **does not support Supabase/DB configuration**.
- **Symptom:** API requests log `[ERROR] - Attempted to access Supabase client when it's not configured` or `You're bypassing authentication`.
- **Fix:** Always set `USE_DB_AUTHENTICATION=false` in the `.env` file before starting the containers.

### Queue Backend (NUQ_BACKEND and FoundationDB)
Recent Firecrawl versions attempt to use FoundationDB as an experimental queue backend alongside or instead of Postgres. The `docker-compose.yaml` uses complex bash string interpolation (`${NUQ_BACKEND:+/var/fdb/fdb.cluster}`) and an entrypoint script for `foundationdb-init` that contains unescaped `$$` characters.
- **Symptom:** `docker compose up -d` fails with `Invalid interpolation format for "entrypoint" option in service "foundationdb-init"` or syntax errors when parsing `$`.
- **Fix:** The most robust fix is to strip out the failing interpolation using `sed`:
  `sed -i 's/${NUQ_BACKEND:+[^}]*}/""/g' docker-compose.yaml`
  If `docker-compose up -d` still fails repeatedly with interpolation errors, consider deploying only the core services: `docker-compose up -d --no-deps api worker playwright-service redis`.

### Proxy Configuration
Firecrawl uses standard HTTP proxies for its Playwright fetches.
- **Setup:** Add `PROXY_SERVER=ip:port`, `PROXY_USERNAME=user`, and `PROXY_PASSWORD=pass` to `.env`. Do NOT uncomment username/password if using IP auth.
- **Verification:** Test the proxy by running `curl -s -X POST http://localhost:3002/v1/scrape -H 'Content-Type: application/json' -d '{"url": "https://httpbin.org/ip"}'`. The resulting markdown should show the proxy's IP.

## Public Exposure (Cloudflared Tunnel)

Firecrawl API runs on port 3002 by default.
- To expose it via Cloudflare Tunnels, route traffic to `http://localhost:3002`.
- **Note:** When editing Cloudflared config YAML (`/etc/cloudflared/config.yml`), ensure proper indentation for `hostname` and `service` attributes and restart the service (`systemctl restart cloudflared`).