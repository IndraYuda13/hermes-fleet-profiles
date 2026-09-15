---
name: reverse-api-gateway-engineering
description: Build & run reverse web API gateways and OpenAI proxies.
version: 1.0.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [reverse-proxy, api-gateway, fastapi, pow, sentinel, openai-compatible, session-pool, opsec]
---

# Reverse API Gateway Engineering & OpenAI Proxy Standards

## Overview

Use this skill when reverse-engineering web application endpoints (e.g. ChatGPT, DeepSeek, Claude) to build production-grade, OpenAI-compatible proxy gateways (`/v1/chat/completions`, `/v1/models`), deploying them behind Cloudflare Tunnels, and packaging them with standalone verification clients and private git repositories.

---

## 1. Traffic Intercept & Protocol Decompilation

1. **Dump Decompression**: Inspect HTTP/WSS dumps using streaming decompressors (`brotli`, `gzip`, `zstandard`). Look for authorization headers, account identifiers, session tokens, and handshake requirements (`/prepare`, `/challenge`).
2. **Anti-Bot & Proof-of-Work (PoW) Solvers**:
   - Implement pure-Python headless solvers (e.g., SHA3-512 / SHA-512 target difficulty solvers and bytecode interpreter VMs for Turnstile challenges) using `curl_cffi` with TLS client impersonation (`chrome` or `edge`).
   - Avoid heavy headless browser dependencies (Playwright/Puppeteer) whenever algebraic/cryptographic verification can be executed in pure Python (<50 MB RAM footprint).
3. **SSE Stream Parsing**:
   - Parse Server-Sent Events line by line (`data: {...}`).
   - Support varied upstream framing: cumulative text parts, standalone token deltas (`{"v": "..."}`), and array-based JSON patches.
   - Always map thinking/CoT metadata to standard `reasoning_content` (or `delta.reasoning_content` in streaming chunks).

---

## 2. Smart Session Pool Architecture

1. **Stateful vs Stateless Mapping**:
   - Client requests are typically stateless, while upstream web backends are stateful conversation trees (`parent_message_id`, `conversation_id`).
   - Implement a thread-safe `SmartSessionPool` with LRU eviction (e.g. 10 active slots).
   - Use SHA-256 fingerprinting of the root prompt or explicit `session_id` header to route follow-up turns to the exact upstream conversation node.
2. **Upstream Lifecycle Management**:
   - When evicting or starting a `/new` thread, trigger an asynchronous upstream deletion (`DELETE /backend-api/conversation/{id}`) to keep user accounts clean and prevent quota lockups.

---

## 3. Swagger UI & OpenAPI Documentation

- **Unconditional Swagger Exposure**: In FastAPI applications, do NOT hide `/docs` behind `if DEBUG else None`. If user interactive testing or client discovery is expected, configure:
  ```python
  app = FastAPI(
      title="...",
      docs_url="/docs",
      redoc_url="/redoc",
      openapi_url="/openapi.json"
  )
  ```
  Gating docs strictly behind `DEBUG=false` causes silent HTTP 404 errors on public domains when debug mode is disabled in production environments.

---

## 4. Interactive CLI Client Delivery (Zero-Dependency REPL)

When providing a Python terminal client (`<gateway>_client.py`):
1. **Default Bare Execution to REPL**:
   - Running `python client.py` without arguments MUST open an **Interactive REPL mode** by default.
   - Display a clean status banner: API Endpoint, Status (Online/Account info), Active Pool Slots, and Slash Commands (`/think [on|off]`, `/model [name]`, `/new`, `/exit`).
   - Wait for user prompt at `You [Model: ... | Think: ...] > `.
   - Single-shot execution MUST trigger only when an explicit positional argument (`python client.py "prompt"`) or piped stdin is provided. Never auto-execute a hardcoded demo prompt when run bare.
2. **Zero External Dependencies**:
   - Use only Python Standard Library (`urllib.request`, `json`, `sys`, `argparse`, `os`).
   - Enable ANSI escape sequences on Windows consoles via `os.system("")` on `win32`.
   - Separate reasoning tokens (dim/yellow) and response tokens (green/bold) in real-time streaming output.
   - **Explicit User-Agent for Cloudflare Ingress**: Cloudflare WAF blocks the default `Python-urllib/3.x` User-Agent with HTTP 403 Forbidden. Always pass a browser-like or explicit client User-Agent (`User-Agent: Mozilla/5.0 ...` or custom app name) in all HTTP requests to prevent ingress rejections.

---

## 5. OpSec & Repository Scaffolding Standards

All reverse-engineered gateway projects must follow strict operational security and repository hygiene:
1. **Discrete Naming**:
   - Never use official vendor or brand names in repository names, package names, or descriptions.
   - Use discrete prefixes: `ds-gateway` (DeepSeek), `cg-gateway` (ChatGPT), `cx-gateway`, etc.
   - Description format: *"Lightweight conversational gateway and proxy interface (<code-name> edition)"*.
   - Visibility must strictly be set to **`PRIVATE`** on GitHub.
2. **Strict Sanitization & Zero Leaks**:
   - `.gitignore` must strictly ignore `.env`, `data/session_pool.json`, `*.pyc`, `__pycache__`, and test cache directories.
   - Provide `.env.example` with placeholder credentials (`Bearer lemon` / `[REDACTED]`).
   - Commit history must never contain live session cookies or Bearer tokens.
3. **Parity Scaffolding**:
   - Complete standard structure: `Dockerfile` (Python 3.11-slim), `docker-compose.yml`, `LICENSE` (MIT), `pyproject.toml`, clean `requirements.txt`, systemd service unit (`systemd/<gateway>.service`), and fully documented English `README.md`.

---

## 6. Integration Boundaries: Reverse Web Gateways vs Coding Agents (Hermes vs Codex CLI)

### Protocol Discrepancy & Agent Support Matrix
1. **OpenAI Chat Completions Clients (`/v1/chat/completions`)**:
   - Clients: **Hermes Agent**, **Cursor**, **LibreChat**, **OpenWebUI**, **Cline**, and official OpenAI Python/Node SDKs.
   - Requirement: Standard `tools: [...]` and `tool_choice` parameters.
   - Function Calling Implementation in Reverse Gateways:
     - **Prompt Compilation**: Inject JSON tool definitions into upstream system context with cryptographic per-turn nonce delimiters (`<<<TOOL_CALL_{nonce}>>>`).
     - **Lookahead Streaming State Machine Parser**: Parse SSE streams in $O(1)$ to separate textual `delta.content` from tool invocation `delta.tool_calls` without buffering the entire turn.
     - **Multi-Turn Normalization**: Convert client `role: "tool"` messages and prior tool calls into valid upstream conversation history. Protect multi-turn conversation sessions with an `asyncio.Lock` to avoid concurrent turn collisions.

2. **OpenAI Codex CLI (`@openai/codex`) & Native Responses API (`/v1/responses`)**:
   - **Wire API Mandate**: Codex CLI v0.154.0+ deprecates `wire_api = "chat"` and strictly requires **`/v1/responses`** (`wire_api = "responses"`).
   - **Discovery of `additional_tools` in `req.input`**:
     - Codex CLI v0.154.0+ does NOT always place client execution tools in `req.tools`. It often embeds them inside `req.input[0]` as `{"type": "additional_tools", "role": "developer", "tools": [...]}`.
     - *Rule*: Always inspect both `req.tools` and `req.input` items for `type == "additional_tools"` before compiling tools. Missing this causes `has_tools=False` and disables all client-side tools.
   - **Hierarchical Tool Namespace Unwrapping**:
     - Codex CLI bundles execution tools inside nested namespace schemas:
       ```json
       {
         "type": "namespace",
         "name": "functions",
         "tools": [
           {"type": "custom", "name": "exec", ...},
           {"type": "custom", "name": "apply_patch", ...}
         ]
       }
       ```
     - **Router Flattening Defect**: Generic multi-model routers (such as 9Router) that convert `/v1/responses` to `/v1/chat/completions` flatten `{type: "namespace", name: "functions"}` into an empty dummy tool `{"name": "functions", "parameters": {}}`, dropping `exec` and `apply_patch`. Upstream models receive zero tool parameters, resulting in text hallucinations without executing commands.
     - **Resolution**: Build a native `POST /v1/responses` adapter directly in the gateway. Extract inner tools from any `namespace` block.
   - **Custom Freeform Tool Adaptation**:
     - CLI tools like `exec` and `apply_patch` have `type: "custom"` with raw text inputs. Expose them to upstream prompt compilation as JSON functions with a single property: `{"input": {"type": "string", "description": "Raw tool input..."}}`.
     - When streaming the model's response back to Codex over SSE, emit `event: response.output_item.added` with `item.type: "custom_tool_call"`, stream chunks via `event: response.custom_tool_call_input.delta`, and close with `event: response.custom_tool_call_input.done`.
   - **Immediate Delimiter Finalization Timing**:
     - Close active tool call items (`output_item.done`) immediately when the end delimiter matches in the streaming lookahead parser.
     - Never defer closing tool call items until stream completion; subsequent assistant text chunks arriving while a tool item remains open trigger `OutputTextDelta without active item` errors in Codex's Rust state machine.
   - **Fail-Closed Client Token Sanitization**:
     - Coding agents send their local config key (`Authorization: Bearer sk-...`) to the gateway.
     - Web session backends (e.g. ChatGPT Web) reject `sk-...` with `HTTP 401: API keys are not supported by this endpoint` or Sentinel verification failures.
     - *Rule*: Only override `DEFAULT_TOKEN` if `bearer.startswith("eyJ")` (an actual web session JWT). All other keys (`sk-...`, proxy keys) validate proxy access only and must keep `DEFAULT_TOKEN` for upstream requests.
   - **Multi-Turn Session ID Resolution & Aliasing**:
     - In non-streaming chat completions, ensure `resp_session_id = req.session_id or final_conv_id or session_id`. Never return a pre-call placeholder UUID when upstream returns a real `conversation_id`.
     - In `SmartSessionPool`, maintain an `aliases` list on `SessionEntry` mapping the original placeholder session ID, custom IDs, and upstream conversation IDs to the same conversation node.
   - **Provider Routing (`openai_base_url` vs `model_provider`)**:
     - Configure Codex CLI via custom provider block to bypass WebSocket probing:
       ```toml
       model = "gpt-5.6-sol"
       model_provider = "cg"

       [model_providers.cg]
       name = "ChatGPT Gateway"
       base_url = "http://127.0.0.1:8560/v1"
       wire_api = "responses"
       ```
     - Setting `openai_base_url` directly under root without `model_provider` causes Codex CLI to attempt WebSocket connections on `ws://.../v1/responses` with 5 retries before falling back to HTTPS SSE, introducing 10s connection latency.
   - **Model Metadata Fallback Trap**:
     - If Codex CLI receives an unknown model slug (e.g. `Gpts/gpt-5-6-thinking`), it warns: `Model metadata not found. Defaulting to fallback metadata`, which automatically sets `turn_context.tools = None`, disabling Codex's local execution sandbox.
     - **Resolution**: Point Codex CLI directly to the gateway with `wire_api = "responses"`, and configure recognized model identifiers (e.g. `gpt-5.6-sol`, `gpt-5.3-codex`, `gpt-5.1-codex`) either directly or via gateway model aliasing.
   - **Codex Execution Persona & Context Anchoring Prevention**:
     - *Trap*: On conversational prompts (e.g. "can you check my VPS status?"), web chat models instinctively claim lack of server access ("I don't have direct access to your VPS"). Once stated in turn 1, multi-turn history anchors the refusal on subsequent turns.
     - *Resolution*: Inject a strict execution persona into `tool_sys_prompt` or system instructions:
       ```text
       You are acting as the execution backend for OpenAI Codex running directly on the user's local machine.
       You HAVE direct access to the local environment and terminal via your attached tools (such as `exec`).
       1. NEVER say that you lack access to the machine or terminal.
       2. NEVER ask the user to run commands manually when you have tools to run them yourself.
       3. IMMEDIATELY call the appropriate tool (e.g. `exec`) using required tool delimiters to inspect the machine and return actual output.
       ```
   - **Intermediate Proxy (9Router) Routing Decision**:
     - *Chat Completions Clients (Hermes Agent, Cursor, Python SDK)*: Safe to route through intermediate multi-model proxies (like 9Router OpenAI-compatible chat nodes) because `/v1/chat/completions` wire format is fully supported.
     - *Responses API Clients (OpenAI Codex CLI)*: Must route **DIRECT** to the gateway (`base_url = "http://127.0.0.1:8560/v1"` with `wire_api = "responses"`). Never route Codex through 9Router or generic OpenAI-compatible chat nodes, because multi-model proxies strip nested `functions` tool namespaces during translation to chat completions, leaving tools empty and causing hallucinated execution.
   - **Diagnosing "Agent Hallucinated Output Instead of Calling Tools"**:
     - *Verification Checklist*:
       1. Did the client payload actually contain tool schemas in `req.tools` or `req.input`? If the client profile or session has tools disabled, `has_tools` evaluates to `False`. Without delimiter prompt compilation, the model will hallucinate plausible-looking outputs (e.g., inventing server metrics, fake file contents) rather than emitting tool calls.
       2. Did an intermediate proxy strip tools? Check the gateway logs for `len_tools`. If `len_tools=0` but the client had tools, the intermediate proxy is flattening or dropping the schemas.
       3. Was the model anchored by previous conversational turns? If turn 1 replied conversationally with "I cannot access the system", the model will repeat that refusal in turn 2 unless the system persona explicitly asserts tool execution authority.

---

## 7. Multimodal Media & Universal File Upload Architecture (Images vs Documents)

Web chat backends (such as ChatGPT) **never** accept raw base64 or file bytes inside the conversation body. They enforce a **3-Phase Presigned Upload Protocol**:

1. **Initiate Metadata (`POST /backend-api/files`)**:
   - Send payload:
     ```json
     {
       "file_name": "filename.ext",
       "file_size": len(data),
       "use_case": "multimodal" | "my_files"
     }
     ```
   - **MIME Type Routing (`use_case`)**:
     - Visual Media (`image/*`): Set `use_case: "multimodal"`. Upstream passes bytes to the vision model.
     - Documents (`application/pdf`, `text/*`, `text/csv`, code, `.docx`): Set `use_case: "my_files"`. Upstream passes file to internal document indexing and retrieval.
   - Response returns `{"status": "success", "upload_url": "https://...", "file_id": "file_..."}`.

2. **Direct Binary Storage PUT**:
   - Execute an HTTP PUT of raw binary bytes directly to `upload_url` (Azure Blob or S3).
   - Storage Header Isolation: Send only required storage headers (`Content-Type: <mime>`, `x-ms-blob-type: BlockBlob`, `x-ms-version: 2020-04-08`). Do NOT leak session cookies or Authorization Bearer tokens to Azure/S3 storage endpoints.

3. **Finalize & Index (`POST /backend-api/files/{file_id}/uploaded`)**:
   - Send `{}` to signal that binary transmission is complete. Upstream triggers virus scanning and document chunking/indexing.

4. **Conversation Message Construction**:
   - **For Images**: Message `content` is `content_type: "multimodal_text"`, containing an item in `parts`:
     `{"content_type": "image_asset_pointer", "asset_pointer": "file-service://{file_id}", "size_bytes": ..., "width": ..., "height": ...}` followed by user prompt text, plus `metadata.attachments`.
   - **For Documents (PDF, TXT, CSV, Code)**: Message `content` is `content_type: "multimodal_text"`, with `parts` containing only the user prompt text string. The file reference is passed exclusively inside `metadata.attachments`:
     ```json
     "attachments": [
       {"id": file_id, "name": file_name, "size": file_size, "mime_type": mime_type}
     ]
     ```
   - Upstream automatically invokes its document retrieval tool and produces inline `filecite` tokens (e.g. `fileciteturn0file0L1-L2`).

5. **Deduplication & SSRF Protection**:
   - Cache SHA-256 byte hashes to avoid re-uploading identical files across multi-turn sessions.
   - For remote URLs, strictly block private/loopback/link-local IP addresses and enforce size caps (e.g. 20MB) and timeouts.

---

## 8. Zero-Setup Client & Offline Laptop Handoff Packaging

When creating an archive (.zip) of a reverse-engineered gateway for zero-setup execution on a user's local laptop:
1. **Include Live Session Artifacts**:
   - Standard repository packaging ignores `.env` and `data/credentials.json`. However, for a user handoff intended to run immediately without browser login or re-authentication, explicitly include `.env` (pre-configured with local host/port) and `data/credentials.json` (active session cookies, Bearer JWT, User-Agent, account ID).
2. **Exclude Bloat & Security Leaks**:
   - Prune `.git/`, `__pycache__/`, `.pytest_cache/`, and test scratch directories. The resulting archive should be lightweight (<200 KB).
3. **Dual Delivery Channel**:
   - Provide native chat delivery (`MEDIA:/path/to/archive.zip`) for mobile/chat clients.
   - Concurrently copy to a local static HTTP directory (e.g. `/var/www/html/openclaw-media/`) with `Cache-Control: no-store` and return a public HTTPS URL for direct `curl` or browser downloads.
4. **Standard 3-Step Runbook**:
   - Always supply the universal Python startup commands:
     ```bash
     unzip <archive>.zip && cd <dir>
     python3 -m venv venv && source venv/bin/activate
     pip install -r requirements.txt
     python server.py
     ```
5. **Faithful Return & In-Place Deployment of User-Modified Archives**:
   - When the user modifies the gateway locally on their laptop and returns an updated archive (.zip) with instructions to apply it as-is ("jangan ubah apapun"):
     - Unpack and sync cleanly into the repository tree without modifying user-provided source files.
     - **Preserve Production Credentials & Runtime State**: Incoming archives often contain blank templates, dummy keys, or temporary keyfiles. NEVER overwrite live production state (`data/credentials.json`, `data/sessions.json`, `.chatgpt_tmp_id_ed25519*`, `.env`) with files from the archive.
     - Keep the repository `.git/` directory intact.
     - Check `requirements.txt` for newly added dependencies (e.g., `mcp`) and ensure they are installed in the service's virtualenv.
     - Run test suites before and after restarting to verify regression boundaries.
     - Restart the systemd daemon (`systemctl restart <gateway>.service`) and verify `/health`, `/v1/models`, and any new endpoints.

---

## 9. Native Model Context Protocol (MCP) Server Integration

Modern reverse API gateways can serve dual roles: an OpenAI-compatible completion proxy AND a native Model Context Protocol (MCP) server.
1. **Direct `/mcp` Route Exposure**:
   - Expose `POST /mcp` directly on the main FastAPI application router so external tools (Cursor, Claude Desktop, autonomous coding agents) can connect via standard Streamable HTTP or JSON-RPC 2.0 transport without spinning up separate adapter daemons.
2. **Dynamic Plugin & Tool Reconciler**:
   - Maintain a unified `ToolRegistry` and `PluginManager` with async lifecycle (`connect`, `disconnect`, `reconcile`).
   - Support both `stdio` subprocess transport (running local MCP tools) and HTTP/SSE remote transports.
   - Guard against stdio async context manager protocol incompatibilities in `mcp` Python SDK: ensure `StdioServerParameters` is paired with `stdio_client()` context manager, not passed directly to `enter_async_context(Client(params))`.
3. **OpenAPI & Discovery Parity**:
   - Expose `/v1/mcp/tools` (OpenAI format list) alongside native `/mcp` (MCP protocol JSON-RPC) so both legacy OpenAI SDK consumers and MCP-native clients discover the exact same tool registry.

---

## 10. System Instructions Channel Separation & MCP Custom App Auth

1. **System & Developer Instructions Channel Separation**:
   - In reverse gateways bridging OpenAI Chat Completions (`/v1/chat/completions`) or Responses API to web chat backends:
   - *Problem*: Prepending `system` or `developer` instructions directly into the user prompt string (`f"{instructions}\n\n{prompt}"`) corrupts user turns, leaks instruction delimiters into multi-turn chat history, and weakens system authority.
   - *Resolution*: Extract caller `system` and `developer` messages using `extract_caller_instructions(messages)`. Inject them into the upstream conversation tree as a native system message node:
     `role: "system"`, `is_user_system_message: True`, `is_visually_hidden_from_conversation: True`, with `user_context_message_data: {"about_user_message": "...", "about_model_message": instructions}`.
   - Upstream models honor instructions with full system role authority without cluttering visible user conversation messages.

2. **Tool Calling Protocol Placement Pitfall (System Role vs User Prompt Channel)**:
   - *Pitfall*: Do NOT route delimiter-based tool calling instructions (`tool_sys_prompt`, e.g. `# TOOL CALLING INSTRUCTIONS` with `<<<TOOL_CALL_{nonce}>>>`) through upstream hidden system messages (`about_model_message`). ChatGPT Web treats hidden user-system messages strictly as passive persona context and frequently ignores delimiter-based tool execution instructions when placed there.
   - *Rule*: Keep caller persona in the upstream system/instructions channel (`instructions_to_send`), but compile tool calling protocol instructions into the active user prompt channel (`prompt_to_send = f"{tool_sys_prompt}\n\n{user_prompt}"` if a user prompt exists, otherwise `prompt_to_send = tool_sys_prompt`). This guarantees the model treats delimiter execution as an immediate active turn directive.

3. **Unauthenticated MCP Access for Custom Developer Apps**:
   - Native `/mcp` endpoints typically enforce bearer token authentication. However, custom developer tools or local browser clients connecting to the gateway often lack arbitrary header injection capabilities.
   - Provide an explicit opt-in environment flag (e.g. `CG_MCP_ALLOW_UNAUTHENTICATED=true/false`). When enabled, allow unauthenticated JSON-RPC requests on `/mcp` while defaulting to fail-closed token validation when disabled.

---

## 11. Caller-Owned Tool Router & Upstream Tool Hijack Guard

When bridging web chat backends that possess native internal capabilities (Python code execution sandbox, web browsing/Bing, DALL-E) to external API callers requesting tool calls:
1. **The Internal Tool Hijack Problem**:
   - Web chat models instinctively prefer their built-in Python sandbox or browsing tool over emitting custom caller delimiters when solving computational, browsing, or system tasks.
   - If not strictly guarded, the upstream model runs code inside ChatGPT's isolated environment or hallucinates tool outputs instead of emitting the delimiter block for the external API caller.
2. **Caller-Owned Tool Router Persona**:
   - Explicitly instruct the upstream model with `# CALLER-OWNED TOOL ROUTER`:
     - All provided tools belong to the API caller outside ChatGPT Web.
     - Strictly forbid using ChatGPT's internal Python, sandbox, or browser tools as a substitute.
     - Forbid hallucinations or simulated tool output; the model must emit the delimiter block and immediately stop (`finish_reason="tool_calls"`).
3. **Upstream Internal Tool Hijack Detection & Fail-Closed Guard**:
   - In both streaming and non-streaming completion handlers, track upstream execution events (`upstream_tool` / code interpreter calls).
   - If the upstream backend attempts to execute internal tools when caller tools were defined, fail closed immediately: abort stream, return HTTP 502 with `upstream_internal_tool_hijack` error, and prevent leaking internal sandbox results to the client.
   - Enforce `required_tool_call_missing` when `tool_choice="required"` or a specific named function is requested but omitted by the model.

---

## 12. Caller Operational Identity & Handling Rule (Base-Model Override Prevention)

1. **The Innate Identity Leak Pitfall**:
   - Upstream web chat models possess heavy reinforcement learning (RLHF/RLAIF) identity priors. When users ask casual persona questions ("who are you?", "what model/assistant is this?"), web backends instinctively answer with the base platform identity (e.g., "I am ChatGPT, a large language model trained by OpenAI"), completely discarding the caller's system persona, orchestrator role, or agent name.
2. **Operational Identity Wrapper & Contract**:
   - When extracting caller system/developer instructions and sending them via the upstream system instructions channel, wrap the instructions in explicit identity boundary delimiters:
     ```text
     # CALLER OPERATIONAL IDENTITY AND INSTRUCTIONS
     <caller_instructions>

     # IDENTITY HANDLING RULE
     When the user asks who you are, your name, or your role, answer using the operational identity and role defined in the caller instructions above.
     Do not replace that operational identity with the underlying platform, provider, or base-model identity (for example, 'ChatGPT') unless the user explicitly asks which model, provider, or platform powers this agent.
     If asked about the underlying model/provider, answer truthfully while keeping it distinct from the operational agent identity.
     ```
   - *Mechanism*: Separating the operational identity (agent role/persona) from the technical engine/provider satisfies user queries about underlying models while preventing premature identity collapses during standard conversational turns.

