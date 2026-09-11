# Reverse-Engineering Modern Web AI & SPA APIs: PoW, WASM & SSE

Playbook for reversing protected SPA / Web AI chat interfaces (e.g. DeepSeek, Claude, ChatGPT web clients) into zero-dependency, pure Python standalone automation clients.

## 1. Traffic Capture Triage
When analyzing exported proxy dumps (Burp Suite, Mitmproxy, or HAR):
1. **Identify Required Auth vs Disposable Cookies:**
   - Filter `GET /` vs `/api/*` requests.
   - Check if API routes actually require CloudFront/AWS WAF cookies (`aws-waf-token`, `smidV2`) or if `Authorization: Bearer <token>` alone authenticates the call. Many API gateways pass authenticated bearer requests directly without inspecting browser cookies.
2. **Locate Dynamic Challenge Endpoints:**
   - Look for pre-flight challenge endpoints before major actions (e.g. `POST /api/.../create_pow_challenge`).
   - Check for external token pollers in frontend bundles (e.g. `https://hif-leim.deepseek.com/query` returning short-lived `x-hif-leim` tokens).

## 2. Reverse-Engineering Frontend PoW & WASM Modules
When an API gates requests behind a Proof-of-Work challenge (e.g. `DeepSeekHashV1`):
1. **Extract Web Workers from JS Bundles:**
   - Search the main bundle (`main.*.js`) for `Worker(new URL(...))` or keywords like `pow-challenge`, `pow-answer`.
   - Web apps often maintain two worker chunks:
     - A WASM worker (high-speed primary, e.g. `37627.*.js` + `sha3_wasm_bg.*.wasm`).
     - A pure JS fallback worker (e.g. `76608.*.js`) which reveals the uncompiled hashing logic.
2. **Deciphering Custom Hashes from JS Fallbacks:**
   - If standard `hashlib.sha3_256` or `keccak` fails to match the challenge, inspect the JS fallback absorb/squeeze loops.
   - Target variations: DeepSeek's `DeepSeekHashV1` is Keccak-256 with 32-bit word swapping on each 64-bit lane:
     - `absorb`: low word from bytes `[r+4..r+7]`, high word from bytes `[r..r+3]`.
     - `squeeze`: extracts high word `t[n+1]` first, then low word `t[n]`.
   - In Python, bitwise shifts must mask by 31 (`(32 - a) & 31`) to avoid `ValueError: negative shift count` when porting JS `>>> (32 - a)`.

## 3. Dual-Engine PoW Solving Architecture
To ensure maximum speed without sacrificing portability in standalone scripts:
1. **Primary: In-Memory WASM via Node.js Subprocess (~30-100ms):**
   - Base64-encode the extracted `.wasm` binary (~26KB) directly into the Python script.
   - Run a short Node.js one-liner via `subprocess.run(["node", "-e", script, wasm_b64, challenge_json])` compiling the WASM buffer in memory and executing `instance.exports.wasm_solve(...)`.
2. **Fallback: Pure Python Keccak (~2-5s):**
   - Provide a pure Python Keccak sponge implementation using only the standard library (`int` bitwise operations) so the script runs anywhere even if Node.js is absent.

## 4. SSE Fragment State Machine (Thinking vs Response)
Modern AI endpoints stream Server-Sent Events with distinct fragment lifecycle states:
1. **Fragment Transitions:**
   - An initial fragment definition arrives:
     `{"v": {"response": {"fragments": [{"type": "THINK", "content": "Initial"}]}}}`
     or `{"p": "response/fragments", "v": [{"type": "RESPONSE", "content": "First"}]}`
   - Delta tokens arrive via shorthand:
     `{"v": " token"}` or `{"p": "response/fragments/-1/content", "v": " token"}`
2. **Critical Pitfall - First Character Loss:**
   - Always extract the initial `content` string from the fragment definition object when `type` switches. If only delta updates are captured, the first letter/word of each fragment (`"We"`, `"Halo"`) is dropped.
3. **Status Filter:**
   - Ignore non-token updates such as `{"p": "response/status", "v": "FINISHED"}` so control strings are not appended to the output text.

## 5. Multi-Turn Context Chaining
- First request sets `"parent_message_id": null`.
- On `event: ready` or the first SSE event, capture `"response_message_id": <int>`.
- In subsequent turns of the same `chat_session_id`, pass `"parent_message_id": <prior_response_message_id>` to maintain conversation memory across the web API.

## 6. Client-Server Gateway Architecture via Cloudflare Tunnel
When distributing access to reversed Web AI endpoints or anti-bot scrapers across multiple client machines:
1. **Offload PoW and Anti-Bot to VPS Gateway:**
   - Client machines (laptops, mobile, developer workstations) often lack Node.js, have strict firewall restrictions, or struggle with CPU-intensive PoW hashing.
   - Run a 24/7 daemon on the VPS (e.g. FastAPI on an unprivileged loopback port like `:8550`) managed via systemd.
   - The daemon handles WASM PoW solving (`DeepSeekHashV1` in ~30ms), dynamic token polling (`x-hif-leim`), session management, and upstream SSE streaming.
2. **Expose via Cloudflare Tunnel:**
   - Map a dedicated subdomain (e.g. `deepseek.<domain>`) to the loopback daemon port in `config.yml`.
   - Expose standard OpenAI-compatible routes (`/v1/chat/completions` and `/v1/models`).
3. **Ultra-Lightweight Client Script:**
   - Client scripts require zero external packages and zero Node.js/WASM binaries. They make standard HTTPS requests directly to the tunnel endpoint.
   - **Crucial Invariant:** Cloudflare Edge Managed Rules block default Python urllib User-Agents (`Python-urllib/<version>`) with HTTP 403 Forbidden. Client scripts must always specify an explicit custom User-Agent header (e.g. `User-Agent: DeepSeekClient/1.0` or browser UA).

## 7. Smart Session Pool & Conversation Fingerprinting
When building an OpenAI-compatible gateway for stateful web chat platforms (such as `chat.deepseek.com`):
1. **The Flaw of a Single Global Session:**
   - Binding all incoming requests to a single global `session_state.json` creates cross-talk/context pollution: if Client A introduces themselves, an unrelated Client B running simultaneously will inherit Client A's context. This breaks OpenAI-like statelessness.
2. **OpenAI Statelessness vs Web Chat Stateful Mismatch:**
   - In OpenAI's `/v1/chat/completions`, the API is stateless; the client maintains history by re-sending the full `messages: [...]` array on each turn.
   - DeepSeek Web is stateful; it tracks a `chat_session_id` and tree pointers (`parent_message_id`).
3. **Conversation Fingerprinting (Session Affinity):**
   - Derive an immutable conversation identifier `conv_id` without requiring client changes:
     - **Priority 1 (Explicit Session):** Use `session_id` from JSON body or `X-Session-ID` header.
     - **Priority 2 (OpenAI User Field):** Use standard OpenAI parameter `user` (e.g. `client.chat.completions.create(..., user="session_1")`).
     - **Priority 3 (Root Message Fingerprint):** Compute `conv_id = f"conv_{sha256(messages[0].content)[:16]}"`.
       Because the initial user prompt remains unchanged throughout multi-turn turns 1, 2, 3... of that conversation, all turns naturally resolve to the exact same pool slot. Unrelated conversations automatically resolve to separate slots.
4. **Bounded LRU Session Pool & Upstream Auto-Pruning:**
   - Maintain an LRU pool of active sessions (e.g. `MAX_POOL_SIZE = 10`):
     - When a new `conv_id` arrives and the pool is full, evict the least recently used conversation.
     - Call the upstream deletion API (`POST /api/v0/chat_session/delete` with `{"chat_session_id": "<id>"}`) to immediately remove the evicted thread from the web account sidebar.
   - Guarantees:
     - 100% isolation between unrelated scripts, users, and sessions.
     - Seamless multi-turn continuity for ongoing conversations.
     - Web account sidebar never overflows or gets spammed with orphaned sessions.
5. **Auto-Healing on Stale/Deleted Sessions:**
   - If an upstream request returns HTTP 400 or 404 (indicating the session was deleted or expired), catch the error, allocate a fresh replacement session in the pool, and retry seamlessly.
6. **Native Token Prompt Serialization:**
   - To send self-contained multi-turn context without relying on server-side message tree state:
     `<｜begin of sentence｜><｜System｜>...<｜end of instructions｜><｜User｜>...<｜Assistant｜>...<｜end of sentence｜><｜User｜>...`
7. **FastAPI Internal Header Delegation Pitfall:**
   - When one FastAPI handler delegates directly to another (e.g. `/chat` calling `chat_completions(...)`), parameter defaults like `header_val: Optional[str] = Header(default=None)` evaluate to the FastAPI `Header` metadata object rather than `None`.
   - Never call string methods directly (e.g. `header_val.lower()`); always guard with `isinstance(header_val, str)` before checking header values.

## 8. Reverse-Proxy Git Packaging & OpSec Discretion
When publishing or packaging reverse-engineered API gateways or scrapers to GitHub:
1. **Never Use Overt Vendor Brand Names in Repositories:**
   - Avoid explicit trademarked names in repository names, package names, or public paths (e.g. use `ds-gateway` instead of `deepseek-web-api` or `deepseek-free-api`).
   - Use discrete abbreviations (`ds`, `tg`, `bs`) for projects that reverse private web APIs.
2. **Neutral Descriptions & Discretion:**
   - Keep repo descriptions functional, neutral, and academic/interoperability-oriented (e.g. *"Lightweight conversational gateway and proxy interface"*).
3. **Default to Private Visibility:**
   - When creating Git repositories for unofficial web reverse proxies or token gateways via CLI (`gh repo create`), always set `--private` by default. Never expose user account bearer tokens or direct web reverse bypasses publicly without explicit confirmation.
4. **Professional English Standard:**
   - All repository documentation (`README.md`), docstrings, schema descriptions, and environment configuration templates (`.env.example`) must be written in clean, professional English to maintain high craftsmanship standards.

## 9. Gateway Operational Health Audit & Diagnostic Protocol
When checking progress, diagnosing outages, or verifying runtime stability for self-hosted AI reverse gateways (e.g. `ds-gateway` on port `:8550`):
1. **Runtime & Port Verification:**
   - Check systemd status: `systemctl status <service>.service --no-pager`
   - Confirm listening port: `ss -tulpn | grep :<port>`
2. **Health & Pool Inspection:**
   - Query the health endpoint: `curl -s http://127.0.0.1:<port>/health`
   - Inspect upstream account status (`account.email`), service version, and `pool.active_conversations_count` to ensure the session pool is healthy and not leaking orphaned sessions.
3. **Ingress & Domain Mapping:**
   - Verify reverse proxy / Cloudflare Tunnel mapping in `/etc/cloudflared/config-vps-baru.yml` (e.g. `deepseek.<domain> -> http://127.0.0.1:<port>`).
   - Validate public HTTPS access: `curl -s https://<subdomain>.<domain>/health`.
4. **End-to-End Inference Verification:**
   - Perform a minimal 1-token prompt test to verify upstream auth and PoW solver health without wasting prompt tokens:
     ```bash
     curl -s -X POST http://127.0.0.1:<port>/v1/chat/completions \
       -H "Content-Type: application/json" \
       -d '{"model": "ds-chat", "messages": [{"role": "user", "content": "ping 1 word"}], "stream": false}'
     ```
   - Check both local loopback and the public tunnel URL to differentiate upstream API errors from Cloudflare edge blocks.
5. **Git Synchronization Check:**
   - Inspect repository working tree in project dir: `git status && git log -n 5 --oneline && git remote -v` to confirm features (e.g. session pool upgrades, bugfixes) are cleanly committed and synced with the remote repository.
