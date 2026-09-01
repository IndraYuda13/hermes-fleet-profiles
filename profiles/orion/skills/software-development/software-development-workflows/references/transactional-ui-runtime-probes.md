# Transactional UI Runtime Probes

Use these read-only probes when reviewing checkout, account, tracking, timer, search, dialog, or animated mockup flows. Static checks often miss stale async state and native browser behavior.

## 1. Lock the reviewed source

- Hash the files before runtime testing and again before reporting.
- If hashes or mtimes change without your edits, state that concurrent work occurred, reread the changed files, rerun checks, and anchor findings to the final hashes.
- Do not silently combine line numbers from one revision with runtime behavior from another.

## 2. Probe state invalidation and delayed effects

For every delayed callback, timer, promise, or simulated status transition:

1. Start the effect.
2. Navigate back, edit/reset the order, or select another parent before it completes.
3. Wait for the old effect.
4. Assert that it cannot mutate the replacement order or summary.

A callback should carry an operation/invoice identity and verify it is still current, or be cancelled during reset. Test child-state reset both synchronously and after pending effects complete.

## 3. Test native form submission, not only clicks

For forms inside native `<dialog>` elements, test all of:

- Clicking the intended submit button.
- Pressing Enter in every text input.
- Escape dismissal.
- Close control.
- Initial focus and focus restoration.

`<form method="dialog">` plus logic gated on `event.submitter` can close silently on implicit Enter because `submitter` may be absent. Verify the action happened before concluding keyboard support works.

## 4. Keep payment instructions mutually consistent

Exercise every payment method, not only the default. Compare selected method, fee, total, action copy, QR/deeplink/balance instructions, expiry, tracking state, and final status. A generic QR screen after selecting wallet or stored balance is a transaction-consistency defect even when totals are correct.

## 5. Timer correctness

Check that a payment timer:

- Does not reset on ordinary rerender.
- Uses an absolute deadline so background-tab throttling cannot extend validity.
- Enters a real expired state at zero.
- Disables or replaces actions after expiry.
- Is cancelled or invalidated when leaving/resetting/replacing the order.

## 6. Validate product-specific destination constraints

Minimum length plus numeric-only is rarely sufficient. Probe empty, nondigit, shorter, exact, longer, extremely long, whitespace, pasted separators, and product-specific values. Match visible helper text to executable min/max/exact/pattern rules.

## 7. Compose motion pause reasons

Intersection and page visibility are independent pause reasons. Do not let separate handlers blindly toggle one class. Probe this sequence:

1. Move the animated stage off-screen and confirm pause.
2. Hide the document.
3. Restore visibility while it remains off-screen.
4. Confirm it is still paused.

Derive pause from `document.hidden || !stageVisible || reducedMotion`, then update the class from that combined state.

## 8. Search accessibility runtime checks

Beyond Arrow/Enter behavior, inspect the accessibility contract: combobox role where applicable, expanded state, listbox relationship, option IDs, active descendant, Escape behavior for populated and empty results, and announcement of empty state.

## 9. Evidence discipline

Report source line, exact reproduction sequence, expected versus actual behavior, and user/transaction impact. Passing static tests do not override a failed runtime probe.