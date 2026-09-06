#!/usr/bin/env python3
"""
Utility script to convert Bstation / Bilibili ASS/SSA subtitles to standard WebVTT (RFC 8216).
"""
import re
import sys

def ass_timestamp_to_vtt(ts: str) -> str:
    """
    Convert ASS timestamp (h:mm:ss.cs) to WebVTT timestamp (hh:mm:ss.mmm).
    """
    m = re.match(r"(\d+):(\d{2}):(\d{2})\.(\d{2,3})", ts.strip())
    if not m:
        return ts
    h, mn, s, cs = m.groups()
    ms = cs.ljust(3, "0")[:3]
    return f"{int(h):02d}:{mn}:{s}.{ms}"

def ass_to_webvtt(ass_text: str) -> str:
    """
    Parse ASS/SSA dialogue lines and produce a valid WebVTT string.
    """
    vtt_lines = ["WEBVTT", ""]
    for line in ass_text.splitlines():
        if not line.startswith("Dialogue:"):
            continue
        
        # ASS Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
        parts = line.split(",", 9)
        if len(parts) < 10:
            continue
            
        start_raw = parts[1]
        end_raw = parts[2]
        text_raw = parts[9]
        
        start_vtt = ass_timestamp_to_vtt(start_raw)
        end_vtt = ass_timestamp_to_vtt(end_raw)
        
        # Clean formatting tags like {\b1}, {\pos(x,y)}, etc.
        clean_text = re.sub(r"\{.*?\}", "", text_raw)
        # Convert literal newlines
        clean_text = clean_text.replace(r"\N", "\n").replace(r"\n", "\n").strip()
        
        if clean_text:
            vtt_lines.append(f"{start_vtt} --> {end_vtt}")
            vtt_lines.append(clean_text)
            vtt_lines.append("")
            
    return "\n".join(vtt_lines)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    else:
        content = sys.stdin.read()
    
    print(ass_to_webvtt(content))
