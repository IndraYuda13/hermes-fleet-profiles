# MAI V3.2 Science Layer Analytics & Protection Implementation Detail

## Key Analytical Rules & Mathematical Formulations

### 1. Overlapping Sample Protection & Effective Sample Size (Deterministic Epoch Cohorts)
When analysis runs execute at high frequency (e.g. every 30 minutes), outcome evaluation intervals (1h/4h/12h/24h) overlap across consecutive runs.
Raw sample count $N_{raw}$ overstates statistical independence.

#### Flaw of Naive `LAG(as_of)` Slicing:
Using `LAG(as_of) OVER (...)` to check `as_of >= prev_as_of + horizon` fails on high-frequency series (e.g. 30m cadence with 4h horizon). Every row $N$ is compared to row $N-1$ (30m earlier), so nearly all rows fail the condition forever, causing `non_overlapping_n` to stay locked near 1.

#### V3.2.1 Epoch Cohort SQL (superseded by V3.2.3):
The epoch bucketing approach assigns runs to `FLOOR(EPOCH/horizon)` cohorts. This works but can select runs only 30 minutes apart across bucket boundaries.

#### V3.2.3 Recursive CTE Greedy Selector (current):
```sql
WITH RECURSIVE outcome_candidates AS (
  SELECT c.scope_type, c.symbol, o.run_id, o.horizon_label, o.horizon_minutes, o.as_of, ...
  FROM mai.v3_outcomes o JOIN mai.v3_2_3_v_run_context c USING (run_id)
),
seed AS (
  SELECT DISTINCT ON (scope_type, symbol, horizon_label) oc.*, 1::integer AS seq
  FROM outcome_candidates oc
  ORDER BY oc.scope_type, oc.symbol, oc.horizon_label, oc.as_of, oc.run_id
),
greedy AS (
  SELECT s.* FROM seed s
  UNION ALL
  SELECT n.*
  FROM greedy g
  CROSS JOIN LATERAL (
    SELECT oc.*, (g.seq+1)::integer AS seq
    FROM outcome_candidates oc
    WHERE oc.scope_type=g.scope_type AND oc.symbol=g.symbol AND oc.horizon_label=g.horizon_label
      AND oc.as_of >= g.as_of + (g.horizon_minutes * INTERVAL '1 minute')
    ORDER BY oc.as_of, oc.run_id LIMIT 1
  ) AS n
)
SELECT * FROM greedy;
```
Key properties: exact seed per `(scope_type, symbol, horizon_label)`, deterministic tiebreaker `(as_of, run_id)`, guaranteed `next.as_of >= prev.as_of + horizon`.

#### Matched-Specific Greedy (V3.2.3):
Champion vs Challenger comparison uses a separate greedy selector over the matched population (runs where both Champion and Challenger produced valid predictions), not an intersection with the global canonical sample.

### 2. Wilson Score 95% Confidence Interval for Hit Rates (Effective N)
Avoid reporting single-point hit rates without uncertainty bounds.
Compute Wilson Score interval ($z=1.96$ for 95% confidence) explicitly using **EFFECTIVE N** ($n_{effective}$):

$$\hat{p}_{lower, upper} = \frac{\hat{p}_{eff} + \frac{z^2}{2 n_{eff}} \pm z \sqrt{\frac{\hat{p}_{eff}(1-\hat{p}_{eff})}{n_{eff}} + \frac{z^2}{4 n_{eff}^2}}}{1 + \frac{z^2}{n_{eff}}}$$

In PostgreSQL SQL:
```sql
ROUND(GREATEST(0, (e.effective_hit_rate + 1.96*1.96/(2*e.effective_n) - 1.96 * SQRT((e.effective_hit_rate*(1-e.effective_hit_rate) + 1.96*1.96/(4*e.effective_n))/e.effective_n))/(1 + 1.96*1.96/e.effective_n)), 4) AS wilson_ci_95_lower,
ROUND(LEAST(1, (e.effective_hit_rate + 1.96*1.96/(2*e.effective_n) + 1.96 * SQRT((e.effective_hit_rate*(1-e.effective_hit_rate) + 1.96*1.96/(4*e.effective_n))/e.effective_n))/(1 + 1.96*1.96/e.effective_n)), 4) AS wilson_ci_95_upper
```

### 3. Sample Maturity Classifications (Effective N Driven)
Sample maturity MUST be evaluated against $N_{effective}$, not raw row count $N_{raw}$:
- `Effective N < 50`: `EXPERIMENTAL`
- `50 <= Effective N <= 199`: `EARLY_EVIDENCE`
- `Effective N >= 200`: `REVIEWABLE` (Requires human review; never auto-promote)

*Note: Raw N >= 200 with Effective N < 50 remains `EXPERIMENTAL`.*

### 4. PIT-Safe Regime Classification (V3.2.3)
Derive regime ONLY from frozen `analysis_runs.snapshot_json` at/before `run.as_of`:
- **Trend:** `BULLISH_TREND` if h1.ema20 > h1.ema50 AND h4.ema20 > h4.ema50; `BEARISH_TREND` if both <; else `RANGE_MIXED`. Return `UNKNOWN` if any EMA field is missing.
- **Volatility:** Absolute bins on `realized_vol` (decimal return std dev): `<0.005 LOW`, `<0.015 MEDIUM`, else `HIGH`. Missing = `UNKNOWN`.
- **Invariance test:** Same snapshot + different future return must produce identical regime. Two controlled snapshot fixtures with opposite EMA relationships must produce different trend regimes.

### 5. Agent Availability on Effective Sample (V3.2.3)
Correct formula: `availability_on_effective_sample = entity_effective_n / canonical_effective_n` for the same `(scope_type, symbol, horizon)`. NOT `effective_n / raw_n`.
Expose `raw_coverage_ratio = raw_n / raw_outcome_n` separately.

### 6. Full Economic Confusion Matrix (V3.2.3)
Economic-good: `aggregation_signed_return_pct > 0.20` (exceeds 20 bps research cost baseline).
Report: `econ_tp`, `econ_fp`, `econ_tn`, `econ_fn`, `econ_unknown` (NULL signed return), `economic_precision`, `economic_recall`, `economic_opportunity_capture`.
Research cost breakdown: 10 bps fee + 5 bps spread + 5 bps slippage = 20 bps. Not a live cost guarantee.

### 7. Verifier Coverage Including NOT_RUN (V3.2.3)
Use `LEFT JOIN mai.verifications` to include runs where verifier was not executed.
Classify: PASS/WARN/BLOCK/NOT_RUN_MISSING. Report coverage rate, correct blocks, harmful blocks, correct passes, bad passes.

### 8. Ensemble Input Reconstruction (V3.2.3)
CHALLENGER_INPUT = Champion base valid agents + V3 supplemental shadow agents.
Dedup: one unique `(run_id, ensemble_variant, agent_key)`. Shadow supplemental has source_priority=2 (wins over champion_base priority=1 via `ORDER BY source_priority DESC`).
Reconciliation: compare `reconstructed_input_n` vs `prediction_valid_agent_count` and directional means. States: MATCH/MISMATCH/NO_PREDICTION/NO_RECONSTRUCTED_INPUT.

### 9. PostgreSQL Analytical Functions & Grant Syntax Notes
- Native sign function in PostgreSQL is `SIGN(numeric)`, not `Math.sign(...)`.
- `GRANT SELECT ON ALL TABLES IN SCHEMA mai TO mai_app;` grants privileges on both base tables and views. `GRANT SELECT ON ALL VIEWS` is invalid SQL syntax in PostgreSQL.
