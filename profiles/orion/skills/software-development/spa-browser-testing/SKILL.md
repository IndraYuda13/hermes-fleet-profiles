---
name: spa-browser-testing
description: Use when testing or automating React and SPA web apps.
---

# Single-Page Application (SPA) & Reactive UI Automation

Use this skill when driving automated browsers (CDP, Playwright, Hermes browser CLI) against modern reactive web apps (React, Vue, Svelte, Solid) and offline-first/local-first architectures.

## Execution Procedure

### 1. Instrument In-Flight Network Requests Before Interacting
In SPAs, clicking action buttons fires asynchronous background requests (`fetch` or `XMLHttpRequest`) without triggering document navigation. `wait_for_load()` will return immediately or miss the response.

Inject an in-memory audit hook before interacting:
```javascript
if (!window.__fetchLogs) {
  window.__fetchLogs = [];
  const _fetch = window.fetch;
  window.fetch = async (...args) => {
    const entry = { url: typeof args[0] === 'string' ? args[0] : args[0]?.url, body: args[1]?.body, started: Date.now() };
    window.__fetchLogs.push(entry);
    try {
      const res = await _fetch(...args);
      entry.status = res.status;
      entry.ok = res.ok;
      const clone = res.clone();
      try { entry.resBody = await clone.json(); } catch(e) { entry.resBody = await clone.text(); }
      return res;
    } catch(err) {
      entry.error = String(err);
      throw err;
    }
  };
}
```

### 2. Mutate Controlled Inputs Using the Prototype Setter
Frameworks like React wrap native input elements and track value changes via property setter overrides. Setting `element.value = "..."` directly only mutates the raw DOM property without notifying the reactive component state.

Always use the native prototype setter followed by bubbling events:
```javascript
// For <textarea>:
const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
setter.call(element, 'desired value');
element.dispatchEvent(new Event('input', { bubbles: true }));
element.dispatchEvent(new Event('change', { bubbles: true }));

// For <input>:
const inputSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
inputSetter.call(element, 'desired value');
element.dispatchEvent(new Event('input', { bubbles: true }));
element.dispatchEvent(new Event('change', { bubbles: true }));
```

### 3. Verify Local-to-Server Sync Preconditions
In local-first or offline-first apps (IndexedDB, Dexie, SQLite WASM, LocalStorage):
- Background/AI endpoints frequently enforce referential integrity or existence checks against the server database (e.g. `sessionId` must exist in `sync_sessions` before `/api/.../bisik` or analysis routes succeed).
- If testing locally generated sessions or guest sessions, either trigger the application's explicit "Sync" action in the UI, or verify the test session record exists in the test database prior to triggering dependent endpoints.
- A 404 NOT_FOUND from an AI/analytics route during browser testing usually indicates an unsynced local session rather than a missing API route.

### 4. Account for Client-Side Privacy Sanitization Boundaries
Modern apps often run client-side privacy filters (PII checks, name masking, prompt-injection guards) on form inputs before dispatching requests to LLMs.
- If an input is rejected or preview fails with warnings like "Hapus identitas", inspect local client validator rules (e.g., student name word-matching, phone/email regex).
- Craft test queries that avoid matching mock student roster names or forbidden tokens.

### 5. Poll In-Memory Logs for Async Completion
Instead of arbitrary sleep delays, poll `window.__fetchLogs` or relevant DOM elements for resolution:
```python
# In automation script:
for _ in range(15):
    time.sleep(1)
    logs = js("window.__fetchLogs")
    last_log = logs[-1] if logs else {}
    if last_log.get("status") is not None:
        print(f"Request completed with status {last_log.get('status')}")
        break
```

### 6. Fast-Forward Deep State via Synthetic Fixtures
Complex SPAs with multi-step workflows or physical sensor prerequisites (such as camera QR/card scanners, barcode readers, or multi-station rotations) frequently provide developer/demo fixtures in the UI.
- Inspect the DOM for synthetic buttons (e.g. `Fixture sintetis`, `Seed data`, `Demo mode`) before attempting to mock camera streams or manually enter dozens of items.
- Trigger batch fixture events sequentially through simulated clicks and assert completion of the accumulator state (e.g. 32/32 cards scanned) before testing downstream UI views.

### 7. Full-Funnel Traceability for User Demonstrations
When demonstrating features or reporting visual verification back to users or stakeholders:
- Never provide only the isolated final card or modal in isolation; users will not know how to reach it from their initial landing state.
- Document and capture the contiguous 4-step sequence:
  1. Entry point and demo bypass (e.g. `/masuk` -> "Coba data contoh").
  2. Route navigation (distinguishing primary dashboard routes from secondary rehearsal/workspace routes like `/latihan`).
  3. Precondition setup (e.g. dataset picker, session recipe generation).
  4. The exact target trigger control and resulting live UI component.

### 8. Prune Stale CDP Tabs on Daemon Timeouts
When driving headless Chrome instances across multiple testing runs, orphaned target pages accumulate on `--remote-debugging-port=9222`, causing the browser harness daemon's IPC calls (`Page.navigate`, `new_tab`) to time out after 5s.
- Inspect open targets: query `http://127.0.0.1:9222/json/list` to count open tabs.
- Close orphaned pages: iterate over obsolete tabs and call `http://127.0.0.1:9222/json/close/{id}` to free Chrome renderer processes.
- Clear daemon locks: if IPC remains unresponsive, remove stale harness files (`/root/.config/browser-harness/runtime/bu-*.pid`) before retrying `browser_exec`.

### 9. Navigate Virtualized Document-Tree SPAs (SharePoint/OneDrive) via URL Parameters
In complex document-tree or file-browser SPAs (such as SharePoint, OneDrive `onedrive.aspx`, or Google Drive), items are rendered inside virtualized tables (`[role="row"]`, `[data-automationid="DetailsRow"]`). DOM mouse events (`click()`, `dblclick`, `dispatchEvent`) often fail to open child folders because handlers are bound to internal React synthetic event dispatchers or row selection managers rather than standard anchor navigation.
- Avoid spending loops attempting synthetic click/dblclick events on folder row elements.
- Inspect URL query parameters: SharePoint/OneDrive encodes the active folder path in the `id` param (e.g., `id=%2Fpersonal%2F<user>%2FDocuments%2F<Folder>&ga=1`).
- Navigate directly via `goto_url(...)` by appending `%2F<SubfolderName>` to the encoded path in `id=`. The SPA router re-mounts the view and queries the new path immediately, bypassing fragile DOM event dispatching.

## Key Pitfalls & Rules

- **Never use raw `.value = ...` in React/Solid forms**: Component state will not update, leaving submit buttons disabled or firing empty payloads.
- **Never rely on `wait_for_load()` for asynchronous SPA mutations**: Full-page navigation does not fire on REST/GraphQL calls; use network interception logs or explicit element polling.
- **Check server sync state before blaming API routes**: Local-first apps keep drafts in browser storage; downstream backend services will return 404 if the session has not been synced to the database.
- **Do not share isolated sub-component screenshots without the access funnel**: When guiding users, missing the entry path or state prerequisites leads to user confusion on complex multi-route SPAs.
- **Prune CDP zombie tabs before declaring browser tools broken**: Detached debug targets choke Chrome IPC sockets; clean up targets via `/json/close/{id}` instead of assuming tools or routes are failing.
- **Do not simulate double-clicks on virtualized folder rows in SharePoint/OneDrive**: Synthetic mouse events in complex React file-trees usually select the row or trigger row action bars without opening the folder; update the URL parameter (e.g., `id=...%2FSubfolder`) and call `goto_url` directly.
