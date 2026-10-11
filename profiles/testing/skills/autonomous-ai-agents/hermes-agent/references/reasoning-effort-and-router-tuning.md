# Reasoning Effort & Local Router Tuning

Two INDEPENDENT layers decide how hard the model thinks. Diagnose and set them separately —
fixing one does not move the other. Answering "what effort is it using?" from only one layer is
the common wrong answer.

## Layer 1 — the router/proxy in front of the endpoint

A `custom` provider often points at a local OpenAI-compatible router (9router, LiteLLM, one-api)
that owns its own per-connection thinking mode, combos, and key pooling. Find the router's config
store before assuming Hermes controls it.

- 9router: `~/.9router/db/data.sqlite`. Tables: `settings` (JSON blob), `providerConnections`,
  `providerNodes`, `combos`, `apiKeys`, `usageHistory`, `requestDetails`.
  - `settings.providerThinking` is keyed by PROVIDER CONNECTION id
    (`openai-compatible-chat-<uuid>`), NOT by the combo/alias name the user sees. `settings.providerOverrides`
    empty means no per-connection override, so the global `providerThinking` entry applies.
  - Combos live in `combos.models` — a JSON array of `prefix/model` (e.g. `["prof/deepseek-v4.1-flash"]`).
    The `prefix` resolves to a baseUrl in `providerNodes`. Two combos can point at the same model.
  - `requestDetails` keeps only a bounded recent window (~1000 rows) and truncates the request body,
    so it is NOT a reliable way to read what was actually sent.
- Dump only the scoped rows you need. A blanket `SELECT data FROM kv;` returns megabytes of base64
  (seen: 2.6 MB of Gemini thought signatures) and the shell output cap truncates the tail, hiding
  the row you wanted.
- Mask secrets in anything you print: `providerConnections.data` contains the upstream `apiKey`
  (and `_meta`/`settings` can contain a bcrypt password + tunnel URL). Strip `apiKey`/`password` keys.

Then read the router's adapter: the mode it stores maps onto the wire in code, not by name.
- Observed in 9router's deepseek case: `xhigh | max -> reasoning_effort:"max"`, and it always emits
  `thinking:{type:"enabled"}`. So raising the router from `xhigh` to `max` is a NO-OP at the wire.
- Several branches force `thinking:{type:"enabled"}` regardless of the stored mode, which is why an
  "off" setting can still produce reasoning tokens.
- Router binaries live under `/usr/lib/node_modules/<router>/`; the real logic is in the bundled
  chunks (`app/.next-cli-build/server/chunks/*.js` for a Next-based router) — grep there, and walk
  back from `case"<provider>":` to the enclosing function to see the full mapping.

## Layer 2 — Hermes sends the level

`agent.reasoning_effort` (global) and `agent.reasoning_overrides` (per-model map) are resolved by
`hermes_constants.resolve_reasoning_config(cfg, model)`. Precedence: session `/reasoning --session`
> per-model override > global `agent.reasoning_effort` > the provider profile's
`default_reasoning_config` (the built-in `custom` profile supplies `{"enabled": True, "effort": "medium"}`).

- Inspect/set: `hermes -p <profile> config get agent.reasoning_effort` /
  `hermes -p <profile> config set agent.reasoning_effort <none|minimal|low|medium|high|xhigh|max|ultra>`.
  `VALID_REASONING_EFFORTS` in `hermes_constants.py` is the canonical ladder.
- `hermes config set` can print `is not a recognized config key … saved anyway` and still be correct:
  the validator schema is a separate list from the keys the runtime resolves. Trust the read-back
  (`config get`) and the resolver test below, not the warning.
- Verify WITHOUT restarting the gateway — call the resolver directly with the profile venv:

```bash
PY=/usr/local/lib/hermes-agent/venv/bin/python
$PY -c "import yaml,sys; sys.path.insert(0,'/usr/local/lib/hermes-agent'); \
from hermes_constants import resolve_reasoning_config; \
print(resolve_reasoning_config(yaml.safe_load(open('config.yaml')),'<model>'))"
# -> {'enabled': True, 'effort': 'max'}
```

- Effort is re-read from `config.yaml` per turn (the gateway loads config fresh, keyed to the file
  signature), so a `config set` takes effect on the NEXT turn. No gateway restart needed.
- `custom` / OpenAI-compatible profiles forward `reasoning_effort` verbatim across the whole
  OpenAI-compat set (`max` is NOT clamped down). Providers with narrower wire vocabularies clamp
  through the tables in `agent/reasoning_effort.py` (`DEEPSEEK_V4_EFFORTS`, `KIMI_K3_EFFORTS`, GLM,
  xAI, `ACTUAL_RELAY_EFFORTS`, …).
- A session-scoped `/reasoning` override SHADOWS the config value until cleared, so a config change
  can look like it did nothing in a live session.

## Benchmarking streaming throughput

Measure decode tok/s from real streamed completions and read `usage` — never estimate from
characters.

- `stream: true` PLUS `"stream_options": {"include_usage": true}` is required, or the final usage
  block never arrives and there are no token counts to divide by.
- `decode_tok_s = completion_tokens / (last_chunk_time - first_chunk_time)`;
  `ttft = first_chunk_time - request_start`. Report TTFT separately — it is easily dominated by
  upstream queueing, not by output length.
- Reasoning tokens count as completion tokens, so always report reasoning-on and reasoning-off
  separately or you are measuring two different things.
- Report per CONTENT SHAPE, because throughput differs ~2.5x: dense/numeric output is far faster than
  prose/essay for the same model (strategies differ per sequence). A single "tok/s" number is
  meaningless without the shape.
- Do not use `completion_tokens vs streamed chunk count` as a shape detector — chunk coalescing
  makes chunk counts a poor proxy (dense output coalesces to ~6 tokens/chunk).
- Concurrency: run N parallel streams. If per-stream tok/s is flat and the aggregate scales ~Nx, the
  upstream is not throughput-sharing.
- Transient 502/503/504 under load: the router's own retry middleware applies only to NON-streaming
  POSTs, so a streamed request gets no automatic retry — add your own bounded backoff.

Ready-to-run helpers: `scripts/bench_stream_tok_s.py` (streaming decode benchmark),
`scripts/inspect_9router_state.py` (dumps combos / per-connection thinking mode, secrets masked).
