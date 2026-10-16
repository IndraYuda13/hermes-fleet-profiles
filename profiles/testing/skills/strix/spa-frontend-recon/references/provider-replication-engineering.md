# Replication engineering: rebuilding an extraction pipeline as your own backend

Depth notes for the phase AFTER recon: the user says "can we build our own version".
Scope: prove replication by running the recovered chain end-to-end as YOUR code
(own resolver modules, own proxy), then hand the working code over as a backend.
The deliverable is a running prototype plus a provider-by-provider verification
table, not a document.

## 1. Port ciphers byte-exact — verify against the original before building on it

When the chain uses a custom cipher (XOR/LGC keystream, AES-GCM envelope), a
plausible-looking port that is subtly wrong fails deep in the chain, and you will
blame the network. Port to a standalone module and prove byte-equality FIRST:

- Feed the SAME seed/id to both implementations and compare the first keystream
  word (or first block) as a hex value — one line of Node vs one line of Python.
- Only after the first word matches, decrypt a real payload and parse it.
- Keep the cipher in its own file with the verified test values in a docstring so
  a future session can re-verify after any edit.

Watch for 32-bit arithmetic semantics when porting JS→Python: `(a*b) & 0xFFFFFFFF`
multiplications, rotate-left (`>>>`), and `Math.imul`-style multiplies all need an
explicit `& M32` mask; Python ints silently produce wrong 64-bit results.

Same-cipher families: aggregators reuse ONE cipher across multiple providers
(observed: two different providers' sources decrypt with the identical function,
only the city/endpoint differs). When provider #2's payload decrypts with
provider #1's port, say so — it collapses two resolvers into one module.

## 2. Provider-class architecture for the rebuild

- One file + one class per provider, a dataclass `Source`/`StreamResult`, and a
  registry with ordered fallback: `resolve_chain(id, type, prefer=…)` tries each
  provider's `resolve()`, catches EVERY exception per-provider, and passes the
  errors dict along in the failure result. A provider being down must never 500
  the API.
- Cache the short-TTL seeds (25–30 s windows) per media id; providers rate-limit
  aggressively (429 on burst) — a cache is correctness, not optimisation.
- HTTP helpers take an optional `proxy` param per call; only the providers whose
  tokens are residential-IP-bound use the residential pool.
- Treat provider order/prefer as API params (`?provider=`), used for tests and
  the UI's server switcher.
- **`success` + sources is not proof the stream plays.** Aggregators hand the
  same playlist URL to several providers, and an upstream still transcoding
  returns a dead URL that looks resolved (observed: `502 "transcoding on node
  joy-03"` from a playlist the resolver had confidently returned). Wire a
  `source_probe(provider_id, source)` callback into `resolve_chain`: fetch the
  first source, accept only `2xx` with an `#EXTM3U` body, treat anything else as
  dead and continue the fallback, and keep the first resolvable-but-dead result
  as a best-effort return so a wholly-transcoding library still yields a link.
  Cache verdicts per URL at module level (~90 s) — several providers share the
  identical URL, so per-request caches probe it over and over and the repeat
  probes are most of the user-visible latency. TDD the probe: fake providers
  returning alive/dead/unknown, assert the chain skips dead and keeps
  unknown-verdict results.
- When the provider set must stay black-box, wrap the observed upstream as a
  temporary bootstrap provider and mark it in-code as such (`# NOTE: temporary
  upstream bootstrap`) — do not let it become silent architecture.

## 3. WASM decryptors: run from Node, plan the portable replacement

The tiny-decryptor shape (`alloc`/`decrypt`/`memory`, output at `ptr+12`) is
runnable in minutes from Node. For a long-lived backend service:

- Check for a Python wasm runtime (`wasmtime` / `wasmer` import) — if present,
  call the same wasm directly with no subprocess. Install into the SERVICE's venv
  (the one in the systemd unit), not the shell's.
- Keep a fixture (real `stream_urls` ciphertext + a copy of the wasm binary) in
  the test tree so the decryptor has a regression test that does not need the
  network or the proxy.
- The VidLink-style Go wasm (`wasm_exec` glue) is heavier: prefer a public
  decode endpoint or a bootstrap provider over vendoring Go+libsodium into the
  backend; the Node recipe stays as the manual/verification path.

## 4. Verification ladder — what "proven" means per provider

Run these in order; each level subsumes the previous. The final artifact is a
table `provider | test | result | evidence` in the report.

1. Resolver returns >=1 source (your code, live network).
2. Playlist fetch through YOUR proxy: HTTP 200 and `#EXTM3U`.
3. Sub-playlist parsed, segment count sane, every segment URI rewritten to your
   proxy when the chain needs it.
4. Fetch ONE init/segment and `ffprobe -show_streams` it: `codec_name=h264` +
   `aac`, width/height, duration.
5. For fMP4 (`.m4s`) chains, fetch init + first segment and `cat` them before
   ffprobe — an isolated `.m4s` has no moov and reports `trun track id unknown`.
6. Generalize: run the full chain for >=2 titles of different types (movie + TV,
   different TV season/episode path shapes) before declaring the resolver done.

## 5. Pitfalls that cost time

- **Content-Type lies on media CDNs.** A segment answering `Content-Type:
  image/png` with 388 KB of body is binary video for ffprobe, not a corrupt
  fetch. Never reject a segment on Content-Type; hex-dump or ffprobe it.
- **A 401/403 body saying `no token`/`invalid token` spanning exactly one hop
  means the token parameter is missing or placed wrong for that level** — need
  not mean the whole chain is dead. Test each path level with and without the
  token; observe which level gates (observed: master needs `?token=`, sub and
  segment need none).
- **A previously-working signed URL answering `404 Not Found` from your direct
  IP while a residential node still returns 200 is IP-binding, not expiry — the
  whole chain must stay on one sticky node** (see `web-surface-triage` →
  `references/datacenter-blocked-targets.md` §5). Mint fresh tokens per request;
  any cached token is bound to the IP that minted it.
- **Browser tooling refusal to proxy local addresses is a harness policy, not a
  target failure**: get fresh URLs from the shell via the residential node, then
  pass them to the browser; or launch your own headless Chrome with
  `--proxy-server` and drive it over CDP.
- **A page stuck on its own challenge wall in the browser is not the end** — the
  same front-end usually delegates to an embed component whose pages/APIs sit on
  different hosts without the wall; traceroute the embed's own host chain instead
  of fighting the challenge loader.
- **Backend service vs local scripts need different dependency sets**: check the
  systemd unit's interpreter (its venv) for every import a new module needs
  (`cryptography`, a wasm runtime, `httpx`) before wiring endpoints; a missing
  import in the service venv shows up as a 500 only after restart.

## 6. Handoff: what the backend needs from the prototype

Keep from the prototype, hand to the implementer:

- The registry + per-provider classes verbatim (registry caches, fallback order,
  error dicts already built here).
- The HLS relay module: playlist rewrite (all URIs → own proxy), per-provider
  Referer/Origin spoofing, Range passthrough — one module serves all providers.
- The verification ladder as the acceptance test: a provider is "done" when
  ffprobe reads real video through your own proxy path.
