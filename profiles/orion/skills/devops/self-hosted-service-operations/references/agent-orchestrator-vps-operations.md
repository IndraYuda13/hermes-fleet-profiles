# Self-Hosted AI Agent Orchestrator Operations & Hardening on Linux VPS

Panduan teknis dan operational runbook untuk menjalankan framework orkestrasi agent AI open-source (LangGraph, PydanticAI, LlamaIndex Workflows, AutoGen/AG2, Temporal) di VPS Linux mandiri.

---

## 1. Core Architecture & Resource Sizing Matrix

Menjalankan agent engine di single VPS (misal 2 vCPU / 4GB RAM) menuntut pemisahan state, runtime, dan model gateway untuk mencegah OOM-killer dan storage explosion.

| Komponen | Pilihan Rekomendasi (VPS Lean) | Alternatif Berat / Enterprise | Memory Footprint (Lean vs Heavy) |
| :--- | :--- | :--- | :--- |
| **Agent Engine** | LangGraph (Python Core) / LlamaIndex Workflows | LangGraph Cloud Server (Docker-in-Docker) | ~180MB - 350MB vs ~1.2GB+ |
| **State Persistence** | SQLite (WAL Mode) / Single Postgres | Distributed Postgres + Redis Cluster | 0MB (VFS) / 80MB vs 400MB+ |
| **Task Queue** | Postgres `FOR UPDATE SKIP LOCKED` | RabbitMQ / Celery / Kafka | 0MB extra vs 250MB - 600MB |
| **Model Gateway** | LiteLLM Proxy / 9router (Local Uvicorn) | Cloud-only SaaS Gateway | ~80MB - 150MB |
| **Observability** | Structured JSONL + systemd-journald + SQLite audit | Langfuse Self-Hosted (ClickHouse+PG+Node) | < 30MB vs 2.0GB - 3.5GB |

---

## 2. Hardening Invariants & VPS Pitfalls

### A. Non-Blocking SQLite WAL Persistence
Untuk single-worker atau low-concurrency multi-reader agents, konfigurasi SQLite via PRAGMA saat inisialisasi koneksi:
```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA busy_timeout = 5000;
PRAGMA cache_size = -64000; -- 64MB cache
PRAGMA temp_store = MEMORY;
```
*Pitfall:* Tanpa `busy_timeout` dan `WAL`, write lock saat LLM tool execution selesai akan memicu `sqlite3.OperationalError: database is locked`.

### B. Mencegah Storage Explosion pada State Checkpoint ($O(N^2)$)
Framework seperti LangGraph menyimpan snapshot state penuh pada setiap superstep. Jika agent mengambil dokumen web/PDF besar (misal 5MB raw text), 20 supersteps menghasilkan 100MB+ snapshot berulang di database.
*Best Practice:*
1. Strip raw tool outputs sebelum state disimpan ke checkpoint channel reducer.
2. Simpan payload besar (HTML/PDF/JSON blobs) di filesystem `/var/lib/agent/blobs/<sha256>` dan simpan pointer URI-nya saja di channel state dictionary.

### C. Systemd Resource Isolation & Auto-Recycle
Cegah memory leak dari akumulasi closure asyncio dan prompt graph yang tidak ter-garbage-collect dengan membatasi cgroup memori dan process worker recycle:

```ini
# /etc/systemd/system/agent-orchestrator.service
[Unit]
Description=AI Agent Orchestration Daemon
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/agent-platform
ExecStart=/opt/agent-platform/venv/bin/uvicorn app.main:app --uds /run/agent/app.sock --workers 2 --limit-max-requests 500
Restart=always
RestartSec=3s
MemoryHigh=1800M
MemoryMax=2200M
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### D. Disabling Silent Telemetry
Banyak framework AI modern (LangChain, CrewAI, ChromaDB, Pydantic Logfire) mengaktifkan auto-telemetry ke server cloud secara default. Matikan eksplisit di `/etc/default/agent-orchestrator`:
```bash
export OTEL_SDK_DISABLED=true
export CREWAI_TELEMETRY_OPT_OUT=true
export LANGCHAIN_TRACING_V2=false
export ANONYMIZED_TELEMETRY=false
```

### E. Idempotency on Worker Crashes & Resumption
Saat proses mati tiba-tiba (SIGKILL OOM) di tengah eksekusi node, worker akan me-reload checkpoint superstep sebelumnya. Jika tool node melakukan mutasi eksternal (mengirim webhook, transfer dana, order API), eksekusi ulang akan menduplikasi side-effect.
*Requirement:* Pasang header `Idempotency-Key` pada semua outbound mutating requests yang disimpan di state checkpoint.
