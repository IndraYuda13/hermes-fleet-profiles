---
name: market-data-integrity-gate
description: Validate market data before directional claims.
version: 1.0.0
author: Fleet Upgrade Research
license: MIT
metadata:
  hermes:
    tags: [markets, trading, data-quality, risk]
    category: fleet-upgrade
---
# Market Data Integrity Gate

## When to Use
Use before directional market conclusions, catalyst trades, derivatives analysis, backtests, or comparisons across venues/instruments.

## Procedure
1. Verify instrument identity: symbol, contract type, quote currency, expiry/perpetual, venue.
2. Verify timestamp and freshness for every major input; normalize time zones.
3. Check units/scales and whether data is mark/index/last/trade/order-book/OHLC.
4. Check liquidity/spread/depth context before interpreting price moves.
5. Avoid mixing current price with stale positioning/order-book/on-chain data without an explicit lag warning.
6. Separate observation, thesis, catalyst, and invalidation.
7. Seek an alternative explanation that would produce the same observed move.
8. State what data would invalidate or materially weaken the conclusion.
9. Calibrate confidence to data quality, not narrative coherence.

## Verification
Directional output includes venue/instrument/timestamps, freshness assessment, thesis, alternative explanation, invalidation, and data-quality caveats.
