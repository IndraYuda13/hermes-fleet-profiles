# MAI V3 Science Layer & n8n CLI Workflow Lessons

## Session Pitfalls & Workarounds

### 1. `n8n import:workflow` Database Constraint Violation
- **Issue:** Bundle JSONs exported without explicit top-level `"id"` attributes fail CLI import.
- **Error:** `null value in column "id" of relation "workflow_entity" violates not-null constraint`.
- **Fix:** Pre-process JSON files to ensure top-level `"id"` string (e.g. `mai-v3-90-error-handler-001`) is present before running `n8n import:workflow`.

### 2. Task Broker Port 5679 Collision
- **Issue:** Running `docker exec n8n n8n execute --id=<wf_id>` fails when n8n daemon is active.
- **Error:** `n8n Task Broker's port 5679 is already in use. Do you have another instance of n8n running already?`
- **Fix:** Seed database trigger jobs or trigger executions directly via API/database seed rows instead of `n8n execute` when daemon container is running.

### 3. PostgreSQL Schema Least-Privilege & View Permissions
- **Issue:** Runtime role `mai_app` requires explicit `GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA mai TO mai_app;` and `GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA mai TO mai_app;` after DDL creation.
