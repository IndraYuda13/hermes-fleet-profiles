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

---

## 7. External AI & Cloud API Resilience

### LLM & Cloud Service Integration Checklist
- **Model Version Pinning**: Pin AI models to official production versions (e.g. `gemini-1.5-flash`, `gemini-2.0-flash`), avoiding undocumented or experimental tags that may be decommissioned without warning.
- **Native Structured Output**: Use official SDK structured output / JSON schema enforcement (`generation_config={"response_mime_type": "application/json"}`) instead of fragile substring slicing (`find('{')` ... `rfind('}')`).
- **Reusable Client / Singleton**: Instantiate AI and translation client objects once during application startup, rather than re-creating them inside every request handler.
- **Explicit Timeouts & Batching**:
  - Always provide an explicit `timeout` parameter to external HTTP calls (e.g., `requests.post(..., timeout=5)`).
  - Use batch translation endpoints rather than sequential per-word translation loops.
