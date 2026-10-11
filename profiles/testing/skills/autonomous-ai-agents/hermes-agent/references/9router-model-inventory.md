# 9router — Model Inventory of a Custom Provider

Task class: "what models are available under provider Y / prefix X on my 9router?" The user names a
custom OpenAI-compatible provider by its LABEL (the name shown in the 9router UI, e.g. a monthly-plan
gateway); its models carry a PREFIX in their ids (`prof/<model>`).

Deliverable: the grouped model list + a router-vs-upstream sync verdict + one liveness proof —
not a raw id dump.

## 1. Resolve the label to its node and baseUrl

DB: `~/.9router/db/data.sqlite` (open read-only — never write to the router's DB).

```bash
sqlite3 ~/.9router/db/data.sqlite \
  "SELECT id, type, name, data FROM providerNodes WHERE lower(name) LIKE '%<label>%';"
# node data JSON: {prefix, apiType, baseUrl}
sqlite3 ~/.9router/db/data.sqlite \
  "SELECT id, provider, name, data FROM providerConnections WHERE provider='<node id>';"
```

- `providerConnections.provider` holds the NODE id (`openai-compatible-chat-<uuid>`), not the label.
- Connection `data` JSON: `apiKey`, `defaultModel`, `providerSpecificData{prefix, apiType, baseUrl,
  nodeName}`, plus per-model locks — mask `apiKey`/`password` in anything printed.
- Column names are camelCase (`createdAt`, `updatedAt`); `created_at` raises "no such column".
- `settings` is ONE JSON blob (`SELECT data FROM settings WHERE id=1`), not key/value rows;
  `SELECT key, value FROM settings` errors.
- If the user already gives the prefix, you can filter `/v1/models` directly — but still resolve the
  node, because you need `baseUrl` for the upstream diff in step 3.

## 2. Router-side list

```bash
curl -s http://127.0.0.1:20128/v1/models | python3 -c "import sys,json; \
  [print(m['id'], m.get('owned_by')) for m in json.load(sys.stdin)['data']]"
```

- `/v1/models` answers even with a dummy Bearer — safe for enumeration. Completions are not: see step 4.
- Custom-node models appear as `prefix/model` with `owned_by` = the prefix; combos appear with
  `owned_by=combo` (combo internals: `scripts/inspect_9router_state.py`).

## 3. Upstream list + diff (is anything hidden?)

The node's `baseUrl` (`https://<host>/v1`) usually serves its own `/v1/models` openly, with richer
metadata than the router passes through:

```bash
curl -s -m 30 https://<host>/v1/models -o /tmp/upstream_models.json
```

Diff the id sets both ways in Python (strip the prefix on the router side). Zero diff = the router
exposes everything upstream offers. Router-only ids = stale config or combo leftovers;
upstream-only = filtered out at the node/connection level.

- Context windows can DISAGREE between the two lists (router `context_length` — what Hermes uses —
  vs upstream's own number; observed 1M vs 262144 for the same model). Report the router value, and
  flag the discrepancy only when model choice depends on it.

## 4. One liveness proof (not all models)

Pull a working key from `apiKeys` into a variable WITHOUT printing it, then run one small completion:

```bash
KEY=$(sqlite3 ~/.9router/db/data.sqlite "SELECT key FROM apiKeys WHERE name='Production Key';")
curl -s -m 120 http://127.0.0.1:20128/v1/chat/completions \
  -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' \
  -d '{"model":"<prefix>/<model>","messages":[{"role":"user","content":"reply OK"}],"max_tokens":5}'
```

- First completion through a custom provider can take 30–60 s (cold model / upstream queue). A 30 s
  timeout returning HTTP 000 cannot distinguish auth failure from cold-start slowness — give ≥90 s
  and a real key before concluding a provider is down.
- Expect `reasoning_content` even for trivial prompts on thinking models; `system_fingerprint`
  identifies the actual upstream operator. Response-parsing caveats (SSE tails appended to
  non-stream responses, `finish_reason: length` burning content on reasoning): see
  `references/9router-app-integration.md` step 3.

## 5. Reporting shape (preferred)

- Group by family (Claude / GPT / Grok / DeepSeek / Qwen / GLM-Step-Nemotron / misc); give
  "uncensored"/"unrestricted" variants their own flagged section when the provider hosts them.
- State counts (total, per group) and note non-standard vision / context windows.
- Include the sync verdict ("router == upstream, nothing hidden") and the one tested model with its
  HTTP status and latency.
- Keep ids in `prefix/model` form so they are copy-pasteable into Hermes config.
