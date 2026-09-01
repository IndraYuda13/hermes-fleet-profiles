# MAI V3.2.3 Transactional Test Fixture Reference

## Pattern: BEGIN/ROLLBACK DB Fixtures in n8n

The V3.2.3 analytics test workflow uses a single PostgreSQL query node that:
1. `BEGIN;`
2. Creates `TEMP TABLE ... ON COMMIT DROP` for test metadata
3. Inserts synthetic rows into real production tables (`analysis_runs`, `v3_outcomes`, `agent_results`, `v3_shadow_agent_results`, `v3_shadow_predictions`, `aggregations`)
4. Queries actual deployed `mai.v3_2_3_v_*` views against the synthetic + existing data
5. Asserts results via a CTE-based assertion framework
6. `ROLLBACK;` — all synthetic rows are removed

## Assertion Catalog (21 tests, A-S)

| # | ID | Name | What it validates |
|---|-----|------|-------------------|
| 1 | A | `A_greedy_exact_sequence` | 4h horizon with runs at 00:00, 00:30, 03:30, 04:00, 04:30, 08:00 selects [00:00, 04:00, 08:00] |
| 2 | A2 | `A_greedy_adjacent_nonoverlap` | Every adjacent pair in selected sequence >= 4h apart |
| 3 | B | `B_missing_boundary_uses_next_valid_row` | No exact 04:00 row; selects next valid >= prev+4h |
| 4 | C | `C_multi_symbol_scope_isolation` | BTC and ETH at same timestamps get independent sequences |
| 5 | D | `D_exact_seed_no_extra_horizon_rows` | Different earliest runs per horizon don't create duplicate branches |
| 6 | E | `E_agent_availability_on_canonical_effective_sample` | entity_effective_n=2, canonical=2 → availability=1.0 |
| 7 | F | `F_calibration_raw_10_effective_2` | raw_n=10, effective_n=2 exact |
| 8 | G | `G_matched_effective_one` | One valid matched Champion+Challenger row → effective_matched_n=1 |
| 9 | H | `H_exact_challenger_ensemble_composition` | Challenger ensemble = [A01, A02, A11, A12] (champion base + supplemental) |
| 10 | H2 | `H2_challenger_input_reconciliation` | Reconstructed input matches prediction metadata (MATCH state) |
| 11 | I | `I_correlation_variant_isolation` | No champion supplemental pairs (0), challenger has them (5) |
| 12 | J | `J_ablation_variant_isolation` | Champion 2 rows, Challenger 4 rows, 1 distinct label |
| 13 | K | `K_pit_regime_snapshot_invariance` | Same snapshot → same regime; opposite EMA → different regime |
| 14 | L | `L_economic_confusion_matrix` | Known 4+1 rows produce econ_tp=1, fp=1, tn=1, fn=1, unknown=1 |
| 15 | M | `M_verifier_missing_coverage` | NOT_RUN case appears as NOT_RUN/MISSING, coverage_rate=0 |
| 16 | N | `N_weekly_report_uses_only_v323_views` | Weekly report contains v3_2_3 refs, no v3_2_2 refs |
| 17 | O | `O_graph_side_effect_scan` | Zero telegram/trading/weight-mutation/auto-promotion nodes |
| 18 | P | `P_neutral_threshold_classification` | ±0.05 mean → NEUTRAL; +0.11 → BULLISH; -0.11 → BEARISH |
| 19 | Q | `Q_aggregator_improvement_quadrants` | Controlled fixtures produce correct both_correct/improved/harmed/both_wrong |
| 20 | R | `R_agent_maturity_uses_entity_effective_n` | entity_effective_n=2 → EXPERIMENTAL even if canonical is large |
| 21 | S | `S_ablation_delta_orientation` | Full outperforms LOO → positive delta (agent helped) |

## Final Sync Additions (P-S)

### P: Neutral Threshold
- Fixtures: FIX_NEUTRAL_POS (mean=+0.05), FIX_NEUTRAL_NEG (mean=-0.05), FIX_BULL_THRESH (mean=+0.11), FIX_BEAR_THRESH (mean=-0.11)
- Verifies the 0.10 threshold boundary is correctly applied in ablation and aggregator evaluation

### Q: Aggregator Quadrants
- Uses TEST_NEUTRAL scope: 4 runs covering all four outcome quadrants
- Confirms `aggregator_improved` = agg correct + det wrong, not just `aggregator_hit`

### R: Agent Maturity
- Uses TEST_AVAIL scope: canonical_effective_n=2, entity_effective_n=2
- Confirms maturity_label=EXPERIMENTAL (entity_effective_n < 50), not inflated by canonical

### S: Ablation Delta
- Uses TEST_ABLAT scope: A01 score=+0.50, A02 score=+0.10, mean=+0.30 (BULLISH)
- Full hit=1, LOO-without-A01 mean=+0.10 (NEUTRAL threshold), LOO hit=0
- Delta = full - LOO = positive (agent helped)

## Key Design Decisions

- **Fixture namespace:** `V3.2.3_TEST_TRANSACTION_ROLLBACK` — clearly identifies test data
- **Run IDs:** Prefixed `FIX_` (e.g. `FIX_GREEDY_0`, `FIX_MATCH`, `FIX_ENSEMBLE`, `FIX_NEUTRAL_POS`, `FIX_ABLAT_FULL`)
- **Scope types:** Prefixed `TEST_` (e.g. `TEST_GREEDY`, `TEST_MULTI`, `TEST_ECON`, `TEST_NEUTRAL`, `TEST_ABLAT`)
- **Graph scan exclusion:** The test query node itself is excluded from the side-effect scan via `WHERE n->>'name' <> 'Query DB Analytics Views'`
- **Evidence consistency:** A JS post-processor recomputes passed/total from the actual tests array
- **Deployed execution is authoritative:** The n8n execution ID is the primary evidence, psql fixture run is secondary
