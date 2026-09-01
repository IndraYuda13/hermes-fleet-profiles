# 9Router local gateway and OpenAI-contract audits

Use this reference for read-only compatibility checks of a local 9Router deployment. Reconfirm behavior against the installed version and upstream commit because provider translators and route guards change frequently.

## Safe read-only audit workflow

1. Identify the listener, owning PID, executable, working directory, installed package version, and bind address. Do not restart the service.
2. Clone upstream into `/tmp` and record its commit/version. Never pull into a live project when the user requested read-only work.
3. Open SQLite with URI `mode=ro`. Inventory table names, schemas, row counts, settings, combo names, and model identifiers only. Never print API keys, tokens, provider blobs, prompts, or responses.
4. For an authorized authenticated probe, read the key inside a script, use it only in the request header, and report status, content type, key names, counts, and protocol markers rather than payload text.
5. Send minimal prompts and cap output. Add `x-9router-token-saver: off` when testing the raw contract rather than RTK/Headroom behavior.
6. Test each boundary separately: loopback, Docker bridge/service DNS, and reverse-proxy/public path. Use `curl --noproxy '*'` for direct-hop checks so ambient proxy variables do not contaminate the result.
7. Verify protected repositories/directories are unchanged at the end. Successful chat probes may still append normal usage/request telemetry to 9Router's own database, so disclose that side effect.

## Base URL and Docker routing

The host-process base URL is normally `http://127.0.0.1:20128/v1`. Inside Docker, `localhost` is the container itself. Prefer one of:

- shared Compose network and 9Router service DNS;
- `http://host.docker.internal:20128/v1`, with Linux `host-gateway` mapping;
- explicit Docker bridge gateway such as `http://172.17.0.1:20128/v1` when stable in that environment.

Set both `NO_PROXY` and `no_proxy` for loopback, bridge addresses, and service names. Application SSRF protection may reject private addresses intentionally; do not weaken it without an explicit trust-boundary decision.

## Two auth layers

9Router may authorize `/v1*` at two distinct layers:

1. The request guard distinguishes trusted loopback traffic from remote/proxied traffic using the real TCP peer stamped by the custom server. A spoofed `Host: localhost` does not make a Docker-bridge request local.
2. Individual handlers may separately enforce the `requireApiKey` setting.

Consequences:

- `/v1/models` can be accessible without a key on true loopback while requiring a key through the Docker bridge.
- `/v1/chat/completions` can still require a key on loopback when `requireApiKey` is enabled.
- Guard errors may be a simple `{error: "..."}`, while handler errors use OpenAI-style `{error:{message,type,code}}`.
- Accepted client credentials include `Authorization: Bearer ...` and `x-api-key`; never disclose which stored key was used.

Probe loopback and bridge independently. Do not infer remote auth policy from localhost behavior.

## OpenAI-compatible contract checklist

Check all of the following with minimal, non-sensitive requests:

- `GET /v1/models`: status, JSON content type, top-level `object: "list"`, `data[]`, model IDs, combo entries, and `owned_by`.
- Non-stream chat: status, JSON content type, `id/object/model/choices/usage`, and `choices[0].message` shape.
- Streaming chat: `text/event-stream`, every `data:` frame, chunk/delta shape, terminal `finish_reason`, and separately whether literal `data: [DONE]` appears. A clean socket close is not equivalent for clients that wait for `[DONE]`.
- Default streaming semantics: test omitted `stream`, explicit `stream:false`, and `Accept: application/json`. Do not assume OpenAI's default behavior.
- Tool calling: declaration, forced `tool_choice`, `message.tool_calls[]`, function name, JSON-string arguments, and stream finish reason `tool_calls`.
- `response_format`: test `json_object` and `json_schema` separately with an adversarial prompt. HTTP 200 and parseable JSON do not prove schema enforcement.
- CORS: test preflight with no Origin, loopback Origin, and external Origin. The outer auth guard may block the route's `OPTIONS` implementation.

## Version-specific compatibility cautions

Observed in 9Router 0.5.45 and requiring revalidation on newer versions:

- The server can default to streaming unless `stream:false` or a JSON-preferring `Accept` header changes the path.
- OpenAI-style SSE chunks may terminate without literal `[DONE]`.
- `json_object` can work while `json_schema` is prompt-emulated or dropped by a provider translation path. Validate returned content against the requested schema yourself.
- Tool calling is provider-dependent. Translation to Claude-like providers can alter `tool_choice`; in this version, `tool_choice:"none"` may become `auto`.
- `parallel_tool_calls` is not uniformly preserved across Chat Completions to Responses/provider translations.

These are compatibility findings, not reasons to reject the gateway globally. State the tested provider/model/combo, local version, and upstream commit.

## Combo aliases, account fallback, and retry

Combo names have no slash and are resolved exactly from the combo table. `/v1/models` exposes combos as models, but a combo containing one target is only an alias, not meaningful cross-model fallback.

Audit both layers:

- combo strategy and ordered target list: fallback, round-robin, or fusion;
- account strategy within each provider: fill-first or round-robin;
- per-model account locks and cooldowns;
- executor in-place retry by status and alternate upstream URLs.

Do not summarize “auto-fallback enabled” without proving that the active combo has multiple viable targets. Retry defaults and provider overrides are version-specific; read the installed source rather than relying on marketing text.

## Compression behavior

RTK and external compression are separate:

- RTK mutates recognized tool-result payloads in process, skips errors and small/unrecognized blobs, and rejects empty or larger output.
- `x-9router-token-saver: off` opts a request out of token savers and is useful for contract probes.
- Headroom calls `{HEADROOM_URL}/v1/compress`, uses a short timeout, and fails open. In Docker, a sidecar should use service DNS; host Headroom needs host-gateway routing.
- A configured Headroom URL does not prove a listener exists or compression is enabled. Probe health/listener state independently.

## Common pitfalls

- Do not copy terminal values elided with `...`. Retrieve an untruncated representation only when needed, and keep credentials inside the process performing the request.
- An `invalid character` parser error often means HTML, text, or SSE was treated as JSON. Capture raw content type and framing first.
- Do not print full request logs or provider blobs; they can contain prompts, responses, credentials, and account identifiers.
- Host-header rewriting does not override the custom server's trusted peer-IP decision.
- If 9Router is service-managed, preserve its lifecycle environment and dynamic tokens by using the owning manager for any explicitly authorized restart.
