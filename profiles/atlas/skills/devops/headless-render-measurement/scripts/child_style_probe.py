#!/usr/bin/env python3
"""Per-child computed-style + Escape/line-box audit for one container.

Answers, from live DOM numbers: does a named child escape its parent's box, how
far per side, does its text wrap to 2 lines, and what are the child's OWN
computed style values (font-size, line-height, white-space, font-weight).

Why this is a separate script: a per-child metric read from a style object
captured on the PARENT reports the parent's font-size, which makes the probe
look like it refutes a per-child change the requester reported. Every value here
comes from getComputedStyle(child) for that child.

Usage:
    child_style_probe.py OUT.json --root /path/to/mockups --file direction-C.html \
        --parent ".kartu.unggulan" --children ".f,.a" \
        --row-sel ".kartu.unggulan .price" \
        --viewport 390x844 --viewport 1440x900

OUT receives one JSON report; stdout gets a compact summary only (a multi-KB
pretty-printed report tail-truncated in a terminal drops the first block).
Inputs are opened read-only.
"""

import argparse
import glob
import json
import os
import sys
from pathlib import Path

AUDIT = r"""
([parentSel, childSels, rowSel]) => {
  const R = n => +n.toFixed(2);
  const root = document.querySelector(parentSel);
  if (!root) return { parentSel, found: false };
  const rr = root.getBoundingClientRect();
  const rcs = getComputedStyle(root);

  const box = el => {
    const r = el.getBoundingClientRect();
    // own computed style of THIS element, never an ancestor's
    const cs = getComputedStyle(el);
    const rg = document.createRange();
    rg.selectNodeContents(el);
    const lines = Array.from(rg.getClientRects()).filter(x => x.width > 0.5 && x.height > 0.5);
    return {
      tag: el.tagName, cls: (el.className || '').toString(),
      text: (el.textContent || '').trim().slice(0, 40),
      rect: { top: R(r.top), bottom: R(r.bottom), left: R(r.left), right: R(r.right),
              w: R(r.width), h: R(r.height) },
      escape: { left: R(Math.max(0, rr.left - r.left)), right: R(Math.max(0, r.right - rr.right)),
                top: R(Math.max(0, rr.top - r.top)), bottom: R(Math.max(0, r.bottom - rr.bottom)) },
      style: { fontSize: cs.fontSize, fontWeight: cs.fontWeight, lineHeight: cs.lineHeight,
               whiteSpace: cs.whiteSpace, display: cs.display, overflowX: cs.overflowX },
      lineCount: lines.length,
      lineBoxes: lines.map(x => [R(x.top), R(x.bottom), R(x.left), R(x.right)]),
      selfScroll: { scrollW: el.scrollWidth, clientW: el.clientWidth,
                    clippedX: el.scrollWidth > el.clientWidth + 1 }
    };
  };

  const children = childSels.map(s => {
    const el = root.querySelector(s);
    return el ? Object.assign({ sel: s }, box(el)) : { sel: s, found: false };
  });

  const rowEl = rowSel ? document.querySelector(rowSel) : null;
  const row = rowEl ? (() => { const cs = getComputedStyle(rowEl); const r = rowEl.getBoundingClientRect();
    return { sel: rowSel, rect: { top: R(r.top), bottom: R(r.bottom), left: R(r.left), right: R(r.right),
              w: R(r.width), h: R(r.height) },
      style: { display: cs.display, justifyContent: cs.justifyContent, alignItems: cs.alignItems,
               gap: cs.gap, whiteSpace: cs.whiteSpace, flexWrap: cs.flexWrap,
               gridColumn: cs.gridColumnStart + ' / ' + cs.gridColumnEnd },
      scrollW: rowEl.scrollWidth, clientW: rowEl.clientWidth,
      selfOverflow: rowEl.scrollWidth > rowEl.clientWidth + 0.5,
      rightOfViewport: R(Math.max(0, r.right - window.innerWidth)) }; })() : null;

  // descendant escape census: named children can be clean while a deeper node escapes
  const escapes = Array.from(root.querySelectorAll('*')).filter(el => {
    const r = el.getBoundingClientRect();
    return r.width > 0 && (r.right > rr.right + 0.5 || r.left < rr.left - 0.5 ||
                           r.bottom > rr.bottom + 0.5 || r.top < rr.top - 0.5);
  }).map(el => box(el));

  // sibling-only overlap: a parent always intersects its children, so containment
  // is structural and only non-nested intersections are collisions
  const nodes = Array.from(root.querySelectorAll('*'));
  const sibCollisions = [];
  for (let i = 0; i < nodes.length; i++) for (let j = i + 1; j < nodes.length; j++) {
    const a = nodes[i], b = nodes[j];
    const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
    if (ra.width <= 0 || rb.width <= 0) continue;
    if (ra.bottom <= rb.top + 0.5 || ra.top >= rb.bottom - 0.5 ||
        ra.right <= rb.left + 0.5 || ra.left >= rb.right - 0.5) continue;
    if (a.contains(b) || b.contains(a)) continue;
    sibCollisions.push([(a.className || a.tagName).toString(), (b.className || b.tagName).toString()]);
  }

  const found = children.filter(c => c.found !== false);
  return {
    parentSel, found: true,
    viewport: { w: window.innerWidth, h: window.innerHeight },
    parent: { cls: (root.className || '').toString(),
              rect: { top: R(rr.top), bottom: R(rr.bottom), left: R(rr.left), right: R(rr.right),
                      w: R(rr.width), h: R(rr.height) },
              style: { display: rcs.display, gridTemplateColumns: rcs.gridTemplateColumns,
                       padding: rcs.padding } },
    children: children, row: row,
    descendantEscapes: escapes, siblingCollisions: sibCollisions, nodeCount: nodes.length,
    anyChildEscape: found.some(c =>
      Math.max(c.escape.left, c.escape.right, c.escape.top, c.escape.bottom) > 0.5),
    anyTwoLine: found.some(c => c.lineCount > 1)
  };
}
"""


def chrome_path():
    for c in ("/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
              "/usr/bin/chromium", "/usr/bin/chromium-browser"):
        if os.path.exists(c):
            return c
    for pat in ("~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome",
                "~/.cache/ms-playwright/chromium-*/chrome-linux/chrome"):
        hits = sorted(glob.glob(os.path.expanduser(pat)))
        if hits:
            return hits[-1]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--file", required=True)
    ap.add_argument("--root", default=".")
    ap.add_argument("--parent", required=True, help="container selector")
    ap.add_argument("--children", required=True, help="comma-separated, relative to parent")
    ap.add_argument("--row-sel", default=None, help="full selector for the parent row of interest")
    ap.add_argument("--viewport", action="append", default=[], help="WxH, repeatable")
    ap.add_argument("--emulate-mobile", action="store_true",
                    help="is_mobile/has_touch on viewports with width <= 500")
    ap.add_argument("--executable", default=None)
    args = ap.parse_args()

    exe = args.executable or chrome_path()
    if not exe:
        sys.exit("no Chrome/Chromium found; pass --executable")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("playwright not importable for this interpreter "
                 f"({sys.executable}); try /usr/bin/python3 explicitly")

    vps = args.viewport or ["390x844", "1440x900"]
    child_sels = [s.strip() for s in args.children.split(",") if s.strip()]
    url = (Path(args.root).expanduser().resolve() / args.file).as_uri()
    report = {"interpreter": sys.executable, "chrome": exe, "file": args.file,
              "parent": args.parent, "children": child_sels, "by_viewport": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=exe, args=[
            "--no-sandbox", "--disable-dev-shm-usage", "--force-device-scale-factor=1"])
        for spec in vps:
            w, h = (int(x) for x in spec.lower().split("x"))
            mobile = args.emulate_mobile and w <= 500
            ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=2 if mobile else 1,
                                      is_mobile=mobile, has_touch=mobile)
            pg = ctx.new_page()
            pg.goto(url, wait_until="load")
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(500)
            report["by_viewport"][spec] = pg.evaluate(AUDIT, [args.parent, child_sels, args.row_sel])
            ctx.close()
        browser.close()

    Path(args.out).write_text(json.dumps(report, indent=1))
    for spec, d in report["by_viewport"].items():
        if not d.get("found"):
            print(f"{spec}: parent {args.parent} NOT FOUND")
            continue
        print(f"{spec}: parent {d['parent']['rect']['w']}x{d['parent']['rect']['h']} "
              f"anyChildEscape={d['anyChildEscape']} anyTwoLine={d['anyTwoLine']} "
              f"descendantEscapes={len(d['descendantEscapes'])} "
              f"siblingCollisions={len(d['siblingCollisions'])}")
        for c in d["children"]:
            if c.get("found") is False:
                print(f"    {c['sel']:<8} NOT FOUND")
                continue
            e = c["escape"]
            print(f"    {c['sel']:<8} {c['style']['fontSize']:>6} lines={c['lineCount']} "
                  f"escape L{e['left']} R{e['right']} T{e['top']} B{e['bottom']} "
                  f"rect=({c['rect']['top']},{c['rect']['bottom']},{c['rect']['left']},{c['rect']['right']})")
        if d.get("row"):
            print(f"    row gridColumn={d['row']['style']['gridColumn']} "
                  f"justify={d['row']['style']['justifyContent']} "
                  f"selfOverflow={d['row']['selfOverflow']}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
