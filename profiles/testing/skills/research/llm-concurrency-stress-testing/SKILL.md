---
name: llm-concurrency-stress-testing
description: "Use when stress-testing LLM router concurrency and limits."
version: 1.0.0
author: hermes-testing
license: MIT
metadata:
  hermes:
    tags: [benchmark, stress-test, concurrency, llm, router]
    related_skills: [llm-provider-benchmarking]
---

# LLM Concurrency & Stress Testing

## When to Use
Use when evaluating the concurrency ceiling, throughput saturation, burst resilience, and queue degradation of LLM endpoints and aggregators (e.g., 9router, jerouter, LiteLLM, vLLM).

## 3-Phase Stress Methodology
Always execute benchmark harnesses using system Python (`/usr/bin/python3`) to ensure third-party networking dependencies (`requests`) are available.

### Phase 1: Concurrency Ramp ($c = 1 \to 2 \to 4 \to 8 \to 12 \to 16$)
- Purpose: Identify the breaking point where requests begin to queue, stall, or fail.
- Fixed prompt: 200–250 token expected output.
- Record per concurrency level:
  - Wall time (total duration from dispatch to last worker completion).
  - Success rate (% OK vs dropped requests).
  - P50 & P90 TTFT (identifies queue buildup).
  - Aggregate Throughput ($\sum \text{Tokens} / \text{Wall Time}$).
  - Straggler rate (fraction of requests taking $>12\text{s}$ to first token).

### Phase 2: Sustained Back-to-Back Burst Waves
- Purpose: Detect whether the router throttles, runs out of upstream connection pools, or exhibits warm-cache acceleration under continuous load.
- Dispatch 2–3 consecutive waves of $c = 8$ with zero cooldown.
- Compare Wave 1 vs Wave 2/3:
  - If Wall Time decreases and TTFT drops: connection pool warm-up.
  - If Wall Time increases or 504s appear: router memory/buffer exhaustion or upstream rate throttling.

### Phase 3: Heavy Payload & Reasoning Endurance ($c = 4$, $\ge 600$ tokens)
- Purpose: Test sustained decode speed and multi-stream stability when emitting thousands of tokens.
- Set HTTP timeout $\ge 120\text{s}$.
- Keep prompt questions tightly bounded (e.g., "explain in 2 concise paragraphs") even when requesting technical depth. Open-ended prompts trigger models with reasoning (CoT) to balloon thinking tokens into the thousands, exceeding test time budgets.

## Metric Calculation Standard
- **TTFT (Time To First Token)**: $t_{\text{first\_text}} - t_{\text{sent}}$. Must measure arrival of first text delta (`delta.content` or `delta.reasoning_content`). Discard keep-alive comments.
- **Decode TPS (Stream Pump Speed)**: $\text{completion\_tokens} / (\text{total\_time} - \text{TTFT})$.
- **Effective TPS (Perceived User Speed)**: $\text{completion\_tokens} / \text{total\_time}$.
- **Aggregate Throughput (Bandwidth Capacity)**: $\sum(\text{tokens}) / \text{Wall Time}$.

## Router Quirks & Pitfalls
- **SSE Keep-Alive Pings (`: ping`)**: Aggregators emit `: ping\n\n` comments while waiting for upstream queues to prevent Cloudflare/TCP socket timeouts. SSE stream readers must discard lines starting with `:` before matching `data: ` blocks; otherwise JSON parsing crashes.
- **Silent Timeout Drops (HTTP 504 vs 429)**: Most aggregators do not issue HTTP 429 when concurrency saturates. Instead, excess requests sit in queue until the upstream gateway timeout (~45–50s), then abort with `HTTP 504 Gateway Timeout`. When testing saturation, monitor for 504 spikes rather than 429s.
- **Always Stream (`stream: true`)**: Non-streaming requests on queued models fail with gateway timeouts because the router cannot send intermediate SSE keep-alive pings.
- **Unclamped Reasoning Tokens**: Models with thinking (Step-5, DeepSeek R1/Flash) often ignore `max_tokens` constraints during the reasoning phase. Benchmark scripts must budget execution time for both reasoning generation and content emission.
