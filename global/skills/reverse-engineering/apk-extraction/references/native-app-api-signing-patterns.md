# Native App API Signing & Encryption Patterns

Common patterns found in modern Indonesian telco/fintech Android apps (MyXL, Axisnet, etc.) that have migrated from Cordova hybrid to full Kotlin/Java native.

## Encrypted Response Envelope

Server encrypts ALL API responses:
```json
{"xdata": "<base64_aes_ciphertext>", "xtime": 1784355516}
```

Decryption flow:
1. Key comes from obfuscated helper (e.g. `CardamomHelper.getEncryptionKeyValue()`)
2. Key is hashed before AES use (`decryptAesWithHashedKey`)
3. AES mode typically CBC or GCM with key-derived IV

**Triage Rule:** If `EncryptionUtil` or the specific AES derivation class is missing from the decompiled APK (due to R8 stripping or missing split APKs), **do not waste time brute-forcing PBKDF2/SHA combinations statically.** Document the missing classes and immediately provide a Frida script to the user to hook the interceptor or dump the AES keys dynamically.

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