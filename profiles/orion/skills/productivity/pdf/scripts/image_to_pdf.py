#!/usr/bin/env python3
"""Zero-dependency lossless JPEG to PDF converter.
Embeds JPEG byte-for-byte using /DCTDecode stream without re-compression.
Supports 1:1 full-bleed (for digital submission/ID cards) and A4 print centering.
"""

import argparse
import os
import struct
import sys

def get_jpeg_info(data: bytes):
    if len(data) < 2 or data[0:2] != b'\xff\xd8':
        raise ValueError("File is not a valid JPEG")
    i = 2
    while i < len(data):
        if data[i] != 0xff:
            i += 1
            continue
        marker = data[i+1]
        i += 2
        # SOF0 (baseline), SOF1 (extended), SOF2 (progressive)
        if marker in (0xc0, 0xc1, 0xc2, 0xc3):
            length = struct.unpack(">H", data[i:i+2])[0]
            precision, height, width, components = struct.unpack(">BHHB", data[i+2:i+8])
            return width, height, components
        elif marker in (0xd9, 0xda): # EOI or SOS
            break
        else:
            length = struct.unpack(">H", data[i:i+2])[0]
            i += length
    raise ValueError("Could not find SOF marker in JPEG stream")

def create_pdf(image_path: str, output_path: str, a4: bool = False, title: str = "Image Document"):
    with open(image_path, "rb") as f:
        jpg_bytes = f.read()

    w_px, h_px, comps = get_jpeg_info(jpg_bytes)
    cs = "/DeviceRGB" if comps == 3 else "/DeviceGray"

    if a4:
        page_w = 595.28  # A4 width in pt
        page_h = 841.89  # A4 height in pt
        margin = 36.0    # 0.5 inch margin
        avail_w = page_w - (margin * 2)
        avail_h = page_h - (margin * 2)

        scale = min(avail_w / w_px, avail_h / h_px)
        img_w = w_px * scale
        img_h = h_px * scale
        img_x = (page_w - img_w) / 2.0
        img_y = (page_h - img_h) / 2.0
    else:
        page_w = float(w_px)
        page_h = float(h_px)
        img_w = float(w_px)
        img_h = float(h_px)
        img_x = 0.0
        img_y = 0.0

    out = bytearray()
    xref = []

    def add_obj(obj_bytes: bytes) -> int:
        offset = len(out)
        xref.append(offset)
        out.extend(f"{len(xref)} 0 obj\n".encode("ascii"))
        out.extend(obj_bytes)
        out.extend(b"\nendobj\n")
        return len(xref)

    out.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

    cat_id = 1
    pages_id = 2
    page_id = 3
    img_id = 4
    content_id = 5
    info_id = 6

    content_stream = f"q\n{img_w:.2f} 0 0 {img_h:.2f} {img_x:.2f} {img_y:.2f} cm\n/Im1 Do\nQ\n".encode("ascii")

    add_obj(f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode("ascii"))
    add_obj(f"<< /Type /Pages /Kids [ {page_id} 0 R ] /Count 1 >>".encode("ascii"))

    page_dict = (
        f"<< /Type /Page\n"
        f"   /Parent {pages_id} 0 R\n"
        f"   /MediaBox [ 0 0 {page_w:.2f} {page_h:.2f} ]\n"
        f"   /Contents {content_id} 0 R\n"
        f"   /Resources <<\n"
        f"      /ProcSet [ /PDF /ImageC ]\n"
        f"      /XObject << /Im1 {img_id} 0 R >>\n"
        f"   >>\n"
        f">>"
    ).encode("ascii")
    add_obj(page_dict)

    img_header = (
        f"<< /Type /XObject\n"
        f"   /Subtype /Image\n"
        f"   /Width {w_px}\n"
        f"   /Height {h_px}\n"
        f"   /ColorSpace {cs}\n"
        f"   /BitsPerComponent 8\n"
        f"   /Filter /DCTDecode\n"
        f"   /Length {len(jpg_bytes)}\n"
        f">>\nstream\n"
    ).encode("ascii")
    add_obj(img_header + jpg_bytes + b"\nendstream")

    content_obj = (
        f"<< /Length {len(content_stream)} >>\nstream\n"
    ).encode("ascii") + content_stream + b"\nendstream"
    add_obj(content_obj)

    safe_title = title.replace("(", "[").replace(")", "]")
    info_dict = (
        f"<< /Title ({safe_title})\n"
        f"   /Producer (Hermes Zero-Dep Image2PDF)\n"
        f">>"
    ).encode("ascii")
    add_obj(info_dict)

    xref_offset = len(out)
    out.extend(b"xref\n")
    out.extend(f"0 {len(xref) + 1}\n".encode("ascii"))
    out.extend(b"0000000000 65535 f \n")
    for offset in xref:
        out.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

    out.extend(
        f"trailer\n<< /Size {len(xref) + 1} /Root {cat_id} 0 R /Info {info_id} 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )

    with open(output_path, "wb") as f:
        f.write(out)

    return os.path.getsize(output_path)

def main():
    parser = argparse.ArgumentParser(description="Zero-dependency lossless JPEG to PDF converter")
    parser.add_argument("image", help="Input JPEG image path")
    parser.add_argument("-o", "--output", required=True, help="Output PDF file path")
    parser.add_argument("--a4", action="store_true", help="Fit and center image inside standard A4 page (for printing)")
    parser.add_argument("--title", default="Document", help="Document title metadata")

    args = parser.parse_args()
    if not os.path.isfile(args.image):
        print(f"Error: Image '{args.image}' not found", file=sys.stderr)
        sys.exit(1)

    try:
        size = create_pdf(args.image, args.output, a4=args.a4, title=args.title)
        print(f'{{"success": true, "output": "{args.output}", "bytes": {size}}}')
    except Exception as e:
        print(f'{{"success": false, "error": "{str(e)}"}}', file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
