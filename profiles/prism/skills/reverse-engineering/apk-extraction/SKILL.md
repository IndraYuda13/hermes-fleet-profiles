---
name: apk-extraction
description: Extract and replicate APK crypto logic offline.
version: 0.1.0
author: Hermes
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Reverse-Engineering, APK, Crypto, Python]
---

# APK Crypto Extraction & Replication

Downloads APKs directly via a third-party mirror (bypassing Play Store authentication), decompiles them using `jadx`, locates cryptographic keys and algorithms using `search_files`, and replicates the encryption/decryption logic in Python. It does NOT handle apps that offload crypto logic entirely to native C/C++ libraries (.so files).

## When to Use

- The user provides a Google Play Store link and asks to extract API keys, decryption keys, or payload logic.
- You need to decrypt API requests/responses intercepted from an Android application.
- You are building a Python client to spoof or interact with an app's backend API.

## Prerequisites

- `jadx` installed (verify with `jadx --version`).
- `unzip` installed.
- Python 3 with `pycryptodome` or `cryptography` installed (`pip install pycryptodome`).

## How to Run

Execute shell commands via the `terminal` tool to download and decompile the APK. Use `search_files` to find crypto classes, and `read_file` to analyze the Java source. Finally, use `write_file` to adapt the Python replication template.

## Quick Reference

- Aptoide API (Reliable Download): `https://ws75.aptoide.com/api/7/app/get/package_name=<package_id>` (Extract `.nodes.meta.data.file.path`)
- APKPure Direct Download URL: `https://d.apkpure.net/b/APK/<package_id>?version=latest` (Often blocked by Cloudflare 403)
- JADX Decompile Command: `jadx -d <out_dir> <file.apk>`
- Support Files:
  - `references/string_decoding_java_to_python.md`: Guide to replicating Java XOR string decoders.
  - `references/hybrid-app-re-guide.md`: Triage patterns for Cordova/Ionic/WebView hybrid apps (JS-side logic, CryptoJS, session mgmt).
  - `references/native-app-api-signing-patterns.md`: Modern native app patterns: `xdata`/`xtime` encrypted envelopes, `x-api-key`/`x-signature` headers, HMAC construction, Spice/Cardamom key obfuscation, MyXL v9.3.0 endpoint map.
- Common Crypto Regex: `SecretKeySpec|Cipher.getInstance|decrypt|encrypt|AES|payload`

## Procedure

0. **Hybrid App Detection (do this right after decompile):**
   After JADX finishes, check if the app is a WebView hybrid (Cordova, Ionic, React Native webview, etc.):
   ```bash
   ls <out_dir>/resources/assets/www/  # Cordova/Ionic
   ```
   Also check `MainActivity.java` for `CordovaActivity`, `WebView`, `@JavascriptInterface`, `loadUrl`.
   **If hybrid**: business logic (login, API calls, crypto) lives in JavaScript files under `assets/www/`, not in Java source. Switch to the hybrid triage path:
   - Read `index.html` to find all `<script>` tags (load order matters)
   - Key files: `*.constants*.js` (endpoints, base URLs), `*.service*.js` or `*.factory*.js` (HTTP call wrappers), `*.controller*.js` (screen logic), and any `aes.js`/`SHA*.js`/`crypto*.js`
   - JS is usually minified single-line: use `python3 -c` with string slicing or `js-beautify` to extract specific functions by searching for `function <name>`
   - Search `assets/www/` for endpoints/auth: `search_files(pattern="login|auth|token|sign|otp|encrypt|decrypt|baseUrl|BASE_URL", path="<out_dir>/resources/assets/www")`
   - `JavascriptInterface` methods in Java are the bridge: they expose native capabilities (KeyStore, device info) to JS. Trace what JS calls via `Android.<methodName>()`
   - See `references/hybrid-app-re-guide.md` for detailed patterns
   **If native Java**: continue with step 3 (Locate Crypto Logic).

1. **Extract Package ID & Download:** 
   Parse the `id=` from the Play Store URL (e.g., `com.app.example`). 
   First, try Aptoide (more reliable for automated downloads):
   ```python
   # using python execute_code or terminal
   import urllib.request, json
   url = "https://ws75.aptoide.com/api/7/app/get/package_name=<package_id>"
   req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
   res = urllib.request.urlopen(req).read().decode("utf-8")
   data = json.loads(res)
   print(data.get("nodes", {}).get("meta", {}).get("data", {}).get("file", {}).get("path"))
   ```
   Download the extracted URL using `wget` or `curl`.
   If Aptoide fails, try APKPure:
   ```bash
   curl -sL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" "https://d.apkpure.net/b/APK/<package_id>?version=latest" -o target.apk
   ```

2. **Decompile APK:**
   Run JADX using `terminal`:
   ```bash
   jadx -d out_dir target.apk
   ```
   *Tip: If the APK is large, run it with `background=true` and `notify_on_complete=true`. You can use `search_files` concurrently on the partially decompiled source (`out_dir/sources/`) to find keys early without waiting for 100% completion.*

3. **Locate Crypto Logic:**
   Use `search_files(pattern="SecretKeySpec|Cipher.getInstance", path="out_dir", target="content")` to pinpoint where keys are initialized. Use `read_file` to analyze the matching Java files. Look for:
   - The Seed Key (hardcoded string or dynamically generated).
   - Block Cipher Mode (e.g., `AES/ECB/PKCS7Padding` or `AES/CBC/PKCS5Padding`).
   - Key Derivation Function (e.g., `MessageDigest.getInstance("MD5")`).
   - Data encoding (Base64 vs. Hexadecimal).

4. **Replicate in Python:**
   Use `write_file` to create a Python script based on `scripts/crypto_template.py`, modifying the key derivation, cipher mode, and padding to match the Java logic. Test it against known encrypted payloads provided by the user.

5. **Cleanup:**
   Delete the downloaded APK and decompiled folder via `terminal` once the script is verified, if the user requests cleanup.

## Pitfalls

- **Hybrid App Misidentification:** Many Indonesian telco/fintech apps (MyXL, Axisnet, etc.) are Cordova hybrids. If `search_files` for `SecretKeySpec|Cipher.getInstance` returns only Facebook/Firebase SDK hits and no app-specific crypto, check `assets/www/` immediately. The crypto is in JS (CryptoJS), not Java. Wasting time tracing obfuscated Java classes that turn out to be analytics SDKs is the #1 time sink.
- **Mirror Version Staleness:** Aptoide frequently serves outdated APK versions (e.g. v3.9.11 when Play Store has v9.3.0). Always compare `vername` from Aptoide response against the Play Store page. If stale, use APKPure instead — it reliably serves latest versions even for 100MB+ APKs. APKPure's `d.apkpure.net` endpoint works well with a browser User-Agent for automated downloads.
- **App Bundle / Split APK Problem:** Modern apps ship as Android App Bundles (AAB). A single APK downloaded from mirrors may be missing entire module dex files. Symptom: a class (e.g. `CardamomHelper`) is referenced in every dex but its class definition exists in NONE of them — jadx, baksmali, and androguard all fail to find it. When this happens: (a) try downloading XAPK/split APK format from APKPure or APKMirror, (b) check if the app has dynamic feature modules, (c) fall back to dynamic analysis (Frida on device/emulator) to dump runtime values.
- **Obfuscated String Decoding:** Apps often use custom string decoding routines (like XORing characters with a hardcoded array). You may need to replicate the decode logic exactly in Python. When translating Java XOR logic for chars to Python, ensure you account for char byte boundaries, e.g., `chr((ord(c) ^ key_val) & 0xFFFF)` instead of raw `0xFF`, since Java uses 16-bit unicode characters. If direct iteration over ciphertext yields padding or encoding errors, try constructing a bytearray first and `.decode("utf-8", errors="ignore")` rather than raw string concatenation.
- **Native Crypto & Secrets:** Apps might use NDK (C/C++ `.so` files) for encryption or secret storage (e.g., Spice/Cardamom library). If `search_files` yields nothing for crypto imports, look for `System.loadLibrary()`. 
  - If analyzing native libs via `objdump`, `nm`, or `readelf`, ensure you use the correct cross-compile binutils for the target architecture if native host tools fail (e.g. `sudo apt-get install binutils-arm-linux-gnueabihf -y` and use `arm-linux-gnueabihf-objdump` for 32-bit ARM).
  - Use `readelf -Ws` and `readelf -l` / `readelf -x .init_array` to analyze `.so` structures when `objdump` architecture parsing fails.
  - **Spice/Cardamom extraction:** JNI functions in `libcardamom.so` often load plaintext secrets from `.rodata` via ARM64 `adrp` + `add` instructions. Disassemble the target function with Capstone, calculate the target address (`(PC & ~0xFFF) + adrp_imm + add_imm`), and extract the string directly from the binary.
  - Native initialization often happens dynamically in `JNI_OnLoad` using `RegisterNatives`, which obscures function names from static exports.
- **Missing Crypto Classes (R8/App Bundles):** If static analysis hits a wall because the crypto utility class (e.g., `EncryptionUtil`) is completely missing from the decompiled output (due to R8 inlining or missing dynamic feature APKs), DO NOT waste time brute-forcing standard AES derivations. Immediately pivot to providing a Frida script for dynamic analysis to hook the callers or dump the decrypted payloads.
- **Padding Mismatches:** Java's `PKCS5Padding` is practically equivalent to Python's `PKCS7` padding.
- **Key Encoding:** Ensure you replicate the exact text encoding (UTF-8) before hashing the seed key.
- **Spice / Cardamom Secret Obfuscation:** Kotlin `Spice` library (package pattern `com.*.spice.CardamomHelper`) generates compile-time objects that store API keys, encryption keys, and HMAC keys as obfuscated values. The generated class may not decompile at all if split across AAB modules. Look for `CardamomHelper.INSTANCE.getApiKeyValue()`, `getEncryptionKeyValue()`, `getCiamHmacKeyValue()`. If the class is missing from dex, values must be extracted via Frida hook at runtime: `Java.use("com.*.spice.CardamomHelper").getApiKeyValue.implementation = function() { var v = this.getApiKeyValue(); send("apiKey=" + v); return v; };`
- **Modern API Encryption Envelope (`xdata`/`xtime`):** Some apps (especially Indonesian telco) encrypt ALL API responses server-side. Response body is `{"xdata": "<base64>", "xtime": <unix_ts>}`. Decryption requires: (a) AES key from `CardamomHelper.getEncryptionKeyValue()`, (b) the `EncryptionUtil.decryptAesWithHashedKey()` method which hashes the key before use. Request-side requires: `x-api-key` header (from CardamomHelper), `x-hv: v3` header, `x-signature-time` (unix timestamp), `x-signature` (HMAC of request fields joined by `;`). The interceptor class is typically at `app/interceptor/encryption/`.

## Verification

Run the generated Python script locally using `terminal` or `execute_code`. It must successfully encrypt a test JSON payload and decrypt a known ciphertext to plain text without throwing padding or block-size errors.