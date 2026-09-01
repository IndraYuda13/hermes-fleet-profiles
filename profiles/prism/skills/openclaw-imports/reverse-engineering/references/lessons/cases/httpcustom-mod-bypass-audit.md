# HTTP Custom Mod Bypass Audit

## Scope
- Target mod APK: `downloads/Apkmodnya.zip` -> `HC MOD v5.11.29 Unlock Config (1).apk`
- Main compare target available locally: `downloads/HTTP-Custom-AIO-Tunnel-VPN_6.9.20-RC93_base.apk`
- Important caveat: compare is cross-version (`5.11.29-RC90` mod line vs `6.9.20-RC93` stock line), so not every diff is pure mod logic. The reusable bypass architecture is still clear.

## Why this matters
The earlier patch-and-reinstall lane on the newer HTTP Custom target kept failing because the app line appears highly sensitive to re-sign/repack at runtime. This working mod APK provides a more realistic blueprint: instead of patching business logic only, it wraps startup/runtime and restores the original app chain safely.

## High-confidence findings

### 1. The mod inserts a startup shell, not just parser tweaks
Manifest-level change shows the mod does not start the stock app directly.

- Stock-style startup:
  - `android:name="team.dev.epro.apkcustom.App"`
  - `android:appComponentFactory="androidx.core.app.CoreComponentFactory"`
- Mod startup:
  - `android:name="fancybypass.component.FancyApplication"`
  - `android:appComponentFactory="fancybypass.component.FancyAppFactory"`

This is the first big lesson: the mod wins by owning startup/runtime first, not by simply editing `ConfigImport` or `GeneratedConfig`.

### 2. The shell still remembers and restores the original app chain
`FancyData` acts as an anchor table for the real/original components.

Observed responsibilities:
- return original `CoreComponentFactory`
- return original `team.dev.epro.apkcustom.App`
- instantiate both original components when needed

Reusable lesson:
- keep original component references in one explicit data/anchor class
- let shell code restore/delegate instead of hardcoding everything across many classes

### 3. `FancyApplication` and `FancyAppFactory` do runtime surgery
The shell does not stay passive. It reflects into Android internals and rewires runtime metadata.

Observed targets include:
- `ActivityThread`
- `LoadedApk`
- `ApplicationInfo`
- `ContextWrapper`
- application/factory references

What this strongly implies:
- it changes startup wiring at runtime
- it fixes/restores app identity after shell entry
- it keeps framework state consistent enough for the original app to continue running under a modified package

Reusable lesson:
- for repack-sensitive Android apps, startup shell + runtime rewrite can matter more than patching downstream logic

## Main bypass framework components

### `d` = runtime/package context manager
Observed role:
- acquires and caches access to `ActivityThread`, `LoadedApk`, `ApplicationInfo`, `IPackageManager`, `PackageInfo`
- serves as a centralized context/intelligence layer for the bypass

Reusable lesson:
- use a single runtime manager instead of scattering reflection logic across many unrelated classes

### `w` = runtime spoof profile
Observed fields:
- strings
- `Signature[]`
- `SigningInfo`
- booleans / flags

Observed use:
- passed into rewrite methods in `y`
- acts as the final packaged metadata used to spoof runtime/package state

Reusable lesson:
- build one final spoof profile object and let all rewrite logic consume that object

### `x` = builder for `w`
Pinned key method:
- `x.a(String, String, String, fancybypass.component.a, int)`

High-confidence role:
- builds `w` from strings, parsed package/signing metadata, and mode flags
- centralizes transformation from parsed metadata into runtime spoof state

## Identity / signing reconstruction pipeline

### `l` = raw transport object
`l.b(InputStream)` uses `ObjectInputStream` and reads:
1. `String`
2. `String`
3. `String`
4. `[[B`
5. `int`

This means the transport format itself is surprisingly simple: a serialized Java object carrying strings, byte-array arrays, and a mode integer.

Reusable lesson:
- the expensive part is often not the wire format itself but the way it is used in the larger bypass pipeline

### `a` = parsed Android-aware identity object
`a(InputStream)` parses transport/signing material into an object that carries:
- strings
- `Signature[]`
- `SigningInfo`
- flags

Confirmed chain:
- `InputStream` -> `l` -> `a`

Reusable lesson:
- separate raw transport parsing from Android-aware identity reconstruction

### `A` = per-entry descriptor object
Observed fields include:
- name/id string
- several size/offset/timestamp-like longs
- `[B` blob
- boolean flag
- `A.h = fancybypass.component.a`

High-confidence role:
- descriptor for a container/payload entry
- stores both raw entry metadata and parsed identity object

Reusable lesson:
- do not operate directly on raw `ZipEntry` metadata forever; promote it into a rich descriptor object first

## Runtime rewrite engine

### `y` = rewrite engine
Pinned responsibilities:
- `y.i(ApplicationInfo, w)` rewrites application metadata such as `name`, `sourceDir`, `publicSourceDir`, `className`
- `y.l(LoadedApk, ..., w)` rewrites `LoadedApk` and keeps its `ApplicationInfo` synchronized
- `y.m(PackageInfo, w)` rewrites package-level identity, including `Signature[]` and `SigningInfo`
- other methods touch component arrays as well

This is one of the most expensive lessons from the audit:
- a stable bypass rewrites `PackageInfo`, `ApplicationInfo`, and `LoadedApk` together
- patching only one layer is often too shallow and leads to inconsistency/crashes

## Dex injection / classloader lane

### `q` = dex injector
Observed role:
- inject dex payload into `BaseDexClassLoader`
- Android 29+ path uses `sharedLibraryLoaders`
- older Android path touches `dexElements`

### `p` = custom `ClassLoader`
Observed role:
- wraps parent classloader + `DexFile[]`
- loads classes from injected dex payloads

### `Y` = classloader/runtime surgery helper
Observed role:
- participates in `BaseDexClassLoader` / path/resources adjustment
- likely makes class loading/resource behavior stable after injection

### `F` = orchestration engine
Observed role:
- scans container entries
- classifies entries
- builds working lists/maps
- constructs `A` descriptors
- builds `w` via `x`
- coordinates dex injection and other payload flows

Reusable lesson:
- successful dynamic bypass often needs a dedicated orchestration class, not just a handful of helpers

## Container / trust-chain observations

### `will/dex/README.txt`
Observed text:
- `dex放置此处可动态加载`
- `Placing some dex files here can be dynamically loaded`

This is an explicit signal that `will/dex/` is a staging area for dynamically loaded dex.

### META-INF trust material is real and likely used by the bypass
Observed in the mod APK:
- `META-INF/APKTOOLK.RSA`
- `META-INF/APKTOOLK.SF`
- `META-INF/MANIFEST.MF`

The codebase also contains lanes that use:
- `PKCS7`
- `SignerInfo[]`
- `X509Certificate`
- `PackageParser.collectCertificates(...)`
- `SigningDetails` / `SigningInfo`

High-confidence conclusion:
- the mod does not just preserve signing artifacts passively; signing/certificate-related material is part of its active runtime identity/trust pipeline

## Multiple trust/signing lanes
The audit strongly suggests more than one signing-related lane exists:

### Lane A: transport -> identity reconstruction
- `InputStream` -> `l` -> `a`
- used to reconstruct strings, `Signature[]`, `SigningInfo`

### Lane B: PKCS7 / certificate-backed extraction
- `c.e(InputStream)` uses `PKCS7`, `SignerInfo`, `X509Certificate`
- likely used for trusted extraction / certificate-backed payload handling

### Lane C: Android package signing compatibility lane
- `PackageParser.collectCertificates(...)`
- `SigningDetails` -> `SigningInfo`

Reusable lesson:
- a stronger bypass does not rely on a single fake-signature trick; it may combine multiple signing lanes for compatibility and resilience

## Practical explanation for why the mod likely works while naive re-signs crash
The working model is now:
1. own startup with shell `Application` + `AppComponentFactory`
2. parse/build identity metadata and signing state
3. rewrite runtime objects (`PackageInfo`, `ApplicationInfo`, `LoadedApk`)
4. dynamically inject helper dex code/classloader adjustments
5. restore and delegate to the original app chain

This is far more advanced than:
- patching parser methods only
- changing a few smali lines in `ConfigImport`
- re-signing and hoping the app survives

## Hard lessons / do-not-repeat list
- Do not assume business-logic patching is the right first move for repack-sensitive apps.
- Do not patch validator/parser helpers first if startup/runtime integrity is the real blocker.
- Do not treat `Signature[]` as enough by itself on modern Android; `SigningInfo` and package/runtime consistency matter too.
- Do not rewrite one layer only. Keep `PackageInfo`, `ApplicationInfo`, and `LoadedApk` synchronized.
- Do not ignore classloader/dex injection possibilities. The working mod clearly relies on that lane.

## Reusable blueprint (simplified)
1. Create shell `Application` and `AppComponentFactory`
2. Keep original app/factory references in a dedicated anchor/data class
3. Open container/zip and build descriptor objects for relevant entries
4. Parse transport metadata into an Android-aware identity object
5. Convert identity metadata into a final runtime spoof profile
6. Rewrite package/app/runtime objects using that profile
7. Load any helper dex dynamically into the runtime classloader
8. Delegate back to the original app chain

## What remains not fully pinned yet
- Exact zip entry names for every signing lane and payload lane are not all mapped yet
- Exact branch selection between the PKCS7 lane and the serialized-transport lane is not fully pinned yet
- Exact use of some helper classes remains partially obfuscated

## Current strategic value
This audit already proved a high-value lesson for future work:
- when naive APK patching/re-signing fails, auditing a known-working mod can reveal the real bypass architecture faster than continuing blind downstream patch attempts
- the main reusable idea here is not a single patch, but a startup/runtime/signing/classloader framework
