# TimesFM 2.5 Real-Time WebSocket Streaming & Deployment Notes

## 1. CCXT Market Data Caching
- Cache OHLCV data into Parquet/CSV formats under `data_cache/` partitioned by `exchange_symbol_timeframe_start_end`.
- When users request wide date ranges, chunk the requests to avoid exchange rate-limits (Binance 500-1000 candles per call) and stream download progress events back to UI.

## 2. Real-Time Candle-by-Candle Streaming Protocol
- Use a dedicated worker task/generator over FastAPI WebSockets (`/ws/backtest`).
- Support playback speed throttling (`1x`, `2x`, `5x`, `10x`, `max`) by adjusting `asyncio.sleep()` intervals between emitted steps.
- Provide bi-directional controls (`pause`, `resume`, `stop`, `set_speed`).

## 3. High-Precision Fee Accounting & Reconciliation
- Calculate maker/taker fees dynamically on notional order value ($Q \times P$).
- Account for entry slippage ($P \times (1 + \text{slip})$) and exit slippage ($P \times (1 - \text{slip})$).
- Keep running total of cumulative fees paid and verify $100\%$ PnL reconciliation:
  $$\text{Final Equity} = \text{Initial Capital} + \sum \text{Realized PnL} - \sum \text{Fees Paid}$$
