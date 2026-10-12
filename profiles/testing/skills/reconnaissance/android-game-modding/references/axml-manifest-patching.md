# Binary AXML manifest patching (and the sorted-attribute trap)

When apktool can't rebuild (illegal resource entry names, e.g.
`res/drawable/$applovin_...` → aapt: "Invalid file name"), patch
`AndroidManifest.xml` (binary AXML) directly inside the zip. Proven flow:

1. Extract `AndroidManifest.xml` from the APK.
2. Add the string (e.g. `largeHeap`) to the string pool: insert the 4-byte
offset at the END of the offset array (`po+28+4*stringCount == po+stringsStart`,
always), insert the encoded string data at the current data end + 4, fix
`stringCount`, `stringsStart += 4`, pool chunk size, file size. `new_off =
ins_pos - (po + stringsStart + 4)` — offsets are relative to the (new)
stringsStart.
3. Extend the RESMAP chunk so `count >= newIndex+1`, set
`resmap[newIndex] = <resource id>` (android attr ids: largeHeap =
0x0101035A). Without the resmap entry the platform treats the attr as unknown.
4. **Insert the new attribute into `<application>` SORTED BY res-id ascending**
— insert at the first index whose res-id > new res-id. THE TRAP: appending
at the end works fine in aapt (dumps the attr) and even in a small test APK,
but for large manifests (many attrs) PMS/libandroidfw SKIPS a non-monotonic
attribute and `LARGE_HEAP` never appears in `dumpsys package`. This cost a
full debug cycle: aapt showed the attr, device flags didn't. Bisect tool:
install the exact patched manifest in a mini APK with a different package
name (fresh parse) vs updating the real package (incremental parse).
   Attribute record = 20 bytes: ns(4) name(4) rawValue(0xFFFFFFFF) +
   typedValue(size=8,res0=0,type=0x12 BOOL,data=0xFFFFFFFF for true).
5. Bump the start-element chunk size + attr count, file size.

Verify after install (in order):
- `aapt dump xmltree out.apk AndroidManifest.xml` → `android:largeHeap(0x0101035a)=(type 0x12)0xffffffff`
- `adb shell dumpsys package <pkg> | grep flags=` → contains `LARGE_HEAP`
- Negative control: same APK without the patch does not show the flag.

Bonus QA: entry diff vs base must be exactly `['AndroidManifest.xml']`
(skip META-INF + stamp-cert), and the lib hashes stay identical.

Ready-made tools in `/mnt/tools/bin/apkmod_kit.py`:
`manifest-fix src dst largeHeap` (sorted insert), `verify`, `diff`.
