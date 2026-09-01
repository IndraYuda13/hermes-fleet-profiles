---
name: octobot-operations
description: Use when installing, operating, or troubleshooting OctoBot.
version: 1.0.0
---

# OctoBot Operations & Troubleshooting

## Key Architecture & Configuration

### Directory Structure & Persistence
Standard persistent directories for Docker Compose under `/opt/octobot`:
- `/opt/octobot/user` -> `/octobot/user` (contains `config.json` and `profiles/`)
- `/opt/octobot/tentacles` -> `/octobot/tentacles`
- `/opt/octobot/logs` -> `/octobot/logs`
- `/opt/octobot/backtesting` -> `/octobot/backtesting`

### Key Configuration Pitfalls & Schema Requirements
When customizing a profile under `/opt/octobot/user/profiles/<profile_id>/specific_config/`:

1. **`DailyTradingMode.json` required fields:**
   Must contain `required_strategies`:
   ```json
   {
       "time_frame": "1h",
       "required_strategies": ["SimpleStrategyEvaluator"]
   }
   ```
   *Missing `required_strategies` causes a fatal exception on startup or profile page load.*

2. **`SimpleStrategyEvaluator.json` required fields:**
   Must contain `required_evaluators` and `required_time_frames`:
   ```json
   {
       "evaluator_depth": "1h",
       "required_time_frames": ["1h"],
       "required_evaluators": ["GPTEvaluator"]
   }
   ```
   *Missing `required_evaluators` causes an unhandled HTTP 500 error when opening `/profile` in Web UI.*

3. **`tentacles_config.json` Service & Interface Activation:**
   Ensure `Services` section has `GPT: true`, `WebService: true`, and `WebInterface: true` enabled.

4. **OpenAI / Custom LLM (9Router) Service Config in `user/config.json`:**
   Note that the service section key is case-sensitive (`GPT`):
   ```json
   {
       "services": {
           "GPT": {
               "api-key": "sk-local-key",
               "llm-custom-base-url": "http://host.docker.internal:20128/v1",
               "model": "ag/gemini-3.6-flash-high"
           }
       }
   }
   ```

5. **Terms & Disclaimer Auto-Acceptance:**
   Set `"accepted_terms": true` in `/opt/octobot/user/config.json` to prevent the Web UI from constantly redirecting to `/terms`.

6. **Backtesting File Mismatch ("Missing time frame in data file"):**
   - **Symptom:** Clicking "Start Backtesting" in Web UI throws `Impossible to start backtesting on this configuration: Missing time frame in data file: 1h`.
   - **Cause:** Pre-existing historical data files in `/opt/octobot/backtesting/data/` (e.g. sample `DOGE/IDR` with 3m/5m/15m/30m timeframes) do not contain the active profile's timeframe (e.g. `1h`).
   - **Fix:** Clear old/mismatched data files from `/opt/octobot/backtesting/data/` or download matching symbol and timeframe data using the Web UI Data Collector before starting a backtest run.

7. **AI / GPTEvaluator Backtesting Limitations:**
   - **Symptom:** Logs show `GPTEvaluator is disabled in backtesting` and `No ChatGPT signal history for <symbol> on <tf>`.
   - **Cause:** Self-hosted OctoBot disables LLM/GPTEvaluator during backtesting (emitting neutral evaluations) and expects OctoBot Cloud historical signal DB.
   - **Fix:** Evaluate AI/GPT profiles using **Paper Trading (Live Simulation)** instead of backtesting.

8. **Verifying Active Paper Trading Status & Binance Testnet Limitations:**
   - **No Binance Testnet API:** OctoBot does not connect to Binance Spot/Futures Testnet endpoints (no `sandboxMode` support for Binance). Demo/risk-free trading relies entirely on OctoBot's internal `trader-simulator` (Paper Trading) driven by real-time Binance Mainnet market data.
   - Check container logs: `Starting OctoBot with simulated trader on ...`
   - Check `/octobot/user/config.json` for active profile `"profile": "<profile_id>"`.
   - Check `/octobot/user/profiles/<profile_id>/profile.json`:
     - `"trader-simulator": { "enabled": true }` (Paper Trading ON)
     - `"trader": { "enabled": false }` (Real Money Trading OFF)

9. **Binance Spot vs Futures Configuration (`exchange-type`):**
   OctoBot supports both Binance Spot and Futures:
   - **Spot:** Set `"exchange-type"`: `"spot"` under exchange config.
   - **Futures:** Set `"exchange-type"`: `"linear"` (USDT-M Futures) or `"exchange-type"`: `"inverse"` (Coin-M Futures).
   - **Critical Sync Requirement:** When switching between Spot and Futures, `"exchange-type"` must be updated in BOTH `/opt/octobot/user/config.json` AND `/opt/octobot/user/profiles/<profile_id>/profile.json`. Restart container (`docker restart octobot`) after saving.

10. **Changing Strategy Timeframe & Scalping Tuning:**
   - Update timeframe settings in profile's `specific_config/`:
     - `DailyTradingMode.json`: `"time_frame"`: `"5m"`
     - `SimpleStrategyEvaluator.json`: `"evaluator_depth"`: `"5m"`, `"required_time_frames"`: `["5m"]`
   - **Fast Limit Fills for Scalping:** To prevent pending `BUY_LIMIT` orders from being canceled unfilled on fast timeframes (5m), enable fixed limit difference in `DailyTradingMode.json`:
     ```json
     {
         "time_frame": "5m",
         "required_strategies": ["SimpleStrategyEvaluator"],
         "fixed_limit_prices": true,
         "fixed_limit_prices_difference": 0.0001
     }
     ```
   - **Exclude Stablecoin Pairs:** Always remove stablecoins (e.g. `USDC/USDT`, `USDS/USDT`) from profile `profile.json` under `crypto-currencies`. Scalping stablecoins produces `Missing ticker data` errors and fee drag without price movement.
   - Restart container (`docker restart octobot`) so WebSocket feeds and trading engine apply changes.

10. **Token Rate Limit Error on Short Timeframes (`max_gpt_tokens`):**
    - **Symptom:** `Impossible to get ChatGPT evaluation for <symbol> on <timeframe>: No remaining free tokens for today : Daily rate limit reached (used X out of Y)`.
    - **Cause:** Default `max_gpt_tokens` limit in `GPTEvaluator.json` is set low (e.g. `1000`), which is quickly exhausted when evaluating shorter timeframes (e.g. `5m`) across multiple pairs.
    - **Fix:** Set `"max_gpt_tokens": 1000000000` in `/opt/octobot/user/profiles/<profile_id>/specific_config/GPTEvaluator.json` and restart container (`docker restart octobot`).

11. **Spot/Futures SHORT Order Behavior & `DailyTradingMode` Dynamics:**
    - **DailyTradingMode Position Allocation & Target Profits Mode:** Under default `DailyTradingMode`, OctoBot treats positions as portfolio allocations (buying on `LONG` / `VERY_LONG`, selling held assets on `SHORT` / `VERY_SHORT`). Even when `"exchange-type"` is set to `"linear"` (USDT-M Futures), `DailyTradingMode` will NOT open a naked short contract if the portfolio holds 0 units of the base asset. Instead, it logs `Skipping order creation for <pair>: not enough available funds`.
    - **No `FuturesTradingMode` Class:** There is no mode named `FuturesTradingMode` in OctoBot. Modes like `SignalTradingMode` or enabling `target_profits_mode: true` inside `DailyTradingMode` allow entry orders (including short entries) with automatic TP/SL placement.
    - **Target Profits Mode Configuration (Futures Entry + TP/SL):**
      To open short/long entries on futures and auto-create Take Profit & Stop Loss orders:
      ```json
      {
          "time_frame": "1h",
          "required_strategies": ["SimpleStrategyEvaluator"],
          "fixed_limit_prices": true,
          "fixed_limit_prices_difference": 0.0001,
          "target_profits_mode": true,
          "target_profits_mode_take_profit": 3.0,
          "target_profits_mode_stop_loss": 1.5,
          "use_stop_orders": true,
          "target_profits_mode_enable_position_increase": false
      }
      ```
    - **Timeframe Tradeoffs (1h vs 5m):** 1h timeframes are optimal for AI trading. 5m timeframes suffer from heavy fee drag (exchange fees eating 0.1% price moves), market noise/whipsaws causing stop-outs, and high API token usage. 1h provides stable signals where TP (e.g. 3%) easily covers fees.
    - **Buy Limit Order Gaps on Fast Timeframes (5m):** OctoBot places `BUY_LIMIT` orders at a dip price below current market price. On 5m timeframes, if price does not drop to hit the limit before the next 5m candle evaluation, an AI shift to `SHORT` will automatically cancel the pending limit order without filling.
    - **Fast Scalping Instant Execution Fix:** To force limit orders to fill immediately near market price during 5m scalping, add `"fixed_limit_prices": true` and `"fixed_limit_prices_difference": 0.0001` to `DailyTradingMode.json` inside the profile's `specific_config/` directory.

13. **Combining AI Evaluator with TA Indicators & Exact Schema Keys:**
    - **Problem:** AI evaluation alone on short timeframes (5m) can cause frequent false signals (*whipsaw*) and fee drag.
    - **Fix:** Combine `GPTEvaluator` with Technical Analysis evaluators in `specific_config/SimpleStrategyEvaluator.json`:
      ```json
      {
          "evaluator_depth": "1h",
          "required_time_frames": ["1h"],
          "required_evaluators": [
              "GPTEvaluator",
              "RSIMomentumEvaluator",
              "MACDMomentumEvaluator",
              "EMAMomentumEvaluator"
          ]
      }
      ```
    - **CRITICAL Schema Requirements for `GPTEvaluator.json`:**
      - `"indicator"` MUST match exact full string keys in `GPTEvaluator.INDICATORS` (e.g. `"RSI: Relative Strength Index"`, `"EMA: Exponential Moving Average"`). Short aliases like `"RSI"` throw `KeyError: 'RSI'`.
      - `"source"` MUST match candle price source in `GPTEvaluator.SOURCES` (e.g. `"Close"`, `"Open"`, `"High"`, `"Low"`, `"Volume"`). Placing indicator names like `"Relative Strength Index"` in `"source"` throws `KeyError: 'Relative Strength Index'`.

14. **Resetting Paper Trading Live State & Portfolio Balance:**
    - To clear stuck orders/trades and reset simulated balance back to initial capital:
      1. Stop container: `docker stop octobot`
      2. Clear live state and logs: `rm -rf /opt/octobot/user/data/live/* /opt/octobot/user/logs/*`
      3. Start container: `docker start octobot`

15. **Binance API Keys & Sandboxed / Testnet Mismatch:**
    - **Symptom:** Logs/UI report `Invalid Binance authentication details. Warning: exchange sandbox is enabled...`.
    - **Cause:** When `"sandboxed": true` is set in `config.json`, OctoBot attempts to validate API keys against Binance Testnet endpoints. Real Binance Mainnet API keys will fail validation.
    - **Fix:** Set `"sandboxed": false` in `/opt/octobot/user/config.json` when using real Binance Mainnet API credentials.



