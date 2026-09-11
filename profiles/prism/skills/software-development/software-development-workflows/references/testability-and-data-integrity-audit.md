# Testability & Data Integrity Audit for Web, Cloud, and AI Applications

Use this guide when conducting a QA engineering, testability, and data-integrity audit on untested or legacy web applications integrating cloud SDKs (Firebase/Firestore, AWS, GCP), external AI APIs (Gemini, OpenAI, Anthropic), and multimedia/speech services.

## 1. Testability Gaps & Architectural Antipatterns

### A. Global Module-Level SDK Initialization
- **Smell:** Cloud client initialization (e.g. `firebase_admin.initialize_app()`, `firestore.client()`, `translate.Client()`, database connection pools) invoked in module root scope rather than inside an application factory.
- **Why it breaks tests:** Importing the module in a test runner (`import app`) triggers eager network connections, requires live credentials in test environments, or raises errors on duplicate initialization.
- **Audit rule:** Verify that client setup is encapsulated in an application factory (`create_app()`) or behind lazy dependency injection so tests can substitute mocks before instantiation.

### B. Hardcoded Inline Third-Party API Calls
- **Smell:** Direct instantiation of SDK model clients (e.g. `genai.GenerativeModel(...)`) inside route handlers without an intermediary service adapter.
- **Why it breaks tests:** Forces unit tests to monkey-patch internal third-party library classes rather than clear domain interfaces.
- **Audit rule:** Recommend a service layer (`LLMService`, `StorageService`) with injectable mock implementations or protocol boundaries.

### C. Unprotected Mutation Routes (Auth Boundary Holes)
- **Smell:** Global auth filters (e.g. `@app.before_request`) that whitelist or match URL prefixes (e.g. only `/admin`, `/guru`), leaving state-mutating endpoints like `/api/*` unauthenticated.
- **Why it breaks integrity:** Anonymous actors can post arbitrary data, corrupting state without going through session guards.
- **Audit rule:** Check all POST/PUT/DELETE routes against authentication/authorization decorators or explicit session checks.

### D. Client-Side Secret Leakage & Offloaded Processing
- **Smell:** Passing third-party API keys (e.g. STT/TTS service keys) directly into HTML templates so client-side JavaScript connects directly via WebSockets or REST.
- **Why it matters for QA:** Backend unit tests cannot verify service behavior because processing is entirely offloaded to the browser. Additionally, this introduces a severe credential leak.
- **Audit rule:** Verify whether backend services should act as an authenticated streaming proxy, or design browser-level E2E tests with WebSocket interception.

---

## 2. Data Integrity & Persistence Boundary Smells

### A. Raw String Entity Relationships (Missing Foreign Keys)
- **Smell:** Relational joins performed in application code using raw human-readable string fields (e.g. `class.teacher_name == user.name`) instead of immutable IDs or UUIDs.
- **Failure modes:**
  - Case sensitivity and capitalization mismatches requiring manual ad-hoc database patches (`name.title()`).
  - Name collisions across entities with identical names.
  - Silent orphaned records when an entity's display name is updated without cascading updates.
- **Audit rule:** Ensure documents store foreign keys (`teacher_id`, `class_id`) rather than mutable display strings.

### B. NoSQL Document ID Injection
- **Smell:** Constructing document paths from raw user input (e.g. `collection('items').document(f"{input}_{lang}")`).
- **Failure modes:**
  - Slash characters (`/`) in input strings are parsed as subcollection paths by document databases (such as Firestore), causing runtime `InvalidArgument` exceptions.
  - Unsanitized leading/trailing whitespaces create fragmented, unqueryable document keys.
- **Audit rule:** Verify that arbitrary user strings used as document IDs are hashed (e.g. SHA-256 or MD5 hex digest) or strictly sanitized.

### C. In-Memory Sorting & Workarounds for Missing Database Indexes
- **Smell:** Fetching unsorted collections to bypass database composite index requirements, then sorting in Python memory (`list.sort(key=lambda x: x['timestamp'])`).
- **Failure modes:**
  - Mixed-type crash: If legacy or dirty data contains both ISO string and datetime objects, Python 3 raises `TypeError: '<' not supported between instances of 'str' and 'datetime.datetime'`.
  - Memory bloat: Unpaginated queries fetch entire collections into RAM, degrading latency and crashing workers under load.
- **Audit rule:** Enforce database-level indexing, pagination (`limit`/`offset` or cursor tokens), and strict schema validation on write.

### D. AI Prompt vs Manual Fallback Contract Divergence
- **Smell:** An application provides an offline/fallback heuristic when an LLM API fails, but the fallback produces an inverted or structurally different output contract.
- **Failure modes:** Client receives different key names, reversed language directions, or unexpected array lengths depending on whether the AI call succeeded or fell back.
- **Audit rule:** Test both the online (AI) and offline (fallback) paths against the exact same JSON schema and linguistic contract.

---

## 3. Testing Strategy Blueprint for Brownfield Projects

| Layer | Target Surfaces | Tools & Approaches |
|---|---|---|
| **Refactoring** | App factory, service adapters, relational IDs | Move initialization into `create_app()`, wrap SDKs in service classes |
| **Unit Tests** | Helper logic, fallback generators, formatters | `pytest`, parameterize boundary cases (empty, `/`, non-ASCII, unicode) |
| **Mocking** | Third-party LLM & cloud APIs | `unittest.mock.patch`, test rate-limit (429) & timeout fallback branches |
| **Integration** | Auth boundaries, session guards, database queries | Flask test client (`session_transaction`), local database/Firestore emulator |
| **Browser E2E** | Multimedia flows, WebSocket STT, client interactions | Playwright with `--use-fake-device-for-media-stream` and WebSocket request interception |
