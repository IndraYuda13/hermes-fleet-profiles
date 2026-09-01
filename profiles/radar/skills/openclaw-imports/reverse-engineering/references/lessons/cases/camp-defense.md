# Investigation Ledger

## Target
- Name: Camp Defense
- Type: Android game APK
- Goal: Build a practical overpowered mod quickly, starting with asset-only edits before native patching.
- Scope / boundaries:
  - in scope: shipped XML/JSON assets, packaging/signing, client-side debug/economy surfaces
  - fallback only if needed: `libcamp_defense.so`
  - out of scope for v1: billing/server-authoritative systems unless they block the local mod path

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
  - source APK: `projects/reverse-apkdownloader-tooling/jobs/20260405-142217_com.stereo7games.tl/raw/Camp Defense_1.0.802_APKPure.apk`
  - modded APK v1: `projects/camp-defense-mod/out/CampDefense_v1.0.802_mod_v1_signed.apk`
  - modded APK v2: `projects/camp-defense-mod/out/CampDefense_v1.0.802_mod_v2_signed.apk`
- Traffic captures: none yet
- Logs: none yet
- Decompiled / extracted paths:
  - `assets/ini/scenes/battle/scene.xml`
  - `assets/ini/scenes/battle/cheats.xml`
  - `assets/ini/scenes/battle/ab_tests.xml`
  - `assets/ini/std/ab_tests.json`
  - `assets/data/data.xml`
- Notes:
  - project folder: `projects/camp-defense-mod/`

## Hypothesis Ledger
| ID | Claim | Evidence Level | Source | Next test | Status |
|----|-------|----------------|--------|-----------|--------|
| H1 | The fastest working mod lane is asset-only, not native patching. | high | single-APK triage plus plain-text battle/economy assets | install and runtime test v1 | narrowed |
| H2 | The game ships a real cheat layer that can be re-enabled by XML only. | high | `scene.xml` contains commented `cheats.xml` template; `cheats.xml` defines working callbacks; native libs reference cheat strings | install and confirm cheat panel appears in battle | primary |
| H3 | Strong battle/economy skew can be achieved through `ab_tests.json` and `data.xml` without touching `libcamp_defense.so`. | medium | plain-text debug flags, mine/storage/training/shop values are patchable | runtime-check battle HP, storage, mine, and training behavior | primary |
| H4 | If v1 installs but has no visible effect, the next blocker is native clamping / asset-load gating in `libcamp_defense.so`. | medium | Cocos2d-x native core and asset references inside `libcamp_defense.so` | trace asset load/use next | open |
| H5 | The settings window can host a practical global cheat panel because it already mounts the shipped `ab_tests.xml` cheat widget. | high | `assets/ini/window_settings/layer.xml` includes `ini/scenes/battle/ab_tests.xml`; v2 repurposes that widget into quick resource buttons | install v2 and confirm settings-screen callbacks mutate balances | primary |

## Probe Log
| Step | Probe | Result | Risk | Follow-up |
|------|-------|--------|------|----------|
| 1 | Acquire public artifact for `com.stereo7games.tl` | succeeded, single APK v1.0.802 | low | inspect assets |
| 2 | Engine / stack triage | confirmed Cocos2d-x native, not Unity/IL2CPP | low | prefer asset-first then native fallback |
| 3 | Search for cheat/debug references | found shipped `cheats.xml`, `ab_tests.xml`, and references in `libcamp_defense.so` | low | inspect scene mounting |
| 4 | Inspect battle scene wiring | `scene.xml` contains commented cheat-layer template | low | re-enable it in mod |
| 5 | Build asset-first mod APK | signed v1 built successfully | medium | device install/runtime validation |
| 6 | Inspect settings window wiring | confirmed `window_settings/layer.xml` already mounts `ini/scenes/battle/ab_tests.xml` | low | repurpose it into a global cheat panel |
| 7 | Build v2 settings cheat panel APK | signed v2 built successfully with settings gold/gems/exp buttons | medium | device install/runtime validation |

## Current Blockers
- No device/runtime validation yet, so v2 is structurally ready but not user-verified.
- Unknown whether settings-screen cheat callbacks mutate balances globally or require a battle/map refresh to surface changes.
- Unknown whether any desired balance path is still clamped in `libcamp_defense.so` after callback dispatch.
- User later chose to pause/skip this target for now after saving the artifacts.

## Next Best Action
- If this target is resumed later, install `CampDefense_v1.0.802_mod_v2_signed.apk` and verify four concrete oracles:
  1. settings window shows the new cheat panel
  2. pressing `+1G Gold` or `+100M Gems` changes visible balance
  3. `Show All Units` or `Add 25 Lvl to units` has a visible effect
  4. battle cheat panel is still present as fallback

## Distilled Lesson
- On Cocos2d-x games, a shipped settings/debug widget can be a cheaper global cheat insertion point than native patching. If a settings scene already mounts a hidden `cheat_widget`, repurposing that widget into direct resource buttons is a strong second step after basic asset-first modding.
