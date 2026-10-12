# Facebook login in a repacked APK ("Invalid key hash")

## Symptom

After installing a repacked (debug-signed) build, Facebook login dies with:

    Invalid key hash. The key hash <BASE64> does not match any stored key
    hashes. Configure your app key hashes at
    https://developers.facebook.com/apps/<APPID>/

The quoted hash is base64(SHA-1) of the repack's signing certificate, read
from the app's own PackageInfo signature. Letters like l/I/1 are easy to
misread in screenshots — compare decoded values, not typed text.

## Root cause (from FB SDK smali, verified)

- `FacebookSdk.getApplicationSignature()` reads the calling app's
  `PackageInfo.signatures` (GET_SIGNATURES = 0x40), SHA-1s the first
  signature, Base64-encodes it — that value is the "key hash".
- The NATIVE app-switch handlers (`KatanaProxyLoginMethodHandler`, the
  `GetToken` path) hand the flow to the installed Facebook app, which rejects
  any app whose hash is not registered for that FB app ID.
- A repack cannot fix this by registering: adding key hashes needs Facebook
  developer-console access to the target app ID, which only the publisher
  has. For a debug-signed repack of someone else's app, the native FB login
  is dead on arrival — plan around it instead of chasing it.
- Quickest flow diagnostic: FB app installed on the device → native flow
  (fails); no FB app → web flow (often works). That difference tells you which
  handler bit you.

## Fix direction: force the web login flow (patch points verified; field test pending)

Web handlers (browser Custom Tab / internal WebView) run the OAuth dialog via
browser or WebView; the native handlers are the ones carrying the key-hash
rejection. In `com/facebook/login/LoginClient.smali` → `getHandlersToTry()`,
four smali sites decide which handlers get registered:

- `allowsGetTokenAuth()` → force `const/4 v2, 0x0` (never add)
- `allowsKatanaAuth()` → force `const/4 v2, 0x0` (never add)
- `allowsCustomTabAuth()` → force `const/4 v2, 0x1` (always add)
- `allowsWebViewAuth()` → force `const/4 v2, 0x1` (always add)

Mechanically: replace each `invoke-virtual {v1}, ...->allowsXxxAuth()Z` +
`move-result v2` pair with the literal `const/4 v2, 0x0|0x1`; leave the
following `if-eqz v2, :cond_XX` untouched. Redirect deeplinks
(`fbconnect://`, `fbconnect://cct.<pkg>`) already exist in the original
manifest, so the web return path works unchanged. Optional second lever:
`FacebookSdk.bypassAppSwitch = true`.

STATUS: designed from SDK analysis and built; end-to-end device verification
was still pending when written up — treat the device test as required before
claiming the fix works. Cheap pre-test on the UNMODIFIED repack:
disable/uninstall the Facebook app and retry — if login then succeeds,
the device was routing to the native flow and this patch addresses the right
lever.

## If web login also fails

If the browser flow shows the same key-hash error, the app validates on every
flow and a foreign repack cannot satisfy that check — report that honestly to
the user instead of chasing more patches.
