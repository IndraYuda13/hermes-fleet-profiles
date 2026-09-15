# OpenAI Codex quick reference

Codex runs from a git repository. For a one-shot task:

```bash
codex exec 'Make the specified focused change and run its tests'
```

Use the normal sandbox or `--full-auto` for intentional workspace edits. If Codex runs under a service context where its sandbox cannot initialize, `--sandbox danger-full-access` is an exception—not a default—and requires a narrow workdir, clean baseline, and independent diff/test review. Use separate worktrees for concurrent Codex tasks.

## Gateway routing and Responses wire API protocol

Codex CLI v0.154.0+ mandates the Responses wire API protocol (`wire_api = "responses"`):

1. **Wire API endpoint:**
   - Configure Codex to target `/v1/responses`, not `/v1/chat/completions`.
   - Generic chat-completions translation layers fail because Codex packages tools inside a `namespace: "functions"` wrapper or inside `input` via `additional_tools`. When a proxy flattens this namespace into an empty tool, `exec` and `apply_patch` are dropped upstream, leading to conversational hallucinations where files are never created on disk.

2. **Tool definition & flattening rules:**
   - Tools with `type: "namespace"` must be unpacked. Inner functions (`type: "function"`) map to standard callable functions.
   - Freeform tools (`type: "custom"`, e.g. `exec`, `apply_patch`) must be exposed with a string parameter schema (`input: string`) so upstream models format raw arguments without breaking on strict JSON parsers.

3. **Streaming SSE protocol contract:**
   - Adhere strictly to the Responses SSE event sequence:
     `response.created` -> `response.output_item.added` -> delta streams -> `response.output_item.done` -> `response.completed`.
   - Distinguish structured vs freeform tool deltas:
     - Standard functions: stream via `response.function_call_arguments.delta`.
     - Freeform/custom tools (`apply_patch`, `exec`): stream raw unescaped input via `response.custom_tool_call_input.delta` and finalize with `response.custom_tool_call_input.done`.
   - Every stream must terminate with a terminal event (`response.completed` or `response.failed`), otherwise Codex CLI hangs indefinitely.

4. **Security & delimiter sanitization:**
   - **Indirect injection defense:** Sanitize all input surfaces (`function_call_output`, `custom_tool_call_output`, and `input_text`) against delimiter tokens. Repositories or command outputs containing fake delimiters can trigger unauthorized tool invocations.
   - **Dynamic nonces:** Wrap tool instructions using cryptographically secure dynamic nonces (`secrets.token_hex(16)` per turn) rather than predictable static delimiters.
   - **Fail-closed auth:** Gateway authentication must fail closed when an API key is configured and verify tokens using constant-time comparison (`secrets.compare_digest`).
