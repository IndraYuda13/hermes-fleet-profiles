# Gate R0 Revision v7 Remediation Standards & Audit Guidelines

Authoritative standards for prediction market lab builds under Gate R0 Revision v7 (`HERMES_R0_REVISION_EXECUTION_PACKET_v7.md`).

## 1. Byte-Exact Authority & Trusted Governing Verification
- **Byte-Exact Packet Preservation:** Packet files installed at the repository root must remain byte-identical to the owner-supplied input artifact. SHA-256 checksums must match the owner-provided expected hash exactly without whitespace/line-ending normalization.
- **Immutable Hardcoded Hash Pinning:** `scripts/verify_governing_integrity.py` must hardcode immutable trusted document hashes in code (`TRUSTED_REQUIRED_DOCS`) and assert that (1) hardcoded hash == (2) manifest hash == (3) observed file hash. If manifest and document are jointly modified to tampered content, verification MUST fail.
- **Path & Collision Security:** Reject symlinked parent components, path traversals, case-insensitive path collisions independent of host OS, and duplicate paths prior to set insertion.

## 2. Strict Adapter Readiness & Model Defaults Removal
- **Required Readiness Flags:** `parse_market_payload()` must require an explicitly present, strict boolean readiness/orderbook-enabled field. Missing readiness must fail closed even if an `OrderBook()` object is passed.
- **No OrderBook Synthesis:** Real adapters must not manufacture `OrderBook()` objects from default boolean flags (`data.get("enableOrderBook", True)`). All orderbook data must be provided by a verified read-only orderbook provider/transport.
- **Required Model Attributes:** Pydantic models (`Market`) MUST NOT set default values for `active`, `closed`, or `orderbook_enabled`. Missing flags during model instantiation must raise validation errors.

## 3. Unique Canonical "Yes" Selection
- **Deterministic Outcome Mapping:** Binary market forecasting requires exactly one outcome whose case-folded string equals `"yes"`.
- **Zero & Multiple Rejection:** Zero matching `"yes"` outcomes or multiple matching `"yes"` outcomes (e.g. `["Yes", "yes"]`) MUST fail closed before price fetching or LLM execution.
- **No Index-Zero Fallback:** Never fall back to index 0 unless index 0 is explicitly proven to be the unique `"yes"` outcome.
- **Selected Identity Invariants:** `CanonicalMarketIdentity` must validate inside its constructor that `selected_outcome == outcomes[selected_index]` and `selected_token_id == clob_token_ids[selected_index]`.

## 4. Price Identity & Fallback Removal
- **Bound Price Reads:** `MarketPriceReader.fetch_market_price_bound()` must assert index range and selected outcome/token consistency prior to any read call.
- **Removal of Raw Price Methods:** Delete public `fetch_market_price(market_id)` methods or require full canonical mapping. Never invent token IDs (`f"tok_{market_id}"`), outcomes, or index zero.

## 5. Independent MCP Contract Pinning
- **Hardcoded Contract Hash:** Hardcode trusted contract SHA-256 (`a78adb07685e99738186de02f7a4fa8ed4460dbe63bb45e7cf42433d6254ccb2` for v1 contract) inside `scripts/verify_mcp_registry.py`.
- **Schema Tamper Protection:** Require candidate and contract to match exact allowlists (8 LLM tools, 13 runtime tools). Verify that allowlisted tool schemas contain NO secret, wallet, private key, signing, transfer, shell, database-admin, or filesystem parameters.

## 6. Active-Source AST Safety Scanner v7
- **Fail-Closed AST/TOML/JSON Parsing:** `scripts/verify_safety_inventory.py` must fail closed on syntax/parse errors across Python, TOML (`pyproject.toml`), JSON (`package.json`, allowlists), and YAML files (or report `YAML_PARSER_UNAVAILABLE` if no parser is present).
- **Secret & Dependency Detection:** Scan `from os import getenv`, `os.environ.get`, `settings.PRIVATE_KEY`, `requirements*.txt`, and live SDK dependencies (`py-clob-client`, `eth-account`, `web3`, `ethers`).

## 7. Semantic Test Catalog Verifier
- **AST Assertion Verification:** `scripts/verify_r0_test_catalog.py` must inspect test method ASTs and reject bodies whose sole content is assignment-only, call-only without assertions, tautologies (`assertEqual(1, 1)`, `assertTrue(True)`), or file text existence checks.
- **Parse Errors:** Parse errors in test files must fail catalog verification.

## 8. Process-Start Inherited Offline Guard
- **Process Deny Guard:** Implement `tests/offline_guard/sitecustomize.py` (or interpreter bootstrap via `PYTHONPATH`) patching `socket.connect`, `connect_ex`, `create_connection`, `getaddrinfo`, and `gethostbyname`.
- **Child Subprocess Inheritance:** All child Python interpreters spawned by tests inherit socket/DNS denial. Child test attempts MUST raise `OFFLINE_GUARD_DENIAL`.

## 9. Truthful Tree Differential & Evidence
- **Binary File Separation:** `scripts/check_tree_diff.py` must emit canonical JSON reporting added, modified, removed, and binary-changed files as distinct arrays.
- **Evidence Consistency:** `changed-files.txt`, `real-diff.patch`, `acceptance-matrix.md`, and command logs must be generated directly from tree-diff JSON output.
- **33 Mandatory Evidence Files:** Ensure `r0-v7-evidence/` contains all 33 required evidence files, hashed cleanly in `SHA256SUMS.txt`.
