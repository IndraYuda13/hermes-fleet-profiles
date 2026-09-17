#!/usr/bin/env python3
"""Heuristic linter for Telkom FIF proposal text/Markdown.

This script is intentionally conservative: it emits warnings, not official grades.
It uses only the Python standard library.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def find_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text, flags=re.I | re.M) for p in patterns)


def bibliography_block(text: str) -> str:
    m = re.search(r"(?ims)^\s*(?:#+\s*)?(?:daftar\s+pustaka|references|referensi)\s*$", text)
    if not m:
        return ""
    return text[m.end():]


def count_numbered_refs(block: str) -> int:
    nums = re.findall(r"(?m)^\s*\[(\d+)\]\s+", block)
    return len(set(nums))


def extract_keywords(text: str) -> list[str] | None:
    m = re.search(r"(?im)^\s*(?:kata\s*kunci|keywords?)\s*[:\-]\s*(.+)$", text)
    if not m:
        return None
    line = m.group(1).strip()
    parts = [x.strip(" .") for x in re.split(r"[,;]", line) if x.strip(" .")]
    return parts


def main() -> int:
    ap = argparse.ArgumentParser(description="Heuristic proposal compliance linter")
    ap.add_argument("file", help="Plain text or Markdown proposal")
    ap.add_argument("--json", action="store_true", help="Emit JSON")
    args = ap.parse_args()

    path = Path(args.file)
    text = path.read_text(encoding="utf-8", errors="replace")
    low = normalize(text)

    checks: list[dict[str, str]] = []

    def add(level: str, code: str, message: str) -> None:
        checks.append({"level": level, "code": code, "message": message})

    required = {
        "abstract": [r"^\s*(?:#+\s*)?abstrak\b"],
        "background": [r"latar\s+belakang"],
        "problem": [r"perumusan\s+masalah", r"rumusan\s+masalah"],
        "objective": [r"^\s*(?:#+\s*)?(?:\d+(?:\.\d+)*\.?\s*)?tujuan\b"],
        "activity_plan": [r"rencana\s+kegiatan"],
        "schedule": [r"jadwal\s+kegiatan"],
        "literature_review": [r"kajian\s+pustaka", r"tinjauan\s+pustaka"],
        "design": [r"perancangan\s+sistem", r"alur\s+pemodelan"],
        "references": [r"daftar\s+pustaka", r"^\s*(?:#+\s*)?references\b"],
    }

    for code, patterns in required.items():
        if not find_any(text, patterns):
            add("BLOCKER" if code in {"problem", "objective", "literature_review", "design"} else "MAJOR",
                f"missing_{code}", f"Bagian yang diharapkan tidak terdeteksi: {code}.")

    if re.search(r"\b(?:saya|kami|kita)\b", low):
        add("MINOR", "first_person", "Terdeteksi kata ganti orang pertama (saya/kami/kita). Panduan baseline meminta menghindarinya pada naskah proposal, kecuali kutipan.")

    keywords = extract_keywords(text)
    if keywords is None:
        add("MAJOR", "keywords_missing", "Baris kata kunci/keywords tidak terdeteksi pada abstrak.")
    elif len(keywords) > 6:
        add("MAJOR", "keywords_over_6", f"Terdeteksi {len(keywords)} kata kunci; baseline resmi menyebut maksimum 6.")

    block = bibliography_block(text)
    if not block:
        add("MAJOR", "bibliography_missing", "Daftar pustaka tidak terdeteksi.")
    else:
        nrefs = count_numbered_refs(block)
        if nrefs and nrefs < 10:
            add("MAJOR", "references_under_10", f"Terdeteksi sekitar {nrefs} referensi bernomor; bagian proposal baseline menyebut minimum 10.")
        elif nrefs and nrefs < 20:
            add("INFO", "references_10_to_19", f"Terdeteksi sekitar {nrefs} referensi. Proposal-specific rule says >=10, tetapi tabel perbandingan S1 di panduan yang sama menyebut >=20; verifikasi aturan kelas/prodi saat ini.")
        elif nrefs == 0:
            add("INFO", "reference_count_unknown", "Format referensi bernomor [n] tidak terdeteksi, jadi jumlah referensi tidak bisa diaudit otomatis.")

        current_year = dt.date.today().year
        cutoff = current_year - 5
        years = [int(y) for y in re.findall(r"\b(19\d{2}|20\d{2})\b", block)]
        if years:
            recent = sum(1 for y in years if y >= cutoff)
            if recent == 0:
                add("MAJOR", "no_recent_years", f"Tidak ada tahun referensi >= {cutoff} yang terdeteksi. Baseline meminta referensi pembentuk gap berasal dari 5 tahun terakhir.")
            else:
                add("INFO", "recent_refs_present", f"Terdeteksi {recent} kemunculan tahun referensi >= {cutoff}; tetap cek manual bahwa sumber terbaru tersebut benar-benar menjadi basis gap.")

    numbered_cites = {int(x) for x in re.findall(r"\[(\d+)\]", text)}
    if block:
        bib_nums = {int(x) for x in re.findall(r"(?m)^\s*\[(\d+)\]\s+", block)}
        missing_in_bib = sorted(numbered_cites - bib_nums)
        if missing_in_bib:
            add("MAJOR", "citation_without_bib", f"Nomor sitasi ada di teks tetapi tidak terdeteksi sebagai entri daftar pustaka: {missing_in_bib[:20]}.")

    if "hipotesis" not in low:
        add("INFO", "hypothesis_optional_absent", "Bagian hipotesis tidak terdeteksi. Ini boleh karena baseline menandainya opsional; pastikan memang sesuai desain penelitian.")

    if args.json:
        print(json.dumps({"file": str(path), "findings": checks}, ensure_ascii=False, indent=2))
    else:
        print(f"Proposal lint: {path}")
        if not checks:
            print("No warnings detected by heuristic checks.")
        for item in checks:
            print(f"[{item['level']}] {item['code']}: {item['message']}")
        print("\nNote: heuristic lint only; not an official Telkom grade or compliance certification.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
