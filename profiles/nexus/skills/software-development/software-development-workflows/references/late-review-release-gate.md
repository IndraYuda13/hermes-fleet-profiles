# Late Review and Release-Gate Reopening

Use this procedure when an independent reviewer or delegated audit finishes after implementation, promotion, or an earlier completion message.

## 1. Do not outrun pending reviews

Before a final completion claim, check whether any requested reviewer, delegated audit, CI job, visual inspection, or browser matrix is still running.

- If a consequential review is pending, report `implementation complete, review pending` rather than `final`.
- A completed happy path, clean console, hashes, and Lighthouse score do not substitute for the review that was explicitly requested.
- Keep the release checklist open until the review handle has returned or the user explicitly accepts skipping it.

## 2. Anchor late feedback to a revision

A late review may describe source that no longer exists.

1. Record the reviewed commit or file hashes from the reviewer.
2. Compare them with current `HEAD`, the working tree, and the public assets.
3. Classify each finding as:
   - stale and already removed,
   - still applicable to current source,
   - unclear and requiring a fresh reproducer,
   - a test-harness failure rather than a product defect.
4. Never patch current code merely because an old line number appears in a report.

For live frontends, reproduce against current local `HEAD` first, then the public URL after promotion.

## 3. Reopen the gate when a finding is real

If a late finding reproduces against current source:

1. State plainly that the prior completion status is withdrawn or downgraded.
2. Reopen the checklist and create an isolated branch/worktree from current `main`.
3. Write the smallest regression check that fails on the current defect.
4. Patch the lifecycle or contract, not just the visible symptom.
5. Re-run the exact reproducer plus the broader relevant suite.
6. Merge, rerun from `main`, and repeat public verification.
7. Only then restore the completion claim.

This is normal release-gate behavior. Hiding the reversal is worse than the defect.

## 4. Isolate runtime probes

Browser audit scripts can contaminate their own later steps.

- Use a fresh navigation or browser context for each independent case.
- Close/reset open dialogs before the next case.
- Scope modal controls to the active dialog. A selector matching two hidden close buttons is a harness error, not an app failure.
- Verify that the chosen localhost port serves the intended app before interpreting browser output. An occupied port may expose an unrelated service.
- When an automation step times out, inspect interception, open dialogs, stale focus, and selector strictness before labeling the product broken.

Keep harness failures separate from product findings in the report.

## 5. Use meaningful visual oracles

A geometric condition can technically pass while the design still fails.

Bad oracle:

```js
card.getBoundingClientRect().top < innerHeight
```

That accepts a one-pixel sliver of a card.

Prefer an intent-bearing oracle, for example:

- the category icon and title are both visible,
- the title bottom is within the initial viewport,
- a useful minimum portion of the card is exposed,
- visual inspection confirms that the exposed content reads as an invitation to continue.

If compression or vision tooling times out, retry with a smaller image and use direct browser inspection plus DOM measurements as fallback. Do not silently convert a failed visual audit into a pass.

## 6. Public freshness remains part of the reopened gate

After the fix:

- bump nested asset URLs in HTML,
- confirm `document.styleSheets` and script URLs use the new token,
- compare hashes for the exact fetched live asset URLs,
- rerun the original late-review reproducer against the public page,
- capture fresh desktop and mobile screenshots.

Origin hash equality alone does not prove the browser rendered fresh nested assets.

## Completion oracle

A late-review closure is complete only when:

- every finding is classified against the current revision,
- applicable findings have red-to-green regression evidence,
- harness-only failures are documented as such,
- tests pass again from merged `main`,
- the public browser loads the intended asset versions,
- the original runtime symptoms no longer reproduce publicly,
- no requested reviewer or release job remains pending.
