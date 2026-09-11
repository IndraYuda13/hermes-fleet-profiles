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
