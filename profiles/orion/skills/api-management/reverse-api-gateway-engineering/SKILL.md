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

## 6. Integration Boundaries: Reverse Web Gateways vs Autonomous Agents (Hermes / 9Router)

**CRITICAL INVARIANT:** Do NOT route autonomous coding agents (such as Hermes Agent) through reverse-engineered web proxies via 9Router.

### Failure Mechanisms
1. **Missing Tool Calling Schemas**: Web chat backends do not accept or process OpenAI client function schemas (`tools: [...]`, `tool_choice`). Agents cannot invoke terminal, file search, or editing tools; the model merely outputs plain conversational text.
2. **Stateless Replay Desynchronization**: Autonomous agents send full stateless conversation histories (`system`, `user`, `assistant[tool_call]`, `tool[result]`). Reverse web gateways only forward the latest user prompt, discarding `system` prompts and `tool` outputs, completely blinding the agent.
3. **Anti-Abuse Burst Signatures & Ban Risk**: Agent loops execute 1-3 second burst cycles. This velocity anomaly triggers Cloudflare Bot Management, infinite Turnstile challenges, and burns web message limits (40-80 msgs/3hr) in minutes, leading to permanent account suspension.
4. **PoW Latency Overhead**: Dynamic Proof-of-Work and Turnstile VM solvers introduce 1.5–3.0s TTFT latency on every single turn.

### Intended Use Cases
- **Valid Uses**: Web chat interfaces (LobeChat, LibreChat, NextChat), IDE code review/chat extensions (Cursor, Continue.dev), and standalone CLI REPL exploration.
- **Agent Engines**: Must use official platform APIs (OpenAI Platform, OpenRouter, DeepSeek Platform) or local vLLM instances for reliable tool-calling and zero ban risk.

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
