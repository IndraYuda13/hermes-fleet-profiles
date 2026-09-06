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
