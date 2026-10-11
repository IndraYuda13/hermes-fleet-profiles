---
name: rea-ghidra-hermes-setup
description: Use when installing REA + Ghidra for a Hermes profile.
---

# REA + Ghidra on Hermes profiles

REA (`rea-agents`, npm) gives agents deep reverse-engineering (Ghidra read-only,
Hopper, IDA, artifact graph, JS/Electron, APK) over MCP. REA 6.4.0+ has a native
`hermes` client id (see below), but this setup registers it by hand in the profile
config via a wrapper — that remains the preferred multi-profile approach.

## Install (per profile)

1. **Ghidra (Linux, free engine):** REA only accepts the exact version it was verified
   against — read `SUPPORTED_GHIDRA_VERSION` in
   `<npm>/rea-agents/dist/ghidra/GhidraInstallationPolicy.js`. Needs a full **JDK 21 or
   newer** (`javac` present). Extract to a big disk (e.g. `/mnt/tools/`), ~900 MB.
2. **Wrapper launcher** at `/usr/local/bin/rea-mcp` (see the TMPDIR trap below).
3. **Config:** `hermes -p <profile> config set mcp_servers.rea '{command: /usr/local/bin/rea-mcp, connect_timeout: 60, timeout: 300}'`
   — never hand-edit config.yaml. Do NOT add `args: [mcp]` when the wrapper already adds it.
4. **Skill:** copy `<npm>/rea-agents/skills/reverse-engineer-anything/` (SKILL.md +
   references/) into `<profile>/skills/<category>/`. Hermes only auto-loads skills under
   `<profile>/skills/`; `~/.agents/skills` (REA's own target) and `~/.claude/skills` are
   scanned only when listed in `skills.external_dirs`.
5. **Verify:** `rea doctor --json` (ghidra checks healthy) -> `hermes -p <p> mcp test rea`
   (139 tools) -> one real decompile.

## Isolate the install (a global npm install can vanish)

Symptom: every REA MCP server in every profile suddenly reports `Connection closed` and
`parked`, with the real cause in the per-profile `agent.log`:

    /usr/local/bin/rea-mcp: 19: exec: .../node-26.7.0-linux-x64/bin/rea: not found

Hermes' own tooling (notably an update) can delete global npm packages under
`<node>/lib/node_modules/` — `rea-agents` and `@21st-dev/cli` were both removed by one event,
leaving a wrapper or `command: rea` entry pointing at a binary that no longer exists.

Install REA into its own prefix on a stable volume and exec it directly, so Hermes tooling
cannot remove it:

```sh
mkdir -p /mnt/tools/rea && cd /mnt/tools/rea
printf '{"name":"rea-isolated","private":true,"version":"1.0.0"}\n' > package.json
npm install rea-agents@<SUPPORTED_GHIDRA_VERSION's REA release> --no-audit --no-fund
```

The wrapper then runs `node /mnt/tools/rea/node_modules/rea-agents/scripts/rea.mjs mcp`
(direct `node` + `.mjs` also sidesteps the executable bit and any broken symlink). Pin the REA
version rather than floating `@latest`: `doctor` verifies a specific Ghidra version, so a
floating REA can move that target and invalidate a working setup. Keep the global install as a
fallback branch only if it exists.

## The TMPDIR dot-path trap (FIXED upstream in 6.2+, wrapper still useful)

Ghidra's `ProjectLocator` rejects any project path element starting with `.`. REA creates
its Ghidra runtime root under `os.tmpdir()`. Hermes pins `TMPDIR` to
`<HERMES_HOME>/cache/scratch`, and HERMES_HOME is usually `~/.hermes` — so older REA
(<=6.1) fails every `open_binary`/`analyze` with:

    ERROR Abort due to Headless analyzer error: Path element starting with '.' is not permitted

**Since 6.2**, `dist/ghidra/GhidraSessionRoot.js` adds `ghidraSessionRoot()`: when the
resolved `TMPDIR` contains any dot-prefixed element it falls back to `/tmp` (or the nearest
dot-free ancestor). Verified live on 6.4.0: with `TMPDIR=/root/.hermes/cache/scratch`,
`open_binary` + `analyze_function` succeed and the runtime lands in `/tmp/rea-ghidra-*`.
On 6.2+ the wrapper's TMPDIR pin (below) is therefore belt-and-braces, not required.
Keep it for deterministic runtime location; drop it when refactoring toward upstream defaults.

**Trap to avoid:** setting `env.TMPDIR` in `mcp_servers.<name>.env` does NOT reliably win —
Hermes' MCP child env (`tools/mcp_tool_config.py::_build_safe_env`) always includes the
parent's `TMPDIR`, and observed spawns inherited the parent value instead. Either rely on
the upstream fix (6.2+) or use a wrapper that pins a dot-free TMPDIR before exec (the
wrapper's own export wins because it runs inside the child after Hermes built the env):

```sh
#!/bin/sh
export TMPDIR="${TMPDIR_CLEAN:-/mnt/tools/rea-runtime}"
export GHIDRA_INSTALL_DIR="${GHIDRA_INSTALL_DIR:-/mnt/tools/ghidra_12.1.4_PUBLIC}"
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java-21-openjdk-amd64}"
[ -d "$TMPDIR" ] || mkdir -p "$TMPDIR" 2>/dev/null
exec /root/.hermes/tools/node-26.7.0-linux-x64/bin/rea mcp
```

Use an absolute Node path, not `npx` (saves ~1s startup). For an isolated install, exec
`node /mnt/tools/rea/node_modules/rea-agents/scripts/rea.mjs mcp` directly.

## Upstream has a native Hermes client (6.4.0+)

Since 6.4.0, `rea` supports `--client hermes` (`HermesClientHome.js` resolves
`HERMES_HOME`, the `profiles/<name>/` layout, `active_profile` sticky selection, and
profile markers). One server serves all profiles. `rea setup --client hermes --dry-run`
plans writes to `<HERMES_HOME>/config.yaml` (target = the resolved profile dir; it does
NOT scan every profile) and installs the skill to `<HERMES_HOME>/skills/reverse-engineer-anything`
(NOT under a category subdir). It also writes a `config.yaml.rea.backup` file next to the
config. It registers the RAW node command with GHIDRA_INSTALL_DIR/JAVA_HOME as server
`env` keys, NOT the wrapper. For the multi-profile hosted setup here the wrapper remains
preferred: setup only configures the ONE resolved profile per invocation and its raw-node
registration loses the wrapper env layering. Doctor's skill identity resolves per
`--client hermes`; with the skill installed under a category dir (e.g.
`skills/reconnaissance/reverse-engineer-anything`) doctor reports `skill: identity
missing` (`config_drift`, cosmetic — the skill still loads in Hermes). To satisfy doctor,
the skill would need to sit at `skills/reverse-engineer-anything` (flat); the category
layout is fine otherwise.
Likewise `registration:hermes` shows state `stale` under the wrapper launcher — doctor
compares against the raw-node registration `rea setup` would write, so this is expected,
not breakage. Confirm liveness with `hermes -p <p> mcp test rea` and a real decompile.

## Release cadence & version pinning (observed Oct 2026)

REA ships frequently (4 minor releases in 3 days: 6.0.0 → 6.4.0, all with breaking changes;
`always-bump-minor` policy — a minor bump is NOT a compatibility promise). Keep the install
pinned to an exact version as this skill already recommends. Upgrade procedure that worked
(staged in scratch first): bump `rea-agents` to the target in `/mnt/tools/rea/package.json`,
`npm install --no-audit --no-fund` (~13s), re-copy the skill tree, restart the gateway so
MCP children respawn, then verify: `--version`, `doctor --json` (ghidra checks), `hermes -p
<profile> mcp test <server>` (expect the new tool count), and one real `open_binary` +
`analyze_function` E2E with a worst-case TMPDIR. Tool count went 139 (6.0.0) → 170 (6.4.0).
Ghidra pin stayed `SUPPORTED_GHIDRA_VERSION=12.1.4` in 6.4.0; JDK 21 still accepted.

## Verify end-to-end through the MCP protocol

`hermes mcp test` proves *connection*, not correct env. Prove the config as Hermes would
spawn it (worst-case parent TMPDIR), then drive a real tool call:

```python
import json,subprocess,os
env=dict(os.environ); env["TMPDIR"]="/root/.hermes/cache/scratch"  # worst case
p=subprocess.Popen(["/usr/local/bin/rea-mcp"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                   stderr=subprocess.DEVNULL,text=True,bufsize=1,env=env)
def send(i,m,par=None):
    p.stdin.write(json.dumps({"jsonrpc":"2.0","id":i,"method":m,"params":par or {}})+"\n"); p.stdin.flush()
def wait(i):
    while True:
        d=json.loads(p.stdout.readline())
        if d.get("id")==i: return d
send(1,"initialize",{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"e2e","version":"1"}}); wait(1)
p.stdin.write(json.dumps({"jsonrpc":"2.0","method":"notifications/initialized"})+"\n"); p.stdin.flush()
send(3,"tools/call",{"name":"open_binary","arguments":{"path":SO,"provider_id":"ghidra"}}); wait(3)
send(4,"tools/call",{"name":"analyze_function","arguments":{"procedure":"JNI_OnLoad"}})
```

Note: `open_binary` requires `path`; `analyze_function` requires **`procedure`** (name or
address), not `address` (CLI uses `address`; MCP uses `procedure`). MCP arg names differ
from CLI arg names.

## Gateway-profile gotchas

- The MCP process is spawned by the long-running **gateway** (parent of every profile).
  `hermes mcp test` in a shell does NOT change the gateway's children.
- Hermes retries failed servers with a cooldown (`not attempted (in retry cooldown)`), and
  gateway child processes can survive config edits for a long time — a fix may only take
  effect at the next spawn. Bumping `connect_timeout` (default 60s; REA needs ~10s) makes
  spawns connect on the first try.
- Config changes auto-reload (`mcp.auto_reload_on_config_change`, default true), but the
  reload path itself can hang (`hermes mcp test` may time out) — run it in the background.
- `rea setup` **refuses to write anything if any detected client config is malformed**, e.g.
  a 0-byte `~/.gemini/config/mcp_config.json` -> whole transaction blocked. Clean those first.
- `rea mcp add --agent generic` needs the third-party `add-mcp` package and fails in
  unattended/offline setups; hand-register instead.

## Repairing an existing profile's REA registration

When a profile already has bare `rea: {command: rea, args: [mcp], enabled: true}` with no
engine env, the gateway may still log `registered 141 tool(s)` — that only proves the server
connected. Deep analysis on such a profile is inert because `rea doctor` reports
`hopper/ghidra/ida = missing_analysis_engine` and any `open_binary`/`analyze` dies with
`provider_unavailable`, or with the TMPDIR dot-path error once an engine is added.

Repair = same three edits (wrapper launcher -> config `command: /usr/local/bin/rea-mcp`
with no `args` -> official skill), then `hermes -p <profile> mcp test rea` (expect exit 0 and
the tool count of the installed REA version — 139 at 6.0.0, 170 at 6.4.0). Back up
`config.yaml` with `cp -a` first: `hermes config set` rewrites the whole section, so keep a
timestamped copy.

**Overwriting a pre-existing custom skill:** a profile may already carry a hand-written
`reverse-engineer-anything` stub (a few KB, official bundled skill is ~12.6 KB + 5
references). Copying the official one replaces it. Hermes' curator keeps a copy, so recover
it from `<profile>/.curator_backups/blobs/` — grep for a distinctive line from the stub —
and park it as `SKILL.md.<something>.bak` beside the official skill instead of deleting it.

## Gateway respawn timing

Config edits trigger a reload that spawns a fresh child process (observed: edits to profile A
can spawn children for profiles A and B). The chain for a wrapper-based entry is
`bash /usr/local/bin/rea-mcp` -> `node .../rea mcp`; the raw `node .../rea mcp` you see in
`ps` may be a pre-fix child from an earlier spawn, and a fix only takes effect at the next
spawn. Since the wrapper script `exec`s node, searching for the literal string `rea mcp`
still matches wrapper-spawned children. Killing the bash wrapper can orphan its node child —
prefer config-driven reloads over manual `kill`.
