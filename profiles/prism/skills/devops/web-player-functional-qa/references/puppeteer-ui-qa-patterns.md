# Puppeteer UI QA Patterns

Patterns learned from functional QA of static UI prototypes (vanilla JS, no framework).

## IIFE Closure Workaround

Many vanilla JS apps wrap all logic in an IIFE:
```javascript
(function() { const state = {...}; function render() {...} })();
```

You **cannot** access `state` or internal functions via `page.evaluate()`. Instead:
- Trigger actions through UI interactions (click buttons, use keyboard shortcuts)
- Use the command palette or navigation controls the app itself provides
- Check DOM output to infer state, not the JS state object

## Transient State Capture (Skeletons, Loaders)

Loading states with `setTimeout` (e.g., 600ms skeleton display) require:
1. Trigger the action that sets loading state
2. Check DOM **immediately** after trigger (within same evaluate or <30ms)
3. Don't rely on `await sleep()` -- the state may have already cleared

```javascript
// WRONG: race condition, skeleton already gone
await triggerAction();
await sleep(100);  // too late!
const skeletons = await page.$$('.skeleton-box');  // 0 found

// RIGHT: check immediately after trigger
await page.evaluate(() => {
  document.querySelector('.trigger-button').click();
});
const skeletons = await page.evaluate(() =>
  document.querySelectorAll('.skeleton-box').length
);  // 30 found
```

**Alternative:** If the app has a command palette, trigger loading through that:
```javascript
await page.keyboard.down('Control');
await page.keyboard.press('k');
await page.keyboard.up('Control');
await sleep(300);  // wait for palette to open
// Click the "Simulate Loading" item
await page.evaluate(() => {
  const items = document.querySelectorAll('.palette-item');
  for (const item of items) {
    if (item.textContent.includes('Simulate')) { item.click(); break; }
  }
});
// Check immediately
const count = await page.evaluate(() =>
  document.querySelectorAll('.skeleton-box').length
);
```

## Keyboard Shortcut Testing

Don't assume all keyboard shortcuts work via `KeyboardEvent` dispatch. Check the app's keyboard handler:
- Some shortcuts require no input focused (guard: `activeTag !== 'input'`)
- Some only work through the command palette (not direct keyboard)
- `page.keyboard.press()` is more reliable than `window.dispatchEvent(new KeyboardEvent(...))`

Always click `body` first to ensure focus is not on an input:
```javascript
await page.click('body');
await sleep(100);
await page.keyboard.press('j');  // now J/K nav works
```

## Puppeteer v25+ API Changes

`page.waitForTimeout(ms)` was **removed** in Puppeteer v25. Replace with:
```javascript
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
await delay(300);
```
Define once at module level and use everywhere.

## Click-Through-Overlay Failures

Puppeteer's `page.click()` performs hit-testing. If a dropdown menu, modal backdrop, or tooltip overlay covers the target element, you get:
```
Error: Node is either not clickable or not an Element
```

**Fix patterns:**
```javascript
// 1. Close overlays first
await page.keyboard.press('Escape');
await delay(200);
await page.click('#target');  // now unobstructed

// 2. JS click bypasses hit-testing (use for setup, not user-flow assertions)
await page.evaluate(() => document.getElementById('target').click());
await page.evaluate(() => {
  const row = document.querySelector('.my-row[data-id="123"]');
  if (row) row.click();
});
```

**When it happens:** Typically after testing service dropdowns, command palettes, or declare-incident modals -- the overlay stays open and blocks clicks on elements underneath.

## File URL Testing

For static prototypes served from filesystem:
```javascript
const FILE_URL = `file://${path.resolve(__dirname, 'app/index.html')}`;
```
Requires Chrome flags: `--disable-web-security --allow-file-access-from-files`

**Preferred: Local HTTP server** (avoids CORS/security flags, favicon 404 noise):
```javascript
const http = require('http'), fs = require('fs'), path = require('path');
const mimeTypes = {
  '.html': 'text/html', '.css': 'text/css',
  '.js': 'application/javascript', '.json': 'application/json'
};
const server = http.createServer((req, res) => {
  const filePath = path.join(APP_DIR, req.url === '/' ? 'index.html' : req.url);
  fs.readFile(filePath, (err, data) => {
    if (err) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { 'Content-Type': mimeTypes[path.extname(filePath)] || 'text/plain' });
    res.end(data);
  });
});
server.listen(0, '127.0.0.1', () => {
  const url = `http://127.0.0.1:${server.address().port}`;
  // use url for page.goto()
});
```
Port 0 lets the OS pick a free port -- eliminates conflicts in parallel test runs.

## Console Error Collection

Set up listeners before navigation:
```javascript
const consoleErrors = [];
const pageErrors = [];
page.on('console', msg => {
  if (msg.type() === 'error') consoleErrors.push(msg.text());
});
page.on('pageerror', err => pageErrors.push(err.toString()));
```

## Test Result Structure

Use a structured record pattern for machine-readable results:
```javascript
function record(name, viewport, passed, detail) {
  RESULTS.push({ name, viewport, result: passed ? 'PASS' : 'FAIL', detail });
}
```

Write results to JSON for downstream consumption:
```javascript
fs.writeFileSync('test-results.json', JSON.stringify({
  testCount, passCount, failCount, results, defects, evidence
}, null, 2));
```
