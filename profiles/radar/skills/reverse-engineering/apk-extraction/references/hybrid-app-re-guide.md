# Hybrid App RE Guide (Cordova/Ionic/WebView)

## Detection Signals
- `MainActivity extends CordovaActivity` (Cordova)
- `assets/www/` directory with `index.html`, `cordova.js`, `plugins/` dir
- `@JavascriptInterface` annotations in Java (bridge methods)
- `WebView.addJavascriptInterface(obj, "Android")` in onCreate
- Minimal Java logic (just bridge + WebView setup)

## Architecture
```
Java Side (thin shell)          JS Side (all business logic)
├─ CordovaActivity              ├─ index.html (script load order)
├─ JavascriptInterface bridge   ├─ app.config.min.js (routing/states)
│  └─ getKeys(), saveKey()      ├─ shared.constants.min.js (endpoints, URLs)
│                               ├─ shared.service.factory.min.js (HTTP wrapper)
│                               ├─ shared.function.min.js (encrypt/decrypt, utils)
│                               ├─ <Feature>.Controller.min.js (per-screen logic)
│                               └─ libs: aes.js, SHA512.js, fingerprint.js
```

## Triage Order
1. `index.html` → find all `<script>` tags, note load order, find hardcoded vars (DeployEnv, fingerprint, app version)
2. `shared.constants*.js` → all endpoint names, base URLs, request body templates. Usually an AngularJS `.constant()` call
3. `shared.function*.js` → utility functions: `encryptData()`, `decryptData()`, `generateRequestID()`, `platformCheck()`, `randomString()`
4. `shared.service*.js` → HTTP call wrapper: how URL is constructed (`baseUrl + endpointName`), headers, session management, SSL pinning check
5. `Login.Controller*.js` (or equivalent) → actual login flow: what gets called, in what order, what params

## Common Patterns Found

### URL Construction
URL = `BaseURL` + `endpointName` (from constants).
Example: `https://my.xl.co.id/prepaid/` + `LoginSendOTPRq` = full URL.
The service factory picks BaseURL from constants based on `DeployEnv` (PROD/UAT/STAGING).

### AES Encryption (CryptoJS)
Keys fetched from server (not hardcoded), stored as `"base64Key,base64IV"` string.
```javascript
var parts = keys.split(",");
var key = CryptoJS.enc.Base64.parse(parts[0]);
var iv  = CryptoJS.enc.Base64.parse(parts[1]);
CryptoJS.AES.encrypt(data, key, {iv: iv});  // AES-CBC, PKCS7 padding (CryptoJS default)
```

### Session Management
- Server returns encrypted `sessionId` in response
- Client decrypts it, stores in `localStorage`
- Before each request, client encrypts `sessionId` and sends it back
- Session expiry: server returns `responseCode: "05"` or `"04"` with `"Invalid Session"`

### Platform Check
```javascript
platformCheck() → "00" (Android native), "02" (mobile web), "04" (desktop web)
```
This value goes in request bodies as `platform` field.

### SSL Pinning
- iOS: `cordova.exec(callback, null, "Device", "implementSslPinning", [url])`
- Android: `checkCertificate(url, successCb, failCb)` (usually via `cordova-plugin-sslcertificatechecker`)
- Runs before every API call in the service factory

## Working with Minified JS
Files are typically single-line minified. Strategies:
- `python3 -c` with `str.find()` / slicing to extract specific function bodies
- Search for `function <name>` to find function boundaries
- For AngularJS: DI parameter names are minified (a,b,c...) but string literals (endpoint names, error codes) are intact
- Response code switches (`case "00"`, `case "31"`) are readable even minified
