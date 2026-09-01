# Prediction Market Handoff & Remediation Protocol

Protocol guidelines for inspecting, auditing, and executing multi-gate remediation for prediction market research monorepos (`prediction-market-lab`).

## 1. Safety & Verification Checklist
1. Extract ZIP archives into isolated, uniquely named temporary staging directories (`/tmp/handoff_inspect_XXXXXX`).
2. **ZIP Path Safety Inspection:** `unzip -t` is insufficient for path safety verification. Always inspect entry paths programmatically using Python `zipfile` to check for:
   - Absolute paths (`n.startswith('/')` or `n[1] == ':'`)
   - Path traversal (`../` or `..\`)
   - Backslash escapes (`\`)
   - NUL bytes (`\x00`)
   - Duplicate entries or unexpected symbolic links (`(external_attr >> 16) & 0o120000 == 0o120000`)
3. Run `sha256sum -c SHA256SUMS.txt` to verify all bundle files against physical files.
4. **Hash Reporting Discipline:** Never guess or manufacture explanations for hash mismatches without physical evidence. If exact cause cannot be established, record honestly: *"Previous hash values were a reporting error; exact root cause cannot be established from retained evidence."*
5. **Git Provenance Rule:** If the source archive lacks `.git` metadata, do NOT run `git init` or create manufactured Git provenance without explicit owner authorization.
6. Validate authority hierarchy:
   - Root `AGENTS.md` and `HERMES_MASTER_BUILD_SPEC_v1.1.md` supersede legacy zip specs.
   - Candidate commit pins (e.g. Vibe-Trading `bec189f...` and Paper Trader `ed601ed...`) are legacy candidate pins to re-verify, NOT verified current truth.
   - Audit documents (`PREDICTION_MARKET_LAB_FULL_AUDIT_2026-08-03.md`) provide forensic ground truth on implementation gaps.

## 2. Mandatory Gate Sequence
- **Gate A / Prompt 1 (Read-Only):** Verify hashes, explain builder role, state product understanding, report true code maturity, list critical defects, map 16 invariants & 13 slice requirements, present R0 plan, confirm zero files modified, and STOP.
- **Gate R0 (Truth Reset & Quarantine):** Move legacy spec to `docs/legacy/`, set `RUNTIME_MODE=RESEARCH_ONLY`, quarantine `PaperTraderAdapter` mutations to throw `PaperExecutionUnavailable`, disable `/analyze` trade approval, bind Vite/API to `127.0.0.1`, write ADRs 0005-0007 & Threat Model / 30-tool manifest, and run R0 regression suite.
- **Gate R0 Revision v3 & v4 (Complete Fail-Closed Endpoint Wiring & Deterministic Validation):**
  - Wire strict JSON probability envelope parser (`ForecastProbabilityEnvelope`) directly into the production `/analyze` endpoint; reject prose, decimals in prose, surrounding prose, malformed JSON, and extra fields with zero downstream calls.
  - Enforce full market availability in `validate_minimum_identity()` (`active=True`, `closed=False`, `orderbook_enabled=True`, `orderbook is not None`) before any LLM gateway calls.
  - Implement explicit `MarketPriceReader` abstraction that fails closed on missing, malformed, empty, mismatched, or out-of-bounds prices; NEVER fall back to synthetic `0.5` market price.
  - Eliminate all synthetic `0.5` default parameters from models (`ForecastDraft`, `SynthesisReport`) and orchestrators (`MultiAgentOrchestrator.synthesize()` raises `ValueError` on empty active drafts).
  - Enforce strict BUY/SELL direction inequalities (`>` for BUY, `<` for SELL) where exact threshold equality is explicitly rejected (`WRONG_DIRECTION_BUY` / `WRONG_DIRECTION_SELL`).
  - Integrate real bounded `DatabaseProbe` abstraction into `/health` (executing SQL `SELECT 1` with 1.0s timeout) and handle connection edge cases / unsupported query interfaces safely.
  - Build machine-readable governing manifest (`config/governing_integrity_v4.json`) and CLI verifier that rejects missing/truncated/tampered files, traversal paths (`../`), absolute paths, and symlinks.
  - Build trusted MCP contract (`config/paper_trader_mcp_contract_v1.json`) and canonical structural validator (`scripts/verify_mcp_registry.py`) that performs normalized JSON comparison and enforces allowlist safety boundaries (`FORBIDDEN_LLM_POLICIES`).
  - Build active-source safety scanner (`scripts/verify_safety_inventory.py`) with comprehensive regexes and adversarial test fixtures.
  - Enforce `PYTHONDONTWRITEBYTECODE=1` during test execution and review ZIP packaging (0 `.pyc` / `__pycache__` entries) and generate a detached `.zip.sha256` sidecar file beside the review ZIP.
  - Add an offline unmocked network guard test (`test_offline_unmocked_network_guard`) ensuring tests execute 100% offline.
- **Gates R1-R6:** Progressive foundation, typed contracts (RFC 8785 canonical JSON hashing & Decimal precision), 9Router clean profile, blind 3-forecaster slice, logit pool `cold_start_logit_v1`, and audited MCP execution.
- **Gate R7 (Reconciliation, Baseline Eval & Honest Dashboard):** PostgreSQL/Paper Trader reconciliation, prospective Brier evaluation against market baselines, partial/50-50/invalid resolution policy, and transparent UI.
- **Gate R8 (Complete Adversarial Vertical-Slice Acceptance):** Full adversarial acceptance test suite across ALL 13 vertical-slice requirement areas (not just penetration testing).

## 3. Strict Audit Failures & R0 Mandatory Regression Tests
- **Naked Sell:** Selling tokens without position ownership crediting cash.
- **Fail-Open Fallback:** Converting LLM errors into `0.5` probabilities. Require strict probability parser (`parse_llm_probability_strict`) that fails closed on free-form text or non-envelope JSON.
- **Quorum Fail-Closed:** Aggregation on empty or sub-quorum inputs MUST return invalid result with `None` probability, never synthetic `0.5`.
- **Identity Check Pre-LLM:** Missing ID, question, condition ID, or mismatched outcome-token mappings MUST block execution before calling LLM gateways.
- **Risk Gate Direction & Side:** Calculating margin/edge incorrectly for SELL positions. `WRONG_DIRECTION_BUY` and `WRONG_DIRECTION_SELL` must return explicit rejection codes. Pydantic schema validation must reject unconstrained or invalid `side` strings.
- **Governing Document Integrity:** Suite must verify `AGENTS.md`, `HERMES_MASTER_BUILD_SPEC_v1.1.md`, and execution packet hashes and exit nonzero on missing/truncation/drift using dynamic subprocess fixtures.
- **MCP Registry & Tool Drift:** Machine-readable 30-tool JSON validator must exit nonzero on missing, extra, renamed, duplicate, or schema-drifted tools using dynamic subprocess fixtures.
- **Active-Source Safety Scan:** Validator must verify active source files contain zero live-money SDKs, wallet keys, signing, funding, geobypass, or LLM-controlled mutation tools.
- **Superseded Claims:** Legacy implementation plan and build log must be visibly marked as SUPERSEDED.

## 4. Remediation Review Artifact Packaging (`prediction-market-lab-r0-revision-review.zip`)
When creating a handoff/review ZIP artifact for owner audit:
1. Exclude heavy or sensitive directories: `.git/`, `.env`, secrets/credentials, `node_modules/`, Python `__pycache__`, virtual environments (`.venv`), database files (`*.db`), logs, and temporary staging files.
2. Include a comprehensive evidence directory (e.g. `r0-revision-evidence/`) containing all required evidence files:
   - `input-artifact-verification.txt`: Input ZIP SHA-256, size, and path safety check results.
   - `provenance-before.txt`: Working directory, timestamp, OS, Python version, Git status (or UNAVAILABLE if unrecorded).
   - `provenance-after.txt`: Final working directory state and Git status.
   - `governing-integrity.txt`: Governing file hashes and CLI verification output.
   - `baseline-tests.txt`: Pre-edit test and compileall outputs.
   - `diff-stat.txt`: Output of `git diff --stat`.
   - `diff-check.txt`: Output of `git diff --check`.
   - `r0.patch` / `tracked.patch`: Clean patch without secrets.
   - `environment.txt`: Runtime, Python version, available dependencies, and factual explanation of test import paths.
   - `unittest-verbose.txt`: Full verbose unittest runner output (`python3 -m unittest discover -s tests -p "test_*.py" -v`).
   - `pytest.txt`: Output of pytest or `PYTEST_UNAVAILABLE`.
   - `compileall.txt`: Python bytecode compilation output across code tree.
   - `governing-negative-tests.txt`: Subprocess test results for missing/truncated/tampered governing files.
   - `mcp-registry-negative-tests.txt`: Subprocess test results for MCP tool drift / missing / extra / schema drift.
   - `r0-adversarial-tests.txt`: Adversarial test suite output.
   - `changed-files.txt`: Complete list of modified and added files.
   - `commands.jsonl`: Machine-readable log of all executed commands and exit codes.
   - `acceptance-matrix.md`: Every gate requirement mapped to named tests/artifacts and PASS/FAIL status.
   - `skipped-unavailable-tests.md`: List of skipped/uncollected tests and exact reasons.
   - `remaining-blockers.md`: Comprehensive list of all technical/architectural blockers remaining after the gate.
   - `SHA256SUMS.txt`: Checksum manifest for all evidence files.
3. Provide the SHA-256 hash and byte size of the generated ZIP artifact and pause for owner review.

