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

## Runtime threads & burners (measure before attributing)

Measured on-device while diagnosing freezes on this title — useful anchors and
what they mean:

- `angousana` — log tag of the hook lib's scanner: `Searching 8BP base until
  found...`, then `Library found! Base: 0x…, Size: 80863232` (the 80 MB value
  = engine blob), then `__INPUT__` when the touch hooks install. A stuck
  session repeats `Found matching path but invalid ELF header at 0x… (bytes:
  76 64 65 78)` (= `"vdex"`) about once per second: the finder picked a
  `.vdex` mapping over the engine and retries forever — a 1 s-sleep loop, not
  a spin, but it leaves the mod inactive.
- Touch hooks: the hook lib intercepts
  `Java_com_miniclip_input_MCInput_nativeTouchesBegin/Move/End` (xhook). Its
  branches can `ret` without forwarding while state flags clear only on the
  END path — a stuck flag swallows every later touch: screen still animates,
  taps dead, sometimes no ANR (event was consumed, not delayed).
- `ResponseTimeMon` — the game's ANR supervisor
  (`com.miniclip.eightballpool.rtm.ResponseTimeMonitor`, started from both
  Application and Activity). Config call shape `create(3750, 0, 250, 1)`:
  the second argument is the check interval and `0` means `Thread.sleep(0)` —
  a flood loop that posts to the main thread and self-kills
  (`Runtime.halt(0)` / `killProcess`) when its timing check trips. The class
  exists in BOTH official and mod builds; only a per-thread measurement says
  whether it is burning CPU in the session in front of you.
- `AppLovinSdk:sha` — ads-SDK anti-hook scan calling
  `Thread.getAllStackTraces()` (suspends every thread in turn). Cost scales
  with thread count; on a 300+ thread game process it can dominate a core.
- `MCRenderer` / `RenderThread` / `DefaultDispatch` — render + SDK dispatch;
  normally the top consumers of a healthy session (sanity baseline).

## Signing / fingerprints

Miniclip app-signing cert SHA-1: `87615343657c0a98155d71ec5a3158218b9a9f62`
(same fingerprint as shown on the Play/APKPure listing). Compare
`apksigner verify --print-certs` against it to flag repacks.

## Re-sign kill switch (in-app anti-tamper)

A re-signed copy of the stock build — zero code changes — is killed by the
app's own anti-tamper SDK shortly after launch: a small in-app toast, then
self-kill about 10 s in. Device fingerprint: exit-info shows `reason=2
(SIGNALED)` `status=9` (SIGKILL) with NO `am_kill` from system_server — a
self-kill, not a system kill. The popup text is runtime-decrypted (not
plaintext anywhere in the APK); users paraphrase it, and the pattern matches
a commercial SDK ("Appdome fusion" vendor strings sit in the main dexes;
"REF: xxxx Security Threat Detected by App" is the same SDK family as
reported on other apps).

Smali shape to look for: a `Toast` subclass (`extends android.widget.Toast`)
shown from a native-integrity callback, then `Handler.postDelayed(...,
4000)` → `Process.killProcess(myPid)`. The official loader keeps
`antamp_integrity_main_run` and related integrity helpers; the third-party
mod loader does NOT carry them — that is why mod bases survive where a plain
re-sign of the official APK does not.

Consequences:
- "Official base + re-sign" is not a deliverable for this title — it dies on
  first run; bin-patching it also stays killed until the integrity path
  itself is neutralized.
- If the user wants the newer official engine, the work is porting features
  onto the surviving mod base rather than fighting the kill switch.

## What this means for building a custom mod

- Offline decryption/patching of the encrypted engine blob is out of scope for
  a normal session; the production mods in the wild do not do it either.
- The realistic path: ship a hook library (xhook / A64 inline hook, or a
  Frida/LSPosed-based instrument) that patches the engine **in memory** after
  `libloader.so` decrypts it.
