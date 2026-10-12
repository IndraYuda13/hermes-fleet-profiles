---
name: llm-provider-benchmarking
description: Use when benchmarking LLM endpoints speed & effort effects.
version: 1.0.0
author: hermes-testing
license: MIT
metadata:
  hermes:
    tags: [benchmark, llm, api, performance, reasoning]
    related_skills: [service-origin-tracing]
---

# LLM Provider Benchmarking (OpenAI-compatible endpoints)

## When to Use
Benchmarking or validating models behind an aggregator (9router, OpenRouter, LiteLLM...): tok/s, TTFT, reasoning-effort effects, "fake reasoning" checks, parallel scaling, stability.

## Method — 4 serial phases, resume-safe JSONL
1. **A Speed matrix**: every model × every effort level (default/None, none, minimal, low, medium, high, xhigh, max), SERIAL, same ~700-word-output prompt, max_tokens ≥6k. Stream SSE with `stream_options:{include_usage:true}`. Record per run: TTFT, decode tps, completion_tokens, reasoning_tokens, reasoning_chars, finish_reason.
2. **B Intelligence**: 8 deterministic tasks with auto-graders (extract `<ans>...</ans>`). Run at none/medium/high/max + default. Accuracy delta (max−none) is the effort-effect proof.
3. **C Parallel/stability**: N identical requests at c=1/4/8 (ThreadPoolExecutor); agg tps = Σtokens/wall, scaling = c8/c1 (ideal ≥3× at 8); plus 2 repeat runs for CV%.
4. **D Upstream direct**: same effort probes bypassing the router — separates "router flattened it" from "upstream ignores it".

## Pitfalls (observed live on 9router + jerouter, 2026-10)
- **BURST delivery**: some backends buffer and dump all tokens at the end — naive decode tps reads absurd (5088 tps seen) but is illusory. Detect: log per-chunk arrival times; span(first→last) < 1s with 100s of tokens = burst. Fair metric: **effective throughput = completion_tokens / wall_time**. Verify burst is upstream (router usually passes through).
- **Hidden CoT**: grok-4.7 sends no reasoning_content deltas (only usage metadata) — TTFT balloons 20–90s as thinking happens "in the dark". Grade effort by accuracy + rtok metadata only.
- **Missing/dual usage**: qwen and muse via jerouter omit reasoning_tokens entirely; some upstreams send two usage chunks (estimated + detailed xAI-style). Fall back to chars/4 estimate and flag as estimated.
- **rtok is not monotonic**: lower reasoning tokens at max than minimal can be legitimate (model stops when satisfied). Non-monotonic ≠ fake; compare accuracy across efforts instead.
- **Upstream 504 on hard prompts** for slow models — use read timeout ≥600s and record status codes.
- **Straggler stalls under concurrency** (jerouter prof/, 2026-10): ~28% of c≥2 requests can sit 5–35s before first token while decode speed stays ~124 t/s. Aggregate tps is bimodal: ~500–570 t/s clean c=8 vs ~90–155 t/s stalled. The stall is UPSTREAM (reproduced bypassing 9router, incl. one single-request 25s TTFT + 504), NOT the router. Methodology: interleave A/B alias-vs-upstream in the same window, count stalls (ttft>5s), and report clean vs stalled aggregates separately — never just average agg_tps.
- **Aggregator effort mappings** (9router source): level→budget none:0, minimal:512, low:1024, medium:8192, high:24576, xhigh:32768, max:128000; per-backend transforms by thinkingFormat (deepseek → `thinking:{type:enabled}` + `reasoning_effort high|max`; zai → `enable_thinking` + low|high|max; qwen → `enable_thinking` + `thinking_budget`; step → raw effort with xhigh/max→high). A provider-level `providerThinking` override may exist in settings — verify empirically whether request-level params still win (they did).
- **9router requestDetails does NOT log openai-compatible providers** — use `usageHistory` for token totals; inspect forwarded payloads only via the `.next-cli-build` server chunks or direct probes.
- Run hours-long matrices as background phase-chains (wait-for-done-marker → next phase → analyze); skip-done logic makes every phase resumable so disconnects don't lose progress.

## Harness & access
- Reference impl + raw data: `/root/prof_bench` (bench_a/b/c/d.py, analyze.py, gen_report.py, chart.py, chunk_probe.py, stream_classify.py).
- Router: `http://127.0.0.1:20128/v1`. Key: `sqlite3 /root/.9router/db/data.sqlite "SELECT key FROM apiKeys WHERE name='Production Key';"` → chmod 600, never echo.
- Report: styled HTML → WeasyPrint PDF.

## Calibration (prof/ = je.jerouter.web.id, 9 models, 549 runs)
- deepseek-v4.1-flash: best all-round — 207 tps sustained, ~0.9s TTFT, real linear effort (none=0 → high≈3800 rtok on hard prompts), 7.7× parallel scaling.
- grok-4.7: hidden CoT, TTFT 20–90s, ~1.05× scaling → avoid live/concurrent use.
- qwen3.8-27b: burst + 504 timeouts + broken usage → avoid. muse-spark: burst → batch only.
- glm-5.3-flash: rtok pinned at output limit regardless of effort (effort knob useless).
