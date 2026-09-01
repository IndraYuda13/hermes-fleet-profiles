# Shipped Cheat Assets First

## Pattern
When an Android game ships plain-text UI scene assets, check for disabled or hidden cheat/debug widgets before spending time on native patching.

## Why it matters
A production build can still carry:
- commented-out cheat layer templates in scene XML
- hidden `switch` buttons with `opacity="0"`
- cheat callback names already wired in native code
- AB-test JSON flags that heavily skew balance/debug behavior

## Fast checklist
1. search assets for `cheat`, `debug`, `ab_tests`, `switch`, `all_units`, `add_resource`
2. inspect scene/layout XML for commented template includes
3. inspect cheat widget XML for hidden panels or invisible trigger buttons
4. patch only the smallest asset diffs first
5. build/sign/test before escalating to native libraries

## Caveat
If the asset edits install cleanly but show no runtime effect, the next boundary is usually native asset-load gating, variant scene selection, or server-authoritative state.
