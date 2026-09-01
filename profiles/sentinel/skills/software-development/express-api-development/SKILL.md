---
name: express-api-development
description: Use when building Express APIs with SQLite or Swagger.
---

# Express API Development & Upstream Synchronization

Patterns and pitfalls for building, extending, and operating Express.js APIs backed by SQLite storage with Swagger/OpenAPI documentation, Native MCP integration, and background synchronization.

## 1. Upstream Data Mirroring & SQLite Sync (`better-sqlite3`)

When syncing external JSON APIs or upstream data feeds into a local SQLite database:

1. **Enable WAL Mode**:
   ```javascript
   const Database = require('better-sqlite3');
   const db = new Database('app.db');
   db.pragma('journal_mode = WAL');
   ```
2. **Incremental Upsert (Zero Redundant Writes)**:
   Use SQLite `ON CONFLICT DO UPDATE WHERE` inside a single transaction to insert new records and update modified ones while skipping identical records:
   ```javascript
   const insertStmt = db.prepare(`
     INSERT INTO table_name (id, col1, col2, updated_at)
     VALUES (?, ?, ?, CURRENT_TIMESTAMP)
     ON CONFLICT(id) DO UPDATE SET
       col1 = excluded.col1,
       col2 = excluded.col2,
       updated_at = CURRENT_TIMESTAMP
     WHERE col1 IS NOT excluded.col1 OR col2 IS NOT excluded.col2;
   `);

   const syncTransaction = db.transaction((items) => {
     let inserted = 0, updated = 0, unchanged = 0;
     for (const item of items) {
       const existing = checkStmt.get(item.id);
       const result = insertStmt.run(item.id, item.col1, item.col2);
       if (result.changes > 0) {
         if (existing) updated++; else inserted++;
       } else {
         unchanged++;
       }
     }
     return { inserted, unchanged, updated };
   });
   ```

---

## 2. Parameter Sanitization & Query Trimming

- **Trailing Whitespace Pitfall**: Users or frontends often pass query strings with trailing spaces (e.g. `?operator=Telkomsel%20`). Exact SQL matches (`operator_name = ?`) or standard `LIKE ?` patterns will fail unless sanitized.
- **Rule**: Always trim string parameters at the handler level:
  ```javascript
  app.get('/api/resource', (req, res) => {
    const operator = (req.query.operator || '').trim();
    const q = (req.query.q || '').trim();
    // proceed with database query using trimmed values
  });
  ```

---

## 3. Swagger / OpenAPI (`swagger-ui-express`) Caching & Visual Proof Fixes

- **Cloudflare / CDN / Mobile Cache Pitfall**: `swagger-ui-express` dynamically generates `swagger-ui-init.js` and serves a default HTML wrapper loading `./swagger-ui-init.js`. Reverse proxies (Cloudflare) and mobile browsers aggressively cache this static JS script regardless of `Cache-Control` headers, causing users to see stale OpenAPI specs even in incognito/mobile sessions.
- **Fix**: Override the default HTML template for `/docs` to append a dynamic timestamp query parameter (`?t=Date.now()`) when injecting `swagger-ui-init.js`:
  ```javascript
  const swaggerHtml = `
  <!DOCTYPE html>
  <html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="./swagger-ui.css" >
  </head>
  <body>
  <div id="swagger-ui"></div>
  <script src="./swagger-ui-bundle.js"></script>
  <script src="./swagger-ui-standalone-preset.js"></script>
  <script>
    const script = document.createElement('script');
    script.src = './swagger-ui-init.js?t=' + Date.now();
    document.body.appendChild(script);
  </script>
  </body>
  </html>
  `;

  app.use('/docs', (req, res, next) => {
    res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
    next();
  });
  app.use('/docs', swaggerUi.serve);
  app.get(['/docs', '/docs/'], (req, res) => res.send(swaggerHtml));
  app.get('/docs/swagger-ui-init.js', swaggerUi.setup(swaggerDocument));
  ```
- **Visual Verification & User Frustration Response**:
  - When the user expresses doubt ("Bukan karena cache bre", "Masih sama aja breee astaga", "Nahhhh gitu kek dari tadi"), do NOT keep insisting or repeating explanations.
  - Immediately perform browser inspection using `browser_navigate` and `browser_vision`, verify what is actually being rendered, capture a screenshot, and send the MEDIA path directly to the user so they can inspect it themselves.

---

## 4. Internal / Hidden Endpoints Pattern

- **Requirement**: Operational or admin routes (e.g. `/api/sync/status`, `/api/sync/trigger`) need to stay accessible for backend monitoring or manual cron triggers, but should not clutter public API documentation.
- **Implementation**: Define Express handlers for all endpoints, but omit internal routes from the `swaggerDocument.paths` object.

---

## 5. HTTP Transport MCP Server Integration

- **Pattern**: Adding HTTP-based MCP servers (such as n8n MCP endpoints) to Hermes config (`~/.hermes/config.yaml`).
- **Structure**:
  ```yaml
  mcp_servers:
    n8n-mcp:
      url: "https://n8n.domain.com/mcp-server/http"
      headers:
        Authorization: "Bearer <token>"
  ```
- **Behavior**: Requires HTTP StreamableHTTP transport support in MCP SDK. Automatically negotiates SSE/JSON-RPC over HTTP.

---

## 6. Telethon SQLite Database Lock Troubleshooting

- **Symptom**: Querying or connecting to a Telethon session file returns `sqlite3.OperationalError: database is locked`.
- **Cause**: Telethon keeps an open read-write connection to the `.session` file while the script/bot process is actively running.
- **Fix / Inspection**:
  - To inspect metadata safely without interrupting the active process, connect in read-only URI mode:
    ```python
    import sqlite3
    conn = sqlite3.connect('file:/path/to/session.session?mode=ro', uri=True)
    ```
  - If a full client reconnect is required, find and kill the locking process first (`fuser -k /path/to/session.session` or `kill -9 <PID>`), perform the authorization/session check, then restart the daemon/bot script in the background.

---

## 7. n8n Workflow Automation via `n8n-mcp`

- **Workflow Creation**: When building automated workflows in n8n via MCP (`mcp__n8n_mcp__create_workflow_from_code`):
  1. Retrieve best practices using `mcp__n8n_mcp__get_workflow_best_practices`.
  2. Consult `mcp__n8n_mcp__get_sdk_reference` to build valid `@n8n/workflow-sdk` TypeScript/JS code.
  3. Validate using `mcp__n8n_mcp__validate_workflow` before creating.
  4. Publish using `mcp__n8n_mcp__publish_workflow` and test run via `mcp__n8n_mcp__execute_workflow`.
- **n8n Expression & Telegram URL Syntax**:
  - In `n8n-nodes-base.httpRequest`, when specifying `url: 'https://api.telegram.org/bot<token>/sendMessage'`, ensure the token format is valid (`<bot_id>:<hash>`).
  - For static or literal JSON payloads in `jsonBody`, pass plain JSON strings instead of `expr(...)` wrappers to avoid n8n expression evaluation syntax errors (`invalid syntax`). Use `expr(...)` only when dynamic `{{ $json... }}` expressions are present.
  - Active Telegram Bot Token for Waffer Bot: `7578843460:AAGGP-541DltkbCgwUYMB_6rvRKqVHFEoqk` (User Chat ID: `696907598`).
- **Workflow Version Hygiene & Cleanup**:
  - When re-creating or refactoring n8n workflows from code, draft or duplicate workflow instances will accumulate in the workspace.
  - Use `mcp__n8n_mcp__archive_workflow` with the old `workflowId` to clean up superseded drafts, keeping only active/published production workflows visible in the n8n UI.
- **Multi-Agent Async Architecture in n8n & 9router Gateway**:
  - For 20+ parallel agent workloads in single-instance n8n, use parent dispatcher emitting job items to sub-workflows with `Wait for Completion: OFF`.
  - Map agent model routes (`model_route` in Postgres) to 9router local gateway endpoints (`http://127.0.0.1:20128`) such as `ag-opus-pool` for unified multi-agent LLM routing.
  - Always write state/results to PostgreSQL (`mai` schema) before evaluating notification gates to ensure both notified and silent runs remain auditable.
  - **Docker Container to Host 9Router Network Authentication**: When n8n runs inside a Docker container, queries to host 9router (`http://172.20.0.1:20128`) will present as remote connections. If 9router requires API keys for remote access (`401 API key required for remote API access`), use a valid bearer token or update `requireApiKey: false` in `settings` table inside `~/.9router/db/data.sqlite` and trigger daemon reload (`fuser -k 20128/tcp`). Avoid killing daemon unnecessarily; 9router auto-restarts via daemon supervisor.


