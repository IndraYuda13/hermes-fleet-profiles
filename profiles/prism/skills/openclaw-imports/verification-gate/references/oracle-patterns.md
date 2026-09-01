# Oracle Patterns

Choose the oracle that matches the claim.

## Coding fixes
- targeted test passes
- exact failing command now exits cleanly
- exact output now matches expected result

## Automation and bot flows
- downstream state changes as expected
- final URL / response / balance / status is correct
- not just a button click, callback, or intermediate message

## Ops work
- process is alive
- service is healthy
- one real post-restart task succeeds

All three are often needed for a strong ops success claim.

## Reverse engineering claims
- xref or trace proves the caller/callee path
- hook or packet proves runtime behavior
- patch or replay proves the claimed effect

## Research or diagnosis
- artifact backs the conclusion
- strongest alternative explanation was checked or falsified

## Quick downgrade rule
If only intermediate proof exists, say `partial`, `narrowed`, or `pending verification`, not `confirmed`.