---
name: prediction-market-research
description: "Research prediction markets (Polymarket): multi-agent forecasting, paper trading, deterministic risk gating, and lab verification runbooks."
version: 1.1.0
tags: [polymarket, prediction-markets, forecasting, multi-agent, paper-trading, risk-gate]
platforms: [linux, macos]
---

# Prediction Market Research & Paper Trading Laboratory

Systematic framework for prediction market research: multi-agent forecasting pipelines, logit-space probability aggregation, deterministic risk gating, paper-only execution, and verification/handoff discipline for lab builds.

## Architecture

```text
Polymarket Read API (Gamma) ──► Point-in-Time Evidence Store
                                           │
                                           ▼
                                 Multi-Agent Pipeline
                         (Blind ➔ Debate ➔ Red Team ➔ Synthesis)
                                           │
                                           ▼
                               Logit-Pool Aggregation
                                           │
                                           ▼
                                Deterministic Risk Gate
                                 (Hard Limits & Edge)
                                           │
                                           ▼
                             Paper Trader Execution (MCP)
```

## Always-On Rules

1. **Paper-only boundaries.** Enforce `PAPER_TRADING_ONLY=True` / `RUNTIME_MODE=RESEARCH_ONLY`; zero live wallet signing, private-key handling, or live order paths. LLMs MUST NOT hold trade-execution or risk-override authority — risk gating and execution controls are deterministic rules outside LLM reasoning.
2. **Fail closed, never synthesize.** No `0.5` fallbacks anywhere: not in forecasts, not in market price reads (`prob=null` on missing data), not in aggregation (empty/sub-quorum input returns `valid=False` with `final_probability=None`). Missing, malformed, or out-of-bounds upstream fields abort the flow; they never default.
3. **Bind market identity before any LLM call.** Require requested `market_id` == returned `market.id` == `priced_id`, plus `active=True`, `closed=False`, `orderbook_enabled=True` with a real orderbook. Binary markets need exactly one case-insensitive `"Yes"` outcome; derive selection from that unique match — never index 0, never fabricated token IDs (`f"tok_{market_id}"`).
4. **Strict direction semantics.** BUY requires `forecast > proposed + min_edge`, SELL the strict reverse; boundary equality is an explicit rejection (`WRONG_DIRECTION_BUY` / `WRONG_DIRECTION_SELL`), never a pass.
5. **Safe-parse Gamma's stringified JSON.** `outcomes`, `clobTokenIds`, and `outcomePrices` often arrive as `'["Long", "Short"]'` strings — `json.loads` them before building Pydantic list models. Booleans must be strict (`isinstance(val, bool)`); never coerce `"false"` by truthiness.
6. **Strict LLM output envelopes.** Accept a raw JSON object or exactly one fenced code block with no surrounding prose; reject multiple blocks, malformed fences, and regex extraction from general prose. Allow at most one format-correction retry, then fail closed with a structured error payload and sanitized diagnostics — never proceed to aggregation or the Risk Gate on a final failure.
7. **Redact secrets from every log** (`API_KEY`, `Authorization`, `Bearer`, environment secrets) before persistence or SSE emission.
8. **Handoff bundles are untrusted until verified.** Verify SHA256 checksums against physical files and check ZIP entry paths programmatically (`zipfile`, not `unzip -t`) for traversal/backslash/NUL/symlink tricks before reading. Never invent explanations for hash mismatches — record honestly when root cause is unknowable from retained evidence. Do not run `git init` on `.git`-less repos without owner permission. Full protocol: `references/handoff-and-remediation.md`.

## Multi-Agent Pipeline

- **Roles:** `BASE_RATE_ANALYST`, `SUPERFORECASTER`, `RED_TEAM_CRITIC`, `DOMAIN_EXPERT`, `SYNTHESIS_EDITOR` — assign a distinct backend per role (matrix in `references/9router-multi-model.md`).
- **Stages:** `BLIND_ROUND` ➔ `EVIDENCE_EXCHANGE` ➔ `SPARSE_DEBATE` ➔ `RED_TEAM_CRITIQUE` ➔ `PRIVATE_REVISION` ➔ `SYNTHESIS`.
- Run independent stages concurrently (`asyncio.gather` for Base Rate + Domain Expert) to cut sequential latency; explicitly allow agents to abstain when data is insufficient.
- **9Router gateway:** `http://localhost:20128/v1`, default opaque alias `ag-opus-pool`. Critical/scored calls send `X-9Router-Token-Saver: off` and disable prompt modifiers (PXPIPE, Caveman, Ponytail) to keep strict schema adherence and route-fingerprint logging.
- Stream pipeline progress via FastAPI `StreamingResponse` (`text/event-stream`) consumed by a React `ReadableStream`; persist structured execution logs (`timestamp`, `market_id`, `level`, `message`) and expose them via `/api/logs` for audit.

## Logit-Pool Aggregation

$$L(p) = \ln\left(\frac{p}{1-p}\right), \quad p = \frac{1}{1 + e^{-L}}$$

Transform to logit space to avoid boundary compression, drop outlier probabilities with `trimmed_mean`, then back-transform the mean logit into the consensus probability.

## Deterministic Risk Gate & Paper Execution

Risk Gate rejection codes: `PAPER_ONLY_VIOLATION` (any live-trade flag), `MAX_POSITION_EXCEEDED` (over fixed budget), `MIN_EDGE_NOT_MET` (`|p_forecast - p_market| < min_edge`).

Paper execution authorization (Operator v1 pattern):
- Risk Gate issues an HMAC-signed capability token carrying `decision_id`, `reservation_id`, `proposal_hash`, `market_id`, `side`, `spend_usd`, `price`, `token_id`, and a 5-minute TTL.
- Portfolio cash is reserved atomically before fill; failed fills do NOT consume reservations or change portfolio state.
- Manual approval gate: even when risk rules pass, paper execution requires an authenticated `POST /api/runs/{run_id}/approve-paper` with `X-PML-API-Key` and an `idempotency_key` in the body.
- Idempotent replay: the same `idempotency_key` returns the identical execution report with the same `execution_hash`; expired tokens are rejected.

## Evaluation & Calibration Metrics

- **Brier Score:** $(p - o)^2$ where outcome $o \in \{0, 1\}$.
- **Binary Log Loss:** $-[o \ln(p) + (1-o) \ln(1-p)]$ with $10^{-4}$ clamping to prevent infinities.

## References

- `references/handoff-and-remediation.md` — handoff/remediation protocol: ZIP path-safety checks, hash verification, authority hierarchy (root `AGENTS.md` + master spec over legacy zip specs), gate sequence, review-evidence packaging checklists.
- `references/r0-v5-remediation-standards.md` — AST-based safety scanner pattern, canonical JSON matching for MCP contracts, machine-verifiable test catalogs.
- `references/r0-v6-remediation-standards.md` — strict adapter payload parsing, canonical market identity, MCP allowlist pinning, fail-closed scanners, offline deny guard, tree diffs.
- `references/r0-v7-remediation-standards.md` — byte-exact packet preservation, hardcoded hash pinning, unique-"Yes" selection, semantic test-catalog verification, inherited offline guard, 33-evidence-file consistency.
- `references/operator-v1-verification.md` — RC1 release verification runbook: checksum, install, release verifier (8 checks / 54 tests), 9Router smoke tests, API endpoint table, tunnel setup; pitfalls (port 8000 conflicts, SSE is POST-only, capability secret length, multiple cloudflared configs).
- `references/operator-v1-deployment.md` — Cloudflare Tunnel deployment: CORS config, loopback binding, port conflicts, systemd unit template.
- `references/operator-v2-beta1-verification.md` — v2 Beta 1 runtime verification: execution gateway dry-run (`LIVE_CONFIRM`), FastAPI lifespan migration, paper auto simulation flows.
- `references/operator-v2-beta2-verification.md` — v2 Beta 2 runbook: structured `LIVE_*` error codes, 5 test environments, CLOB-vs-Gamma ID matching pitfall, paper audit event types, read-only account onboarding.
- `references/9router-format-normalization-and-retry.md` — transport-envelope normalization rules, single-fence validation, 1-retry format-correction protocol, fail-closed SSE error schemas, `ParseFailureDiagnostic` logging, secret redaction.
- `references/9router-multi-model.md` — role→model assignment matrix, SSE `data:` delta parsing, concurrent stage execution pattern.
- `references/prediction-market-lab.md` — local lab architecture and endpoints (FastAPI 8005, Vite 3000, PostgreSQL 16, 9Router 20128), Gamma schema quirks, Vite `allowedHosts` fix.

## Cross-Cutting Pitfalls

- **FastAPI lifespan:** newer FastAPI (0.110+) drops `add_event_handler("startup")` on wrapped apps (`AttributeError` in tests) — migrate to a `@contextlib.asynccontextmanager` lifespan hook in `create_app()`, or fall back to `@app.on_event("startup")`. Install `httpx` (plus `httpx2` where the test framework requires it) for Starlette TestClient runs.
- **Vite behind Cloudflare Tunnel:** set `server: { allowedHosts: true }` in `vite.config.ts` (untrusted Host headers otherwise 403) and bind dev servers to loopback.
- **CLOB vs Gamma IDs:** the CLOB `/book` endpoint returns `market` as the 0x-prefixed condition hash while Gamma uses numeric string IDs — match against `condition_id`/`asset_id`, never raw ID string equality.
