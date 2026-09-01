---
name: time-series-foundation-models
description: Deploy, optimize, and backtest TimesFM and TS models.
version: 1.0.0
author: ORION
license: MIT
metadata:
  hermes:
    tags: [timesfm, time-series, forecasting, quant, backtesting, mlops]
    related_skills: [vps-llm-sizing, trading-research]
---

# Time-Series Foundation Models (TimesFM & Zero-Shot Forecasting)

## When to Use This Skill
Use this skill when integrating, benchmarking, optimizing, or deploying foundation models for time-series forecasting (such as Google TimesFM, Amazon Chronos, or Salesforce MOIRAI), especially in quantitative trading, financial analysis, or load telemetry.

## Core Capabilities & Properties (TimesFM 2.5)

- **Architecture:** Decoder-only transformer pre-trained on multi-domain time-series datasets.
- **Model Checkpoints:** `google/timesfm-2.5-200m-pytorch` (200M parameters, max 16k context, up to 1k forecast horizon).
- **Quantile Head:** Outputs both point forecasts and continuous quantile distributions (10th to 90th percentiles).
- **Zero-Shot Advantage:** No per-dataset fine-tuning required; input historical sequence $\to$ output future forecast.

---

## CPU Installation & Optimization Workflow

Avoid bloated CUDA wheels on CPU-only VPS hardware to prevent disk exhaustion:

```bash
# 1. Install CPU-only PyTorch build first
pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# 2. Install TimesFM package & quantitative dependencies
pip install timesfm ccxt pandas numpy
```

### In-Memory Optimization Template

```python
import torch
import timesfm

# Set thread parallelism matching available physical/virtual cores
torch.set_num_threads(4)
torch.set_float32_matmul_precision("high")

# Load model into RAM
model = timesfm.TimesFM_2p5_200M_torch.from_pretrained("google/timesfm-2.5-200m-pytorch")
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

---

## Latency & Batching Guidelines

Benchmarked on Intel Xeon Platinum (4 vCPU allocated):
- **Single Window Inference:** `~1.38s` average latency per forecast (Context: 128, Horizon: 12).
- **Batch Inference Optimization:** Grouping inputs into batches (e.g. 16 windows) drops latency to `~940ms` per window.
- **Production Rule:** For walk-forward backtests or multi-asset streaming, always batch rolling window contexts instead of executing sequential single-item loops.

## Orchestration & Production Deployment Guidelines
- **Real-Time Backtest Streaming:** Expose step-by-step telemetry via FastAPI WebSocket (`/ws/backtest`) with candle index, TimesFM point/quantile predictions, position state, equity, and trade blotter.
- **Web Interface:** Design high-density Neo-Brutalist dashboards (dark obsidian, neon accents, candlestick charts with prediction fan overlays).
- **Public Domain Exposure:** Route FastAPI daemon via Cloudflare Tunnel to production domain (e.g. `timesfm.indrayuda.my.id`).

---

## Quantitative Backtesting & Fee Friction Standards

When evaluating forecasting foundation models on financial assets (e.g., Binance Spot / Futures):

1. **Exchange Fee & Slippage Baseline:**
   - **Maker Fee:** `0.02%` (0.0002) - Limit order fills
   - **Taker Fee:** `0.05%` (0.0005) - Market order fills
   - **Slippage Impact:** `0.02%` (0.0002) per fill
2. **Zero-Lookahead Constraint:**
   - Predictions at bar $t$ must only consume prices up to index $t$.
   - Trade execution must strictly occur at bar $t+1$ `open` (or verified intra-bar limit fills).
3. **Quantile Spread (Uncertainty Filter):**
   - Extract 10th and 90th percentiles: $q_{10}$ and $q_{90}$.
   - Relative Spread: $\text{Spread} = \frac{q_{90} - q_{10}}{\text{Price}_t}$
   - Only trigger trades when directional forecast $\Delta > \text{Threshold}$ AND uncertainty spread remains low.
