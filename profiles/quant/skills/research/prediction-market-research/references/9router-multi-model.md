# 9Router SSE & Multi-Model Execution Reference

## 9Router SSE Streaming Behavior
When completing chat completions via 9Router (`http://localhost:20128/v1/chat/completions`), responses may arrive formatted as Server-Sent Events (`data: {...}`).

- Client `httpx` parsing must handle `data: ` line deltas instead of strictly expecting a single JSON object.
- Parse `delta.content` chunks and assemble final text string.

## Multi-Model Assignment Matrix

| Role | Model Backend | Rationale |
|---|---|---|
| Base Rate Analyst | `ag-opus-pool` (Gemini 3.6 Flash) | High throughput historical reference analysis |
| Domain Expert | `ag/gemini-3-flash-agent` | Fast domain mechanics evaluation |
| Red Team Critic | `ag/gemini-pro-agent` | Critical reasoning & hypothesis attack |
| Synthesis Editor / Superforecaster | `ag/claude-sonnet-4-6` | High-order synthesis & final calibration |

## Concurrent Stage Execution Pattern
Use `asyncio.gather` for non-dependent agent calls to reduce latency:

```python
base_task = call_agent(base_prompt, ROLE_MODELS[AgentRole.BASE_RATE_ANALYST])
domain_task = call_agent(domain_prompt, ROLE_MODELS[AgentRole.DOMAIN_EXPERT])
base_res, domain_res = await asyncio.gather(base_task, domain_task, return_exceptions=True)
```
