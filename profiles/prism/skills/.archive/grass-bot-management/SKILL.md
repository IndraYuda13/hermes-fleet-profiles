---
name: grass-bot-management
description: Manage and run Grass Auto Farm Bot (grass_511) using local Surfshark proxy fleet.
category: devops
---

# Grass Bot Management

Use this skill when deploying, configuring, troubleshooting, or starting the Grass Auto Farm Bot (`grass_511` mod) on a VPS using the local Surfshark proxy fleet (node01 - node17).

## Trigger Conditions
- Running the `grass_511` python bot.
- Configuring accounts (`accounts.txt`), wallets (`wallets.txt`), proxy mappings (`proxies.txt`), or config parameters (`config.py`).
- Generating proxy configuration from local Surfshark nodes.

## Environment & Directories
- Active working directory on VPS: `/mnt/grass_511_bot/`
- Python virtualenv: `/mnt/grass_511_bot/venv/bin/python3`
- Config path: `/mnt/grass_511_bot/data/config.py`
- Proxy list path: `/mnt/grass_511_bot/data/proxies.txt`

## Proxy Setup (Surfshark Node Integration)
The bot leverages local SOCKS5 proxy endpoints managed by Surfshark Proxy Studio containers:
- SOCKS5 Proxy Format: `socks5://127.0.0.1:320XX` (where `XX` is node ID from `01` to `17`).
- HTTP Proxy Format: `http://127.0.0.1:310XX` (if HTTP proxying is required).

To generate the proxy list automatically, use the python script `/mnt/grass_511_bot/gen_proxies.py`.

## Execution Workflow

1. **Verify Dependencies & Config:**
   Make sure all python requirements are installed inside the venv and the captcha service config is defined (e.g. `DEBUG_LOGS = False` in `config.py`).

2. **Run Bot Menu:**
   ```bash
   cd /mnt/grass_511_bot
   ./venv/bin/python3 main.py
   ```
   Choose the desired mining mode (e.g., `1.25x` or `1x`) or utility mode (e.g., `Link Wallets` or `Check Airdrop`).

## Critical Pitfalls
- **`DEBUG_LOGS` Import Error:** Ensure `DEBUG_LOGS = False` is explicitly defined in `data/config.py` as it is imported by `core/utils/captcha.py` but sometimes missing in the upstream repository's default configuration.
- **Python-socks & aiohttp-socks dependencies:** SOCKS5 proxying in `aiohttp` (used for rest and websocket operations in the bot) requires both `python-socks[asyncio]` and `aiohttp-socks` libraries to be installed in the venv, otherwise SOCKS5 connections will fail with connection refused or socket errors.
- **SOCKS5 DNS Resolution Issue:** When routing SOCKS5 traffic using python/aiohttp libraries on the local network (such as Docker Surfshark proxy endpoints), set `rdns=False` inside the `ProxyConnector` (e.g. `ProxyConnector.from_url(proxy, rdns=False)`) to prevent remote DNS resolution failures (`Connection refused by destination host` or `ProxyError`) caused by local DNS configurations on Azure/internal cloud networks.
- **REST Check-in API Version Checks:** API Grass (`director.getgrass.io/checkin`) will reject older client versions with a `426 upgrade_required` HTTP response. If this occurs, patch or override the client version in the check-in request payload (located in `core/grass_sdk/extension.py`) to match a currently accepted version.
  * *Scanning Method:* To identify active valid versions (those that bypass the `426` blocker and instead return a `429` or successful response), perform testing across different proxy nodes (rotating ports `32001` - `32017`) rather than using the same node. Repeating version checks on a single node will cause Cloudflare to trigger a broad IP rate limit (`429 Limit exceeded`) which can falsely mask a valid version or block all subsequent scanning.
  * *Known Valid Versions:* As of July 2026, version **`4.26.2`** and **`4.29.1`** (and higher variations) are among those that bypass the `426` version constraint.
- **SOCKS5 Rest Bypass on HTTP API:** The Grass REST API calls (`retrieveUser`, etc.) may drop connections or fail when SOCKS5 proxies are used without proper encapsulation. Ensure SOCKS5 proxies are passed cleanly via the appropriate `ProxyConnector` setup rather than default HTTP proxy parameters on standard GET/POST client calls. In `core/grass_sdk/extension.py`, ensure individual requests (`session.post` or `session.ws_connect`) set `proxy=None` if a SOCKS5 `ProxyConnector` is already initialized on the parent `ClientSession` to avoid protocol collisions.
  Also note that some endpoints (such as `retrieveUser` or `checkin`) may enforce strict IP/proxy limits or geographical locks, causing some proxy nodes to return `426 upgrade_required` or `429 Limit exceeded` while others succeed. Testing multiple proxy ports (e.g. rotating between SOCKS5 ports `32001` - `32017`) is critical when debugging check-in validation.
- **Auth Database & Token Formats:** `data/auth_tokens.db` caches session tokens. Prioritize copying/preserving existing DB files to bypass captcha/login challenges when restarting the bot. Ensure the authorization tokens fetched or refreshed carry the `Bearer ` prefix (e.g., `Bearer <token>`) when sent in HTTP request headers.
- **Headless CLI Execution:** When executing the bot in a headless screen/tmux environment, patch the `MenuManager.show_menu` runtime CLI check to select the desired menu option automatically (e.g. option `1` for 1.25x farming) to prevent the program from blocking on input.
