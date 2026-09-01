# Local Prediction Market Research & Paper Trading Laboratory Architecture

Reference guide for local Polymarket research, multi-agent forecasting, and paper trading simulations based on `/root/prediction-market-lab`.

## Deployment & Endpoint Architecture

- **API Server (FastAPI):** `http://127.0.0.1:8005` (Public: `https://prediction-lab-api.indrayuda.my.id`)
- **Dashboard (Vite/React 19):** `http://127.0.0.1:3000` (Public: `https://prediction-lab.indrayuda.my.id`)
- **Database (PostgreSQL 16):** Port `5432` (Docker Container: `prediction_market_lab_db`)
- **LLM Gateway (9Router):** `http://localhost:20128/v1` (Default model alias: `ag-opus-pool`)

## Key Architectural Boundaries & Troubleshooting Lessons

1. **Paper-Only & Read-Only Real Market Data:**
   - Real market discovery and data fetch via Polymarket Gamma API (`https://gamma-api.polymarket.com`) and CLOB API.
   - **Gamma API Schema Quirk:** Parse stringified JSON fields like `outcomes`, `clobTokenIds`, and `outcomePrices` when parsing Gamma response data into typed Pydantic models.
   - Paper execution is completely isolated using Polymarket Paper Trader MCP adapter or local paper account state (`PAPER_TRADING_ONLY=True`).
   - No private key, wallet signing, or live transaction execution allowed.

2. **Cloudflare Tunnel & Vite `allowedHosts`:**
   - When exposing Vite dev server via Cloudflare Tunnel (`prediction-lab.indrayuda.my.id`), Vite blocks untrusted Host headers by default (403 Forbidden).
   - **Fix:** Update `vite.config.ts` with `server: { allowedHosts: true }`.

3. **9Router Local LLM Gateway:**
   - Base URL: `http://localhost:20128/v1`
   - Default Model Alias: `ag-opus-pool` (treated as opaque alias).
   - Custom async LLM client handling JSON mode and health probes (`/health/llm`).

4. **Multi-Agent Debate & Forecasting Pipeline:**
   - 5 Key Roles: `BASE_RATE_ANALYST`, `SUPERFORECASTER`, `RED_TEAM_CRITIC`, `DOMAIN_EXPERT`, `SYNTHESIS_EDITOR`.
   - Pipeline Stages: `BLIND_ROUND` ➔ `EVIDENCE_EXCHANGE` ➔ `SPARSE_DEBATE` ➔ `RED_TEAM_CRITIQUE` ➔ `PRIVATE_REVISION` ➔ `SYNTHESIS`.
   - Abstained forecaster handling & Synthesis Report generation.

5. **Deterministic Risk Gate:**
   - Independent, rule-based Risk Gate outside of LLM authority.
   - Enforces rejection codes: `PAPER_ONLY_VIOLATION`, `MAX_POSITION_EXCEEDED`, `MIN_EDGE_NOT_MET`.

6. **Logit Pool Aggregation & Evaluation Metrics:**
   - Logit-space transformation: $L(p) = \ln(p / (1-p))$ and $p = 1 / (1 + e^{-L})$.
   - Outlier rejection via `trimmed_mean`.
   - Forecast accuracy evaluated via Brier Score: $(p - o)^2$ and clipped binary Log Loss.
