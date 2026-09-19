# Reverse API Gateways & Autonomous Agent Compatibility

Patterns, pitfalls, and verification procedures when wrapping reverse-engineered web chat endpoints into OpenAI-compatible API gateways (`/v1/chat/completions`) and evaluating them for autonomous agent runtimes.

## 1. Multimodal & File Ingestion Architecture

Web chat backends (e.g. ChatGPT, Claude web) do not accept inline raw image base64 or arbitrary URLs inside standard conversation streams. They enforce an asynchronous, presigned object-storage upload lifecycle.

### Upstream 3-Phase Upload Lifecycle
1. **Metadata Allocation (`POST /backend-api/files`):**
   - Client declares file metadata: `{"file_name": "...", "file_size": ..., "use_case": "multimodal"}`.
   - Upstream validates quotas and returns a presigned upload URL (S3 or Azure Blob SAS) plus a unique tracking ID (`file-xxx`).
2. **Direct Binary Transfer (`PUT <upload_url>`):**
   - Client streams raw binary bytes directly to the object storage endpoint with the required storage headers (e.g. `x-ms-blob-type: BlockBlob` for Azure).
   - Upstream API proxy is bypassed during the byte transfer.
3. **Registration & Asynchronous Processing (`POST /backend-api/files/{file_id}/uploaded`):**
   - Client signals upload completion. Upstream triggers internal antivirus/malware scanning, thumbnail generation, OCR, and vision embedding.
   - Client polls or verifies readiness before referencing the file in chat.
4. **Conversation Attachment Linking:**
   - The message payload is transformed from `text` to `multimodal_text`.
   - The file is referenced via an internal pointer scheme (e.g. `{"asset_pointer": "file-service://file-xxx", "width": ..., "height": ...}`) and linked under `metadata.attachments`.

### Gateway Implementation Guardrails
- **Ingress Parsing:** When parsing OpenAI Vision requests (`{"type": "image_url", "image_url": {"url": "..."}}`), branch explicitly between base64 data URIs (`data:image/...;base64,...`) and external HTTP(S) URLs.
- **SSRF & Resource Protection:** For remote image URLs, enforce private IP blocking (reject loopback, link-local, and RFC 1918 subnets), bounded HTTP timeouts (max 10s), and strict size caps (max 20MB) before fetching.
- **Dimension Extraction:** Inspect image headers (PNG/JPEG/WebP) in-memory to supply required width/height fields without invoking heavy rendering engines.
- **Asset Deduplication Cache:** Hash image bytes using SHA-256 and map `hash -> file_id`. Multi-turn agent chats repeatedly re-send earlier images in the message history; re-uploading identical bytes on every turn wastes bandwidth and exhausts upstream rate limits.

---

## 2. Autonomous Agent Compatibility Traps

Reverse web gateways that perform well for interactive chat UIs frequently fail completely when deployed as backend model engines for autonomous agents (e.g. Hermes Agent, OpenCode, AutoGen, 9router).

### The Native Tool/Function Calling Gap
- **Problem:** Autonomous agents require native structured tool calls (`tools: [...]`, `tool_choice`, and response `tool_calls`). Web conversational endpoints only support upstream internal plugins (e.g. internal browser, code sandbox) and reject or ignore arbitrary client function schemas.
- **Consequence:** Models behind web reverse proxies cannot execute native tool loops. Text-prompted function calling (e.g. XML or Markdown ReAct tags) requires heavy client-side regex parsing, is prone to syntax hallucination, and fails schema validation.

### History Flattening & Role Dropping
- **Problem:** OpenAI standard API is stateless: clients supply the complete conversation history on every turn, including `role: "system"`, `role: "assistant"` with `tool_calls`, and `role: "tool"` execution results.
- **Pitfall:** Naive reverse gateways often extract only the last user turn (`for m in reversed(messages): if m.role == 'user': ...`).
- **Consequence:**
  - System prompts (agent identity, security boundaries, available tools) are silently dropped.
  - Tool execution outputs (`role: "tool"`) are completely invisible to the model on subsequent turns, causing infinite re-execution loops or total context loss.

### Stateless vs Stateful Graph Desynchronization
- **Problem:** Web chat backends maintain server-side conversation DAGs indexed by `conversation_id` and `parent_message_id`.
- **Pitfall:** Agent loops frequently branch, retry failed steps, or compact/truncate context windows.
- **Consequence:** If the gateway attempts to map a truncated or edited agent history into an existing upstream conversation thread, the server-side tree desynchronizes, generating context hallucinations or `404 Parent Message Not Found` errors.

### Handshake Latency Multiplier
- **Problem:** Upstream web anti-bot defenses (Proof-of-Work SHA3 challenges, Turnstile bytecode VM emulation, Sentinel handshakes, conduit token exchanges) require multiple sequential roundtrips before starting generation.
- **Consequence:** Pre-flight overhead of 0.8s–2.5s per turn compounds across multi-turn agent execution. A 10-turn tool loop incurs up to 25 seconds of pure handshake latency, starving interactive agent responsiveness.

### Concurrency Locks & Account Quarantine
- **Problem:** Single-session web subscriptions enforce strict single-thread concurrency constraints (`Only one message at a time per conversation`).
- **Consequence:** Agent fanout (parallel subagents, concurrent review or planning queries) causes HTTP 429 concurrency rejections. High-frequency automated requests originating from datacenter IP addresses trigger Cloudflare Turnstile blocks or immediate account termination.

---

## 3. Provider Qualification Checklist for Agent Runtimes

Before configuring an API gateway as a provider for autonomous agent execution, verify all six criteria:

- [ ] **Native Function Calling:** Endpoint accepts `tools` array and returns valid structured `choices[0].message.tool_calls`.
- [ ] **Full Role Preservation:** Gateway preserves `system`, `assistant` (with tool calls), and `tool` (with tool call ID) messages without flattening to user-only prompts.
- [ ] **Stateless History Ingestion:** Gateway accepts arbitrary full-history arrays without relying on server-side message trees.
- [ ] **Sub-Second TTFT:** Pre-flight handshake latency is zero or minimal (<200ms) without multi-step browser emulation.
- [ ] **Concurrency Isolation:** Supports at least 3-5 concurrent execution slots without cross-thread lockups or session collisions.
- [ ] **Stable IP Egress:** Requests use clean residential/datacenter IPs with zero risk of interactive CAPTCHA blocking.

---

## 4. Universal Function Calling & MCP Bridge Implementation Pattern

When wrapping a web LLM endpoint into an OpenAI-compatible function-calling gateway (`tools`, `tool_choice`, `tool_calls`), use a dual-layer engine: native upstream toggles for platform tools (web search, code interpreter) and a universal virtual compiler + streaming state machine for client-defined tools.

### A. Dynamic Delimited Prompt Injection & Sanitization
- **Dynamic Nonce Delimiters:** Never use static tags like `<tool_call>` or `[TOOL_CALL]`. Attackers or user prompts can easily inject closing tags and spoof tool executions. Generate a per-turn random nonce (e.g. `<<<TOOL_CALL_<hex8>>>>` ... `<<</TOOL_CALL_<hex8>>>>`) and instruct the model to wrap calls strictly inside that tag.
- **Input Neutralization:** Scan and escape any occurrences of the gateway delimiter pattern in user messages before submitting the payload upstream so the model never sees conflicting delimiter structures.
- **Strict Schema Whitelisting:** Strip experimental or deeply nested properties from client-submitted tool definitions. Enforce max character caps (e.g. 512 chars) on tool and parameter descriptions to prevent prompt-injection via metadata.

### B. Lookahead Streaming State Machine (O(1) Argument Streaming)
- **Token Lookahead Buffer:** When streaming SSE from upstream, maintain a lookahead buffer sized to the open delimiter. While outside tags, yield text immediately as `choices[0].delta.content`.
- **Zero O(N^2) JSON Decoding:** Do NOT run `json.loads()` on every incoming delta token. Stream raw argument slices directly as `choices[0].delta.tool_calls[0].function.arguments` fragments. Only validate complete JSON once upon encountering the closing delimiter.
- **Bounded Accumulator Buffers & Fail-Closed Truncation:** Cap argument accumulation buffers (e.g. max 64 KB per parameter string, max 1 MB per turn). If a runaway model exceeds the limit without closing tags, terminate stream immediately (fail-closed) with `finish_reason: "length"` to prevent ReDoS or memory exhaustion. Furthermore, if the upstream connection terminates, errors, or hits upstream token limits while the parser is still in `IN_TOOL_CALL` without encountering the end delimiter, never emit partial unclosed arguments with `finish_reason: "tool_calls"`. Routers rewriting `length` to `tool_calls` cause downstream agents to crash on JSON decode validation or abort with router-masked truncation; explicitly expose `finish_reason: "length"` so the client runtime can execute continuation recovery.

### C. Multi-Turn Session Pool Normalization
- **Root-Only Injection for Hidden System Instructions:** When translating caller instructions into upstream system messages marked `is_user_system_message: True` and `is_visually_hidden_from_conversation: True`, inject the system node strictly on initial root conversation creation (`parent_message_id == "client-created-root"`). Never prepend a hidden system message on continuation turns; upstream retains custom instructions from root, and injecting hidden nodes on every turn pollutes the message tree DAG and triggers model safety refusals regarding skipped/hidden context when users query turn history.
- **Environmental Disambiguation for User-Mapped Tool Results:** When wrapping client `role: "tool"` execution results into upstream user messages (`author: {"role": "user"}`), wrap the payload in an explicit runtime envelope (`[SYSTEM / RUNTIME ENVIRONMENT: Automated tool execution output]`). Without this delimiter, upstream models treat tool outputs as human messages, corrupting user turn counts and conversation recall.
- **Stateful Tool Call Registry:** Retain active `tool_call_id` mappings in the session pool. When the client sends `role: "tool"`, verify that `tool_call_id` matches an active pending call from the previous assistant turn; reject orphan or unprompted tool messages with HTTP 400.
- **Message Tree Normalization:** Translate client history into upstream format. Map `role: "assistant"` with `tool_calls` and subsequent `role: "tool"` messages into structured context blocks (e.g. `[Tool Result for <name> (<id>)]: <content>`) anchored to the assistant turn's message ID (`parent_message_id`).
- **Session Mutex & 404 Recovery:** Protect per-session state with an `asyncio.Lock` to prevent DAG corruption from concurrent requests. If upstream returns 404 due to context eviction, replay the full normalized conversation history from root (`parent_message_id="client-created-root"`).

### D. MCP Plugin Bridge Hardening
- **SSRF Mitigation:** When connecting to remote/SSE MCP endpoints, perform synchronous DNS pre-resolution and reject connections to loopback (`127.0.0.0/8`, `::1`), private subnets (RFC 1918: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), and cloud metadata services (`169.254.169.254`). Disable automatic HTTP redirects.
- **Zero-Shell Subprocess Execution:** Run local MCP servers via `subprocess.Popen(cmd_list, shell=False)` using an explicit binary allowlist.
- **Credential & Environment Isolation:** Pass a sanitized, empty environment (`env={}` + explicitly whitelisted keys) to child MCP processes. Never pass `os.environ.copy()`, which leaks gateway API keys, session tokens, and proxy secrets.
- **Hard Execution Timeout:** Enforce a strict execution deadline (e.g. 15s) for external tool calls so hanging MCP servers do not starve the gateway.

### E. Codex / Responses Wire Protocol Custom Tool Streaming
- **Incomplete JSON Prefix Guard:** When extracting unwrapped arguments for custom/freeform tool delta streaming (e.g. converting `{"input": "<cmd>"}` to `response.custom_tool_call_input.delta`), argument tokens arrive incrementally (`'{"'`, `'in'`, `'pu'`, `'t"'`, `': '`, `'"'`). If `s.startswith("{")` or `s.startswith("[")` and the payload has neither parsed as complete JSON nor matched the value regex, return `""` immediately. Never fall through to returning raw `s`: returning partial JSON syntax emits syntax fragments as tool input and advances `emitted_input_len` past 0, which stalls delta streaming until actual input length exceeds the syntax length and corrupts the command prefix.
- **Delimiter-Adjacent Formatting Whitespace Suppression:** When models emit closing tool delimiters (e.g. `<<</TOOL_CALL_...>>>\n`), the trailing newline is delimiter formatting, not assistant speech. Buffer leading text or check for completed tool calls so delimiter-adjacent whitespace does not spuriously instantiate an empty or newline-only `message` output item in turn output arrays.

