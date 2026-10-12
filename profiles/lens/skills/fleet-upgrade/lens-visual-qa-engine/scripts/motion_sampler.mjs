#!/usr/bin/env node
/**
 * LENS motion sampler - re-runnable interval probe.
 *
 * Answers "did this trigger spike, and how high" - a question a single reading
 * taken after a fixed delay cannot answer (it reports the delay, not the motion).
 *
 * Samples BOTH units, because a ceiling written for one is not the other:
 *   - distinct animated ELEMENTS  (Set of animation.effect.target; playState not finished/idle)
 *   - running ANIMATIONS          (getAnimations() filtered on playState === 'running')
 * An element carrying two animations counts once as an element, twice as an animation.
 * Report whichever unit the contract is written in.
 *
 * Usage:
 *   export PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright
 *   export PW_MODULE=$(ls -d /root/projects/*/node_modules/.pnpm/playwright@*/node_modules/playwright/index.mjs | head -1)
 *   PAGE_URL=file:///abs/path/page.html node motion_sampler.mjs '<trigger>' ['<trigger2>' ...]
 *   DURATION_MS=800 INTERVAL_MS=60 EXTRA='document.querySelector(".readout")?.textContent' \
 *     PAGE_URL=... node motion_sampler.mjs '[data-play="question"]'
 *
 * PW_MODULE is the import specifier; it defaults to 'playwright' if the environment
 * already resolves it. Pass multiple triggers to sweep every beat in one run.
 * Prints per-trigger peak (both units) plus the full time series, as JSON on stdout.
 */
import { chromium } from process.env.PW_MODULE || 'playwright';

const triggers = process.argv.slice(2);
if (!triggers.length) { console.error('pass at least one trigger selector'); process.exit(2); }
const DURATION = Number(process.env.DURATION_MS || 800);
const INTERVAL = Number(process.env.INTERVAL_MS || 60);

const url = process.env.PAGE_URL;
if (!url) { console.error('set PAGE_URL to the page under test'); process.exit(2); }

// Unit 1: distinct animated elements. Set dedupes an element animated several times.
const DISTINCT_ELEMENTS = `(() => {
  const els = new Set();
  for (const a of document.getAnimations()) {
    if (a.playState === 'finished' || a.playState === 'idle') continue;
    const t = a.effect && a.effect.target;
    if (t) els.add(t);
  }
  return els.size;
})()`;
// Unit 2: animations currently in the running play state.
const RUNNING_ANIMATIONS =
  `document.getAnimations().filter(a => a.playState === 'running').length`;

const browser = await chromium.launch({ headless: true });
const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
const page = await ctx.newPage();

const consoleErrors = [];
const requests = [];
page.on('console', m => { if (m.type() === 'error') consoleErrors.push(m.text()); });
page.on('pageerror', e => consoleErrors.push(String(e?.message || e)));
page.on('request', r => requests.push(r.url()));
page.on('requestfailed', r => requests.push(`FAILED ${r.url()}`));

await page.goto(url, { waitUntil: 'load' });
await page.waitForTimeout(1200); // settle

const results = [];
for (const trigger of triggers) {
  await page.locator(trigger).first().click({ timeout: 10000 });
  const series = [];
  const t0 = Date.now();
  for (;;) {
    const running = await page.evaluate(RUNNING_ANIMATIONS);
    const elements = await page.evaluate(DISTINCT_ELEMENTS);
    series.push({ t: Date.now() - t0, running, elements });
    if (Date.now() - t0 >= DURATION) break;
    await page.waitForTimeout(INTERVAL);
  }
  // the artifact's own self-measurement, if it exposes one
  // NOTE: EXTRA is read at the end of the burst window (~DURATION ms), where a
  // self-measuring readout is often still its immediate/transient form. If the
  // number you need is the SETTLED one, raise DURATION_MS past the page's own
  // settle threshold (or re-read after an extra wait) before trusting this value.
  const extra = process.env.EXTRA ? await page.evaluate(process.env.EXTRA) : null;
  results.push({
    trigger,
    peak_distinct_elements: Math.max(...series.map(s => s.elements)),
    peak_running_animations: Math.max(...series.map(s => s.running)),
    settled_running: series.at(-1).running,
    settled_elements: series.at(-1).elements,
    series,
    self_reported: extra,
  });
}

const foreign = requests.filter(u => u !== url);
console.log(JSON.stringify({
  url,
  window_ms: DURATION,
  interval_ms: INTERVAL,
  shadow_note: 'getAnimations() omits shadow roots; counts are light-DOM only',
  moments: results,
  requests_total: requests.length,
  foreign_requests: foreign,
  console_errors: consoleErrors,
}, null, 2));

await browser.close();
