# Operator v2 Beta 2 Live Research & Readiness Runbook

## Overview & Scope
Operator v2 Beta 2 extends Operator v2 Beta 1 with Live Research, structured error codes, live-read diagnostics, read-only account onboarding, and refined audit event logging for paper policy approvals.

## Key Configurations & Defaults
- Default runtime parameters:
  - `PML_OPERATING_MODE=RESEARCH_MANUAL`
  - `PML_LIVE_EXECUTION_ENABLED=false`
  - `PML_LIVE_EXECUTION_DRY_RUN=true`
- Five Testing Environments:
  1. **Deterministic Fixture:** `PML_OPERATING_MODE=RESEARCH_AUTO`, `PML_DATA_MODE=fixture`, `PML_LLM_MODE=deterministic`
  2. **9Router Fixture:** `PML_OPERATING_MODE=RESEARCH_AUTO`, `PML_DATA_MODE=fixture`, `PML_LLM_MODE=9router` (`PML_LLM_GATEWAY_URL=http://127.0.0.1:20128/v1`)
  3. **Live Read:** `PML_OPERATING_MODE=RESEARCH_MANUAL`, `PML_DATA_MODE=live_read`, `PML_EVIDENCE_MODE=metadata`, `PML_LLM_MODE=9router`
  4. **Paper Auto:** `PML_OPERATING_MODE=PAPER_AUTO`, `PML_RUNTIME_MODE=PAPER_SIMULATION`, `PML_ENABLE_PAPER_MUTATIONS=true`
  5. **Gateway Dry-Run:** `PML_OPERATING_MODE=LIVE_CONFIRM`, `PML_LIVE_EXECUTION_ENABLED=true`, `PML_LIVE_EXECUTION_DRY_RUN=true`

## Structured Error Codes
When live reads or upstream calls fail, capture exact error codes rather than generic errors:
- `LIVE_DISCOVERY_DNS_FAILED`: DNS lookup to Polymarket/Gamma API failed.
- `LIVE_DISCOVERY_HTTP_FAILED`: HTTP error during market discovery.
- `LIVE_MARKET_NOT_FOUND`: Target market ID not found in upstream catalog.
- `LIVE_IDENTITY_INVALID`: Mismatch between requested `market_id`, returned `id`, or token outcome mapping.
- `LIVE_ORDERBOOK_UNAVAILABLE`: Orderbook API returned empty or inaccessible.
- `LIVE_ORDERBOOK_STALE`: Orderbook timestamp exceeds freshness threshold.
- `LIVE_UPSTREAM_SCHEMA_INVALID`: Unexpected payload structure from Gamma or CLOB API.

### Polymarket CLOB vs Gamma ID Matching Pitfall
Upstream Polymarket CLOB API (`https://clob.polymarket.com/book?token_id={token_id}`) returns `market` as the 0x-prefixed condition hash (e.g. `0xa467...`), whereas Gamma API uses string numeric market IDs (e.g. `559651`). Matching `response_market != market_id` in orderbook verification will fail unless checked against `condition_id` or `asset_id` token binding rather than raw string comparison against Gamma market ID.

## FastAPI Lifespan Migration Pattern
When updating or running with newer FastAPI versions, `@app.on_event("startup")` and `app.add_event_handler` raise `AttributeError` or deprecation warnings in test suites. Use `@contextlib.asynccontextmanager async def lifespan(app_instance: FastAPI):` inside `create_app()` and pass `lifespan=lifespan` to `FastAPI(...)`.

## Agent Tool Execution & Output Discipline
When executing background processes or long tool chains:
- Always produce non-empty assistant messages alongside or following tool executions to avoid empty response glitches on messaging platforms like Telegram.
- Clean up background launcher processes (`pkill -9 -f services.api.launcher`) between environment test runs to prevent port conflicts on 8000/8091.

## Paper Auto Event Clarification
Audit logs must explicitly distinguish paper execution stages:
1. `manual_approval`: Human operator explicitly signed off via API (`/api/v2/operator/runs/{run_id}/approve-paper`).
2. `automatic_paper_policy_approved`: Autopilot policy automatically passed deterministic risk rules without manual intervention.
3. `paper_filled`: Local paper simulation fill executed atomically.

## Read-Only Account Onboarding
- Verification of account readiness operates strictly read-only (`setup_polymarket_account.py`).
- Inspects: wallet address, wallet type (e.g. Proxy/Gnosis/EOA), geographic eligibility, USDC balance, positions, open orders, and user-stream WS connectivity.
- Never accepts, logs, or stores private keys, seed phrases, or signing materials.
