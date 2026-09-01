# Packed native loader first

## Pattern
When an Android game's main `libgame*.so` on disk is not a real ELF and instead looks like opaque data/blob content, do not waste the first RE cycle treating that file like a normal exported-symbol binary.

## Better first move
Pivot immediately to:
1. the Java-side native load wrapper
2. the first real loader ELF
3. the loader's bootstrap chain around `JNI_OnLoad`, `inflate*`, `android_dlopen_ext`, `dlopen`, `dlsym`, `mprotect`, and related page-protection or mapping calls

## Why
- The real executable game payload may only exist after runtime inflate/decrypt/map.
- Static strings and exports on the fake `.so` can be too sparse to guide useful early work.
- The loader often reveals both the unpack boundary and the protection boundary.

## Extra payoff
If the same target also ships an input-telemetry or anti-cheat SDK, map that in parallel. It can be easier to pin than the packed gameplay blob, and it can immediately tell you which assist lanes are noisy or dangerous.

## Applied example
- `Eight Ball Pool` `com.miniclip.eightballpool` `56.21.2`
  - packed on-disk `libgame-BPM-GooglePlay-Gold-Release-Module-3935.so`
  - real first boundary was `libloader.so`
  - match/input telemetry boundary exposed cleanly through `libanybrainSDK.so`
