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

## Dashboard Authentication, Password Recovery & Lockout Architecture

### Password Storage Precedence & Unset Password Trap
- Check auth status first: `curl -s http://127.0.0.1:20128/api/auth/status`
- When `hasPassword: false`, no bcrypt password row is stored in the database/settings. The Web login UI displays *"Default password is 123456 / Security risk: no password set"*, which is misleading when `INITIAL_PASSWORD` is defined in the environment.
- The login route (`/api/auth/login`) evaluates:
  1. If a custom password hash is present in settings, verify via bcrypt.
  2. If absent (`hasPassword: false`), evaluate against `process.env.INITIAL_PASSWORD || "123456"`.
- When an operator forgets their dashboard password, check the systemd unit file first:
  ```bash
  grep -n 'INITIAL_PASSWORD' /etc/systemd/system/9router.service
  # or inspect running process environment directly:
  tr '\0' '\n' < /proc/$(pgrep -f "next-server.*20128" | head -1)/environ | grep INITIAL_PASSWORD
  ```
  Do not delete the SQLite database or wipe `~/.9router/db/data.sqlite`; password configuration is held in the service environment unless explicitly overridden in the UI.

### Rate Limiting & Escalating Lockout
- In-memory rate limiting monitors failed login attempts per client IP (`remainingBeforeLock`).
- Lockout threshold: 5 consecutive failed attempts trigger an escalating lockout window.
- Lockout schedule: `[30s, 120s, 600s, 1800s]` (escalating from 30 seconds to 2 minutes, 10 minutes, and 30 minutes).
- Lockout state is in-memory; it clears automatically upon successful login or service restart.

### Password Reset Route & Local-Only Middleware Boundary
- Reset endpoint: `POST /api/auth/reset-password`
  ```bash
  curl -X POST http://127.0.0.1:20128/api/auth/reset-password -H 'Content-Type: application/json'
  ```
- Calling reset removes any stored bcrypt password, instantly reverting authentication back to `process.env.INITIAL_PASSWORD` (or `123456` if unset).
- **Loopback Enforcement**: The Next.js middleware guards `reset-password` (along with tunnel and OAuth management routes) strictly to loopback addresses (`localhost`, `127.0.0.1`, `::1`). Requests via Cloudflare Tunnel, public IP, or reverse proxy return 401/403. All reset operations MUST be executed directly on the host or via SSH port forwarding.

### Hardening & Plaintext Unit File Remediation
- When changing the password via the Web UI (**Dashboard > Profile**), 9router writes a bcrypt hash to persistent settings (`hasPassword: true`), which permanently bypasses `INITIAL_PASSWORD`.
- Systemd unit files under `/etc/systemd/system/` default to permissions `0644` (world-readable by all unprivileged users on the host). Once a custom password is set, remove `Environment=INITIAL_PASSWORD=...` from `/etc/systemd/system/9router.service` and reload:
  ```bash
  systemctl daemon-reload && systemctl restart 9router.service
  ```