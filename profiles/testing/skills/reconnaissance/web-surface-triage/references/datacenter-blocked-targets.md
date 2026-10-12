# Testing Targets That Block Datacenter Egress

Some targets (commonly Indonesian government sites) accept DNS resolution from
anywhere but filter TCP 80/443 from datacenter/hosting IP ranges. Every direct
HTTP tool from the sandbox — curl, sqlmap, httpx, nmap service probes — then
times out with code `000` while `https://example.com` still answers. That is a
re-routable condition, not a dead target: the cloud browser backend's egress is
separate from the sandbox's and usually still reaches the host. Verify that
separation holds in the current environment before relying on it, then run the
whole HTTP test through the browser.

## 1. Confirm it is the target filtering, not your stack

- `curl -skI -m 25 https://host/` returning `000` after a full timeout, while a
  control fetch to a known-good site returns 200, means filtered — not offline.
- Probe TCP on **each** resolved A record (round-robin DNS may have one
  reachable address): `timeout 8 bash -c 'echo > /dev/tcp/IP/80'`, then :443.
- Compare DNS views: local `getent hosts` vs DoH
  (`curl -s https://dns.google/resolve?name=host&type=A`). If the public answer
  is an RFC1918 address, an egress proxy will refuse the navigation itself
  ("private or internal address") — that is proxy policy, not the target.
- Port-level filtering is the expected posture for this class of target; a
  bounded `nmap --top-ports` sweep is confirmation only. Do not burn engagement
  time on full port sweeps of filtered hosts.

## 2. Reachability triage across the estate

For every host in scope, test **both** paths and record the result per host:

- Sandbox: `curl -sk -o /dev/null -w "%{http_code}" -m 8` for `https://` and
  `http://` (some hosts serve only one).
- Browser: navigate `location.assign(url)` and read `location.href` — a
  `chrome-error://chromewebdata/` URL with `ERR_CONNECTION_CLOSED/SSL_PROTOCOL`
  text is unreachable; a real page is reachable. The browser proxy may refuse
  hosts the sandbox reaches and vice versa, so never classify a host from one
  path alone.

Directly reachable hosts get the full tooling (curl batteries, sqlmap, nuclei).
Browser-only hosts get the manual route below. Anything reachable by neither is
**UNTESTED** — carry that label into the report verbatim.

## 3. Browser as instrumented HTTP client

Navigate to any page on the target origin first, then install a fetch helper
once (same-origin fetch sends cookies/Origin naturally; custom headers like
`X-Requested-With` are allowed, but `Cookie`, `Origin`, and `User-Agent` are
forbidden header names — header-control tests need a directly reachable host):

```js
window.__h = (u, o) => fetch(u, o).then(r => r.text().then(t => {
  const hd = {}; r.headers.forEach((v, k) => hd[k] = v);
  return {status: r.status, headers: hd, body: t};
})).catch(e => ({err: String(e)}))
```

- Persist every fetched HTML/JSON body to the workspace scratch dir before
  parsing; parsing live via repeated `js()` calls wastes the CDP budget.
- Helper functions live in the page's JS realm and **die on navigation**. Keep
  the helper source in a workspace `.py` file so re-installing after any
  navigation is one line. Install helpers AFTER navigation completes.
- Navigation can itself exceed the CDP window: use
  `js("location.assign(url)")` plus a sleep instead of awaiting navigation.

### The ~5s CDP limit decides the loop shape

`js()` kills any evaluation after about five seconds. A fetch that takes longer
(slow page, slow query) raises a harness timeout that LOOKS like a target
failure. Never await the fetch inside `js()`:

- Dispatch fire-and-forget with an IIFE that returns immediately and parks the
  result:

```js
js("(() => { window.__r = null; window.__h('/path', {...})" +
   ".then(x => { window.__r = JSON.stringify(x) })" +
   ".catch(e => { window.__r = JSON.stringify({err: String(e)}) });" +
   "return 1; })()")
```

- Poll from Python: sleep 0.3–0.5s, `js("window.__r")` until non-null, cap at
  ~90s. The poll loop doubles as the timing oracle.
- For precise timings bracket INSIDE the browser (`window.__t0 = Date.now()` at
  dispatch, `__t1` in the `.then`); Python-side elapsed time includes poll
  granularity.

### Reading results

- Loop over payloads collecting status + length + Content-Type + timing; diff
  responses by length AND by counting result-bearing anchors (e.g. article
  links) rather than eyeballing raw HTML.
- Identical bodies across wildly different inputs means the parameter never
  reaches the query (early validation). Chase the parameter shape — don't
  throw more payloads at a normalized one.
- `%`-sequences in the URL path can draw a bare nginx `400 Bad Request` before
  any application code runs. A 400 on a payload with a 200 on a benign sibling
  is usually encoding noise, not WAF: resend the same sequence with a harmless
  prefix to confirm before calling it a filter.
- Explicit SQL-keyword payloads tend to trip 403 block pages only after
  aggressive probing, not on the first requests. Do the boolean-differential
  work BEFORE tripping the WAF; once 403s start, treat further positives as
  unreliable and pace down.

### Timing-oracle discipline

- Server-side slow queries are cache-dependent: first hit can take 12–25s,
  warm repeats 0.5s. Run each timing probe several times and report the range
  and reproducibility — never a single sample.
- A long hang ending in connection reset is a normal presentation of a slow
  upstream through an egress proxy: record "hang ≥Ns, reset", not "tool
  failure".
- A timing differential that appears only with valid-shaped values (valid IP,
  existing record id) and vanishes with malformed ones indicates an
  early-exit validation path. That is itself a target-behavior finding
  (unauthenticated slow endpoint, missing index) — but it is NOT an injection
  oracle until boolean/timing payloads move the timing, not just validity.

## 4. Scope the report honestly

- Never-run tests are untested hosts, never "no issue". State per host which
  route applied (direct tooling vs browser-only manual battery), because it
  bounds what "not found" means for each.
- sqlmap cannot run through the browser-fetch route. For browser-only hosts,
  run manual boolean/error/timing batteries and record that limitation.
- Fingerprint leaks collected along the way (build/version endpoints, internal
  IPs in CSP headers, cert expiry) are findings in their own right — log them
  with the same evidence discipline as any other exposure.

## 5. Local residential proxy pool (Surfshark Proxy Studio)

This host runs a residential proxy pool (owned by another profile — treat it as
read-only infrastructure: use the nodes, never stop/restart/edit its service or
config). This is the strongest re-route when the target filters datacenter ASNs:
requests that get `403`/timeouts direct answer `200` through a residential node.

- List nodes + quality: `curl -s http://127.0.0.1:8808/proxies` — JSON per node:
  `node_id`, `proxy` (`http://127.0.0.1:310NN`), `country`, `ip`, `grade`/`risk`.
- HTTP through a node: `curl -x http://127.0.0.1:310NN <url>`. For a real browser:
  launch your own headless Chrome with
  `--headless=new --no-sandbox --proxy-server=http://127.0.0.1:310NN --remote-debugging-port=9777`
  and drive it over CDP (`PUT http://127.0.0.1:9777/json/new?<url>`; Node's
  built-in WebSocket works fine as the CDP client).
- Run proxy networking from the terminal: the browser harness refuses
  private-address URLs, so curl through the pool from the shell and give the
  browser its own `--proxy-server` rather than routing the harness.
- **Verify the egress before debugging downstream errors**:
  `curl -x <node> -s https://api.ipify.org` must return the node's IP, not the
  host's. Most "the proxy didn't help" results are requests that never went
  through it.

Sticky-IP rules (violating these costs real time):

- Chains that mint IP-bound credentials (JWT claims like `ip_cidr`, signed
  one-time URLs) must run EVERY step from the SAME node. Switching nodes
  mid-chain turns previously valid URLs into `404 Not Found`/`Session expired`;
  that is session invalidation, not a dead target.
- A node that worked can get flagged mid-session (starts erroring/404ing).
  Rotate to another node AND restart the chain from step 1 — retrying on the
  same node just reproduces the flag.
- Keep a browser session pinned to one node; per-request rotation breaks
  cookie/clearance continuity.
