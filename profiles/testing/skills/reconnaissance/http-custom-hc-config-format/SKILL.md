---
name: http-custom-hc-config-format
description: Use when decoding HTTP Custom (xyz.easypro) .hc configs.
metadata:
  hermes:
    tags: [android, apk, httpcustom, hc, config, reverse-engineering]
    related_skills: [reverse-engineer-anything, flutter-apk-android-reversing]
---

# HTTP Custom `.hc` config: format & decode (7.10.x–7.11.x)

## When to use
Target app `xyz.easypro.httpcustom` (HTTP Custom / AIO Tunnel VPN) or a
"locked" `.hc` config that must be opened.

Working decoder — canonical public copy: `https://github.com/IndraYuda13/hctool`
(hcdecrypt.py, hcencrypt.py, selfcheck.py + samples). Mirror of it during
sessions: `/root/.hermes/profiles/testing/cache/scratch/hc/hctool/` (scratch can
be pruned — clone the repo instead of rebuilding). When fixing it, edit with
`patch()` / targeted replacements — never rewrite the whole file and never
slice on the module docstring: it spans the file head, so docstring/offset
edits collide and leave a file that will not import. Restore from the delivered
zip and re-apply with `patch()`.

Boundary: this covers HTTP Custom `.hc` ONLY. Sibling injector apps use
different containers and keys (`.ziv` ZIVPN = `base64(32).base64(12).base64(data)`,
`.ehi` HTTP Injector, `.dark`, `.npvt`, `.maya`, …). Do not decode those with
this tool or assume the keys/slot layout carry over. When a sibling-format file
arrives mid-task, do only the cheap container probe (split delimiters, sizes,
base64 layering), report that one line, and ask which file/format they actually
want before reverse-engineering the new container — the user may have sent it by
mistake, and a new-app RE effort is expensive to redirect.

## Ground truth: get REAL samples first
App code alone is NOT enough. The `.hc` writer/reader is native and stripped
(`libf2c.so` exports only `JNI_OnLoad` + 4 natives; no crypto in DEX/app logic).
Get real configs and treat them as the oracle:
- `https://api.github.com/search/repositories?q=http+custom+decrypt` then list
  trees for `*.hc` (e.g. `ProNeet-27/httpcustom-configs`,
  `matinezdaniel846-spec/httpcustom-config`).
- Public old decryptors (HCTools/hcdecryptor, hcdrill) only handle <=4.x
  (`hc_reborn_*` AES-ECB + `[splitConfig]`) and FAIL on 7.x. Don't waste time
  on them; the container and keys changed completely.
- Which slots are populated varies per store, so one sample is not
  representative: one store leaves `proxyAddr` (slot 1) as plain text and `sni`
  empty, another puts an 11-byte user in slot 7 with `connectionMode` 2. Keep
  several samples and test every change against all of them.

## Format (verified against 6 real files)
```
L0 file bytes = codepoint&0xff of each UTF-8 char (NOT raw UTF-8 bytes)
L1 byte ^= XOR_KEY[i%11], XOR_KEY = e382e4b8adc386f09f9293   -> ASCII hex
L2 hexdecode -> ChaCha20 legacy (8-byte nonce, seek 64 = counter block 1)
   key table #5, nonce 0xdb*8 -> outer JSON {"a":{...},"b":...,"c":...}
L3 a.uv = slot delimiter (96 hex chars, used AS-IS on the decrypted stream)
   a.xy = chacha#1(uv.join(segments)) + 16 trailing bytes
   a.* and "c" = chacha#7(value) + 16 trailing bytes
L4 a.xy -> chacha#1 -> split by a.uv -> EXACTLY 32 segments
L5 segment: non-hex = plain text ("true", HTML notes), BUT a non-hex segment
            can also be bare base64 JKL with NO chacha layer (`proxy` = base64
            of "www.axis.co.id:80"); try JKL on non-hex segments too
            hex = chacha#7 -> drop 16 trailing bytes:
      slot0 payload  : JKL 1-2x        -> "GET / HTTP/1.1[crlf]..."
      slot7 sshField : JKL -> BRAILLE -> "host:port@user:pass" (see below)
      slot11 ovpnUserPass: JKL
      slot24 psiphon2: chacha#7 keeps the leading `[splitPsiphon]` marker
      slot26 v2rayConfig: chacha#7 -> JKL -> a FULL v2ray JSON config
            (vmess/vless outbounds, streamSettings, ws path, TLS SNI). It is
            multi-line (tabs/newlines), present only when v2ray is enabled
L6 JKL: b64 -> byte ^= T(key) -> b64, T(x)=((x^0xff)&0xca)|(x&0x35),
   key OLD = d5 d4 d3 d2 d1 d0 cf ce cd cc bd bc bb ba b9 b8 b7 b6 b5 b4
   BRAILLE: 2 chars/byte, alphabet starts U+2801,U+2803,U+2809...
```
Key table (used #5 container, #1 slots, #7 meta; full values in hcdecrypt.py):
`2be4342943c6f91ff58987f41a1aafd1…`, `3380aa278b744ba5b529a7f32fa803e4…`,
`cea9305c95168b162a335b137c61983b…`, `4beeace0e42bae8f29470cf40cf2dfac…`,
`f8e5f6ebea90558eb32229da24fd0fb7…`, `81342f558a6273bac4548d473f54c4ff…`,
`45635e6fc70486e2fd10d3c2b4780f02…`, `3d632a251c9820f2baf83e15498d2754…`

## Pitfalls learned the hard way
- Quick path per user file: `python3 scripts/runcase.py <file>` (from this
  skill's directory) prints the app-shaped JSON in one call; add
  `--patch-payload "…"` to also write a mutated copy and decode it back as a
  round-trip proof. Inspect this way instead of writing a fresh probe script
  for every file the user sends.
- A 32-char all-digit "hex" string is NOT a hex field ("645" is the version) —
  require len>=16 and at least one a-f char.
- Every encrypted field = plaintext + 16 keystream bytes. Small values come out as
  `false<garbage>`; normalize by prefix (false/true/lifeTime/\d{1,4}/hex32-64).
- JKL output may be Braille = UTF-8 non-ASCII, so a printable-ASCII filter
  rejects valid results. Validate by UTF-8 decode + isprintable OR alphabet char.
- Delimiter is the outer `uv` value verbatim (NOT its decrypted form), so
  `split(uv)` returns N parts while `split(dec(uv))` returns 1.
- A segment can arrive as a valid hex field WITH a non-hex tail (the container's
  16 trailing keystream bytes sometimes do not get split off). If `is_hex_field`
  fails, walk the cut point down from `len(seg)-1` to `len(seg)-16` and, when the
  prefix is a valid hex field, keep that prefix as the field; only fall through
  to raw text when no prefix qualifies. Skipping this returned whole slots as
  garbage strings.
- Multi-byte UTF-8 in a plain-text segment is preserved only if you keep the
  stream decoded as latin-1 for splitting (1:1 byte index) and re-encode
  latin-1 -> decode UTF-8 before returning the value.
- Judge "is this value real data?" with ONE shared helper that counts `\r\n\t`
  as printable, and apply it in every filter (slot decode AND the
  empty/false drop in the JSON output). Two different notions of printable is
  how a valid multi-line slot gets zeroed by one path while another keeps it;
  the symptom is a populated slot missing only in the app-shaped output.
- A slot holding JSON (e.g. `v2rayConfig`) must be parsed and emitted as a real
  object, not an escaped string: check `value[:1] in "{["` then `json.loads`.
  Users consume that config directly.
- Distinguish JKL once vs twice by scoring candidates (tokens like `[crlf]`,
  `CONNECT`, `HTTP/1.`, `://` win; base64-looking output loses). Payloads can
  chain several requests in one field (`GET …[crlf][crlf]GET-RAY …`) and use
  `[host]`, `[ua]`, `@name` markers — do not assume one request line.
- When the user supplies a known-good decrypted output, diff your JSON against
  it field-by-field (keys AND values) and mirror the app's omission rules. That
  diff is what exposes mojibake, stray metadata keys, and slots the app drops.
- APK download: apkcombo/apkpure are Cloudflare-walled. Working path:
  `apk.cafe/download?file_id=<id>/<slug>` -> parse
  `apk.cafe/go/?file_id=..&b=<b64>`, b64decode -> signed
  `s-06.filesincloud.com` URL (expires); or split URL via
  `apk.watch/download?split=<a>/<b>/<slug>` (prebuilt `.zip` with base+split APKs).

## Field semantics (matched against a user-supplied ground truth)
Output shape the app produces: `{"config": {...}, "protections": {...},
"metadata": {...}}`.
- `metadata.verApp` = outer field `a.vw`; `metadata.pingUrl` = outer `a.rq`.
- `protections.verCfg` = root `"b"` (chacha#7).
- Other outer fields (`yz wx aa cb gf hg ih ji kj ml nm on po qp sr ts ut vu wv
  xw yx zy`) are small flags; keep them in a separate `raw_metadata` block
  instead of dumping them into `metadata`.
- App drops slots that are `"false"` or empty EXCEPT `v2rayConfig`; mirror that
  (and offer a `--full` mode for all 32 slots).
- Slot names in the app's own output differ from the internal labels: slot 1 is
  `proxy` (not `proxyAddr`), slot 7 is `sshField`, slot 24 is `psiphon2`. Diff
  the key list against the user's ground truth and rename to match, or the
  values look right while the keys look wrong.
- Slot 24 (`psiphon2`) is stored as `chacha#7 -> "[splitPsiphon]" + binary
  blob`. Do NOT drop it as non-printable: keep the leading marker and render it
  as one `[splitPsiphon]` per entry (a single blob entry the app shows twice
  => `[splitPsiphon][splitPsiphon]`).
- Any hex segment whose decoded value is mostly non-printable is leftover
  keystream, not data; normalize it to "" (slot 31 / `dnsResolver` always is,
  and an empty `sni` slot is the same thing). Keep normalization per-slot: it
  must not turn a real multi-byte UTF-8 payload into "". Treat `\r\n\t` as
  printable when scoring — `notes` legitimately contains newlines, and a naive
  `str.isprintable()` check silently drops the whole notes field.
- `notes` contains astral-plane math alphanumerics (U+1D400+). The stream is
  split as latin-1 to keep 1:1 indices, so re-encode latin-1 -> decode UTF-8
  before returning, or the notes come out as mojibake.

## Delivering results
When the user asks for the decoded config ("kirim hasil decryptnya", "as JSON"),
deliver FILES, not just chat text — three variants per config, plus the tool:
1. `<name>.decrypted.json` — app-shaped (drops `false`/empty, keeps `v2rayConfig`).
2. `<name>.decrypted.full.json` — all 32 slots, unfiltered.
3. `<name>.decrypted.raw.json` — the above plus raw segments and the per-slot
transform trace (keep the trace: it is the only place a discarded non-printable
value survives, as `non-text:<hex>`).
Ship them together (e.g. `zip -qr pkg.zip hctool` then `zip -qrj pkg.zip out/*.json`)
and also copy the JSONs somewhere durable, since the scratch dir gets pruned.
The app-shaped file is the default; when the user says the output "looks
different" from the app, diff field-by-field against the ground truth they paste
before changing anything, and use `.full.json` to show what your filter is hiding.

When they ask whether the raw file is already JSON: it is not. The `.hc` on disk
is XOR'd UTF-8; JSON appears only after XOR -> hex-decode -> ChaCha20 (outer
JSON), and the outer JSON still holds hex-encrypted fields. Answer with the
layer breakdown plus the two raw levels you can emit — outer JSON (L3) and
segments + transform trace (L4/L5) — and walk the steps explicitly
(file -> XOR -> hex -> ChaCha20 -> outer JSON -> 32 segments -> per-slot decode)
with the real intermediate values, since this user asks for step-by-step
reasoning and prints the file's md5/sha256 for the record. The exact per-layer
commands, expected checkpoints and the per-slot transform signature are in
`references/raw-layer-walkthrough.md`.

## Credentials (slot 7 / 11) — SOLVED
Format `host:port@user:pass`. After chacha#7 -> JKL -> [BRAILLE], user and pass
are each encoded as numeric `A.B` pairs, decoded SEPARATELY with
`byte = (A - IV) >> (B - IV)`.

**IV is not a constant** — observed IV=11 for the 11-byte user, IV=45 for the
28-byte password. Do NOT use `iv = len(pairs)` (that was wrong and produced
garbage). Search IV 0..255, require ASCII-printable output, score by
alphanumeric ratio, pick the best. Works across stores:
- cybertun  -> `CYBERTUNNEL` / `GAUSAH_DI_SAHRE_LAGI_GOBLOK_PAKE_SENDIRI_AJAH`
- vpnjantit -> `1256-vpnjantit.com` / `1256` (tigo: `7658-...` / `7658`)

Pitfall: keep the raw encryption path (enc_raw) available so re-encoding stays
faithful for configs whose credentials are still encoded, instead of leaking the
plaintext back into the file. Encoder round-trip can be made bit-exact: the
container loses 16 trailing keystream bytes, `a.xy` keeps its 16-byte tail, and
the last stream slot's tail bytes are dropped by the consumer.
