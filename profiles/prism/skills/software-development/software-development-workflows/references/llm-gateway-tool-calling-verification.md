# LLM Gateway & OpenAI-Compatible Tool Calling Verification

When verifying LLM reverse proxies, gateway adapters, or OpenAI-compatible endpoints (such as `/v1/chat/completions`) that bridge client tool calls to upstream stateful models or MCP plugin bridges, enforce this verification procedure and test matrix.

## 1. OpenAI Contract Compliance Matrix

### A. Non-Streaming Contract (`stream=False`)
- **Root Fields:** Verify `id` (`chatcmpl-*`), `object: "chat.completion"`, `created` (int timestamp), `model`, `choices`, and `usage`.
- **Finish Reason Invariants:**
  - Must be `"tool_calls"` whenever the message requests one or more tool executions.
  - Must be `"stop"` for normal text completions.
  - Must be `"length"` if max_tokens was reached.
- **Message Shape Invariants:**
  - `role`: Exactly `"assistant"`.
  - `content`: Null (`None`) or string.
  - `tool_calls`: List of objects, each containing:
    - `id`: Unique string (e.g. `call_xyz123`).
    - `type`: Exactly `"function"`.
    - `function.name`: Target function name.
    - `function.arguments`: Valid serialized JSON string (never a Python dictionary or raw object).

### B. Streaming SSE Contract (`stream=True`)
- **Transport Headers:** Verify `Content-Type: text/event-stream`, `Cache-Control: no-cache`, `Connection: keep-alive`.
- **Chunk Framing Structure:**
  - **Chunk 0 (Metadata):** Delta sets `role: "assistant"` and initiates `tool_calls` with `index: 0`, `id`, `type: "function"`, and `function: {"name": "...", "arguments": ""}`.
  - **Chunks 1..N (Argument Fragments):** Delta contains ONLY `tool_calls: [{"index": 0, "function": {"arguments": "..."}}]`. Do not repeat `id`, `type`, or `name` in subsequent fragment chunks.
  - **Parallel Multiplexing:** When multiple tools are invoked in parallel, second tool begins with `index: 1`, separate `id`, and separate `name`.
  - **Penultimate Chunk:** Sets `finish_reason: "tool_calls"`.
  - **Terminal Chunk:** Exactly `data: [DONE]\n\n`.
- **SDK Accumulator Verification:** Pipe SSE output directly into `openai.OpenAI().chat.completions.create(..., stream=True)` and verify that the official client accumulator parses chunks into a valid completion without schema validation exceptions.

## 2. Stateful Pool & Multi-Turn Continuity

When an API gateway fronts a stateful upstream session pool (e.g. ChatGPT Web conversation tree):
1. **Full Message History Parsing:** Verify the gateway parses the full array of messages, including `role: "assistant"` with `tool_calls` and subsequent `role: "tool"` messages with `tool_call_id`. Do not rely solely on the last user message.
2. **Parent Message Node Continuity:**
   - Turn 1 (tool call): Gateway records assistant response message ID in pool.
   - Turn 2 (tool result): Gateway passes the recorded message ID as `parent_message_id`, maintaining tree continuity.
3. **Session Reconnect & 404 Recovery:** If upstream returns 404 (session expired or pruned), verify that gateway falls back to replaying full conversation history as a fresh conversation (`parent_message_id="client-created-root"`) rather than propagating an unhandled 500 error.
4. **Session Mutex Isolation:** Ensure each session ID uses an asynchronous lock (`asyncio.Lock`) so parallel requests to the same session do not corrupt upstream parent message pointers.
5. **System Instruction Lifecycle on Continuations:** In DAG-based stateful backends, inject hidden system messages (`is_visually_hidden_from_conversation: True` or custom instructions) ONLY at root conversation creation (`parent_message_id == "client-created-root"` or `conversation_id is None`). Never re-inject them on continuation turns: re-injection creates redundant hidden nodes at every turn in the upstream message tree, bloating context and triggering model safety/RLHF disclaimers regarding "hidden or skipped messages in context".
6. **Tool Result Channel Isolation:** When upstream backends lack a distinct `tool` author/role and force tool execution results into a `user` role message, prepend an unambiguous automated execution header (e.g. `[AUTOMATED RUNTIME TOOL OUTPUT (NOT HUMAN USER CHAT)]`) and do not echo user prompts inside tool payloads. Without structural or lexical separation, the upstream model conflates automated tool returns with human chat turns, breaking turn accounting and conversational history recall.

## 3. Adversarial Edge Cases & Failure Injection

- **Truncated Arguments & Masked Finish Reason:** When an upstream LLM cuts off mid-argument (`{"param": "val`), verify the gateway transmits the raw argument string without crashing. However, if the stream terminates prematurely while inside a tool call before closing delimiters appear:
  - Do NOT stamp `finish_reason: "tool_calls"` on an incomplete payload that fails JSON closing syntax (`}` or `]`). Client runtimes detect this as masked truncation and abort.
  - The gateway parser must detect mid-call stream termination and surface `finish_reason: "length"`, allowing downstream runtimes to invoke token-limit recovery instead of failing JSON validation.
  - Account for fixed upstream token generation caps: web-based backends enforce fixed generation limits (~4K-8K tokens) that client `max_tokens` cannot override. High-volume tools (DOM reads, large logs) must truncate or paginate before yielding outputs.
- **Empty Function Parameters:** Verify arguments for zero-argument functions serialize to `"{}"`, never empty string `""` or `null`.
- **Mismatched or Missing `tool_call_id`:** If client sends `role: "tool"` without matching `tool_call_id` or with a nonexistent ID, verify gateway returns HTTP 400 (`invalid_request_error`), not HTTP 500.
- **`tool_choice` Semantics:**
  - `"none"`: Asserts `finish_reason: "stop"` with no `tool_calls`.
  - `"required"`: Asserts `finish_reason: "tool_calls"`.
  - Specific function: Asserts called function matches target name exactly.
  - Unknown function target: Asserts immediate HTTP 400 rejection.
- **Client Disconnect Handling:** On client disconnect mid-stream, verify generator catches `GeneratorExit`, aborts the upstream request, and releases session pool locks within 1 second.
- **Oversized Tool Result Buffer Protection:** Clamp or reject single tool outputs exceeding gateway payload boundaries (>20MB) to prevent upstream connection drops.
- **Tool Result Injection Delimiters:** Ensure tool results are wrapped in structured data delimiters so raw tool output cannot inject system prompt commands.

## 4. MCP Plugin Bridge & Upstream Tools

- **JSON-RPC Lifecycle:** Assert `initialize`, `tools/list`, and `tools/call` handshakes follow the MCP specification.
- **Hard Timeout Gate:** External MCP tools taking longer than threshold (e.g. 15s) must be interrupted and return structured `timeout_error`.
- **Crash Isolation:** If an external MCP server terminates abruptly (SIGKILL), the gateway must return a clean service error rather than crashing the gateway process.
