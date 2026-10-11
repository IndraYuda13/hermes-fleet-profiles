#!/usr/bin/env python3
"""runcase.py — decode a .hc in one command, and optionally prove re-encode.

Usage (from alongside hcdecrypt.py, or set HCTOOL_DIR):
    python3 runcase.py /path/to/config.hc
    python3 runcase.py /path/to/config.hc --patch-payload "GET / HTTP/1.1[crlf][crlf]"

Why: keeps inspection to TWO calls per user file instead of many probe scripts —
print the app-shaped JSON, then (optionally) write a mutated copy and decode it
back to prove the encoder round-trips. Depends only on hcdecrypt/hcencrypt.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CANDIDATES = [HERE, os.environ.get("HCTOOL_DIR", ""),
              "/root/.hermes/profiles/testing/cache/scratch/hc/hctool"]
for cand in CANDIDATES:
    if cand and os.path.exists(os.path.join(cand, "hcdecrypt.py")):
        sys.path.insert(0, cand)
        break
else:
    sys.exit("hcdecrypt.py not found — set HCTOOL_DIR")

import hcdecrypt as H  # noqa: E402
import hcencrypt as E  # noqa: E402


def decode(path: str) -> dict:
    return H.decrypt_hc_file(path).to_dict(full=False)


def full(path: str) -> dict:
    return H.decrypt_hc_file(path).to_dict(full=True)


def patch_payload(path: str, payload: str, out_path: str) -> dict:
    """Rebuild the file with a new payload; return the re-decoded slots."""
    blob = open(path, "rb").read()
    outer, meta_raw, segments, url = H.extract_layers(blob)
    vercfg = ""
    if isinstance(outer.get("b"), str):
        vercfg = H.printable_prefix(
            H._field_plain(outer["b"], H.CHACHA_KEYS[7])
        ).decode("ascii", "replace")
    new_segments = list(segments)
    # slot 0 = payload; app stores it as chacha#7(JKL(text)) + 16 tail bytes
    new_segments[0] = E.enc_raw(E.jkl_encode(payload), H.CHACHA_KEYS[7])
    rebuilt = E.encode_outer_raw(meta_raw, new_segments, vercfg, url)
    open(out_path, "wb").write(rebuilt)
    return H.decrypt_hc_file(rebuilt).to_dict(full=False)


def main() -> int:
    ap = argparse.ArgumentParser(description="Inspect / patch an HTTP Custom .hc")
    ap.add_argument("file")
    ap.add_argument("--full", action="store_true",
                    help="show all 32 slots, unfiltered")
    ap.add_argument("--patch-payload", metavar="TEXT",
                    help="write a copy with this payload, then decode it back")
    ap.add_argument("--out", default="patched_payload.hc")
    args = ap.parse_args()

    data = full(args.file) if args.full else decode(args.file)
    print("# decoded", args.file)
    print(json.dumps(data, indent=2, ensure_ascii=False))

    if args.patch_payload:
        back = patch_payload(args.file, args.patch_payload, args.out)
        print(f"\n# re-decoded {args.out}")
        print(json.dumps(back, indent=2, ensure_ascii=False))
        ok = back.get("payload") == args.patch_payload
        print("\nROUND-TRIP OK" if ok else "\nROUND-TRIP FAILED")
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
