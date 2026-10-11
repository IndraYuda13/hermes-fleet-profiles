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

- **Trailing Whitespace Pitfall**: Users or frontends often pass query strings with trailing spaces (e.g. `?operator=name%20`). Exact SQL matches (`operator_name = ?`) or standard `LIKE ?` patterns will fail unless sanitized.
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
- **Visual Verification Over Verbal Reassurance**:
  - When visual caching issues or client-side rendering discrepancies are suspected, do not rely on verbal explanations.
  - Immediately perform browser inspection using browser navigation and vision tools, verify the rendered DOM, capture a screenshot, and present the artifact directly.

---

## 4. Internal / Hidden Endpoints Pattern

- **Requirement**: Operational or admin routes (e.g. `/api/sync/status`, `/api/sync/trigger`) need to stay accessible for backend monitoring or manual cron triggers, but should not clutter public API documentation.
- **Implementation**: Define Express handlers for all endpoints, but omit internal routes from the `swaggerDocument.paths` object.

---

## 5. External Automation: MCP & n8n Integration

- HTTP MCP servers are registered in Hermes config (`~/.hermes/config.yaml`) under `mcp_servers` with a `url` and `Authorization` header; StreamableHTTP transport auto-negotiates SSE/JSON-RPC.
- n8n workflow creation via `n8n-mcp` follows a fixed tool order: best practices → SDK reference → validate → create → publish → execute. In `jsonBody`, wrap values in `expr(...)` only when dynamic `{{ $json... }}` expressions are present — static payloads wrapped in `expr(...)` throw `invalid syntax`.
- Archive superseded n8n workflow drafts (`archive_workflow`) so the workspace keeps only published workflows, and write run state to Postgres before notification gates so silent runs stay auditable.
- Full patterns (config YAML, multi-agent fan-out, Docker-to-host gateway auth): `references/mcp-n8n-integration.md`.


