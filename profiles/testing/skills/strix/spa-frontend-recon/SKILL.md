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

Use when a target is a JavaScript SPA (Vue/React/Next/Nuxt/Svelte), or when a host returns the same catch-all shell for every path, or when the user asks how a given web product works and whether its architecture can be rebuilt — the bundle is the specification. Modern JS sites hide their real attack surface behind a single HTML shell. The shell is nearly empty; the application lives in the JS bundle and, when misconfigured, its source map. Recover that, harvest the backend hosts and endpoints it calls, then pivot. Assess only assets you are authorized to test.

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
- The entry bundle lists its **lazy chunks**: `grep -oE 'assets/[A-Za-z0-9_-]+\.js' entry.js | sort -u`, then fetch each into a per-target `chunks/` dir. Route logic (player, search, providers, docs pages) ships as separate files — the entry alone is not the app.

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

- A map request answering `200` with the shell's exact byte size is the catch-all shell, not a map — treat it as absent.
- No map is a speed loss, not a dead end: minified constant names survive, so the Step 4 greps still work on the raw bundle — do not stall on source-map tooling.

## Step 4 — Harvest from the recovered source

**Start with the environment/config object — it is the single highest-yield
grep.** Frameworks inline their build config into the bundle and it routinely
carries production secrets and third-party pointers:

```bash
grep -oE '\{production:!?[01][^}]{0,800}\}' main*.js      # Angular-style env object
grep -oE '(apiUrl|apiKey|googleApiKey|apiMicrosoft|clientId|baseUrl)\s*:\s*"[^"]+"' main*.js
grep -oE 'https?://[a-zA-Z0-9.-]+(\.ngrok\.io|\.trycloudflare\.com|\.loca\.lt|\.serveo\.net)' main*.js
grep -oE 'var [a-z]=`https?://[^`]+`' main*.js                     # minified base-host constants (survive minification)
grep -oE '`/[a-zA-Z0-9_/{}$.:?=&-]+`' main*.js | sort -u         # route paths live in backtick template literals
```

Then read the config for these in order of severity:

- **Tunnels in production config** (`*.ngrok.io`, `trycloudflare.com`, `serveo`, `loca.lt`) — a
  production build pointing an auth or API flow at a dev tunnel. The tunnel itself may already be
  dead (`404` from the tunnel edge) while the pointer stays in shipped code: the risk is the
  reconnect/claim window, and the URL embeds the dev machine's identity. Report the pointer plus
  the claim/expiry mechanics; do not report a dead tunnel as a live compromise.
- **API keys**: validate the key's own restrictions before scoring (a Google key answering
  `REQUEST_DENIED: API keys with referer restrictions cannot be used with this API` is
  Medium-low/hygiene; a key that answers `OK` is a live credential). Never print the full key in
your output — capture it once, store it redacted, and cite prefix+suffix only.
- **Every backend host** the config names (`api-gateway.`, `auth-v2.`, user-management, MS/OAuth
  endpoints) — these are sibling hosts with their own surface; feed the hostnames into the
  subdomain/inventory pass, because they often are NOT in the public cert/CT inventory.
- **Obfuscated endpoint tables**: paths that look like hashes
  (`/api/account/<64-hex>/forgot_password`) are just obfuscation, not secrecy. The readable
  operation names in the same object (`forgot_password`, `check_token_*`, `change_password`,
  `resend_otp_code`, `validation_nik_student`) tell you what each route does — enumerate the
  operations, and probe routes read-only (OPTIONS/GET) instead of triggering account flows.

Grep the app files (exclude `node_modules`) for:

- API base URLs and every endpoint path (commonly `store/api/*` or a `config` module)
- Sibling/aux hosts: `api.`, `cdn.`, `analytics.`, back-office/admin
- Config files: `firebase.js`, `.env*` references, axios/fetch base URLs
- Auth logic: how sessions/tokens are built, hardcoded keys, commented test credentials
- XSS sinks: `v-html`/`innerHTML`/`dangerouslySetInnerHTML`/`:href` bound to API data
- Internal hostnames (`127.0.0.1:PORT`, staging names) and environment leftovers
- **Media/streaming pipeline apps** (providers, extractors, `/api/stream`, `window.fetch` patches, WASM modules): follow `references/fetch-hook-and-media-pipeline-recon.md` — fetch-hook detection, static-host vs API-host splitting, the multi-layer proxy pattern, and the one-live-call verification recipe.

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
- **A shell `200` from the static host does not mean an endpoint is missing.** On SPAs the static host answers `/api/*` with the index HTML, the client monkey-patches `window.fetch` at runtime, and the real API lives on a separate host named in the config chunk. Test endpoints against that host; validate runtime-only routes in a real browser (CDP `evaluate`), not with curl.
- **Do not describe a backend's behavior from bundle strings alone.** One live call (e.g. an unauthenticated `/api/stream` returning real playlist URLs) converts an inferred architecture into an observed one — label the rest as inferred.
- **`500` on a parameter is not injection.** A single quote (or any malformed value) forcing 500 is usually generic input handling. Confirm with a syntactically-harmless-but-invalid control and require reproducible body or timing deltas before claiming SQLi/injection.
- **Client-side auth is not authorization.** Double-encoded cookies with a hardcoded key, hidden routes, and code comments grant no access; the real control is server-side. Report the weak scheme as a hygiene finding, never as a proven auth bypass.
- **A Firebase web `apiKey` is public by design** — leaking it is expected. The finding is exposed *data* (rules), not the key.
- **Verify a leaked `apiKey`/secret's format and length** before reporting it; if it cannot be a real key, note it as hygiene only.
- **A tunnel URL or key in the bundle is not automatically live.** Test it, then report what you observed: a `404` from the tunnel edge means the pointer is stale but still shipped (a reconnect-window finding), not that auth is currently intercepted. State the mechanics and the residual risk, not a false "live" claim.
- **A key surrounded by referer/origin restrictions is not exploitable from your position** — record it as hygiene plus a rotation recommendation. Resist upgrading it because the session needs a critical; an honest Medium-low is worth more than an inflated High.
- **Bundles vendor third-party libraries**, so an archived library version inside a bundle is not a reachable CVE — rate it only with a demonstrated chain.
- **An odd-looking constant in grep output (`265****5769`) is viewer-side masking, not file corruption.** Dump the raw bytes (`node -e` with `charCodeAt` hex) and read the true literal before building around a phantom.

## Tooling

- `curl -s -D -` for headers; `-k` only when the certificate is genuinely self-signed (and say so)
- Python `json` to explode source maps and parse JSON API responses
- Keep all evidence under a per-target directory and dedupe before writing the report
- A real browser session (CDP `evaluate`) for runtime-only routes and WASM-obfuscated IDs — reproduce what the bundle does at runtime instead of re-implementing minified crypto by hand. Node can host the same wasm when the glue allows (instantiate `*_exec.js` + `.wasm`, call the exported global), but supply the module's dependency globals first — a libsodium-based one silently returned `null` until `globalThis.sodium` was set from `libsodium-wrappers-sumo` after `await sodium.ready`.
- `scripts/mover_chain_extract.py` — packaged end-to-end extractor for the signed handoff chain shape (embed → player → stream API → tiny-wasm decrypt → per-host token → media), film + TV, proxy via `VENUS_PROXY`.
