# AI Agent & Orchestration Services

Deployment depth for Vibe-Trading-class Python AI agents and n8n. The operating loop and gateway rules live in SKILL.md.

## Python AI agents (Vibe-Trading pattern)

- Put heavy-dependency virtualenvs (`scipy`, `duckdb`, `akshare`, `ccxt`) on `/mnt`, not `/`, to protect the root partition.
- Heavy pip installs exceed the default 60s terminal timeout — pass `timeout: 300`.
- Wiring a local OpenAI-compatible gateway via `.env`: `OPENAI_BASE_URL`, `OPENAI_API_KEY` (a real key — placeholder values like `***` get `401 Invalid API key`), `LANGCHAIN_PROVIDER=openai`, `LANGCHAIN_MODEL_NAME=<model>`. Missing provider/model env fails the startup preflight.
- Single-port web UI: PyPI packages may ship backend only. Build the repo frontend (`cd frontend && npm install && npm run build`) and copy `frontend/dist/*` into `<site-packages>/frontend/dist/` so `SPAStaticFiles` mounts at `/`.
- Behind a domain/tunnel: `API_ALLOWED_HOSTS=<domain>,localhost,127.0.0.1` prevents `403 Untrusted local API host`; non-loopback clients also require `API_AUTH_KEY=<key>` (enter once in the Web UI Settings — persists in browser `localStorage` — and it mints one-shot `/auth/sse-ticket` tokens for SSE).
- Telegram channel: install `python-telegram-bot>=21` in the venv; configure `~/.vibe-trading/agent.json` with `channels.telegram` (`token`, `mode: "polling"`, `allowlist: [<user_id>]`) and `channels.operators`; set `VIBE_TRADING_CHANNELS_AUTO_START=1` or `POST /channels/start` with the Bearer key.

## n8n

- Behind a reverse proxy/tunnel set `N8N_PROXY_HOPS=1` (or Express `trust proxy`) — otherwise rate-limiter crashes on `X-Forwarded-For` (`ValidationError`, `ERR_ERL_UNEXPECTED_X_FORWARDED_FOR`).
- Pin known-good versions instead of floating `latest`: a ToolsAgent V3 regression (`Cannot read properties of undefined (reading 'map')` in `executeBatch.ts`) shipped in v2.31.7; v1.82.0 is a stable fallback.
- Node engine: npm-installed n8n requires Node `>=18.17 <=22` — on Node 24 hosts use Docker or an nvm-pinned Node 20.
