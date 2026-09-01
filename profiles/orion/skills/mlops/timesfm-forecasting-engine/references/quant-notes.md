# TimesFM 2.5 Quantitative Implementation Notes & Trading Pitfalls

### Quantile Calibration Formula
$$\text{Expected Value} = \mu = \text{Forecast}_0$$
$$\text{Lower Bound (10th)} = q_{10} = \text{Forecast}_1$$
$$\text{Upper Bound (90th)} = q_{90} = \text{Forecast}_9$$

### Risk-Adjusted Decision Rule
$$\text{Conviction Signal} = \frac{\mu - \text{Price}_t}{\text{Price}_t} \times \left(1 - \frac{q_{90} - q_{10}}{\text{Price}_t}\right)$$

---

## 1. Why Zero-Shot Time-Series Models (TimesFM, Chronos) Underperform in Raw Trading

When deploying foundation models directly into financial time series without a quant wrapper:

1. **Smoothing / Mean-Reversion Drift:**
   - Foundation models pre-trained across multi-domain datasets inherently expect smooth continuity or mean-reverting curves.
   - Financial assets (crypto in particular) exhibit non-stationary regimes, fat tails, and sharp liquidity sweeps. Raw point forecasts often yield tiny drifts (0.1%–0.3%) that trigger trades without sufficient signal magnitude.

2. **The "Fee Bleed" Phenomenon:**
   - In realistic backtesting, round-trip transactions cost ~0.14% (Taker fee 0.05% + Slippage 0.02% upon entry AND exit).
   - High-frequency unconstrained AI signal changes cause rapid position flipping where transaction friction wipes out all gross alpha.

3. **Absence of Trend Alignment (Counter-Trend Whipsaws):**
   - Entering long simply because the AI predicts +0.5% during a macro bear trend (below 200 EMA) creates heavy downside exposure.

---

## 2. Institutional Hybrid Framework: AI Forecast + Quantitative Risk Overlays

To turn time-series AI predictions into a consistently profitable strategy, implement a 4-layer quantitative pipeline:

```
[ Market Bar (OHLCV) ]
         │
         ▼
[ Layer 1: Trend Regime Filter ]
  - Bull: Close > EMA(50) -> Long Only
  - Bear: Close < EMA(50) -> Short Only
         │
         ▼
[ Layer 2: Dynamic Volatility Gate (ATR) ]
  - Require Predicted Drift > 1.5 * ATR(24) / Price
  - Silence signals during dead low-volatility chop
         │
         ▼
[ Layer 3: Quantile Asymmetry Ratio ]
  - Upside/Downside Skew: (q90 - Price) / (Price - q10) >= 2.0
  - Quantile spread must be expanding in favor of the direction
         │
         ▼
[ Layer 4: Active Trade & Risk Management ]
  - Take Profit: 1.5x - 2.0x ATR
  - Stop Loss: 0.8x - 1.0x ATR (Risk:Reward >= 1:1.8)
  - Trailing Stop & Breakeven Lock at +1.0% PnL
  - Forecast Stride: Evaluate only every 4 to 8 bars (reduce fee churn)
```

---

## 3. Proven Parameter Baselines for Crypto 1H Timeframe

- **Context Window:** 128 to 256 bars
- **Forecast Horizon:** 6 to 12 bars ahead
- **Signal Drift Threshold:** Dynamic $1.5 \times \text{ATR}$ (or $\ge 0.8\%$ minimum fixed)
- **Stride:** 4 bars
- **Execution:** $t+1$ Open fill with $0.02\%$ slippage and $0.05\%$ taker fee

### Key CCXT Fetch Settings for Clean Backtest Data
- Always sort timestamps ascending.
- Ensure no gap in timestamps: verify interval matches `timeframe` delta.
- Deduplicate timestamps before seeding backtester.
