# Investigation Ledger

## Target
- Name: Hungry Shark Evolution
- Type: Android game APK
- Goal: build a practical mod APK for the requested Ubisoft build `13.9.2`
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
  - clean preferred candidate:
    - `downloads/hungry-shark-evolution/hungry-shark-evolution-13.9.2.apkcombo.xapk`
  - fallback specimen / repack:
    - `downloads/hungry-shark-evolution/hungry-shark-evolution-mod_13.9.2-apkvision.apk`
  - strong hybrid outputs:
    - `projects/hungry-shark-evolution-mod/out/HungrySharkEvolution_13.9.2_specimenport_v1.xapk` (superseded, Android R+ install packaging issue)
    - `projects/hungry-shark-evolution-mod/out/HungrySharkEvolution_13.9.2_specimenport_v2.xapk` (current fixed build)
- Traffic captures:
  - none
- Logs:
  - none
- Decompiled / extracted paths:
  - `projects/hungry-shark-evolution-mod/clean_extract/assets/bin/Data/`
  - `projects/hungry-shark-evolution-mod/original_xapk_clean/`
  - `projects/hungry-shark-evolution-mod/specimen_diff/`
- Notes:
  - project folder: `projects/hungry-shark-evolution-mod/`
  - boundary catalog: `projects/hungry-shark-evolution-mod/BOUNDARY-CATALOG.md`
  - roadmap: `projects/hungry-shark-evolution-mod/ROADMAP.md`

## Hypothesis Ledger
| ID | Claim | Evidence Level | Source | Next test | Status |
|----|-------|----------------|--------|-----------|--------|
| H1 | The fastest safe lane will depend on whether the build is mono APK, split, or packed with native-heavy protections. | high | real artifact fingerprint shows clean split XAPK plus fallback mono repack | none for build truth | closed |
| H2 | A direct asset-first godmode/balance lane may exist, but lightweight triage may not expose it cleanly because much of the game lives behind IL2CPP and harder-to-read serialized assets. | medium | Unity IL2CPP confirmed; only a small amount of obvious plaintext content surfaced | keep open as secondary lane | narrowed |
| H3 | The fastest strong mod lane is differential specimen analysis against the same-version APKVISION mod build, then porting those payload deltas onto the cleaner original-signed base. | high | same package/version, concrete payload diffs narrowed to manifest/resources/dex/native, plus real device oracle now confirms the ported build gives large coins/gems | continue with native godmode lane from the narrowed quartet | primary |

## Probe Log
| Step | Probe | Result | Risk | Follow-up |
|------|-------|--------|------|----------|
| 1 | Retrieval preflight across workspace and memory | no prior case note or workspace hit for this target found | low | treat as a fresh target |
| 2 | Start acquisition lane | initial public artifact acquired from APKVISION | low | do not trust as final base |
| 3 | Clean-build search | cleaner APKCombo XAPK acquired and verified as original-signed candidate | low | switch main lane to clean base |
| 4 | Engine triage on clean build | confirmed Unity IL2CPP with `global-metadata.dat` + `libil2cpp.so` | medium | avoid blind Java-only patching |
| 5 | Lightweight content triage | reward/store/shark-related script surface exists, but direct clean gameplay instance closure stayed incomplete with current light tooling | medium | use differential lane instead of stalling |
| 6 | Differential specimen analysis | same-version clean vs mod specimen narrowed real patch surface to base manifest/resources/dex payloads and arm64 `libil2cpp.so` | low | port those payloads to clean split base |
| 7 | Build hybrid `specimenport_v1` | rebuilt clean split package with specimen base payloads + specimen arm64 `libil2cpp.so`, then re-signed | medium | verify on real device |
| 8 | Byte-level verification | rebuilt base/split payloads now match the specimen bytes for the replaced files | low | runtime oracle next |
| 9 | Android R+ packaging fix | user install report proved `specimenport_v1` failed parse because rebuilt `resources.arsc` was compressed; rebuilt `specimenport_v2` preserving original/stimulus compression methods, then zipaligned and re-signed | medium | retry real install with v2 |
| 10 | Runtime oracle on v2 | user installed and played `specimenport_v2`; game runs and large gold/gems are confirmed in real gameplay | low | continue into stronger health/invincibility lane |

## Current Blockers
- Coins/gems lane is now runtime-confirmed, but health/invincibility is still not confirmed.
- Native godmode quartet is narrowed, but not yet mapped to exact managed names.

## Next Best Action
- Keep `specimenport_v2` as the confirmed economy build and continue a separate patch iteration for the native survival quartet.

## Distilled Lesson
- When a same-version public mod specimen exists, differential analysis can be the highest-leverage fast lane. Instead of guessing one cheat at a time, compare clean vs specimen, isolate the real modified payloads, and port them onto the cleaner base while keeping verifier-first discipline.
- Packaging lesson from this target: after hybrid rebuilding for Android R+, `resources.arsc` must preserve stored/uncompressed mode and then be zipaligned. A signed build is not install-proof until those package-level invariants are re-checked.
- Runtime lesson from this target: after the packaging fix, `specimenport_v2` is a real confirmed coins/gems build, not just a byte-matched laboratory port.

## Narrow native godmode lane milestone
- New strongest next lane for a real survival/godmode-style patch is still native `libil2cpp`, not dex/assets.
- Proven narrow candidate cluster from specimen diff:
  - `0x34a790c` -> specimen patch `mov x0, #1 ; ret`
  - `0x34a7990` -> specimen patch `mov x0, #1 ; ret`
  - `0x34ae070` -> specimen patch `mov x0, #1 ; ret`
  - `0x34ae0f4` -> specimen patch `mov x0, #1 ; ret`
- Why this matters:
  - four sibling boolean-looking functions were forced into unconditional success by the specimen
  - that shape is a much stronger survival/gate signal than the earlier coin/gem lane alone
- Lower-value cluster deprioritized:
  - `0x37534f4`, `0x3753528`, `0x37535a4`
  - current read looks more like bounds/rect or UI/gating logic, not the best health oracle
- Secondary cluster kept open:
  - `0x33e2634`
  - `0x33e2c40`
  - specimen returns `0x4fffffff`
  - likely a huge stat/value lane, but semantic meaning is still open
- What is still open:
  - exact managed names for the survival quartet are not closed yet
- Best next action:
  - map only the four survival candidates above to exact Il2Cpp methods before patching them blind into a new build

## Distilled Lesson
- On IL2CPP game specimens, the best godmode lane can hide in a tiny boolean-return native quartet. Constant-return `mov x0, #1 ; ret` clusters deserve higher priority than noisier UI/config diff blocks when searching for survival/invincibility gates.

## Narrow native godmode lane milestone
- New strongest next lane for a real survival/godmode-style patch is still native `libil2cpp`, not dex/assets.
- Proven narrow candidate cluster from specimen diff:
  - `0x34a790c` -> specimen patch `mov x0, #1 ; ret`
  - `0x34a7990` -> specimen patch `mov x0, #1 ; ret`
  - `0x34ae070` -> specimen patch `mov x0, #1 ; ret`
  - `0x34ae0f4` -> specimen patch `mov x0, #1 ; ret`
- Why this matters:
  - four sibling boolean-looking functions were forced into unconditional success by the specimen
  - that shape is a much stronger survival/gate signal than the earlier coin/gem lane alone
- Lower-value cluster deprioritized:
  - `0x37534f4`, `0x3753528`, `0x37535a4`
  - current read looks more like bounds/rect or UI/gating logic, not the best health oracle
- Secondary cluster kept open:
  - `0x33e2634`
  - `0x33e2c40`
  - specimen returns `0x4fffffff`
  - likely a huge stat/value lane, but semantic meaning is still open
- What is still open:
  - exact managed names for the survival quartet are not closed yet
- Best next action:
  - map only the four survival candidates above to exact Il2Cpp methods before patching them blind into a new build

## Distilled Lesson
- On IL2CPP game specimens, the best godmode lane can hide in a tiny boolean-return native quartet. Constant-return `mov x0, #1 ; ret` clusters deserve higher priority than noisier UI/config diff blocks when searching for survival/invincibility gates.
