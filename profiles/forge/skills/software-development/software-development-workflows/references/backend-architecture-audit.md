# Backend Architecture & Systems Audit

Use this checklist and reference guide when conducting architectural audits, code reviews, or refactoring assessments of web backends, APIs, database integrations, and third-party service connections (Flask, FastAPI, Express, Firebase/Firestore, RTDB, AI APIs, STT streaming).

---

## 1. Concurrency Model & Multi-Worker State Isolation

### The Multi-Process In-Memory State Trap
- **The Trap**: Storing shared state, application-level cache (`_cache = {}`, `threading.Lock()`), session state, or rate-limiting counters (`f"otp_sent_{phone}"`) in global Python variables when running under multi-worker WSGI/ASGI servers (e.g., Gunicorn with `--workers 2+`, uWSGI, or Kubernetes multiple pods).
- **Failure Mechanism**: Each worker is an independent OS process with its own private heap memory. 
  1. **Split-Brain Cache Invalidation**: When Worker 1 mutates data and calls `clear_cache('list')`, Worker 2's cache is not cleared and continues serving stale data.
  2. **Rate-Limit Bypass**: Requests routed round-robin across workers bypass per-worker attempt counters and cooldown timers.
  3. **Unbounded Memory Leaks**: An in-memory dict without an eviction policy (LRU) or TTL cleanup thread accumulates stale keys indefinitely.
- **Auditor Verification**:
  - Check `Dockerfile` or process supervisor (`Procfile`, systemd) for `--workers > 1`.
  - Search code for global dictionaries holding cache or cooldown state.
- **Rule**: Never use in-memory dictionaries for shared state across worker processes. Use centralized in-memory stores (**Redis** / **Valkey**) or database-backed cache/rate-limiting abstractions (`Flask-Caching`, `Flask-Limiter` with Redis backend).

---

## 2. Third-Party Credentials & Client Exposure

### Master Key vs Ephemeral Scoped Token Boundary
- **The Pitfall**: Passing master API keys (e.g., Deepgram, speech-to-text, OpenAI, cloud storage) from server environment variables into client-side Jinja templates or frontend JavaScript to open client-direct WebSockets or HTTP calls.
- **Impact**: Any user or browser client inspecting page source or DOM can steal the master credential, drain account credit/quota (Denial of Wallet), or abuse administrative project capabilities.
- **Remediation Options**:
  1. **Ephemeral Key Minting**: Expose an authenticated backend endpoint (e.g., `GET /api/stt/token`) that calls the provider's management API to generate a temporary, scoped credential with a short TTL (15–30 minutes) and minimal permissions (`usage:write`).
  2. **Server-Side WebSocket / Audio Relay**: The browser streams media to the backend over WebSocket; the backend attaches the master credential and proxies the stream to the third-party service.

---

## 3. Database Access Patterns & Indexing (NoSQL / Firestore)

### Query Discipline Checklist
1. **No Full-Collection Scans (`.stream()` Anti-Pattern)**:
   - Flag any `db.collection('...').stream()` loop that evaluates filters (`if q in doc.get('name')`) or matches identifiers (`if doc.get('nip') == nip`) in Python memory.
   - Enforce database-level indexed lookups: `db.collection('...').where(filter=FieldFilter('nip', '==', nip)).limit(1).get()`.
2. **Composite Index Integrity**:
   - Verify that compound queries combining equality filters and sort orders (e.g., `.where('class_id', '==', id).order_by('timestamp', desc)`) have matching composite indexes defined in `firestore.indexes.json`.
   - Never remove `order_by` or pagination to bypass index requirements in favor of in-memory sorting; this causes massive memory bloat and breaks cursor-based pagination.
3. **Paging & Document Bloat**:
   - Large collections (session histories, audit logs, messaging threads) must enforce cursor-based pagination (`start_after(last_doc).limit(20)`).
   - Avoid downloading nested heavy arrays (e.g. dialogue transcripts) when only summary metadata is needed for listing pages.
4. **Relational Integrity & Entity Separation**:
   - Entities must reference other entities using immutable primary keys / document IDs (`guru_id`), never mutable display strings (`guru_name`), to prevent broken joins on capitalization or rename.
   - Do not reuse domain entity tables/collections (e.g. `kelas`) to store unrelated UI concepts (e.g. custom folders) with dummy fields (`jadwal: 'TBA'`).

---

## 4. Streaming Ingestion vs Synchronous Web Threads

### HTTP Ingestion Flooding Trap
- **The Anti-Pattern**: Client speech-to-text or streaming interfaces firing high-frequency HTTP POST requests (interim/final transcript chunks) directly to a synchronous WSGI route, which in turn performs synchronous writes to a database (e.g. Firebase RTDB `ref.set()`).
- **Failure Mechanism**: Continuous speech generates 5–10 chunks per second per active client. A synchronous WSGI server with limited worker threads (e.g. 2 workers x 4 threads = 8 concurrent slots) quickly experiences **Thread Starvation**, blocking all standard HTTP requests across the entire application.
- **Remediation**:
  - Decouple streaming ingestion from WSGI request threads: use WebSockets on an asynchronous ASGI engine (FastAPI/Aiohttp) or let clients write directly to Firebase RTDB using scoped security rules and Firebase Auth custom tokens.
  - Partition realtime keys by session/room ID (e.g., `/sessions/{session_id}/transcript`), never using hardcoded global keys (`teks_realtime`) which collide across multiple concurrent users.

---

## 5. Storage Architecture in Containerized Deployments

### Stateless Containers vs Ephemeral Local Filesystem
- **The Anti-Pattern**: Splitting media handling such that some files (e.g., learning modules) go to cloud object storage (Firebase Storage / S3) while other user assets (e.g., profile photos) are saved to local paths (`static/uploads/...`).
- **Failure Mechanism**: Modern production deployments run in ephemeral container runtimes (Cloud Run, Azure Container Apps, Kubernetes). The local filesystem is ephemeral and private to each container instance. Any restart, scaling event, or redeployment instantly destroys local uploads and creates 404 broken images across instances.
- **Rule**: All persistent user uploads must uniformly target remote object storage (Cloud Storage/S3), storing remote URLs or storage object keys in the database.

---

## 6. Authentication, Route Guards & Account Recovery Logic

### Audit Traps in Auth Flows
1. **Broken Access Control on API Prefixes**:
   - Verify that route guard middleware (e.g., `@app.before_request`) protects `/api/*` endpoints with the same rigor as web views (`/admin/*`, `/guru/*`). Unauthenticated API routes lead to IDOR and public proxy exploitation.
2. **Account Takeover in Password Reset Contact Fallback**:
   - **Vulnerability**: If an account does not have a registered contact number (e.g., `no_wa` is empty), allowing the user to provide an arbitrary number during the reset flow, sending an OTP to that number, and granting password reset permissions enables **100% account takeover** of any user lacking contact metadata.
   - **Rule**: Recovery flows must strictly verify existing, pre-registered contact information. If contact info is missing or unset, the flow must fail closed and require administrator intervention.
3. **Credential Hashing & Querying**:
   - Never store passwords in clear text or query passwords directly via database filters (`where('password', '==', password)`). Use cryptographic salted hashes (`scrypt`, `bcrypt`, `argon2id`) and verify using constant-time comparison (`check_password_hash`).
4. **CSPRNG for Verification Tokens**:
   - Never generate OTPs or reset tokens with `random.randint()`. Use the cryptographically secure standard library `secrets` module (`secrets.randbelow(900000) + 100000` for 6-digit OTPs).

### Password Authentication Migration Procedure

1. **Trace the real runtime path.** Read the deployed launch command, auth routes, provider HTTP adapter, user store, token lookup, refresh/logout, and fixture bootstrap. Prefer the native provider's signup/password-login SDK; if a local adapter is actually deployed, inspect and harden that adapter rather than presenting a test double's email-link reveal as genuine email verification.
2. **Freeze the public responses.** Define strict signup/login/enrollment payloads, fixed redirect, generic wrong/unregistered errors, and whether signup returns a session or confirmation-required state. Reject blank passwords without silently trimming meaningful password characters. Keep confirmation-password client-side unless the API explicitly needs it. Preserve origin checks, no-store responses and existing HttpOnly/SameSite/Secure cookie boundaries.
3. **Protect existing ownership.** Normalize email consistently and serialize registration by normalized email in a transaction. Refuse unauthenticated registration when any existing owner already has that email, even if no password credential exists; otherwise adding signup becomes legacy account takeover. Bind initial enrollment to the authenticated bearer subject, not caller-supplied email/UUID. Reject ambiguous duplicate historical emails and never overwrite an existing credential through signup. Use trusted recovery when the owner cannot authenticate.
4. **Persist secrets and sessions safely.** Store random per-user salt and a slow password hash such as scrypt, never plaintext or a password-based SQL predicate. Compare fixed-length hash bytes with timing-safe equality and perform comparable hash work for missing accounts. Keep credential/session tables private and absent from client-select/RPC allowlists. Store token digests with expiry, session identity and access/refresh kind; enforce kind during lookup, revoke the pair on local logout, and rotate refresh sessions. Prove lookup after a real provider restart rather than trusting a process-memory map.
5. **Close alternate authentication paths.** Remove public in-band link delivery and arbitrary-email auto-create fallbacks when moving to password auth. Retain legacy fixture paths only under an explicit internal flag plus independently isolated DB and loopback application configuration; fail closed when a public origin is configured. Seed sample accounts through the normal isolated setup runner, never by weakening the password/authentication branch.
6. **Bound abuse and leakage.** Apply durable per-email and per-IP throttling before expensive hashing, cap request size, and return constant errors without SQL/provider details. Verify proxy header sanitization before using forwarded IPs. Avoid deliberate SQL errors containing credential parameters, because database error context or statement logging can expose hashes or salts even when the HTTP response is generic. Keep synthetic passwords/tokens in memory and out of handoff artifacts.
7. **Verify the vertical path and release boundary.** Exercise actual HTTP signup, duplicate signup, correct/wrong/unregistered login, owner-class continuity, restart, access-vs-refresh confusion, authenticated legacy enrollment, unauthenticated takeover, rate limiting and logout. Test private-table privileges and malformed/null rate inputs. Run native-provider confirmation behavior at the route seam without claiming SMTP execution. Inventory pre-migration memory-only sessions and require enrollment/recovery before restart; durable new token storage cannot recover the previous process's token map. Obtain bounded independent auth review and integrated cookie/UI evidence before deployment.

---

## 7. Contract Freeze: Compatibility, Lifecycle, and Evidence Boundaries

Use this sequence before dividing backend and frontend implementation work. It is a design checklist, not proof that a proposed implementation works.

1. **Trace both validators.** Read the client schema and server SQL/RPC validator together, including schema registries and positional union consumers. Export named action schemas instead of indexing a discriminated union by array position, because adding actions can silently change the queue's accepted shape.
2. **Preserve strict legacy shapes.** If old clients reject unknown fields, negotiate a protocol version or use a separately versioned DTO; keep metadata in sidecars where immutable legacy documents must remain valid. Define omitted-field semantics for legacy saves so an old editor cannot erase new metadata. Test old client payloads against the upgraded backend and old cache/pending records against the new client.
3. **Freeze source snapshots.** Bind rendering, printing, grading, and capture to one immutable form/version/item order. Strip private keys and identities before passing print inputs to a renderer, because hiding them visually does not remove them from PDF metadata or embedded objects. Reuse scanner geometry only after verifying the binding still identifies the intended assignment and roster.
4. **Separate lifecycle axes.** Model assignment completion, parent activity closure, and assessment finalization independently. Allow authorized late evidence/corrections through the response path without reopening presentation grants; otherwise a late submission can accidentally resurrect a board. Exclude child runs from the parent results index to avoid duplicate activity rows.
5. **Preserve correction provenance.** Keep response revisions and distinguish assessment time from correction-recorded time, because a rescan is not a new assessment. Import only history that exists; do not invent previous revisions when the predecessor database stored only the current answer.
6. **Represent uncertainty explicitly.** Keep blank, unreadable, pending review, absence, explicit unknown answers, and observed incorrect answers distinct. Do not coerce missing evidence into a non-null level to satisfy an older domain type. Require explicit comparability rules before ranking results from different forms or versions; matching topic labels alone does not establish equivalent difficulty. Keep group activity outcomes out of individual assessment evidence unless a separately valid individual observation exists.
7. **Protect check/commit boundaries.** If deterministic checking runs outside the database, authorize the exact saved input, compute server-side, then commit under revision/input CAS. Never let a directly callable RPC accept client-supplied correctness. Check current grant/epoch authorization before returning idempotency receipts, because a retry must not recover revoked access.
8. **Challenge simultaneous state.** Test duplicate advance, teacher/board races, reconnect with rotated grants, corrected evidence for the next activity, and unchanged membership/evidence snapshots for active and historical activities. A contract inspection cannot substitute for these runtime gates.

---

## 8. Bound PDF and Scan-Surface Remediation

Use this sequence for a small readable-label/binding repair without redesigning a scan-compatible document.

1. **Trace the binding source.** Inspect the question-sheet helper, answer-card drawing, QR serializer, layout, font, and saved-PDF tests. Derive the human-readable code/version from the same frozen form as the QR; a layout version is not the assignment version, and a machine-readable QR alone does not help match mixed paper piles.
2. **Write a saved-output red assertion.** Generate real PDF bytes, save them in the managed scratch directory, and extract text with `pdftotext file.pdf -`. Assert the exact code/version and expected repeated-card count. Do not treat intercepted renderer calls as proof that the saved PDF contains the text.
3. **Reuse the existing header slot.** Replace a generic subheading when sufficient, preserving coordinates/font size and all marker, bubble, QR, and layout commands. Measure `x + font.widthOfTextAtSize(label, size)` against the QR's left edge in consistent units, including the largest supported version label, because normal short labels can hide an overlap at the boundary. Keep unbound/legacy branches unchanged.
4. **Decode the saved QR, not its input.** For pdf-lib vector QRs, load the saved document, decode its content streams, recover black filled rectangles inside each known QR bounding box, rasterize those rectangles into RGBA, and pass the pixels to jsQR. Assert every printed cell decodes to the frozen form/version/page/row payload. This detects serialization/rendering defects that checking the original payload string misses.
5. **Exercise affected scan paths.** Run saved-PDF, legacy-card, synthetic OMR, and capture regression suites after changing drawing output. Preserve the distinction between an explicit unknown answer and blank/unreadable states. Do not weaken geometry or decoder assertions to accommodate a text-only change.
6. **Produce the matching pair.** Generate question and answer sheets with the same synthetic immutable binding; run `pdftoppm -png -r 120 -singlefile file.pdf output-prefix` for each single-page sheet, or render every page for multi-page output. Record PDF/image paths, source revision, and hashes. Rasterization is not independent visual clearance, and synthetic OMR is not physical printer/camera certification.
7. **Close the bounded slice.** Commit only the drawing and narrow regression test, report actual counts/exits and artifact paths, and hand final pair rendering/build integration to its owner. Do not mutate already-frozen backend/migrations merely because a print issue is discovered late.

## 9. External AI & Cloud API Resilience

### LLM & Cloud Service Integration Checklist
- **Model Version Pinning**: Pin AI models to official production versions (e.g. `gemini-1.5-flash`, `gemini-2.0-flash`), avoiding undocumented or experimental tags that may be decommissioned without warning.
- **Native Structured Output**: Use official SDK structured output / JSON schema enforcement (`generation_config={"response_mime_type": "application/json"}`) instead of fragile substring slicing (`find('{')` ... `rfind('}')`).
- **Reusable Client / Singleton**: Instantiate AI and translation client objects once during application startup, rather than re-creating them inside every request handler.
- **Explicit Timeouts & Batching**:
  - Always provide an explicit `timeout` parameter to external HTTP calls (e.g., `requests.post(..., timeout=5)`).
  - Use batch translation endpoints rather than sequential per-word translation loops.
