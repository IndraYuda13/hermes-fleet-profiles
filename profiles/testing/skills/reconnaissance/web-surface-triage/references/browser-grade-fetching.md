# Behind a local getting-started page: browser-grade fetching for challenge / framed hosts

Some hosts you must test sit behind an interactive anti-bot challenge (Cloudflare
"Just a moment...") or answer only to a real browser stack. The `web` surface's
recovery ladder (`blocked-page-recovery`) recovers *content*; this reference is
about using a local **browser-grade fetcher** to keep testing a **target host**
from a script.

The local stack (Docker on the engagement host):

- **FlareSolverr** at `http://127.0.0.1:8191` — solves the challenge itself and
  returns the resolved page.
- **Playwright / Patchright + Chromium** on PATH — for full in-page behaviour
  (clicks, XHR capture, route enumeration) when the challenge cannot be solved
  headlessly by FlareSolverr.

## The one call that matters

```bash
curl -s -m 120 -X POST http://127.0.0.1:8191/v1 \
  -H 'Content-Type: application/json' \
  -d '{"cmd":"request.get","url":"https://TARGET/","maxTimeout":90000}'
```

The body is JSON — the page itself is under `solution.response`, not the outer
level. Read `solution.status` and `solution.url` too: a challenge that resolves
can land you on the final URL after a redirect.

## Pacing (why this binds)

- Sequential calls only. Two or three back-to-back requests earn the
  FlareSolverr IP a Cloudflare `520`; the "solution" then contains the edge's
  error HTML (`<title>... | 520 ...`), which looks like a fetch but is not the
  target.
- Between requests in a loop, wait tens of seconds. Treat it like a human
  browser, not a scanner.
- If one host keeps answering `520` after pacing, park it as **untested** and
  note the evidence; do not mark it clean.

## Provenance discipline

A resolved page is a **live** fetch, not a snapshot: cite it like any other
live request but record that the challenge was solved via FlareSolverr (and its
version, from `GET http://127.0.0.1:8191/`, which returns `version` plus the
resolved UA). That UA is what the target's logs will show — keep tests
attributable instead of anonymous.

## What it is and is not for

- **Is for**: pulling the shell, the JS bundles and the REST/JSON surface of a
  challenge-framed host so recon continues; confirming that a `403` was the
  challenge and not the app.
- **Not for**: credential guessing, session forgery, or bypassing an
  *authorization* control. A solved challenge yields the same unauth surface
  any visitor sees; anything beyond that stays scoped to the engagement's
  written authorization.
- **A solved render does not carry clearance for the page's own follow-up API
  calls.** When the app gates its API behind its own exchange (an invisible
  Turnstile solved in-page plus a short-lived minted token), FlareSolverr gets
  you the HTML but not that token — reproduce the app's own token flow (or drive
  a full browser through the proxy pool, §5 of `datacenter-blocked-targets.md`)
  before concluding the API is unreachable.

## Anti-patterns

- Don't send every request through FlareSolverr — it is slow and rate-bound.
  Use it only for the challenge-gated hosts, then keep using plain curl/httpx
  for the rest.
- Don't interpret a `520` body as "the host is down". The edge answered; the
  tool was throttled. Re-test once, paced, then downgrade that host's coverage.
- Don't attribute the challenge to the target as a finding by itself — an edge
  in front of a host is infrastructure context, not a vulnerability.
- Don't rotate IPs at a loader that returns a constant placeholder (`// mt`, an
  empty `<html></html>`) from every node and UA — that is a browser-side
  challenge handshake (note `accept-ch: sec-ch-ua-*` response headers), not an
  IP block. Use a full browser, or pivot to the downstream component the page
  delegates to; its endpoints are usually the less-protected path.
