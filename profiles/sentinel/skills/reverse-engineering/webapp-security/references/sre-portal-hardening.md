# SRE & observability portal hardening

Depth for security review of SRE dashboards, observability portals, and automation control planes.

## Upstream integrations

- Cache upstream reads in memory (TTL ≥ 60s) with strict per-request timeouts (≤ ~2.5s); unbounded multi-account polling invites upstream throttling and local DoS.
- Gate mutations on upstream state: while an account reports UNDER REVIEW / IN PROGRESS, suppress further triggers with backoff windows (hours) to avoid fraud flagging.
- `.gitignore` must block credential files (`config.json`, `state/`, `.env`, logs, session tokens) before any push; audit staged files (`git diff --cached`) in release pipelines.

## Process lifecycle (multiplexers → systemd)

- Terminate orphaned interactive multiplexer sessions (`screen -ls`, `tmux ls`) — duplicates compete for locks and sessions.
- Verify every supervisor and child worker executes the intended virtualenv interpreter (`psutil` / `ps aux`), not host site-packages.
- Unit sanity: `KillSignal=SIGINT`, `TimeoutStopSec=30`, `Restart=always`, `RestartSec=10` so workers flush atomic state; `journalctl -u <unit>` should show rate-limit/FloodWait cooldown syncs and no reconnect storms.
- Hardening directives: `ProtectSystem=full/strict`, `PrivateTmp=true`, `NoNewPrivileges=true`, `LimitNOFILE=65536`, explicit `ReadWritePaths=`. Flag any web-facing dashboard bound to `0.0.0.0` without authn/authz.

## Log streaming & SSE

- Initial tail: seek `max(0, file_size - 16384)`; `f.readlines()` on an active log is a memory-exhaustion DoS and event-loop stall.
- Track the byte offset and reset it (`last_pos = 0`) whenever `curr_size < last_pos` — log rotation otherwise stalls the stream permanently.

## Streaming media & reverse proxy

- Starlette/FastAPI: never pair `allow_origins=["*"]` with `allow_credentials=True`.
- Bound on-the-fly transcoding (`ffmpeg`, `yt-dlp`) with `asyncio.Semaphore(N)` and `proc.kill()` on `request.is_disconnected()`; unbounded subprocess endpoints exhaust PIDs and file descriptors.
- Validate text parameters (e.g. `lang`) against strict regexes before WebVTT concatenation — unescaped newlines inject arbitrary cues into cached responses.
- Health endpoints must not leak internal paths, cookies/tokens, or unmasked proxy connection strings.

## Sandbox protocol parameters (reference values)

Dedicated mock services on loopback ports (e.g. 8381-8384), two-step arming, ~10s auto-disarm for armed-but-unexecuted state, ~10s auto-abort that recovers the healthy baseline.
