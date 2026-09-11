# FastAPI Probes, Entrypoints, and Systemd Service Architecture

## 1. FastAPI / Starlette HTTP HEAD 405 Pitfall

In FastAPI / Starlette, route decorators like `@app.get("/")` strictly match `GET` requests by default. They do NOT automatically handle HTTP `HEAD` requests.

### Symptom
- Automated uptime probes, cloud load balancers, container orchestrators, or CLI checks using `curl -I` or `curl -sI` receive:
  ```http
  HTTP/1.1 405 Method Not Allowed
  allow: GET
  content-type: application/json
  {"detail":"Method Not Allowed"}
  ```
- This causes monitoring systems to falsely flag a healthy web service as failing or offline.

### Solution
Use `@app.api_route` to register both `GET` and `HEAD` on root and health check endpoints:
```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={...})
```
Alternatively, for global coverage across all endpoints, add a lightweight middleware that rewrites `HEAD` requests internally to `GET` while discarding response bodies.

---

## 2. Root Entrypoint Proxy Pattern for Submodule Layouts

When a web app is organized into a subdirectory (e.g. `web/dashboard.py` or `src/api/server.py`), external tooling, systemd unit files, Docker containers, or user commands may expect a root-level import (`dashboard:app`).

### Solution
Place a lightweight proxy module at the repository root (`dashboard.py`):
```python
"""Root entrypoint proxy for FastAPI Dashboard."""
from web.dashboard import app

__all__ = ["app"]
```
Benefits:
- Allows both `uvicorn web.dashboard:app` and `uvicorn dashboard:app`.
- Avoids `ModuleNotFoundError` across different deployment scripts and interactive terminal checks.
- Preserves clean internal submodule directory structure without breaking legacy CLI contracts.

---

## 3. Decoupled Systemd Daemons: Worker + Telemetry Dashboard

When deploying background processing pipelines (e.g., video renderers, crawler workers, AI batch processors):

1. **Decouple Worker and Dashboard Services**:
   - `service-worker.service`: Dedicated to the continuous processing loop.
   - `service-web.service`: Dedicated to FastAPI/Uvicorn telemetry dashboard (e.g. port 8450).
   - If the worker crashes or uses high CPU/memory during rendering or downloading, the telemetry dashboard remains responsive and accessible.

2. **Environment & Log Streaming Essentials**:
   - Set `Environment=PYTHONUNBUFFERED=1` in both services so log events flush immediately to `journalctl` and file-based SSE streams without Python buffering lag.
   - Set `Environment=PYTHONPATH=/path/to/project/root` to guarantee consistent package imports.
   - **Memory & File Rotation Hardening for SSE Log Streaming**:
     * Avoid `f.readlines()` on active logfiles—it reads the entire file into RAM, blocking the asyncio event loop on large logs.
     * Seek to `max(0, file_size - 16384)` to stream only the last 16KB for initial buffer lines.
     * Guard against log rotation or truncation (`curr_size < last_pos`) by resetting `last_pos = 0`.
   - **Post-Upload / Intermediate Artifact Cleanup Invariant**:
     * In disk-heavy pipelines (video rendering, FFmpeg, Whisper, speech-to-text), prune raw and rendered artifacts (`*.mp4`, `*.ass`) immediately upon verified remote upload.
     * Protect deletion with strict containment validation (`resolved_path.is_relative_to(output_dir.resolve())`) to eliminate arbitrary file deletion vulnerabilities.
     * Update database records with explicit audit markers (e.g. `[UPLOADED_AND_CLEANED]`) while preserving pending/failed artifacts for manual review.
   - **Starlette / Jinja2 TemplateResponse Signature Compatibility**:
     * Modern Starlette (v0.28+ / 1.0+) requires `templates.TemplateResponse(request=request, name="index.html", context={...})` with explicit `request` or keyword arguments. Positional `(name, context)` raises `TypeError: unhashable type: 'dict'`.
   - **Dual-Target Logging & Interruptible Micro-Sleep for Daemons**:
     * Configure root logging with both `StreamHandler(sys.stdout)` (for `journalctl -u service`) and `FileHandler(log_path, mode="a", encoding="utf-8")` (for real-time SSE dashboard streaming).
     * Never use large blocking sleeps (`time.sleep(300)`) in daemon loops; sleeping in 1-second interruptible ticks (`for _ in range(interval): if not RUNNING: break; time.sleep(1)`) ensures `systemctl stop` or `SIGTERM` shuts down cleanly in <1s instead of hanging until the full interval expires.
     * Execute periodic WAL checkpoints (`PRAGMA wal_checkpoint(TRUNCATE)`) in the daemon loop after each processing cycle to prevent unbounded SQLite WAL journal file growth while web dashboards continuously read the DB.

---

## 5. Telemetry & Dashboard Database Schema Adapters (Zero-500 Invariant)

### Symptom
A web dashboard or API status endpoint returns `500 Internal Server Error` after a backend schema migration (e.g. migrating from a monolithic flat table like `clips` to normalized relational entities `uploads` JOIN `renders` JOIN `candidates` JOIN `videos`).
Common stack trace:
```text
sqlite3.OperationalError: no such column: processed_at
```
or queries return empty rows despite active processing records.

### Root Cause
1. Route handlers or background status inspectors execute raw SQL ordering by columns that only existed in legacy schemas (e.g. `ORDER BY processed_at DESC` vs `updated_at` / `discovered_at`).
2. Status inspection functions (e.g. `get_daemon_status()`) do not contain database exceptions; an unexpected schema mismatch or temporary lock bubbles up directly to Starlette middleware as an unhandled 500 error.

### Solution & Best Practices
1. **Dynamic Column & Table Detection**:
   Inspect available columns via `PRAGMA table_info(table)` and tables via `sqlite_master` before executing queries that vary across versions:
   ```python
   cursor.execute("PRAGMA table_info(videos)")
   cols = {row["name"] for row in cursor.fetchall()}
   order_col = "updated_at" if "updated_at" in cols else ("processed_at" if "processed_at" in cols else "discovered_at")
   ```
2. **Multi-Table Relational Adapter with Dual-Compatibility**:
   Check if modern normalized tables exist; if present, query the relational JOIN with COALESCE defaults; if absent, fall back gracefully to legacy tables:
   ```python
   cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='uploads'")
   if cursor.fetchone():
       # Query uploads JOIN renders JOIN candidates JOIN videos
       ...
   else:
       # Fallback to legacy clips table
       ...
   ```
3. **Fail-Safe Dashboard Inspection (Degrade Instead of 500)**:
   Live status inspectors must catch `Exception` around database telemetry calls and log warnings, returning a safe default state (`Active / Scanning` or `Offline / Stopped`) so transient database locks or schema updates never take down the web dashboard.

---

## 4. Direct Route Handler Invocation Pitfall (FastAPI `Query` / `Path` Default Objects)

### Symptom
When calling a FastAPI route handler function directly in Python unit tests or background scripts without passing all arguments:
```python
@app.get("/api/catalog")
async def get_catalog(
    page: int = Query(1, ge=1),
    sort: str = Query("title"),
    q: Optional[str] = Query(None)
): ...

# Direct test call:
res = await get_catalog(sort="rating")
```
Python raises runtime errors:
- `TypeError: unsupported operand type(s) for -: 'Query' and 'int'` (at `(page - 1) * pagesize`)
- `AttributeError: 'Query' object has no attribute 'strip'` (at `q.strip()`)

### Root Cause
When FastAPI handles an HTTP request through ASGI, its dependency injection mechanism inspects `Query(...)`, extracts and validates query parameters, and passes actual primitive values (`int`, `str`, `None`) into the handler.
However, when calling the async function directly in Python, omitted arguments evaluate to their default Python expressions—which are `fastapi.params.Query` descriptor objects rather than the underlying primitive defaults.

### Solution & Best Practices
1. **Defensive Parameter Normalization (In Handler)**:
   If a route handler may be invoked directly by internal helpers or unit tests, defensively sanitize parameter types:
   ```python
   page_val = page if isinstance(page, int) else 1
   pagesize_val = pagesize if isinstance(pagesize, int) else 24
   q_val = q if isinstance(q, str) else None
   sort_val = (sort if isinstance(sort, str) else "title").strip().lower()
   ```
2. **Use ASGI Test Clients for Route Testing**:
   Prefer calling FastAPI routes through `TestClient` or `httpx.AsyncClient` with `ASGITransport(app=app)` so FastAPI's full parameter injection and validation pipeline executes:
   ```python
   from httpx import AsyncClient, ASGITransport
   async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
       res = await ac.get("/api/catalog?type=anime")
   ```

