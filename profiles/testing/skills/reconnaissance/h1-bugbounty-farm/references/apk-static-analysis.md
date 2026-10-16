# APK / shipped-artifact static analysis

For `GOOGLE_PLAY_APP_ID`, `APPLE_STORE_APP_ID`, `OTHER_APK` and
`DOWNLOADABLE_EXECUTABLES` assets. A shipped binary is a complete, static,
publicly downloadable attack surface that needs no rate limits and no live
instance — the best target class when a program bans automation. Everything
below is read-only against a public download; no device or emulator is required.

## 1. Pin the artifact to the store version

Programs only accept the latest store build, and a report without the version is
closed N/A. Google Play builds usually come from the project's GitHub releases:

```bash
curl -sSL -o app.apk \
  https://github.com/<org>/<repo>/releases/download/<tag>/gplay-<name>-<ver>.apk
sha256sum app.apk
```

Record `versionName`, `versionCode`, the git rev the tag points at, the SHA-256
and the byte size in the report's artifact table. The commit rev is what lets a
triager check the source you quoted.

## 2. Prove the constant ships in the binary, not just in source

The strongest single check available statically — do it before reading any code:

```bash
unzip -p app.apk resources.arsc | strings -n 20 | grep -c '<constant>'
```

A count of 1 (or more) proves the value is in the shipped `resources.arsc`.
A count of 0 means you found it in the repository only and must say so.

Then decode for a readable citation:

```bash
apktool d -f -s app.apk -o apktool_out
grep -n '<resource_name>' apktool_out/res/values/strings.xml
```

Quote the file and line number. `apktool d -s` skips dex disassembly, which is
enough for resource work and much faster.

## 3. Trace the constant to its consumer

Clone the repo at the exact tag (`--depth 1`) and grep for the resource name and
the raw value. You are looking for the sink: which API receives it, and whether
anything wraps, derives or protects it. Note explicitly what is *absent* — no
keystore wrapping, no per-install random, no user-derived key — because the
absence is the finding.

## 4. Establish impact from the artifacts in the same binary

Do not speculate about what the data store holds; read the entity/schema
definitions that ship in the same APK and quote the column names. That converts
"the database is encrypted with a weak key" into "this database holds the account
token and plaintext messages", which is what a triager can rate.

## 5. Negative-result discipline

A mobile review that only lists one issue is not credible. Record the areas you
cleared and why, so the next round does not re-derive them: deep-link handlers,
share-intent path traversal, exported components, the JS bridge, hardcoded
secrets beyond the one reported, app-pin / biometric gate, backup
(`android:allowBackup`) settings, and the WebView configuration.

## 6. Duplicate check

Run `search_hacktivity` for the CWE plus the product name, and separately for the
asset family. Prior art frequently exists on a *sibling* asset (the Files client
versus the Talk client) — that is not a duplicate, but it is the argument you must
pre-empt in the report. `program:`, `url:`, `handle:` and `weakness_id:` are
rejected by that endpoint, so a cross-program duplicate stays possible; say so.

## 7. Stop at the boundary

Never install or execute the artifact on a device, and never touch a production
instance the app talks to. If a dynamic proof is required for the program's
policy, the finding is reported as locally proven and the missing step is named
for the human — not silently claimed.
