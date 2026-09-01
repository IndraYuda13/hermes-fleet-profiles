# Remediation Gate R0 Revision v5 Learnings & Specifications

## AST-Based Active Source Safety Scanner Pattern
When auditing repositories for forbidden live-money SDKs, wallet creation, or secret key leakage:
- Prefer Python `ast` module over line-by-line regex.
- Parse `ast.Import`, `ast.ImportFrom`, `ast.Call` (e.g. `os.getenv('PRIVATE_KEY')`), and `ast.Assign` to identify active execution leaks without false positives from historical markdown docs or strings.
- Parse `pyproject.toml` using `tomllib` and `package.json` using `json` to verify no prohibited live trading libraries are declared as active dependencies.

## Strict MCP Registry & Contract Canonical Matching
- Create an independent trusted contract (`paper_trader_mcp_contract_v1.json`) containing explicit `llm_tool_allowlist` and `normal_runtime_allowlist`.
- Canonicalize JSON objects by dumping with `sort_keys=True` and `separators=(',', ':')` to detect subtle schema or property drift regardless of whitespace or ordering.
- Disallow any tool with policy `execution_mutation`, `resolution_worker_only`, `offline_admin_only`, or `prohibited_from_runtime` from entering the `llm_tool_allowlist`.

## Machine-Verifiable Test Catalog Pattern
- Maintain `config/r0_v5_required_tests.json` declaring exact required test method names.
- Provide a CLI verifier (`scripts/verify_r0_test_catalog.py`) that parses Python test files using `ast` to ensure all mandatory tests are present as distinct, un-duplicated test methods.
