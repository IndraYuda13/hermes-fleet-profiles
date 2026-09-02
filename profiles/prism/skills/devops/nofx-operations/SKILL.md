---
name: nofx-operations
description: Use when operating or configuring AI models in NOFX.
---

# NOFX Operations & AI Model Configuration

Guide for operating, troubleshooting, and configuring AI models for the NOFX AI-powered trading platform (`ghcr.io/nofxaios/nofx`).

## Service Topology
- **Backend Container:** `nofx-trading` (Go, port 8080)
- **Frontend Container:** `nofx-frontend` (Nginx/React, port 3000)
- **Working / Data Directory:** `/mnt/nofx/data/`
- **Database:** `/mnt/nofx/data/data.db` (SQLite via GORM)

## AI Model & Provider Management

### API Key Encryption
NOFX encrypts `api_key` values in the `ai_models` SQLite table using AES-GCM format:
`ENC:v1:<base64_nonce>:<base64_ciphertext>`

The encryption key is passed via container environment variable `DATA_ENCRYPTION_KEY`.

### Adding/Modifying AI Models
Use the supported NOFX UI or API. Supply provider credentials through the
container secret environment and never paste `DATA_ENCRYPTION_KEY`, API keys,
wallet addresses, user IDs, or encrypted credential blobs into documentation.
If the UI/API cannot perform the change, stop and repair that control path
instead of writing credential rows directly in SQLite.

## Known Troubleshooting Pitfalls

### Demo / Paper Trading & Testnet Mode
NOFX does not have a built-in historical backtesting engine or standalone offline paper trading module.
To run demo / paper trading, use exchange Testnet environments natively supported in the `exchanges` database table:
```sql
-- Enable testnet for exchange (e.g. Binance Futures Testnet)
UPDATE exchanges SET testnet = 1 WHERE id = '<exchange_id>';
```

### Initial Balance Must Be Greater Than 0 Failure
If `trader_manager` logs `failed to load trader: failed to create trader: initial balance must be greater than 0`:
- **Cause**: NOFX queries exchange account balance on startup when `initial_balance` is unconfigured. If total balance returns 0 (e.g., empty Binance Futures wallet), trader initialization fails and NOFX endpoints (`/api/status`, `/api/positions`, `/api/account`, `/api/decisions/latest`) return 404.
- **Fix**: Deposit USDT into the exchange futures wallet or set `initial_balance` in the strategy/trader configuration or database.

### System-Wide HTTP/HTTPS Proxy Setup
To route NOFX outbound exchange traffic through a proxy (e.g. Surfshark proxy studio):
- Add `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY` in `/mnt/nofx/docker-compose.yml` under `nofx-trading` service:
  ```yaml
  environment:
    - HTTP_PROXY=http://user:pass@ip:port
    - HTTPS_PROXY=http://user:pass@ip:port
    - NO_PROXY=localhost,127.0.0.1,9router.indrayuda.my.id,127.0.0.1:20128
  ```
- Make sure to include local AI endpoints (`9router.indrayuda.my.id`, `127.0.0.1`) in `NO_PROXY` so local AI routing is not sent to the external proxy.

### Hyperliquid MetaMask 502 Bad Gateway ("Unable to recover signer")
When approving Hyperliquid trade-only access via MetaMask frontend modal (`/api/hyperliquid/submit-exchange`):
- **Cloudflare / HTTPS SSL Mismatch**: Ensure `TRANSPORT_ENCRYPTION=true` is set in `/mnt/nofx/.env` when behind Cloudflare HTTPS tunnel so EIP-712 domain & scheme are preserved.
- **Wrong Chain ID in MetaMask**: MetaMask must be connected to **Arbitrum One (Chain ID 42161 / 0xa4b1)**. If wallet is on Ethereum/BSC/Polygon, Hyperliquid node rejects EIP-712 signer recovery with `{"response":"Unable to recover signer.","status":"err"}` which NOFX surfaces as `502 Bad Gateway`.
- **Credential safety**: do not bypass the signed authorization flow or insert exchange credentials directly into SQLite. Repair TLS/chain configuration, then retry the supported flow.

### AI500 Coin Source Failure
If `use_ai500` is active and fails with legacy API error (`Failed to fetch AI500 list`):
```sql
UPDATE strategies SET config = json_set(config, '$.ai_config.coin_source.use_ai500', json('false'));
UPDATE strategies SET config = json_set(config, '$.ai_config.coin_source.source_type', 'static') WHERE json_extract(config, '$.ai_config.coin_source.source_type') = 'ai500';
UPDATE strategies SET config = json_set(config, '$.ai_config.coin_source.static_coins', json('["BTCUSDT","ETHUSDT"]'));
UPDATE traders SET use_coin_pool = 0 WHERE id = '<trader_id>';
```
Restart `nofx-trading` container afterwards.

### AI Model SSE Streaming Output Error ("invalid character 'd'")
If backend fails with `AI API call failed: fail to parse AI server response: failed to parse response: invalid character 'd' looking for beginning of value`:
- **Cause**: The custom AI endpoint/proxy (e.g., 9router or custom OpenAI endpoint) returned SSE streaming output (`data: {...}`) instead of non-streaming JSON (`{"id": ...}`).
- **Fix (9router Combo)**: Update 9router's database (`/root/.9router/db/data.sqlite`) so the combo (e.g. `nofx`) routes to a non-streaming model endpoint (like `cx/gpt-5.5`):
  ```sql
  UPDATE combos SET models = '["cx/gpt-5.5"]' WHERE name = 'nofx';
  ```
- Alternatively, switch `custom_model_name` in NOFX's `ai_models` table directly to a non-streaming model ID, then restart `nofx-trading` container.

### Vergex 502 Bad Gateway / Frontend "Server Error" Toast
If UI displays recurring `"Server Error: Please try again later or contact support"` toasts:
- **Cause**: Frontend auto-polls `/api/vergex/*` endpoints or kline endpoints. If `claw402` wallet lacks funds or payment retries are suppressed (HTTP 429/502), NOFX surfaces toast errors via Axios interceptor.
- **Impact**: Does not break auto-trading if strategy uses static coin lists (`source_type = 'static'`).
- **Fix (Frontend Patch)**: Suppress global error toast on HTTP status >= 500 in `nofx-frontend` container:
  ```bash
  docker exec nofx-frontend sed -i 's/throw n||be.error("Server Error",{id:"server-error",description:"Please try again later or contact support"}),new Error("Server error")/return Promise.reject(t)/g' /usr/share/nginx/html/assets/index--COHZSRx.js
  ```
