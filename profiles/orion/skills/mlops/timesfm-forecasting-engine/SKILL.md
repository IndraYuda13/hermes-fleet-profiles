---
name: timesfm-forecasting-engine
description: Use when building TimesFM 2.5 time-series quant engines.
---

# TimesFM Forecasting & Quantitative Engine

Comprehensive operational workflow for integrating Google Research's **TimesFM 2.5 (200M)** decoder-only foundation model into production forecasting services and quantitative backtesting platforms.

## When to Use This Skill
- Loading and configuring `google/timesfm-2.5-200m-pytorch` or Flax variants.
- Performing zero-shot point and continuous quantile forecasting on time-series data.
- Building low-latency streaming backtesters with WebSocket telemetry.
- Implementing realistic quantitative trading backtests with exchange fees (Maker/Taker), slippage, and strict anti-lookahead guarantees.

---

## 1. TimesFM 2.5 Model Setup & Optimization

### Environment Setup (PyTorch CPU / GPU)
```bash
# PyTorch CPU optimization
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install "timesfm>=2.0.2" pandas numpy ccxt
```

### Python Model Initialization
```python
import torch
import numpy as np
import timesfm

# Optimize threading for multi-core vCPU
torch.set_num_threads(4)
torch.set_float32_matmul_precision("high")

# Load 200M parameter foundation model
model = timesfm.TimesFM_2p5_200M_torch.from_pretrained("google/timesfm-2.5-200m-pytorch")

# Compile configuration
model.compile(
    timesfm.ForecastConfig(
        max_context=1024,
        max_horizon=256,
        normalize_inputs=True,
        use_continuous_quantile_head=True,
        fix_quantile_crossing=True,
    )
)
```

### Quantile Output Parsing
TimesFM continuous quantile head returns distribution quantiles from 10th to 90th percentile:
- `point_forecast`: shape `(batch_size, horizon)`
- `quantile_forecast`: shape `(batch_size, horizon, 10)`
  - `q_fc[:, :, 0]`: Mean
  - `q_fc[:, :, 1]`: 10th Percentile ($q_{10}$)
  - `q_fc[:, :, 5]`: Median (50th Percentile)
  - `q_fc[:, :, 9]`: 90th Percentile ($q_{90}$)

### Quantile Uncertainty Filter:
$$\text{Quantile Spread} = \frac{q_{90} - q_{10}}{\text{Price}_t}$$
High quantile spread indicates high forecast uncertainty; avoid trading or reduce position size to prevent fee bleeding in noisy market regimes.

### Common Pitfalls & Hybrid Strategy Solutions:
- **Raw AI Smoothing vs Crypto Noise:** Raw point forecasts suffer from mean-reversion smoothing. Wrap the AI inside a **Trend Regime Filter (EMA 50)** and **Dynamic Volatility Threshold (ATR)**.
- **Fee Bleed Defense:** A standard round-trip friction is ~0.14%. Use evaluation **stride = 4-8 bars** and require predicted drift $\ge 1.5 \times \text{ATR}$ to prevent over-trading.
- **Active Risk Control:** Pair with ATR-based TP ($1.5 \times \text{ATR}$) and SL ($0.8 \times \text{ATR}$) with breakeven trailing stop.
*(See `references/quant-notes.md` for full hybrid architecture).*

---

## 2. Realistic Quantitative Backtesting Protocol

### Anti-Lookahead Guarantees
1. Features, past context, and TimesFM predictions at step $t$ must strictly use data up to $\text{Close}_t$.
2. Trade entry and exit execution must strictly be simulated on bar $t+1$ $\text{Open}$ (or realistic intra-bar limit fills).

### Exchange Fee & Slippage Friction
- **Binance VIP0 / Futures Baseline:**
  - Maker Fee: `0.02%` ($0.0002$)
  - Taker Fee: `0.05%` ($0.0005$)
  - Execution Slippage: `0.02%` ($0.0002$) per fill
- **Formulas:**
  - Long Entry Fill: $\text{Price}_{\text{open}, t+1} \times (1 + \text{Slippage})$
  - Long Exit Fill: $\text{Price}_{\text{open}, t+1} \times (1 - \text{Slippage})$
  - Transaction Fee: $\text{Notional} \times \text{TakerFee}$

---

## 3. Streaming WebSocket Telemetry Pattern
For real-time backtesting dashboards, decouple CPU inference by streaming state payloads:
```json
{
  "event": "step",
  "index": 150,
  "timestamp": "2026-08-15T12:00:00Z",
  "current_price": 65420.50,
  "predicted_price": 66100.00,
  "quantiles": [64800, 65100, 65420, 65800, 66100, 66500, 67200],
  "position": "LONG",
  "unrealized_pnl": 124.50,
  "realized_pnl": 350.20,
  "equity": 10474.70,
  "fees_paid": 12.80
}
```

---

## 4. Production Deployment & Cloudflare Tunnel Streaming
- When deploying real-time WebSocket backtesters behind Cloudflare Tunnel:
  1. Ensure HTTP host headers and WebSocket upgrades (`Upgrade: websocket`, `Connection: Upgrade`) are supported.
  2. Set up dedicated background daemon/systemd service binding to an isolated local port (e.g. `8250`).
  3. Route ingress in `/root/.cloudflared/config.yml` to `http://localhost:<port>` and configure CNAME record.
  4. Test both HTTPS document root and WSS handshake endpoints (`wss://<domain>/ws/backtest`) to ensure zero proxy buffering.

