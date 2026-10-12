# Fetch-hook & media-pipeline recon (SPA streaming/aggregator apps)

Depth notes for SPA targets whose product IS the pipeline: movie/TV/anime aggregators and
embed players. The client bundle, not the DOM, is the architecture diagram. Everything here
is read-only recon plus verified live-call checks; upstream crypto is never re-implemented.

## 1. Split host roles before believing any endpoint

- Static host (apex/`www`, behind Cloudflare or similar): the SPA + PWA. It answers the
  index shell for arbitrary paths — `robots.txt`, `sitemap.xml`, and `/api/*` all return the
  shell. Byte-diff against the root: identical size = catch-all, not an API.
- API host: named in the config chunk. Only IT has REST endpoints.
- The config chunk (linked from the shell via `<link rel="modulepreload">`) exports backend
  selection: query overrides (`?backend=local|prod`), localhost-port fallbacks, then the
  prod host. Read the export and the host constants; never assume the apex is the API.

Live-vs-shell check for an endpoint the app supposedly calls:

    curl -s -o /dev/null -w '%{http_code} %{size_download}\n' https://STATIC/api/foo   # shell size => soft-404
    curl -s https://APIHOST/api/foo | head -c 200                                     # JSON error => route is real

A static-host response carrying `cf-cache-status: HIT` and the shell's byte size is the
catch-all. A JSON error from the API host (`{"success":false,"error":"Missing required 'id' parameter"}`)
proves the route exists — parameter-validation errors enumerate the server's own state.

## 2. Enumerate the lazy chunks first

The entry bundle lists every route chunk by filename. Fetch the interesting ones (Player,
Search, Docs, api-hooks, provider modules) into a per-target `chunks/` dir and grep them
individually — endpoint tables and provider logic live there, not in the entry.

## 3. Detect and read the fetch monkey-patch

Pattern: `window.fetch=async function(...)` / `e.fetch=async function(...)` in the entry
bundle, replying with `new Response(JSON.stringify({...}))` for routes the static host does
not serve. Meaning: some "endpoints" exist ONLY in the browser. Cheap greps:

    grep -oE '.{60}fetch\(.{120}' entry.js          # call sites + which host each uses
    grep -oE 'localStorage' entry.js                 # caching layers next to the hooks

Read the interceptors as the primary spec of provider behavior: they embed provider IDs,
param normalization (`type`|`media_type`, `id`|`tmdb_id`, default ids), and each provider
branch's fallback order. The server provider list (`/api/providers`) and the client branches
can disagree — record both, and note that a server copy is authoritative when it returns
real data.

## 4. Multi-layer proxy pattern (the masking layer)

Aggregators chain 2–3 proxies so upstreams only ever see wrapper headers:

- Origin API proxy: `/api/proxy?url=<enc>&origin=<site>&referer=<site>`, often with a
  `/api/subtitles/proxy` sibling.
- Cloudflare Worker relays (`*.workers.dev`): rewrite every segment URI in the returned m3u8
  to route back through the worker (anti-hotlink + CORS + spoofed Referer/Origin). If every
  `#EXTINF`/segment line points at the proxy host, that IS the rewrite proof — playback then
  needs no third-party cookies.
- Per-provider header spoofing: requests to third-party extractor APIs carry the
  `Referer`/`Origin` of the upstream player domain, not the target's own.

Detection greps: `workers.dev|/api/proxy|Referer:|origin:` across entry + chunks.

## 5. WASM-obfuscated parameters (encrypted IDs)

Pattern: a shim script (`/xxx_exec.js` = Go `wasm_exec.js`) plus a multi-MB `.wasm` whose
header shows the `go:buildid` string; the bundle then calls a global like
`window.getAdv(tmdbId)` to mint an opaque id for an upstream API (`/api/b/movie/<id>`).

- Reproduce at runtime with the browser/CDP `evaluate` (load shim, instantiate wasm, call
  the global) — do NOT re-implement the crypto from minified JS.
- Report the mechanism (client-side obfuscation of an API call, not server-side auth), with
  the wasm's size/magic, not a claim of "encryption".
- The same wasm can be driven headlessly from Node when scripting the chain: eval the
  glue text so it attaches to `globalThis`, `WebAssembly.instantiate(buf, inst.importObject)`,
  `inst.run(mod)`. Trap: a Go wasm global returns `null` for every input until its
  dependency globals exist — one needed `globalThis.sodium` (from `libsodium-wrappers-sumo`,
  `await sodium.ready`) before `getAdv(id)` produced anything. `null` from a wasm global
  means missing dependency, not bad input.
- Tiny decryptor wasms (a few KB, exports `memory`/`alloc`/`decrypt`, no imports) share one
  shape: `alloc(len)` → copy ciphertext to `ptr` → `decrypt(ptr,len)` returns the output
  length → plaintext starts at `ptr + 12`. Run straight from Node:

```js
const { instance } = await WebAssembly.instantiate(buf, {});
const ex = instance.exports, bin = Buffer.from(encB64, 'base64');
const ptr = ex.alloc(bin.length);
new Uint8Array(ex.memory.buffer, ptr, bin.length).set(bin);
const n = ex.decrypt(ptr, bin.length);
console.log(new TextDecoder().decode(new Uint8Array(ex.memory.buffer, ptr + 12, n)));
```

## 6. Extractor chains and their verification recipe

Typical sub-flow (one provider family):

    upstream?title=…&type=…&tmdb=<id>&server=<A> → wrapper encode API (/enc-…)
      → JSON {data, state} → client decrypts (WebCrypto AES-GCM, key/state in payload)
    upstream /seed?mediaId=<id> → {seed, ttlMs} short-lived token → per-city
      (/miami|/atlanta|/dallas) /sources?... with spoofed Origin/Referer → playlists

Verify with ONE live call per step, then end-to-end: sources JSON → playlist fetch (200,
`#EXTM3U`) → parse a segment URI → fetch it → `file` it (`.ts`/mpegts proves a real chain).
Treat upstream 502s like `transcoding on node X` as deploy-time transients — retry or pick
another source before drawing conclusions.

Availability endpoints (`/api/stream/check?provider=…`) expose the server's own try-order and
per-provider failure reasons — cheaper than trial calls and good evidence.

### Signed handoff chains (embed → player → API → per-host token)

Later-generation players resolve in hops, each hop embedding the next URL:

    embed page (`data-api="/vs_src.php?…"`) → GET it → {"src": "<signed embed url>"}
      → next embed page contains `playerUrl` → player page carries `window.CONFIG = {apiToken, api|streamBase, …}`
      → stream API with the token exactly as the client sends it → encrypted `stream_urls`
        + `{"vs":{"w":<id>,"wasm_url":"…/wasm.php?w=…"}}` → tiny-wasm decrypt (above) → master playlists
      → per-stream-host token: GET `https://<stream-origin>/generate.php` (fresh, one-time)
      → `?token=` on the master only; sub-playlist and segments often need nothing.

Rules that cost time when missed:

- Extract each hop from the fetched HTML by regex (`"playerUrl":"([^"]+)"`, `data-api="…"`,
  `window.CONFIG = {…}`) and carry the previous hop's Referer — hops accept only their
  predecessor's referer set.
- Copy the client's token placement EXACTLY — grep the player JS for `api_token=`,
  `withApiToken`, `Bearer`. One chain accepts `&api_token=<jwt>` as a QUERY param and answers
  `403 invalid api token` for the identical token in an Authorization header; wrong placement
  looks exactly like a rejected credential.
- Decode token payloads: claims like `ip_cidr` plus a short `exp` declare the binding — the
  whole chain must run from one sticky IP within the TTL. A previously valid URL answering
  `404`/`Session expired` from a different IP is session invalidation, not a dead host
  (sticky-IP rules: `web-surface-triage` → `references/datacenter-blocked-targets.md` §5).
- Tokens are minted per fresh GET of the mint endpoint and consumed per use: fetch a fresh one
  immediately before each new path level; reusing an old token on a new path yields `403`.
- Test auth per path level (master / sub-playlist / segment) instead of assuming the whole
  tree is gated identically.
- If the front-end's own bootstrap is an opaque challenge loader (constant `// mt`, an
  `accept-ch` client-hints handshake), don't fight it — find the embed component the
  front-end delegates to (its page/API is usually the less-protected route to the same
  stream) and chain from there.
- A working end-to-end extractor for this chain shape is packaged at
  `scripts/mover_chain_extract.py` (film + TV, proxy via env var).

## 7. What the deliverable looks like

- Separate the LEGAL catalog layer (TMDB metadata, posters, search) from the extraction layer
  (third-party stream APIs, spoofed headers, proxy rewriting). The architecture teardown plus
  one verified live call IS the answer to "how does it work".
- For "can we build our own": propose the same architecture with owned/licensed sources
  (own HLS/CDN, official APIs) and note the copyright constraint of the extraction layer
  briefly — no lecture.
- Security findings that fall out naturally: unauthenticated `/api/stream` returning direct
  4K playlist URLs, `/api/providers` inventory disclosure, stack/version banner on the API
  root, upstream hostnames leaked in error bodies.
