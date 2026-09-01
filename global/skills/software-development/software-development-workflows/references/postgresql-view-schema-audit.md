# PostgreSQL view and base-schema audit

Use this reference for read-only audits of deployed PostgreSQL views, migrations, analytics SQL, and the base schema behind them.

## Evidence order

1. Read the supplied view-definition and column artifacts.
2. Inspect the live PostgreSQL catalog. Confirm database, schema, relation kind, deployed view definition, columns, constraints, indexes, row counts, and representative data.
3. Compare source SQL with `pg_get_viewdef(..., true)`. Treat the live definition as authoritative for deployment status, and source files as evidence of intended design.
4. Run bounded probes for each high-risk semantic claim. Do not infer correctness from a view existing or from a prior PASS report.
5. Confirm no writes occurred by using read-only commands and reporting the no-change boundary.

Useful catalog probes:

```sql
SELECT table_type, table_name
FROM information_schema.tables
WHERE table_schema = 'mai'
ORDER BY table_type, table_name;

SELECT c.relname, c.relkind, pg_get_viewdef(c.oid, true)
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'mai' AND c.relname LIKE 'v3_2_2_v_%';

SELECT conrelid::regclass, conname, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE connamespace = 'mai'::regnamespace;
```

## Correctness patterns

### Recursive greedy non-overlap

An effective sample must carry every partition key through the seed and recursive terms. If the domain has a scope, use `(scope_type, scope_key, horizon_label)` rather than only `(symbol, horizon_label)`. Select the first row deterministically with `ORDER BY as_of, run_id`, then select the next row with:

```sql
next.as_of >= previous.as_of + make_interval(mins => previous.horizon_minutes)
```

Do not use `LAG` as a substitute for greedy selection. `LAG` compares to the immediately preceding raw row, not the last accepted row, and therefore fails when skipped observations still overlap the accepted observation. Validate effective counts and accepted timestamps with a synthetic or real probe.

If scope fields are absent from the base schema, derive a versioned fallback from frozen metadata, such as `snapshot_json`, and label the fallback (`SYMBOL` or `UNKNOWN`) rather than silently presenting it as an explicit scope.

### Matched-specific effective samples

Build `matched_raw` first, then inner join it to the effective-outcome view to form `matched_effective`. Compute effective metrics only from `matched_effective`. Compute raw counts separately with distinct keys such as `(run_id, horizon_label)`. Never left join effective rows back to raw rows and then average effective fields, because raw rows can remain in the denominator and duplicate keys can multiply metrics.

### Exact input reconstruction

If an output table stores only an aggregate prediction, do not claim its original input set is recoverable. Reconstruct from the same source tables and rules used by the workflow, including:

- valid-status filters;
- champion and challenger source boundaries;
- category and agent identity;
- horizon-specific weights;
- weight source entity type;
- deterministic ordering;
- null/default weight behavior.

Expose reconstructed input count, stored input count, reconstructed mean, stored mean, and an explicit match flag. A mismatch is a data-quality finding, not a reason to silently substitute the reconstruction for the stored result. Prefer persisting an input manifest/hash in future schema revisions.

### PIT regime and leakage

Regime labels must come from data frozen at or before `analysis_runs.as_of`, normally from `snapshot_json` or a PIT-safe source table. Never derive a forecast-time regime from outcome fields such as `return_pct`, `max_high`, `min_low`, or any target/future price. If the frozen snapshot lacks the required regime field, emit `UNKNOWN` and a coverage/status field. Do not fabricate a constant regime to make the view non-empty.

### Directional and economic confusion matrices

Use explicit labels and units. If returns are stored in percentage points, 20 bps is `0.20`, not `20`. Calculate all four cells for both directional and economic labels, and add `unknown` for NULL outcomes. Use `IS TRUE` and `IS FALSE` predicates so NULL does not become a false negative or true negative by accident. Keep cost parameters visible and versioned rather than hiding them in a magic literal.

### Missing verifier or coverage

Start from the effective sample and `LEFT JOIN` optional verifier, challenger, or domain evidence. An inner join measures only present coverage and hides missingness. Report total effective rows, present rows, missing rows, and coverage rate before computing quality metrics. This applies to verifier evaluation, challenger matching, domain coverage, and optional agent results.

### System overview

A system overview should distinguish raw totals from effective totals and expose data-health denominators: status breakdowns, pending/retry/failed jobs, latest completion times, verifier coverage, challenger input mismatches, scope groups, and unknown regime counts. Every effective total should be sourced from the canonical effective view, not reimplemented with a second counting rule.

## PostgreSQL and SQL pitfalls

- `CREATE OR REPLACE VIEW` cannot safely change the existing public column contract. Prefer versioned view names for incompatible output changes.
- Join on all semantic keys, especially `run_id` plus `horizon_label`, scope, configuration, and source variant where applicable. A primary key on `(run_id, horizon_label)` is a warning that `run_id` alone is incomplete.
- `COUNT(*)`, `COUNT(column)`, and `COUNT(*) FILTER (...)` have different NULL behavior. Make the denominator explicit.
- Use `COUNT(DISTINCT (key1, key2))` or a pre-deduplicated CTE when duplicate source rows are possible.
- `BETWEEN` creates overlapping confidence buckets at shared boundaries. Prefer half-open intervals, with an explicit final inclusive bucket.
- `CORR` can be NULL for constant or undersized samples. Preserve NULL or expose a `correlation_undefined` flag instead of treating it as zero without a label.
- Recursive CTEs need deterministic tie-breaking and a monotone acceptance condition. Check execution plans and add indexes on partition/order keys for production-scale data.
- JSON path extraction returns NULL for absent fields. Cast only after guarding malformed or absent values, and preserve unknown status.
- `NOT x` is NULL when `x` is NULL. Use three-valued logic deliberately in quality and confusion-matrix queries.
- A prior analytics test passing proves only the tested predicates and fixture, not that the deployed view matches the intended semantics or covers missing data.

## Verification checklist

- [ ] Live relation kind and deployed definition inspected.
- [ ] Source/deployed definition diff understood.
- [ ] Base columns, PKs, FKs, checks, and indexes inspected.
- [ ] Cardinality and duplicate-key probes run.
- [ ] Effective sample logic checked against accepted timestamps.
- [ ] PIT fields and leakage boundaries checked.
- [ ] NULL and missing-coverage paths counted explicitly.
- [ ] Units and thresholds checked.
- [ ] Raw versus effective denominators separated.
- [ ] No files or database objects modified during audit.
