# Multi-Service Microservice Cluster Deployment & SRE Pattern

## Context & Architecture
When deploying applications where a central master/gateway daemon (e.g. FastAPI on port 8380) supervises and spawns child mock microservice subprocesses across a dedicated port range (e.g. ports 8381–8384):

## SRE & Reliability Best Practices

### 1. Dual Health Routing Aliases
Always expose both root `/health` and prefixed `/api/v1/health` on the primary gateway and each microservice mock. Automated test suites, external reverse proxies, and Kubernetes/systemd readiness probes frequently assume standardized prefix paths.

### 2. Pre-flight Socket Sweeps (`start.sh` and `stop.sh`)
Child mock processes spawned in the background or during application lifespan can outlive a master process crash or `SIGKILL`.
- In `start.sh`, run `fuser -k -n tcp <port>` across all assigned cluster ports prior to starting the master process to guarantee clean bindings.
- In `stop.sh`, follow a two-stage termination: graceful `SIGTERM` to the master PID, followed by explicit socket sweeps across the cluster port range (`fuser -k -15` then `fuser -k -9`) to guarantee zero zombie listeners.

### 3. Systemd User Unit Hardening
When wrapping multi-process Python clusters in systemd user units (`~/.config/systemd/user/<service>.service`):
```ini
[Service]
Type=simple
WorkingDirectory=/path/to/backend
ExecStart=/usr/local/lib/hermes-agent/venv/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8380
Restart=always
RestartSec=5s

# Isolation & Resource Ceilings
LimitNOFILE=65535
MemoryMax=1G
CPUQuota=200%
TimeoutStopSec=15s
KillMode=mixed
KillSignal=SIGTERM
```
`KillMode=mixed` ensures `SIGTERM` is sent to the main process first (allowing Python lifespan shutdown hooks to terminate child subprocesses), and after `TimeoutStopSec=15s`, any remaining child processes in the cgroup are forcefully cleaned up with `SIGKILL`.
