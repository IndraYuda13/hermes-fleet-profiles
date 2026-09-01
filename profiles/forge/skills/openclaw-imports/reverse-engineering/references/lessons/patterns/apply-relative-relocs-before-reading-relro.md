# Apply relative relocations before reading RELRO startup cells

## Pattern
On stripped native Android libraries, RW / RELRO startup cells can look empty or misleading on disk because the loader populates them through `R_AARCH64_RELATIVE` relocations at runtime.

## Better first move
Before concluding that a startup cell is just zeroed memory or an opaque seed blob:
1. inspect dynamic relocations with `readelf -rW --use-dynamic`
2. reconstruct file-backed `R_AARCH64_RELATIVE` writes offline when possible
3. then re-read the target tables in their relocation-applied shape

## Why
- bootstrap helpers often load pointer tables from RELRO, not from plaintext constants
- raw file bytes can hide the real graph of descriptor objects, vtable-like tables, and BSS anchors
- a wrong zero/blob interpretation can send the next RE cycle into the wrong helper entirely

## Practical guardrails
- only rewrite file-backed addresses when reconstructing offline
- keep imported `JUMP_SLOT` / `GLOB_DAT` entries separate from resolvable `RELATIVE` entries
- treat semantics as open until the relocated tables are tied back to real callers, callbacks, or runtime traces

## Applied example
- `Hill Climb Racing 2` `com.fingersoft.hcr2` `1.72.3`
  - raw view around `0x70d2d8` / `0x712fd8` looked like empty or blob-like cells
  - relocation-applied view showed `0x70d2d8 -> 0x709a98 -> 0x709d40` and `0x712fd8 -> 0x652d4c` as pointer-rich startup tables consumed by the JNI bootstrap tail
