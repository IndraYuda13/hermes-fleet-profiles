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

### Adding/Modifying AI Models (e.g. 9router / Custom OpenAI Proxy)
When adding custom OpenAI-compatible endpoints or models (such as local 9router at `https://9router.indrayuda.my.id/v1`), inject entries directly into the `ai_models` table if UI selectors are locked or restricted.

```python
import base64, os, sqlite3
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from datetime import datetime

# Read DATA_ENCRYPTION_KEY from container env (docker exec nofx-trading env)
dek = "tauI2+67t/ZaoMSK4MGA43CnOvctrApfMTUS5LAsYEc="
key_bytes = base64.b64decode(dek)

def encrypt(plain_text):
    aesgcm = AESGCM(key_bytes)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plain_text.encode('utf-8'), None)
    return f"ENC:v1:{base64.b64encode(nonce).decode()}:{base64.b64encode(ciphertext).decode()}"

user_id = "9b57d526-0272-4131-a89e-17ab0055245d"
model_id = f"{user_id}_openai_9router"
name = "OpenAI (9router)"
provider = "openai"
enabled = 1
api_key = encrypt("sk-9router-local-key-2026")
custom_api_url = "https://9router.indrayuda.my.id/v1"
custom_model_name = "nofx"
now = datetime.utcnow().isoformat() + "Z"

conn = sqlite3.connect("/mnt/nofx/data/data.db")
cursor = conn.cursor()
cursor.execute("""
    INSERT OR REPLACE INTO ai_models 
    (id, user_id, name, provider, enabled, api_key, custom_api_url, custom_model_name, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (model_id, user_id, name, provider, enabled, api_key, custom_api_url, custom_model_name, now, now))
conn.commit()
conn.close()
```

After updating the database, restart the backend container to reload models:
```bash
docker restart nofx-trading
```

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
- **Direct Database Bypass**: If MetaMask EIP-712 flow fails, insert Hyperliquid exchange credentials directly into `exchanges` table in `/mnt/nofx/data/data.db` using `DATA_ENCRYPTION_KEY`:
  - `exchange_type`: `hyperliquid`
  - `hyperliquid_wallet_addr`: `<main_wallet_address>`
  - `api_key`: `ENC:v1:...` (encrypted Agent private key)
  - `hyperliquid_builder_approved`: `1`

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
