# Wrap / rebrand detection: is this model the model it claims to be?

Use when paying for a named model behind an aggregator (any `provider/model` alias) and the buyer doubts authenticity. Goal: a verdict backed by independent signals, not the model's self-report.

## Evidence hierarchy
Strongest to weakest. A verdict needs at least two independent STRONG signals.

**STRONG**
1. **Identity rotation**: >=6 identical identity probes returning *different developers/model families* (e.g. Claude + MiniMax + Xiaomi MiMo + OpenAI Codex under one name). One model cannot change developer between requests -> load-balanced pool behind one label. Protocol: same prompt, temperature unset, 3-6s spacing, retry 429/502 with 20-25s backoff; record every answer verbatim.
2. **Tokenizer delta fingerprint**: `prompt_tokens(model, FIXED_LONG_TEXT) - prompt_tokens(model, "Halo.")` compared across models on the SAME gateway. Deltas within ~1% of a different family (candidate 396 vs deepseek 398, while mimo 449) = candidate is that family, not its claimed vendor's tokenizer. Use the same gateway so the injected system prompt cancels in the subtraction; never compare raw prompt_tokens across gateways.
3. **Injected-prompt overhead**: `prompt_tokens` for a 1-2 word prompt. Candidate ~699 vs peers 82-423 on the same gateway = ~700 tokens of hidden system prompt (branding/instructions) injected by the reseller. Confirmed when a watermark/promo footer appears appended inside otherwise clean answers.
4. **`/v1/models` self-declaration**: `owned_by: "rebrand"` (or an `owned_by` naming a non-vendor org), identical `created` across all models, a model list containing `-UNCENSORED`, joke, or third-party names alongside the claimed flagship — a vendor catalog never looks like this.

**MEDIUM**
5. **Envelope forensics**: response `id` prefix and usage shape must match the claimed vendor. Anthropic real -> `msg_...` + `input_tokens/output_tokens`; observed `gen-...` + OpenAI-style `completion_tokens_details.reasoning_tokens` = gateway-emulated. Same for a native `/v1/messages` probe: an OpenAI-shaped payload or `gen-` id proves emulation, not passthrough.
6. **Header/branding leaks**: custom `x-*` notice headers or HTML page branding naming the reseller.
7. **Endpoint liveness**: consistent `502 Bad Gateway` from origin across >=10 tries, both direct and via router = that label's upstream is dead (buyer pays for an error page). Distinguish from 429 (shared free pool; message often contains the reseller's support email) and from transient 503.

**WEAK (record, never a verdict alone)**
- Self-reported knowledge cutoff, self-identified name, claimed parameter count. A wrapper's system prompt can force any answer and a real model can be told to lie. Only *inconsistency across repeats* is informative.

## Standard probe battery (order matters — cheapest first)
1. `GET /v1/models` with the key -> dump `owned_by`, `created`, `context_length`, full id list.
2. Bare `GET /` and `/v1` (HTML) -> read `<title>` + meta description for reseller branding.
3. Headers on any POST (`curl -D-`) -> custom `x-*` notice headers.
4. Identity battery x6 (identical prompt) -> rotation check.
5. Cutoff battery x6 -> inconsistency check.
6. Baseline-vs-fixed `prompt_tokens` per model -> injected-prompt overhead + tokenizer delta.
7. Envelope capture (full JSON, non-stream, small `max_tokens`) -> id prefix, usage shape, footer text.
8. Native vendor endpoint probe (e.g. `/v1/messages` + `anthropic-version`) -> emulation check.
9. Liveness loop on every claimed model -> catch dead labels (502/504).
10. Repeat the identity battery through the local router alias -> confirms the local setup serves the same pool.

## Router-side traps
- **Bare id vs prefixed id**: requesting a prefixed provider's model by bare name returns `No active credentials for provider: openai|anthropic` — the router infers provider from id shape. Use the stored alias form from `sqlite3 /root/.9router/db/data.sqlite "SELECT name,models FROM combos;"` (e.g. `oni/claude-opus-5.5`).
- Map an alias to its connection via `providerConnections`: `provider LIKE 'openai-compatible-chat-%'`, `data` JSON holds `baseUrl`, `providerSpecificData.prefix`, `apiKey`. The key is plaintext in that row — write it to a 600 file, never echo it into command output.
- A combo bound to a dead label still looks "configured"; liveness must be probed, not inferred from the row existing.
- Cloudflare-fronted resellers answer scripts with `403 error code: 1010`; send a browser User-Agent on every request or you misread a UA block as an auth failure.

## Report shape the user wants
Verdict line first (`wrap.` / `genuine` / `inconclusive`), then numbered *observed* evidence each carrying the concrete value read, weaker signals explicitly labeled weak, then an action (refund / retest command). Cite probe script paths so the run is reproducible; mark claims observed vs inferred.