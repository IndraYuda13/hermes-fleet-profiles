#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

UPSTREAM = "https://raw.githubusercontent.com/JaimePolop/RExpository/main/regex.yaml"
SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "vendor", "dist", "build", "__pycache__",
    ".venv", "venv", "target", ".gradle", ".idea", ".cache", "coverage",
}
TEXT_EXT_HINTS = {
    ".txt", ".log", ".json", ".yaml", ".yml", ".xml", ".html", ".htm", ".js", ".mjs", ".cjs",
    ".ts", ".tsx", ".jsx", ".css", ".scss", ".java", ".kt", ".smali", ".py", ".go", ".rs", ".c",
    ".cpp", ".h", ".hpp", ".cs", ".php", ".rb", ".swift", ".m", ".mm", ".sh", ".bat", ".ps1",
    ".env", ".properties", ".conf", ".config", ".ini", ".toml", ".gradle", ".patch", ".diff",
}


def eprint(*args: Any) -> None:
    print(*args, file=sys.stderr)


def load_yaml(text: str) -> Any:
    try:
        import yaml  # type: ignore
    except Exception as exc:
        raise SystemExit("PyYAML is required. Install python3-yaml or run inside an env with pyyaml.") from exc
    return yaml.safe_load(text)


def cache_path() -> Path:
    base = Path(os.environ.get("OPENCLAW_WORKSPACE", str(Path.home() / ".openclaw" / "workspace")))
    return base / ".cache" / "rexpository" / "regex.yaml"


def get_catalog(path: str | None, refresh: bool) -> Path:
    if path:
        return Path(path)
    out = cache_path()
    if refresh or not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(UPSTREAM, headers={"User-Agent": "openclaw-rex-scan/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            out.write_bytes(r.read())
    return out


def is_binary_sample(data: bytes) -> bool:
    if b"\x00" in data[:4096]:
        return True
    if not data:
        return False
    sample = data[:4096]
    weird = sum(1 for b in sample if b < 9 or (13 < b < 32))
    return weird / max(1, len(sample)) > 0.20


def iter_files(root: Path, max_size: int) -> list[Path]:
    if root.is_file():
        return [root]
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            p = Path(dirpath) / name
            try:
                if p.stat().st_size > max_size:
                    continue
            except OSError:
                continue
            out.append(p)
    return out


def mask_value(value: str) -> str:
    clean = value.replace("\n", "\\n")
    if len(clean) <= 12:
        return clean[:3] + "…" + clean[-2:]
    return clean[:8] + "…" + clean[-6:]


def line_col(text: str, start: int) -> tuple[int, int]:
    line = text.count("\n", 0, start) + 1
    last = text.rfind("\n", 0, start)
    col = start + 1 if last < 0 else start - last
    return line, col


@dataclass
class Pattern:
    category: str
    name: str
    regex: str
    false_positive: bool
    flags: int


def compile_patterns(catalog: dict[str, Any], include_fp: bool, categories: set[str] | None) -> tuple[list[tuple[Pattern, re.Pattern[str]]], list[dict[str, str]]]:
    compiled: list[tuple[Pattern, re.Pattern[str]]] = []
    errors: list[dict[str, str]] = []
    for cat in catalog.get("regular_expresions", []) or []:
        cname = str(cat.get("name") or "uncategorized")
        if categories and cname.lower() not in categories:
            continue
        for item in cat.get("regexes", []) or []:
            fp = bool(item.get("falsePositives") is True or str(item.get("falsePositives", "")).lower() == "true")
            if fp and not include_fp:
                continue
            flags = re.IGNORECASE if bool(item.get("caseinsensitive")) else 0
            raw = str(item.get("regex") or "").replace("\n", "")
            pat = Pattern(cname, str(item.get("name") or "unnamed"), raw, fp, flags)
            try:
                compiled.append((pat, re.compile(raw, flags)))
            except Exception as exc:
                errors.append({"category": cname, "name": pat.name, "error": str(exc), "regex": raw})
    return compiled, errors


def scan_file(path: Path, patterns: list[tuple[Pattern, re.Pattern[str]]], root: Path, max_matches_per_file: int, show_secrets: bool) -> list[dict[str, Any]]:
    try:
        data = path.read_bytes()
    except OSError:
        return []
    if is_binary_sample(data):
        return []
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("latin-1", errors="ignore")
    rel = str(path.relative_to(root)) if root.is_dir() else str(path)
    hits: list[dict[str, Any]] = []
    for pat, rx in patterns:
        for m in rx.finditer(text):
            val = m.group(0)
            if not val:
                continue
            ln, col = line_col(text, m.start())
            sha = hashlib.sha256(val.encode("utf-8", "ignore")).hexdigest()[:16]
            hits.append({
                "file": rel,
                "line": ln,
                "col": col,
                "category": pat.category,
                "pattern": pat.name,
                "false_positive_marked": pat.false_positive,
                "match": val if show_secrets else mask_value(val),
                "match_sha256_16": sha,
            })
            if len(hits) >= max_matches_per_file:
                return hits
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description="Scan files with the RExpository regex catalog")
    ap.add_argument("target", help="file or directory to scan")
    ap.add_argument("--catalog", help="path to regex.yaml; defaults to cached upstream RExpository")
    ap.add_argument("--refresh", action="store_true", help="refresh cached upstream catalog")
    ap.add_argument("--include-fp", action="store_true", help="include patterns marked as false-positive prone")
    ap.add_argument("--category", action="append", help="restrict to category name; can repeat")
    ap.add_argument("--max-file-size", type=int, default=2_000_000)
    ap.add_argument("--max-matches-per-file", type=int, default=200)
    ap.add_argument("--show-secrets", action="store_true", help="print raw matched values instead of masked values")
    ap.add_argument("--json-out", help="write full JSON results to this file")
    ap.add_argument("--summary", action="store_true", help="print compact summary")
    args = ap.parse_args()

    target = Path(args.target).resolve()
    if not target.exists():
        raise SystemExit(f"target not found: {target}")
    cat_path = get_catalog(args.catalog, args.refresh)
    catalog = load_yaml(cat_path.read_text())
    cats = {c.lower() for c in args.category} if args.category else None
    patterns, errors = compile_patterns(catalog, args.include_fp, cats)
    root = target if target.is_dir() else target.parent
    files = iter_files(target, args.max_file_size)
    hits: list[dict[str, Any]] = []
    for p in files:
        hits.extend(scan_file(p, patterns, root, args.max_matches_per_file, args.show_secrets))
    summary: dict[str, Any] = {
        "target": str(target),
        "catalog": str(cat_path),
        "files_scanned": len(files),
        "patterns_loaded": len(patterns),
        "compile_errors": errors,
        "hit_count": len(hits),
        "by_category": {},
        "by_pattern": {},
    }
    for h in hits:
        summary["by_category"][h["category"]] = summary["by_category"].get(h["category"], 0) + 1
        key = f"{h['category']}::{h['pattern']}"
        summary["by_pattern"][key] = summary["by_pattern"].get(key, 0) + 1
    result = {"summary": summary, "hits": hits}
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    if args.summary or not args.json_out:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        for h in hits[:50]:
            print(f"{h['file']}:{h['line']}:{h['col']} [{h['category']} / {h['pattern']}] {h['match']}")
        if len(hits) > 50:
            print(f"... {len(hits) - 50} more hits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
