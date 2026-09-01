# Remediation Gate R0 Revision v6 Standards

Strict standards and implementation patterns for Gate R0 Revision v6 remediation.

## 1. Strict Upstream Adapter Payload Parsing (`parse_market_payload`)
- Fail closed if any upstream critical field is missing, malformed, or ambiguous (`id`, `conditionId`, `question`, `outcomes`, `clobTokenIds`, `active`, `closed`, `enableOrderBook`).
- NEVER synthesize default values for requested ID, `["Yes", "No"]`, `active=True`, `closed=False`, or `orderbook_enabled=True`.
- Booleans MUST be strict booleans (`isinstance(val, bool)`). String values like `"false"` must NOT be coerced by truthiness.

## 2. Canonical Market Identity & Outcome Selection (`get_canonical_identity`)
- Create an immutable `CanonicalMarketIdentity` model carrying `market_id`, `condition_id`, `outcomes`, `clob_token_ids`, `selected_index`, `selected_outcome`, and `selected_token_id`.
- Require a unique, case-insensitive `"Yes"` outcome in binary markets. Derive `selected_index`, `selected_outcome`, and `selected_token_id` deterministically from that unique match.
- Fail closed if a unique `"Yes"` outcome cannot be established.
- Eliminate raw string token fallbacks like `f"tok_{market_id}"` across all proposals and persisted runs.

## 3. Exact Outcome/Token/Price Identity Matching (`fetch_market_price_bound`)
- `MarketPriceReader` MUST accept `CanonicalMarketIdentity` objects rather than unverified raw string market IDs.
- Validate that the response market ID, outcome array, and token ID array match the canonical identity EXACTLY in both length and element order.
- Reject reordered or substituted outcome/token arrays even when total array length is identical.
- Extract price strictly at `selected_index`. Fail closed on missing, out-of-range, NaN, or infinite values.

## 4. Independent MCP Allowlist Pinning & Policy Verification
- Verifiers (`verify_mcp_registry.py`) MUST independently pin exact required R0 tool allowlists (8 LLM tools, 13 normal runtime tools) rather than blindly trusting allowlists in candidate or contract JSON files.
- Reject empty allowlists, allowlist subsets, allowlist supersets, or any mutation/admin/resolution tools in runtime allowlists.

## 5. Fail-Closed AST & Structured Safety Scanner (`verify_safety_inventory.py`)
- Python files MUST be parsed via `ast.parse()`. Detect `eth_account.Account.from_key` / `from_mnemonic`, env key access (`os.getenv("PRIVATE_KEY")`, `os.environ["ETH_PRIVATE_KEY"]`), and live CLOB imports (`py_clob_client`).
- Parse JSON allowlists and TOML manifests (`pyproject.toml`, `package.json`).
- If AST, JSON, or TOML parsing fails due to syntax errors, the scanner MUST fail closed (`SAFETY_FAIL_CLOSED`).

## 6. Real Behavioral Test Catalog Verification (`verify_r0_test_catalog.py`)
- Test catalog verifier MUST inspect AST function bodies (`is_placeholder_body`) to ensure every required test method contains real behavioral assertions.
- Reject placeholder bodies containing only `pass`, `...`, unconditional `return`, `self.assertTrue(True)`, or docstrings alone.

## 7. Process-Wide Inherited Offline Network Deny Guard (`run_unittest_offline.py`)
- Test runner MUST install a process-wide socket/DNS deny guard (`socket.socket`, `socket.getaddrinfo`, `socket.gethostbyname`) blocking outbound non-loopback connections.
- Run an active canary (`run_offline_canary()`) asserting external DNS queries or IP connections raise `OFFLINE_GUARD_DENIAL`.
- Pass environment flag `R0_OFFLINE_GUARD=1` to child Python subprocesses to ensure inherited deny behavior.

## 8. Deterministic Tree Diff & Whitespace Checker (`check_tree_diff.py`)
- Compute recursive SHA-256 baseline vs working tree differentials (`added`, `modified`, `removed`).
- Scan modified text files for trailing whitespace and git conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).
- Exit 0 only when diff check completes cleanly without formatting or conflict issues.
