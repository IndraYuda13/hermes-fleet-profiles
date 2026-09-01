# HCR2 native bootstrap and wrapped-asset triage

## Target
- Name: Hill Climb Racing 2
- Package: `com.fingersoft.hcr2`
- Version: `1.72.3` (`717`)
- Goal: find the first realistic mod lane with minimal blind patching.
- Scope / boundaries: wrapped gameplay assets, native bootstrap, integrity-adjacent startup path.

## Current Milestone
- The JNI bootstrap tail is now reinterpreted correctly at runtime shape level.
- `0x66de24(x19, [0x70d2d8], [0x712fd8])` is no longer treated as consuming a zero cell plus one opaque blob.
- After applying file-backed `R_AARCH64_RELATIVE` relocations offline, both arguments resolve into pointer-rich startup tables.

## Artifacts
- Checklist: `projects/hcr2-mod/RE-CHECKLIST.md`
- Boundary catalog: `projects/hcr2-mod/BOUNDARY-CATALOG.md`
- Runtime bootstrap probe: `projects/hcr2-mod/instrumentation/hcr2_bootstrap_probe_v1.js`
- Runtime asset/decode probe: `projects/hcr2-mod/instrumentation/hcr2_asset_probe_v1.js`
- First libcocos xref note: `projects/hcr2-mod/notes-libcocos-xref-2026-04-07.md`
- Offline reloc-aware dump helper: `projects/hcr2-mod/scripts/hcr2_runtime_relro_dump.py`
- Extracted native lib: `projects/hcr2-mod/extracted/libfingersoft_hcr2.so`

## Confirmed Findings
- Real Java bootstrap is closed:
  - `zvcgksddm/t.attachBaseContext()`
  - `zvcgksddm/F.c(app)`
  - `zvcgksddm/F.a(app)`
  - `zvcgksddm/F.c()` loads `libfingersoft_hcr2.so`
  - `zvcgksddm/F.d(app)` crosses into native `b(app)`
- `JNI_OnLoad` is pinned at `0x6e2e40`.
- Duplicated bootstrap blocks are pinned:
  - primary: `0x6e2f7c -> 0x6e2fa0`
  - fallback/retry: `0x6e3014 -> 0x6e3038`
- Exact duplicated call shape is pinned:
  - `x19 = 0x66dc3c(8)`
  - `0x652d94()`
  - `0x66de24(x19, [0x70d2d8], [0x712fd8])`
- `0x6e2fac` is allocator/retry-oriented glue, not gameplay logic:
  - calls `posix_memalign@LIBC` via `0x6e3f20`
  - retries through `0x652ba8`
  - then falls into the same duplicated bootstrap tail
- Relocation-aware runtime table truth is now pinned:
  - `0x70d2d8 <- 0x709a98`
  - `0x709a98 <- 0x709d40`
  - `0x712fd8 <- 0x652d4c`
  - `0x7110f8 <- 0x7254f0`
- `0x709a98`, `0x709a70`, `0x709b00`, and `0x709d40` form a linked RELRO descriptor family after reloc application.
- `0x712fd8` is a pointer table rooted at `0x652d4c` with linked BSS / RELRO cells such as `0x731cb8`, `0x731cd8`, `0x731f48`, `0x707ea8`, `0x707f28`, `0x707f78`, and `0x708048`.
- Table-entry addresses surfaced by that family, including `0x652d4c`, `0x652e44`, `0x652e9c`, `0x652ecc`, `0x652f6c`, `0x653168`, `0x6531e0`, `0x653258`, `0x6535d8`, `0x653c00`, and `0x654108`, currently have zero direct `bl` / `b` callsites in the executable segment.
- Wrapped gameplay assets remain real and selective:
  - `assets/Common/json/*` and `assets/Common/rube/*` are mostly wrapped with header `12 13 aa 12 13 ba 13 ba`
  - plaintext JSON still exists elsewhere, for example `assets/HD/textures/animations/character/Abduction.json`
- First headless `libcocos2dcpp.so` xref pass is now closed as a tooling/result boundary:
  - Python headless GhidraScript path failed here because headless was not started with PyGhidra
  - Java headless replacement worked and produced `projects/hcr2-mod/ghidra_xref_imports.out`
  - that output is still only a guardrail: raw external-symbol-address xrefs for `AAssetManager_open`, `AAsset_read`, and `AAsset_getLength` do not close caller flow yet, so the next static cut must be thunk-aware

## Not Yet Proven
- Exact semantics of `0x66dc3c`, `0x652d94`, and `0x66de24`
- Whether the `0x709a98` / `0x712fd8` family is registration, RTTI-like glue, constructor metadata, or another table-driven startup mechanism
- Exact wrapped-asset decoder path and whether it starts in `libcocos2dcpp.so`, `libfingersoft_hcr2.so`, or both

## Probes Run
- Capstone disassembly on `JNI_OnLoad` and its duplicated bootstrap blocks
- Direct branch-target scan across the executable segment for `b` / `bl` callsites
- Offline application of file-backed `R_AARCH64_RELATIVE` relocations to inspect runtime table shape
- Raw byte / linear disassembly checks around `0x66dc3c`, `0x652d4c`, and `0x66de24`

## Blockers
- Raw linear decoding of `0x66dc3c`, `0x652d4c`, and `0x66de24` is still not trustworthy enough to assign honest semantics.
- The wrapped gameplay/config lane is still unopened, so gameplay tunables are not yet mapped to a concrete decoder.

## Next Best Action
- Static lane: keep the cut narrow around the relocation-built descriptor family first, especially `0x709a98 -> 0x709d40` and `0x712fd8 -> 0x652d4c`, before over-naming `0x66dc3c`.
- Runtime lane: if a device window opens, run both probes together:
  - `hcr2_bootstrap_probe_v1.js` to capture the real contents and effects around `x19`, `0x709a98`, and `0x712fd8`
  - `hcr2_asset_probe_v1.js` to log `AAsset*`, `mz_uncompress` / `uncompress`, and `AppActivity.onJsonReceived`
- Wrapper lane: pivot the first decode triage to `libcocos2dcpp.so` asset-open/read plus `mz_inflate*` / `uncompress` callsites instead of returning to blind Java filename searches.

## Distilled Reusable Lesson
- On stripped native Android targets, raw file bytes in RW / RELRO startup cells can lie by omission. Apply `R_AARCH64_RELATIVE` relocations offline before calling those cells zero, empty, or blob-like.
