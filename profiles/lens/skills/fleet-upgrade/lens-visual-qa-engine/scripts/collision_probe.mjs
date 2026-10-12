#!/usr/bin/env node
/**
 * LENS geometry collision probe - re-runnable.
 *
 * Answers the assertion set a token/typography/motion audit cannot: do visible
 * boxes overlap, does anything escape the title-safe frame, does anything clip
 * its own text. Runs every trigger in BOTH size modes, and proves the detector
 * fires with a built-in positive control before reporting a clean result.
 *
 * Usage:
 *   export PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright
 *   export PW_MODULE=$(ls -d /root/projects/*/node_modules/.pnpm/playwright@*/node_modules/playwright/index.mjs | head -1)
 *   PAGE_URL=file:///abs/path/page.html \
 *     TRIGGERS='[data-play="siar"],[data-play="question"]' \
 *     SAFE_SEL='.safe' STAGE_SEL='.stage' BOARDSIZE_SEL='#boardsize' \
 *     node collision_probe.mjs
 *
 * Env:
 *   PAGE_URL       required, the page under test
 *   TRIGGERS       required, comma-separated CSS selectors clicked in order
 *   SAFE_SEL       default '.safe'    (title-safe frame)
 *   STAGE_SEL      default '.stage'   (clipping canvas)
 *   BOARDSIZE_SEL  optional; when set, the whole sweep re-runs after clicking it
 *   SETTLE_MS      default 900        (wait after each trigger click)
 *
 * Output: JSON on stdout. `control` shows the detector firing on injected
 * geometry; `modes` holds the per-trigger verdicts.
 */
import { chromium } from process.env.PW_MODULE || 'playwright';

const url = process.env.PAGE_URL;
const triggers = (process.env.TRIGGERS || '').split(',').map(s => s.trim()).filter(Boolean);
if (!url) { console.error('set PAGE_URL'); process.exit(2); }
if (!triggers.length) { console.error('set TRIGGERS to a comma-separated selector list'); process.exit(2); }
const SAFE = process.env.SAFE_SEL || '.safe';
const STAGE = process.env.STAGE_SEL || '.stage';
const BOARDSIZE = process.env.BOARDSIZE_SEL || '';
const SETTLE = Number(process.env.SETTLE_MS || 900);

const DETECT = (safeSel, stageSel) => `(() => {
  const safe = document.querySelector('${safeSel}'), stage = document.querySelector('${stageSel}');
  if (!safe || !stage) return { error: 'missing safe/stage' };
  const sr = safe.getBoundingClientRect(), st = stage.getBoundingClientRect();
  const vis = el => { const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) return false;
    const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  const set = [];
  for (const el of safe.querySelectorAll('*')) {
    if (!vis(el)) continue;
    const tag = el.tagName.toLowerCase();
    const txt = (el.textContent || '').replace(/\\s+/g, ' ').trim();
    if (!txt && tag !== 'svg' && tag !== 'canvas') continue;
    set.push(el);
  }
  const label = el => { const t = (el.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 40);
    const cn = (typeof el.className === 'string' && el.className.trim())
      ? '.' + el.className.trim().split(/\\s+/).slice(0, 2).join('.') : '';
    return el.tagName.toLowerCase() + cn + (t ? ' "' + t + '"' : ' [graphic]'); };
  const R = set.map(el => el.getBoundingClientRect());
  const collisions = [], containment = [];
  for (let i = 0; i < set.length; i++) for (let j = i + 1; j < set.length; j++) {
    const A = R[i], B = R[j];
    const ix = Math.max(0, Math.min(A.right, B.right) - Math.max(A.left, B.left));
    const iy = Math.max(0, Math.min(A.bottom, B.bottom) - Math.max(A.top, B.top));
    const area = ix * iy;
    if (area <= 0.5) continue;
    const nested = set[i].contains(set[j]) || set[j].contains(set[i]);
    const rec = { a: label(set[i]), b: label(set[j]), area_px2: +area.toFixed(1) };
    (nested ? containment : collisions).push(rec);
  }
  const overflow = [];
  set.forEach(el => { if (el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1)
    overflow.push({ el: label(el), scrollW: el.scrollWidth, clientW: el.clientWidth,
      scrollH: el.scrollHeight, clientH: el.clientHeight }); });
  const outside = [];
  set.forEach((el, i) => { const r = R[i];
    if (r.left < sr.left - 1 || r.right > sr.right + 1 || r.top < sr.top - 1 || r.bottom > sr.bottom + 1) {
      const painted = Math.max(0, Math.min(r.bottom, st.bottom) - Math.max(r.top, st.top));
      outside.push({ el: label(el),
        over_left: +(sr.left - r.left).toFixed(1), over_right: +(r.right - sr.right).toFixed(1),
        over_top: +(sr.top - r.top).toFixed(1), over_bottom: +(r.bottom - sr.bottom).toFixed(1),
        painted_px: +painted.toFixed(2), painted_pct: +(100 * painted / r.height).toFixed(0) });
    } });
  return { counted_elements: set.length,
    collision_count: collisions.length, collisions,
    containment_pair_count: containment.length,
    overflow_count: overflow.length, overflow,
    outside_safe_count: outside.length, outside_safe: outside };
})()`;

// the positive control: two overlapping probes, one out-of-frame probe, one narrow overflow box
const INJECT = (safeSel) => `(() => {
  const safe = document.querySelector('${safeSel}');
  const mk = (css, txt) => { const d = document.createElement('div'); d.textContent = txt;
    d.style.cssText = css; safe.appendChild(d); return d; };
  mk('position:absolute;left:40px;top:40px;width:300px;height:120px;background:#f2a33a;color:#000;z-index:9', 'PROBE A');
  mk('position:absolute;left:200px;top:90px;width:300px;height:120px;background:#0b6b6b;color:#fff;z-index:10', 'PROBE B');
  mk('position:absolute;left:0;bottom:-80px;width:200px;height:60px;background:#9a5b00;color:#fff;z-index:11', 'PROBE OUTSIDE');
  const w = document.createElement('div'); w.textContent = 'WWWWWWWWWWWWWWWWWWWW';
  w.style.cssText = 'width:40px;height:20px;overflow:hidden;background:#14212b;color:#fff';
  safe.appendChild(w);
  return true;
})()`;

const browser = await chromium.launch({ headless: true });
const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
const page = await ctx.newPage();
const consoleErrors = [];
page.on('console', m => { if (m.type() === 'error') consoleErrors.push(m.text()); });
page.on('pageerror', e => consoleErrors.push(String(e?.message || e)));
await page.goto(url, { waitUntil: 'load' });
await page.waitForTimeout(1200);

async function sweep(mode) {
  const rows = [];
  for (const trigger of triggers) {
    await page.locator(trigger).first().click({ timeout: 10000 });
    await page.waitForTimeout(SETTLE);
    rows.push({ mode, trigger, ...(await page.evaluate(DETECT(SAFE, STAGE))) });
  }
  return rows;
}

const modes = {};
modes.default = await sweep('default');
if (BOARDSIZE) {
  await page.locator(BOARDSIZE).first().click();
  await page.waitForTimeout(300);
  modes.boardsize = await sweep('boardsize');
}

// control: baseline on the last trigger, then inject and re-detect
const ctrlBefore = await page.evaluate(DETECT(SAFE, STAGE));
await page.evaluate(INJECT(SAFE));
await page.waitForTimeout(200);
const ctrlAfter = await page.evaluate(DETECT(SAFE, STAGE));

const ok = ctrlAfter.collision_count > ctrlBefore.collision_count
  && ctrlAfter.outside_safe_count > ctrlBefore.outside_safe_count
  && ctrlAfter.overflow_count > ctrlBefore.overflow_count;

console.log(JSON.stringify({
  url, safe_sel: SAFE, stage_sel: STAGE, settle_ms: SETTLE,
  control: { detector_fires: ok, before: ctrlBefore, after: ctrlAfter,
    note: 'a zero result below is only evidence when detector_fires is true' },
  modes, console_errors: consoleErrors,
}, null, 2));

await browser.close();
