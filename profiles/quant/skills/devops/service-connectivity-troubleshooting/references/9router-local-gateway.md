# 9router local gateway reference

When a public 9router endpoint demands a key, first determine whether the caller is on the same host and whether the local listener intentionally uses different auth policy. A local URL such as `http://127.0.0.1:20128/v1` is only local to the host process; from a container, use the host bridge or a shared network.

## Common boundary failures

- Application SSRF protection may intentionally reject private host addresses; do not weaken it without an explicit trust-boundary decision.
- `localhost` inside Docker is the container itself. Use an explicit host bridge address or Docker service DNS.
- Proxy variables can redirect internal traffic; set both `NO_PROXY` and `no_proxy` for loopback and bridge addresses.
- SQLite terminal output may truncate long API keys. Query an untruncated representation (e.g. `hex(key)`) and decode it before use.
- An `invalid character` parsing error frequently means the client received HTML, text, or SSE rather than JSON; capture the raw response and ensure the request's stream mode matches the client's parser.
- If 9router is systemd-managed, restart through systemd so its expected service environment and dynamic tokens remain consistent.
