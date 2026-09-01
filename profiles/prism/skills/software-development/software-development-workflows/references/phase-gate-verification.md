## Phase Gate Verification & Python Verification Probes

When executing multi-phase software implementation projects with automated verification scripts (e.g. `scripts/verify_phase0.py`):

## Gate Verification Best Practices
1. **Term Matching Integrity**: Ensure all required needles/terms in the verification script correspond exactly to existing text or update missing references in documentation artifacts before running the gate.
2. **Deterministic Assertions**: Verify required hashes, required file structures, and secret scans (`private_key_block`, `openai_style_secret`, `github_pat`).
3. **Commit Cleanliness**: Always stage and commit all modified files (including plan updates, build logs, and decision records) on the feature branch before marking a phase as complete.
4. **Transient Error Handling**: If verification fails due to string term mismatches or late build-log updates, update the relevant log entry/document directly to match the script's exact check terms rather than bypassing the script.
5. **Stream Interruption Recovery**: When output gets cut off mid-stream or interrupted by network errors, resume execution directly from the exact truncation point without repeating prior context.

## Python MCP & Upstream Constraints
- Pin transitive dependency limits explicitly (e.g. `mcp==1.29.0`) when fastmcp imports fail under unconstrained versions like `mcp>=2.0.0`.
- When mocking `httpx.AsyncClient` methods in `unittest.IsolatedAsyncioTestCase` with `unittest.mock.patch`, ensure synchronous response methods like `.json()` return `MagicMock()` or a standard dict rather than `AsyncMock` to prevent `'coroutine' object is not subscriptable` errors.

