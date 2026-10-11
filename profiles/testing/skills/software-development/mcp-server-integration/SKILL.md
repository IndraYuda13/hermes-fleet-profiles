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
**audit → probe → register → restart → verify**. Skipping the probe produces a
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

Run `scripts/mcp_stdio_probe.py` with the server's launch command. It performs
the real JSON-RPC handshake over stdin/stdout and prints server name, version,
protocol version, and tool count.

If the probe fails, fix the server — do not register a broken entry and debug it
through the agent's logs. A successful probe is also what lets you tell the user
"the server itself is healthy" independently of any registration state.

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

## Step 5 — Restart, then verify by calling a tool

`mcp_servers` has **no hot-reload**: the change lands only after the profile's
agent/gateway restarts. After restart, tools appear as `mcp_<server>_<tool>`.
Verify by calling one trivial tool and checking the real result — startup logs
saying "connected" are not proof that the tool set is usable.

## Pitfalls

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
- `references/rea-agents.md` — REA (`rea-agents`) specifics: client registry,
  engine providers, companion-skill location, install/pinning notes.
