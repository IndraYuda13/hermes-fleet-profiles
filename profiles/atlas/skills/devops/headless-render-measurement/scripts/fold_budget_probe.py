#!/usr/bin/env python3
"""Fold-budget probe: rect metrics + ancestor-chain flow decomposition + closure check.

Usage:
  python3 fold_budget_probe.py <file.html> \
      [--sel .bar --sel .job --sel .job\ h1 ...] \
      [--vp 390x844 --vp 412x915 --vp 768x1024] \
      [--mobile-ua] [--json /tmp/fold_budget.json]

Prints, per viewport: document metrics (innerWidth/innerHeight/scrollWidth/
clientWidth/scrollHeight, horizontal overflow) then one row per selector with
rect.top, rect.height, computed marginTop, paddingTop+paddingBottom, the document
offset of its top, the decomposed chain sum and the RESIDUAL.

RESIDUAL MUST BE 0.00 for the number to be publishable. A nonzero residual means
the model is wrong for that selector -- a missing flex/grid `gap`, an ancestor's
own margin-top, a `position: absolute` sibling counted as flow, or a box counted
twice. Refine the chain (see references/dom-measurement-probes.md, "Fold budget")
until it closes, or report the selector as unresolved. Do not publish a column you
have not closed.

Read-only: launches its own Chrome, opens the file over file://, mutates nothing,
and writes only the optional --json path.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

CHROME_CANDIDATES = ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
                     "/usr/bin/chromium", "/usr/bin/chromium-browser"]
UA_MOBILE = ("Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 "
             "(KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36")

JS = r"""
(sels) => {
  const q = v => Math.round(v * 100) / 100;
  const absTop = el => { let t = 0, n = el;
    while (n) { t += n.scrollTop || 0; n = n.parentElement; } return t; };
  const chain = (el) => {
    const parts = []; let sum = 0, n = el, guard = 0;
    while (n && n.parentElement && guard++ < 60) {
      const p = n.parentElement, pc = getComputedStyle(p);
      const sibs = Array.from(p.children), idx = sibs.indexOf(n);
      for (const s of sibs.slice(0, idx)) {
        const sc = getComputedStyle(s);
        if (sc.display === 'none') continue;
        if (sc.position === 'absolute' || sc.position === 'fixed') continue;
        const sr = s.getBoundingClientRect();
        const add = sr.height + (parseFloat(sc.marginTop) || 0) + (parseFloat(sc.marginBottom) || 0);
        if (add) { sum += add; parts.push(((s.tagName) + '.' + ((s.className || '') + '').trim().split(' ')[0]) + ' +' + q(add)); }
      }
      const gap = parseFloat(pc.gap) || 0;
      if (gap && idx > 0) { sum += gap; parts.push(p.tagName + '[gap] +' + q(gap)); }
      const lead = (parseFloat(pc.paddingTop) || 0) + (parseFloat(pc.borderTopWidth) || 0);
      if (lead) { sum += lead; parts.push(p.tagName + '[padTop+border] +' + q(lead)); }
      n = p;
    }
    return { sum: q(sum), parts };
  };
  const seen = new Set();
  const rows = [];
  for (const raw of sels) {
    const els = Array.from(document.querySelectorAll(raw));
    const el = els.find(e => !seen.has(e));
    if (!el) { rows.push({ selector: raw, count: els.length, missing: true }); continue; }
    seen.add(el);
    const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
    const c = chain(el);
    const top = q(r.top + absTop(el));
    rows.push({
      selector: raw, count: els.length, tag: el.tagName,
      cls: ((el.className || '') + '').trim(),
      display: cs.display, visibility: cs.visibility,
      top: q(r.top), docTop: top, height: q(r.height), width: q(r.width),
      marginTop: q(parseFloat(cs.marginTop) || 0), marginBottom: q(parseFloat(cs.marginBottom) || 0),
      paddingTop: q(parseFloat(cs.paddingTop) || 0), paddingBottom: q(parseFloat(cs.paddingBottom) || 0),
      padSum: q((parseFloat(cs.paddingTop) || 0) + (parseFloat(cs.paddingBottom) || 0)),
      fontSize: cs.fontSize, lineHeight: cs.lineHeight,
      chainSum: c.sum, residual: q(top - c.sum), closes: Math.abs(top - c.sum) <= 0.01,
      parts: c.parts,
    });
  }
  return { rows, doc: { innerWidth: innerWidth, innerHeight: innerHeight,
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
    scrollHeight: document.documentElement.scrollHeight,
    horizontalOverflow: document.documentElement.scrollWidth > innerWidth,
    overflowPx: document.documentElement.scrollWidth - innerWidth } };
}
"""


def find_chrome():
    for c in CHROME_CANDIDATES:
        if Path(c).exists():
            return c
    return None


def parse_vp(s):
    w, h = s.lower().split("x")
    return int(w), int(h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--sel", action="append", default=[])
    ap.add_argument("--vp", action="append", default=[])
    ap.add_argument("--mobile-ua", action="store_true")
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    f = Path(args.file)
    exe = find_chrome()
    if exe is None:
        sys.exit("no Chrome found; pass nothing -- install one or use cdp_measure.mjs")
    sels = args.sel or ["body *"]
    vps = [parse_vp(v) for v in (args.vp or ["390x844"])]

    before = hashlib.sha256(f.read_bytes()).hexdigest()
    rep = {"file": str(f), "sha256_before": before, "chrome": exe, "results": {}}
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=exe, args=[
            "--no-sandbox", "--disable-dev-shm-usage", "--force-device-scale-factor=1"])
        for w, h in vps:
            kw = dict(viewport={"width": w, "height": h}, device_scale_factor=1)
            if args.mobile_ua:
                kw.update(is_mobile=True, has_touch=True, user_agent=UA_MOBILE)
            ctx = b.new_context(**kw)
            pg = ctx.new_page()
            pg.goto(f.as_uri(), wait_until="load")
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(400)
            rep["results"][f"{w}x{h}"] = pg.evaluate(JS, sels)
            ctx.close()
        b.close()
    after = hashlib.sha256(f.read_bytes()).hexdigest()
    rep["sha256_after"] = after
    rep["readonly_ok"] = before == after

    for vp, r in rep["results"].items():
        d = r["doc"]
        print(f"\n=== {vp}  innerW={d['innerWidth']} innerH={d['innerHeight']} "
              f"scrollW={d['scrollWidth']} clientW={d['clientWidth']} "
              f"hOverflow={d['horizontalOverflow']} overflowPx={d['overflowPx']} "
              f"scrollH={d['scrollHeight']}")
        print(f"{'selector':32s} {'top':>9} {'height':>8} {'mt':>6} {'padSum':>7} "
              f"{'docTop':>9} {'chainSum':>9} {'resid':>7} display")
        for row in r["rows"]:
            if row.get("missing"):
                print(f"{row['selector']:32s} count=0 (no match in DOM)")
                continue
            print(f"{row['selector']:32s} {row['top']:>9} {row['height']:>8} "
                  f"{row['marginTop']:>6} {row['padSum']:>7} {row['docTop']:>9} "
                  f"{row['chainSum']:>9} {row['residual']:>7} {row['display']}"
                  f"{'   <-- DOES NOT CLOSE: refine addends' if not row['closes'] else ''}")
            if row["parts"]:
                print("      addends: " + " | ".join(row["parts"]))

    print(f"\nreadonly_ok={rep['readonly_ok']}  sha256={before}")
    if args.json:
        Path(args.json).write_text(json.dumps(rep, indent=1))
        print("wrote", args.json)


if __name__ == "__main__":
    main()
