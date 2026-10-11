---
name: reactive-spa-development
description: Use when building or testing reactive SPA applications.
version: 1.0.0
author: Orion Fleet Lead
license: MIT
metadata:
  hermes:
    tags: [react, vue, svelte, spa, async-worker, polling, browser-testing, cdp, playwright, ui-ux]
    category: software-development
---

# Reactive Single-Page Application (SPA) Engineering & Automation

Comprehensive standard for building, polling, state-synchronizing, and automating reactive web applications (React, Vue, Svelte, Solid) with asynchronous background workers and headless browser test runners.

---

## When to Use

Use this skill when:
1. Designing UI workflows that poll asynchronous background workers (AI generation, media rendering, job queues) and manage state transitions.
2. Automating or testing modern reactive SPAs via CDP, Playwright, or browser tools without triggering form desynchronization.
3. Preserving form drafts, preventing phantom loading spinners, and masking internal worker infrastructure leaks from end-user UI.
4. Intercepting in-flight network requests, polling in-memory client logs, and trapping unhandled React runtime exceptions.

---

## 1. Async Worker UI Flow & Polling Architecture

### A. Unified State Synchronization on Completion
- In database-backed job queues (`SKIP LOCKED`, Celery, pg-boss), polling tracks: `PENDING` -> `PROCESSING` -> `COMPLETED` | `FAILED`.
- **Pitfall**: Setting `isGenerating = false` on `COMPLETED` without re-fetching updated parent entities leaves newly generated records invisible until a manual page refresh.
- **Rule**: On terminal `COMPLETED`, immediately trigger parent state re-fetch (e.g. `loadStory()`, `revalidate()`), then scroll fresh content into view.

### B. Single Authoritative Progress Indicator & Phantom Spinner Guard
- Bind loading spinners strictly to the active stream tail; suppress duplicate sticky or header banners during in-progress execution.
- **Phantom Spinner Pitfall**: Defaulting progress indicators to an active spinning state when no `jobId` exists or initial dispatch was rejected (429/403) strands users in a perpetual fake loading screen.
- **Rule**: Never render active spinners without an active `jobId` or verified polling loop. If items equal 0 and no job runs, display an explicit idle state with a primary action CTA.
- **URL Job Handoff**: Pass accepted job IDs in navigation query params (`?jobId=<uuid>`). The target page must check `urlJobId` on mount to kick off polling immediately.

### C. Clean User-Facing Status & Sanitized Errors
- Never leak internal model names, proxy routes, retry counts, or queue names (e.g. *"Diproses oleh model Gemini via 9router"*) in client-facing UI. Display customer-centric status only (*"Audio Siap Didengarkan"*, *"Menyusun Draf"*).
- Map raw upstream schema failures, JSON parser errors, or database constraints through a domain sanitizer to calm, actionable guidance (*"AI sedang mengalami kendala sesaat. Silakan coba lagi"*).

### D. Resilient Draft Preservation & Non-Destructive Error Handling
- Storing form drafts purely in component state erases user input on quota limits, network drops, or accidental page reloads.
- Synchronize custom inputs to `sessionStorage` on change (keyed by entity ID). Clear storage strictly upon verified HTTP 200 queue acceptance.
- On API rejection, set the error state without resetting input fields so users can edit and retry. Never use unstyled `window.alert()` dialogs.

---

## 2. SPA Automated Browser Testing & State Manipulation

### A. Mutate Controlled Inputs via Prototype Setters
Frameworks (React, Solid) track input values by overriding native property setters. Setting `element.value = "..."` directly mutates raw DOM without notifying component state, leaving submit buttons disabled.
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

### B. Instrument In-Flight Network Requests Before Interacting
In SPAs, button clicks dispatch asynchronous `fetch` calls without full document navigation. Standard `wait_for_load()` returns prematurely. Inject an in-memory audit hook before interacting:
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

### C. Trap Client-Side Exceptions & Minified React Crashes
Production SPA builds return HTTP 200 even when components crash into generic error screens (*"Application error: a client-side exception has occurred"*). Inject an uncaught error trap before navigation:
```python
cdp('Page.addScriptToEvaluateOnNewDocument', source="""
window.__caughtErrors = [];
window.addEventListener('error', (e) => {
  window.__caughtErrors.push({ message: e.message, stack: e.error ? e.error.stack : 'no stack' });
});
window.addEventListener('unhandledrejection', (e) => {
  window.__caughtErrors.push({ reason: String(e.reason) });
});
""")
```

### D. Scoping Locators & Virtualized Document Tree Navigation
1. **Scope Locators to Visible Containers**: SPAs retain hidden tabs or collapsible drawer forms in the DOM. Using bare `page.getByLabel()` triggers strict mode violation timeouts when multiple inputs share labels across collapsed sections. Always scope via `container.getByLabel(...)` or `.locator(':visible').first()`.
2. **Virtualized Document Trees (SharePoint/OneDrive)**: Synthetic double-clicks on virtualized row items often trigger row selection rather than opening child folders. Inspect URL query parameters (e.g. `id=%2Fpersonal%2F...`) and append the subfolder path to navigate directly via `goto_url`, bypassing fragile DOM event dispatching.
3. **Prune Stale CDP Tabs**: Orphaned tabs accumulate on `--remote-debugging-port=9222`, causing browser IPC calls to time out after 5s. Query `http://127.0.0.1:9222/json/list` and close obsolete tabs via `/json/close/{id}` before running extensive audit sweeps.

---

## 3. Pitfalls & Anti-Patterns

- **Never rely on raw `.value = ...` in React/Solid forms**: Component state will not update, leaving submit buttons disabled or firing empty payloads.
- **Never rely on `wait_for_load()` for asynchronous SPA mutations**: Full-page navigation does not fire on REST/GraphQL calls; use network interception logs or explicit element polling.
- **Check server sync state before blaming API routes**: Local-first apps keep drafts in browser storage; downstream backend services return 404 if the session has not been synced to the database.
- **Trap client-side window errors when auditing production SPAs**: Next.js and React return HTTP 200 even on unhandled runtime exceptions; inject error listeners on document creation to capture call stacks.
- **Cloud browser SSRF guards block 127.0.0.1**: External browser runners reject private network addresses; use local Node with `/usr/bin/google-chrome` and `--no-sandbox` to capture loopback pages directly.
