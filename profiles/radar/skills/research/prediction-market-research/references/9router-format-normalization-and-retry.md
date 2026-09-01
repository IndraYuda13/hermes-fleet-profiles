# 9Router Format Normalization, Format-Correction Retry & Diagnostic Standards

When integrating 9Router OpenAI-compatible `/v1` endpoints (`http://127.0.0.1:20128/v1`) with strict structured JSON schemas in prediction market research pipelines:

## Upstream Formatting Behavior
LLMs routed via 9Router (e.g. Gemini 3.6, Grok 4, Claude Sonnet 4.6) intermittently wrap JSON responses in Markdown code blocks (` ```json ... ``` ` or ` ``` ... ``` `) even when `response_format={"type": "json_object"}` is set.

## Transport-Envelope Normalization Rules (`normalize_transport_envelope`)
1. **Raw JSON Object:** `raw.startswith("{") and raw.endswith("}")` -> `RAW_JSON`.
2. **Single Fenced Block:** `raw.startswith("```") and raw.endswith("```")` with exactly two ` ``` ` markers and no leading/trailing prose outside the fence -> `SINGLE_FENCED_JSON` or `SINGLE_FENCED_UNLABELLED`.
3. **Strict Rejections:**
   - Leading or trailing prose outside the code block (`PROSE_WITH_JSON` / `TRAILING_TEXT`).
   - Multiple code blocks (`MULTIPLE_BLOCKS`).
   - Unclosed/malformed fences (`MALFORMED_FENCE`).
   - Arbitrary regex extraction from general prose (REJECTED).
4. **Schema Validation:**
   - Apply Pydantic model validation (`extra="forbid"`) on normalized JSON string without easing requirements.
   - Enforce probability range ($0.001 \le p \le 0.999$), valid uncertainty interval ($lower\_80 \le p \le upper\_80$), non-empty rationale, valid evidence citations.

## Format-Correction Retry Protocol (Max 1 Retry)
- **Attempt 1:** Standard prompt with `json_mode=True`.
- **If Attempt 1 Fails:** Record diagnostic artifact, then send Attempt 2 retry prompt:
  > *"IMPORTANT FORMAT CORRECTION: Your previous output failed JSON validation ({error}). Return ONLY a raw valid JSON object matching the requested schema. Do NOT use Markdown code blocks (no ``` fences) and do NOT include any introductory or explanatory prose."*
- **If Attempt 2 Fails:** Fail closed immediately. Do NOT run downstream logit aggregation, Risk Gate, or persistence. Emit structured SSE error event:
  ```json
  {
    "code": "LLM_OUTPUT_FORMAT_INVALID",
    "stage": "multi_agent_forecasting",
    "agent_role": "<role>",
    "attempts": 2
  }
  ```

## Diagnostic Artifact Logging (`ParseFailureDiagnostic`)
Record diagnostic entry in persistent repository for every failure (Attempt 1 failure, Attempt 2 failure, or safe normalization):
- `run_id`
- `agent_role`
- `model_alias`
- `upstream_resolved_model`
- `attempt` (1 or 2)
- `response_format_classification` (`RAW_JSON`, `SINGLE_FENCED_JSON`, `SINGLE_FENCED_UNLABELLED`, `PROSE_WITH_JSON`, `MULTIPLE_BLOCKS`, `MALFORMED_FENCE`, `INVALID_JSON`, `SCHEMA_INVALID`)
- `raw_response_sha256`
- `raw_response_truncated` (max 500 chars, secrets redacted)
- `parser_error`
- `normalization_or_retry_used`

## Secret Redaction Requirement
All diagnostic logs and error payloads MUST run through `redact_sensitive_content` to strip `API_KEY`, `Authorization`, `Bearer` tokens, and environment secrets before persistence or SSE emission.
