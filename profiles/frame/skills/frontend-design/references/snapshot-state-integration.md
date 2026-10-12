# Snapshot and state integration workflow

Use for teacher workflows, editable assignments, printable forms, offline queues, or autonomous shared screens backed by versioned server state.

## 1. Trace the integration boundary before implementation
1. Read the frozen action/DTO types, route layout/provider conditions, cache schemas, outbox consumers, existing renderer callbacks, and post-build/offline-shell checks.
2. If a route must remain prerendered, keep its server page static and resolve query-driven workflow branches in a client entry. Exercise initial load, same-route navigation, and back/forward behavior; do not weaken the offline build invariant to accommodate a dynamic page.
3. Separate legacy and negotiated protocol paths. Preserve old stores and parse strict DTOs at boundaries; use protocol-specific owner-scoped cache keys for new fields.
4. Trace the source of each visible claim: server receipt, immutable assignment snapshot, local draft, pending queue, or public projection. A sidecar mapping must remain outside a strict content document and freeze with its version.

Do not infer a new response method from an old mode field when both combinations are valid; that loses intent on offline reload. Do not feed arbitrary quiz scores into an existing placement engine just to satisfy its required type; the underlying evidence domains may be incompatible.

## 2. Persist preparation before printing or starting
1. Save the assignment and obtain authoritative run/form/version/roster bindings.
2. Generate preview and PDFs from that saved snapshot, not the live collection editor.
3. If method, collection, version, or membership changes, replace the assignment binding as required by the server and invalidate print confirmation. Unchanged assignments retain their exact binding.
4. Begin using the same saved snapshot; report stale readiness as requiring explicit re-prepare/reprint rather than silently replacing a form.
5. Provide a discoverable resume path for saved drafts, not only a URL captured immediately after creation.

Keep document-download success separate from the teacher's confirmation that paper is prepared. Keep group completion, class closure, and assessment completion separate so late individual responses cannot reopen a public screen.

## 3. Implement asynchronous answer/progress safely
1. Carry assignment ID, revision, task epoch, channel epoch, and request ID from the current authorized state.
2. Lock mutations synchronously before awaits. Save an answer, await its receipt, then check using the returned revision; never submit caller-derived correctness.
3. Retain the exact failed request for idempotent retry. If retrying an answer succeeds, continue the check phase; if authorization or epoch changes, refetch/reconcile instead of blindly replaying.
4. Ignore lower-revision polling results for the same binding. Clear the projection on access revocation and prevent stale local selections from crossing task epochs.
5. For existing manipulatives with synchronous local-check callbacks, provide a bounded remote-check mode that bypasses local correctness feedback while retaining legacy behavior outside that mode. Do not return a fabricated boolean while an async server check is pending.
6. Encode exact-number models through the contract's wire adapter before JSON serialization and decode after readback; native BigInt cannot be directly serialized.

Retain unsent input visibly on transport loss and distinguish retry from discarding it to load another device's progress.

## 4. Preserve response meaning through scan, draft, and queue
- Map scanner row status, not whole-scan status, to blank versus unreadable. Explicit “don't know” is an observed answer, never a placeholder for missing marks.
- Persist nullable answers with explicit row states. Unresolved review is not accepted evidence.
- Display pending writes from the protocol's actual outbox without optimistic grading. Emit a sync notification and reread accepted results after receipts.
- Prevent unsent same-pupil edits from silently replacing a queued predecessor; expose reconciliation or block until sync when the queue API cannot preserve correction ordering.

## 5. Verify saved PDF output and reached browser states
1. Generate the real PDF bytes with the actual embedded font. Enforce an allowlist before asynchronous work so keys, roster, names, or editor-only data never reach content or metadata.
2. Reuse fixed answer-card geometry unchanged. Test question PDFs separately with long prompts/options and unbroken tokens.
3. Extract saved PDF text with `pdftotext` to check complete content and order; render every page with `pdftoppm -png` and inspect wrapping, clipping, and footer overlap. Decode QR from saved output, not merely the source drawing calls. For paired question/answer sheets, assert the same human-readable form code and version on both saved PDFs as well as the authoritative QR binding; a machine-readable binding alone does not let teachers match paper safely. Measure the longest permitted header against the QR/marker/bubble exclusion zones before adding readable identity.
4. Run targeted unit files with the project's test runner and reconcile its matched-file and test counts. A nonexistent path may be ignored while other files pass.
5. Once the backend is ready and writers are quiescent, run the complete project build, including post-build/offline generation, then exercise the positive browser journey against the resulting production-style server and isolated real backend. Record the last reached assertion when a prerequisite fails; rerun previously blocked journeys instead of carrying forward their error-only evidence.
6. Synchronize tests with the mutation that just happened: await the destination URL before extracting route identifiers, and await editor closure or a fresh receipt before asserting corrected server state. A still-visible success message from an earlier save is not evidence that the next save completed.
7. Match mathematically formatted choices semantically, because fraction markup can split their accessible names. Keep separate assertions for displayed content, chosen option, and server feedback rather than requiring a plain-text name that the actual renderer does not produce.
8. Capture normal, empty, and unavailable renders as separately labelled evidence. Inspect selected/submitted answer styling in pixels, not just ARIA state. After a visual repair, rebuild and rerun affected browser tests on that revision. Keep physical printer/camera certification separate from synthetic render/QR/OMR tests.

## 6. Bounded source-quality cleanup before review
1. Inventory comments in owned feature/UI files and inspect their full blocks. Remove historical audit narration, not identifiers or executable strings that happen to contain a matching word.
2. Replace a verbose comment with a short rationale when it protects a non-obvious invariant, such as stable pagination, lazy landmark height, or sent-versus-applied acknowledgement. Delete commentary that merely narrates a prior change.
3. Extract a cohesive presentational panel or read-only summary verbatim first, then introduce explicit typed props. Leave orchestration state and network mutations with the existing owner; avoid a broad refactor during a release-bound cleanup.
4. Apply cleanup in bounded batches below the tool-call budget. Check each edit result and persist the successful changed-path list before continuing; a loop finishing does not mean edits after a tool limit succeeded.
5. Format and lint explicit owned paths, run TypeScript, and compare protected backend paths against the frozen revision. Stage only the intended frontend files and preserve unrelated generated QA changes.
6. Build the complete candidate and rerun affected positive and empty-state browser journeys on the cleanup revision. Regenerate screenshots/downloads before handing the frozen source to independent review; unchanged PDF generator/geometry does not justify claiming a new physical-device test.

## 7. Shared-runtime handoff
Before rebuilding a shared candidate, inspect listener PIDs, parent supervisor, working directory, and runtime ownership; an active server may still depend on the same `.next` directory. Stop only processes you own, or request that the runtime owner stop theirs before overwriting build artifacts. After stopping them, inspect listeners before claiming ports free: another worker may have legitimately started a newer runtime. A free-port guard can fail on an already-running isolated server without proving a production collision; reconcile process ownership and environment identity before further tests, never kill the unknown listener for convenience. If no listener remains but the bind check still fails, allow a bounded foreground cleanup interval and rerun the unchanged guard rather than weakening isolation checks.

Report owned commit, explicit changed paths, commands/exits, matched counts, artifacts, reached states, and residual blockers. Full integrated build and independent review belong to the quiescent combined revision, not confidence inferred from a frontend-only compile.
