# Wiring Third-Party Apps to 9router

A local OpenAI-compatible router (9router, API `127.0.0.1:20128`) sits in front of pooled upstream
providers, and external apps get pointed at it instead of their documented provider. Assess
compatibility from the APP's source first, then probe the router with the app's exact request
shape. Never answer 'will it work?' from the `/v1/models` list alone — list membership proves
nothing about wire behavior.

## Step 1 — Read the app's client code before promising anything

Fetch the source (clone the repo / unzip the app) and establish four facts:

1. **Protocol shape.** OpenAI `chat/completions` is the only protocol the router speaks. A
   proprietary protocol (vendor SDK with its own pick-one-of-N + score endpoint) is a mismatch no
   model choice can fix — it needs a translating shim.
2. **Base-URL overridability.** Grep for hardcoded constants (`api.openai.com`, `const API =`)
   and for env/config overrides. A hardcoded constant with no override means a source patch +
   rebuild; check the shipped deployment mode (prebuilt image vs local `--build` compose) allows
   that before recommending it.
3. **Per-call timeout and failure mode.** Decision-loop apps often fail CLOSED (hold, do nothing)
   when the model call is slow or errors. Compare the app's timeout against the router's real p95
   latency for the candidate model — a technically-working shim is useless if answers arrive after
   the timeout and the app just holds forever.
4. **Endpoint classes used.** Chat is not the whole surface. Probe every class the app calls:
   `/v1/images/*`, embeddings, files. A router proxies chat while returning 404/400 for image
   endpoints (no upstream credentials), and a single required image call (e.g. a mandatory setup
   portrait) can block the app's whole first-run flow even when chat works.

## Step 2 — Find undocumented overrides in the SDK dependency

Download the exact version-pinned tarball and grep the dist, not the README:

```bash
curl -sL https://registry.npmjs.org/<pkg>/-/<pkg>-<ver>.tgz -o /tmp/p.tgz && tar xzf /tmp/p.tgz -C /tmp
grep -n 'baseURL\|BASE_URL' /tmp/package/dist/*.js /tmp/package/dist/*.d.ts
grep -on 'https://[a-zA-Z0-9./-]*' /tmp/package/dist/*.js | sort -u
```

The constructor config, the ENV name map (`<PKG>_BASE_URL`-style), and the default endpoint sit
right there. This regularly turns 'impossible, hardcoded' into 'one env var'.

## Step 3 — Probe the router with the app's exact request shape

Pull a key from the router DB (`apiKeys` table) into a variable WITHOUT printing it, then
replicate the app's call: same endpoint, same `response_format` (e.g. strict `json_schema`),
realistic prompt, generous `max_tokens`. Use `scripts/inspect_9router_state.py` for the combo/
provider layout first.

A candidate model passes only if ALL hold:

- The HTTP response parses as ONE complete JSON object: decode with
  `json.JSONDecoder().raw_decode(raw)` and inspect the trailing bytes. Some upstreams append SSE
  fragments (`data: [DONE]`) even to a non-stream response, which breaks the app's `res.json()`.
- `choices[0].message.content` parses as JSON and matches the requested schema. Some models
  ignore `json_schema` strict mode and return plausible-but-wrong fields — parse + field-check,
  don't eyeball.
- Nothing streamed when `stream` was not set (some provider paths always emit SSE chunks).
- `finish_reason` is not `length`: reasoning models burn completion tokens on `reasoning_content`
  before the answer, so a small `max_tokens` returns EMPTY content that looks like a refusal.

Prefer a stable combo for production wiring; free-tier paths 503 under load. For non-streaming
POSTs the router's own retry middleware helps; for streaming it does not.

## Step 4 — Pick the integration path

- **Clean pass** → point the app at the router (env var or 2-line patch), rebuild, and re-test the
  app's real flow end-to-end, not just the probe.
- **Protocol mismatch** → write a small translating shim (accept the vendor protocol, forward as
  chat completions, map the response back). It only needs the fields the app actually reads.
- **Hard requirement the router cannot meet** (e.g. image generation with no upstream credential)
  → scope a native provider key to the one-time part of the flow if the app separates setup-time
  from runtime calls, or patch the requirement out of the app's source. State plainly which parts
  run through the router and which do not.

Never report an integration as viable on probe success alone when a mandatory setup flow still
blocks on an endpoint the router does not cover.
