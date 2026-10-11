---
name: flutter-apk-android-reversing
description: Use when reversing a Flutter/Dart Android APK for secrets.
metadata:
  hermes:
    tags: [android, flutter, dart, reverse-engineering, blutter, apk]
    related_skills: [reverse-engineer-anything]
---

# Flutter/Dart Android APK Reversing

## When to use
Target is a Flutter Android app (APK/XAPK) and you need hardcoded secrets, endpoints, or logic. Flutter app logic is NOT in DEX — it is AOT-compiled into `lib*/libapp.so`. `jadx`/`apktool` on the DEX only give plugins; you MUST dump the Dart snapshot.

## Fast path
1. **Fetch artifact.** XAPK = zip containing base APK + split APKs. The native libs live in the ABI split, NOT the base APK. Prebuilt mirrors (apkpure/apkcombo) are Cloudflare-walled; `pgyer.com/apk/apk/<pkg>` exposes a direct `storage.appmeme.com/<pkg>--<id>.xapk` link scrapable with a real browser.
2. **Triage quickly.** `aapt dump badging`, `aapt dump permissions`, `aapt dump xmltree <apk> AndroidManifest.xml`, and `res/xml/network_security_config.xml` (cleartext domains!).
3. **`strings libapp.so`** for URLs/endpoints — catches many, but misses obfuscated/split literals.
4. **blutter** for the full snapshot (below) — recovers `package:*` disassembly, object pool (`pp.txt`), `objs.txt`.
5. **Probe the recovered API black-box** (auth map, CORS, rate limit, injection).

## blutter setup pitfalls (learned the hard way)
- Run against the **ABI split APK** (`config.arm64_v8a.apk`), NOT the base APK — base has no `lib/*/libapp.so` (`"Cannot find libapp.so"`).
- Needs host deps: `pip install requests pyelftools` **and** `apt-get install -y libcapstone-dev` (cmake fails `pkg_search_module(capstone)` otherwise).
- First run builds the matching Dart VM from source (~100-200s); fetches `dartvm<ver>_android_arm64` and builds in `tools/blutter/build/`.
- Output: `blutter_out/asm/<package path>/*.dart`, `pp.txt` (string literals), `objs.txt` (objects).

## Recovering hardcoded secrets
Secrets are often **XOR-obfuscated integer arrays**, not plain strings. In the dumped asm look for
`[closure] static int <anonymous closure>` containing two `rN = const [ <64 ints> ]` lists; the real value is
`''.join(chr(a ^ b) for a, b in zip(listA, listB))`. A `loadHex`/`base64Decode` call right after (e.g. an `env.dart` getter) reveals the secret. Reconstruct programmatically with regex over the asm, not by hand.

## Crypto patterns to check
- `decodeHexString` / `.base16` → key is a hex string.
- **The client's cipher mode tells you what the client does, not what the server does.** An enum like `AESMode@…` (=`ctr`) resolved in the client's own `encryptData` describes the client's encryption path; a server that decrypts the same key can use a different mode. Do not state the server's algorithm from client code alone.
- **Resolve the raw code format and the server mode empirically — grid-test, don't assume.** For a given decrypt endpoint, vary left/right hex-string lengths and read the error class: `Invalid IV length` = the short side is the IV; `Unexpected token in JSON at position 0` = it decrypted (right mode, valid padding); a PKCS7/JCE `bad decrypt` = wrong mode/padding. Note that `Invalid IV length` fires *at `createDecipheriv` construction*, before any decrypt — so it always wins and is neutral for a true padding oracle. A mode that accepts a 16-byte IV with no PKCS7 complaint is CTR (or a no-padding/ciphertext-stealing mode).
- Check whether the *same* key is used to (a) encrypt data the client hands out AND (b) decrypt via a public endpoint — that is the forgery/decryption-oracle chain.

## Proving the chain (don't stop at a decrypted response)
- Forging a blob the server accepts is the CRITICAL proof, but if the impact is *rendered* (an ID card, a token that a page displays), a JSON response is not enough: capture a **real rendered screenshot** of the artifact on the target's own public page and verify it (see `pentest-report-deliverable`).
- Headless Chrome is the reliable renderer when a CDP `Page.captureScreenshot` times out: `google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars --window-size=430,1400 --force-device-scale-factor=2 --virtual-time-budget=20000 --screenshot=out.png "<url>"`. Use a tall `--window-size` so the whole artifact is captured, then trim uniform white borders with PIL (luminance threshold → bbox) instead of guessing a crop ratio.

## High-value vuln classes for these apps
- Public decrypt/validate endpoints with no auth (`/v2/qrcodes/decrypt-*`, `validate`, `open`) → forge tokens/PII.
- `cleartextTrafficPermitted=true` for internal domains in network-security-config.
- Credentials/tokens in plain `SharedPreferences` (fixed key names) instead of Keystore.
- Stack traces exposed on unauth endpoints (`NODE_ENV` not production).
- React admin `.js.map` left in production.

## Verify impact, don't stop at the key
Recovering a key is HIGH, not CRITICAL — it becomes CRITICAL only when you demonstrate use (forge a token/PII blob the server accepts, or decrypt real data). Prove it end-to-end before rating it.
