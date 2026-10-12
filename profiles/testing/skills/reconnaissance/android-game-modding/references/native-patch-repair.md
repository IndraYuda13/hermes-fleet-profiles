# Repairing a shipped mod's native protection (kill-switch → freeze fixes)

Playbook for when a modded build misbehaves on a real device and there is no
source: arm64 patching of the mod's own hook lib. Worked end-to-end on an
8 Ball Pool hook lib (`libsoimod.so`, 56.31.x-era, ~9 MB, stripped, obfuscated
C++). Addresses below are for that build — always re-verify by asserts, builds
differ between releases.

## 0. Evidence first, patches second

If the tester's device is reachable over adb (wireless debugging or a tailnet),
pull real evidence before building anything. Treat adb as read-only unless the
user explicitly approves device changes — pull logs and status; never modify
device settings or the installed app (a tester may enforce this constraint):

    adb logcat -d > log.txt        # greps below
    adb shell ls /data/anr/        # ANR traces (root or debuggable build)
    adb shell dumpsys dropbox --print   # tombstones / crash entries

Signatures and what each proves:

- `Input dispatching timed out (Waited 5000ms for MotionEvent)` — main thread
  blocked → ANR → frozen screen.
- `Waiting for a blocking GC Alloc` repeated — GC stalled; every thread parked.
- `SuspendThreadByPeer timed out ... culprit <tid>` — one thread refuses to
  suspend; that tid is the freeze source.
- Tombstone backtrace with `sigchain` → mod-lib frames → `dl_iterate_phdr` —
  the handler was mid-dump when everything locked; it holds the linker lock.

Chain: deliberate SEGV (license check) → handler starts a stack dump + retry
loop, maybe `sleep` → thread can't be suspended → GC can't complete → ANR →
eventual SIGKILL. The "crash" is not the bug; the handler's workload is.

Classify the freeze before patching — two classes look identical on screen
(animating app, dead input, ANR dialog repeating):

- Handler class: `SuspendThreadByPeer ... culprit <tid>` with that tid parked
  inside the hook lib — stub the handler (section 2); the GC-flood lines are a
  symptom. Signal handlers are process-wide, so the blocked thread can be any
  worker (SDK / ad threads included), not just the mod's own scanner thread.
- GC-choke class: repeated `Waiting for a blocking GC Alloc` with no culprit
  inside the hook lib while the process heap sits at its cap (`adb shell
  getprop dalvik.vm.heapgrowthlimit` vs the app's `largeHeap` manifest flag).
  The signal path is not the cause and a further native patch round cannot
  help — the levers are the heap cap and the app's allocation pressure.
  Two sub-causes — classify before acting:
  - Heap-cap: main thread parked in `WaitForGcToCompleteLocked` under plain
    allocation frames with the heap at cap → `largeHeap` manifest fix
    (skill §7).
  - Class-load stall: the stack reaches `WaitForGcToCompleteLocked` through
    `ClassLinker::FindClass` / `DefineClass` / `NterpAllocateObject` from a
    first-use UI path (`EditText.setText` + `TextWatcher.onTextChanged`, the
    game's own keyboard/name dialog), often with many workers in
    `WaitingForTaskProcessor`, and package dexopt is not `speed` (check
    `dumpsys package <pkg> | grep 'arm64: \[status'`). Fix: force AOT —
    `adb shell cmd package compile -m speed -f <pkg>`. Observed once: a build
    that froze at profile-name entry completed it and played a full match
    ANR-free after AOT — re-verify per title. Re-apply after every reinstall
    of the APK; the setting does not travel inside the APK.

To find where the un-suspendable thread sits, take the `<tid>` from the culprit
line and read its `sysTid=<tid>` block; the main thread's tid equals the pid.
ANR text captured via `dumpsys dropbox --print` may lack the `DALVIK THREADS` /
`"main"` markers that `/data/anr/` files carry — key on `Cmd line:` and
`sysTid=` instead of assuming the markers exist, and split a huge dropbox dump
per entry — one dump interleaves traces for every dumped process, so split
again per `----- pid N at` block and attribute thread blocks by their `Cmd
line:`.

Extraction that survives huge dumps: list entries first (`dumpsys dropbox |
grep data_app_anr`), then stream just your entry on the device — pipe the
`--print` through `awk '/^<entry-timestamp>/{f=1} f'` — instead of pulling
everything: a full print can exceed the transfer buffer and truncate mid-file
(one 20 MB capture held only the first entries). Same principle for the events
buffer: `am_kill` lines carry THE REASON in the kill record. `... remove task`
right after a fresh install of the same package is the OLD build's process
being removed during update (normal, not a crash); `excessive cpu NN during NN
dur=NN limit=25` is the system's CPU watchdog; and a death with `reason=2
(SIGNALED) status=9` and NO `am_kill` at all is a self-kill (kill-switch /
halt). And when grepping device logs from the host, your own shell command
string is echoed into the device log and pollutes the match set — filter it
out (bracket trick `grep -a '[a]ngousana'`, or drop `adbd` lines) or you will
chase your own query as a "new event".

One package can run several PIDs (game + child processes): `pidof <pkg>` may
print a list — snapshot every PID's `/proc/<pid>/task/*` before concluding
where the burner is.

## 1. Find the mechanism in a stripped/obfuscated lib

- Hunt by behavior, not symbols. Log tag strings in `.rodata` are the best
  anchors: find the tag, xref its address to find the logging call, then walk
  out to the enclosing function.
- Signal setup: locate the init that installs the handler (sigaction or a C++
  wrapper; several signos often share one generic handler). The C++ realm also
  has function-level try/catch personality handlers — patch the sigaction'd
  address, not the personality one.
- Kill-switch trigger: `mov w0,#0xb` (SIGSEGV) near a `raise`/`pthread_kill`
  PLT call; the mod fakes a crash so its handler can exit "silently".
- Fallback kill chain (patch all layers or the bypass leaks): handler `_exit`,
  nearby `kill`/`abort`, Java-side `Process.killProcess`/`System.exit` in dex.
- In this ELF family, file offset == VA for `.text` (sections aligned), which
  makes byte-level patching scriptable; verify per file, never assume. Derive
  the check from `readelf -lW` PT_LOAD (offset vs vaddr) per segment — non-code
  segments like `.data` may not share the identity.
- Toolchain: host binutils `objdump` refuses foreign-arch binaries; disassemble
  with capstone from the venv python. Two traps: set `md.detail = True` before
  touching `insn.operands` (else `CS_ERR_DETAIL`), and for a linear sweep set
  `md.skipdata = True` or decoding silently yields zero instructions at the
  first data blob in the stream. In capstone the `adrp` operand is the
  ABSOLUTE target page (`adrp x1, #0x119000`), not a delta — `adrp` + `add
  x1, x1, #imm` gives the string/data address directly; do not re-add the PC
  page.
- String xref hunt (linear): decode the whole executable segment with
  `skipdata=True`, track the last `adrp` per register, and flag `add/ldr reg,
  reg, #imm` whose sum equals a target string address. Handles ~1.6M
  instructions in seconds and finds every log-string site in a 9 MB lib — the
  fastest behavior anchor on a stripped, obfuscated binary.
- PLT stub to symbol name: correlate GOT slots against `.rela.plt` +
  `.dynsym` (elftools) — `r_offset` IS the GOT address; the stub fetches it
  via `adrp x16 / ldr x17,[x16,#off] / br x17`. This maps every `bl <stub>` to
  `sleep`, `kill`, `abort`, `fopen`, `getAllStackTraces`, etc. Check the args
  before calling a retry loop a spin: `mov w0,#1 ; bl <sleep-stub>` is a 1 s
  sleep loop — confirm with the log cadence (~1 line/s) instead of assuming a
  busy-wait, and throttle it rather than deleting it.

## 2. Patch table (pattern → this build's site)

| # | Original | Replacement | Site (56.31.x `libsoimod.so`) |
|---|----------|-------------|-------------------------------|
| 1 | `bl raise` | `nop` | 0x403994 |
| 2 | handler tail `bl _exit` | `b +8 ; nop` (resume path) | 0x3d1f04 |
| 3 | `bl kill` / `bl abort` | `nop` | 0x40a128, 0x40a12c, 0x4b3218 |
| 4 | trace-builder entry `sub sp,sp,#0x70` | `stp xzr,xzr,[x8] ; str xzr,[x8,#0x10] ; ret` | 0x3d15f4 |
| 5 | `mov w0,#0x64 ; mov w1,#1 ; bl DumpTrace` | `b <epilogue>` (skip 100-frame dump) | 0x3d1b18 → 0x3d1b24 |
| 6 | SEGV/SIGBUS/SIGILL/SIGFPE handler entry | minimal stub (see below) | 0x3d1e08 |
| 7 | `b sleep(x)` tail | `ret` | 0x3d1fe4 |

Patch 4 is the highest-leverage one: every dump path funnels through the trace
builder, so returning an empty list kills `dl_iterate_phdr` everywhere at once.
Patch 6 stub (preserves the handler so the signal is swallowed, but returns):

    stp x29,x30,[sp,#-0x10]!      ; a9bf7bfd
    mov x29,sp                    ; 910003fd
    log(prio 4, tag, "SEGV")      ; copy the original adrp/add/mov/bl words,
                                  ; recompute the bl imm26 for the new PC
    ldp x29,x30,[sp],#0x10        ; a8c17bfd
    ret                           ; d65f03c0

Pitfall: when signal comes from self-inflicted `raise()`/`kill()`, returning
from the handler resumes cleanly at the call site — that's why these patches
work. A recurring real fault re-faults instead, and a stub that logs + returns
WITHOUT advancing the saved PC is then an unbounded re-fault loop. Signature:
your handler tag floods the log (six-figure line counts in a minute), CPU
pins, the system kills the app for excessive CPU, input dies — it looks like a
brand-new bug but it is the same fault. To stop the flood, advance the saved
PC by +4 via ucontext (arm64: pc slot = ucontext+0x1b8 on Android 12+,
derived from the device's libunwindstack: frame pc begins at ucontext+0xb8,
+0x100 into that block). This masks the fault, not the cause — if the app
still misbehaves afterwards (dead input, crashes in the loader/linker), stop
repairing the foreign mod and rebuild from the official base (own-build
section of the skill).

## 3. arm64 encoding cheat sheet (verify each with capstone before writing)

    nop                     d503201f
    ret                     d65f03c0
    b  +N                   14000000 | ((target - pc) >> 2 & 0x3ffffff)
    bl +N                   94000000 | same imm26 math
    ldp x29,x30,[sp],#0x10  a8c17bfd   (matches stp x29,x30,[sp,#-0x10]! = a9bf7bfd)
    mov x29,sp              910003fd
    stp xzr,xzr,[x8]        a9007d1f
    str xzr,[x8,#0x10]      f900091f

Encode → disassemble the produced words back with capstone → only then write
bytes. One silent miscalculation in a control-flow patch is a ship-and-bootloop.

## 4. Safety rules (each one cost a rebuild when skipped)

- Assert original bytes at every site before replacing; capture before/after
  hex in the build log.
- Branch-target scan: enumerate every B/BL target in `.text` and assert no
  target lies strictly inside a region being overwritten (entry point itself is
  fine; interior is a crash waiting).
- Stub frames must be self-consistent: if you `b` to an existing epilogue, its
  `ldp`/`add sp` must match the frame the path pushed (e.g. land on
  `ldp x29,x30,[sp],#0x10` only from a 16-byte frame).
- Neutralizing an exit inside a handler can route execution into the handler's
  retry loop; check what follows the exit call and redirect to the epilogue
  instead of falling through.
- Keep one build script per iteration (`work/build_fix<N>.py`) that starts from
  the previous good APK and re-asserts the whole accumulated patch table, not
  just the new sites.

## 5. Build & verify pipeline

1. Replace exactly one entry in the APK (preserve entry list/order; keep the
   entry's compression) → `zipalign -f -p 4` → `apksigner sign` (debug
   keystore) → `apksigner verify`.
2. QA diff: entry list identical to base; the only non-`META-INF` byte-diff is
   the file you replaced.
3. Final proof: unzip the SIGNED apk, re-disassemble all patch points from the
   shipped `.so`, and assert unchanged companions (other mod libs, dex hashes)
   still match the previous fix.
4. Deliver: sha256 + md5 + size, gofile mirror, confirm the page renders the
   file name/size before reporting the link.

## 6. End state and next iteration

With the handler stubbed, the license SEGV still fires harmlessly — that is the
desired end state (the flag is swallowed, app continues). Ask the tester for a
fresh `adb logcat | grep -iE "<handler tag>|ANR|blocking GC"` on the next run
instead of re-patching speculatively; a healthy post-fix log still contains the
occasional handler line and nothing about GC or input-timeout.

If the follow-up run shows a NEW failure mode instead (input dead while the
screen still animates, a crash inside the loader/linker, a stack overflow in a
component you never touched), the protection is layered and this path has hit
its limit — pivot to the own-build route (section 8 of the skill) instead of
another patch round.
