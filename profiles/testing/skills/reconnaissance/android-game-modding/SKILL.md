---
name: android-game-modding
description: "Use when sourcing, repairing, or building Android mod APKs."
version: 1.3.0
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
- A previously delivered mod misbehaves on the user's device — silent close,
  force-close after login, or freeze mid-game (repair case; see section 7).
- The user wants their OWN mod built — or repair rounds on a sourced mod are
  not converging: build from the official APK with your own patches (section
  8). While that instruction stands, drop the third-party mod's code entirely
  — no reuse of its patches or libs. The user may later re-authorize the
  third-party base (section 7); the latest instruction governs, keep both
  pipelines' scripts on disk so a pivot needs no rebuilt caches.

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
- Iterate as FIX<n>: each repair ships as its own APK plus a short INFO note
  (sha256, what changed, how to test); never overwrite a previous build — the
  tester may still be on it.

## 6. Protected games: what a mod can and cannot be

If the core `.so` on disk is encrypted (high entropy, no ELF magic), you cannot
patch the game offline — production mods work by ADDING a hook library that
patches in memory at runtime. Plan custom mods the same way (hook lib /
in-memory patch), not by editing the blob.

## 7. Repairing a mod's own protections (kill-switch and freeze fixes)

Fallback path only — prefer the section-8 rebuild once the user wants an own
mod, or when a repair round has not converged. Users can switch direction
between the two bases as rounds land (an own build stalling → back to the mod
base); the latest instruction governs, so keep both pipelines' scripts and
key artifacts in the project dir — a pivot must not require rebuilding caches.
Layered third-party protections
routinely produce a NEW failure mode after each fix (observed escalation:
silent close → freeze/ANR → SIGSEGV log storm → loader stack overflow →
broken Facebook login) — that escalation is the signal you are fixing the
wrong artifact.

Mod hook libs carry their own anti-tamper: a license check that `raise()`s
SIGSEGV for an installed handler to turn into a silent exit, plus
`kill`/`abort`/`System.exit` fallbacks. Two failure modes, in order:

- **Instant or silent close**: neutralize the kill chain — `raise` -> `nop`,
  the handler's `_exit` -> return path, `kill`/`abort`/`exitProcess` -> `nop`.
  Patch both the dex and the native lib; either layer alone remains a trigger.
- **Freeze / ANR minutes in** (app runs, then touches stop registering):
  a signal fires (the same license check, now swallowed) and the handler does
  heavy work inside the signal context — a stack dump that calls
  `dl_iterate_phdr` (takes the linker lock) plus `sleep`/retry loops. That
  thread can no longer be suspended, so ART's GC stalls, all threads sit on
  "Waiting for a blocking GC Alloc", and the main thread trips
  "Input dispatching timed out (Waited 5000ms ...)" — frozen animating screen,
  then SIGKILL. The fix is to make the handler cheap: stub it to log + return,
  return an empty list from the trace builder it calls, drop sleep/loop tails.
- **Freeze that survives a validated handler stub (GC-choke class)**: same
  screen — animating app, dead input, repeating ANR dialog — but the handler
  patches are all in place. Read the ANR and classify: a flood of "Waiting for
  a blocking GC Alloc" with NO culprit tid parked inside the hook lib means
  heap pressure, not the signal path — the process heap sits at its cap under
  the mod's allocation load and the main thread starves waiting for GC. Check
  the cap (`adb shell getprop dalvik.vm.heapgrowthlimit` vs the app's
  `largeHeap` manifest flag). Another native patch round cannot fix this class;
  the levers are the heap cap and cutting allocation pressure.
  **Fix = `android:largeHeap="true"` in the manifest** (raises the cap from
  heapgrowthlimit e.g. 256m to heapsize e.g. 512m). apktool round-trip often
  fails on these APKs (resource names like `$applovin_...` are illegal for
  aapt/aapt2), so patch the AXML manifest binary directly — see
  references/axml-manifest-patching.md. After install, confirm the platform
  took it: `dumpsys package <pkg> | grep flags=` must show `LARGE_HEAP`
  (mini-apk control tests prove the pipeline; see that reference).
  If GC-choke persists even with `LARGE_HEAP` confirmed active, try the
  cheapest lever before another build: force AOT compilation —
  `adb shell cmd package compile -m speed -f <pkg>`; verify with
  `dumpsys package <pkg> | grep 'arm64: \[status'` → `status=speed`.
  Tell-tale that AOT (not a patch) is the lever: the ANR main stack reaches
  `WaitForGcToCompleteLocked` through class loading (`ClassLinker::FindClass`
  / `DefineClass`) from a first-use UI path — focusing a text field, a
  game-side `EditText.setText` / `TextWatcher.onTextChanged` callback; testers
  report it as "freezes when I type my name". AOT survives reboot but is lost
  on reinstall/update — re-run it after every APK install, and give the
  tester the one-liner alongside the APK.
- **"Runs fine, then the SYSTEM kills it minutes in" (excessive CPU class)**:
  the app never stops and the ANR stack shows no culprit inside your lib —
  instead ActivityManager kills it: exit-info `reason=9 (EXCESSIVE RESOURCE
  USAGE) subreason=7 (EXCESSIVE CPU USAGE)`, and `logcat -b events` shows
  `am_kill: [... excessive cpu 302430 during 300075 dur=502374 limit=25]`
  (CPU-time burned vs window vs the 25% limit). a full-screen game you can
  SEE animating is already ~2 cores, so do not reason about "normal" CPU —
  measure. The sysfs-ticks trick: read `/proc/<pid>/task/*/stat` fields
  14+15 (utime+stime) twice 30 s apart over adb (with HZ=100, `Δtick/s ≈ %
  of one core`), or `top -H -p <pid>` on the device; the single runaway
  worker shows up instantly. Vocabulary: the ANR `CPU usage from ...` header
  reports % of ONE core, so a line like `196% 31503/com.miniclip…` is about
  two cores, not 196%; a probe that prints `rate*100` looks like "thousands
  %" and is a factor-100 bug — sanity-check the scale before reporting.
- **A runaway timer/supervisor INSIDE the game (why measuring beats guessing)**:
  a watchdog thread can loop with `Thread.sleep(0)` (passed config e.g.
  `create(3750, 0, 250, 1)` where the second arg is `checkInterval`) — i.e.
  no sleep at all — flooding the main thread via `Handler.post` every
  iteration and burning ~half a core with the main thread at ~2/3 of a core
  just servicing it. The tell is a busy named worker visible only in a
  per-thread measurement (`ResponseTimeMon` here). Fix by stubbing the
  wrapper's start/ensure/resume methods AND the inner runnable's `run()` to
  `return-void` — the class stays referenced so calls remain valid, and the
  self-kill path inside the loop (`Runtime.halt(0)` / `killProcess`) is
  neutralized as a side effect. Do NOT assume such a class is mod-specific:
  this one existed in the official build byte-for-byte with the same call
  site, yet only the mod build burned CPU — attribute from the measurement,
  not from the class's presence. Verified positive test (device): the same
  APK went from a system kill every ~8–9 min to an ANR-free, kill-free
  13-minute session with the runaway worker gone and idle CPU ~4%.
- **"Input dies but the app still animates" (input-hook class)**: the hook
  lib intercepts the game's native touch entry points and has branches that
  `ret` without forwarding, with state flags cleared only on the END path —
  a gesture that never reaches END leaves the flags stuck and every later
  touch is swallowed. Minimal fix: force the END hook to always run its
  clear-state block (turn the guarded `b.eq <clear>` into an unconditional
  `b <clear>`). Keep the menu-function intact; only the leak is removed.

Take the device log first (adb logcat / ANR traces / tombstone backtrace) —
the culprit tid and the handler's call chain are in there, and patching blind
wastes a build. Keep ADB work scoped to the target package and the log
surfaces (`logcat`, `dumpsys`, `/data/anr`, `dumpsys dropbox`): installing/
uninstalling the target package for QA is in scope, but never pull, copy, or
even read the device's own system-app APKs — testers treat that as overreach
however read-only it is; if such a pull already started, kill it, delete the
local copies, and tell the user. To separate "my patches broke it" from
"re-signing broke it", ship controls in one round: the untouched official
build (original signature) and a re-sign-only copy — if only the re-sign-only
and modded builds fail, the cause is repackaging (signature checks, in-app
anti-tamper), not your code. Full patch table, arm64 encodings, and the
verify-from-shipped-APK pipeline:
[references/native-patch-repair.md](references/native-patch-repair.md).
Per-thread CPU probe (names the burner thread from adb):
[scripts/probe_thread_cpu.py](scripts/probe_thread_cpu.py). This title's
runtime-thread anchors (scanner log tag, touch hooks, supervisor):
[references/miniclip-pgl-protection.md](references/miniclip-pgl-protection.md).

## 8. Own-build path: official base + your own patches (preferred)

When the user wants features/fixes they will keep, rebuild from the official
APK with your own patches instead of extending someone else's mod. Tell-tale
that the mod is the whole problem: raw-byte-scan ALL of the official build's
`classes*.dex` for the mod's markers (obfuscated runtime packages, hook-lib
strings, its log tags) — zero hits means the "kill-switch", crash handler, and
freeze machinery are mod-owned and vanish by construction on a clean base.
(Observed: the obfuscated package the mod loaded at runtime had zero hits in
the official dexes.) Chasing such protections through repair rounds costs one
build per new failure mode and does not converge.

Pipeline — exercised through build → sign → QA; swap in your real dex name:

1. `baksmali d classesN.dex -o smali/off_cN`; assemble with
   `smali a <tree> -o classesN.dex -a 25` (baksmali/smali 2.5.2; a dex
   reassembled at api 25 loaded fine on Android 16). Keep the pristine tree —
   it is the diff baseline.
2. Patch a COPY of the tree (e.g. `smali/v1_cN`), never the pristine one.
3. Assemble, then zip-swap that single dex into the official APK, preserving
   entry order and per-entry compression (same swap mechanics as
   references/native-patch-repair.md §5).
4. `zipalign -f -p 4` → `apksigner sign` (debug keystore) → verify v2+v3.
5. QA: entry sets identical except `META-INF/*` and `stamp-cert-sha256` (a
   Play-signed original carries that stamp; re-signing drops it — do not fail
   QA on those); the only byte-differing entry is your dex. Assert the base
   APK's sha256 in the build script before touching anything.
6. Proof: re-baksmali the dex from the SIGNED APK and (a) diff against your
   tree — `cond_XX` label renames are cosmetic reassembly noise, verify no
   semantic change; (b) re-read every patch site. Ship only after both pass.
7. Audit repack side effects before delivery: the new signature breaks
   Facebook login (references/facebook-login-repack.md) and anything else that
   reads the app's own signature.

Keep a per-version build script (`work/ownmod/scripts/build_v<N>.py` pattern):
copy → patch → assemble → swap → sign → QA, every step asserting, so each
build is reproducible from the previous one.

## 9. Workspace hygiene between rounds (shared host)

Multi-round repair work accumulates extracted APKs, decoded trees, intermediate
signed APKs, and multi-hundred-MB log captures. The host may be shared with
other agents/profiles, so only the project directory is yours.

1. Inventory first — `du -sh <project>/* <project>/work/* <project>/refs/*`,
   plus a per-file listing of the project root — and record free space
   (`df -h`).
2. Classify every deletion candidate as: yours-and-regenerable,
   yours-and-keep, or another agent's. Never delete or touch anything outside
   the project dir.
3. Delete regenerable/superseded: `work/fix<N>/` intermediates, baksmali/jadx
   trees (rebuildable from the source APK plus scripts), temp dex trees, raw
   log captures once distilled to a findings note, and FIX builds the tester
   has moved past.
4. Keep: the latest shipped APK (plus any build the tester might still report
   on), all per-version build scripts, journals, INFO notes, and one distilled
   log per incident.
5. Run deletions as a checked script that echoes before/after free space, not
   an ad-hoc `rm` chain, and kill leftover background captures (a long-running
   `adb logcat` pipe keeps writing to disk). Report freed space plus the
   kept-artifact list.

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
- Before overwriting a code region, enumerate every B/BL target and confirm
  none lands strictly inside it — a branch into a half-replaced stub crashes
  in a way that looks unrelated to the patch.
- Assert the expected original bytes (and every earlier fix's bytes) before
  each replace; abort on mismatch and rebuild from the previous good APK.
- Prove patches by disassembling from inside the final signed APK, not from a
  working .so copy — the zip/align/sign steps are where a wrong payload slips in.
- After any re-sign, audit features that read the app's own signature before
  delivery — Facebook login key-hash is the common breaker
  (references/facebook-login-repack.md).
