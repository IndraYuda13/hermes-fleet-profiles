# REA analysis engines — inventory, setup, priorities

REA treats every engine as an independent provider. A missing engine never breaks the
others: doctor-audited engines (hopper, ghidra, ida, jadx) report
`missing_analysis_engine`; the PATH/env-resolved engines added in 6.5.0 (cutter, rizin,
frida, gdb, objdump) simply return `provider_unavailable` at call time when their
binary/package is absent.

## How each engine is resolved

| Engine | Resolution | Install | Notes |
|---|---|---|---|
| Ghidra | `GHIDRA_INSTALL_DIR` + full JDK 21+; doctor-verified against `SUPPORTED_GHIDRA_VERSION` in `dist/ghidra/GhidraInstallationPolicy.js` | extract the release to a big disk (~900 MB) | primary deep-static engine (headless `analyzeHeadless`) |
| Hopper | `HOPPER_LAUNCHER_PATH` or `rea setup` | paid, macOS | doctor-audited |
| IDA | `REA_IDA_MCP_CONFIG` (upstream IDA MCP registration JSON) | paid | doctor-audited |
| jadx | `REA_JADX_MCP_JAR` — absolute path to a caller-supplied jadx-headless-mcp 0.7.1 JAR | user supplies the JAR; REA never downloads it | dex -> Java; pairs with the apktool/adb toolset for Android work |
| GDB | `REA_GDB_COMMAND ?? "gdb"` from PATH | `apt install gdb` | REA supervises a GDB MI session (`--nx`, no target-exec commands) |
| objdump | argv built for `objdump` from PATH | binutils (present on stock Linux) | quick disassembly without standing up a Ghidra project |
| Rizin | `REA_RIZIN_COMMAND ?? "rizin"` from PATH | NOT in Ubuntu apt (`apt-cache policy rizin` is empty) — static tarball from GitHub releases (`rizin-vX-static-x86_64.tar.xz` -> /mnt/tools/rizin, ~900M unpacked); wrapper exports `REA_RIZIN_COMMAND` | radare2 successor; rz-pipe one-shot commands + debug sessions |
| Frida | dynamic `import("frida")` — the npm package, NOT the CLI and NOT a bundled dependency | `npm install frida` inside REA's isolated prefix | dynamic instrumentation; pairs with frida-server on the target (Android: push via adb, then connect with the frida remote-connection tool) |
| Cutter | TCP socket bridge to the Cutter desktop app | Cutter GUI install | needs a desktop session; near-zero value on a headless server |

## Worth-it ranking for this user (pentest + Android game modding + RE)

1. **Frida** — biggest capability jump: hook Java/native methods, bypass anti-cheat,
   trace crypto; the natural pairing with an adb-connected Android device. Install into
   the isolated prefix so the shared wrapper serves every profile.
2. **GDB + objdump** — usually already present on a Linux box; zero-cost native debugging
   and quick disassembly.
3. **Rizin** — apt-installable complement to Ghidra for fast CLI static analysis and
   scripting.
4. **Cutter** — skip on headless servers (GUI + socket bridge).
