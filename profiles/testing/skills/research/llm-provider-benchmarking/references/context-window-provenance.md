# Context-window provenance: 9router → Hermes (openai-compatible providers)

## Symptom
A model supports N context upstream, but the router reports a different number and Hermes follows the router number. Values can be wrong in BOTH directions (too small AND too large).

## Where the router number comes from (source-read)
Resolution lives in the built server at `/usr/lib/node_modules/9router/app/.next-cli-build/server/chunks/` — primary `24.js`, near-identical copies in `8402.js` and `412.js` (grep all three). `getCapabilitiesForModel(provider, model)` (function `x`) merges, in order:

1. `PROVIDER_CAPABILITIES` — exact (provider, model) entries for first-class providers (nvidia, codex, kiro, qoder, poolside, opencode-go, ...).
2. `MODEL_CAPABILITIES` (`let k={...}`) — exact model-id map, e.g. `deepseek-v4.1-flash`, `glm-5.3-flash`, `claude-opus-4-6`/`claude-sonnet-4-6` → 1e6.
3. `PATTERN_CAPABILITIES` (`let r=[...]`) — glob list, FIRST match wins: `*step-*` → 128k, `*qwen*` → 262144, `*grok-4.6*` → 500k, `*grok-4*` → 256k, `*nemotron*` / `*ling-*` / `*deepseek*` → 128k, `*muse*spark*` → 1048576, `*laguna-s-2.1*` → 1e6 before generic `*laguna*` → 200k. Caps without an explicit `contextWindow` (e.g. `*claude*haiku*`) fall through to the default.
4. `DEFAULT_CAPABILITIES` (`h`) — 200k ctx / 64k output.
5. Catalog overlay — `setCatalogSource.getLimits()` reads `~/.9router/model-catalog.json` `providers[provider][model]`; if an entry with `contextWindow>0` exists it OVERRIDES everything above.

For openai-compatible custom providers (provider id like `openai-compatible-chat-<uuid>`, display prefix e.g. `prof/`), 9router's live `/models` fetch keeps only ids/names. `model-catalog.json` providers are keyed by models.dev provider names; custom providers never appear there, so step 5 never fires. Net result: the reported number is the first matching static rule — treat it as a heuristic, not metadata.

## Diagnose before theorizing
1. Upstream: `curl -s "$UPSTREAM_BASE/models" -H "Authorization: Bearer $KEY"` → map id → `context_length`.
2. Router: same curl against `http://127.0.0.1:20128/v1/models`; key from `sqlite3 /root/.9router/db/data.sqlite "SELECT key FROM apiKeys WHERE name='Production Key';"` (chmod 600, never echo).
3. Diff in Python; for each differing model find its rule: exact entries `grep -o '"<id>":{[^}]*}' chunks/24.js`, pattern list `grep -n 'let r=\[' chunks/24.js`, then first-match order.

## Fix options
- **Hermes client-side — VERIFIED recipe (most direct, applies today)**: `agent/model_metadata.py: get_model_context_length` resolves in this order — step 0 explicit `context_length` config override → MoA → **step 0b `model_overrides`** → step 0c `custom_providers` → endpoint-scoped → persistent cache → endpoint `/models` probe. The override therefore beats BOTH the cache and the router probe, so you do NOT need to clear `<profile>/context_length_cache.yaml` for it to take effect.

  ```bash
  # pin the true window for ONE runtime model id (alias/combo name), e.g. "ds"
  hermes -p <profile> config set model_overrides.<provider>.<model_id>.context_window 524288
  hermes -p <profile> config get model_overrides        # confirm it landed
  ```

  - Schema: `model_overrides.<provider>.<model_id>.context_window`. `<provider>` is the Hermes provider id (`custom` for a custom endpoint); `<model_id>` is the **runtime id the request is sent under** — an alias/combo name such as `ds`, NOT the underlying upstream id (`prof/step-5-preview`). That is what makes per-alias scoping possible: an override on `ds` leaves `prof/step-5-preview` still resolving to the router's number. Read the combo membership first (`sqlite3 ~/.9router/db/data.sqlite "SELECT name,models FROM combos;"`) so you know what an alias actually serves.
  - Each `config set` writes a timestamped backup under the profile's `backups/config/` — cite that as the revert path; revert with `hermes -p <profile> config unset model_overrides.<provider>.<model_id>.context_window`.
  - File-edit tools (`patch`, `write_file`) REFUSE `config.yaml` outright ("security-sensitive configuration"). Write it from `terminal` with `hermes config set` — never a direct edit, and never the bare global `hermes config set` on a multiplexed host.

  Verify without mutating config twice — run this BEFORE the change (baseline) and again after:

  ```python
  import sys; sys.path.insert(0, "/usr/local/lib/hermes-agent")
  from hermes_cli.config import load_config_readonly
  from agent.model_metadata import _config_override_context_length, get_model_context_length
  cfg = load_config_readonly(); base = "http://127.0.0.1:20128/v1"
  for m in ["ds", "prof/step-5-preview"]:
      print(m, "override:", _config_override_context_length(m, base, cfg["model"]["provider"], cfg.get("custom_providers")))
      print(m, "final:  ", get_model_context_length(m, base_url=base, api_key="x", provider="custom"))
  ```

  A served profile's already-running turn keeps the old value until its adapters are rebuilt — bounce the profile (see `hermes-agent` → `references/multiplex-profile-lifecycle.md`) when the change must apply immediately.
- **The reported number is advisory, not enforced**: a request whose prompt exceeds the router's reported window still succeeds (observed 161982 prompt_tokens through a 128000 report, HTTP 200). The real damage is client-side — Hermes compacts/truncates early and silently discards context the model would have accepted. Frame the fix as "stop losing usable context", not "unblock a failing request".
- **Router-side via catalog overlay**: add `providers["<provider-id>"]["<model>"] = {"contextWindow": N, "maxOutput": M}` to `~/.9router/model-catalog.json` — the overlay path (step 5) applies it at request time. CAVEAT: `catalog-sync` rebuilds that file from models.dev/api.json (24h interval, or POST /api/models/catalog-sync) and writes only models.dev-derived providers, so manual entries get wiped — pair with `MODEL_CATALOG_SYNC=off` or re-apply after each sync. Verify on the running instance before promising it.
- Patching the static tables in the built chunks works until the next 9router update/reinstall — prefer the overlay or client-side override.

## Observed mapping (all base ids upstream at 524288, one custom provider)
- Too small: `step-*` → 128000 (`*step-*`), `nemotron-*` → 128000, `ling-*` → 128000, `deepseek-unrestricted` → 128000 (`*deepseek*`), `qwen3.8-flash` → 262144, `qwen3.8-omni-flash` → 262144, `grok-4.7` → 256000, `claude-haiku-5.5` → 200000 (pattern matched but carried no ctx → default), ids with no rule at all (`big-pickle`, `cat-jam`, `north-mini-code`) → 200000.
- Too large: `claude-opus-4-6`, `claude-sonnet-4-6`, `deepseek-v4.1-flash`, `glm-5.3-flash`, `laguna-s-2.1` → 1000000; `grok-4.6` → 500000; `muse-spark-1.3-contributor`/`mimo-v2.6-flash` → 1048576.
- Upstream 1M `*-unrestricted` ids often map to 128k/200k for the same reason (their base names hit the small-window patterns).
