---
name: prediction-market-research
description: "Use for prediction market research & multi-agent labs."
version: 1.0.0
tags: [polymarket, prediction-markets, forecasting, multi-agent, paper-trading, risk-gate]
platforms: [linux, macos]
---

# Prediction Market Research & Paper Trading Laboratory

Systematic framework and architectural patterns for prediction market research, multi-agent forecasting, logit-space probability aggregation, deterministic risk gating, and paper-trading evaluation.

## Core Architectural Architecture

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

## Key Guidelines & Safeguards

### 1. Hard Paper-Only Boundaries & Security Governance
- Always enforce strict paper-only execution bounds (`PAPER_TRADING_ONLY=True` / `RUNTIME_MODE=RESEARCH_ONLY`).
- Zero live wallet signing, private key requests, or live order execution paths.
- **LLM Mutation Isolation:** LLMs MUST NOT hold trade execution or risk override authority. Risk Gate and execution controls must be deterministic rules outside LLM reasoning.
- **Handoff & Audit Verification:** When resuming or remediating prediction market lab builds from handoff bundles:
  - Verify SHA256 checksums (`SHA256SUMS.txt`) against physical files before reading. Programmatically verify ZIP path safety (absolute paths, `../` traversal, backslashes, NUL bytes, symlinks) via Python `zipfile`.
  - Never guess or manufacture explanations for hash mismatches without physical evidence. If exact root cause cannot be established from retained evidence, record honestly as a reporting error.
  - Require strict multi-gate authorization (Read-only Gate A -> R0 Truth Reset -> R1 Foundation -> R2 Contracts -> R3 9Router -> R4 3-Forecaster Slice -> R5 Aggregation/Risk -> R6 MCP Execution -> R7 Baseline Eval & Reconciliation -> R8 Complete Adversarial Slice Acceptance across all 13 areas).
  - Treat embedded ZIP specifications as non-authoritative historical artifacts; bundle root `AGENTS.md` and `HERMES_MASTER_BUILD_SPEC_v1.1.md` form current authority. Treat upstream commit hashes as legacy candidate pins to re-verify. Do not run `git init` on repos lacking `.git` without explicit owner permission.
  - When compiling review artifacts (like `r0-review.zip`), ensure complete verification evidence (`r0-evidence/`) is included with `provenance.txt`, `diff-stat.txt`, `diff-check.txt`, `r0.patch`, `environment.txt`, `unittest-verbose.txt`, `pytest.txt` (or `PYTEST_UNAVAILABLE`), `compileall.txt`, `r0-negative-tests.txt`, `skipped-tests.txt`, `remaining-blockers.md`, and `SHA256SUMS.txt`. Exclude `.git/`, secrets, `node_modules/`, `__pycache__`, and virtual environments. Report test status accurately without converting failures to passing claims.
- **Execution Gateway API Quirks:** When dealing with newer `FastAPI` (0.110+), `add_event_handler("startup")` might be deprecated or removed depending on internal app wrapping, causing `AttributeError` in tests. Either fallback to standard `@app.on_event("startup")` / `"shutdown"` or properly transition the root `main.py` entrypoint to a `lifespan` hook using `@contextlib.asynccontextmanager`. When transitioning tests with `starlette.testclient`, ensure `httpx` (and `httpx2` if required by the test framework version) are installed to prevent DeprecationWarning failures.
- **Gamma API Quirks:** Fields like `outcomes`, `clobTokenIds`, and `outcomePrices` returned from Gamma API endpoints often arrive as stringified JSON strings (e.g. `'["Long", "Short"]'`). Always safe-parse stringified JSON before instantiating Pydantic list models (`isinstance(val, str)` -> `json.loads(val)`).
- **9Router Critical Profile:** Endpoint `http://localhost:20128/v1` with opaque alias `ag-opus-pool`. Critical and scored calls require sending `X-9Router-Token-Saver: off` and disabling prompt modifiers (PXPIPE, Caveman, Ponytail) to ensure strict schema adherence and route fingerprint logging.
- **Real-Time Progress Streaming (SSE):** Use FastAPI `StreamingResponse` with `text/event-stream` and React `ReadableStream` reader to stream pipeline progress (`percent`, `step`) and completion payloads to the UI.
- **Execution Logging & Auditing:** Record structured execution logs (`timestamp`, `market_id`, `level`, `message`) in memory/DB and expose via `/api/logs` for auditability.
- **Frontend Reverse Proxy & Vite `allowedHosts`:** When routing Vite dev server through Cloudflare Tunnel, set `allowedHosts: true` in `vite.config.ts` to prevent 403 Forbidden Host Header errors. Bind dev server to loopback (`127.0.0.1`) by default for security. Also configure Vite proxy (`/api` -> `http://127.0.0.1:8005`) for seamless frontend-backend communication.
- **Dynamic Prompt & Endpoint Probability Parsing:** Production endpoints MUST use strict typed JSON envelope validation (`ForecastProbabilityEnvelope` requiring `{"probability": 0.5}`) and safe transport-envelope normalization (`normalize_transport_envelope`) that handles bare raw JSON or exactly one Markdown code block (` ```json ... ``` ` or ` ``` ... ``` `). Fenced blocks with leading/trailing prose, multiple code blocks, unclosed fences, or extra/out-of-range fields MUST be rejected. Support a maximum of one format-correction retry (asking for raw JSON object only) before failing closed with a structured SSE error payload (`{"code": "LLM_OUTPUT_FORMAT_INVALID", "stage": "multi_agent_forecasting", "agent_role": "<role>", "attempts": 2}`) and recording sanitized diagnostic artifacts (`ParseFailureDiagnostic`). Never generate synthetic `0.5` fallback forecasts or proceed to downstream aggregation/Risk Gate on final failure.
- **Fail-Closed Quorum, Identity & Availability Checks:** Enforce canonical identity and availability checks (`validate_minimum_identity()` checking requested `path_id` == returned `market.id` == `priced_id`, `active=True`, `closed=False`, `orderbook_enabled=True`, `orderbook is not None`) before calling LLM gateways or price readers. Require strict minimum quorum for aggregation (`min_quorum=4`); empty/invalid forecast sets MUST return `valid=False` and `final_probability=None` rather than generating synthetic prior values.
- **Explicit Fail-Closed Market Price Reads:** Use explicit price readers (`MarketPriceReader`) that fail closed on missing/mismatched/out-of-bounds prices instead of defaulting to `0.5` anywhere in the API (including `GET /api/markets` where `prob` must be `null` on missing data).
- **Strict Direction & Boundary Semantics:** Proposal direction validation MUST enforce strict inequalities (`forecast > proposed + min_edge` for BUY; `forecast < proposed - min_edge` for SELL). Boundary exact equalities must be explicitly rejected (`WRONG_DIRECTION_BUY` / `WRONG_DIRECTION_SELL`).
- **Two-Tree Baseline Differential, Machine-Verifiable Test Catalog & Clean Review Bundles:** When producing review ZIPs for no-`.git` source trees:
  - Generate deterministic evidence via two-tree directory hash comparison (`diff -urN`).
  - Enforce machine-verifiable test catalogs (`r0_v6_required_tests.json` & `verify_r0_test_catalog.py`) ensuring all required distinct named tests exist without grouping, duplication, or pass-only/tautological placeholders (`pass`, `...`, `assertTrue(True)`).
  - Parse Python AST, JSON, and TOML in active-source safety inventory scanners (`verify_safety_inventory.py`) to detect forbidden live-money SDKs, private keys, signing, or mutation tools, failing closed on any parse/syntax errors.
  - Enforce strict JSON envelope parsing requiring bare JSON (`{"probability": 0.5}`) and rejecting fenced Markdown JSON (```).
  - Bind requested path `market_id`, returned `market.id`, and `priced_id` canonically before LLM invocation.
  - Enforce strict adapter payload parsing (`parse_market_payload`) without synthesizing missing IDs, outcomes, active/closed flags, or orderbook readiness.
  - Bind `CanonicalMarketIdentity` with unique `"Yes"` outcome selection, enforcing exact order and element matching for outcomes/tokens in `MarketPriceReader` (rejecting reordered or substituted same-length arrays).
  - Independent MCP Contract Pinning: Hardcode trusted contract SHA-256 in `verify_mcp_registry.py` and enforce exact allowlist tool schema integrity (rejecting secret/wallet/shell parameters on allowlisted tools).
  - Semantic Test Catalog Verifier: Inspect test ASTs to reject assignment-only, call-only, tautological (`assertTrue(True)`), or text-existence tests.
  - Process-Start Inherited Offline Guard: Use `sitecustomize.py` / `PYTHONPATH` to enforce socket and DNS denial (`OFFLINE_GUARD_DENIAL`) inherited across child Python subprocesses.
  - Tree Diff & Evidence Consistency: Separate binary changed files in `check_tree_diff.py` JSON and generate all 33 evidence files consistently.

### Supporting Reference Files
- `references/operator-v2-beta2-verification.md` — Operator v2 Beta 2 Live Research & Readiness runbook: structured error codes, 5 environment specs, paper policy audit wording, and read-only account onboarding.
- `references/operator-v2-beta1-verification.md` — Operator v2 Beta 1 runtime verification: execution gateway dry-run, FastAPI lifespan pitfalls, and paper auto simulation flows.
- `references/r0-v6-remediation-standards.md` — Detailed audit standards and implementation patterns for Gate R0 Revision v6.
- `references/r0-v7-remediation-standards.md` — Authoritative audit standards, trusted hash enforcement, and offline inheritance patterns for Gate R0 Revision v7.
- `references/operator-v1-verification.md` — Operator v1 RC1 runtime verification runbook: checksum, install, release verifier (8 checks / 54 tests), API smoke, SSE events, paper simulation flow with idempotent replay. Includes pitfalls (port 8000 conflicts, SSE is POST-only).
- `references/operator-v1-deployment.md` — Cloudflare Tunnel deployment: CORS config, loopback binding, port conflicts, systemd unit template. Live at prediction-lab.indrayuda.my.id.
- `references/9router-format-normalization-and-retry.md` — 9Router transport envelope normalization, single-fence validation rules, 1-attempt format correction retry protocol, fail-closed SSE error schemas, and sanitized diagnostic artifact logging.

### 2. Multi-Agent Debate & Forecasting Pipeline
- **Role Specialization:** Separate forecaster personas (`BASE_RATE_ANALYST`, `SUPERFORECASTER`, `RED_TEAM_CRITIC`, `DOMAIN_EXPERT`, `SYNTHESIS_EDITOR`). Assign distinct 9Router backends per role (e.g., Gemini 3.6, Gemini Pro, Grok 4, Claude Sonnet 4.6).
- **Parallel Sub-agent Execution:** Execute independent agent stages concurrently (e.g. `asyncio.gather` for Base Rate + Domain Expert) to prevent sequential latency bottlenecks.
- **Sequential Stages:** `BLIND_ROUND` ➔ `EVIDENCE_EXCHANGE` ➔ `SPARSE_DEBATE` ➔ `RED_TEAM_CRITIQUE` ➔ `PRIVATE_REVISION` ➔ `SYNTHESIS`.
- **Abstention Support:** Explicitly allow agents to abstain when data is insufficient.

### 3. Logit-Pool Probability Aggregation
- Transform probabilities to logit space to avoid boundary compression:
  $$L(p) = \ln\left(\frac{p}{1-p}\right), \quad p = \frac{1}{1 + e^{-L}}$$
- Apply `trimmed_mean` to drop extreme outlier probabilities.
- Re-convert average logit back to probability space for final consensus forecast.

### 4. Deterministic Risk Gate
- Trade validation MUST be rule-based and outside LLM authority.
- Enforce explicit rejection codes:
  - `PAPER_ONLY_VIOLATION`: Rejects any live trade flag.
  - `MAX_POSITION_EXCEEDED`: Rejects trade sizes above fixed budget.
  - `MIN_EDGE_NOT_MET`: Rejects trades where $|p_{\text{forecast}} - p_{\text{market}}| < \text{min\_edge}$.

### 5. Paper Execution Authorization Flow (Operator v1)
- **Capability Token:** Risk Gate issues a hex-encoded JSON payload with HMAC signature. Contains `decision_id`, `reservation_id`, `proposal_hash`, `market_id`, `side`, `spend_usd`, `price`, `token_id`, `expires_at`.
- **Reservation System:** Portfolio cash is reserved atomically before fill. Failed fills do NOT consume reservations or change portfolio state.
- **Manual Approval Gate:** Even when risk rules pass, paper execution requires an authenticated POST to `/api/runs/{run_id}/approve-paper` with `X-PML-API-Key` header and `idempotency_key` in body.
- **Idempotent Replay:** Same `idempotency_key` returns identical execution report with same `execution_hash`. Portfolio revision does not increment on replay.
- **CSRF/Nonce Protection:** Idempotency keys prevent duplicate fills. Expired capability tokens (5-minute TTL) are rejected.

### 6. Evaluation & Calibration Metrics
- **Brier Score:** $(p - o)^2$ where outcome $o \in \{0, 1\}$.
- **Binary Log Loss:** $-[o \ln(p) + (1-o) \ln(1-p)]$ with $\epsilon$-clamping ($10^{-4}$) to prevent infinities.
