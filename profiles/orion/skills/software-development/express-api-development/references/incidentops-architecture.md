# SRE Incident Monitoring & Telemetry Architecture (IncidentOps)

## System Architecture

IncidentOps implements a lightweight, high-performance incident tracking and SRE telemetry dashboard using Express.js, SQLite with WAL mode, and responsive Vanilla HTML5/CSS/JS frontend.

### Core Endpoints & Payloads

- `GET /api/health`
  - Returns `{ status: "ok", version: "1.0.0", timestamp: ISO }`
- `GET /api/incidents`
  - Query params: `status`, `severity`, `service`, `search`, `limit`, `offset`
  - Returns `{ total: N, incidents: [...] }`
- `POST /api/incidents`
  - Body: `{ title, severity, service, description, reporter }`
  - Strict type checking on `severity` (`P1`, `P2`, `P3`, `P4`)
- `PATCH /api/incidents/:id`
  - Body: `{ status, severity, root_cause, assignee }`
  - Updates incident state and appends automatic timeline event if status changed.
- `POST /api/incidents/:id/updates`
  - Body: `{ message, status_change, author }`
- `GET /api/metrics`
  - Computes MTTR in minutes, severity distribution, status breakdown, and calculated SLA Health Score.

### Database Schema (SQLite WAL)

```sql
CREATE TABLE IF NOT EXISTS incidents (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    severity TEXT NOT NULL CHECK(severity IN ('P1', 'P2', 'P3', 'P4')),
    status TEXT NOT NULL CHECK(status IN ('investigating', 'identified', 'monitoring', 'resolved')),
    service TEXT NOT NULL,
    reporter TEXT NOT NULL,
    assignee TEXT,
    root_cause TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME
);

CREATE TABLE IF NOT EXISTS timeline_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id TEXT NOT NULL,
    author TEXT NOT NULL,
    message TEXT NOT NULL,
    status_change TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(incident_id) REFERENCES incidents(id) ON DELETE CASCADE
);
```

### Security & Container Hardening

- Security headers applied via Helmet (CSP, X-Content-Type-Options, X-Frame-Options, X-XSS-Protection).
- Payload size capped at 100KB to prevent memory exhaustion DoS.
- `.dockerignore` excludes `node_modules`, `.git`, temporary test files, and local logs.
- SQLite WAL mode ensures concurrent readers do not block transaction commits.
