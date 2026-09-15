# Web-LLM to Local MCP Agent Bridging Architecture

Engineering patterns, state machines, and boundary safeguards for bridging cloud web LLM interfaces (e.g. ChatGPT, Claude Web) to local MCP servers, filesystems, terminals, and OS automation via browser extensions.

## 1. Hybrid Web-Extension + Local MCP Bridge Pattern

Rather than wrapping web chat endpoints into reverse-proxy API gateways (`/v1/chat/completions`)—which face CAPTCHA/Turnstile challenges, server-side message DAG desynchronization, and lack of native function calling—the hybrid architecture uses the browser as the frontend/reasoning UI and connects the cloud model to local capabilities via Model Context Protocol (MCP) and an outbound tunnel.

### Component Topology
```text
[ Cloud LLM Backend ]
       | (Outbound Tunnel: OpenAI Secure Tunnel gRPC / Cloudflared HTTPS)
       v
[ Local MCP Server (server.ts) ] <---------+
  - /mcp/core/<secret-token>               |
  - /mcp/desktop/<secret-token>            | (Deterministic Correlation)
  - /mcp/plugins/<secret-token>            | HTTP x-request-id == message.metadata.request_id
                                           v
[ Local App Bridge Server (bridge.ts) ] <---+
       ^ (HTTP REST + Bearer Token, Port 8765-8769)
       |
[ Chrome Extension MV3 (background.js) ]
       | (postMessage bridge)
[ Web DOM Context (content.js, fiber.js, usage.js) ]
```

### Key Architectural Separations
- **Surface Isolation in MCP:** Split MCP servers into granular surfaces (`core`, `desktop`, `plugins`) under unique tokenized base paths (`/mcp/<surface>/<base64url-token>`). LLMs retrieve schemas via full catalog listing (`api_tool.list_resources`); monolithic servers dump all schemas into context, wasting thousands of prompt tokens on irrelevant tools.
- **Dual-Loopback Security:**
  - The local MCP server listens on an ephemeral loopback port and strictly **refuses browser origins** to prevent malicious web pages from executing tool RPC.
  - The local bridge server listens on fixed ports (e.g. 8765-8769), requires `chrome-extension://` origin verification, and validates bearer tokens using constant-time comparison (`timingSafeEqual`).

---

## 2. Browser Extension Traversal & Request Correlation

### Multi-World Execution in Manifest V3
- **`MAIN` World Execution:**
  - `usage.js` injected at `document_start`: Hooks `window.fetch` before application instrumentation runs, observing usage tokens and model tier transparently.
  - `fiber.js` injected at `document_idle`: Extracts internal React Fiber metadata and prototype methods before page scripts can monkey-patch `window.postMessage` or `Object.prototype`.
- **`ISOLATED` World Execution:**
  - `content.js` and DOM adapters handle overlay rendering, composer typing, and secure messaging to the extension service worker.

### React Fiber Traversal Rules
1. **Dynamic Key Resolution:** React appends random build hashes to internal Fiber keys. Discover the key dynamically:
   ```javascript
   function fiberOf(node) {
     for (const key in node) {
       if (key.charCodeAt(0) === 95 && key.indexOf('__reactFiber$') === 0) return node[key];
     }
     return null;
   }
   ```
2. **Nearest Row Group vs Turn Messages:**
   - ChatGPT folds multiple tool executions into a single rendered row ("Called tool").
   - Climbing too far up the Fiber tree (`at = at.return`) reaches the turn-level container (`allMessages`), risking tool misattribution across neighboring rows.
   - Anchor strictly on the nearest row group carrying `memoizedProps.messages`, where `messages[0]` uniquely identifies that row's tool invocation. Cap traversal with `MAX_CLIMB` (e.g. 80) to prevent cyclic or detached tree hangs.
3. **Zero Argument Parsing at Ingress:**
   - Extract only the tool path anchored at the front of payload strings via regex (e.g. `/^\s*\{\s*"path"\s*:\s*"([^"\\]{1,200})"/`).
   - Never pass raw request payloads to `JSON.parse` during UI labeling; tool arguments contain user secrets and large file bodies that risk memory bloat and credential leakage.
4. **Co-Mounted Route Conflict Detection:**
   - During SPA transitions between chats, React can briefly co-mount nodes from both conversation A and B on the same tree branch. Inspect `conversation.id` and `conversation.serverId$()`. If conflicting IDs are found, flag `conflict: true` and fail closed.

### Permanent Request-ID Correlation
- Connect incoming MCP HTTP requests to browser conversation models via the shared unique request identifier:
  - Header `x-request-id` on incoming MCP HTTP calls.
  - `message.metadata.request_id` on the connector message in the React Fiber model.
- Once proven, **ownership must never expire via arbitrary LRU time TTL**. Multi-turn tool loops, long background compilations, or browser tab reloads outlive temporary in-memory caches. Retain request-id mappings until the durable session is archived or deleted.

---

## 3. Autonomous Turn Lifecycle & Session Continuity

### Meta-Prompter Modes: Goal Gate vs Loop
When automating long-running tasks without live human intervention, drive the chatbox using a specialized meta-prompter:
- **Goal Gate:** Evaluates the latest assistant response. If the assistant claims the requested task is finished, it **must output `NO_REPLY` and stop**. It must not audit, ask for extra tests, or invent follow-up work. If items are missing, it sends one concise directive in the user's register.
- **Goal Objective:** Enforces an upfront requirements specification. Meta-prompter re-reads the complete objective on every turn to prevent the model from quietly narrowing scope to whatever subset it already implemented.
- **Loop Mode:** Operates with **zero finish line and no `NO_REPLY` option**. When work appears complete, it instructs the model to harden code, increase test coverage, or clean dead paths. Only user intervention stops Loop mode.

### Active Turn Boundary Holding (`session_finish`)
- Expose a `session_finish` tool for autonomous coding runs.
- When the model attempts to finalize implementation, it calls `session_finish`.
- The backend holds the HTTP boundary (up to 25s) with a `HELD` response rather than concluding the turn.
- If queued user inputs exist in the local session queue, deliver them directly inside the tool result (`offerToolInput`). The model processes the new instruction in the same active turn without triggering full chat completion and restart latency.

### Atomic 4-Phase Compact & Resume (WAL Rebind)
When context window limits are approached (e.g. 150k-300k tokens), transfer the session into a fresh chat without losing local state:
1. **Open:** Pin the local session's multi-agent prime binding and workspace so closing chat A does not abort active background jobs.
2. **Summary:** Prompt chat A for a comprehensive handoff brief (target 10k-30k tokens). Validate length via `briefShortfall` (reject briefs <1,000 characters for substantial sessions to avoid truncated state capture).
3. **Claim:** Open chat B with a unique continuation marker (`[[CLF-RESUME:<token>]]`). Enforce single-claimant verification to reject shadow collisions.
4. **Commit (3-Step Atomicity):**
   - *Preflight:* Freeze multi-agent swarm handovers; abort if handover is invalid.
   - *Durable:* Write the session rebind transaction atomically to the disk WAL.
   - *Publish:* Atomically update in-memory maps (conversation ID, workspace, swarm routing).
   - If any step fails, roll back cleanly to `abort` and keep session pinned to chat A.

---

## 4. Sandboxing & Execution Optimization

### QuickJS WASM Code Mode (Single-Turn Tool Composition)
- Instead of forcing 1 model roundtrip per tool call (LLM -> Tool 1 -> LLM -> Tool 2), expose a `code_mode` tool accepting JavaScript.
- Run JavaScript in an isolated WebAssembly QuickJS sandbox (`quickjs-emscripten-core`) inside a dedicated Worker thread.
- Expose MCP tools via `await tools.<name>(args)`.
- Intermediate results stay in WASM memory; only data explicitly emitted via `text(...)` or `image(...)` returns to the LLM context. This prevents megabytes of file/directory payloads from polluting LLM context.
- Enforce strict limits: CPU 2s, Wall-clock 60s, RAM 32MB, max 32 calls, payload caps.

### AST Command Interception (Tree-sitter Bash)
- Port upstream execution parsers using `tree-sitter` and `tree-sitter-bash` (AST query matching `apply_patch` heredocs).
- When models issue bash heredoc patches (`apply_patch << 'EOF' ... EOF`) inside `exec_command` on any OS (including PowerShell and cmd on Windows), unwrap and parse the AST to intercept the patch.
- Route directly to internal atomic patch engines without spawning host subshells or requiring external binaries.
