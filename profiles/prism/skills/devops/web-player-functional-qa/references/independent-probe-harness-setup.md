# Standing up an independent probe suite against a repo you must not modify

Depth for SKILL.md sections 10 and 11. Use when you are asked to verify a repo whose working tree and build must stay frozen, and you need your own Playwright suite that does not pollute it.

## 1. Keep every write out of the repo

`git status --porcelain` must still be empty when you finish. Probe specs, configs, JSON results, and screenshots live in their own evidence tree (`<evidence>/prism/`); nothing goes into `tests/`. Re-check `git status` after the run, not only before.

Reuse the repo's dependency tree with a symlink instead of installing:

```bash
ln -sfn /root/projects/<repo>/node_modules <evidence>/node_modules
```

Playwright will look for `package.json` upward from the config, so give the evidence dir a minimal `package.json` (`{"private": true, "type": "module"}`). Invoke the CLI by absolute path to avoid a package-manager wrapper that tries to resolve its own workspace:

```bash
node <repo>/node_modules/@playwright/test/cli.js test --config=<evidence>/config.ts --reporter=list
```

`pnpm exec playwright` from a directory with no manifest fails with `ERR_PNPM_NO_PKG_MANIFEST`. A bare `pnpm exec` is fine when you invoke it from the repo root.

## 2. Make your config self-sufficient

Point `testDir`/`outputDir` at the evidence tree, import the harness's own origin helper, and copy the repo's `webServer` block into your config with `cwd` pinned to the repo. A config without the web server silently produces `net::ERR_CONNECTION_REFUSED` on every navigation and reads like a product outage.

Run the repo's `globalSetup` with `cwd` at the repo root: a Vite-based setup that resolves relative entry modules (`tests/browser/<fixture>.ts`) fails with `UNRESOLVED_ENTRY` when invoked from the evidence dir.

## 3. Seed fixtures by API, never through the UI

Drive setup through the app's own JSON endpoints with `page.request.post(path, { headers: { Origin }, data })` and fail loudly on a non-OK status (`throw` with the body). This keeps probes short and makes a fixture failure obvious instead of showing up as an unrelated assertion failure three steps later.

Read the contract schemas before writing the seed payload. Strict schemas reject a plausible-looking fixture: a card option field typed as a 4-tuple rejects a 2-element array with an unhelpful `422 INVALID_INPUT`. When a seed 422s, check the schema in `src/contracts/` first rather than assuming the endpoint is broken.

## 4. DOM accessors and waits are the top source of self-inflicted red

- **Wait for the hydrated shell** before reading anything: a client page renders a loading notice first, so an immediate `isVisible()`/`count()` reads the pre-hydration DOM and reports a missing element that appears moments later. Gate on a stable control being visible (the real submit button), not on the URL.
- **After a navigation that triggers a keyed remount**, wait for the destination phase's heading before reading that phase's chrome; the URL commits before the remount finishes.
- **A component may render the same value twice** (a visible span plus an `sr-only` prose span). `locator(...).innerText()` on the parent concatenates both and breaks exact-equality assertions: target `span[aria-hidden]` for the visible value and `span.sr-only` for the prose, and record both.
- **Record raw geometry JSON as well as boolean assertions**, so a verdict is reproducible from the log without re-reading the spec.

## 5. Model the product's own rules in your fixture

A probe that violates a documented rule tests your probe, not the product. Read the invariant in the source (for example: only one group may be assigned to the shared screen) and make the fixture obey it. When you assert that a readiness control is disabled, assert *why* by reading the reason list, and count the expected reasons.

Expect the same for numeric fields: a clamped status line can legitimately disagree with what the raw input box still displays. Confirm the request used the clamped value (read it back through the API) before reporting a discrepancy; a truthful status line plus a raw input value is a cosmetic observation, not a defect.

## 6. API-level probes worth having in the corpus

Beyond UI claims, three cheap backend probes catch regressions a DOM suite never sees:

- **Idempotency of a retried mutation:** replay the byte-identical request and assert the response is equal and the generated child IDs are identical (not merely that both calls returned success).
- **Identity conflict:** same object id with a different payload must be rejected (`409 CONFLICT`), never silently replace.
- **Cross-tenant isolation:** a second registered account gets `404`/empty list for the first account's object and its parent record. Assert the *absence* of the id in the other account's list, not just the detail status.

Write the observed statuses and bodies to JSON; "isolation passed" without the status codes is not reproducible.
