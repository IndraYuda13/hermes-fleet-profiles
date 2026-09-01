# HTTP Custom APK

## Target
- Name: HTTP Custom AIO Tunnel VPN 6.9.20-RC93
- Type: Android APK / config-protection reverse engineering
- Goal: Map config import/export flow and recover likely decrypt/encrypt path
- Scope / boundaries: static triage plus artifact-driven reasoning in workspace

## Current Milestone
- Native path mapped deeply enough to justify pivot toward patch-APK oracle workflow
- Live stock-app hook fallback prepared for the same oracle goal when APK repack or rebuild becomes brittle
- 2026-04-05: option-1 APK oracle artifact now exists as a signed minimal patch that dumps post-decrypt Java-side config strings before and after Gson validation

## Artifacts
- `downloads/HTTP-Custom-AIO-Tunnel-VPN_6.9.20-RC93_base.apk`
- `downloads/HTTP-Custom-AIO-Tunnel-VPN_6.9.20-RC93_apkcombo.apks`
- supplied config sample recovered as high-range text-wrapped payload
- `state/httpcustom_target_recovered_raw.bin`
- `state/httpcustom_probe/`
- `tmp/httpcustom-unidbg-harness/`

## Confirmed Findings
- Package: `xyz.easypro.httpcustom`
- Import path maps to `team.dev.epro.apkcustom.activities.ConfigImport.u(..., path)`
- Export/generate path maps to `team.dev.epro.apkcustom.activities.GeneratedConfig.v(String)`
- `.hc` is the primary config container; `.mr`, `.zxc`, and `.acm` are also accepted by the import activity
- Outer config sample behaved like UTF-8 text containing only high-range characters; recovered payload length `28616`, bytes restricted to `0x80..0xFE`, multiple of 8
- Decrypted plaintext is likely JSON because validators parse strings into `models.config.a` / `models.config.d`
- Protected/native-heavy stack includes `libf2c.so`, `libf2cvm.so`, `lib_eCrypt.so`, `libeCrypt.so`, and `libsysNative.so`
- `lib_eCrypt.so` JNI registrations were pinned for:
  - `load([B)[B`
  - `easyCrypt([B)[B`
  - `xrc(Ljava/lang/String;)Ljava/lang/String;`
  - `arrInt()[I`
- Working low-CPU Unidbg harnesses exist and can execute the real native JNI on this VPS

## Hypotheses In Play
- `libf2c.so` virtualizes protected activity methods and hands off sensitive config logic to `lib_eCrypt.so`
- `SystemNative.abc(...)` participates in string/config decode paths but is not yet proven as the final `.hc` decryptor
- `Crypt.load([B)[B` is still the strongest candidate oracle path for actual config transform, but its output finalization depends on helper state that the current harness does not fully preserve

## Probes Run
- APK triage, library inventory, string extraction, dex analysis, protected method mapping, sample-format recovery
- Ghidra JNI table recovery
- VM stub / selector mapping
- Unidbg black-box execution of `easyCrypt` and `load`
- working buffer dump from native flow
- finalizer-state narrowing probes

## Blockers
- Exact config algorithm and key schedule remain hidden in native/protected handlers
- Current harness can reach the real native path but final output collapses before Java-side byte-array return is materialized
- Patch-APK route is now preferable, but it still depends on on-device install/runtime execution to prove the dump oracle actually fires

## Next Best Action
- Two valid oracle lanes now exist:
  1. patch-APK route
     - decode APK/smali cleanly
     - patch the closest post-import / post-decrypt Java-side sink to dump payload/result to file
     - rebuild and sign APK
     - run patched APK on a real Android device only for execution, not for heavy RE
  2. stock-app live hook fallback
     - attach Frida to the unmodified app on-device
     - hook `ConfigImport.u(String)`, `Crypt.load([B)[B`, `Crypt.easyCrypt([B)[B`, `GeneratedConfig.v(String)`
     - keep JSON sinks armed at `org.json.JSONObject(String)`, `org.json.JSONArray(String)`, and `Gson.fromJson(String, ...)`
     - treat the first `HC_PLAINTEXT_ORACLE ...` console block or saved `/sdcard/Download/httpcustom_hook/*.txt` artifact as the success oracle for recovered readable config plaintext

## Distilled Reusable Lesson
- When native RE has already narrowed the bottleneck to a small finalizer but the app itself can still be repurposed as an oracle, pivoting to minimal patch-and-dump is often more efficient than continuing deep native lifting.
- Keep a stock-app runtime fallback ready too. If APK rebuild/signing becomes brittle, the narrowest practical dynamic boundary is usually the first validated JSON/string sink after the protected decrypt path, not the earlier obfuscated native wrapper.

## Update 2026-04-05 07:10 WIB - Option 1 Java-side Oracle Artifact

### Newly Confirmed Findings
- The cheapest mature plaintext sink is inside `b4/f.smali`, not inside the native VM wrapper.
- Two validator methods receive the post-decrypt Java string directly as `p0` immediately before Gson parsing into `models.config.a` and `models.config.d`.
- Existing earlier patch work already dumped parsed-object `toString()` output after successful validation.
- The stronger option-1 patch now also dumps the raw candidate plaintext string before Gson parse, which is a better oracle for partially valid or edge-case configs.

### Concrete Patch
- Working dir: `state/httpcustom_patch_a/`
- Reused source container from existing inbound signed artifact:
  - `/root/.openclaw/media/inbound/httpcustom_patched_signed---d4b2089b-a79c-468f-91a5-2a1863e7bdd0.zip`
- Decoded with apktool to:
  - `state/httpcustom_patch_a/apktool_decoded/`
- Patched file:
  - `state/httpcustom_patch_a/apktool_decoded/smali/b4/f.smali`
- New raw dump files added:
  - `decoded_config_a_raw.txt`
  - `decoded_config_d_raw.txt`
- Existing parsed dump files kept:
  - `decoded_config_a.json`
  - `decoded_config_d.json`
- Dump helper remains `b4/f.x(name, text)`.
- Lane-B path upgrade applied afterward:
  - first tries public folder `/sdcard/Download/httpcustom_dump/`
  - then still writes a backup copy under `App.v.getFilesDir()`
  - this keeps device-side retrieval easier without losing the older safe fallback

### Build / Artifact Result
- Full apktool rebuild failed on this VPS because `apktool 2.5.0-dirty` plus host `aapt` aborts on this target resource table with `First type is not attr!`.
- Narrow workaround succeeded:
  1. reassemble only `classes.dex` from smali with `org.jf.smali.Main`
  2. replace `classes.dex` inside the existing APK container
  3. re-sign with local debug keystore via `apksigner`
- Produced signed artifacts:
  - initial app-private dump build: `state/httpcustom_patch_a/httpcustom_option1_signed.apk`
  - easier-download variant: `state/httpcustom_patch_a/httpcustom_option1_download_signed.apk`

### Success Oracle Status
- Build/sign oracle: confirmed
  - `apksigner verify -v state/httpcustom_patch_a/httpcustom_option1_signed.apk` passed for v1, v2, and v3
- Runtime plaintext oracle: not yet confirmed
  - requires one real-device import run and retrieval of the dumped files
  - preferred retrieval path is now `/sdcard/Download/httpcustom_dump/`
  - backup path remains the app private files directory

### Exact Narrow Blocker
- The blocker is no longer sink location or APK signing.
- New concrete install blocker proved on 2026-04-05 after Boskuu tested Lane B:
  - the delivered patched artifact is still a **base-only** APK container
  - the manifest explicitly requires split companions via `android:requiredSplitTypes="base__abi,base__density"`
  - therefore Android can reject install even when no original app is present, because the package set is incomplete rather than merely signature-conflicting
- So the current blocker is split-aware packaging plus real-device runtime execution and extraction of the emitted dump files to confirm the oracle fires after import.

### Narrowest Next Move
- Rebuild Lane B as a **split-aware package set** using the original ABI+density companion splits, while only patching the base APK `classes.dex`.
- After that, deliver/install the full package set, import one `.hc` config, then check `/sdcard/Download/httpcustom_dump/` first.
- If the public dump path stays empty, fall back to checking the app files dir for the same filenames.
- Important Android 11+ packaging lesson proved on 2026-04-05:
  - a rebuilt split package can still fail install even after split completeness is fixed if **any installed split APK** that contains `resources.arsc` gets repacked with that entry compressed
  - the exact observed installer error was: `Targeting R+ (version 30 and above) requires the resources.arsc of installed APKs to be stored uncompressed and aligned on a 4-byte boundary`
  - the first partial fix corrected only the base split, but density and locale splits such as `config.xxhdpi.apk`, `config.xhdpi.apk`, and `config.en.apk` were still bad because their re-signed outputs had `resources.arsc` recompressed
  - the working fix is: for every split APK with `resources.arsc`, start from the original recovered split, `zipalign` it first, then sign it, while the modified base split must also preserve original entry compression modes before `zipalign` + signing
- Only after a split-aware package where all installed `resources.arsc` entries remain stored/uncompressed and aligned still fails should the anti-tamper / repack-sensitive explanation be promoted again as the primary blocker.
- Boskuu then confirmed a later `fixed2` Lane-B build could finally be installed and opened, but the app immediately force-closed at runtime.
- The first crash logcat then pinned the runtime boundary much tighter:
  - repeated warning before crash: `Failed to find entry 'classes.dex': Entry not found`
  - fatal error: `java.lang.UnsatisfiedLinkError: JNI_ERR returned from JNI_OnLoad in .../libeasypro.so`
  - crash site in Java side: `team.dev.epro.apkcustom.App.<clinit>` during `System.loadLibrary(...)`
- Interpretation tightened by that evidence:
  - install/packaging blocker is now effectively cleared for the tested arm64 bundle
  - the active blocker is specifically native startup integrity logic inside `libeasypro.so` `JNI_OnLoad`, not generic packaging anymore
  - the modded-dump code has not even become relevant yet, because the process dies during app bootstrap before the import path is reached
- Practical next move after this milestone is no longer packaging iteration first.
  - for fastest config readability, pivot back to the stock-app Frida oracle
  - only continue Lane B if the task explicitly shifts to bypassing `libeasypro.so` startup integrity / `JNI_OnLoad`

## Update 2026-04-05 08:15 WIB - Split-Aware Rebuild Attempt and Toolchain Blocker

### Newly Confirmed Findings
- The workspace still contains the patched Lane-B base artifact at `state/httpcustom_patch_a/httpcustom_option1_download_signed.apk`, and its manifest still advertises `android:requiredSplitTypes="base__abi,base__density"`.
- The originally cited split bundle artifacts are **not** present anymore in the live workspace or inbound media, despite being referenced earlier in the case note:
  - missing locally: `downloads/HTTP-Custom-AIO-Tunnel-VPN_6.9.20-RC93_apkcombo.apks`
  - missing locally: `downloads/HTTP-Custom-AIO-Tunnel-VPN_6.9.20-RC93_base.apk`
- Reacquisition attempts against public mirrors for the same version were blocked in this environment by anti-bot interstitials:
  - APKMirror page fetch returned HTTP 403 `Just a moment...`
  - APKPure page fetch returned HTTP 403 `Just a moment...`
  - browser tool was unavailable due gateway/browser timeout, so no manual browser-assisted recovery path existed from this session.
- A local XAPK with real ABI+density split companions was used only as a structural reference (`downloads/myxl/myXL_9.1.0_apkcombo.com.xapk`). That confirmed the companion split manifests need modern `android:splitTypes` values such as `base__abi` and `base__density`.
- The current host toolchain is insufficient to synthesize those modern split manifests cleanly:
  - host `aapt` can compile a basic split APK only when `android:splitTypes` is absent
  - host framework package `/usr/share/android-framework-res/framework-res.apk` is too old and fails on `android:splitTypes`
  - `apktool 2.5.0-dirty` can decode an existing split manifest carrying `splitTypes`, but its rebuild path falls back to raw-text manifest copy instead of recompiling that attribute correctly on this host
- Therefore the blocker is now precise: **without either the original split companions or a newer Android framework/build-tools set that can compile `android:splitTypes`, this VPS cannot produce a trustworthy split-aware HTTP Custom package set from scratch.**

### Artifacts Produced During This Attempt
- Structural reference extraction:
  - `state/httpcustom_patch_a/tmp_myxl/com.apps.MyXL.apk`
  - `state/httpcustom_patch_a/tmp_myxl/config.arm64_v8a.apk`
  - `state/httpcustom_patch_a/tmp_myxl/config.xxhdpi.apk`
- Failed scratch work kept for forensics:
  - `state/httpcustom_patch_a/split_build/`
  - `/tmp/myxl_abi_dec/`
  - `/tmp/myxl_dpi_dec/`
  - `/tmp/httpc_abi_dec/`
  - `/tmp/httpc_dpi_dec/`

### Exact Remaining Blocker
- Missing source split set and blocked reacquisition.
- Fallback synthetic-split build is also blocked because this host lacks a framework/build-tools combo new enough to compile split manifests with `android:splitTypes`.
- Browser-assisted mirror recovery is currently blocked in this environment when the OpenClaw browser tool cannot start: host browser startup timed out with a gateway/browser failure and explicitly warned that retries will keep failing until the gateway/browser path is repaired.

### Distilled Reusable Lesson
- For recent Play-style split APK targets, a base APK whose manifest declares `android:requiredSplitTypes` is not safely recoverable into an installable set with an old `aapt/framework-res` stack alone. Keep the original `.apks` or split companions, or keep a newer Android platform jar/build-tools ready before promising a split-aware rebuild.
- APKCombo can expose a directly downloadable signed Cloudflare R2 `.apks` URL inside the static `/download/apk` HTML. In this environment that path was recoverable with plain HTML fetch and `curl`, even while APKPure and APKMirror were blocked by anti-bot interstitials.

## Update 2026-04-05 08:36 WIB - Real Split-Aware Lane-B Package Set Built From Recovered `.apks`

### Newly Confirmed Findings
- The recovered exact split bundle is now locally present again:
  - `downloads/httpcustom-recover/HTTP-Custom-AIO-Tunnel-VPN_6.9.20-RC93_apkcombo.apks`
  - `downloads/httpcustom-recover/HTTP-Custom-AIO-Tunnel-VPN_6.9.20-RC93_base.apk`
- Extracting that bundle proved the install set is much larger than just ABI+density companions. The signed package set contains `56` APKs total:
  - base: `xyz.easypro.httpcustom.apk`
  - ABI: `config.arm64_v8a.apk`, `config.armeabi_v7a.apk`
  - density: `config.ldpi.apk`, `config.mdpi.apk`, `config.hdpi.apk`, `config.tvdpi.apk`, `config.xhdpi.apk`, `config.xxhdpi.apk`, `config.xxxhdpi.apk`
  - locale splits: `config.af.apk`, `config.ar.apk`, `config.az.apk`, `config.bg.apk`, `config.bn.apk`, `config.bs.apk`, `config.ca.apk`, `config.da.apk`, `config.de.apk`, `config.el.apk`, `config.en.apk`, `config.es.apk`, `config.et.apk`, `config.fa.apk`, `config.fi.apk`, `config.fr.apk`, `config.gu.apk`, `config.hi.apk`, `config.hu.apk`, `config.hy.apk`, `config.in.apk`, `config.it.apk`, `config.iw.apk`, `config.ja.apk`, `config.kn.apk`, `config.ko.apk`, `config.lo.apk`, `config.lv.apk`, `config.mr.apk`, `config.ms.apk`, `config.my.apk`, `config.nl.apk`, `config.pl.apk`, `config.pt.apk`, `config.ru.apk`, `config.sv.apk`, `config.sw.apk`, `config.ta.apk`, `config.te.apk`, `config.th.apk`, `config.tr.apk`, `config.uk.apk`, `config.ur.apk`, `config.uz.apk`, `config.vi.apk`, `config.zh.apk`
- Only the base split was modified. The already-patched dump-to-Download dex from `state/httpcustom_patch_a/classes_patched_download.dex` was transplanted into `xyz.easypro.httpcustom.apk`.
- Verifier-first proof of that transplant exists:
  - patched `classes.dex` SHA-256 inside the rebuilt base split: `6aa059a8edbb61ebb273a05b98f1f4de6e81860e1f5e6ace1915657fd622a703`
  - source patched dex SHA-256: `6aa059a8edbb61ebb273a05b98f1f4de6e81860e1f5e6ace1915657fd622a703`
  - result: exact match
- Every split APK in the package set was re-signed with one consistent key using the local debug keystore already used by the earlier Lane-B base artifact.
- Verification succeeded on representative splits after resigning:
  - base split `xyz.easypro.httpcustom.apk`: `apksigner verify -v` passed for v1, v2, v3
  - ABI split `config.arm64_v8a.apk`: `apksigner verify -v` passed for v1, v2, v3
  - density split `config.xxhdpi.apk`: `apksigner verify -v` passed for v1, v2, v3
- Deliverables produced under `state/httpcustom_patch_a/`:
  - grouped signed split set: `httpcustom_lane_b_signed_splits/`
  - repacked installer bundle: `HTTP-Custom-AIO-Tunnel-VPN_6.9.20-RC93_laneB_signed.apks`

### What is Proven vs Unproven
- Proven:
  - the recovered `.apks` was extracted successfully
  - the patched dump-to-Download logic is present in the rebuilt base split
  - the full 56-APK set is signed consistently and individually verifies
  - an installer-importable `.apks` bundle was repacked from that signed set
- Not yet proven:
  - on-device install acceptance by Android or third-party installers
  - on-device runtime execution of the plaintext dump oracle
  - creation of `decoded_config_*` outputs on a real device after importing a `.hc` file

### Distilled Reusable Lesson
- When the exact original split bundle is available, the narrow safe rebuild lane is: patch only the base split payload, leave companion split payloads intact, strip old signatures, then re-sign the **entire** split set with one key before repacking the `.apks`.
- For split-aware app-oracle mods, packaging completeness is no longer just `base + abi + density` in practice. Preserve the whole recovered split set unless you have a tested installer-specific minimization rule.

## Update 2026-03-30 00:56 WIB - Ghidra/PyGhidra JNI Mapping

### Newly Confirmed Findings
- `xyz.easypro.ecrypt.NativeUtil.<clinit>` loads `libf2c.so`.
- `ConfigImport.<clinit>` calls `NativeUtil.classesInit0(93)`.
- `GeneratedConfig.<clinit>` calls `NativeUtil.classesInit0(16)`.
- `SystemNative.<clinit>` calls `NativeUtil.classesInit0(90)` and then loads another obfuscated native library path consistent with `libsysNative.so`.
- `libf2c.so` is the concrete protection/JNI bridge for protected activity methods. It contains class/signature strings for `ConfigImport`, `GeneratedConfig`, and `methodRequiresReadWrite`, and exports `JNI_OnLoad` at `0x00000000000b3fb8`.
- `libf2cvm.so` appears to be a VM/helper dependency for `libf2c.so`, not the main JNI registration surface.
- `lib_eCrypt.so` is the concrete JNI registrar for `xyz/easypro/ecrypt/utils/Crypt`.
- Dumped JNI registration table from `lib_eCrypt.so` at `0x001f0038` mapped the following native methods:
  - `load([B)[B` -> `0x00128e80`
  - `easyCrypt([B)[B` -> `0x001216ec`
  - `xrc(Ljava/lang/String;)Ljava/lang/String;` -> `0x00125178`
  - `arrInt()[I` -> `0x00127960`
- `lib_eCrypt.so` `load([B)[B` references version/key-like string `eCrypt_v2.1.9_k3YJn1D3x`, which is strong evidence that `load()` participates in a keyed config transform path.
- `Crypt.a(String)` is Java-side glue: it hex-decodes input, calls native `easyCrypt([B)[B`, then builds a Java string from the output.
- `libsysNative.so` is the native backend for `team/dev/epro/apkcustom/widgets/SystemNative`; its `JNI_OnLoad` is at `0x001169a4` and it calls `sodium_init`, confirming a real crypto/anti-tamper native role.
- `SystemNative.abc(...)` belongs to `libsysNative.so`, but exact overload-to-address mapping is still not pinned.
- `cryptKey` and `checkReSetCryptKey` names seen in the APK belong to `com.tencent.mmkv.MMKV`, so they are not direct evidence of the main HTTP Custom easyCrypt config routine.

### Active Blockers
- Exact ARM64 handler addresses for `ConfigImport.u(...)`, `GeneratedConfig.v(String)`, and `ConfigImport.methodRequiresReadWrite()` are still not pinned from the stripped `libf2c.so` registration/dispatch table.
- `libeCrypt.so` and likely parts of `libsysNative.so` use obfuscated JNI registration data, so their method-name mapping needs another decoding pass.
- `lib_eCrypt.so` `easyCrypt([B)[B` (`0x001216ec`) is confirmed as the main entrypoint, but its internal algorithm is still heavily flattened/obfuscated.

### Refined Next Best Action
- Recover the exact `JNINativeMethod[]` / dispatch for `libf2c.so` to pin:
  - `ConfigImport.methodRequiresReadWrite`
  - `ConfigImport.u(L...;Ljava/lang/String;)V`
  - `GeneratedConfig.v(Ljava/lang/String;)V`
- Recover exact `SystemNative.abc(...)` overload mappings in `libsysNative.so`.
- Decode `libeCrypt.so` registration table around `0x0018e018`.
- Do backwards data-flow on `lib_eCrypt.so` `easyCrypt([B)[B` at `0x001216ec` and compare it against `load([B)[B` at `0x00128e80` to determine whether they share core primitives or represent separate keyed transforms.

### Distilled Reusable Lesson
- For stripped Android native libs protected behind `classesInit0(...)`, strong progress can still be made by combining Java `<clinit>` analysis with Ghidra JNI table recovery: first map which class IDs initialize which native surfaces, then dump `RegisterNatives` tables before trying to read the flattened crypto routine itself.

## Update 2026-03-30 01:28 WIB - Exact libf2c VM Entry Stubs

### Newly Confirmed Findings
- Exact arm64 `libf2c.so` registered native entrypoints for protected HTTP Custom methods are now pinned:
  - `ConfigImport.u(Lteam/dev/epro/apkcustom/activities/ConfigImport;Ljava/lang/String;)V` -> `0x00167fbc`
  - `GeneratedConfig.v(Ljava/lang/String;)V` -> `0x0013e804`
  - `ConfigImport.methodRequiresReadWrite()V` -> `0x00167c48`
- These are VM entry stubs, not the final business logic bodies.
- Stub-specific VM anchors recovered:
  - `ConfigImport.u(...)` -> `DAT_00212ab8`, selector `0x71`
  - `GeneratedConfig.v(String)` -> `DAT_001f9698`, selector `0x176`
  - `ConfigImport.methodRequiresReadWrite()` -> `DAT_002128fc`, selector `0x99`
- `GeneratedConfig` row also includes:
  - `w(ILjava/lang/String;)V -> 0x0013e9dc`
  - `u()V -> 0x0013eaf4`
- `ConfigImport` row also includes:
  - `w()V -> 0x00167bc4`
  - `v()V -> 0x00167f38`
- Conclusion: `libf2c.so` does not directly expose high-level config logic here; these methods are thin wrappers handing execution to `vmInterpret(...)` with per-method selector/VM blob data.

### Refined Blocker
- The real protected import/export behavior is now clearly behind VM program blobs rather than the JNI registration layer itself.
- The next bridge to recover is from those VM blobs/selectors into concrete backend calls touching `lib_eCrypt.so` or `libsysNative.so`.

### Refined Next Best Action
- Stay in low-CPU mode and trace only the three confirmed VM blobs/selectors:
  - `DAT_00212ab8` / `0x71`
  - `DAT_001f9698` / `0x176`
  - `DAT_002128fc` / `0x99`
- Goal: determine whether these paths invoke `easyCrypt/load` in `lib_eCrypt.so`, `SystemNative.abc(...)` in `libsysNative.so`, or both.

### Distilled Reusable Lesson
- When a protected JNI surface resolves to VM entry stubs, the key milestone is not just class/method registration but the exact selector + blob anchor passed into the VM. Once those are pinned, deeper tracing can stay narrow and CPU-light.

## Update 2026-03-30 01:40 WIB - Low-CPU VM Bridge Clarification

### Newly Confirmed Findings
- Low-cost evidence now shows the three pinned `libf2c.so` stubs do **not** directly bridge to `lib_eCrypt.so` or `libsysNative.so` at the ELF dependency/import layer.
- `libf2c.so` `DT_NEEDED` only includes:
  - `libf2cvm.so`
  - `liblog.so`
  - `libm.so`
  - `libdl.so`
  - `libc.so`
- The main unresolved/imported VM symbols exposed through `libf2c.so` are:
  - `vmInterpret`
  - `getCacheClass`
  - `cacheInitial`
  - `gVm`
- These bridge into the VM runtime path in `libf2cvm.so`, not directly into `lib_eCrypt.so` or `libsysNative.so`.
- `libsysNative.so` only exposes the expected `SystemNative` class surface.
- `lib_eCrypt.so` does not contain `ConfigImport` / `GeneratedConfig` method strings, which supports the conclusion that the current pinned import/export stubs first enter the VM runtime rather than directly invoking easyCrypt JNI exports.

### Refined Conclusion
- Current strongest model:
  - `ConfigImport.u(...)` / `GeneratedConfig.v(String)` -> `libf2c.so` thin stub -> `vmInterpret` in `libf2cvm.so`
  - any later use of `lib_eCrypt.so` / `libsysNative.so` would happen deeper inside VM-driven protected logic, not at the first native bridge edge.

### Refined Next Best Action
- Keep CPU-light and do a very narrow disassembly/instruction trace only around:
  - `0x00167fbc`
  - `0x0013e804`
  - `0x00167c48`
- Goal: prove the direct edge into `vmInterpret@plt` and capture minimal stub structure, then decide whether a deeper VM-program extraction is worth the CPU cost.

### Distilled Reusable Lesson
- For VM-protected Android native stubs, checking `DT_NEEDED` and unresolved/imported symbol edges can cheaply rule out false direct-bridge theories before spending heavy CPU on deeper decompilation.

## Update 2026-03-30 01:57 WIB - Exact vmInterpret Edge Proof

### Newly Confirmed Findings
- Exact instruction-level edge from the three pinned `libf2c.so` stubs to `vmInterpret@plt` is now proven.
- `vmInterpret@plt` is at `0x00136a20` in the image-base-adjusted address space used by the prior mappings.
- Minimal `vmInterpret@plt` thunk shape:
  - `adrp x16, #...`
  - `ldr  x17, [x16, #0xec8]`
  - `add  x16, x16, #0xec8`
  - `br   x17`
- Proven stub edges:
  - `ConfigImport.u(...)` at `0x00167fbc` loads blob `DAT_00212ab8`, stores selector `0x71`, then calls `bl #0x136a20`
  - `GeneratedConfig.v(String)` at `0x0013e804` loads blob `DAT_001f9698`, stores selector `0x176`, then calls `bl #0x136a20`
  - `ConfigImport.methodRequiresReadWrite()` at `0x00167c48` enters its real wrapper path, loads blob `DAT_002128fc`, stores selector `0x99`, then calls `bl #0x136a20`
- Two wrapper shapes are now supported by evidence:
  - direct stack-descriptor wrapper
  - alloc-backed frame/object wrapper followed by cleanup helper
- This conclusively proves the first execution bridge is:
  - protected JNI stub in `libf2c.so` -> `vmInterpret@plt` -> deeper VM runtime (`libf2cvm.so`)

### Refined Conclusion
- The earlier low-cost model is now confirmed at instruction level: the protected import/export methods first hand execution to the internal VM path, not directly to `lib_eCrypt.so` or `libsysNative.so`.
- Any later use of crypto/system helper libs must therefore occur deeper in VM-driven logic.

### Refined Next Best Action
- Stay CPU-light and inspect `libf2cvm.so` around `vmInterpret` only.
- Immediate goal: confirm how blob pointer and selector are consumed and pin the first fetch/decode of the VM program.

### Distilled Reusable Lesson
- When protected JNI wrappers are thin, proving the exact branch to the VM interpreter with a tiny disassembly slice can collapse uncertainty quickly without expensive full-program decompilation.

## Update 2026-03-30 02:13 WIB - Black-box JNI Emulation Milestone

### Newly Confirmed Findings
- Built a working low-CPU Unidbg harness under `/root/.openclaw/workspace/tmp/httpcustom-unidbg-harness` and successfully executed `lib_eCrypt.so` JNI on this VPS.
- `JNI_OnLoad` completed after stubbing the library's anti-Xposed/classloader probe.
- Confirmed live registration/execution surface for `xyz/easypro/ecrypt/utils/Crypt` methods inside emulation:
  - `load([B)[B`
  - `easyCrypt([B)[B`
  - `xrc(Ljava/lang/String;)Ljava/lang/String;`
  - `arrInt()[I`
- Real test against recovered config bytes (`state/httpcustom_target_recovered_raw.bin`) produced:
  - `easyCrypt([B)[B` executed and returned `28616` bytes
  - output was entirely zero bytes (`nonZero=0`)
  - saved temp artifact: `tmp/httpcustom-unidbg-harness/easyCrypt.out.bin`
- `load([B)[B` also reached JNI execution, but current Unidbg host shim aborted on a zero-length/null `SetByteArrayRegion` path, so final intended native output is not yet observed.

### Refined Conclusion
- Black-box JNI emulation is viable on this VPS and is a better continuation path than forcing deeper static VM lifting.
- `load([B)[B` remains the stronger candidate for the real keyed config transform path.
- The recovered raw blob is either not the exact expected direct input for `easyCrypt`, or `easyCrypt` requires context/preconditions and zero-fills on mismatch.

### Refined Next Best Action
- Keep Unidbg as the main path.
- Patch the harness/Unidbg JNI shim to tolerate `SetByteArrayRegion(len=0, buf=null)`, then rerun `load([B)[B` on the recovered config bytes.
- If `load()` still returns empty/null, try a very small set of adjacent candidate inputs from the same case chain, especially any pre-trimmed or hex-decoded material matching `Crypt.a(String)` expectations.

### Distilled Reusable Lesson
- Once JNI registration is mapped, black-box emulation can cut through VM-protected wrappers faster than continuing static VM analysis, especially on headless VPS environments where CPU must stay gentle.

## Update 2026-03-30 04:22 WIB - Direct ConfigImport Stub Attempt Blocker

### Newly Confirmed Findings
- Built two follow-up Unidbg probes to chase the real `ConfigImport` path instead of naively invoking `Crypt.load([B)[B`:
  - `tmp/httpcustom-unidbg-harness/ConfigImportPayloadProbe.java`
  - `tmp/httpcustom-unidbg-harness/ConfigImportDirectStubProbe.java`
- Standard Unidbg `callStaticJniMethod(..., "u(Lteam/dev/epro/apkcustom/activities/ConfigImport;Ljava/lang/String;)V")` failed exactly as expected with `find method failed`, confirming `ConfigImport.u(...)` is not exposed like an ordinary registered JNI method.
- Direct native-call attempt using the previously noted offset `libf2c.so + 0x00167fbc` also failed, but for a more important reason:
  - on the current local `armeabi-v7a` `libf2c.so`, that offset is not a valid in-file code offset at all
  - the resulting runtime address landed in `libf2cvm.so` instead (`0x123dbfc0`), where Unicorn stopped on an invalid instruction / wrong-mode branch sequence
- Additional hard evidence from the current artifact set:
  - local `libf2c.so` size is only `1279676` bytes (`0x1385bc`), so offsets like `0x00167fbc`, `0x00167c48`, and `0x0013e804` are outside the file and cannot be trusted as direct file offsets for this concrete library copy

### Refined Conclusion
- The high-level approach is still correct: the next useful step is to enter the real protected `ConfigImport` VM wrapper and keep `load/easyCrypt` hooks armed.
- But the specific stub offset values carried forward from earlier notes are not directly reusable against the local `libf2c.so` artifact now mounted in Unidbg.
- Therefore, the blocker is no longer calling convention alone; it is offset provenance / mapping correctness.

### Refined Next Best Action
- Re-pin `ConfigImport.u(...)` directly from the exact current `armeabi-v7a` `libf2c.so` and/or `libf2cvm.so` loaded in this workspace, then retry the direct native call only after confirming:
  - correct module (`libf2c.so` vs `libf2cvm.so`)
  - correct address basis (runtime VA vs file offset vs image-relative offset)
  - correct mode bit (ARM vs Thumb)
- Only after the stub is re-pinned from the current binary should the direct-call + `load/easyCrypt` dump plan be resumed.

### Distilled Reusable Lesson
- When carrying RE offsets between sessions or tools, always revalidate them against the exact binary currently mounted in the harness. A seemingly precise native offset can silently belong to a different image/basis and waste the whole probe if not checked against actual file size and module mapping first.

## Update 2026-03-30 04:50 WIB - Local Binary Repin Progress with Valid Wrapper Candidates

### Newly Confirmed Findings
- Installed lightweight helper stack on this VPS for local ELF repinning:
  - Python `lief`
  - Python `r2pipe` package
- `radare2` binary was not available from the current apt sources, but `lief + capstone` was enough to start extracting valid wrapper patterns from the exact local `armeabi-v7a/libf2c.so`.
- Confirmed local import edge for the VM bridge in the real binary:
  - `vmInterpret` PLT thunk resolves through `0x256e8`
  - `getCacheClass` / `cacheInitial` / `gVm` are also present in relocations as expected
- Critically, real wrapper candidates were recovered at valid in-file offsets from the current local binary, proving the earlier out-of-range offsets were from a different basis/image:
  - `0x2ac9c` with selector `0x176` (strongly consistent with prior `GeneratedConfig.v` memory)
  - `0x71098` with selector `0x110`
  - `0x71184` with selector `0xca2`
  - `0x71234` with selector `0xca2`
- Additional local candidates containing field/slot value `0x71` were identified while scanning around VM-wrapper patterns:
  - `0x4ff04`
  - `0x767d8`
- Important nuance from those `0x71` candidates:
  - the value `0x71` there is currently observed as a struct field byte (`strb.w r1, [r5, #0x71]`), not yet proven as the `ConfigImport.u` VM selector itself
  - one of them (`0x4ff04`) also writes selector-like stack value `0x17e`, which makes it unlikely to be the import-path target we want
- Therefore, the local repin is now on solid footing, but `ConfigImport.u(..., path)` is not yet conclusively bound to a single wrapper entry.

### Refined Conclusion
- The repinning phase is now genuinely productive: valid wrapper offsets from the current local `libf2c.so` have been recovered and correlated with VM bridge calls.
- However, the first local appearances of `0x71` are not yet enough to declare success, because they may be ordinary field offsets rather than the selector value previously associated with `ConfigImport.u`.
- The next task is semantic binding: determine which recovered wrapper is truly `ConfigImport.u`, then re-run the direct-call harness with the correct Thumb entry.

### Refined Next Best Action
- Continue the local scanner specifically for wrappers that:
  1. call `vmInterpret` via `0x256e8`
  2. prepare the helper frame for the downstream VM helper call (`0x256dc`)
  3. store the actual selector value for `ConfigImport.u` in the frame, not merely a field at offset `0x71`
- Once that exact wrapper is confirmed, invoke it in Unidbg using `entry | 1` for Thumb mode and keep the `load/easyCrypt` hooks armed to dump the mature payload.

### Distilled Reusable Lesson
- For stripped VM-wrapper libraries, matching a magic number alone is not enough. Distinguish carefully between a selector value written into the VM-call frame and a plain struct field offset that happens to share the same number.

## Update 2026-03-30 05:12 WIB - Selector Table Dump and Directed Unidbg Brute Force

### Newly Confirmed Findings
- Built a candidate-driven selector dump from the exact local `armeabi-v7a/libf2c.so` by collecting wrappers that:
  - call the VM path
  - store a selector into `[sp, #0xc]`
  - continue into the downstream VM helper call
- This produced a local selector table of 99 wrapper entries, including several validated/high-interest examples:
  - `0x6ae3c` -> selector `0x99` (strong positive control for `ConfigImport.methodRequiresReadWrite`)
  - `0x4ff04` -> selector `0x17e`
  - `0x767d8` -> selector `0x12`
  - `0x71184` / `0x71234` -> selector `0xca2`
- A `.data.rel.ro` table containing Thumb wrapper pointers was found for validated wrappers such as `0x6ae3d`, `0x2ac9d`, and `0x4ff05`.
- Important structural correction: the neighboring words in that table are not plain `JNINativeMethod` name/signature pointers. They behave like token/metadata indices, not direct plaintext string pointers, so the table is a custom VM method descriptor table rather than a standard JNI triplet array.
- Directed Unidbg brute-force was then run against nearby cluster candidates and later against higher-scoring `(this, String)`-looking wrappers:
  - tested: `0x6aee9`, `0x6b131`, `0x6e1c9`, `0x6e5b1`, `0x767d9`
- Result: none of those candidates reached `Crypt.load([B)[B]` or `easyCrypt([B)[B]` hooks.
- Failure shape was highly consistent and therefore informative:
  - several wrappers died on null dereferences such as `ldr r0, [r4]` or `ldr r1, [r0]`
  - this means the candidate wrapper expected a prebuilt internal context/frame/object graph, not just `(JNIEnv, dummy-this, jstring path)`
  - examples from logs:
    - `0x6aee9` and `0x6e1c9` collapse in the `0x897de` lane on `ldr r0, [r4]` with `r4 = 0`
    - `0x6b131`, `0x6e5b1`, and `0x767d9` collapse in the `0x88e7e` / `0x89574` lanes due to null pointer reads from frame slots like `[sp,#0x24]` / `[sp,#0x18]`

### Refined Conclusion
- Offset hunting is no longer the main blocker. We now have valid local wrapper offsets and a selector table from the correct binary.
- The current blocker is argument/context reconstruction: the likely import-path wrappers require internal VM/context state beyond the naive direct-call arguments.
- Therefore, simply calling neighboring wrappers with `(JNIEnv, jobject, jstring)` is insufficient even when the offset and Thumb bit are correct.

### Refined Next Best Action
- Shift focus from pure wrapper discovery to reconstructing the missing context/frame expected by the import-path wrapper.
- Practical next steps:
  1. identify which stack/object slots are null at the common crash sites (`[sp,#0x18]`, `[sp,#0x24]`, `r4`-backed context)
  2. trace where those slots would normally be initialized in the caller chain
  3. either emulate the proper caller stub or synthesize the minimal context object/frame before invoking the target wrapper
- Keep the `load/easyCrypt` hooks armed during future attempts, because the first successful context reconstruction should immediately reveal the mature payload.

### Distilled Reusable Lesson
- Once local wrapper offsets are known, the next hidden trap is often not the selector but the caller-prepared context. In VM-bridged native stubs, a correct function pointer plus wrong or incomplete frame state can fail just as hard as a wrong offset.

## Update 2026-04-05 10:35 WIB - v7 Early Native Watcher Refinement

### Facts from the real v6 run
- Real v6 output proved the Java import boundary only:
  - `[HCV6_JAVA] ConfigImport boundary hooks armed`
  - `[HCV6_REGNATIVES] hooking ...`
  - `[HCV6_READY] ...`
  - import-window saves for `ConfigImport.v_java` and `ConfigImport.u_java`
  - the real imported `.hc` path was captured
- Real v6 output did **not** show any of the following:
  - zero `[HCV6_REG]` lines
  - zero native enter/leave hits for `ConfigImport` or `Crypt`
  - dump folder contained only two `IMPORT_WINDOW` files
- The extracted artifact path for that proof set is:
  - `tmp/httpcustom_v6_real/hasil_v6.txt`
  - `tmp/httpcustom_v6_real/httpcustom_hook_v6/`

### Strongest evidence-backed reason v6 missed native events
- Fact:
  - in v6, `tryInstallRegisterNativesHook()` is called only from inside `Java.perform(...)`
  - the real run log shows `[HCV6_REGNATIVES] hooking ...` only **after** the app was already spawned/resumed far enough for Java hooks to arm
  - later manual import activity triggered only the Java import-window markers, with no registration callbacks afterward
- Inference:
  - the most likely missed boundary is startup-time native registration, not the later manual import path
  - in other words, the relevant `RegisterNatives` calls likely happened before v6 armed its watcher
- Secondary evidence, weaker than the timing point:
  - the delayed known-offset fallback also produced no hits, so ABI/module-name/offset mismatch remains possible, but v6's own code structure makes late watcher install the first thing to fix

### v7 change and rationale
- Added a new tracer:
  - `scripts/frida/httpcustom-live-plaintext-hook-v7.js`
  - `scripts/frida/httpcustom-live-plaintext-hook-v7.md`
- v7 arms these earlier than v6:
  - top-level `dlopen` / `android_dlopen_ext` hooks
  - top-level `RegisterNatives` scan for `libart.so`
  - re-scan/retry when `libart.so` is observed loading
- v7 also adds focused load markers for:
  - `libf2c.so`
  - `lib_eCrypt.so`
  - `libeCrypt.so`
- v7 keeps the proven `ConfigImport.u/v/w` Java import-window hooks intact so the real `.hc` path and import timing are still captured
- This is still a tracer, not a plaintext-recovery claim

### Exact expectation markers for v7
- earliest load proof:
  - `[HCV7_DLOPEN] ... libart.so`
  - `[HCV7_DLOPEN] ... libf2c.so`
  - `[HCV7_DLOPEN] ... lib_eCrypt.so` or `libeCrypt.so`
- registration proof:
  - `[HCV7_REGNATIVES] ...`
  - `[HCV7_REG] team.dev.epro.apkcustom.activities.ConfigImport::...`
  - `[HCV7_REG] xyz.easypro.ecrypt.utils.Crypt::...`
- native-intersection proof:
  - `HCV7_NATIVE_ATTACH`
  - `Crypt.load_enter/leave` or `Crypt.easyCrypt_enter/leave`

### Exact blocker if it remains after v7
- If v7 still shows target-library `DLOPEN` events but no `HCV7_REG`, the next blocker is no longer just watcher timing.
- Then the most likely remaining causes are:
  - wrong `RegisterNatives` symbol variant for this ART build
  - registrations happening through another uncovered path
  - ABI/build mismatch against the known fallback offsets or module naming

## Update 2026-04-05 10:xx WIB - v6 Native-Boundary Runtime Tracer Prepared

### Newly Confirmed Findings
- The latest user-provided v5 dump bundle is present at `downloads/hasil.zip` and was inspected as a blocker check, not as a new proof source.
- That bundle still supports the earlier conclusion that v5 reached the correct app class loader and saw helper/schema activity, but it still did **not** prove final imported config plaintext:
  - `hasil.txt` did not contain `HC_IMPORT_PATH`, `Crypt.load`, `ConfigImport`, or `HC_PLAINTEXT_ORACLE`
  - sampled saved captures under `httpcustom_hook_v5/` included helper outputs such as regex text and app status JSON-array strings, not proven final user config plaintext
- A stricter v6 Frida artifact was added to target the proven native/import boundary first instead of widening Java sinks again:
  - `scripts/frida/httpcustom-live-plaintext-hook-v6.js`
  - `scripts/frida/httpcustom-live-plaintext-hook-v6.md`

### What v6 Actually Does
- Uses only the already-proven Java boundary to arm the capture window:
  - `ConfigImport.u(ConfigImport, String)`
  - `ConfigImport.v()`
  - `ConfigImport.w()`
- Then tries to pin the real runtime native registration surface by intercepting `RegisterNatives` in `libart.so` and capturing fnPtr values for exactly these classes/methods:
  - `team.dev.epro.apkcustom.activities.ConfigImport::{u,v,w}`
  - `xyz.easypro.ecrypt.utils.Crypt::{load,easyCrypt,xrc}`
- After pointer capture, attaches native interceptors to those exact fnPtr values and dumps only during the import window or when output is already readable.
- Late-attach fallback is still narrow and evidence-backed only:
  - `lib_eCrypt.so` known offsets for `load/easyCrypt/xrc`
  - `libf2c.so` known offsets for `ConfigImport.u/v/w`

### What v6 Proves vs Does Not Yet Prove
- v6 can prove, on a real run, the actual runtime native function pointers registered for `ConfigImport` and `Crypt`.
- v6 can also prove whether `Crypt.load` or `Crypt.easyCrypt` is actually hit during the live import window.
- v6 does **not** yet prove final plaintext by itself until one device run shows readable config text in a `Crypt.*_leave` capture or saved dump.

### Narrowest Next Move
- Run v6 with `frida -U -f xyz.easypro.httpcustom -l scripts/frida/httpcustom-live-plaintext-hook-v6.js` so `RegisterNatives` observation is not missed.
- Import one `.hc` file.
- Judge success in this order:
  1. did `RegisterNatives` map the target pointers for this exact run
  2. did `Crypt.load` or `Crypt.easyCrypt` fire during the import window
  3. did any return buffer decode to readable config plaintext

### Distilled Reusable Lesson
- After a broad-but-correct class-loader hook proves the surface, the next iteration should shrink to runtime-registered native pointers plus the proven entry boundary that opens the relevant time window. This keeps noise low and upgrades evidence from "right class loader" to "right native function pointer on this exact run".

## Update 2026-04-05 07:xx WIB - Stock-App Frida Plaintext Oracle Fallback Prepared

### Newly Confirmed Findings
- A concrete live-hook fallback artifact was added at:
  - `scripts/frida/httpcustom-live-plaintext-hook.js`
  - usage notes: `scripts/frida/httpcustom-live-plaintext-hook.md`
- The runtime hook stays aligned with the already pinned boundaries from this case rather than restarting blind:
  - `team.dev.epro.apkcustom.activities.ConfigImport.u(String)`
  - `xyz.easypro.ecrypt.utils.Crypt.load([B)[B`
  - `xyz.easypro.ecrypt.utils.Crypt.easyCrypt([B)[B`
  - `team.dev.epro.apkcustom.activities.GeneratedConfig.v(String)`
- To avoid overcommitting to a single native edge, the hook also arms the first likely validated Java sinks:
  - `org.json.JSONObject(String)`
  - `org.json.JSONArray(String)`
  - `com.google.gson.Gson.fromJson(String, Class)`
  - `com.google.gson.Gson.fromJson(String, Type)`
- The explicit success oracle is now fixed for future sessions:
  - any `HC_PLAINTEXT_ORACLE ...` block showing readable JSON/config text in Frida output
  - or a saved capture under `/sdcard/Download/httpcustom_hook/*.txt`
- Important blocker note that should not be relearned:
  - the old local Unidbg temp dir was no longer present in workspace during this pass, and the HTTP Custom APK artifact was also not present under the current workspace `downloads/`; this does **not** block the Frida lane because it runs against the stock installed app on-device

### What is proven vs unproven
- Proven from prior case work:
  - package and import/export class names above are real and worth targeting
  - decrypted mature data is likely JSON/string before model parsing
- Not yet proven in a live device run:
  - which of `Crypt.load`, `GeneratedConfig.v`, or the JSON/Gson sinks will fire first with human-readable plaintext on the stock app build actually installed on-device

### Refined Next Best Action
- Run exactly one on-device Frida import attempt against the stock app with `httpcustom-live-plaintext-hook.js` armed.
- If no `HC_PLAINTEXT_ORACLE ...` block appears, only then fall back to the patch-APK lane or widen the sink net one step deeper into model constructors.

### Distilled Reusable Lesson
- For this target, the most practical live fallback boundary is not the VM-protected native stub itself. It is the first readable post-decrypt Java sink with a stack trace anchored in `ConfigImport` / `GeneratedConfig`.

## Update 2026-03-30 06:45 WIB - Deep Native Bottleneck Mapped and Patch-APK Pivot Prepared

### Newly Confirmed Findings
- `Crypt.load([B)[B` reaches the real native flow in Unidbg and progresses far beyond a stub/no-op path.
- The native path allocates/uses two important working regions:
  - `0x12212000` as the primary working blob buffer
  - `0x12219000` as metadata/helper region containing marker `eCrypt_v2.1.9_k3`
- The dumped `0x12212000` blob is not plaintext or common compression output:
  - size `16384`
  - very high entropy
  - no ZIP/GZIP/ZLIB/XZ/BZIP2 magic
  - not obvious JSON/plaintext
- Final-stage tracing narrowed the failure to an inline finalizer block around `0x2cd20..0x2cd70` in the active native flow.
- Immediately before that finalizer, sentinel-like state `0xee9200d1` zeroes slot `[r7-0x80]`, which previously held helper pointer `0x12219000`.
- After helper-slot zeroing, the finalizer collapses to zeroed output state and JNI returns fail as:
  - `NewByteArray(305070600)`
  - `SetByteArrayRegion(..., null)`
- This is now the narrowest native bottleneck: helper metadata appears to be invalidated too early for the final copy-back/output materialization to succeed in the current harness.
- Strategic pivot was justified: rather than spending unbounded time lifting the final native state machine, a patch-APK oracle workflow became the more practical next lane.
- VPS environment status for that pivot was also mapped:
  - `apktool` installed
  - `apksigner` installed
  - Frida Python module available but no Android runtime target / `adb` yet

### What is now likely not worth redoing blindly
- Repeating naive direct `ConfigImport.u(...)` wrapper calls with only `(JNIEnv, jobject, jstring)`
- Repeating shallow branch-force patches at the end of the finalizer without restoring missing helper state/context
- Treating `easyCrypt([B)[B` zero-filled output as if it were the main successful decrypt path

### Refined Next Best Action
- Use `jadx` + `apktool` to identify and patch the nearest post-import / post-decrypt Java-side sink so the app can dump the mature payload/config to file during normal execution on a real Android device.

### Distilled Reusable Lesson
- Once native RE proves the real path and narrows failure to a late-stage state collapse, switching to app-driven oracle patching can preserve all prior learning while avoiding diminishing returns from deeper native lifting.
