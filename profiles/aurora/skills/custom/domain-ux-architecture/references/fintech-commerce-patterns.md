# Fintech Commerce Patterns

## Checkout and order integrity

- Keep checkout on one scoped page: select product, preserve the relevant identity draft, perform a cancellable inquiry, select a nominal, then enable a gated payment action.
- Debounce identity inquiries and discard stale responses, but do not block a valid checkout solely because an upstream verification service is slow; explain uncertainty clearly.
- Calculate final price, fees, and stock from server-owned SKU data, rate-limit public inquiries, and never expose supplier cost or internal SKU details.
- Treat payment as explicit states—pending, received, provider processing, delivered, expired, and failed—and recheck status when the tab becomes visible after a banking-app switch.
- Protect fulfillment with authenticated webhooks, timestamp validation, idempotency keys, short-lived payment stream tokens, and an atomic transition from pending to submission.

## Conversion and retention

- Allow guest purchase with minimal delivery contact, retain local order continuity, and offer account conversion only after a successful payment.
- Use one-time, signed, short-lived deep links for cross-channel account binding, and allow customers to locate orders by stable ID or verified contact.
- For same-device QR payments, provide gallery save and copyable payload alternatives; users cannot scan the QR code displayed on their own phone.

## Product catalog and media

- Reserve 3:4 cover-card geometry before images load, serve modern image formats with fallbacks, and degrade to a branded monogram when artwork fails.
- Use catalog cards to expose selection-relevant variants such as duration, account type, stock, and price without forcing a deep detail page.
- Show selected-product identity again in the order ledger using a restrained banner and readable logo; confirmation media should reduce purchase anxiety, not compete with the transaction.
- Use tabular numerals and locale-correct currency formatting on all dynamic totals, countdowns, and nominal matrices to prevent layout jitter.

## Responsive, tactile, and performance constraints

- Replace desktop-only rails with an expandable order summary or bottom action dock on small screens, then reserve safe-area and virtual-keyboard clearance in the scroll region.
- Convert dense category grids to horizontally scrollable tracks and preserve 44px targets; never hide root overflow merely to suppress a layout defect.
- Make checkout interactions silent by default and use optical feedback or permitted vibration; payment contexts should not emit ambient or click audio without an explicit product requirement.
- Bound heavy visual effects: pause offscreen or hidden rendering, clamp pixel ratio, preserve form hit testing above decorative layers, and animate transforms rather than layout properties.
- Use larger cinematic composition only when authentic content and performance budgets support it; conversion controls must remain fast, legible, and reachable at every stage.
