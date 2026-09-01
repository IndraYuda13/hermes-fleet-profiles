# Eight Ball Pool Android initial triage

## Target
- Name: Eight Ball Pool
- Package: `com.miniclip.eightballpool`
- Version: `56.21.2` (`3935`)
- APK SHA256: `852458330ed9c4504d7b6e4b837ef713f52d2e21ac672fd9ebc40107d26df540`
- Goal: isolate the highest-leverage lane for a real-time shot-assist that is accurate on aim, power, spin, and trajectory.

## Proven facts
- The app is not Unity/IL2CPP, not React Native, and not Flutter.
- The dominant engine surface is native.
- The on-disk `libgame-BPM-GooglePlay-Gold-Release-Module-3935.so` is not a normal ELF. It is a packed/blob-style payload.
- The first real native choke point is `libloader.so`, which exports `JNI_OnLoad` and imports `inflate*`, `android_dlopen_ext`, `dlopen`, `dlsym`, `mprotect`, and `syscall`.
- The app has a strong explicit anti-cheat / telemetry surface through `com.miniclip.mcanybrain.Anybrain` and `libanybrainSDK.so`.
- Java shell boundaries are visible and useful even though gameplay logic is not:
  - `EightBallPoolActivity`
  - `EightBallPoolBaseActivity`
  - `com.miniclip.nativeJNI.cocojava`
  - `com.miniclip.input.InputManager`
  - `com.miniclip.network.HttpConnection`
  - `com.miniclip.network.JavaSocket`
  - `com.miniclip.events.EventsReceiver`
  - `com.miniclip.attest.PlayIntegrity*`
- Every touch is mirrored into Anybrain through `EightBallPoolBaseActivity.dispatchTouchEvent()` -> `Anybrain.handleTouchEvent(MotionEvent)`.
- `EventsReceiver` explicitly names detection classes such as `OverlayDetected`, `IllegalDisplayEvent`, `IllegalAccessibilityServiceEvent`, `HookFrameworkDetected`, `FridaDetected`, `MagiskManagerDetected`, `RootedDevice`, `ActiveADBDetected`, `DeveloperOptionsEnabled`, and `RuntimeBundleValidationViolation`.
- Unpacked assets are mostly presentation/UI surfaces.
- The best asset-side hit so far is `assets/unpack/CushionShotTutorial.json`, which exposes guide-render art names like `AimGuide_Line`, `AimGuide_LineEnd*`, `AimGuide_Circle`, `Cue`, ball nodes, and tutorial-space table geometry.
- Those assets help visual matching, not solver extraction.

## Not yet proven
- Exact aim / shot / spin / trajectory solver entry points inside the real native game code.
- Whether the live guide is only a limited consumer of richer local shot state.
- Exact gameplay socket/protocol fields for pre-release shot state.
- Exact native producer path for `OverlayDetected` and related security events.
- Whether a low-footprint off-device read-only helper can avoid the explicit overlay/accessibility detection surfaces.

## Security event ingress milestone
- `EightBallPoolActivity.onCreate(...)` registers `com.miniclip.events.EventsReceiver` for explicit security actions including `OverlayDetected`, `IllegalDisplayEvent`, `IllegalAccessibilityServiceEvent`, `HookFrameworkDetected`, `FridaDetected`, `FridaCustomDetected`, `MagiskManagerDetected`, `RootedDevice`, `ActiveADBDetected`, `DetectUnlockedBootloader`, `DeveloperOptionsEnabled`, `UnknownSourcesEnabled`, and `RuntimeBundleValidationViolation`.
- `EventsReceiver.onReceive(...)` -> `onEvent(...)` -> `Process(...)` -> `Send(...)` -> `sendBlobsNative(byte[], byte[])` is the Java ingress/forwarding chain.
- `EventsReceiver` queues blobs until native is loaded, then forwards them onto the main game thread.
- No Java-side producer for those broadcasts was found in the decoded shell, and no Java-only UI gate/dialog branch was found for them.
- Narrowest supported conclusion:
  - Java is a receiver/serializer bridge only.
  - Producer side is native or otherwise hidden.
  - Native gameplay/telemetry gating remains possible because the sink is native.
- Practical implication:
  - naive on-device overlay/accessibility/hook lanes are explicitly on the watched side of the boundary.
  - off-device helper lanes are materially safer from the currently proven detection surface.

## Dead / downgraded branches
- Do not treat unpacked assets as the real physics engine.
- Do not start from direct long-line patching as the first lane.
- Do not expect Java business logic for cue physics.
- Do not assume a normal ELF workflow on `libgame-BPM-...so`; the loader must be opened first.

## Current best boundaries
1. Java native-load wrapper -> `cocojava` -> obfuscated load wrapper -> `libloader.so`
2. `libloader.so::JNI_OnLoad` and its inflate/dlopen/mprotect chain
3. Anybrain match/input telemetry boundary
4. `EventsReceiver` producer chain for overlay/hook/root detections
5. `InputManager`, `HttpConnection`, and `JavaSocket` as bridge nodes into native gameplay and transport

## Loader-sequence milestone
- Exact Java-side call order is now pinned:
  - `EightBallPoolActivity.onCreate(...)`
  - `EightBallPoolBaseActivity.onCreate(...)`
  - `cocojava.onCreate(...)`
  - later `cocojava.firstRun()`
  - `cocojava.loadNativeLibrary()`
  - `cocojava$1.run()`
  - `pZhy61.dIjmp5(name)`
  - `i0E6i7.loadLibrary(name)`
- `i0E6i7.loadLibrary(name)` first tries `System.loadLibrary(name)`, then on `UnsatisfiedLinkError` falls back to a native helper path (`i8WqJ1.hRL1L2(...)`) that can return absolute paths for `System.load(...)`.
- No separate Java-side explicit `System.loadLibrary("pglarmor")` was found in the traced bootstrap path.
- Narrowest supported interpretation:
  - the protected loader wrapper chain, not the activity itself, is the first runtime instrumentation boundary.
  - if `pglarmor` is involved, it is likely downstream of the loader helper/native resolution path rather than a separate top-level Java bootstrap stage.

## Practical implication
- The cheapest promising assist lane is still read-only state extraction plus helper rendering.
- But a naive on-device floating overlay is already downgraded because overlay/accessibility/display abuse is explicitly in the detection taxonomy.
- Java bridge usage is now narrowed too:
  - `InputManager` is a thin native stub for generic mouse/wheel input.
  - `HttpConnection` and `JavaSocket` are useful traffic boundaries but appear mostly native-driven rather than exposing gameplay business state from Java.
  - they should be treated as future narrow trace hooks, not as a cheap Java-only shot-state extraction lane.
- The next useful work is to map:
  - how touches and match state are fed into Anybrain
  - how security events are produced and uploaded
  - how `libloader.so` materializes the real native game payload

## Off-device still-frame PoC v1 milestone
- Canonical geometry schema is now generated from tutorial assets:
  - `projects/eight-ball-pool/table_schema.json`
  - extractor: `projects/eight-ball-pool/scripts/extract_table_schema.py`
- Screenshot annotator contract is frozen:
  - `projects/eight-ball-pool/ANNOTATOR-CONTRACT.md`
- Geometry-only solver core is implemented:
  - `projects/eight-ball-pool/scripts/stillframe_solver_v1.py`
  - supports direct-pot and one-cushion mirrored-pocket candidate ranking from annotated table-space ball/cue geometry
- Manual annotation bridge is implemented:
  - `projects/eight-ball-pool/scripts/manual_annotator_runner_v1.py`
  - converts a lightweight manual label file into contract-compliant annotation JSON using table-corner homography
- Smoke-tested with synthetic fixture:
  - labels: `projects/eight-ball-pool/examples/manual_labels_synthetic_v1.json`
  - annotation output: `projects/eight-ball-pool/examples/annotation_from_manual_runner_synthetic_v1.json`
  - solver output: `projects/eight-ball-pool/examples/solution_from_manual_runner_synthetic_v1.json`
- Practical implication:
  - the off-device lane is no longer just planning; there is now executable v1 solver infrastructure ready for real-frame validation.

## Real-frame bootstrap validation milestone
- First real screenshot was accepted as a valid aiming-state bootstrap frame.
- Bootstrap artifacts:
  - labels: `projects/eight-ball-pool/examples/manual_labels_real_2026-04-05_s1.json`
  - annotation: `projects/eight-ball-pool/examples/annotation_real_2026-04-05_s1.json`
  - solver output: `projects/eight-ball-pool/examples/solution_real_2026-04-05_s1.json`
  - debug overlay: `projects/eight-ball-pool/examples/overlay_real_2026-04-05_s1.png`
- Practical result:
  - the off-device pipeline now works on a real frame, not just a synthetic fixture
  - current result quality is still bootstrap-dependent because table corners and ball centers were seeded from quick detections/manual correction, not a mature annotator
  - solver produced ranked direct and one-cushion candidates without needing any on-device hook lane
- Honest boundary:
  - this is proof of executable end-to-end flow on a real screenshot, not proof that the ranked top candidate is already reliable enough for live use

## Bootstrap auto-annotator milestone
- `projects/eight-ball-pool/scripts/bootstrap_auto_annotator_v1.py` now exists.
- Current scope:
  - dominant felt-region table bbox detection
  - Hough-circle bootstrap ball detection inside the table
  - cue-ball classification by low saturation / high value heuristic
  - cue-axis estimate from bright line segments near the cue ball
  - direct export into the frozen annotator contract format
- Honest current quality:
  - the script is a bootstrap helper, not a mature detector
  - it still needs tuning on clean raw aiming screenshots because noisy overlays can inflate false circle detections
- First concrete tuning win:
  - tighter Hough settings, candidate contrast scoring, border felt/blob filtering, and pocket-mouth rejection reduced a noisy overlay-based validation pass from 31 detections down to 12 while still preserving all 11 manually labeled real balls on the bootstrap frame
  - quantified by `evaluate_annotation_vs_manual.py`: 11/11 manual balls matched, 0 misses, 1 false positive, mean match error about 1.13 px, cue error about 1.41 px
- Practical implication:
  - the next leverage point is no longer writing more solver math first
  - it is improving the screenshot-to-annotation stage so the existing solver gets cleaner geometry

## Verifier-first correction + restored raw-frame batch
- Important correction: the older `examples/annotation_real_2026-04-05_s1.json` is a manual-seeded reference artifact, not a faithful saved output from the current auto-annotator.
- The old raw screenshot path referenced by that example no longer existed, so earlier quality claims were not replayable from surviving artifacts alone.
- On 2026-04-06, three new raw aiming screenshots were supplied and preserved under:
  - `projects/eight-ball-pool/frames/2026-04-06/raw/frame_01.jpg`
  - `projects/eight-ball-pool/frames/2026-04-06/raw/frame_02.jpg`
  - `projects/eight-ball-pool/frames/2026-04-06/raw/frame_03.jpg`
- The annotator was hardened before replay:
  - false-positive suppression before solver input
  - cue-ball ambiguity gate
  - rejected-candidate audit output
  - solver perception quality gate in `stillframe_solver_v1.py`
- Reproducible batch artifacts now exist under `projects/eight-ball-pool/frames/2026-04-06/auto/`.
- Current replayable batch results:
  - frame 01: annotation `ok`, `14` accepted, `0` rejected, solver `ok`
  - frame 02: annotation `ok`, `16` accepted, `0` rejected, solver `ok`
  - frame 03: annotation `ok`, `9` accepted, `3` rejected (`low_contrast`, `edge_near`), solver `ok`
- Honest boundary:
  - this now proves the off-device lane runs end-to-end on fresh real raw frames without manual seeding
  - it does **not** yet prove geometric accuracy, because these three fresh frames still lack manual-label evaluation
- Batch summary note:
  - `projects/eight-ball-pool/frames/2026-04-06/BATCH-SUMMARY.md`

## Fresh manual evaluation milestone
- Manual evaluation artifacts now exist under `projects/eight-ball-pool/frames/2026-04-06/manual/` and `projects/eight-ball-pool/frames/2026-04-06/eval/`.
- Important caveat: the current manual labels are **visual-assisted manual oracles**, not fully blind labels from scratch.
  - frame 01 labels were kept where the accepted detections were visually aligned on the raw frame
  - frame 03 labels kept the visually aligned accepted detections and added 2 visually real missed balls manually during the first evaluation pass
- Replayable evaluation summary:
  - `projects/eight-ball-pool/frames/2026-04-06/EVAL-SUMMARY.md`
- First evaluation pass pinned two concrete miss classes:
  1. top-left low-contrast real ball near `495,168`
  2. bottom-left edge-near real ball near `561,510`
- A narrow annotator recall patch was then applied:
  - low-contrast rescue for a constrained blue-white style profile
  - edge-near rescue for a constrained ball-like profile
- Current replayable results after that patch and one more evaluated frame:
  - frame 01: `14/14` matched, `0` misses, `0` false positives
  - frame 02: `16/16` matched, `0` misses, `0` false positives
  - frame 03: `11/11` matched, `0` misses, `0` false positives
  - one low-contrast junk candidate near `964,265` still remains correctly rejected on frame 03
- Solver ranking now emits a replayable `ranking_summary` block with margin-based ambiguity signals.
- First useful ranking lesson from the clean evaluated set:
  - frame 02 is a real ambiguity case under the current heuristic model
  - its top-2 candidates differ by only `2.168` score points, so the solver should treat it as low-margin rather than a strongly settled pick
- A first user-facing MVP runner now exists:
  - script: `projects/eight-ball-pool/scripts/helper_shot_once_v1.py`
  - usage note: `projects/eight-ball-pool/HOW-TO-USE-MVP.md`
  - output bundle: annotation JSON, solver JSON, recommendation overlay PNG, summary text, result JSON
  - ambiguous top-pick cases are surfaced to the user instead of being silently presented as confident
- Narrowest supported conclusion now:
  - the current evaluated regression set is clean across 3 frames
  - the next bottleneck is no longer the known recall misses
  - the next real question is candidate-ranking quality, especially low-margin cases like frame 02

## Mod-lane pivot milestone
- User explicitly deprioritized the screenshot-helper lane because it felt impractical for immediate use.
- Fastest evidence-backed mod pivot is **not** smali-only blind repack.
- Chosen path is now:
  - small runtime neutralizer and loader oracle first
  - then native patching against the materialized real game module
- First runtime mod-side deliverables now exist:
  - `projects/eight-ball-pool/instrumentation/ebp_mod_runtime_neutralizer_v1.js`
  - `projects/eight-ball-pool/MOD-RUNTIME-PIVOT-v1.md`
- Current neutralizer scope:
  - keep loader trace alive
  - cut `EventsReceiver.Send(EventBlob)` / `sendBlobsNative([B,[B)`
  - force `Anybrain.shouldRegisterTouches(false)` and short-circuit `handleTouchEvent(...)`
  - bypass `MCAttest.registerPlayIntegrity(long)`
  - drop `PlayIntegrityProviderNativeBridge` failure callbacks
- New emulator blocker lesson (Android Studio AVD, 2026-04-06):
  - current 8 Ball Pool build in workspace ships native libs only for `arm64-v8a` and `armeabi-v7a`
  - no `x86` or `x86_64` game libs are present in the APK artifacts
  - on the tested Android Studio x86_64 emulator, the app process can exist but only `base.odex` plus system loaders appear; `libloader.so`, `libanybrainSDK.so`, and the real gameplay payload never materialize
  - practical reading: Android Studio x86_64 AVD is currently a bad primary mod target for this build, and force-close on launch is likely ABI/emulator-path related before gameplay runtime comes alive
- Honest boundary:
  - this is the first mod-lane runtime front, not proof that the final gameplay patch target is already solved
  - the first real native gameplay patch still depends on runtime truth from a target where the loader-materialized module actually comes alive

## Non-root ARM64 phone milestone
- A real ARM64 phone path is now live and usable through reverse-tunneled ADB.
- Live phone package facts captured from the device:
  - package: `com.miniclip.eightballpool`
  - version: `56.21.1`
  - split layout: `base.apk` + `split_config.arm64_v8a.apk`
  - device ABI: `arm64-v8a`
- The first non-root modded build has been prepared from the live phone APKs:
  - base patched to load `libgadget.so` in `EightBallPoolApplication.<clinit>()`
  - `android:extractNativeLibs` forced to `true` in the modded base manifest so Gadget config can be found at runtime
  - Frida Gadget ARM64 injected into the arm64 split with listen port `27052`
- New repeatable artifacts:
  - build script: `projects/eight-ball-pool/scripts/build_nonroot_gadget_mod_v1.sh`
  - install script: `projects/eight-ball-pool/scripts/install_nonroot_gadget_mod_v1.sh`
  - install note: `projects/eight-ball-pool/INSTALL-NONROOT-v1.md`
- Important boundary:
  - because the modded APK is re-signed, it cannot replace the Play-signed original in-place
  - installation requires uninstalling the original app first

## Gadget install proof milestone
- The first non-root modded build was installed successfully on the real ARM64 phone after uninstalling the Play-signed original.
- Verified runtime proof from live `logcat`:
  - initial build: `Load ... /lib/arm64/libgadget.so ... : ok`
  - later stealth build: Gadget renamed and still reachable through port `27052`
- This proves the current repack lane is not just build-complete. The injected instrumentation runtime is actually loading on the phone.
- Runtime findings after live Gadget attach:
  - `libloader.so` is present
  - `libanybrainSDK.so` is present
  - the real gameplay/protection payload is materialized into a randomized executable file under app-private data, e.g. `/data/data/com.miniclip.eightballpool/.../7zxQz50kNKpov9xb3hXj33N45NRhDnL1ykE9lGlUd49eIdwCDN`
  - early Gadget builds and lighter Java sink patches were not enough; the app still died after a few seconds
  - during the observed early kill window, `AnybrainStart*` did not fire and no `kill/tgkill/abort/exit` path was observed through normal libc wrappers or exported `syscall`
- Important discriminator found later:
  - a **no-Gadget** build still died, proving the main startup kill was not just Frida/Gadget presence
- Breakthrough milestone:
  - after disabling ASUS game overlay influence and then sweeping remaining shell-side self-kill paths (`killProcess`, `System.exit`, `Runtime.halt`) across the decompiled base, a no-Gadget debug build kept `EightBallPoolActivity` alive for >30 seconds on the real phone
- Narrowest supported conclusion now:
  - the startup death was not a single one-line Java sink, but a combination of shell-side self-termination lanes plus environmental interference
  - the app can now be kept alive long enough to move from blind startup bypass into controlled next-stage instrumentation

## Next best action
- Treat the current stable no-Gadget build as the startup-safe baseline.
- Reintroduce observability carefully on top of that baseline, ideally with a less noisy/earlier instrumentation lane than the first listen-Gadget build.
- Then resume payload-side tracing and guide/physics target discovery from a stable app state.
- Keep the screenshot helper as fallback/oracle, not as the primary near-term lane.

## PC-hosted bridge re-proof (2026-04-06 04:45 WIB)
- Boskuu re-exposed the live phone through his Windows PC using reverse SSH to the VPS:
  - `ssh -N -T -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes -R 15037:127.0.0.1:5037 -R 27052:127.0.0.1:27052 -p 22109 root@85.209.163.218`
- Concrete proof from the VPS:
  - `adb -H 127.0.0.1 -P 15037 devices -l` detected the phone cleanly
  - tunneled ADB could read package paths for `com.miniclip.eightballpool`
  - tunneled ADB could launch the app and confirm `EightBallPoolActivity` was foreground
  - while the app was alive, `frida-ps -H 127.0.0.1:27052` enumerated `Gadget`
- Important interpretation:
  - this re-proves the transport chain itself is healthy end-to-end
  - if attach later fails with `connection closed`, do not blame the bridge first; re-check whether the app has already died
- Current narrow blocker after the re-proof:
  - an untimed remote attach attempt still hit `frida.TransportError: connection closed`
  - immediate ADB recheck showed the app process had already exited, so the remaining issue is the short runtime window, not basic PC/VPS/ADB setup
- Follow-up milestone from the same session:
  - relaunch + **fast attach to `Gadget` by name** from the VPS succeeded
  - the neutralizer script loaded and immediately proved these live surfaces again:
    - global `android_dlopen_ext`
    - global `dlopen`
    - `libloader.so`
    - `libanybrainSDK.so`
    - randomized executable payload materialization under app-private data
  - live export-hook setup succeeded for:
    - `AnybrainSetCredentials`
    - `AnybrainSetUserId`
    - `AnybrainSetPlayerToken`
    - `AnybrainSetTargetProcess`
    - `AnybrainSetTargetWindow`
    - `AnybrainStartSDK`
    - `AnybrainStartMatch`
  - the process stayed alive through the fast-attach capture window with PID `21237`
- Updated interpretation:
  - stable instrumentation is possible if launch and attach are timed tightly enough
  - the next leverage is keeping a timed attach alive while moving deeper into the app or into a real match, not reworking the PC/VPS bridge again
- New helper artifact from the same cycle:
  - `projects/eight-ball-pool/scripts/pc_bridge_fast_attach_neutralizer_v1.sh`
  - purpose: launch via tunneled ADB on `15037`, wait for `Gadget` on `27052`, then auto-attach the neutralizer with tight timing
  - first live run succeeded and re-confirmed the module/materialization set under process `23516`
- Observability upgrade after that:
  - additive script `projects/eight-ball-pool/instrumentation/ebp_mod_runtime_neutralizer_v2.js` now retries until Java becomes available and adds watch/suppress coverage for `Activity.finish*`, `moveTaskToBack`, `android.os.Process.killProcess`, `System.exit`, `Runtime.exit`, and `Runtime.halt`
  - the fast-attach helper now accepts `HOOK_JS=...` override, so v1/v2 hook packs can be swapped without changing the launcher itself
- Persistent attach breakthrough:
  - new script `projects/eight-ball-pool/scripts/pc_bridge_persistent_attach_v1.py` successfully performed launch -> wait Gadget -> attach -> keep-session-alive through the PC/VPS bridge
  - during the first persistent run, the script stayed alive long enough to capture a real lifecycle hit beyond loader setup: `AnybrainSetCredentials` with non-null credential values
- Updated interpretation after the persistent run:
  - the lane has now crossed from `early loader only` into `real Anybrain identity setup`
  - the new narrow target is to keep the app foregrounded long enough to capture the next Anybrain lifecycle calls (`SetUserId`, `SetPlayerToken`, `StartSDK`, `StartMatch`) and correlate those with the remaining forced-exit or task-background behavior
- Hard crash oracle discovered immediately after the next FC:
  - crash buffer now proves the current active lane can die by **native abort**, not just silent finish
  - repeated live shape:
    - thread: `MCRenderer`
    - signal: `SIGABRT`
    - uptime: about 4 seconds
    - stack core: `libc syscall/abort -> libcrashlytics-common.so -> libmcbridge.so -> libwebviewchromium.so -> libmcbridge.so -> abort`
  - events buffer confirms the downstream activity removal is simply the consequence of process death: `am_proc_died` then `wm_finish_activity ... proc died without state saved`
- Important discriminator this adds:
  - the **current Gadget lane** has a concrete renderer/WebView-linked abort surface involving `libmcbridge.so`
  - this is a different, more specific oracle than the older no-Gadget startup-kill behavior
- Updated next action:
  - split the problem into two lanes instead of mixing them:
    1. Gadget/renderer/WebView abort lane tied to `libmcbridge.so`
    2. older no-Gadget startup enforcement lane
  - prioritize the cheapest differentiator first: reduce or delay active Gadget interaction around the early renderer/WebView phase so we can see whether the abort is caused by Gadget presence/timing or by a deeper shared target path
- Differentiators completed right after that:
  - no-attach baseline on the same Gadget build survived past 8 seconds with `EightBallPoolActivity` still foreground and no crash buffer hit
  - early attach with only `noop_attach_v1.js` also survived past 8 seconds with no crash buffer hit
  - this proves the early `MCRenderer` `SIGABRT` is not just Gadget presence and not just attach/script-load alone
- New additive safe lane:
  - `projects/eight-ball-pool/instrumentation/ebp_anybrain_min_trace_v1.js`
  - scope reduced to Anybrain lifecycle exports only:
    - `AnybrainSetCredentials`
    - `AnybrainSetUserId`
    - `AnybrainSetPlayerToken`
    - `AnybrainSetTargetProcess`
    - `AnybrainSetTargetWindow`
    - `AnybrainStartSDK`
    - `AnybrainStartMatch`
  - under this minimal hook pack, the app avoided the earlier renderer `SIGABRT` and successfully logged `AnybrainSetCredentials` again with real non-null values
- Updated interpretation after these differentiators:
  - the heavy hook pack itself, or one of its aggressive hook families, is the trigger for the early renderer/WebView abort
  - minimal Anybrain-only tracing is currently the safest live lane because it crosses into real lifecycle setup without reproducing the earlier abort
  - the remaining unsolved lane is now the later soft proc-death path that still occurs even when the early renderer abort is avoided
- New milestone from the next live user run:
  - the app can now reach the **lobby/menu** before it closes itself
  - this upgrades the current state from `startup barely survives` to `startup survives long enough for real front-door UI`
- New late-exit oracle from that lobby-reaching run:
  - crash buffer remained empty
  - Android exit info still reports the app as `EXIT_SELF`
  - a lightweight watcher on common libc wrappers (`exit`, `_exit`, `quick_exit`, `abort`, `kill`, `tgkill`, `pthread_kill`) did not observe any of those wrappers firing before the process died
- Updated interpretation:
  - the remaining late self-exit likely uses a lower-level path than the common wrappers already watched, or another route that bypasses those specific hooks
- New next-step artifact:
  - `projects/eight-ball-pool/instrumentation/ebp_syscall_exit_watch_v1.js`
  - purpose: hook global `syscall` and filter the ARM64 numbers for `exit`, `exit_group`, `kill`, and `tgkill` so the next lobby-then-close event can be caught below the wrapper layer
