# Pure Python Stdlib Multi-Threaded Telemetry, State & Action Server

## Overview

When building zero-dependency telemetry collectors, control panels, or status dashboards that run as systemd daemons alongside worker processes:

1. **Zero External Dependencies**: Use Python's standard library `http.server.BaseHTTPRequestHandler`, `http.server.HTTPServer`, and `socketserver.ThreadingMixIn`.
2. **Non-Blocking Multi-Threading**: By default, `HTTPServer` handles requests sequentially in a single thread. If an HTTP request does an upstream probe or browser polling overlaps, all other requests hang. Inheriting `ThreadingMixIn` with `daemon_threads = True` gives every connection its own worker thread.
3. **In-Memory TTL Caching**: High-frequency dashboard polling (e.g. 1-2s) will flood upstream APIs or proxy health endpoints. Use a lightweight in-memory cache with timestamp comparison (`now_ts - cache[key]['timestamp'] < TTL`).
4. **Thread-Safe & Atomic State Persistence**: When multiple worker threads or background tasks update shared state files (e.g. `fleet_state.json`, `sessions.json`, `config.json`), acquire a `threading.Lock()` and write to a thread/PID-specific temporary file before replacing with `os.replace` to prevent race conditions and corrupted JSON reads.
5. **Log-Driven Live State Extraction & Bounded Tail Seek**: When workers log structured activity, extract near-real-time metrics using bounded tail seeking (`f.seek(max(0, file_size - 65536))`) to prevent reading multi-megabyte log files into memory and keep daemon RAM consumption <30MB.
6. **Action Endpoints Security & Token Auth**: Protect all mutating action endpoints (`/api/actions/*`) with constant-time token comparison (`secrets.compare_digest`), inject the key into embedded single-file HTML dashboards, and validate headers (`X-Dashboard-Key` or `Authorization: Bearer`).

---

## Minimal Standard Architecture Pattern

```python
import json
import os
import re
import secrets
import subprocess
import threading
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from socketserver import ThreadingMixIn
from typing import Any, Dict, List, Optional, Tuple

_FILE_WRITE_LOCK = threading.Lock()
_GEO_CACHE: Dict[str, dict] = {}
_LAST_USER_FETCH: Dict[str, dict] = {}
CACHE_TTL = 15  # seconds

CONFIG_FILE = Path("config.json")
LOG_FILE = Path("bot.log")


def atomic_write_json(file_path: Path, data: Any, indent: int = 2) -> None:
    """Thread-safe and process-safe atomic JSON file writer using temp file replacement."""
    with _FILE_WRITE_LOCK:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = file_path.with_name(f"{file_path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
        try:
            content = json.dumps(data, indent=indent) + "\n"
            tmp_path.write_text(content, encoding="utf-8")
            os.replace(tmp_path, file_path)
        except Exception:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except Exception:
                    pass
            raise


def get_dashboard_api_key() -> str:
    """Retrieve or generate persistent dashboard API key."""
    if not CONFIG_FILE.exists():
        return "lw_sec_default_key"
    try:
        cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        key = cfg.get("dashboard_api_key")
        if not key:
            key = f"lw_{secrets.token_hex(16)}"
            cfg["dashboard_api_key"] = key
            atomic_write_json(CONFIG_FILE, cfg)
        return str(key)
    except Exception:
        return "lw_sec_default_key"


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


class TelemetryHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, data: Any):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Dashboard-Key, Authorization")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Dashboard-Key, Authorization")
        self.end_headers()

    def _check_auth(self) -> bool:
        """Validate dashboard API key via header, bearer token, or query param."""
        expected_key = get_dashboard_api_key()
        if not expected_key:
            return True

        header_key = self.headers.get("X-Dashboard-Key")
        if header_key and secrets.compare_digest(header_key.strip(), expected_key):
            return True

        auth_header = self.headers.get("Authorization", "")
        if auth_header.startswith("Bearer ") and secrets.compare_digest(auth_header[7:].strip(), expected_key):
            return True

        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        query_key = qs.get("key", [None])[0]
        if query_key and secrets.compare_digest(query_key.strip(), expected_key):
            return True

        return False

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            api_key = get_dashboard_api_key()
            # Live template reloading from disk with fallback to embedded string
            template_path = Path("dashboard_template.html")
            template_content = template_path.read_text(encoding="utf-8") if template_path.exists() else DASHBOARD_HTML
            html = template_content.replace("__DASHBOARD_API_KEY__", api_key)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
        elif parsed.path == "/api/stats":
            stats = get_latest_stats()
            self._send_json(200, stats)
        else:
            self._send_json(404, {"error": "Not Found", "path": parsed.path})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith("/api/actions/"):
            if not self._check_auth():
                self._send_json(401, {"status": "error", "message": "Unauthorized: Invalid or missing API key."})
                return

        if parsed.path == "/api/actions/retry":
            try:
                subprocess.Popen(["systemctl", "restart", "worker-service.service"])
                self._send_json(200, {"status": "ok", "message": "Worker restart triggered."})
            except Exception as e:
                self._send_json(500, {"status": "error", "message": str(e)})
        elif parsed.path == "/api/actions/refresh":
            _LAST_USER_FETCH.clear()
            _GEO_CACHE.clear()
            self._send_json(200, {"status": "ok", "message": "Caches invalidated."})
        else:
            self._send_json(404, {"error": "Endpoint not found"})

    def log_message(self, format, *args):
        # Suppress noisy standard request logging
        pass
```

---

## Log Parser State Machine Pattern & Tail-Seek Memory Guard

When log files grow into tens or hundreds of megabytes in long-running daemons, calling `log_path.read_text()` or `splitlines()` on every telemetry request will read the entire multi-megabyte file into memory and cause massive RSS memory spikes (hundreds of MBs) and GC pauses.

**Memory-Safe Tail Seeking Pattern (Constant O(1) Memory Overhead)**:

```python
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

def parse_bot_logs(log_path: Path, max_bytes: int = 65536, max_lines: int = 150) -> Tuple[List[str], Dict[str, List[str]], Dict[str, Dict[str, Any]]]:
    """Parse tail logs and extract live worker states without full-file read in RAM."""
    if not log_path.exists():
        return [], {}, {}

    try:
        file_size = log_path.stat().st_size
        if file_size == 0:
            return [], {}, {}

        seek_bytes = min(file_size, max_bytes)
        with open(log_path, "rb") as f:
            f.seek(file_size - seek_bytes, os.SEEK_SET)
            chunk = f.read(seek_bytes)

        decoded = chunk.decode("utf-8", errors="ignore")
        lines = decoded.splitlines()
        if seek_bytes < file_size and len(lines) > 1:
            lines = lines[1:]  # Discard partial leading line
        tail = lines[-max_lines:]
    except Exception:
        tail = []
        lines = []

    account_logs: Dict[str, List[str]] = {}
    account_live_state: Dict[str, Dict[str, Any]] = {}
    scan_lines = lines[-200:] if len(lines) > 200 else lines

    for line in scan_lines:
        m = re.match(r"^(\d{2}:\d{2}:\d{2})\s+\[(\w+)\]\s+(?:\[([\w\.-]+)\]\s+)?(.*)$", line)
        if not m:
            continue
        ts, level, tag, msg = m.groups()
        if not tag:
            continue

        acc = tag.lower()
        account_logs.setdefault(acc, []).append(line)
        if len(account_logs[acc]) > 150:
            account_logs[acc].pop(0)

        state = account_live_state.setdefault(
            acc,
            {
                "status": "ACTIVE",
                "current_task": None,
                "countdown_sleep": 0,
                "error_reason": None,
                "last_activity_time": ts,
            },
        )
        state["last_activity_time"] = ts

        if level == "ERROR":
            state["status"] = "ERROR"
            state["error_reason"] = msg
        elif "▶ Task" in msg:
            state["status"] = "ACTIVE"
        elif "Sleeping" in msg or "limit" in msg.lower():
            state["status"] = "SLEEPING"

    return tail, account_logs, account_live_state
```

---

## Security, Caching & API Protection on Public Tunnels

When exposing a telemetry or admin server via Cloudflare Tunnel or reverse proxy:
1. **Anti-Caching Response Headers for Real-Time Dashboards**: Proxies (Cloudflare/Nginx) and browsers aggressively cache HTML/JSON responses by default. Always include anti-caching headers on `GET /` and `GET /api/*`:
   ```python
   self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
   self.send_header("Pragma", "no-cache")
   self.send_header("Expires", "0")
   ```
2. **Live External Template Reloading**: Rather than relying strictly on an immutable in-memory constant (`DASHBOARD_HTML`), read `dashboard_template.html` from disk dynamically in `do_GET` with fallback to the embedded constant. This allows UI updates and hot-reloads to reflect immediately without requiring a full server restart.
3. **Upstream Nested API History Sorting & Normalization**: When parsing upstream paginated transaction or payout histories (e.g. `data.history.data` or `data.items`), never assume ascending or descending order. Explicitly sort by `unixtime` or `id` descending (`sorted(items, key=lambda x: int(x.get("unixtime", 0) or x.get("id", 0)), reverse=True)`) to ensure index `0` represents the true latest record.
4. **Mutating APIs**: Endpoints that execute actions (`/api/actions/withdraw`, `/api/actions/save_wallet`, `/api/actions/retry`) must require authentication (e.g. `X-Dashboard-Key` or `Authorization: Bearer <TOKEN>`).
5. **CORS & Auth Headers**: Explicitly allow `X-Dashboard-Key` and `Authorization` in CORS preflight `Access-Control-Allow-Headers`.
6. **Atomic State File Replacement**: Never write directly to live JSON files that are polled concurrently. Always write to `.tmp.<pid>.<thread_id>` and atomically rename with `os.replace`.
7. **Log Rotation**: Always pair file logging with `logging.handlers.RotatingFileHandler(maxBytes=10*1024*1024, backupCount=3)` so logs cannot grow unbounded on disk.
