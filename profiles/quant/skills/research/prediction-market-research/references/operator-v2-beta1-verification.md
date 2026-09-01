# PML Operator v2 Beta 1 Verification

The v2 Beta 1 verification involves confirming the release artifact, running tests, checking the fixture dashboard/API, using 9Router models, fetching live data (or confirming strict fails), ensuring Paper Auto local fills are idempotent, and dry-running against the new Execution Gateway.

## Test Pitfalls (FastAPI Lifespan)
During the offline `unittest` execution, an `AttributeError` for `add_event_handler` may occur due to newer FastAPI versions where `.add_event_handler` on the `app` instance is incompatible with background job binding techniques previously used.
**Fix**: Update `main.py` to use `contextlib.asynccontextmanager` for `lifespan`:
```python
import contextlib

@contextlib.asynccontextmanager
async def lifespan(app_instance: FastAPI):
    if cfg.AUTOPILOT_ENABLED and cfg.OPERATING_MODE in {"RESEARCH_AUTO", "PAPER_AUTO", "LIVE_AUTO"}:
        scheduler.start()
    yield
    await scheduler.stop()

app = FastAPI(..., lifespan=lifespan)
```
*Alternatively, standard `@app.on_event("startup")` decorators often bypass the direct attribute lookup error.*

Ensure `httpx2` and `httpx` are installed into `.venv` for the offline Starlette `TestClient` runs.

## Execution Gateway Dry-Run (`LIVE_CONFIRM`)
The Execution Gateway requires starting a separate background daemon via:
```bash
python3 -m services.execution_gateway.main
```
Or via uvicorn (port 8091):
```bash
python3 -m uvicorn services.execution_gateway.main:app --port 8091
```

Set:
```dotenv
PML_OPERATING_MODE=LIVE_CONFIRM
PML_LIVE_EXECUTION_ENABLED=true
PML_LIVE_EXECUTION_DRY_RUN=true
PML_EXECUTION_INTENT_SECRET=<32-char-secret>
PML_POLYMARKET_WALLET_ADDRESS=0x0000000000000000000000000000000000000000
PML_EXECUTION_GATEWAY_URL=http://127.0.0.1:8091
```

The gateway should return `"dry_run": true` in its `/health` status and `"status": "DRY_RUN_ACCEPTED"` on execution. It must not generate an `order_id` or submit real keys.