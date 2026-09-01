# Operator v1 RC1 — Runtime Verification Reference

Condensed operational patterns from Operator v1 RC1 verification and 9Router AI Integration.

## Release Structure

```
prediction-market-lab-operator-v1/
├── pyproject.toml          # prediction-market-lab 1.0.0rc1
├── .env.example            # Template for runtime config
├── scripts/
│   ├── verify_release.py   # Full release verifier (8 checks, 54 tests)
│   ├── pml.py              # CLI: demo-run, etc.
│   └── ...                 # Other verifiers (governing integrity, MCP, safety, etc.)
├── services/api/
│   ├── launcher.py         # uvicorn.run() entry point
│   └── main.py             # FastAPI app factory (create_app)
├── apps/dashboard/dist/    # Pre-built HTML dashboard
├── config/                 # Governing integrity manifests, test catalogs
├── data/fixtures/           # Fixture markets + evidence
└── tests/                  # 54 offline tests with offline_guard
```

## Verification Runbook (Step-by-Step)

### 1. Checksum
```bash
sha256sum prediction-market-lab-operator-v1.zip
# Compare against .sha256 sidecar
```

### 2. Extract & Install
```bash
mkdir clean-dir && cd clean-dir
unzip /path/to/prediction-market-lab-operator-v1.zip
cd prediction-market-lab-operator-v1
python3 -m venv .venv && source .venv/bin/activate
python3 -m pip install -e .
```

### 3. Release Verifier
```bash
python3 scripts/verify_release.py
```
Runs 8 sub-checks:
- governing_integrity (document hashes against v7 manifest)
- mcp_registry (contract SHA-256 pinning)
- safety_inventory (forbidden SDK/key/signing pattern scan)
- test_catalog (54/54 required tests discovered)
- offline_unittest (54 tests, offline guard enforced)
- compileall (bytecode compilation)
- dashboard_bundle (HTML + inline JS syntax)
- fixture_vertical_slice (full pipeline with demo market)

### 4. Demo Run (Deterministic Mode)
```bash
python3 scripts/pml.py demo-run --market demo_rate_cut_2026 --profile STANDARD
```
Expected output: JSON with run_id, probabilities, `RESEARCH_ONLY_QUARANTINE` rejection.

---

## 9Router AI Integration & Verification

To enable real LLM multi-agent forecasting via 9Router:

### 1. Pre-flight 9Router Probe
Ensure 9Router daemon is running on port 20128 and contains the target model alias (e.g. `ag-opus-pool`):
```bash
curl -sS http://127.0.0.1:20128/v1/models | grep "ag-opus-pool"
```

### 2. Direct 9Router Completion Smoke Test
Verify 9Router returns valid JSON for structured completion:
```bash
curl -sS \
  -X POST http://127.0.0.1:20128/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "ag-opus-pool",
    "messages": [{"role": "user", "content": "Return only a valid JSON object with exactly one field named probability whose numeric value is 0.5."}],
    "temperature": 0,
    "stream": false,
    "response_format": {"type": "json_object"}
  }'
```

### 3. Configure `.env` for 9Router LLM Mode
Create or overwrite `.env`:
```dotenv
PML_RUNTIME_MODE=RESEARCH_ONLY
PML_ENABLE_PAPER_MUTATIONS=false
PML_DATA_MODE=fixture

PML_LLM_MODE=9router
PML_LLM_GATEWAY_URL=http://127.0.0.1:20128/v1
PML_LLM_DEFAULT_MODEL=ag-opus-pool
PML_LLM_TIMEOUT_SECONDS=60
PML_LLM_MAX_RETRIES=1

PML_FORECAST_PROFILE=STANDARD
PML_API_HOST=127.0.0.1
PML_API_PORT=8000
PML_SQLITE_PATH=data/local/pml.db
PML_FIXTURE_DIR=data/fixtures
PML_EXPORT_DIR=data/exports
```

### 4. Application LLM Health Check
Start API launcher and probe application-level LLM status:
```bash
python3 -m services.api.launcher &
curl -sS http://127.0.0.1:8000/health/llm
```
Must return `"status": "ok"` and `"has_default_model": true`.

### 5. Execute AI Forecast Runs (FAST & STANDARD)
```bash
python3 scripts/pml.py demo-run --market demo_rate_cut_2026 --profile FAST
python3 scripts/pml.py demo-run --market demo_rate_cut_2026 --profile STANDARD
```

### 6. Audit Verification (9Router Origin Proof)
Inspect the generated audit ZIP under `data/exports/run_<ID>-audit.zip`:
1. Confirm `final_report.json` contains `model_alias: "ag-opus-pool"` for all agents.
2. Confirm absence of `"deterministic-fixture-v1"` and `"offline-deterministic-route"`.
3. Confirm `blind_forecasts` count (6 for STANDARD) and `final_forecasts` count (5 for STANDARD).

---

## API & Cloudflare Tunnel Deployment

### Endpoints
| Endpoint | Method | Notes |
|---|---|---|
| `/health` | GET | Returns `{"status":"ok"}` with db/llm health |
| `/health/llm` | GET | Returns gateway status, models, and default model flag |
| `/` | GET | Serves dashboard HTML from `apps/dashboard/dist/index.html` |
| `/api/markets` | GET | Returns fixture markets array |
| `/api/markets/{id}/analyze` | **POST** | SSE stream. **GET returns 405.** |
| `/api/runs/{id}/approve-paper` | POST | Requires `X-PML-API-Key` header |
| `/api/portfolio` | GET | Shows cash + positions |

### Cloudflare Tunnel Setup (vps-baru)
1. Systemd unit uses `/etc/cloudflared/config-vps-baru.yml` (NOT `config.yml`).
2. Add ingress rule:
   ```yaml
   - hostname: prediction-lab.indrayuda.my.id
     service: http://127.0.0.1:8000
   ```
3. Set CORS in `.env`: `PML_DASHBOARD_ORIGIN=https://prediction-lab.indrayuda.my.id`.
4. Route DNS: `cloudflared tunnel route dns --overwrite-dns b66c1298-4272-4138-99da-af993a3fa931 prediction-lab.indrayuda.my.id`.
5. Check for ghost PIDs (`ps aux | grep cloudflared`) to avoid stale connector load-balancing (1033 / 404 error).
6. Restart tunnel: `systemctl restart cloudflared`.

---

## Pitfalls & Troubleshooting

- **Port 8000 conflict:** Uvicorn fails if port 8000 is occupied by a previous launcher run. Run `fuser -k 8000/tcp` before launching.
- **SSE Endpoint is POST-only:** Requesting `GET /api/markets/{id}/analyze` returns HTTP 405 Method Not Allowed. Use `POST /api/markets/{id}/analyze?profile=FAST`.
- **Capability Secret Length:** `PML_CAPABILITY_SECRET` must be at least 32 characters, otherwise Pydantic validation fails on startup.
- **Multiple cloudflared Config Files:** Always run `systemctl cat cloudflared` to verify which config file is active before editing ingress rules.
