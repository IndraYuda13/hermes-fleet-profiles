# Stateful regression recipes

## Authentication changes
1. Read the frozen server response contract before editing forms or fixtures. Separate signed-in success from confirmation-required success, and never turn registration into a claim of verified email.
2. Replace obsolete email-only test helpers with genuine registration/login fixtures. Keep credentials synthetic and in memory; disable secret-bearing traces and avoid serializing request bodies into logs.
3. Exercise signup → create data → logout → wrong/unregistered denial → correct login → same data identity. Check duplicate registration cannot replace the original credential or owner.
4. Test confirmation mismatch focus and zero network submission, busy/disabled state, service-unavailable retry, and confirmation-required copy. Label mocked confirmation tests as UI coverage, not proof of actual email delivery.
5. Seed sample identities through the normal isolated seed runner before sample-account scenarios; do not compensate for missing data with a public authentication bypass.

## Changed product paths and storage contracts
1. Read the actual rendered workflow before replacing a selector. An assessment purpose may already imply cards while a teaching purpose requires an explicit method choice. Open collapsed print sections before waiting for a download.
2. Preserve the intended scenario in shared helpers. Explicitly opt into existing demo routes for old adaptive scenarios instead of making real-class routes render obsolete UI.
3. When offline detail probes return undefined, inspect the current public client adapter and its cache namespace before changing app behavior. Use the current adapter rather than reading an obsolete internal table directly.
4. Build pending mutations through the strict current schema, including contract version, source, and answer-state fields. An unknown answer such as `?` can still be an answered state; do not invent a state enum from its display wording.
5. Assert queued edits survive an offline reload, reconnect drains the queue exactly once, server revisions/data agree, and logout locks cached reads. Keep older replay/migration checks distinct when they remain supported.
6. Bind PDF filename assertions to the documented form identity and version, not an assumed run ID or obsolete prefix.

## Measured pagination and projected tools
1. Run both legal one-screen content and lossless oversized-content traversal at the affected viewport. Preserve exact concatenated source text and stable total-count assertions.
2. Wait for fonts and observable pagination settlement after changing appearance before walking pages; fallback-font or resized geometry can repartition fragments under the reader. Assert the last activity page, not merely a transient disabled Next button.
3. Diagnose overflow with actual element rectangles, scrollHeight/clientHeight, computed styles, and a screenshot before patching. Inspect all matching CSS rules and their specificity: later board rules can override an earlier scoped repair.
4. Re-author only the bounded projected panel. Retain touch-sized controls and give table/model, operation controls, and feedback explicit space rather than hiding overflow or shrinking every surface.
5. Verify each tool before and after its Run/check feedback appears; a model that fits at rest can overflow when status copy adds a row. Cover the intended viewport sequence, not only an isolated tool render.
6. Re-run the combined affected selection once source is frozen. Classify residuals as setup failure, superseded expectation, actual defect, or cosmetic defer; never call unresolved content loss a cosmetic issue.

## Failing-first browser regressions on a build-gated runner
When the browser suite boots a production server, order the work so red and green are both real observations:
1. Build the pre-fix tree first and run the new spec. Capture the exact failure text (the missing/incorrect rendered state), not just a non-zero exit.
2. Apply the fix (or the config route change) and rebuild; the green run must come from a build that contains it. A server booted from a stale build reports the old rendered state and will disagree with the source.
3. Bring the failing spec and the fix into one commit so the red-to-green transition is auditable alongside the change that caused it.

Prove a rendered-defect assertion discriminates rather than passing for an unrelated reason: measure the target once with the fix in place, then re-inject the old rule with `page.addStyleTag({ content: "<old rule> !important" })` and measure again in the same run. A defect assertion that passes in both states is worthless; require the two measurements to straddle the threshold. For cut/overflow defects, measure the glyph bounds with `document.createRange()` over the cell's contents and assert the width is non-zero, because a collapsed grid track reports a zero-width cell that no `right <= row.right` comparison rejects.
Set the viewport to the defect width before opening and measuring the surface, and keep any temporary probe spec out of the commit — rerun the real gates on the final tree after deleting it.

## Portable evidence
Make new artifact roots configurable with defaults under the repository's artifact tree. Keep screenshots/downloads separate from test runner scratch output, which subsequent runs may clear. Report logs and evidence that still exist at handoff; do not cite deleted attachments as inspectable proof.
