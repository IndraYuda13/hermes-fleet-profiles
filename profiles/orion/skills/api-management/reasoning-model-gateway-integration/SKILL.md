---
name: reasoning-model-gateway-integration
description: Use when routing reasoning LLMs through local AI gateways.
version: 1.0.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [llm, reasoning, deepseek, 9router, gateway, openai-proxy, json-mode]
---

# Reasoning Model Gateway Integration

## Overview

Reasoning models (such as DeepSeek-R1, DeepSeek-V3 with reasoning paths, o1, or local quantized reasoning variants) introduce distinct protocol behaviors when routed through OpenAI-compatible local reverse proxies (e.g., 9Router, LiteLLM, vLLM, or custom proxies).

Failing to account for reasoning tokens and thinking latency results in premature token truncation (`finish_reason: "length"`), broken JSON syntax, or client timeout aborts.

## Integration Architecture & Protocol Invariants

### 1. Token Budget Allocation (Reasoning Tokens + Output Tokens)
- **Mechanism:** Reasoning models emit hidden or explicit reasoning content (`reasoning_content`) before generating the target response or structured JSON. Both the reasoning chain and the output payload are billed against the request's `max_tokens` (or `max_completion_tokens`).
- **Failure Mode:** Capping `max_tokens` at standard defaults (e.g., 2048 or 4096) causes the model to consume most tokens during the reasoning phase, truncating the final JSON payload mid-stream (`finish_reason: "length"`), producing unparseable strings (e.g., `Unterminated string in JSON`).
- **Rule:** Set `max_tokens` to at least `8192` (or >= `12288` for extensive generations) when calling reasoning models for structured JSON output.

### 2. Client-Side HTTP Timeouts
- **Mechanism:** Deep reasoning models perform sequential chain-of-thought processing before emitting the first content tokens. Generating 500-800 words of rich content alongside a deep reasoning trace routinely takes 40-70 seconds.
- **Failure Mode:** Standard HTTP client timeouts (30s or 60s) trigger an `AbortSignal.timeout` before the gateway completes the request.
- **Rule:** Configure HTTP client timeouts to at least `120000ms` (2 minutes), or decouple the execution into an asynchronous background worker queue with polling.

### 3. Explicit Framing (`stream: false` vs Streaming)
- **Mechanism:** Local reverse proxies (such as 9Router) may negotiate SSE streaming by default when the `stream` parameter is omitted or when client headers differ from standard OpenAI SDK defaults.
- **Failure Mode:** A non-streaming consumer parsing the raw response body receives partial chunk frames or trailing `data: [DONE]` delimiters, causing JSON parser crashes.
- **Rule:** Always explicitly pass `stream: false` in the completion payload when expecting a standard JSON completion object from a gateway adapter.

### 4. Structured JSON Extraction & Fallback Parsing
- **Mechanism:** When using `response_format: { type: "json_object" }` through gateway combos or proxy translations, some upstream backends wrap JSON in markdown blocks (` ```json ... ``` `) or append terminal markers.
- **Rule:** Implement a layered sanitization pipeline:
  1. Strip trailing `data: [DONE]` if present.
  2. Strip markdown fences (```json ... ```).
  3. Locate the outer `{` and `}` if extraneous commentary wraps the object.

### 5. Latency Control & Bypassing Reasoning Overhead for Interactive Workflows (`enable_thinking: false`)
- **Mechanism:** When routing reasoning models (e.g. DeepSeek-R1, hybrid reasoning checkpoints) through OpenAI-compatible reverse proxies or gateways (such as 9Router), the model by default generates long internal chain-of-thought traces (often 2,000–8,000 tokens) before emitting structured output. For interactive user-facing generation (such as real-time narrative choices, dynamic web forms, autocomplete), this inflates latency from 10–20 seconds to 250–350+ seconds, causing perceived UI freezing and proxy timeouts.
- **Rule:** For latency-sensitive structured generation where deep reasoning is unnecessary:
  1. Pass gateway-supported parameters to disable or suppress reasoning generation: `chat_template_kwargs: { "enable_thinking": false }` or model parameters like `thinking: { type: "disabled" }` / `max_tokens` throttling depending on the gateway specification.
  2. Maintain a strict distinction in configuration: enable reasoning (`enable_thinking: true` or default) for deep analysis, verification, and code architecture audits; disable reasoning (`enable_thinking: false`) for low-latency interactive consumer experiences.

## Checklist for Background Worker Pipelines

- [ ] Adapter sets `max_tokens >= 8192` for reasoning model identifiers (`ds`, `r1`, `o1`).
- [ ] Fetch timeout configured to `>= 120000ms`.
- [ ] Explicit `stream: false` passed in POST payload.
- [ ] Suppress reasoning generation (`chat_template_kwargs: { enable_thinking: false }`) when latency is critical.
- [ ] Background worker handles long-running jobs gracefully with idempotency keys.
- [ ] Raw JSON response cleaned of SSE delimiters and markdown backticks before `JSON.parse`.
