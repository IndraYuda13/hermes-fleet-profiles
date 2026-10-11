#!/usr/bin/env python3
"""PNG geometry + blank-render check, stdlib only (no Pillow dependency).

Prints width x height, decoded row count, and the number of distinct RGB
colours. A distinct-colour count of 1 means a blank/uniform image, so this is
the cheap proof that a headless screenshot actually rendered something.

Usage:
    python3 png_stats.py shot-or-dir [more paths ...]

Exit code 0 if every input has >1 distinct colour, 1 otherwise (so it can gate
an evidence report).
"""
import pathlib
import struct
import sys
import zlib


def png_stats(path):
    """Return (width, height, decoded_rows, distinct_rgb_colours)."""
    data = pathlib.Path(path).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path}: not a PNG")
    pos, idat = 8, bytearray()
    w = h = bd = ct = None
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        typ = data[pos + 4:pos + 8]
        if typ == b"IHDR":
            w, h, bd, ct = struct.unpack(">IIBB", data[pos + 8:pos + 18])
        elif typ == b"IDAT":
            idat += data[pos + 8:pos + 8 + ln]
        elif typ == b"IEND":
            break
        pos += 12 + ln

    if bd != 8:
        raise ValueError(f"{path}: only 8-bit depth supported (got {bd})")
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ct]
    bpp = channels
    stride = w * bpp
    raw = zlib.decompress(bytes(idat))

    prev = bytearray(stride)
    uniq = set()
    off = 0
    rows = 0
    for _ in range(h):
        ft = raw[off]
        off += 1
        line = bytearray(raw[off:off + stride])
        off += stride
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if ft == 1:
                line[i] = (line[i] + a) & 255
            elif ft == 2:
                line[i] = (line[i] + b) & 255
            elif ft == 3:
                line[i] = (line[i] + ((a + b) >> 1)) & 255
            elif ft == 4:
                pp = a + b - c
                pa, pb, pc = abs(pp - a), abs(pp - b), abs(pp - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        for i in range(0, stride, bpp):
            uniq.add(bytes(line[i:i + 3]))
        prev = line
        rows += 1
    return w, h, rows, len(uniq)


def main(argv):
    targets = []
    for arg in argv:
        p = pathlib.Path(arg)
        targets.extend(sorted(p.glob("*.png")) if p.is_dir() else [p])
    if not targets:
        print("usage: png_stats.py <png-or-dir> [...]", file=sys.stderr)
        return 2

    bad = 0
    for f in targets:
        try:
            w, h, rows, u = png_stats(f)
        except Exception as exc:  # noqa: BLE001 - report, do not abort the batch
            print(f"{f}: ERROR {exc}")
            bad += 1
            continue
        verdict = "BLANK" if u <= 1 else "OK"
        if u <= 1:
            bad += 1
        print(f"{f.name}: {w}x{h} decoded_rows={rows} "
              f"distinct_colours={u} {verdict}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
