# Investigation Ledger

## Target
- Name: Space Shooter
- Type: Android game APK
- Goal: build a practical mod APK for the requested ONESOFT build `1.967`
- Scope / boundaries:
  - in scope: artifact acquisition, package/signer verification, static triage, minimal-diff patch planning, rebuild/signing
  - only if needed: native-heavy analysis, runtime hooks, anti-tamper bypass
  - not yet fixed: exact mod feature set, because the user only asked for a mod APK in general

## Milestones
- [x] target and goal defined
- [x] interface map complete
- [x] artifact inventory complete
- [x] first hypothesis written
- [x] first controlled probe executed
- [x] evidence confidence updated
- [x] mechanism summary ready

## Artifact Inventory
- Binary / APK:
  - source XAPK: `downloads/space-shooter/Space-shooter-Galaxy-attack_1.967_APKPure.xapk`
  - extracted source splits:
    - `projects/space-shooter-mod/original_xapk/com.game.space.shooter2.apk`
    - `projects/space-shooter-mod/original_xapk/UnityDataAssetPack.apk`
    - `projects/space-shooter-mod/original_xapk/config.arm64_v8a.apk`
  - first mod outputs:
    - `projects/space-shooter-mod/out/SpaceShooter_1.967_mod_noads_v1.xapk` (packaging mistake, patch zipped to wrong internal path and not trustworthy)
    - `projects/space-shooter-mod/out/SpaceShooter_1.967_mod_noads_v2.xapk` (current fixed local build)
- Traffic captures:
  - none
- Logs:
  - none
- Decompiled / extracted paths:
  - `projects/space-shooter-mod/base_dec/`
  - `projects/space-shooter-mod/base_dec/assets/bin/Data/level0`
  - `projects/space-shooter-mod/extracted/assets/bin/Data/Managed/Metadata/global-metadata.dat`
  - `projects/space-shooter-mod/extracted/lib/arm64-v8a/libil2cpp.so`
- Notes:
  - project folder: `projects/space-shooter-mod/`
  - boundary catalog: `projects/space-shooter-mod/BOUNDARY-CATALOG.md`
  - roadmap: `projects/space-shooter-mod/ROADMAP.md`

## Hypothesis Ledger
| ID | Claim | Evidence Level | Source | Next test | Status |
|----|-------|----------------|--------|-----------|--------|
| H1 | The fastest safe lane will depend on whether the build is mono APK, split, or packed with native-heavy protections. | high | real artifact fingerprint shows Unity IL2CPP split XAPK | none for build truth | closed |
| H2 | The first practical mod may be asset-first if gameplay/economy values ship locally in readable or lightly wrapped form. | medium | Unity assets and metadata are locally present, but economy lane is broad and hybrid | prefer the smallest scene/object patch first | narrowed |
| H3 | If the game is native-heavy or integrity-gated, the first v1 mod may need to narrow to a smaller lane like ads, speed, or local rewards instead of broad economy edits. | high | IL2CPP + split packaging + ACTk strings confirmed | runtime test a tiny no-ads patch before larger edits | primary |
| H4 | Disabling the `AdmobAds` MonoBehaviour in the startup scene is the cheapest first mod lane and should carry less risk than deep economy/native edits. | high | real Unity scene object found in `level0`, patched `m_Enabled 1 -> 0`, fixed build now embeds the patched `level0` bytes in the final base split | real install/startup/ad oracle | primary |

## Probe Log
| Step | Probe | Result | Risk | Follow-up |
|------|-------|--------|------|----------|
| 1 | Retrieval preflight across workspace and memory | no prior case note or workspace hit for this target found | low | treat as a fresh target |
| 2 | Start acquisition lane | exact `1.967` artifact acquired and verified | low | fingerprint package/signature/splits |
| 3 | Local RE tooling smoke check | `apktool`, `apksigner`, `zipalign`, `aapt`, `aapt2`, `java`, `python3` present; `jadx` missing from PATH | low | use apktool/aapt/UnityPy first |
| 4 | Fingerprint source package | package `com.game.space.shooter2`, versionCode `300967`, split XAPK with base + asset pack + arm64 split | low | inspect engine and protections |
| 5 | Engine triage | confirmed Unity IL2CPP via `global-metadata.dat` + `libil2cpp.so` | medium | avoid blind Java-only patching |
| 6 | Feature-surface triage from metadata | found large local feature surface: ships, rewards, boss, PvP, shop, VIP, battle pass, watch-video, buy-energy, etc. | medium | do not assume economy lane is purely local |
| 7 | Anti-tamper triage | ACTk / obscured prefs / speedhack related strings present | medium | choose minimal scene patch first |
| 8 | First controlled patch | found `AdmobAds` MonoBehaviour in Unity scene file `level0` and changed `m_Enabled 1 -> 0` | medium | rebuild and sign full split set |
| 9 | Rebuild split mod v1 | first rebuild produced a signed XAPK, but local re-check later proved the patched `level0` had been zipped to the wrong internal path | medium | rebuild cleanly from original splits |
| 10 | Rebuild split mod v2 + byte-level verification | rebuilt and re-signed all splits again, then verified the final base APK now contains `assets/bin/Data/level0` byte-for-byte equal to the patched local file | medium | need real device startup oracle |

## Current Blockers
- No real device install/startup proof yet, so the no-ads patch is only build-verified, not runtime-verified.
- ACTk/integrity surfaces may still react differently at runtime on a real device.
- Economy/gameplay lanes remain open but are not yet narrowed enough to justify a larger patch.

## Next Best Action
- Install `SpaceShooter_1.967_mod_noads_v2.xapk` on a real device and verify boot + ad behavior.

## Distilled Lesson
- On a Unity IL2CPP split build with ACTk present, the first practical mod should be the smallest scene/object patch that can be rebuilt safely. A narrow `MonoBehaviour` disable in a real scene file is a better first oracle than jumping straight into currency or damage surgery.
- Extra packaging lesson from this target: a signed split build is not enough proof. Re-open the final base APK and verify the patched asset is embedded at the exact original internal path, not just added as a duplicate/new path.
