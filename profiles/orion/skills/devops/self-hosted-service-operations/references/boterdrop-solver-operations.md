# Boterdrop Solver (Camoufox) Operations

## Overview
Boterdrop-Solver is a high-performance solver for Cloudflare Turnstile, cf_clearance, Recaptcha V3, and AWS WAF tokens using FastAPI and Camoufox (stealth Firefox automation).

## Systemd & Service Details
- **Unit**: `/etc/systemd/system/boterdrop-solver.service`
- **Working Dir**: `/root/Boterdrop-Solver`
- **Venv Python**: `/root/Boterdrop-Solver/venv/bin/python3`
- **Local Bind**: `127.0.0.1:8008` (avoids colliding with default 8000)
- **Public Domain**: `https://boterdrop.indrayuda.my.id` (via Cloudflare Tunnel `config-vps-baru.yml`)

## Pitfalls & Best Practices

1. **Non-Interactive Startup (`EOFError`)**:
   - `api_server.py` prompts interactively by default (`input(...)`).
   - Guard entrypoint with `if os.environ.get("NON_INTERACTIVE") != "1" and sys.stdin.isatty(): config = _interactive_config(config)`.
   - Pass `Environment=NON_INTERACTIVE=1` in the systemd unit.

2. **FastAPI Lifespan Compatibility (`add_event_handler`)**:
   - Newer FastAPI / Starlette releases deprecate `add_event_handler`.
   - Pin `fastapi==0.95.2`, `starlette<0.28.0`, and `pydantic<2.0.0` or update handlers to modern Lifespan context managers.

3. **Camoufox Binary Cache Initialization**:
   - On first install, `camoufox fetch` and `playwright install-deps` + `playwright install firefox` MUST be executed explicitly in the venv before starting the daemon. Otherwise, startup fails with `FileNotFoundError: Version information not found at ~/.cache/camoufox/version.json`.

4. **API Endpoints**:
   - Create Task: `GET /turnstile?url=<target_url>&sitekey=<sitekey>` (Returns `202 Accepted` + `task_id`).
   - Poll Result: `GET /result?id=<task_id>` (Poll every 1-2s until status is `success`).
