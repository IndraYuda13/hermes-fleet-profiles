# Tool Helpers

Use this file when optional specialized tooling may accelerate a reverse-engineering task.

## IDA Pro MCP

Repository:
- `https://github.com/mrexodia/ida-pro-mcp`

What it is:
- An MCP bridge for IDA Pro that exposes live IDB state and actions to an LLM-capable client.
- Useful for decompile/disasm lookup, xrefs, symbol browsing, rename/comment/type cleanup, and some debugger-assisted workflows.

When it helps:
- Large native binaries where live xref navigation matters.
- Ongoing IDA sessions where the operator already has an IDB open.
- Cases that benefit from structured function triage, annotation, or patch planning.

Prerequisites:
- IDA Pro 8.3+ required, with 9.x preferred.
- IDA Free is not supported.
- MCP-capable client integration is required.
- For headless `idalib-mcp` workflows, the operator also needs the relevant Hex-Rays/idalib setup.

Operational caveats:
- Treat helper output as advisory, not ground truth.
- Validate important claims with artifacts, traces, or controlled repro.
- LLMs can still hallucinate around byte/int conversions and obfuscated control flow.
- Obfuscated targets still need human-led prep work such as deobfuscation, string recovery, FLIRT/Lumina/library resolution, and anti-analysis awareness.
- Rename/comment/patch tools are powerful. Use them carefully and keep changes minimal-diff.

Recommendation:
- Mention `ida-pro-mcp` as an optional advanced accelerator in IDA-centric workflows.
- Do not make it a hard dependency of the skill.

## Ghidra: official automation-first path

Prefer this as the default open-source Ghidra path when no MCP integration is required.

Recommended stack:
- `analyzeHeadless`
- `PyGhidra`

Why this is the primary recommendation:
- official Ghidra-native automation path
- good for batch triage, scripted analysis, CI, and repeatable probes
- lower maintenance risk than unofficial bridge stacks

When it helps:
- batch-importing binaries or APK native libraries
- running pre/post scripts over many samples
- building repeatable artifact extraction or function triage steps
- headless environments where a GUI decompiler session is unnecessary

Notes:
- `Pyhidra` is historically relevant, but modern Ghidra direction favors `PyGhidra`.
- If you want the most stable long-term recommendation, prefer `analyzeHeadless + PyGhidra` over older Python bridge patterns.

## Ghidra MCP options

Use these when the operator wants a true MCP-capable Ghidra workflow rather than plain scripting.

### LaurieWired/GhidraMCP

Repository:
- `https://github.com/LaurieWired/GhidraMCP`

Use when:
- the operator already uses desktop Ghidra
- broad GUI-centric MCP support is desired
- decompilation, imports/exports listing, renaming, and general artifact navigation should be exposed to an agent

Recommendation:
- best default Ghidra MCP recommendation for normal GUI workflows

### clearbluejar/pyghidra-mcp

Repository:
- `https://github.com/clearbluejar/pyghidra-mcp`

Use when:
- the workflow is headless or automation-heavy
- Python-first orchestration is preferred
- CI-style or scripted project analysis matters more than GUI integration

Caveat:
- stronger Python/JVM plumbing than a simple extension install
- still better treated as an optional advanced path, not the base assumption

### symgraph/GhidrAssistMCP

Repository:
- `https://github.com/symgraph/GhidrAssistMCP`

Use when:
- richer MCP ergonomics, multi-window awareness, prompts, or a broader extension ecosystem is desired

Caveat:
- valid advanced option, but not the most universal default recommendation

### Other advanced options

Mention only as alternatives with stronger caveats:
- `cyberkaida/reverse-engineering-assistant` (ReVa)
- `13bm/GhidraMCP`
- `mrphrazer/ghidra-headless-mcp`

Do not present these as the canonical default unless the operator specifically wants their architecture or workflow.

## Ghidrathon

Repository:
- `https://github.com/mandiant/Ghidrathon`

What it is:
- a Python 3 scripting extension for Ghidra that replaces the old Jython-limited experience with a modern Python workflow

Use when:
- the operator wants to stay inside Ghidra but still use Python 3 libraries and scripts
- headless or in-UI scripting needs packages such as `angr`, `unicorn`, or other Python tooling

Caveat:
- more moving parts than plain `PyGhidra`
- best treated as a strong extension option, not the minimal default

## Remote bridge / external orchestration

### ghidra_bridge

Repository:
- `https://github.com/justfoxing/ghidra_bridge`

Use when:
- Ghidra runs separately, but an external Python process or agent needs to orchestrate analysis remotely
- a remote-object or proxy style workflow is acceptable

Caveat:
- practical and agent-friendly, but less official than the core Ghidra automation path
- maintenance and trust surface are larger than native scripting

## Open-source automation companions outside Ghidra

Use these when Ghidra is too heavy, too GUI-centric, or the task is better served by CLI-first or solver-heavy analysis.

### Rizin + rz-pipe

Repositories:
- `https://github.com/rizinorg/rizin`
- `https://github.com/rizinorg/rz-pipe`

Use when:
- fast headless triage matters
- JSON-friendly CLI automation is preferred
- you want lightweight xref/disasm/query loops without spinning up Ghidra

Recommendation:
- best open-source automation companion to mention alongside Ghidra

### radare2 + r2pipe

Repository:
- `https://github.com/radareorg/radare2-r2pipe`

Use when:
- mature remote/headless scripting is needed
- the operator already lives comfortably in the radare2 ecosystem

Caveat:
- powerful, but usually harsher ergonomically than Rizin

### angr

Repository:
- `https://github.com/angr/angr`

Use when:
- the task is better framed as programmatic reasoning, symbolic execution, CFG recovery, or path exploration
- decompiler UI is less important than solver-driven automation

Caveat:
- not a drop-in decompiler replacement for ordinary GUI-centric reversing

## Recommendation order

If only a small curated set should be referenced in this skill, prefer this order:
1. `Ghidra analyzeHeadless + PyGhidra` for official open-source automation
2. `LaurieWired/GhidraMCP` for GUI-centric Ghidra MCP
3. `clearbluejar/pyghidra-mcp` for headless/scripted Ghidra MCP
4. `Ghidrathon` for Python 3 inside Ghidra
5. `Rizin + rz-pipe` as the best lightweight automation companion

## Active VPS Tool Mapping for this skill

Use this section as the quick reality map of what is actually available on this VPS for reverse-engineering work.

| Tool | Status | Main use | Current notes / caveats |
|---|---|---|---|
| `jadx` | installed | Java decompile / flow mapping | good for APK logic reading, not for rebuild |
| `java` | installed | runtime for APK/RE tooling | usable now |
| `python3` | installed | scripts, blob analysis, helpers | primary glue layer |
| local `cloudscraper` venv | installed-local | Cloudflare-gated APK/page acquisition | available at `/root/.openclaw/workspace/.venvs/terabox-re`; useful when normal VPS requests to APKPure are blocked |
| `UnityPy` | installed | Unity asset / scene inspection and patching | now available via `python3`; useful for Unity `assets/bin/Data/*` triage and narrow scene/object edits before deeper IL2CPP work |
| `frida` Python module | installed-partial | future dynamic hook orchestration | client library exists, but no Android runtime/adb target yet |
| `Ghidra analyzeHeadless` | installed | native static analysis | validated earlier on this VPS |
| `PyGhidra` | installed | scripted Ghidra automation | validated earlier on this VPS |
| custom `Unidbg` harnesses | installed-local | controlled JNI/native execution | already productive for HTTP Custom case |
| `apktool` (distro) | installed-old | decode/rebuild APK + smali patching | Debian `2.5.0-dirty`; too old for some modern Play bundle rebuilds |
| `python-socks` / `imap_tools` | installed | SOCKS5-relayed IMAP client | used in grass_511 to access mailbox via SOCKS5 proxy to bypass spam filters |
| pinned `apktool_2.9.3.jar` | installed-local | primary modern patch-APK route | preferred default for current Android APK rebuild work |
| `aapt2` (distro) | installed-old | resource compile/link | `2.19-debian`; usable but not the preferred modern default |
| pinned Google `aapt2` | installed-local | newer resource compile/link | `2.20-14792394` at `tools/android-build/bin/aapt2` |
| `apksigner` | installed | sign rebuilt APKs | working for current non-root mod builds |
| `adb` | available-via-tunnel | device attach / install flow | works through reverse tunnel; current good path is `ADB_SERVER_SOCKET=tcp:[::1]:5037` |
| Android SDK / emulator | partial | dynamic Android runtime in VPS | x86_64 Android Studio AVD is a poor target for this ARM-only Eight Ball Pool build |
| `frida-tools` CLI | installed | `frida-ps`, attach UX | installed and usable from `~/.local/bin` |
| `qemu-user-static` | installed | foreign-arch user-mode triage | useful for probing ARM/Android-ish binaries, but not enough to make Android/Termux-only tools truly portable on this Ubuntu VPS |
| `willstore69/toolkit` / `aio-mod` | sandboxed-static-only | opaque APK patcher/mod helper candidate | latest public asset is ARM64 + Android/Termux-oriented; direct run and QEMU-assisted run on this x86_64 VPS both failed to produce a usable session |

## Patch-APK route recommendation for this VPS

For Android config-decrypt cases like HTTP Custom, prefer this order on the current VPS:
1. `jadx` for code reading and sink discovery
2. `apktool` for decode/smali patch/rebuild
3. `apksigner` for installable output
4. `Ghidra`/`Unidbg` only when Java/smali sink patching is insufficient
5. `Frida` only when an Android runtime target actually exists

### Smali-only rebuild fallback for modern APK resources

- If distro `aapt` fails during rebuild because modern resources use names like `$...xml`, do not assume the smali patch is wrong.
- When the intended change is dex/smali-only, prefer `apktool d -r` and rebuild the no-resource tree so original resources stay untouched.
- After that, `zipalign` and re-sign the full split set with one key before device install.

## General helper rules

- Prefer helpers that reduce repetitive navigation, not helpers that replace evidence.
- Record which helper contributed to a conclusion when that matters for reproducibility.
- If a helper is unavailable, fall back to the core TRACE workflow rather than blocking the investigation.
- Treat helper output as navigation aid, not final truth.
- Confirm important claims with artifacts, traces, xrefs, or controlled repro before promoting confidence.

## Install fallback: headless Ghidra stack on this VPS

Use this only when the Ghidra stack is actually needed and not already installed.

Known-good install shape on this Ubuntu 22.04 VPS:
- JDK: `openjdk-21-jdk-headless`
- Ghidra: official NSA release `12.0.4` under `/opt/ghidra/current`
- PyGhidra venv: `/opt/venvs/pyghidra`
- pyghidra-mcp venv: `/opt/venvs/pyghidra-mcp`
- project root: `/srv/ghidra/projects`

Minimal reminder flow:
1. check disk space first with `df -h`
2. if root is nearly full, clear only safe temp artifacts, especially under `/tmp`
3. install JDK 21
4. install official Ghidra release
5. smoke test `analyzeHeadless` with an existing project directory
6. install bundled/aligned `PyGhidra`
7. install `pyghidra-mcp` only after the base stack works

Practical environment variables:
```bash
export GHIDRA_INSTALL_DIR=/opt/ghidra/current
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
export PATH="$JAVA_HOME/bin:$GHIDRA_INSTALL_DIR/support:$PATH"
```

Headless smoke test reminder:
```bash
mkdir -p /tmp/ghproj
"$GHIDRA_INSTALL_DIR/support/analyzeHeadless" /tmp/ghproj testproj -import /bin/ls -overwrite
```

PyGhidra smoke test reminder:
```bash
. /opt/venvs/pyghidra/bin/activate
python - <<'PY'
import pyghidra
pyghidra.start(install_dir='/opt/ghidra/current')
print('PyGhidra OK')
PY
```

pyghidra-mcp smoke test reminder:
```bash
. /opt/venvs/pyghidra-mcp/bin/activate
export GHIDRA_INSTALL_DIR=/opt/ghidra/current
pyghidra-mcp --help
```
