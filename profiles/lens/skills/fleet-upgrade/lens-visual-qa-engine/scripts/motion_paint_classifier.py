#!/usr/bin/env python3
"""Motion frame classifier: record a node's short lifecycle via in-page rAF and
classify each frame as PRE-OPEN (hidden) vs PAINTED, then report the mid-flight
count under BOTH the naive predicate (computed transform != settled) and the
corrected one (painted-only).

WHY: a node carrying [hidden] is display:none, so getComputedStyle reports
`transform: none`, which differs from the settled pose and is miscounted as
mid-flight. A recorder that starts before the trigger captures those hidden
frames, so a counter that should read 0 under reduced motion reads N and fails a
`no_intermediate_pose_held` assert on a correct artifact -- deterministically,
in every repeat (probe mis-calibration, not a defect, not a flake).

Run:  PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright \
        <python-with-playwright> motion_paint_classifier.py

Resolve the interpreter that actually imports playwright (see SKILL.md §7
bootstrap); do not pip-install one just for this.
Edit URL / NODE_SEL / TRIGGER_SEL / VIEWPORT below for the surface under test.
Prints JSON: per-repetition {naive_midflight, corrected_painted_midflight,
preopen_hidden_frames, first_painted_frame}. A corrected value of 0 with a
nonzero naive value is the mis-calibration, proven.
"""
import os
import glob
import json

# --- configure -------------------------------------------------------------
URL = "file://" + os.path.expanduser("~/path/to/prototype.html")
NODE_SEL = "#countrySheet"          # node whose lifecycle you are recording
TRIGGER_SEL = "#pSheet"             # selector whose click starts the transition
VIEWPORT = (1280, 800)
REDUCED = True                      # emulate prefers-reduced-motion: reduce
REPEATS = 3
# ---------------------------------------------------------------------------

LOGGER = """() => {
  window.__mLog = [];
  const tick = () => {
    const n = document.querySelector(%(sel)s);
    const c = n ? getComputedStyle(n) : null;
    window.__mLog.push({
      t: Math.round(performance.now()),
      cls: n ? n.className : null,
      transform: c ? c.transform : null,
      opacity: c ? c.opacity : null,
      open: !!n && n.classList.contains('is-open'),
      // PAINTED is the gate: a [hidden] node has no client rects and is
      // display:none, so its computed transform is a rest value, not travel.
      painted: !!n && n.getClientRects().length > 0 && !n.hasAttribute('hidden')
    });
    window.__mRaf = requestAnimationFrame(tick);
  };
  window.__mRaf = requestAnimationFrame(tick);
}"""


def find_chrome():
    hits = glob.glob("/root/.cache/ms-playwright/chromium*/chrome-linux*/chrome")
    return hits[0] if hits else None


def run_once(browser, logger_src):
    from playwright.sync_api import sync_playwright  # noqa: F401  (import guard)
    ctx = browser.new_context(viewport={"width": VIEWPORT[0], "height": VIEWPORT[1]},
                              device_scale_factor=1,
                              reduced_motion="reduce" if REDUCED else "no-preference")
    page = ctx.new_page()
    cdp = ctx.new_cdp_session(page)
    feats = [{"name": "prefers-reduced-motion",
              "value": "reduce" if REDUCED else "no-preference"}]
    if REDUCED:
        cdp.send("Emulation.setEmulatedMedia", {"features": feats})
    page.goto(URL, wait_until="load", timeout=30000)
    if REDUCED:
        cdp.send("Emulation.setEmulatedMedia", {"features": feats})
    page.wait_for_timeout(300)
    # ensure the node starts closed so the recorder sees its pre-open frames
    page.evaluate("""() => { document.querySelectorAll('.sheet').forEach(s => {
        if (s.classList.contains('is-open')) {
          const b = s.querySelector('[data-close]'); if (b) b.click(); }}); }""")
    page.wait_for_timeout(300)
    page.evaluate(logger_src)
    page.click(TRIGGER_SEL)
    page.wait_for_timeout(920)
    log = page.evaluate("() => { cancelAnimationFrame(window.__mRaf); return window.__mLog; }")
    settled = page.evaluate(
        "() => getComputedStyle(document.querySelector(%r)).transform" % NODE_SEL)
    ctx.close()

    painted = [f for f in log if f["painted"]]
    naive = [f for f in log if f["transform"] is not None and f["transform"] != settled]
    corr = [f for f in naive if f["painted"]]
    return {
        "log_frames": len(log),
        "preopen_hidden_frames": len([f for f in log if not f["painted"]]),
        "settled_transform": settled,
        "naive_midflight": len(naive),
        "corrected_painted_midflight": len(corr),
        "first_painted_frame": painted[0] if painted else None,
    }


def main():
    from playwright.sync_api import sync_playwright
    logger_src = LOGGER % {"sel": json.dumps(NODE_SEL)}
    exe = find_chrome()
    out = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=exe) if exe else pw.chromium.launch()
        for _ in range(REPEATS):
            out.append(run_once(browser, logger_src))
        browser.close()
    print(json.dumps(out, indent=2))
    if all(r["corrected_painted_midflight"] == 0 for r in out) and \
       any(r["naive_midflight"] > 0 for r in out):
        print("VERDICT: naive counter mis-counts hidden frames as mid-flight; "
              "corrected (painted-only) count is 0 -- probe mis-calibration, not a defect.")


if __name__ == "__main__":
    main()
