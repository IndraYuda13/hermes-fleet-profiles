# NOFX AI500 Troubleshooting & Bypass

This reference records the solution for the `Failed to fetch AI500 list` error on the NOFX platform when using the legacy `nofxos.ai` API.

## Problem Context
The legacy API key `cm_568c67eae410d912c54c` used in the default source code for the `ai500` coin pool has been deprecated by `nofxos.ai`. Requests to `/api/ai500/list` fail, which blocks the trader from starting if `use_ai500` is active.

## Resolution
To bypass this without changing the Go source code:
1. Turn off `use_ai500` and switch the source type to `static` in the `strategies` table.
2. Provide a default static coin list (e.g., `["BTCUSDT","ETHUSDT"]`) so the trader has coins to analyze.
3. Update the `use_coin_pool` flag to `0` in the `traders` table for existing traders.

### Execution Scripts
```sql
-- Update strategy configuration to use static coins instead of ai500
UPDATE strategies SET config = json_set(config, '$.ai_config.coin_source.use_ai500', json('false'));
UPDATE strategies SET config = json_set(config, '$.ai_config.coin_source.source_type', 'static') WHERE json_extract(config, '$.ai_config.coin_source.source_type') = 'ai500';
UPDATE strategies SET config = json_set(config, '$.ai_config.coin_source.static_coins', json('["BTCUSDT","ETHUSDT"]'));

-- Disable AI500 directly on the trader instance
UPDATE traders SET use_coin_pool = 0 WHERE id = '<trader_id>';
```

After modifying the database, restart the `nofx-trading` docker container to clear the cache and reload the modified strategy.