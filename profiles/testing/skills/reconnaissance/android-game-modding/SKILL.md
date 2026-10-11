---
name: android-game-modding
description: "Use when sourcing or checking a modded Android APK."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Android, APK, Mods, Verification, Reversing]
    related_skills: [blocked-page-recovery, flutter-apk-android-reversing, reverse-engineer-anything]
---

# Android Game Modding: source, verify, deliver

## When to Use

- User asks to download/patch/mod an Android game or app to add features
  (long lines, prediction, auto-aim, unlimited resources).
- User sends a Google Play / APKPure link and asks for "the latest version"
  or a modded build of it.
- You need to verify whether an APK from a mod site is genuine or a repackage.

Task shape: "get me a mod for <Android game> with feature X" → return a
**verified** installable APK, a mirror link, and install notes. Mod-aggregator
sites are full of fakes, repackages, and version forgeries; the diff test in
step 3 is mandatory before you deliver anything.

Work in a dedicated project dir (e.g. `/mnt/<game>-mod/`) and keep an INFO file
with provenance: source page, sha256, signer, verification results.

## 1. Official baseline

Needed for both the diff test and the user's reference copy.

1. Versions page via `web_extract` (plain curl gets Cloudflare-blocked):
   `https://apkpure.net/<slug>/<package>/versions` → note the versionCode of the
   release the user asked for.
2. Direct download:
   `curl -sL -A "<Chrome UA>" -e "https://apkpure.net/" "https://d.apkpure.net/b/APK/<package>?versionCode=<code>" -o official.apk`
3. Verify before trusting: `unzip -t`, `aapt dump badging` (package + version),
   `apksigner verify --print-certs`, `sha256sum`.
   - Miniclip titles: cert SHA-1 anchor
     `87615343657c0a98155d71ec5a3158218b9a9f62` (matches the fingerprint shown
     on the Play/APKPure listing).

## 2. Candidate mod sources

modplays.com, moddroid.com, liteapks.com, apkmody, gamedva. These are
JS/Cloudflare-hard: open the mod's detail page in the cloud browser, pull the
real file URL out of the rendered DOM (`dl.*` / `files.*` CDN links), and take
the download through the browser's own download path — see
`blocked-page-recovery`, section "Files, not pages". A link that 403s for curl
usually fetches fine through the browser.

## 3. Fake-or-real diff test (the core check)

Unzip both APKs (same or nearest version) and compare structure and bytes:

```bash
diff <(cd official && find . -type f | sort) <(cd mod && find . -type f | sort) | head -50
diff -rq official/ mod/ | grep -vE "res/|assets/(unpack|j1O1)"
for f in $(cd official && find lib -name '*.so'); do
  a=$(sha256sum official/$f | cut -d' ' -f1); b=$(sha256sum mod/$f 2>/dev/null | cut -d' ' -f1)
  [ "$a" = "$b" ] || echo "DIFF: $f"
done
```

Verdict rules:
- **Every file identical except META-INF/signature → FAKE.** It is a repackage
  with zero mods (observed from an aggregator's own file host). Stop; do not
  deliver.
- Real mod markers: debug-key signature (`CN=Android, O=Android`), ADDED `.so`
  files, an extra obfuscated dex package, and often v7a libs stripped
  (arm64-only APK).
- Watch version forgery: the manifest can claim the newest release while the
  native modules are an older build — the module number inside the game lib
  filename (`libgame-...-Module-<NNNN>.so`) is the truth.

## 4. Feature evidence (what to actually tell the user)

Dump strings from the added libs and grep for feature-flag identifiers; these
are the real feature list, not the marketing blurb:

```bash
strings -a lib/libsoimod.so | grep -aE '^[bc][A-Z][A-Za-z_]+$|ESP_|AIM_|Prediction|Extension'
```

8 Ball Pool example set: `bESP_DrawPredictionLine` (bounce prediction line),
`bESP_DrawPredictionPos` (predicted resting position), `bESP_BounceMarkers`,
`bESP_InternalLineExtension` (long line), `bAutoAim` / `cAIM_SnapLine`,
`bPredictionAfterShot` + power control (`Canceling power slider at power %f`).
Full stack notes on this title's protection:
[references/miniclip-pgl-protection.md](references/miniclip-pgl-protection.md).

## 5. Delivery

- Name the final APK descriptively (game, version, mod kind); sha256 it.
- Mirror that works from this host with no key:
  `curl -F "file=@<apk>" https://upload.gofile.io/uploadfile` → the response
  carries `downloadPage` (`https://gofile.io/d/<code>`). Share the **page** link,
  not the per-server download URL (that needs a token). Confirm the page renders
  the file name + size in the browser before reporting the link.
- Install notes to include: uninstall the official app first (signature
  mismatch), Play-Protect "install anyway", the mod menu usually boots with
  everything OFF, and client-side mods carry ban risk → test on a throwaway
  account.

## 6. Protected games: what a mod can and cannot be

If the core `.so` on disk is encrypted (high entropy, no ELF magic), you cannot
patch the game offline — production mods work by ADDING a hook library that
patches in memory at runtime. Plan custom mods the same way (hook lib /
in-memory patch), not by editing the blob.

## Pitfalls

- Do not skip the diff test because a site looks reputable — a byte-identical
  repackage sat behind the most "official-looking" download of all.
- Verify EVERY download this way: marketing text lies, and a forged manifest
  version is a common trick. Trust `aapt dump badging` plus module numbers in
  native lib names.
- Never deliver an APK that has not passed `unzip -t` + `apksigner verify` +
  a fresh `sha256sum` in the same session.
- Triage natively first: `strings`, `readelf`, `baksmali`, `diff` answered every
  question in this class; set up a decompiler only when a specific question
  remains open.
