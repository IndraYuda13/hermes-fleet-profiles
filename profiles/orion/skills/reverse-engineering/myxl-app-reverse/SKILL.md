---
name: myxl-app-reverse
description: "Reverse MyXL APK: unpack DEX, keychain, HMAC API."
---

# MyXL App Reverse Engineering & API Automation

Canonical client repository: `/root/projects/ds-myxl-client` (`IndraYuda13/ds-myxl-client`, private).

## Quick Execution Workflow

```bash
cd /root/projects/ds-myxl-client
export MYXL_PROXY="http://127.0.0.1:31001"   # Residential/proxy required for CIAM endpoints
python3 -m myxl otp 62817xxxxxxx             # Request OTP via SMS
python3 -m myxl login 62817xxxxxxx <OTP>     # Redeem OTP and persist ~/.myxl_session.json
python3 -m myxl profile                      # Inspect subscriber identity and plan
python3 -m myxl balance                      # Check balance and active status
python3 -m myxl quotas                       # Check data quota packages
python3 -m myxl store                        # List package families
python3 -m myxl options <family_id>          # List package options under family
python3 -m myxl detail <package_id>          # Fetch package confirmation token
python3 -m myxl buy <package_id>             # Execute full settlement chain
```

## Production Protocol & Key Working Values
- XDATA_KEY = `5dccbf08920a5527b99e222789c34bb7` (AES-256-CBC, IV=sha256(str(xtime_ms)).hex[:16])
- X_API_BASE_SECRET = `mU1Y4n1vBjf3M7tMnRkFU08mVyUJHed8B5En3EAniu1mXLixeuASmBmKnkyzVziOye7rG5nIekMdthensbQMcOJ6SLnrkGyfXALD7mrBC6vuWv6G01pmD3XlU5rT7Tzx`
- API_KEY = `vT8tINqHaOxXbGE7eOWAhA==`, ENCRYPTED_FIELD_KEY = `5dccbf08920a5527`
- PAYMENT_SIGN_SALT = `ae-hei_9Tee6he+Ik3Gais5=`
- UA = `myXL / 8.9.0(1202); com.android.vending; (oppo; CPH2737; SDK 33; Android 13)`

### x-signature (main API): HMAC-SHA512 HEX
- key = `SECRET;idToken;METHOD;path;ts` — msg = `idToken;ts;` — ts = xtime//1000

### payment x-signature: **NO access_token in key!**
- key = `SECRET;TS#SALT;POST;path;TS` — msg = `accessToken;tokenPayment;TS;BUY_PACKAGE;BALANCE;itemCodes;`

### Purchase chain: families → options/list → options/detail (token_confirmation) → intercept-page → payment-methods-option (token_payment+timestamp) → settlement-multipayment
- Success signal: code 213 FAILED_RESERVE_THIRDPARTY = format OK, just needs balance

### Reference implementations (GitHub):
- `bitscoid/Ah-Si-Ata` (Python, most complete — auth+sess+purchase)
- `Banday-Wrt/myxl-cli` (Python)

### CIAM OTP: ts_for_sign = NOW+300s in Ax-Api-Signature; Ax-Request-At = now (.SS+07:00 format)

## Original Notes (RE details below)

MyXL 9.6.0 protection stack (3 layers), all reversed and live-verified. Artifacts live in `/mnt/rea-work/`.

## Layer 1 — Native packer (libwwuivgwnlm.so)

Symptom: `EncryptionUtil`, `CardamomHelper` referenced but no `.class` def in visible DEX; fake Application `gzple.yxktp` (`source "OurEntryPoint.java"`) loads `libwwuivgwnlm.so`; assets/tmp* files entropy 8.0.

Unpack procedure (script: `/mnt/rea-work/unpack_dex.py`):
1. 5 asset files (`tmp*`) in apk/assets — each:
   - `nonce = f[0:12]`, `ct = f[12:-16]`, `tag = f[-16:]`
   - `key = arrA[i] XOR arrB[i]` — 2×32-byte arrays in `.data` of libwwuivgwnlm.so (map via RELATIVE relocations r_offset 0x4a560+i*8 / 0x4a588+i*8)
   - `plaintext = AES-256-GCM(key).decrypt(nonce, ct+tag, AAD=None)` — AAD length argument is xzr (0); don't use "vkey01" even though the buffer is built
   - `dex = gzip.decompress(plaintext)` — gzip (1f8b), NOT zlib
2. Asset order = pointer array at reloc r_offset 0x4a538..0x4a558.

## Layer 2 — Key sealing (cert-bound)

Native key strings in `libcardamom.so` are sealed. Unseal:
1. Extract signing cert: `openssl pkcs7 -inform DER -in META-INF/BNDLTOOL.RSA -print_certs` → DER
2. `K = base64(cert_der)` (standard, no-wrap)
3. `seal_key = sha256(K)[:32].encode()`, `seal_iv = sha256(K[:10])[:16].encode()`
4. `value = AES-CBC-PKCS5-decrypt(urlsafe_b64decode(native_string), seal_key, seal_iv)`

Sanity check: `getEncryptionKey` unseals to `880d8e7e9b4b787aa50a3917b09fc0ec` (matches hardcoded testKey in EncryptionUtil.kt).

## Layer 3 — Body + HMAC crypto

Body (Request/ResponseBodyEncryptionInterceptor, InterceptorUtil.g):
- `key = sha256(seed)[:32]` ASCII (32 chars = AES-256), `iv = sha256(str(xtime_ms))[:16]` ASCII, AES/CBC/PKCS5Padding
- Request envelope: `{"xdata": b64std(ct), "xtime": ms}`; Response: `{"xdata": b64url(ct), "xtime": ms}` — URL-safe on response.

Headers: `x-api-key`, `x-hv: v3`, `x-signature-time` (unix SECONDS), `x-signature`, `X-REQUEST-ID`, `X-REQUEST-AT`, `X-VERSION-APP`.

HMAC (HmacSecretKey.c + HmacV3 a.java):
- Key format for DEFAULT group (`/api/v8/auth/login`): `key = f"{encHmac512Key};{idToken};POST;{clean_path};{ts}"`
- Data to sign: `data = f"{idToken};{ts};"`
- Signature: `HMAC-SHA512(data, key=key).hexdigest()` — hex-encoded string (not base64).
- Dispatcher uses 24 SecretHmacType switch cases mapping URL groups to signature recipes.

## CIAM Authentication & Token Lifecycle (Keycloak realm xl-ciam)
- Base URL: `https://gede.ciam.xlaxiata.co.id` (blocks datacenter IPs — CF 1006; route via Surfshark proxy :31001+).
- Client IDs:
  - `clientId` (client1: `db80b743...`): OTP request and password grant token minting.
  - `clientIdSecond` (client2: `75e937bc...`): Session extension and autoHE signature handling.
- OTP Request:
  - `GET /realms/xl-ciam/auth/otp?contact=<msisdn>&contactType=SMS&alternateContact=false`
  - Required query param: `contactType=SMS` (never `MSISDN`).
- Token Exchange (Password Grant):
  - `POST /realms/xl-ciam/protocol/openid-connect/token` (form-urlencoded)
  - Fields: `grant_type=password`, `contact=<msisdn>`, `contactType=SMS`, `code=<otp>`, `scope=openid`, `client_id`, `client_secret`.
  - Required headers: `ax-request-at` (`yyyy-MM-dd'T'HH:mm:ss.SSSZ`) and `ax-api-signature`. Without `ax-api-signature`, rejects with 401.
  - Signature formula (`d5/m.a`): `HMAC-SHA256(ciamHmacKey, ax_request_at + grant_type + contactType + contact + code + "openid")`.
- Token Refresh Grant (90-day validity without re-prompting OTP):
  - `POST /realms/xl-ciam/protocol/openid-connect/token`
  - Header: `Authorization: Basic base64(clientId:clientSecret)` using client1 + device headers.
  - Body: `grant_type=refresh_token&refresh_token=<token>` form-urlencoded.
  - Returns fresh `access_token` and `id_token` without OTP. Must use the client that issued the token; client mismatch causes rejection.
- Bearer Header Convention:
  - Protected endpoints require `Authorization: Bearer <id_token>` (JWE 5-segment token from `CiamSession.e()`), not the `access_token`.
- Device Headers (`c5/b` DefaultInterceptor):
  - `ax-request-at`, `ax-request-id` (UUID), `ax-device-id` (MD5 of android_id hex, 32 chars), `ax-request-device`, `ax-request-device-model`, `ax-fingerprint`.
  - `ax-fingerprint` = AES-CBC-PKCS5(`ciamHmacKey` raw bytes, 16 zero IV, device info string) base64-encoded.
- Extend Session (`/realms/xl-ciam/auth/extend-session`):
  - Method is GET. Requires `contact` (AES-CBC encrypted using `ciamHmacKey` + 16 zero IV, base64 urlsafe no-wrap), `contactType=SMS`, and `ax-device-id`.
- Identity Token AutoHE (`/api/v8/auth/identity-token-autohe`):
  - Accepts CIAM token and returns XL session UUID token with HTTP 200 / code `000`.

## Response Error Codes & Troubleshooting
- `132 REQUEST_MISSING_BEARER`: Returned if `Authorization: Bearer` header is missing, token expired, or request body fails parser extraction.
- `135 INVALID_REQUEST`: Request structure or HTTP method mismatch (e.g., calling GET endpoint as POST, or wrong payload wrapper).
- `151 GENERAL_ERROR_HANDLER`: Bearer token and envelope syntactically accepted, but backend account validation failed. Check token client mismatch or account-level authorization.
- `177 REQUEST_BODY_MALFORMED`: Mismatch in settlement body structure or payment signature key. Crucial check: payment signature key must omit `access_token` (`SECRET;ts#SALT;POST;path;ts`).
- `213 FAILED_RESERVE_THIRDPARTY`: Protocol and signature are 100% valid. Refusal is at telecom billing layer due to insufficient balance.
- `User Agent mismatch during token refresh`: CIAM binds tokens to the User-Agent, device ID, and Client ID used during OTP minting. Keep device parameters consistent across refreshes.
- `Cloudflare 1006`: CIAM rejects datacenter IP addresses. Route via residential proxy.

## Key Artifacts & Documentation
- `/root/projects/ds-myxl-client/` (Production Python package, CLI, and test suite)
- `/root/projects/ds-myxl-client/docs/PROTOCOL.md` (Comprehensive protocol specification)
- `/mnt/rea-work/unpack_dex.py` (DEX unpacker)
- `/mnt/rea-work/myxl_final.py` (Consolidated reference script)
- `/mnt/rea-work/evidence/MASTER-FINDINGS.md` (Detailed reverse engineering log)
