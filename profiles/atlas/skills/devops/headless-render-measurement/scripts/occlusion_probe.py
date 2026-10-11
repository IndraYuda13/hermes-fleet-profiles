#!/usr/bin/env python3
"""Read-only fixed/sticky bar occlusion probe for HTML artefacts.

Answers the three questions a fold-bucket probe cannot:

  1. rect band     - which product boxes intersect the bar band at all
  2. text coverage - which of those actually have TEXT ink under the bar
                     (padding/border tails overlap without hiding content)
  3. hit-test      - elementFromPoint at center + 4 inset corners, membership
                     resolved against the bar's SUBTREE (the topmost hit inside a
                     bar band is normally a label INSIDE the bar, so an
                     `el === bar` test falsely reports "not occluded")
  4. reachability  - after scrolling to the document bottom, does the last painted
                     content element clear the bar top?  A reserved padding-bottom
                     is reported but is not by itself proof.

Usage:
    occlusion_probe.py OUT.json --root /path/to/mockups \
        "B=direction-B.html::[data-testid=service-tile]::.sess" \
        "C=direction-C.html::.kartu::.actionbar" \
        --viewport 390x844 --dsf 2

Writes JSON to OUT, never stdout (a tailed multi-KB report drops the first
artefact). Inputs are opened read-only.
"""

import argparse
import glob
import json
import os
import sys
from pathlib import Path

SCROLL_TO_BOTTOM = "window.scrollTo(0, document.documentElement.scrollHeight)"

PROBE = r"""
([prodSel, barSel, wantReach]) => {
  const R = n => +n.toFixed(2);
  const de = document.documentElement;
  const vh = window.innerHeight, vw = window.innerWidth;
  const barEl = barSel ? document.querySelector(barSel) : null;
  const bar = barEl ? barEl.getBoundingClientRect() : null;
  const within = (root, el) => !!root && (root === el || root.contains(el));

  // Text leaves: no element children, non-empty trimmed text.
  const leaves = (root) => {
    const out = [];
    const walk = (n) => {
      for (const c of n.children) {
        const cs = getComputedStyle(c);
        if (cs.display === 'none' || cs.visibility === 'hidden') continue;
        if (c.children.length === 0) {
          const t = (c.textContent || '').trim();
          if (t) { const r = c.getBoundingClientRect();
            if (r.height > 0) out.push({ tag: c.tagName,
              cls: (c.className || '').toString().slice(0, 40), text: t.slice(0, 40),
              top: R(r.top), bottom: R(r.bottom) }); }
        } else walk(c);
      }
    };
    walk(root);
    return out;
  };

  const els = Array.from(document.querySelectorAll(prodSel));

  // 1 + 2 + 3: per-product rect band, text coverage, hit-test
  const rows = els.map((el, i) => {
    const r = el.getBoundingClientRect();
    const foldVisible = r.top >= 0 && r.bottom <= vh;
    const rectOverlapPx = bar ? R(Math.max(0,
      Math.min(r.bottom, bar.bottom) - Math.max(r.top, bar.top))) : 0;
    const lv = leaves(el);
    const under = bar ? lv.filter(l => !(l.bottom <= bar.top || l.top >= bar.bottom)) : [];

    let hit = null;
    if (bar) {
      const cx = (r.left + r.right) / 2, cy = (r.top + r.bottom) / 2;
      const ix = Math.min(12, r.width / 4), iy = Math.min(12, r.height / 4);
      const pts = [[cx, cy], [r.left + ix, r.top + iy], [r.right - ix, r.top + iy],
                   [r.left + ix, r.bottom - iy], [r.right - ix, r.bottom - iy]];
      const hits = pts.map(([x, y]) => {
        const inside = x >= 0 && x <= vw && y >= 0 && y <= vh;
        if (!inside) return { x: R(x), y: R(y), offscreen: true };
        const e = document.elementFromPoint(x, y);
        if (!e) return { x: R(x), y: R(y), tag: null, hitSelf: false, inBar: false };
        return { x: R(x), y: R(y), tag: e.tagName,
                 cls: (e.className || '').toString().slice(0, 40),
                 hitSelf: within(el, e), inBar: within(barEl, e) };
      });
      const valid = hits.filter(h => !h.offscreen).length;
      const selfHits = hits.filter(h => h.hitSelf).length;
      hit = { validPoints: valid, selfHits,
              occluded: valid > 0 && selfHits < valid,
              blockedBy: hits.filter(h => !h.offscreen && !h.hitSelf)
                             .map(h => `${h.tag}.${h.cls}`) };
    }

    return { i, top: R(r.top), bottom: R(r.bottom),
      left: R(r.left), right: R(r.right), foldVisible,
      rectOverlapPx, rectOverlaps: rectOverlapPx > 0,
      contentBottom: lv.length ? Math.max(...lv.map(l => l.bottom)) : null,
      textLeavesUnderBar: under.map(u => `${u.tag}.${u.cls}"${u.text}"@${u.top}-${u.bottom}`),
      hit };
  });

  const foldIdx = rows.filter(x => x.foldVisible).map(x => x.i);
  const out = {
    viewport: { w: vw, h: vh }, scrollY: Math.round(window.scrollY),
    scrollHeight: de.scrollHeight,
    bar: bar ? { sel: barSel, top: R(bar.top), bottom: R(bar.bottom), h: R(bar.height),
                 left: R(bar.left), right: R(bar.right),
                 position: getComputedStyle(barEl).position,
                 zIndex: getComputedStyle(barEl).zIndex,
                 background: getComputedStyle(barEl).backgroundColor } : null,
    count: els.length,
    rows,
    foldVisibleIdx: foldIdx,
    foldVisibleRectOverlap: rows.filter(x => x.foldVisible && x.rectOverlaps).map(x => x.i),
    foldVisibleContentCovered: rows.filter(x => x.foldVisible && x.textLeavesUnderBar.length > 0)
                                  .map(x => x.i),
    foldVisibleHitTestOccluded: rows.filter(x => x.foldVisible && x.hit && x.hit.occluded)
                                  .map(x => x.i),
  };

  // 4: end-of-scroll reachability (second pass, already scrolled to bottom)
  if (wantReach) {
    const walk = (el) => {
      let last = el;
      for (const c of el.children) {
        const cs = getComputedStyle(c);
        if (cs.position === 'fixed' || cs.display === 'none') continue;
        if (c.getBoundingClientRect().height > 0) last = walk(c);
      }
      return last;
    };
    const lastEl = walk(document.body);
    const lr = lastEl.getBoundingClientRect();
    out.reachability = {
      maxScrollY: de.scrollHeight - vh,
      bodyPaddingBottom: getComputedStyle(document.body).paddingBottom,
      lastContentTag: lastEl.tagName,
      lastContentTop: R(lr.top), lastContentBottom: R(lr.bottom),
      clearanceAboveBarTop: bar ? R(bar.top - lr.bottom) : null,
      tailReachable: bar ? (lr.bottom <= bar.top) : true,
    };
  }
  return out;
}
"""


def chrome_path():
    for c in ("/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
              "/usr/bin/chromium", "/usr/bin/chromium-browser"):
        if os.path.exists(c):
            return c
    for pat in ("~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome",):
        hits = sorted(glob.glob(os.path.expanduser(pat)))
        if hits:
            return hits[-1]
    return None


def parse_vp(s):
    w, h = s.lower().split("x")
    return {"width": int(w), "height": int(h)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("cases", nargs="+", help="NAME=FILE::PRODUCT_SEL::BAR_SEL")
    ap.add_argument("--root", default=".")
    ap.add_argument("--viewport", default="390x844")
    ap.add_argument("--dsf", type=int, default=2)
    ap.add_argument("--no-reachability", action="store_true")
    ap.add_argument("--executable", default=None)
    args = ap.parse_args()

    exe = args.executable or chrome_path()
    if not exe:
        sys.exit("no Chrome/Chromium found; pass --executable")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit(f"playwright not importable for {sys.executable}; try /usr/bin/python3")

    root = Path(args.root).expanduser().resolve()
    vp = parse_vp(args.viewport)
    report = {"interpreter": sys.executable, "chrome": exe,
              "viewport": vp, "dsf": args.dsf, "results": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=exe, args=[
            "--no-sandbox", "--disable-dev-shm-usage",
            "--force-device-scale-factor=1"])
        for spec in args.cases:
            name, rest = spec.split("=", 1)
            parts = [x.strip() for x in rest.split("::")]
            f, prod, bar = parts[0], parts[1], (parts[2] if len(parts) > 2 else None)
            url = (root / f).as_uri()
            ctx = browser.new_context(viewport=vp, device_scale_factor=args.dsf)
            pg = ctx.new_page()
            pg.goto(url, wait_until="load")
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(500)

            at_top = pg.evaluate(PROBE, [prod, bar, not args.no_reachability])
            at_bottom = None
            if not args.no_reachability:
                pg.evaluate(SCROLL_TO_BOTTOM)
                pg.wait_for_timeout(300)
                at_bottom = pg.evaluate(PROBE, [prod, bar, True])
            report["results"][name] = {"file": f, "product_selector": prod,
                                       "bar_selector": bar,
                                       "at_top": at_top, "at_bottom": at_bottom}
            ctx.close()
            rc = (at_bottom or {}).get("reachability", {})
            print(f"{name}: bar={at_top['bar']['top'] if at_top['bar'] else None}-"
                  f"{at_top['bar']['bottom'] if at_top['bar'] else None} "
                  f"foldVis={len(at_top['foldVisibleIdx'])} "
                  f"rectOverlap={at_top['foldVisibleRectOverlap']} "
                  f"contentCovered={at_top['foldVisibleContentCovered']} "
                  f"hitOccluded={at_top['foldVisibleHitTestOccluded']} "
                  f"tailReachable={rc.get('tailReachable')}")
        browser.close()

    Path(args.out).write_text(json.dumps(report, indent=1))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
