# Model Re-Route Capability-Flag Audit

A fleet model re-route (dashboard assignment, `config set model.default`, or any full model-block rewrite) can silently drop adjacent capability keys. Observed 2026-10-13: after all fleet profiles were re-routed to `gpt-sol`, `model.supports_vision` and `context_length` disappeared from 12 profile configs that carried them the day before; the untouched `groupbot` kept its flag.

## Why it matters

`agent/image_routing.py` resolves the vision verdict in order: `model.supports_vision` -> `providers.<p>.models.<model>.supports_vision` -> `custom_providers[].models.<model>.supports_vision` -> managed-runtime probe -> models.dev catalog -> Ollama probe. Local 9router combo IDs are absent from models.dev, so with the override gone the verdict is None and image attachments fall back to auxiliary text enrichment (an aux vision model transcribes instead of native image blocks). Chat still works, so the regression is invisible without a probe. `config.yaml` is re-read per turn (mtime check), so a corrected flag applies without a gateway restart.

## Audit procedure

1. List profiles missing the flag: `grep -L 'supports_vision' /root/.hermes/profiles/*/config.yaml`
2. Confirm prior intent: pre-route backup `profiles/<name>/backups/config/config.yaml.good.<ts>` and the declarative repo history.
3. Re-add via CLI only: `hermes -p <profile> config set model.supports_vision true`
4. Verify with the Hermes venv python and `HERMES_HOME=/root/.hermes/profiles/<p>`: `decide_image_input_mode("custom", "<model>", load_config())` must return `native` (returns `text` while the flag is missing).
5. Re-sync declarative repo + gates + push, then refresh the dual-layer snapshot so backups capture the corrected state.

## Rule

Treat every re-route as capability-flag-lossy until proven otherwise; re-audit `supports_vision` (and `context_length`) immediately after any main-model write.
