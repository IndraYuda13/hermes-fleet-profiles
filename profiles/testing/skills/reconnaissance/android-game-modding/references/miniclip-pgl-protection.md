# Miniclip 8 Ball Pool protection & mod layering

Condensed notes from triage of an 8 Ball Pool Google-Play build (56.x line).
Use when a task needs to go deeper than mod sourcing: why the game cannot be
patched offline, or how to plan a custom mod.

## On-disk layout (stock Play build)

- `libgame-BPM-GooglePlay-Gold-Release-Module-<NNNN>.so` — the real game
  engine, **encrypted on disk**: entropy ≈ 8.0, no ELF magic, padded with byte
  `0x42` to a round size. E.g. arm64 file 85,561,152 B houses a ~19 MB blob;
  v7a 53,269,480 B houses ~16 MB. Two copies: `lib/<abi>/` plus a small stub
  under `assets/<rand1>/<rand2>/<abi>/`, whose real sizes are listed in
  `assets/<rand1>/<rand2>/k8f2….json` (a JSON map of blob sizes).
- `libloader.so` — plain ELF; decrypts the engine to the app data dir at
  runtime and `System.load`s it. Obfuscated dex helpers (e.g. `ykfld2.*`)
  call `System.loadLibrary("loader")`, kill the process on failure, and use
  native methods (JNI class e.g. `eafjZ1`) for string decryption
  (`zDL5e1.dxV9C9` XOR decode). Contains OpenSSL.
- PGL protection set: `libpglarmor.so`, `libbuffer_pgl.so`,
  `libfile_lock_pgl.so`, `libdatastore_shared_counter.so`; dex classes
  `com.pgl.ssdk.*`. Marker string `LIBLOADER_VERSION=` in the loader.
- Google Play PairIP ("deku"): `com.google.android.play.deku.*` classes,
  `gpdeku` parts, content provider `<pkg>.play.deku.contentprovider`.
- `assets/j1O1pP4…/<uuid>` blobs (header `e11cff10…`) — additional protected
  config payloads.

## Real mod layering (verified sample)

Mod = stock base version + additions; the stock engine blob and PGL libs stay
byte-identical:

- Two added `.so` files: `libsoimod.so` (~9 MB — the hook/feature engine) and
  `libgdtgos.so` (~7 MB, companion); armeabi-v7a libs stripped (arm64-only).
- Modified `classes.dex` / `classesXX.dex`: added obfuscated package `loQPY7`
  (unicode-named classes, XOR string tables).
- Manifest versionCode bumped to the newest public release although the code
  base is an older build (e.g. claims a 56.31.x identity while shipping
  `Module-3902` libs). The module number in the game lib filename is truth.
- Repacked and signed with the Android debug key.

Hook framework visible in strings: `Java_com_qiyi_xhook_NativeHandler_*`,
`A64HookFunctionV`, `MSHookFunction`, `A64_HOOK`; runtime logs
`ApplyInternalLinePatch: libmain or g_Vault not ready!`,
`Applying Internal Line Extension (Scrambled Vault)...`,
`Reverting Internal Line Extension...`, `Scanning...`.

Feature flags live as plaintext in the mod lib — enumerate with:

```bash
strings -a lib/libsoimod.so | grep -aE '^[bc][A-Z][A-Za-z_]+$|ESP_|AIM_|Prediction|Extension'
```

Known flags: `bESP_DrawPredictionLine`, `bESP_DrawPredictionPos`,
`bESP_BounceMarkers`, `bESP_InternalLineExtension`, `bAutoAim`,
`cAIM_SnapLine`, `cAIM_SnapLineBot`, `cESP_Line*`, `bPredictionAfterShot`;
power control log `Canceling power slider at power %f`.

## Signing / fingerprints

Miniclip app-signing cert SHA-1: `87615343657c0a98155d71ec5a3158218b9a9f62`
(same fingerprint as shown on the Play/APKPure listing). Compare
`apksigner verify --print-certs` against it to flag repacks.

## What this means for building a custom mod

- Offline decryption/patching of the encrypted engine blob is out of scope for
  a normal session; the production mods in the wild do not do it either.
- The realistic path: ship a hook library (xhook / A64 inline hook, or a
  Frida/LSPosed-based instrument) that patches the engine **in memory** after
  `libloader.so` decrypts it.
