# Native App API Signing & Encryption Patterns

Common patterns found in modern Indonesian telco/fintech Android apps (MyXL, Axisnet, etc.) that have migrated from Cordova hybrid to full Kotlin/Java native.

## Encrypted Request/Response Envelopes (`xdata`/`xtime`)

Server encrypts ALL API responses and requires encrypted bodies for mutating/POST requests:
```json
{"xdata": "<base64_aes_ciphertext>", "xtime": 1784355516}
```

Key and IV Derivation:
1. **Body AES Key:** `sha256(seed_key)[:32]` (first 32 hex chars / ASCII bytes → AES-256)
2. **Body AES IV:** `sha256(str(xtime))[:16]` (first 16 hex chars / ASCII bytes)
3. **Cipher Mode:** `AES/CBC/PKCS7Padding` (equivalent to Java PKCS5Padding)
4. **Encoding Asymmetry:**
   - **Request body `xdata`:** standard Base64 (`base64.b64encode`)
   - **Response body `xdata`:** **URL-Safe Base64** (`base64.urlsafe_b64decode`, replaces `+` with `-` and `/` with `_`)

**Triage Rule (Native Packer Detection):** If `EncryptionUtil` or other core utility classes are missing from all decompiled DEX files despite being referenced everywhere:
- Do NOT assume R8 stripping or missing split APKs.
- Check `AndroidManifest.xml` for an obfuscated `application android:name` (e.g. `gzple.yxktp`).
- Check if its `attachBaseContext` loads a native `.so` (e.g. `libwwuivgwnlm.so`).
- Check `assets/` for encrypted DEX blobs (e.g. `tmp*` files with entropy ~8.0).
- The native library decrypts hidden DEX files at runtime (AES-GCM or AES-CBC + gzip). Extract keys from `.data` relative relocations in the `.so` and decrypt statically to recover all original DEX classes offline without needing a device.

## Request Signing Headers

Interceptor chain adds these to every OkHttp request:

| Header | Source | Notes |
|--------|--------|-------|
| `x-api-key` | `CardamomHelper.getApiKeyValue()` | Added by `ApiKeyInterceptor` |
| `x-hv` | Hardcoded `"v3"` | HMAC version identifier |
| `x-signature-time` | `Calendar.getInstance() + server time offset` | Unix timestamp (seconds) |
| `x-signature` | HMAC of request-specific fields joined by `;` | Varies by URL group |

## HMAC Signature Construction

The app maps each URL to a `GroupTypeUrl` enum (PAYMENT, CREATE_CASE, DEFAULT, NON_LOGIN, etc.).

For login/default requests:
```
signature_input = [accessToken, time].join(";") + ";"
hmac_key = CardamomHelper → decrypt → per-type secret key
signature = HMAC(signature_input, hmac_key)
```

For non-login requests (unauthenticated):
```
signature_input = [time, lang].join(";") + ";"
```

## Retrofit API Structure (MyXL v9.3.0)

Base URLs:
- Auth: `https://api.myxl.xlaxiata.co.id/auths/api/v8/`
- General: `https://api.myxl.xlaxiata.co.id/api/v8/`
- Info: `https://api.myxl.xlaxiata.co.id/infos/api/v8/`
- FTTH: `https://api.myxl.xlaxiata.co.id/ftth/api/v8/`
- Gamification: `https://api.myxl.xlaxiata.co.id/gamification/api/v8/`

Key auth endpoints:
- `POST /api/v8/auth/login` — main login
- `POST /api/v8/auth/validate-msisdn` — MSISDN validation
- `POST /api/v8/auth/regist/request-otp` — registration OTP
- `POST /api/v8/auth/regist/validate-otp` — validate registration OTP
- `POST /api/v8/consent/login` — consent-based login

## CIAM Authentication (Aleph Labs)
Apps may offload authentication network calls entirely to Customer Identity and Access Management (CIAM) SDKs (e.g., `com.aleph_labs.ciam`). If Retrofit `@POST("/api/v8/auth/login")` interfaces are missing, look for a CIAM initializer (e.g., `CiamAuthInitializer`) that consumes `CardamomHelper` secrets (Client ID, Secret, URLs) to configure the SDK.

## Key Obfuscation: Kotlin Spice Library / Cardamom

Package: `com.myxlultimate.core.spice.CardamomHelper`
Methods: `getApiKeyValue()`, `getEncryptionKeyValue()`, `getCiamHmacKeyValue()`, `getMoEngageAppIdValue()`, `getMedalliaAppIdValue()`, `getOptimizelyAppIdValue()`

The class may be missing from single-APK downloads (AAB split delivery). Extractable via:
1. XAPK/split APK download (all modules): find the native lib (`libcardamom.so`) in the architecture split, extract the `.rodata` section strings targeted by the `adrp` + `add` instructions in the JNI functions.
2. Frida runtime hook on device/emulator
3. MITM proxy + patched APK (bypass cert pinning, capture decrypted traffic)