---
name: model-benchmark-cekin
description: Use when comparing LLM benchmarks or picking 9router models.
---

# Model Benchmark Cekin (9router + Arena)

## 9router facts (VERIFIED 2026-10-10)
- Router: next-server on :20128, app at /usr/lib/node_modules/9router/app. `/v1/models` lists ~98 models; `prof/*` = provider "unli 30 day" (flat). `ag/*` = agent-pool combos.
- QUIRK: non-streaming responses have `data: [DONE]` appended → strip via `raw.split('data: [DONE]')[0]` before json.loads.
- QUIRK: reasoning models need max_tokens >=1200 for trivial prompts (reasoning tokens eat budget → empty content, finish_reason=length).
- Route health is per-model: 503 = upstream route down on that provider (retry later ≠ model bad); 410 Gone = removed; empty non-JSON = route broken. Verify a "failed" model by probing another route (e.g. gemini/ prefix) before judging the model.
- Smoke script (tool-call + tool-loop + instruction test, 4 workers): /root/.hermes/profiles/orion/cache/scratch/agent_smoke.py — reusable, edit MODELS list.

## Benchmark workflow
1. LMArena = arena.ai (heavy CSR). Use browser session isolation (browser_exec session='bench') — shared default tab can be hijacked by other automations. Extract via js('document.body.innerText') after >10s wait; pages: /leaderboard/text, /agent, /webdev, /vision (coding redirects to webdev sub-pages).
- Agent arena metric = Net Improvement % (not Elo). Text/WebDev/Vision = Elo-ish score.
2. llm-stats.com/leaderboards/best-ai-for-tool-calling → hard tool-calling bench (Terminal-Bench, Toolathlon, MCP Atlas). web_extract works, save to cache/web/ and grep.
3. Decode codenames: web_search with 'openrouter' / 'opencode zen' keywords. Known map (2026-10): muse-spark=Meta (contributor tier = trains on your prompts), nemotron=Nvidia, glm=Z.ai, mimo=Xiaomi, ling=Ant Group, dots=Xiaohongshu, longcat=Meituan, step=StepFun, north-mini-code=Cohere Labs, laguna=Poolside, apodex=Apodex, jev-1.13=TypeSafe STRUCTURED DECISION model (not a chat model, 400s on chat completions), qwen=Alibaba, grok=SpaceXAI label on arena, claude=Anthropic.
- Stealth (unverifiable identity): big-pickle & exo & fledge-alpha (OpenCode Zen; fledge likely a router, GPQA 92.3% per stealthmodels.com), space-bunny (OpenRouter; community guess MiniMax M3, GPQA 82.1%).
4. Never judge a model's agentic ability from simple smoke alone; cross-check arena Agent + tool-calling leaderboard. "NO_TOOLCALL" in smoke can be router passthrough bug (content empty / tool call not surfaced), not model incapacity — if loop test passes, tool RESULTS are handled fine.

## 2026-10-10 verdict (unli provider, 32 prof/* models)
- Best Hermes brain: prof/deepseek-v4.1-flash (3/3 smoke, 1.9s tool latency, TB2.1 90.6%, tool-board #4, 1M ctx, vision).
- Quality ceiling: prof/claude-opus-4-6 (arena TEXT 1504) but route 503'd all day on unli; sonnet-4-6 same.
- Dark horse agentic: prof/qwen3.7-plus (agent arena +7.21%) but route returned garbage that day; qwen3.7-max +5.50% same.
- Solid working alts: qwen3.8-flash, grok-4.6, glm-5.3-flash (cheap, 1M ctx, best working vision 1273), step-3.7-flash, laguna-s/xs, north-mini-code, dots-3-note-preview, nemotron-3-super.
- Avoid for agentic: jev-1.13, exo (410), mimo-v2.6-flash (agent arena 0.35% + broken tool passthrough), step-5* (arena agentic 0.01-0.35% despite passing simple smoke), nemotron-3-ultra, longcat, ling-3.1 (slow, 66s), muse contributor (privacy).