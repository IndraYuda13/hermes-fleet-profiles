---
name: troubleshooting-proxy-and-404-errors
description: Resolving false positive 404 HTTP errors masked by reverse proxies or mismatched API configurations, particularly when analyzing logs or direct API calls between inter-connected services like a backend and an internal Telegram bot.
---

# Troubleshooting Hidden 404 Errors and Proxy Conflicts

Use this skill when investigating persistent `404 API Not Found` or `Invalid API Key` errors between interconnected local services (like a backend server and a local proxy or bot engine) where the endpoint appears correct but fails to resolve or authenticate properly.

## Trigger Conditions
- A `curl` or internal service request yields `404 page not found` or `API Not Found`, but the application architecture suggests the request shouldn't route to the API at all (e.g., internal Telegram bot handling its own state vs sending an HTTP POST).
- A service behind a proxy or Docker container fails to reach a host network port (e.g., `http://localhost:20128` vs `http://172.17.0.1:20128`).
- Authentication fails repeatedly (e.g., `{"error":{"message":"Invalid API key"}}`), and the API key is retrieved via a CLI tool that truncates long output.

## Core Workflows and Lessons

### 1. Diagnosing Missing/404 Endpoints
When logs display 404 errors for an endpoint (e.g., `/api/agent/chat/stream`), do not assume the endpoint *must* be added to the backend. 
- **Verify Architecture:** Check if the system actually expects that endpoint to exist. Sometimes frontend logs leak into backend inspection, or a bot engine processes commands internally via Go-routines rather than HTTP POSTs.
- **Trace the Source:** Check `docker logs` and filter carefully. Ensure you aren't chasing a ghost endpoint that only the frontend UI attempts to call when the backend is offline.

### 2. Docker Network Isolation & Proxy Variables
If a Dockerized service attempts to hit a service running on the host OS (e.g., a local proxy on port 20128):
- **Avoid `localhost`:** In bridge networking, `localhost` points inside the container. Use the Docker host IP (typically `172.17.0.1` or `host.docker.internal`).
- **Check Proxy Env Vars:** Look for `HTTP_PROXY`, `HTTPS_PROXY`, and `ALL_PROXY`. If these are set, internal network requests might get hijacked and routed to an external proxy node.
- **Set `NO_PROXY`:** Explicitly set `NO_PROXY=localhost,127.0.0.1,172.17.0.1,172.19.0.1,::1` to prevent local traffic from being intercepted.
- **Cross-network Bridging:** If Container A (e.g., SearXNG) needs to hit proxies in Container B's network (e.g., Surfshark Proxy Studio), routing through the default `docker0` bridge (`172.17.0.1:31001`) may drop packets due to iptables/firewall rules blocking inter-container routing on the host gateway.
  - *Fix A:* Use the target container's specific network IP (e.g. `172.18.x.x` from `docker network inspect`).
  - *Fix B (Better):* Connect both containers to the same custom Docker network (`docker network connect <network> <container>`) and use Docker's internal DNS (`http://container-name:port`) instead of IP routing.

### 2b. SOCKS5 Proxy Handling in Python (aiohttp/httpx)
When routing asynchronous HTTP/WebSocket client connections through SOCKS5 proxies:
- **DNS Resolution Pitfall (`rdns`):** By default, asynchronous SOCKS5 connectors (like `aiohttp-socks`) attempt remote DNS resolution (`rdns=True`). If the local SOCKS proxy (such as a local dante relay or proxy container) does not support remote DNS resolving properly, requests will fail immediately with `python_socks._errors.ProxyError: Connection refused by destination host` or `Server disconnected`.
- **The Fix:** Explicitly set `rdns=False` when creating the proxy connector:
  ```python
  from aiohttp_socks import ProxyConnector
  connector = ProxyConnector.from_url('socks5://127.0.0.1:32001', rdns=False)
  # pass connector to your aiohttp.ClientSession
  ```

### 3. Avoiding Truncated Credential Reads
When retrieving API keys or long strings from a database (e.g., SQLite via terminal):
- SQLite CLI truncates long strings by default (e.g., `sk-68b...f8e3`). 
- **The Fix:** Extract the full key using Hex encoding to bypass UI truncation:
  ```bash
  sqlite3 data.sqlite "select hex(key) from apiKeys;"
  python3 -c "import binascii; print(binascii.unhexlify('HEX_STRING_HERE').decode('utf-8'))"
  ```

### 4. Cloudflared Tunnel WebSocket / 1006 Errors
When investigating `1006` WebSocket connection errors via Cloudflare Tunnels (often seen as `Chat connection interrupted` in web UIs):
- Check the `cloudflared` config (`/etc/cloudflared/config.yml`) for `originRequest: httpHostHeader: localhost`.
- **The Issue**: Forcing the `Host` header to `localhost` triggers Cross-Origin Resource Sharing (CORS) or origin mismatch rejections at the application WebSocket layer (which expects the public hostname).
- **The Fix**: Remove the `originRequest` and `httpHostHeader` blocks from the tunnel configuration entirely, so Cloudflare passes the real public hostname to the backend service. Restart the `cloudflared` service.

### 4. Cloudflared Tunnel WebSocket / 1006 Errors
When investigating `1006` WebSocket connection errors via Cloudflare Tunnels (often seen as `Chat connection interrupted` in web UIs):
- Check the `cloudflared` config (`/etc/cloudflared/config.yml`) for `originRequest: httpHostHeader: localhost`.
- **The Issue**: Forcing the `Host` header to `localhost` triggers Cross-Origin Resource Sharing (CORS) or origin mismatch rejections at the application WebSocket layer (which expects the public hostname).
- **The Fix**: Remove the `originRequest` and `httpHostHeader` blocks from the tunnel configuration entirely, so Cloudflare passes the real public hostname to the backend service. Restart both the backend service and `cloudflared`.

## Pitfalls
- **Assuming all 404s require code changes:** Before writing a new handler, verify if the endpoint is actually supposed to exist on that specific service (backend vs frontend).
- **Restarting blindly:** Restarting containers during active diagnosis can trigger unrelated UI errors that mask the original issue.
- **Trusting terminal output for secrets:** Never trust a terminal output that includes `...` in the middle of an API key or token. Always extract the raw, unformatted value.
- **WebSocket 1006 Errors and Cloudflared CORS:** When dealing with WebSocket disconnections (code 1006) through a Cloudflare Tunnel:
  - Do NOT set `originRequest: httpHostHeader: localhost`. This forces the Host header to `localhost`, which triggers CORS validation failures (403 Forbidden) on strict backends like FastAPI/Starlette when the browser originates from the real domain.
  - Fix by either removing the `httpHostHeader` override entirely (so the real domain is passed through), or explicitly configuring the backend (e.g. `hermes-dashboard`) to allow the origin using its built-in CORS configuration flags (e.g., in config.yaml).
- **Hermes Dashboard Binds:** Hermes dashboard specifically refuses to start (`Refusing to bind dashboard to 0.0.0.0`) or accept remote CORS origins if an authentication provider is not configured. It defaults to a strictly local `127.0.0.1` binding with `localhost` CORS. When using it behind Cloudflared, you must leave the tunnel's originRequest pointing to `localhost` AND use auth to expose it safely, or rely on SSH tunneling.
- **Hermes Dashboard WebSocket `origin_mismatch`:** When accessing the dashboard via a custom domain tunnel (e.g., Cloudflared), the PTY terminal websocket may fail with `origin_mismatch` in logs. This is DNS-rebinding protection. Fix this natively via `hermes config set dashboard.cors_origins "['https://yourdomain.com']"` or by setting `dashboard.host: 0.0.0.0` with `dashboard.auth: "password:YOUR_PW"`. Do NOT patch `hermes_cli/web_server.py`.
- **Missing Internal Tool Output on Telegram:** If the user complains that Hermes stopped showing its internal steps or tool executions (especially on the Telegram platform), this is usually because mobile-friendly defaults hide tool progress to reduce noise. To fix this and restore full visibility, run `hermes config set display.tool_progress all` and `hermes config set display.platforms.telegram.busy_ack_detail true`, then restart the `hermes-dashboard` service.