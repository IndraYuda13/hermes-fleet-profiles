#!/usr/bin/env python3
"""Read-only DOM geometry probe for HTML artefacts.

Emits ONE JSON report per job: per-viewport fold buckets and first-element
rects, document-level horizontal overflow WITH per-element containment
analysis, a census of every fixed/sticky element plus its occlusion of the
product set, and an optional parent/child rect + overlap audit.

Usage:
    geometry_probe.py OUT.json --root /path/to/mockups \
        "A=direction-A.html::.row:has(.buy)::.bar" \
        "B=direction-B.html::[data-testid=service-tile]::.sess" \
        "C=direction-C.html::.kartu::.actionbar" \
        --redundant "A=.row" \
        --child-audit "C=.kartu.unggulan::.badge-unggul,.top,.price,.pilih" \
        --gate-ratio 0.60 --min-visible 2

Case spec:      NAME=FILE::SELECTOR::BAR      (BAR optional)
--redundant:    NAME=SELECTOR
--child-audit:  NAME=PARENT::CHILD1,CHILD2,...

Splitting is on '::' so ':has(' and other single-colon pseudo-classes are safe
inside the selector.

Writes JSON to OUT -- never to stdout, because a multi-KB pretty-printed report
tail-truncated in a terminal silently drops the first artefact's block. Prints
only a compact summary to stdout. Inputs are opened read-only; nothing on the
host is installed or modified.
"""

import argparse
import glob
import json
import os
import sys
from pathlib import Path

PROBE = r"""
([sel, barSel]) => {
  const de = document.documentElement;
  const vh = window.innerHeight, vw = window.innerWidth;
  const out = {
    scrollWidth: de.scrollWidth, innerWidth: vw, clientWidth: de.clientWidth,
    scrollHeight: de.scrollHeight, innerHeight: vh, bodyScrollWidth: document.body.scrollWidth,
  };
  out.horizontalOverflow = de.scrollWidth > vw;
  out.overflowPx = de.scrollWidth - vw;
  const els = Array.from(document.querySelectorAll(sel));
  const boxes = els.map((el, i) => {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return { i, top: +r.top.toFixed(2), bottom: +r.bottom.toFixed(2),
      left: +r.left.toFixed(2), right: +r.right.toFixed(2),
      h: +r.height.toFixed(2), w: +r.width.toFixed(2),
      display: cs.display, visibility: cs.visibility, opacity: cs.opacity,
      offsetParentNull: el.offsetParent === null, clientRects: el.getClientRects().length };
  });
  out.selector = sel; out.count = els.length;
  out.firstTop = boxes.length ? boxes[0].top : null;
  out.firstBottom = boxes.length ? boxes[0].bottom : null;
  out.firstBox = boxes.length ? boxes[0] : null;
  out.fullyVisibleTopZero = boxes.filter(b => b.top >= 0 && b.bottom <= vh).length;
  out.fullyVisibleSkillDefault = boxes.filter(b => b.top < vh && b.bottom <= vh).length;
  out.partial = boxes.filter(b => b.top < vh && b.bottom > vh).length;
  out.belowFold = boxes.filter(b => b.top >= vh).length;
  out.anyRightBeyondViewport = boxes.filter(b => b.right > vw + 0.5).length;
  out.distinctPositions = new Set(boxes.map(b =>
    `${Math.round(b.top)}|${Math.round(b.bottom)}|${Math.round(b.left)}`)).size;
  out.renderedCount = boxes.filter(b => b.display !== 'none' && b.visibility !== 'hidden'
      && parseFloat(b.opacity) > 0 && !b.offsetParentNull && b.clientRects > 0).length;
  // Census EVERY fixed/sticky element: the decisive occluder is often one the
  // requester never named.
  out.fixedBars = Array.from(document.querySelectorAll('*')).filter(el => {
    const cs = getComputedStyle(el);
    return cs.position === 'fixed' || cs.position === 'sticky';
  }).map(el => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
    return { tag: el.tagName, cls: (el.className || '').toString().slice(0, 60),
      position: cs.position, top: +r.top.toFixed(2), bottom: +r.bottom.toFixed(2),
      left: +r.left.toFixed(2), right: +r.right.toFixed(2), h: +r.height.toFixed(2),
      zIndex: cs.zIndex };
  });
  out.bar = null; out.barOverlapIdx = [];
  if (barSel) {
    const be = document.querySelector(barSel);
    if (be) { const br = be.getBoundingClientRect(); const bcs = getComputedStyle(be);
      out.bar = { sel: barSel, top: +br.top.toFixed(2), bottom: +br.bottom.toFixed(2),
        left: +br.left.toFixed(2), right: +br.right.toFixed(2), h: +br.height.toFixed(2),
        position: bcs.position, zIndex: bcs.zIndex };
      // Both axes: the vertical-band test is only valid for a full-width bar.
      out.barOverlapIdx = boxes.filter(b =>
        !(b.bottom <= out.bar.top || b.top >= out.bar.bottom ||
          b.right <= out.bar.left || b.left >= out.bar.right)).map(b => b.i);
      out.foldVisibleThenOccluded = boxes.filter(b => b.top >= 0 && b.bottom <= vh)
        .filter(b => out.barOverlapIdx.indexOf(b.i) !== -1).map(b => b.i);
    } else { out.bar = { sel: barSel, found: false }; }
  }
  out.boxes = boxes;
  return out;
}
"""

# Per-element offenders are not page overflow: a rail / chip strip / segmented
# control with overflow-x:auto holds children past the edge by design.
CONTAINMENT = r"""
() => {
  const vw = window.innerWidth;
  const offenders = [];
  document.querySelectorAll('body *').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.right <= vw + 0.5) return;
    let scroller = null, p = el.parentElement, hops = 0;
    while (p && p !== document.body && hops++ < 12) {
      const cs = getComputedStyle(p);
      if (cs.overflowX !== 'visible' || cs.overflow !== 'visible') {
        scroller = { tag: p.tagName, cls: (p.className || '').toString().slice(0, 40),
                     overflowX: cs.overflowX };
        break;
      }
      p = p.parentElement;
    }
    offenders.push({ tag: el.tagName, cls: (el.className || '').toString().slice(0, 40),
      left: +r.left.toFixed(2), right: +r.right.toFixed(2),
      containedBy: scroller, pageOverflow: scroller === null });
  });
  return { innerWidth: vw, scrollWidth: document.documentElement.scrollWidth,
    horizontalOverflow: document.documentElement.scrollWidth > vw,
    offenderCount: offenders.length,
    pageOverflowCount: offenders.filter(o => o.pageOverflow).length,
    offenders: offenders.slice(0, 40) };
}
"""

CHILD = r"""
([parentSel, childSels]) => {
  const root = document.querySelector(parentSel);
  if (!root) return { parentSel, found: false };
  const rec = el => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
    return { cls: (el.className || '').toString().slice(0, 50),
      top: +r.top.toFixed(2), bottom: +r.bottom.toFixed(2),
      left: +r.left.toFixed(2), right: +r.right.toFixed(2),
      w: +r.width.toFixed(2), h: +r.height.toFixed(2),
      display: cs.display, position: cs.position,
      overflowsViewportRight: r.right > window.innerWidth + 0.5 };
  };
  const rr = root.getBoundingClientRect();
  const children = {};
  childSels.forEach(s => { const e = root.querySelector(s); children[s] = e ? rec(e) : null; });
  const escapees = Array.from(root.querySelectorAll('*')).map(rec).filter(c =>
    c.right > rr.right + 0.5 || c.left < rr.left - 0.5 ||
    c.bottom > rr.bottom + 0.5 || c.top < rr.top - 0.5);
  const named = childSels.filter(s => children[s]);
  const overlaps = [];
  for (let i = 0; i < named.length; i++) for (let j = i + 1; j < named.length; j++) {
    const a = children[named[i]], b = children[named[j]];
    if (!(a.bottom <= b.top || a.top >= b.bottom || a.right <= b.left || a.left >= b.right))
      overlaps.push([named[i], named[j]]);
  }
  return { parentSel, found: true,
    viewport: { w: window.innerWidth, h: window.innerHeight },
    root: rec(root), children, escapees, overlaps,
    childOverflowsViewport: named.filter(s => children[s].overflowsViewportRight).length };
}
"""

MOBILE = {"width": 390, "height": 844}
DESKTOP = {"width": 1440, "height": 900}


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


def split_spec(spec, sep="::"):
    return [p.strip() for p in spec.split(sep)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("cases", nargs="+", help="NAME=FILE::SELECTOR::BAR")
    ap.add_argument("--root", default=".")
    ap.add_argument("--redundant", action="append", default=[], help="NAME=SELECTOR")
    ap.add_argument("--child-audit", action="append", default=[], help="NAME=PARENT::CHILD1,CHILD2")
    ap.add_argument("--gate-ratio", type=float, default=None,
                    help="pass if first .top / viewport height <= this")
    ap.add_argument("--min-visible", type=int, default=None,
                    help="pass if fully-visible (top>=0 and bottom<=vh) count >= this")
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

    cases = {}
    for spec in args.cases:
        name, rest = spec.split("=", 1)
        parts = split_spec(rest)
        cases[name.strip()] = {
            "file": parts[0],
            "selector": parts[1] if len(parts) > 1 else None,
            "bar": parts[2] if len(parts) > 2 else None,
        }
    redundant = dict(s.split("=", 1) for s in args.redundant)
    audits = {}
    for spec in args.child_audit:
        name, rest = spec.split("=", 1)
        parts = split_spec(rest)
        audits[name.strip()] = (parts[0], [s.strip() for s in parts[1].split(",")])

    root = Path(args.root).expanduser().resolve()
    report = {"interpreter": sys.executable, "chrome": exe, "root": str(root),
              "cases": {n: cases[n] for n in cases}, "results": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=exe, args=[
            "--no-sandbox", "--disable-dev-shm-usage", "--force-device-scale-factor=1"])
        for name, spec in cases.items():
            url = (root / spec["file"]).as_uri()
            sel, bar = spec["selector"], spec["bar"]
            entry = {"file": spec["file"], "selector": sel, "bar": bar}

            def load(ctx):
                pg = ctx.new_page()
                pg.goto(url, wait_until="load")
                pg.evaluate("document.fonts.ready")
                pg.wait_for_timeout(500)
                return pg

            # --- mobile emulated
            ctx = browser.new_context(viewport=MOBILE, device_scale_factor=2,
                                      is_mobile=True, has_touch=True)
            pg = load(ctx)
            m = pg.evaluate(PROBE, [sel, bar])
            entry["mobile"] = m
            entry["mobile_containment"] = pg.evaluate(CONTAINMENT)
            if name in redundant:
                entry["mobile_redundant"] = {"selector": redundant[name],
                                             "probe": pg.evaluate(PROBE, [redundant[name], bar])}
            if name in audits:
                psel, csel = audits[name]
                entry["mobile_child_audit"] = pg.evaluate(CHILD, [psel, csel])
            ctx.close()

            # --- mobile plain (no is_mobile, no hidden scrollbars) cross-check
            ctx = browser.new_context(viewport=MOBILE, device_scale_factor=1)
            pg = load(ctx)
            pl = pg.evaluate(PROBE, [sel, bar])
            entry["mobile_plain"] = {k: pl[k] for k in (
                "scrollWidth", "innerWidth", "clientWidth", "horizontalOverflow",
                "overflowPx", "count", "firstTop", "firstBottom", "fullyVisibleTopZero")}
            entry["mobile_plain"]["agrees_with_emulated"] = (
                pl["horizontalOverflow"] == m["horizontalOverflow"] and
                pl["scrollWidth"] == m["scrollWidth"])
            ctx.close()

            # --- desktop
            ctx = browser.new_context(viewport=DESKTOP, device_scale_factor=1)
            pg = load(ctx)
            entry["desktop"] = pg.evaluate(PROBE, [sel, bar])
            if name in audits:
                psel, csel = audits[name]
                entry["desktop_child_audit"] = pg.evaluate(CHILD, [psel, csel])
            ctx.close()

            # --- gate verdict, computed from the requester's own predicate
            if args.gate_ratio is not None or args.min_visible is not None:
                vh = m["innerHeight"]
                ratio = None if m["firstTop"] is None else m["firstTop"] / vh
                ratio_ok = (args.gate_ratio is None or
                            (ratio is not None and ratio <= args.gate_ratio))
                count_ok = (args.min_visible is None or
                            m["fullyVisibleTopZero"] >= args.min_visible)
                entry["gate"] = {
                    "ratio_limit": args.gate_ratio, "min_visible": args.min_visible,
                    "first_top_ratio": None if ratio is None else round(ratio, 4),
                    "fully_visible": m["fullyVisibleTopZero"],
                    "pass": bool(ratio_ok and count_ok),
                    "occlusion_note": m.get("foldVisibleThenOccluded", []),
                }
            report["results"][name] = entry
        browser.close()

    Path(args.out).write_text(json.dumps(report, indent=1))
    for name, e in report["results"].items():
        m = e["mobile"]
        g = e.get("gate", {})
        cont = e["mobile_containment"]
        print(f"{name}: n={m['count']} first.top={m['firstTop']} first.bottom={m['firstBottom']} "
              f"hOv={m['horizontalOverflow']}({m['overflowPx']}) "
              f"fullyVis={m['fullyVisibleTopZero']} partial={m['partial']} below={m['belowFold']} "
              f"offenders={cont['offenderCount']}/page={cont['pageOverflowCount']} "
              f"bars={len(m['fixedBars'])}" + (f" pass={g['pass']}" if g else ""))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
