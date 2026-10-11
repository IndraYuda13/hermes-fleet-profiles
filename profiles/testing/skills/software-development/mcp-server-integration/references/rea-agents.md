# REA (`rea-agents`) — reverse-engineering MCP server

Companion notes for the `mcp-server-integration` workflow. REA is a CLI + MCP
server that drives disassemblers and artifact parsers so an agent can inspect
shipped binaries, ASAR/JS trees, archives, managed assemblies, firmware, and
runtime captures.

## Wiring into Hermes

- Package `rea-agents`, CLI `rea` (alias `rea-agents`), MCP entrypoint
  `rea mcp` (**stdio**). Register it manually: REA's client registry covers
  Claude Code/Desktop, Codex, Cursor, Gemini CLI, Windsurf, Devin, OpenCode,
  Antigravity, Copilot CLI, CommandCode and VS Code — **not Hermes**. Use
  `rea setup --client generic` for the companion skill and add the `mcp_servers`
  entry yourself.
- The companion skill is installed to `~/.agents/skills/reverse-engineer-anything`
  — invisible to Hermes until that path is in `skills.external_dirs`.
- Engine paths belong in the entry's `env:` block (`GHIDRA_INSTALL_DIR`,
  `JAVA_HOME`, `HOPPER_LAUNCHER_PATH`, `REA_ANALYSIS_PROVIDER`) because Hermes
  filters the shell environment for stdio servers.

## Verifying without changing anything

```bash
rea mcp doctor --json       # boots the stdio server: tool inventory + catalog digest vs npm version
rea doctor --json           # read-only environment/registration audit
rea providers --json        # which analysis providers exist
rea capabilities --json     # per-operation availability + availability_code
```

`doctor`/`providers` distinguish `missing_analysis_engine` from `config_drift`,
so it separates "engine not installed" from "registration stale" — exactly the
classification to report. Artifact/archive/JS/managed-assembly operations work
with **no engine**; native decompilation needs Hopper, Ghidra, or IDA.

## Setup wizard behaviour

- Writes are additive and backup-first, read back and verified; reruns are safe.
- A **single malformed managed client config aborts the entire transaction**
  (state `invalid`), including writes to other clients. Inspect the reported
  config path and repair it first.
- `--dry-run` / `--json` print the plan without applying it; `--client <id>`
  (repeatable) or `--all-detected` scope it; `--install-hopper` is required to
  approve Hopper installation non-interactively.
- `rea mcp add` delegates to a third-party npm helper; when that package cannot
  be fetched, register the stdio entry directly instead of retrying it.

## Analysis providers

- **Ghidra** — bring-your-own, read-only: extract an official release and export
  absolute paths externally, then `GHIDRA_INSTALL_DIR` + `JAVA_HOME`. REA pins an
  **exact** supported release and JDK major: read them from the installed
  package's `dist/ghidra/GhidraInstallationPolicy.js`
  (`SUPPORTED_GHIDRA_VERSION`, `SUPPORTED_GHIDRA_JAVA_MAJOR`) rather than the
  README, which tracks `main`. A newer/older release is reported with an
  "unverified build" limitation instead of being silently accepted.
- **Hopper** — separate commercial app with a free demo mode; on Linux REA runs
  it on a private Xvfb display, so no desktop session is needed. It is installed
  only through the REA setup path (native package manager), not by direct
  download; a paid license is never required or automated.
- **IDA** — reuses an existing IDA MCP registration (`REA_IDA_MCP_CONFIG`).

## Cost planning

Ghidra's release archive alone is several hundred MB and its extracted tree
several GB; plus a JVM. Check free disk, report the numbers, and obtain explicit
agreement before removing anything to make room.
