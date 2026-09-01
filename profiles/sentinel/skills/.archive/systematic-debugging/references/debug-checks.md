# Debug Checks

Use this short checklist before saying the bug is fixed.

## Root-cause check
- Can I point to the narrow faulty boundary?
- Did I prove it with evidence, not just intuition?
- Did the fix target that same boundary?

## Regression check
- Did I verify the original failure is gone?
- Did I check the nearest adjacent lane that could break from this patch?
- Did I avoid unrelated changes?

## Documentation check
- Did I update the project change log or structured note?
- Did I write down the durable lesson if it will save time later?

## Delivery check
- Am I claiming more than the oracle proves?
- If any doubt remains, did I downgrade the wording?