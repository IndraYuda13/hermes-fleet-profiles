---
name: a2a-fleet-orchestration
description: Use when orchestrating multi-agent A2A pipelines.
version: 1.0.0
metadata:
  hermes:
    tags: [orchestration, a2a, fleet, multi-agent]
    category: custom
---

# A2A Fleet Orchestration Patterns

## When to use

Orchestrating work across fleet specialists via A2A calls — UI build pipelines, research fan-out, multi-phase QA, or any mission requiring sequential or parallel specialist dispatch.

## A2A Timeout Management

Large prompts (>500 words with embedded specs, code samples, or multi-step instructions) and long-running execution (headless browser audits, extensive test suites) frequently cause A2A agent timeouts. Proven countermeasures and architectural rules:

### Dual-Timeout Architecture (Outbound Client vs Inbound Gateway Server)
A2A timeouts operate across two independent boundaries:
1. **Outbound Client Timeout (`config.yaml`):** Set under `a2a_agents.<peer>.timeout` on the calling profile. Dictates how long `urllib.request.urlopen` in `tools.py` waits before raising `[agent did not reply in time]`.
2. **Inbound Gateway Deadline (`.env`):** Evaluated by `_reply_timeout()` in `plugins/platforms/a2a/adapter.py` on the receiving profile, reading `os.getenv("A2A_REPLY_TIMEOUT", "300")`. If the receiving gateway's worker turn does not finish within this deadline, the adapter returns `protocol.STATE_FAILED` with `[agent did not reply in time]`.
3. **Queue Wait Accumulation Pitfall:** Inbound deadline is computed as `pending["started"] + _reply_timeout()` where `started` is timestamped immediately upon HTTP `SendMessage` receipt. Time spent waiting in queue while the gateway process finishes prior turns or acquires locks counts directly against the timeout budget.
4. **Symmetric Target Matrix Invariant:** Setting outbound timeout to 1800s while inbound `A2A_REPLY_TIMEOUT` remains 300s causes failure at exactly 300s. Whenever timeouts are adjusted, synchronize BOTH caller `config.yaml` (`a2a_agents.<target>.timeout`) AND receiver `.env` (`A2A_REPLY_TIMEOUT=<target>`). Target baseline:
   - LENS / PRISM / SENTINEL / ORION: 1800s (30m)
   - FORGE / FRAME / AURORA: 1200s (20m)
   - ATLAS / RADAR / QUANT: 900s (15m)
   - NEXUS: 600s (10m)

### Fleet Gateway Rolling Restart Protocol
Outbound tools reload config dynamically via `_load_config()`, but inbound gateway adapters read `os.environ` and bind listeners during startup. Changes to inbound timeouts require gateway process restarts.
- **Zero Fleet Blackout:** Never stop or restart all gateways concurrently. Never touch the model provider/router (`localhost:20128`).
- **Sequential Rolling Step:**
  1. Restart single user unit: `systemctl --user restart hermes-gateway-<profile>.service`.
  2. Poll `GET http://127.0.0.1:<port>/health` until response JSON contains `{"status": "ok"}` (typically 3–15s).
  3. Confirm port listening before advancing to the next peer.
- **Supervised Gateway Self-Restart Invariant:**
  An agent session running inside its own gateway (e.g. ORION running on `hermes-gateway-orion.service`) is blocked by `terminal_tool_guards.py` from directly invoking `systemctl restart hermes-gateway-<self>` because SIGTERM would kill the calling turn and subshell mid-flight.
  - To safely restart the orchestrating gateway, request graceful restart via control socket (`{"verb": "pause-for-update"}` to `gateway.sock`) or trigger it via a detached helper that waits for active turns to drain, or prompt the human operator before session close.
- **Two-Way A2A Reverse Smoke Test Invariant:**
  Never assume bidirectional connectivity from outbound pings alone (e.g. ORION -> LENS passing does not prove LENS -> ORION is healthy). Always verify the reverse direction (LENS -> ORION, PRISM -> ORION, etc.) using direct A2A JSON-RPC `SendMessage` calls to ensure the inbound receiver loop, context dispatch, and reply serializers function without effective 300s timeout or socket errors.

### Progressive decomposition (preferred)
Break a large specialist task into a multi-turn A2A conversation using `context_id` continuation:
1. Start with the smallest self-contained subtask (e.g., "create PRODUCT_CONTEXT.md").
2. Confirm completion in the response.
3. Issue the next piece in the same context (`context_id` from prior reply).
4. Each turn stays under ~300 words of instruction.

### Availability ping
If a specialist times out twice, send a minimal ping ("Are you available? Reply 'yes'") to distinguish connectivity failure from prompt-size timeout. If the ping succeeds, the problem is prompt size — decompose further.

### Concise prompt retry
When an initial comprehensive consultation times out on a specialist (common with broad audits, threat modeling, or multi-point checklists), do not abandon the peer or repeat the verbose prompt. Immediately dispatch a concise retry: compress the request into 3–4 essential bullets and request an evidence manifest. This reliably completes within the turn timeout while capturing critical domain coverage.

### Mechanical fallback routing
When a specialist (e.g., LENS for visual QA) repeatedly times out on a combined task (inspect + capture + write report), split mechanical from judgment:
- Route mechanical capture (screenshots, file generation, grep checks) to an available general agent (e.g., FORGE).
- Then route the assessment/judgment to the specialist with mechanical work already completed.
- This preserves separation of duties: the specialist still owns the verdict.

## Evidence Manifest Git Revision Strategy

Manifests committed inside a git repo can NEVER self-referentially contain their own commit SHA. SHA-1's avalanche effect makes `amend` loops diverge forever — this is an inherent property of content-addressed storage.

Correct pattern:
1. FRAME commits implementation code → record this as the **implementation commit SHA**.
2. All evidence manifests reference the implementation commit SHA (the code they verified).
3. QA reports, screenshots, and manifests are committed in a separate evidence commit.
4. The evidence commit's SHA is different from what manifests contain — this is expected and correct.

Do NOT attempt iterative `git commit --amend` to make manifest content match its own commit hash.

## Multi-Turn A2A Conversation Architecture

For complex specialist work (e.g., AURORA creating 5+ design documents):

```
Turn 1: Create PRODUCT_CONTEXT.md → confirm
Turn 2 (same context): Create REFERENCE_LEDGER.md → confirm  
Turn 3 (same context): Create DESIGN_DIRECTIONS.md → confirm
Turn 4 (same context): Create DESIGN_DNA.md → confirm
Turn 5 (same context): Create DESIGN_CONTRACT.md + manifest → confirm
```

Benefits: each turn stays fast, agent has growing context from prior work in same thread, failures are isolated to one artifact.

## Pipeline Execution Order

For UI build missions with evidence requirements:
1. Design (AURORA) — creates specs, no git commit
2. Implementation (FRAME) — creates app code, commits to git
3. Functional QA (PRISM) — tests at implementation commit, writes report, no commit
4. Visual QA (LENS) — screenshots + assessment at implementation commit, no commit
5. Evidence packaging (FORGE) — commits all QA artifacts, closure report, manifests
6. Closure (ORION) — synthesis and verdict, zero production edits

Only FRAME and the evidence-packaging step should commit to git. Verifiers MUST NOT edit app/ source.

## Pitfalls

- Do not send the full design spec as part of the FRAME prompt — tell FRAME to read the files already in the workspace.
- Do not ask verifiers to commit — their files get committed in the evidence-packaging phase.
- Screenshot capture is a mechanical task; if LENS times out, FORGE can capture PNGs and LENS can assess existing files.
- `a2a_orchestrate` is for independent parallel tasks only; sequential pipeline phases must use sequential `a2a_call`.
- For fleet-wide broadcasts or roster syncs (e.g. all 10 peers introducing themselves or responding to a uniform prompt), use `a2a_orchestrate(capability='*', mode='all')` for single-shot parallel dispatch rather than 10 sequential calls.
- On read-only audit/investigation missions ("jangan lakukan improvement langsung"), explicitly stamp `READ-ONLY AUDIT: DILARANG MODIFIKASI KODE/FILE` into every outbound A2A prompt to ensure execution-capable peers (FORGE, FRAME, ATLAS) do not perform speculative mutations.
- When the user asks "tanya mereka langsung" regarding readiness/availability, immediately contact the involved peers via `a2a_call` (continuing their respective `context_id`), collect their first-person statements and execution plans, and present them directly to the user rather than speaking on their behalf from static role knowledge.
- **Serial Incremental SDLC Invariant ("1 Point Improvement = 1 Putaran SDLC"):** When the user mandates step-by-step improvement execution without rushing ("1 per 1 dikerjakan, di-test, di-verifikasi lalu lanjut ke point berikutnya"):
  1. Tag the initial repository state as a stable baseline (e.g. `git tag vX.Y.Z-stable-baseline`).
  2. NEVER batch multiple functional improvements into a single monolithic task or commit. Decompose each distinct improvement into its own dedicated Kanban lifecycle: Implementer (FORGE/FRAME) -> Verifier/Deployer (ATLAS/PRISM) -> Verification suite pass -> Git commit/tag.
  3. Verify each point against both unit test suites and live runtime regression checks before promoting to the next iteration.
- **Nginx Socket Binding Reload vs Restart:** Changing Nginx listen directive from a wildcard IP (`0.0.0.0:PORT`) to loopback (`127.0.0.1:PORT`) causes a socket binding collision (`bind() to 127.0.0.1:PORT failed (98: Address already in use)`) during `nginx -s reload` or `systemctl reload nginx` because the existing master process holds the `0.0.0.0` descriptor. A clean service restart or graceful stop-and-start is required to re-bind the socket cleanly.
- **Kanban Task Creation Title Requirement:** `kanban_create` strictly requires the `title` parameter; passing only `assignee` and `body` fails immediately with `ValueError: title is required`. Ensure `title` is always supplied.
- **Deploying Service Workers (`sw.js`) & Companion Ad Tags for Monetization / Push Networks:**
  When integrating ad network tags (e.g., Quge5, Monetag, PropellerAds, 5gvci):
  1. **Root Service Worker (`sw.js`):** Write file directly to frontend static root (`frontend/sw.js`). Validate syntax with `node -c frontend/sw.js`. Ensure Nginx serves it at `/sw.js` with `Content-Type: application/javascript` and `Cache-Control: no-cache`. Verify via `curl -sI https://domain/sw.js` (HTTP 200 OK).
  2. **Service Worker Client Registration Invariant:** Placing `sw.js` on the web server alone does NOT run push notification ads. Modern web browsers require explicit registration from the web page via `navigator.serviceWorker.register('/sw.js')`. Without this client-side call, the service worker is never activated by visiting users.
  3. **Zone ID Audit & Account Synchronization:** Always verify that the `zoneId` inside `sw.js` matches the active zone assigned to the exact domain in the ad network dashboard or API (e.g. via MCP `get_zones`). Do not leave placeholder or foreign snippet zone IDs.
  4. **In-Page Companion Script Tag:** Place the tag (`<script src=".../tag.min.js" data-zone="..." async data-cfasync="false"></script>`) immediately before `</body>` to prevent blocking initial HTML/CSS rendering.
  5. **Cloudflare Rocket Loader Guard (`data-cfasync="false"`):** Cloudflare Rocket Loader by default rewrites script tags to `type="text/rocketscript"`, which breaks the ad tag's event listeners (onclick/popunder) and Service Worker registration handshake. Ensure `data-cfasync="false"` is preserved on the script element.
  6. **Ad Format Expectations (OnClick / Popunder vs Static Banners):** Be aware that scripts like `tag.min.js` (e.g. Quge5) are typically OnClick / Popunder formats that do not render visual banner elements upon page load, but trigger new tab popunders on the first user interaction, often subject to frequency capping (`locked: true`).
  7. **Verification:** Test that (a) `sw.js` returns HTTP 200 with correct zoneId, (b) `navigator.serviceWorker.getRegistrations()` returns an active registration in browser runtime, (c) companion tag script executes without unhandled errors, and (d) full frontend Playwright test suite passes.
- **Remote HTTP / SSE MCP Server Diagnostics & OAuth 2.1 PKCE Flow (e.g. Monetag MCP):**
  When tasked with connecting external/third-party MCP services over HTTP (e.g. `https://mcp.monetag.com/`):
  1. **Probe HTTP Auth & Metadata:** Probe `GET /` (with `Accept: text/html` to read human setup guides like Claude/ChatGPT setup) and probe `GET /mcp` or `GET /sse` without credentials. Inspect the 401 response `WWW-Authenticate` header to extract `resource_metadata` (e.g., `/.well-known/oauth-protected-resource`). Fetch that endpoint to discover `authorization_servers`, `scopes_supported`, and authentication mechanics.
  2. **Detect SSE Transport:** A request with Bearer auth to `/mcp` or `/sse` returning HTTP 406 with `jsonrpc: 2.0, code: -32000, message: "Not Acceptable: Client must accept text/event-stream"` definitively identifies an SSE-based MCP transport.
  3. **Dynamic Client Registration (RFC 7591) & OAuth 2.1 PKCE:** Many modern MCP providers (such as Monetag, Claude custom connectors) do NOT have a manual "API Key / Personal Token" menu in their web dashboard. Instead, they implement OAuth 2.1 with PKCE:
     - Check `GET /.well-known/oauth-authorization-server` on the authorization server (e.g. `https://publishers.monetag.com/`).
     - Register a dynamic client via `POST <registration_endpoint>` with `{"client_name": "Hermes Agent", "redirect_uris": [...]}` to receive a dynamic `client_id`.
     - Generate a PKCE `code_verifier` (64-byte urlsafe token) and `code_challenge` (SHA256 base64url-encoded).
     - Construct the web login authorize URL: `<authorization_endpoint>?response_type=code&client_id=...&redirect_uri=...&scope=...&state=...&code_challenge=...&code_challenge_method=S256`.
     - Give the user the clickable authorization link. Once approved, extract `code` from the callback redirect URL and exchange it via `POST <token_endpoint>` (`grant_type=authorization_code`) to obtain the `access_token` and configure Hermes MCP.
  4. **Headless / Remote VPS OAuth Callback Relay (`mcp-remote` Port 10266):**
     When `mcp-remote` starts an OAuth callback server on `localhost:10266` on a remote VPS, opening the authorization link in the user's local PC/mobile browser causes the post-login redirect to fail locally (`ERR_CONNECTION_REFUSED` on `http://localhost:10266/oauth/callback?...`).
     - *Workaround:* Instruct the user to copy the entire redirect URL from the address bar (containing `?code=...&state=...`) even though the page displays connection refused.
     - Have the agent make an internal loopback GET request on the VPS: `urllib.request.urlopen("http://127.0.0.1:10266/oauth/callback?code=...&state=...")`.
     - The listening `mcp-remote` process intercepts the code verifier, successfully completes the token exchange, and persists the session without requiring port-forwarding or reverse proxy setup.
  5. **Authorization Code Ephemerality & Persistent Direct Python PKCE Exchange:**
     OAuth 2.1 authorization codes (e.g. Monetag) are single-use and expire rapidly (~60s). If the callback request is delayed, background daemon dies across tool turns, or code replay occurs, the server responds with HTTP 400 `{"error":"invalid_request","hint":"Authorization code has expired"}`.
     - *Anti-Flake Pattern:* Avoid relying on ephemeral background `npx mcp-remote` daemons across multi-turn chat loops.
     - Direct Python Flow: (1) Register dynamic client (`POST /api/oauth2/register`), (2) Generate PKCE `code_verifier` and save to persistent storage (e.g. `/root/.hermes/<service>_active_oauth.json`), (3) Construct authorization URL with `code_challenge`, (4) When user supplies callback redirect URL, immediately extract `code` and execute direct token exchange via `POST /api/oauth2/token` using the stored `code_verifier`.
     - Persist the acquired `access_token` and `refresh_token` directly into `/root/.hermes/config.yaml` and profile config under `mcp_servers.<name>`.
     - Also save tokens in mcp-remote cache format (`/root/.mcp-auth/mcp-remote-v1/<serverUrlHash>_tokens.json`) to allow CLI and subagent toolkits to use the connection out of the box.
     - Verify with `hermes mcp test <name>` and live tool execution (`tools/call` with `Accept: application/json, text/event-stream`).
- **Task Drift Guard / Prerequisite Precedence Invariant:**
  When a user injects an immediate setup or prerequisite task ("pertama tama connect mcp dia dlu", "setup ini dulu"):
  1. Freeze secondary or broad exploration tasks (e.g. site audits, roadmaps).
  2. Maintain 100% execution focus on completing the prerequisite task until verified or definitively blocked.
  3. Never jump ahead to answering an earlier broad request while the immediate prerequisite is pending or half-completed.
  4. Explicitly confirm prerequisite completion with live tool evidence before resuming deferred roadmap discussions.
- **Factual Codebase Improvement Audits ("Bukan Hal yang Dibuat-buat"):**
  When tasked with auditing an existing project to propose real improvements across UI/UX, Frontend, Backend, QA, and Security:
  1. **Strict Zero-Hallucination Invariant:** Do not invent missing features or report hypothetical bugs. Every claimed improvement point MUST be grounded in an inspected file, DOM element, CSS rule, or API endpoint.
  2. **Inspection Checklist:**
     - Check native API availability vs implementation (e.g. HTML5 `requestPictureInPicture()`, Fullscreen API, PWA `manifest.json`).
     - Check unbounded array rendering in SPA rails (e.g. lack of pagination / chunking for 100+ episodes).
     - Check accessibility and state persistence (`localStorage` for watchlists, search history, playback speed).
     - Check backend defense-in-depth (rate limiters on video streaming endpoints, cache-control headers on static vs dynamic assets).
  3. **Reporting Format:** Structure every proposed point into: (a) *Kondisi Riil Saat Ini* (with file & line / grep evidence), (b) *Masalah UX / Performa / Keamanan*, (c) *Solusi / Rekomendasi Konkret*.

## Reference Documents
- `references/ad-network-and-mcp-monetag.md`: Detailed end-to-end guide for Monetag OAuth 2.1 PKCE MCP integration, Service Worker push monetization, and ad deactivation/cleanup runbooks.
