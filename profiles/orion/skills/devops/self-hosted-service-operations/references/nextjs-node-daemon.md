# Next.js Node App (9router) Operations

## PR Testing & Swapping
To test an in-flight Pull Request without overriding the official CLI tool:
1. Isolate: Clone the repo and checkout the PR branch in a temporary directory (e.g. `/mnt/9router-flash`).
2. Build: `npm install && npm run build`
3. Identify Daemon: Next.js/Node apps often run via background auto-restarters (PM2, systemd, or bash background scripts).
4. Kill Aggressively: A simple `kill` or `pkill` may be outpaced by an auto-restarter. Kill the port owner immediately before starting the test instance:
   ```bash
   fuser -k 20128/tcp && cd /path/to/repo && PORT=20128 node --dns-result-order=ipv4first .next/standalone/server.js &
   ```
5. Port Note: The Next.js standalone `server.js` ignores CLI flags like `-p 20128`. You must pass the port via the `PORT` environment variable.

## Resolving a 9router combo alias to its real upstream model

When asked "model apa yang lagi dipakai", the Hermes-facing name (e.g. `ag-opus-pool`) is usually a 9router **combo**, not a real model. Resolve it against the live DB:

```bash
curl -s http://localhost:20128/v1/models | head -c 3000     # lists combos + real provider models
sqlite3 /root/.9router/db/data.sqlite "select * from combos where name='ag-opus-pool';"
# -> id|name||["cc/claude-opus-5"]|created|updated   (4th col = JSON array of member models)
sqlite3 /root/.9router/db/data.sqlite "select id,name from providerConnections;"
```

Notes:
- Live DB is `/root/.9router/db/data.sqlite`. Sibling `9router.db` / `database.sqlite` are empty leftovers; `app/cli/.build-home/...` is build scaffolding.
- Tables: `combos`, `providerConnections`, `providerNodes`, `apiKeys`, `proxyPools`, `usageDaily`, `usageHistory`, `requestDetails`, `settings`, `kv`.
- `/api/combos` returns `{"error":"Unauthorized"}` without a key. `/v1/models` is open, so prefer it plus a direct sqlite read.
- `providerConnections` has no `type` column; select `id,name` only.
- Combo members use `provider/model` form (`cc/claude-opus-5` = Claude Code provider).

## Next.js Standalone Mode
Apps built with Next.js `output: 'standalone'` run out of `.next/standalone/server.js`.
- Do NOT use the wrapper CLI scripts (`cli.js`, `9router`) for testing the bare server unless you specifically need CLI wrappers (tray icons, auto-updaters).
- Start it directly: `PORT=<port> node .next/standalone/server.js`