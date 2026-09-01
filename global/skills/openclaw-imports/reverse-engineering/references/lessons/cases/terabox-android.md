# TeraBox Android

## Target
- Name: TeraBox: 1TB Cloud & AI Space
- Type: Android split APK / XAPK
- Goal: menemukan lane mod anti-iklan yang stabil dengan patch sesempit mungkin
- Scope / boundaries: fokus ke build APKPure `4.15.1 (586)` paket `com.dubox.drive`, mulai dari static triage dulu

## Current Milestone
- Central anti-ads specimen berhasil dibangun: build `4.15.1 (586)` sekarang punya signed split mod yang memaksa state `isAdFree` + `isAdFreeAllThisDay` menjadi true lewat patch smali minimal.

## Artifacts
- APKPure page slug: `terabox-1tb-cloud-ai-space-app/com.dubox.drive/download`
- Package: `com.dubox.drive`
- Version: `4.15.1`
- Version code: `586`
- Source artifact: `projects/terabox-mod/artifacts/TeraBox_4.15.1_586_apkpure.xapk`
- Declared split set from APKPure: base `com.dubox.drive.apk`, `config.armeabi_v7a`, `config.en`, `config.mdpi`
- Rebuilt signed base: `projects/terabox-mod/build/signed/com.dubox.drive_mod-signed.apk`
- Signed companion splits: `projects/terabox-mod/build/signed/config.armeabi_v7a.apk`, `config.en.apk`, `config.mdpi.apk`
- Bundle for install/test: `projects/terabox-mod/build/TeraBox_4.15.1_586_mod-adfree-signed-splits.zip`

## Confirmed Findings
- Belum ada jejak case note TeraBox lama di workspace.
- APKPure web dari VPS biasa kena Cloudflare, tapi acquisition tetap bisa lewat `cloudscraper`.
- APKPure metadata saat ini menyatakan arsitektur `armeabi-v7a`, Android minimum `6.0+`, dan file utama didistribusikan sebagai XAPK split set.
- Static triage menunjukkan dua layer penting yang app-owned: `com.dubox.drive.ads` dan `com.mars.united.international.ads`, jadi lane anti-iklan terbaik bukan mulai dari SDK vendor acak.
- Boundary pusat yang paling kuat saat ini adalah `com/mars/united/international/kmp/rewardads/RewardAdTasksAdFreeState.smali`.
  - `b()Z` adalah predicate `isAdFree`
  - `c()Z` adalah predicate `isAdFreeAllThisDay`
- `DelayStartupKt` memanggil `RewardAdTasksAdFreeState.b()` sebelum mengaktifkan flow app-open ad, jadi predicate ini memang masuk ke jalur iklan saat startup.
- `AdsFreeScreenViewModel` dan controller reward-ads lain juga membaca state yang sama, jadi patch ini bukan sekadar kosmetik di satu layar.
- Ada gate entitlement/remote config terpisah di `AdManager`: switch `na_switch_reward_ad_free_ad`, placement `ad_placement_reward_ad_free`, dan `AdConfig.adFreeRewardAdConfig.userCanUse`.
- Rebuild resource penuh dengan distro `aapt` gagal karena resource modern memakai nama file dengan prefix `$...xml`; rebuild no-res (`apktool d -r`) berhasil karena patch hanya mengubah dex/smali.
- Signed base APK hasil akhir sudah diverifikasi secara statik dengan re-decode ulang, dan method `b()` + `c()` tetap berbentuk `const/4 0x1`.
- User-side runtime oracle then reported `INSTALL_FAILED_MISSING_SPLIT` on the first website XAPK build.
- A concrete packaging mismatch was proven immediately after that report:
  - original APKPure XAPK stores its APK payload entries as `stored` (not compressed), with DOS timestamp `1980-01-01`, and with payload order starting from the base APK
  - the first generated website XAPK had deflated entries and a different order
- The XAPK builder was then corrected to mirror the original container style more closely. New artifact: `projects/terabox-mod/build/TeraBox_4.15.1_586_mod-adfree.xapk`, SHA-256 `e7d7612349220f36136120ef9b42cb3d0853b58a37a49100ecfa91e34d8c32c1`.
- Important remaining truth after that stage: the APKPure specimen was still explicitly `armeabi-v7a`, so if the corrected XAPK still failed with the same split error, device ABI/variant mismatch became the strongest next blocker.
- The public artifact was then pivoted to the APKMirror bundle for the same version `4.15.1 (586)`, because that bundle contains both `split_config.arm64_v8a.apk` and `split_config.armeabi_v7a.apk` plus matching dynamic-feature arm64 splits.
- Current public XAPK hash is now `c85b1e392960320377a727a7f2c390e9db508fac42072de6cbe8eba4a17d0765`, and the root build file matches the APKMirror lane build byte-for-byte.
- Current public manifest truth from the final XAPK:
  - base payload: `base.apk`
  - architecture splits present: `split_config.arm64_v8a.apk`, `split_config.armeabi_v7a.apk`
  - density splits present include `hdpi`, `mdpi`, `xhdpi`, `xxhdpi`, `xxxhdpi`, `ldpi`, `tvdpi`
  - extra dynamic-feature splits remain included, including `split_lib_business_document*` and `split_lib_dynamic_beautify_photo*`
- Current final patch proof in the working/verified arm64-capable lane:
  - file: `projects/terabox-mod/work/apkmirror-base-nores/smali_classes13/com/mars/united/international/kmp/rewardads/RewardAdTasksAdFreeState.smali`
  - `b()Z` returns constant true
  - `c()Z` returns constant true
  - re-decoded signed artifact lane `work/apkmirror-verify-base/.../RewardAdTasksAdFreeState.smali` keeps the same patched truth
- First positive user runtime confirmation later arrived: the rebuilt public mod installed successfully and showed no ads in initial real use.

## Hypotheses In Play
- H1: lane anti-iklan termurah memang bukan rip-out semua SDK, tapi memaksa predicate app-owned `RewardAdTasksAdFreeState` yang sudah dipakai lintas flow.
- H2: remote config / entitlement masih mungkin mengendalikan surface tertentu di luar predicate pusat ini, jadi runtime check tetap wajib sebelum mengklaim coverage penuh.

## Probes Run
- grep workspace untuk jejak `terabox|com.dubox.drive`: tidak ada hasil.
- Fetch APKPure metadata via `r.jina.ai`: berhasil ambil page text dan variant info.
- Download XAPK via `cloudscraper`: berhasil.
- Extract XAPK dan inventaris split/base APK: berhasil.
- Dex/class triage via androguard: berhasil pin package internal ads dan reward-ads state boundary.
- Smali decode via apktool: berhasil.
- Grep callsite untuk `RewardAdTasksAdFreeState.b()` / `c()`: berhasil dan menunjukkan penggunaan di startup + UI ads-free.
- Patch smali `b()` / `c()` lalu rebuild no-res: berhasil.
- Align + sign ulang full split set: berhasil.
- Static re-decode signed base APK sebagai oracle packaging: berhasil.

## Blockers
- Belum ada confirmed successful install+launch on the user's device, so there is still no runtime oracle for actual anti-ads behavior.
- Current build is tied to an APKPure specimen whose split set is explicitly `armeabi-v7a`; this may still be incompatible with some devices even after the XAPK container fix.

## Next Best Action
- Ask user to retry with the corrected XAPK container first.
- If the same `INSTALL_FAILED_MISSING_SPLIT` persists, immediately pivot to variant compatibility triage, especially device ABI / density vs the current `armeabi-v7a` APKPure specimen.

## Distilled Reusable Lesson
- Untuk APKPure yang kehalang Cloudflare dari VPS, `cloudscraper` bisa jadi lane akuisisi awal yang cukup untuk mengunci artifact dan varian build.
- Jika target Android modern gagal rebuild karena distro `aapt` protes nama resource `$...xml`, dan patch hanya menyentuh smali/dex, lane aman yang murah adalah `apktool d -r` lalu rebuild no-res, kemudian align + re-sign seluruh split set dengan satu key.
