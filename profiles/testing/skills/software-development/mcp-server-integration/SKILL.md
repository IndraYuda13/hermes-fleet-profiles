---
name: mcp-server-integration
description: "Use when wiring an MCP server into a Hermes profile."
version: 1.0.1
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [mcp, hermes, configuration, integration, stdio, toolsets]
    related_skills: [hermes-agent]
---

# MCP server integration (Hermes profiles)

Auditing, installing, and verifying a third-party MCP server for a Hermes
profile, and answering "is it already installed?" correctly. The order matters:
**audit → probe → register → apply → verify**. Skipping the probe produces a
config entry that looks right and never connects.

## When to Use

- "Can this be installed on our setup? Is it already installed?" — for any MCP
  server, CLI-with-MCP-mode, or agent extension the user points at.
- Registering a new MCP server (stdio or HTTP) in a profile's `config.yaml`.
- An MCP server is configured but its tools never appear in a session.
- The user asks for planning before any install into the live Hermes setup.

## Step 1 — Audit before installing anything

```bash
npm ls -g --depth=0              # is the package already installed globally?
which <cli>; <cli> --version     # does the binary resolve?
hermes config path               # WHICH config.yaml is live (profile-aware)
hermes config get mcp_servers    # already wired? "Config key not set" = not wired
hermes mcp list                  # connected servers
<cli> doctor --json              # tool's own diagnosis, when it has one
```

A package can be **installed and dormant at the same time**. A binary on PATH
plus no `mcp_servers` entry means "not wired", and that is what to report —
never collapse the two into "already installed". Distinguish the states the
tool's doctor reports (missing registration vs missing config vs missing backend
engine) before proposing work.

All of these are profile-relative. With profiles in play, resolve the live file
first (`hermes config path`) instead of assuming `~/.hermes/config.yaml`. The
gateway's PATH already contains the Hermes-managed node bin directory, so a bare
binary name resolves without exporting PATH.

## Step 2 — Prove the server speaks MCP before writing config

- **stdio server** → `scripts/mcp_stdio_probe.py <command> [args...]`. Real
  JSON-RPC handshake over stdin/stdout; prints server name, version, protocol
  version, tool count.
- **SSE / HTTP server** → `scripts/mcp_sse_probe.py <url> [bearer-token|-] [tool|json-args ...]`.
  Handshake + `tools/list`, then optional benign calls. Run it once WITHOUT the
  token too: a `401` proves the auth layer is alive, a full tool list proves the
  token. SSE servers must emit `event: endpoint` + `data: ?sessionId=…` within
  seconds — if they do not, the transport is wrong, not the config.

If the probe fails, fix the server — do not register a broken entry and debug it
through the agent's logs. A successful probe is also what lets you tell the user
"the server itself is healthy" — and nothing stronger: a raw probe handshakes
against the server URL directly, so it never exercises Hermes' own config path
(env/secret rendering, transport selection, tool registration). Proving THAT
path is step 5's job.

## Step 3 — Register in the profile's config.yaml

Shape of the entry (target form):

```yaml
mcp_servers:
  <name>:
    command: /absolute/path/to/<cli>   # absolute path > npx: no exec hop, no cache dependency
    args: ["<subcommand-that-starts-stdio>"]
    env:                                # anything the server needs MUST go here
      SOME_DIR: /absolute/path
    connect_timeout: 60
    timeout: 300
```

Remote / SSE entry (no `command` — the transport is the URL):

```yaml
mcp_servers:
  <name>:
    url: http://127.0.0.1:9876/
    transport: sse            # SSE-only servers need this explicit; streamable-HTTP has an automatic initial-connect SSE fallback
    headers:
      Authorization: "Bearer <token>"
    connect_timeout: 30
    timeout: 300
```

Pass a multi-key entry to `hermes config set` as ONE JSON argument (nested
maps survive), then re-read `hermes config get mcp_servers` after every write.

Apply it through `hermes config set` (or the dashboard's MCP page), never by
hand-editing `config.yaml` — a stray indent corrupts the live gateway. Check
`hermes config set --help` on the running version for how it takes list/map
values, and confirm with `hermes config get mcp_servers` afterwards.

**Environment filtering is the most common silent failure.** For stdio servers
Hermes passes only a safe baseline (`PATH`, `HOME`, `USER`, `LANG`, `LC_ALL`,
`TERM`, `SHELL`, `TMPDIR`, `XDG_*`) — every other variable in your shell is
stripped. A server that depends on an exported path/credential and is launched
without an `env:` block fails as if it were broken. Put those variables in the
entry.

## Step 4 — Skills shipped by other ecosystems do not auto-load

Many agent tools install their companion skill into `~/.agents/skills/<name>`
(or `.claude/skills/`). Hermes scans its own skills directory plus
`skills.external_dirs`, so that skill stays invisible until the path is added
there. Installing the companion skill is not the same as loading it.

## Step 5 — Apply, then verify by calling a tool

A running session does NOT pick up the new entry by itself. Apply it with
`/reload-mcp` (reconnects servers and rebuilds the tool surface; it invalidates
that session's provider prompt cache, and the confirm modal's "always" opt-out
persists as `approvals.mcp_reload_confirm: false`). The next CLI session loads
it automatically — CLI sessions watch `mcp_servers` and auto-reload on change
(unless `mcp.auto_reload_on_config_change: false`). On a multiplexed host,
bounce only the affected profile; a gateway restart drops every served
profile's in-flight turns.

Tools appear as `mcp_<server>_<tool>` (some surfaces render
`mcp__<server>__<tool>`). Finish with TWO checks — neither substitutes for the
other:

1. `hermes -p <profile> mcp list` — inventory only: shows transport and
   enabled state, never proves a live connection.
2. ONE real tool call from a fresh session, e.g.
   `hermes -p <profile> chat -q "call <tool> with <benign args> and report the raw result"`.
   Startup logs saying "connected" are not proof either.

When the client path itself is in doubt, connect through Hermes' own code —
`/usr/local/lib/hermes-agent/venv/bin/python` plus
`tools.mcp_tool_discovery._connect_server(name, config)` — which follows the
exact config-rendering and transport-selection path the agent uses, and is the
cheapest way to isolate "server broken" from "Hermes-side wiring broken".

## Pitfalls

- **`hermes mcp add` ends in an interactive "Enable all N tools?" prompt** — with
  no TTY (agent shell, piped run) it auto-cancels AFTER saving nothing, and the
  server simply doesn't appear in `mcp list`. Pipe the answer:
  `printf 'y\n' | hermes -p <profile> mcp add <name> --command ... --env ... --args ...`.
  Use `--args` as the LAST flag (its value swallows trailing words).

- **A tool name that resolves to an unrelated same-name binary.** `httpx` may be
  the Python HTTP client CLI while the intended tool is ProjectDiscovery's Go
  httpx — every wrapper built on the bare name silently runs the wrong program.
  `head -1 $(which <name>)` (shebang), `file`, and a `-version` probe separate
  them; put the real binary on PATH under a distinct name (`<name>-pd`) and
  reference that name everywhere (skills, wrappers, configs).
- **"Config looks right, tools never appear" — diagnose in this order:** server
  process running → listening on the expected port → unauthenticated request
  returns `401` (auth layer alive) → transport handshake (SSE `event: endpoint`)
  → Hermes' own connect path handshakes (step 5). Each failure has a different
  fix; jumping straight to re-registering the config wastes the whole cycle.
- **`loaded: true` in a GUI app's extension config is not "running".** If the
  app's own startup is blocked (a first-run/modal dialog waits for a click),
  extensions never initialize and their ports stay closed even though the
  persisted config says loaded. Screenshot the display before concluding the
  extension is broken — the fix may be one click at the dialog, not a
  reinstall.
- **Config-dump commands mask secrets, so a masked value is not proof about
  what the server received.** `hermes config get mcp_servers` / `mcp list`
  redact anything key- or bearer-shaped. Verify the write by function (a
  token-protected endpoint answering 200 through the configured flow, one live
  tool call); read raw `config.yaml` only for shape/structure.
- **One malformed client config blocks an installer's whole write transaction.**
  When a tool's setup wizard manages several agents' config files, a single file
  in a bad state (`invalid`, truncated JSON) aborts every write, including the
  one you wanted. Read the wizard's `--dry-run`/doctor output for the offending
  path and repair or remove that file *before* blaming the new install.
- **Read engine/version requirements from the installed package's own constants,**
  not the upstream README. A README tracking `main` can describe a newer release
  than the npm version actually installed. Look for a `*InstallationPolicy.*`
  style module with `SUPPORTED_*_VERSION` / `SUPPORTED_*_JAVA_MAJOR` and cite it.
- **Not every tool's setup wizard supports Hermes as a client.** Check the tool's
  own client registry or `--client` list. If the host agent is absent, the
  automatic setup path cannot wire it: install the companion skill through the
  tool's generic/other-client route and register the MCP entry by hand.
- **Price the disk before pulling a large analysis engine.** A downloaded archive
  plus its extracted tree is roughly 2–3× the download size. Check free space
  first, report the numbers, and get agreement before deleting anything —
  proposing a cleanup is not authorization to delete.
- **A subcommand that shells out to a third-party npm helper fails when that
  package cannot be fetched.** When a CLI's convenience subcommand needs an
  external package on demand, prefer the direct/manual path (write the config
  entry yourself) over retrying the wrapper.

## Support files

- `scripts/mcp_stdio_probe.py` — standalone JSON-RPC handshake/tool-list probe.
- `scripts/mcp_sse_probe.py` — SSE probe: handshake, tool list, and optional
  tool calls against a bearer-token SSE endpoint.
- `references/rea-agents.md` — REA (`rea-agents`) specifics: client registry,
  engine providers, companion-skill location, install/pinning notes.
