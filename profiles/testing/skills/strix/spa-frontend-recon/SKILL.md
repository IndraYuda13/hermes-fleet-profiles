---
name: spa-frontend-recon
description: Recover a JS SPA's real attack surface from bundles.
version: 1.0.0
author: hermes-curator
license: MIT
metadata:
  hermes:
    tags: [recon, spa, javascript, source-map, api-discovery]
    related_skills: [information-disclosure, firebase, authentication-jwt, oauth]
---

# SPA Frontend Recon

## When to Use

Use when a target is a JavaScript SPA (Vue/React/Next/Nuxt/Svelte), or when a host returns the same catch-all shell for every path. Modern JS sites hide their real attack surface behind a single HTML shell. The shell is nearly empty; the application lives in the JS bundle and, when misconfigured, its source map. Recover that, harvest the backend hosts and endpoints it calls, then pivot. Assess only assets you are authorized to test.

## Signals

- Same body/ETag/length for `/`, `/.env`, `/admin`, `/wp-login.php`, and random paths — all HTTP 200
- `<div id="app"></div>` (or similar) empty mount point; scripts under a hashed build dir like `/2.1.0/index.<hash>.js`
- `robots.txt` disallowing spam keywords (`gacor`/`slot`/`bet`) — trace of past SEO-injection abuse

## Step 1 — Confirm it is a catch-all SPA

- `curl -s -D - -o /dev/null https://TARGET/` vs `https://TARGET/anything`
- If status/length/ETag match across unrelated paths, every `200` is meaningless (soft-404). Do not brute-force directories. The only real files are the static assets referenced by the shell.

## Step 2 — Enumerate build assets

- Fetch the shell and extract referenced scripts/styles:
  `curl -s https://TARGET/ | grep -oE '(src|href)="[^"]+\.(js|css)"'`
- Note the build version directory (e.g. `/2.1.0/`); sibling paths may 403/404 while the versioned assets serve.

## Step 3 — Pull the source map

- Try `<bundle>.js.map` next to each bundle; Vite/webpack maps are often shipped to production.
- If present, explode it to disk (never keep the multi-MB map in memory) and drop `node_modules` so the app's own `src/` surfaces first:

```python
import json, os
os.makedirs('src', exist_ok=True)
d = json.load(open('index.js.map'))
for s, c in zip(d['sources'], d.get('sourcesContent') or []):
    if not c: continue
    name = s.replace('../../', '').replace('/', '__') or 'empty'
    open('src/' + name, 'w', errors='ignore').write(c)
```

## Step 4 — Harvest from the recovered source

Grep the app files (exclude `node_modules`) for:

- API base URLs and every endpoint path (commonly `store/api/*` or a `config` module)
- Sibling/aux hosts: `api.`, `cdn.`, `analytics.`, back-office/admin
- Config files: `firebase.js`, `.env*` references, axios/fetch base URLs
- Auth logic: how sessions/tokens are built, hardcoded keys, commented test credentials
- XSS sinks: `v-html`/`innerHTML`/`dangerouslySetInnerHTML`/`:href` bound to API data
- Internal hostnames (`127.0.0.1:PORT`, staging names) and environment leftovers

## Step 5 — Pivot to discovered hosts and fingerprint each

- Resolve and probe each host; identify stack (`Server`, `X-Powered-By`, framework cookies, health endpoints)
- For each API host, enumerate the endpoints found in Step 4 (`/api/<resource>`) and test id/page/param handling
- Check per-host CORS and headers: watch for `Access-Control-Allow-Origin: *`, `Allow-Credentials: true` combined with `*`, contradictory or repeated CSP headers, and internal hostnames inside `frame-ancestors`
- See `references/pivot-topology.md` for the typical service layout and API-host triage cues

## Step 6 — Test the modern cross-service layering

- If the client writes to Firebase/Firestore/Storage directly, test its security rules — see the firebase skill; the UI's gating is irrelevant
- If auth is a JWT/session, test the token end — see authentication-jwt and oauth
- Self-hosted third-party services (analytics, metrics UIs) add their own exposure surface; fingerprint them by their static asset names and health endpoints

## Pitfalls

- **A 200 is not existence.** Catch-all routing answers 200 for every path; only body/ETag differences or a genuine 404 marker prove a path is real.
- **`500` on a parameter is not injection.** A single quote (or any malformed value) forcing 500 is usually generic input handling. Confirm with a syntactically-harmless-but-invalid control and require reproducible body or timing deltas before claiming SQLi/injection.
- **Client-side auth is not authorization.** Double-encoded cookies with a hardcoded key, hidden routes, and code comments grant no access; the real control is server-side. Report the weak scheme as a hygiene finding, never as a proven auth bypass.
- **A Firebase web `apiKey` is public by design** — leaking it is expected. The finding is exposed *data* (rules), not the key.
- **Verify a leaked `apiKey`/secret's format and length** before reporting it; if it cannot be a real key, note it as hygiene only.
- **Bundles vendor third-party libraries**, so an archived library version inside a bundle is not a reachable CVE — rate it only with a demonstrated chain.

## Tooling

- `curl -s -D -` for headers; `-k` only when the certificate is genuinely self-signed (and say so)
- Python `json` to explode source maps and parse JSON API responses
- Keep all evidence under a per-target directory and dedupe before writing the report
