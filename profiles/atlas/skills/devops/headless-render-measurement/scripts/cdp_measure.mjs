#!/usr/bin/env node
// Playwright-free headless measurement over the Chrome DevTools Protocol.
//
// Verified path (attach to an already-listening Chrome):
//   node cdp_measure.mjs /abs/path/page.html 390x844,412x915 [probe.js]
// Fallback path (launch our own): same command, if nothing answers the endpoint.
//
// probe.js must hold a single JS expression that returns a JSON-serialisable value.
// node >= 22 provides global fetch and WebSocket, so there are no dependencies.
// Nothing on disk is written; redirect stdout to a file when the probe JSON is large
// (tailing a long stdout silently drops the first artefact's block).
//
// --endpoint defaults to http://127.0.0.1:9222; if nothing answers there we
// launch our own Chrome (--headless=new --no-sandbox, scratch profile) and shut
// it down at the end. `# targets before/after` proves we only closed our own.
import { setTimeout as sleep } from 'node:timers/promises';
import { readFileSync, mkdtempSync, rmSync } from 'node:fs';
import { spawn } from 'node:child_process';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const argv = process.argv.slice(2);
let endpoint = 'http://127.0.0.1:9222';
const rest = [];
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === '--endpoint') { endpoint = argv[++i]; continue; }
  rest.push(argv[i]);
}
const [target, vpArg, probePath] = rest;
if (!target || !vpArg) {
  console.error('usage: node cdp_measure.mjs <url-or-path> <WxH[,WxH...]> [probe.js] [--endpoint http://host:port]');
  process.exit(2);
}
const pageUrl = /^[a-z][a-z0-9+.-]*:\/\//i.test(target) ? target : 'file://' + target;
const viewports = vpArg.split(',').map(s => {
  const [w, h] = s.trim().split('x').map(Number);
  if (!w || !h) { console.error('bad viewport: ' + s); process.exit(2); }
  return { w, h };
});
// Increasing settle delays: report a metric only after two consecutive samples agree.
const DELAYS = (process.env.CDP_SETTLE_MS || '1500,5000').split(',').map(Number).sort((a, b) => a - b);
const UA = process.env.CDP_UA ||
  'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36';

// Default probe: fold geometry for a tile grid, plus webfont provenance.
const DEFAULT_PROBE = `(() => {
  const vh = window.innerHeight, de = document.scrollingElement;
  const boxes = [...document.querySelectorAll('[data-testid=service-tile]')].map(e => {
    const r = e.getBoundingClientRect();
    return { top: +r.top.toFixed(2), bottom: +r.bottom.toFixed(2), left: +r.left.toFixed(2), right: +r.right.toFixed(2) };
  });
  return { tile_count: boxes.length,
    first_top: boxes.length ? boxes[0].top : null,
    first_top_over_vh: boxes.length ? boxes[0].top / vh : null,
    fully_visible: boxes.filter(b => b.top >= 0 && b.bottom <= vh).length,
    innerHeight: vh, scrollWidth: de.scrollWidth, clientWidth: de.clientWidth,
    horizontal_overflow: de.scrollWidth > de.clientWidth,
    fonts_status: document.fonts.status, font_faces: [...document.fonts].length, boxes };
})()`;
const PROBE = probePath ? readFileSync(probePath, 'utf8') : DEFAULT_PROBE;

const versionInfo = async () => {
  const r = await fetch(endpoint + '/json/version');
  if (!r.ok) throw new Error('CDP /json/version returned ' + r.status);
  return r.json();
};
const targetCount = async () => (await (await fetch(endpoint + '/json/list')).json()).length;

async function ensureBrowser() {
  try { return { info: await versionInfo(), launched: null }; } catch { /* not listening */ }
  const port = new URL(endpoint).port || '9222';
  const profile = mkdtempSync(join(tmpdir(), 'cdp-profile-'));
  const args = ['--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
    '--remote-debugging-port=' + port, '--user-data-dir=' + profile,
    '--no-first-run', '--no-default-browser-check', '--disable-gpu', 'about:blank'];
  const exe = process.env.CHROME_BIN || 'google-chrome';
  const child = spawn(exe, args, { stdio: 'ignore', detached: true });
  for (let i = 0; i < 40; i++) {
    try { return { info: await versionInfo(), launched: { child, profile } }; }
    catch { await sleep(250); }
  }
  throw new Error('Chrome never exposed CDP on ' + endpoint);
}

const { info, launched } = await ensureBrowser();
console.log('# endpoint ' + endpoint + ' | Browser: ' + info.Browser + ' | targets before: ' + await targetCount());
if (launched) console.log('# NOTE: launched our own Chrome with profile ' + launched.profile);

const ws = new WebSocket(info.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
const send = (method, params = {}, sessionId) => new Promise((res, rej) => {
  const m = { id: ++id, method, params };
  if (sessionId) m.sessionId = sessionId;
  pending.set(m.id, { res, rej });
  ws.send(JSON.stringify(m));
});
await new Promise(res => ws.addEventListener('open', res));
ws.addEventListener('message', ev => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) {
    const p = pending.get(m.id);
    pending.delete(m.id);
    m.error ? p.rej(new Error(JSON.stringify(m.error))) : p.res(m.result);
  }
});

for (const { w, h } of viewports) {
  const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
  await send('Page.enable', {}, sessionId);
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: true }, sessionId);
  await send('Emulation.setUserAgentOverride', { userAgent: UA }, sessionId);
  await send('Page.navigate', { url: pageUrl }, sessionId);
  let elapsed = 0;
  for (const delay of DELAYS) {
    await sleep(Math.max(0, delay - elapsed));
    elapsed = delay;
    const r = await send('Runtime.evaluate', { expression: PROBE, returnByValue: true }, sessionId);
    console.log('=== ' + w + 'x' + h + ' | settle ' + delay + 'ms ===');
    if (r.exceptionDetails) {
      console.log('EXCEPTION ' + JSON.stringify(r.exceptionDetails.exception && r.exceptionDetails.exception.description));
    } else {
      console.log(JSON.stringify(r.result.value, null, 1));
    }
  }
  await send('Target.closeTarget', { targetId }); // close only what we opened
}
console.log('# targets after: ' + await targetCount());

if (launched) {
  try { process.kill(-launched.child.pid, 'SIGTERM'); } catch { /* already gone */ }
  try { rmSync(launched.profile, { recursive: true, force: true }); } catch { /* best effort */ }
  console.log('# we launched this Chrome: stopped it and removed its profile');
}
process.exit(0);
