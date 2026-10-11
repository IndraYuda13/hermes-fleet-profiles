# Raw layers: what the bytes actually are

Answers "is the raw file already JSON?" with real intermediate values instead of
prose, and gives the verified per-layer check commands. Re-deriving these from
scratch wastes a session; copy the recap.

## One-line answer

**No.** The `.hc` on disk is XOR'd UTF-8. JSON appears only after
`XOR -> hex-decode -> ChaCha20`. There are two raw levels worth emitting:

| Level | What it is | Still encrypted? |
|---|---|---|
| L3 outer JSON | `{"a": {...}, "b": "...", "c": "..."}` | yes — every value is a hex field |
| L4/L5 | 32 split segments + per-slot transform trace | slots still need per-slot decode |

## Verified layer recap (run these to reproduce)

The fastest path is the built-in dumper — it emits stages 0..6 (raw file, XOR
output, ciphertext, outer JSON, decoded outer fields, slot stream, per-slot
values with transform trace) as one JSON document:

```bash
python3 hcdecrypt.py config.hc --layers              # all stages
python3 hcdecrypt.py config.hc --layers --limit 120  # cap preview bytes
```

`0_raw_file.is_ascii_json` is the machine-checkable proof that the on-disk file
is NOT JSON (it is `false`), and `3_outer_json.is_json` is where JSON first
appears. Use the manual steps below to double-check or when the tool is absent.

```python
import json
XOR = bytes.fromhex("e382e4b8adc386f09f9293")
K5  = bytes.fromhex("81342f558a6273bac4548d473f54c4ffc7c41747dee81369acab9c787d41ab9c")

raw = open("config.hc", "rb").read()

# L0+L1: codepoint&0xff of each UTF-8 char, XORed with the 11-byte key
txt    = raw.decode("utf-8")                       # byte count != char count
hexstr = bytes((ord(c) & 0xff) ^ XOR[i % 11] for i, c in enumerate(txt))

# L2: hex -> ChaCha20 (nonce db*8, counter block 1, key #5)
from Crypto.Cipher import ChaCha20
c = ChaCha20.new(key=K5, nonce=b"\xdb" * 8); c.seek(64)
plain = c.decrypt(bytes.fromhex(hexstr.decode()))
outer = json.loads(plain[: plain.rfind(b"}") + 1].decode("utf-8", "replace"))
```

Observable checkpoints on a healthy file:
- `len(raw)` in bytes != `len(txt)` in chars when the outer XOR produces
  codepoints > U+00FF (typical UTF-8 expansion, e.g. `c3 97` = `×`).
- `all(chr(b) in "0123456789abcdef" for b in hexstr)` must be **True** — if it is
  not, you have the wrong XOR key or a non-`.hc` container.
- `plain[:1] == b"{"` and `outer` has key `"a"`.
- `hexstr` may already be ASCII hex, so `bytes.fromhex(hexstr.decode())` takes the
  hex string, not `hexstr` bytes as raw ciphertext.

## Per-slot transform signature (what a decoded file should look like)

From a v2ray-enabled sample, the expected `slot_transforms` shape:

```
payload      -> chacha#7, jkl
proxy        -> jkl                    (bare base64, no chacha layer)
sshField     -> chacha#7, jkl, braille
ovpnUserPass -> chacha#7, jkl
sni          -> chacha#7
psiphon2     -> chacha#7               (keeps the [splitPsiphon] marker)
v2rayConfig  -> chacha#7, jkl          (decodes to a JSON object)
notes        -> (no transform)         (plain-text segment)
version      -> (no transform)
```

Slots whose only trace is `chacha#7` + `non-text:<hex>` are leftover keystream
("" in app output). `dnsResolver` (slot 31) is normally exactly that.

## Verified fixtures

Six real files are kept in `samples/`. Record md5/sha256 whenever a new one
arrives — the user tracks hashes, and identical hashes prove a re-send.
Distinct stores ship distinct slots: one fills only `payload`+`sni`, another
only `sshField`, another carries a full `v2rayConfig`.

Regression gate after ANY change to the decoder:

```bash
python3 hcdecrypt.py --self-test      # per-sample expected sshField strings
python3 hcencrypt.py                  # bit-exact round-trip, all samples
```

Both must stay fully green; the encoder suite is what catches a change that
decodes fine but can no longer be written back.
