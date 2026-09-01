# MyXL 8.0.0 Modded Tamper-Bypass Specimen

## Target
- Name: MyXL Android modded specimen
- Package: `com.apps.MyXL`
- Uploaded artifact: `/root/.openclaw/workspace/downloads/com_apps_MyXL_8_0_0_1143_4arch_7dpi_1821d4ea21cf0ad5932a780aca.apk`
- Goal: learn what the bypass specimen teaches about startup tamper boundaries, native bootstrap, and secret-vault access that can shorten the path to a working MyXL Python client

## Strongest Original Basis
- Strongest matched original public basis is the APKMirror universal bundle:
  - `myXL - XL, PRIORITAS & HOME 8.0.0 (1143)`
  - package `com.apps.MyXL`
  - uploaded `2025-03-06`
  - packaging: base APK plus split companions, 4 architectures, 120-640 dpi
- Original publisher signer evidence for that build family:
  - `CN=XL Axiata, OU=XL Axiata, O=XL Axiata, L=Jakarta, ST=Jakarta, C=ID`
  - SHA-256 `d768fc1758cd47a0982a5ab5c68d995ddb352178dec84573fae7dadadffdce24`
- The exact original binary was not downloadable from this VPS because APKMirror/APKPure final binary paths were blocked by Cloudflare.

## Proven Facts
- The uploaded APK is a repack/re-sign artifact, not stock publisher output.
- Uploaded artifact signer:
  - `EMAILADDRESS=android@android.com, CN=Android, OU=Android, O=Android, L=Mountain View, ST=California, C=US`
  - SHA-256 `a40da80a59d170caa950cf15c18c454d47a39b26989d8b640ecd745ba71bf5dc`
- The uploaded artifact is a merged universal APK containing all 4 ABI lib trees instead of the original split bundle shape.
- Manifest `Application` is wrapper `com.myxlultimate.srwqw.ershw`, not the ordinary real app class.
- Wrapper `ershw` loads native lib `cuthojkryh` in `<clinit>` and calls native bootstrap methods from:
  - `attachBaseContext()` -> `cxphi()`
  - `onCreate()` -> `uyyzv()`
- Real app class `com.myxlultimate.app.MainApplication` still exists behind the wrapper path.
- VKey / VGuard / VOS is still present and wired:
  - `assets/vkeylicensepack`
  - `assets/voscodesign.vky`
  - manifest `android:zygotePreloadName="vkey.android.vos.AppZygote"`
  - `VkeyListenerImpl` and `VGuardFactory` setup remain in app code
- Request-signing / secret-vault lane is still present:
  - `libmyxl-secret.so`
  - `HmacSecretKey`
  - `SecretKey` injection in app wiring
- `libmyxl-secret.so` exports highly relevant JNI getters including:
  - `getCiamClientId`
  - `getCiamClientIdSecond`
  - `getCiamClientSecret`
  - `getCiamClientSecondSecret`
  - `getCiamHmacKey`
  - `getCiamSslCertKey`
  - `getCiamUrl`
  - `getSslCertKey`
- Local Java-side root/tamper detectors still exist under `i4.*`:
  - `i4/a` checks `Build.TAGS` for `test-keys`
  - `i4/g` checks Magisk / su packages
  - `i4/h` checks Xposed / Substrate / root-cloak packages
- TLS pinning code still exists in Java wiring:
  - `NetworkModule` builds `CertificatePinner` for `https://api.myxl.xlaxiata.co.id/api/v8/` using `secretKey.getSslCertKey()`

## Boundary Catalog
### 1. Java bootstrap boundary
- Location: `com.myxlultimate.srwqw.ershw`
- Why relevant: first app-owned execution boundary after process start
- Status: primary, confirmed
- Reading: wrapper shell inserted before real app lifecycle

### 2. Native loader boundary
- Location: `libcuthojkryh.so`
- Why relevant: strongest candidate for early integrity short-circuit, loader indirection, or real app handoff
- Status: primary, confirmed
- Evidence: `ershw` loads it and calls native bootstrap from `attachBaseContext` and `onCreate`

### 3. VKey / VGuard / VOS boundary
- Location: VKey classes, VOS zygote preload, license assets
- Why relevant: likely runtime integrity / device-attestation layer
- Status: open but strongly confirmed present

### 4. Root / hook / debug boundary
- Location: `i4.*` plus likely `libchecks.so`
- Why relevant: common obstacle for dynamic extraction on rooted / instrumented devices
- Status: narrowed

### 5. Secret-vault / request-signing boundary
- Location: `libmyxl-secret.so`, `SecretKey`, `HmacSecretKey`
- Why relevant: likely shortest path to CIAM HMAC material and SSL pin source
- Status: primary, confirmed

### 6. TLS / pinning boundary
- Location: `NetworkModule` `CertificatePinner`
- Why relevant: matters for MITM, but not the first blocker if the real goal is Python protocol cloning
- Status: confirmed, secondary

## What Is Clearly Patched
- Application entrypoint is wrapped by `ershw`
- Native bootstrap lane via `libcuthojkryh.so` is introduced or at minimum made central
- Artifact is rebuilt and re-signed with Android testkey

## What Is Not Yet Proven
- Whether VKey failure handling was neutralized or only tolerated
- Whether `libchecks.so` anti-root / anti-Frida logic was patched
- Whether TLS pinning was removed or left intact
- Whether request-signing or secret generation was patched
- Whether signature/integrity assets such as `signature` or `sig_cfs` are bypassed, spoofed, or still enforced through native code

## Learning Value For The Current MyXL Client Goal
- Highest value: treat this specimen as a **secret-extraction specimen**, not a generic UI-bypass specimen.
- The most promising transfer is from `libmyxl-secret.so` into the current 9.1.0 CIAM blocker chain:
  - CIAM client IDs / secrets
  - CIAM HMAC key
  - CIAM URL source
  - SSL cert key source
- Even if literal values rotated across versions, this specimen can still reveal the packaging format, JNI boundary, and retrieval structure for the same secret family.
- Proven follow-on lesson from the newer build: 9.1.0 `libcardamom.so` preserves the same getter family and also returns fixed literals from `.rodata`, but those literals are now opaque/base64url-like rather than human-readable final-form strings. This means the old specimen still taught the right boundary, while the newer build adds one more semantic-interpretation step.

## Next Best Action
1. Verify whether the extracted 9.1.0 `Cardamom_getCiamHmacKey` output is consumed directly as the live signer secret or decoded upstream.
2. Diff and triage `libcuthojkryh.so` second.
3. Only then move to `libchecks.so` and VKey enforcement if dynamic extraction is still blocked.
4. Do not spend the next cycle on UI features, generic root bypass, or quota endpoint cosmetics. The shortest path remains CIAM secret recovery and bootstrap understanding.
