---
name: revision-bound-evidence-audit
description: Verify claims against a frozen revision's fresh evidence.
version: 1.0.0
author: PRISM
license: MIT
metadata:
  hermes:
    tags: [verification, evidence, revision-binding, audit]
    category: fleet-upgrade
---
# Revision-Bound Evidence Audit

## When to Use
Any verification where the verdict is bound to a specific commit/build (frozen revision,
deploy candidate, release gate). Especially when an evidence tree has accumulated across
several work sessions and runs.

## The failure this prevents
An evidence directory that grew over a long campaign contains artifacts from MULTIPLE
revisions. Citing a fresh-looking JSON whose mtime predates the frozen commit silently
launders old results into a new verdict. File names like `claim3-pagination.json` do not
carry their revision.

## Procedure
1. Record the revision at task start into a preflight file next to the evidence
   (`git rev-parse HEAD` plus the build id/token). Capture it once and cite that file.
2. Before citing ANY artifact, compare its mtime against the commit time AND the build
   time. Anything older than both is stale for this revision.
3. Where an acceptance criterion rested only on stale evidence, RE-MEASURE it fresh.
   Do not carry the verdict across on the assumption that nothing changed; layouts and
   strings do change between revisions.
4. Where a stale artifact is still informative (e.g. an A/B negative control proving a
   spec is discriminating), keep it but label it explicitly stale and superseded, and
   never let it carry the verdict alone.
5. Assert the claim in the direction that fails. A measurement that is true in both the
   fixed and broken states is not evidence: verify the same probe flips when the fix is
   reverted, or measure the broken state directly.
6. State, in the report, exactly which artifacts are fresh and which are historical, so
   the next reader does not repeat the audit. Name the stale patterns (paths/globs).

## Reading run logs (harness exit codes lie)
A wrapper of the form `cmd > log 2>&1; echo "EXIT=$?" >> log` makes the SHELL's exit status
the echo's status, not the test result. Background-process notifications report that shell
status, so they read `exit 0` even when the suite failed (`1 failed ... EXIT=1` in the log),
and read `exit 1` only when the redirect/echo itself failed. Never take the notification's
exit code as the outcome: open the log and read the summary line (`N passed`, `N failed`)
and the appended `EXIT=` value, which IS the real exit code.

Also check WHICH tests a log contains before trusting it as coverage. A Playwright command
with no positional spec filter runs only the default project match, so a log named like a
full-suite run may hold 2 of 12 probes. `grep -oE '<name>\.spec\.ts' log | sort -u` and a
test-count check settle it. And never redirect onto a log the report cites; use a new
filename, or a later re-run silently overwrites evidence.

## Distinguishing probe defect from product defect
A failing probe is not a finding until you read the failure. Causes I have actually seen in
raw logs:
- asserting a render-all-at-once count when the UI paginates (`toHaveCount(5)` vs
  `Received: 4`) — assert per page and walk pages
- `.check()` on an animated/off-screen control: fails as "Clicking the checkbox did not
  change its state" with "element is not stable" — use `scrollIntoViewIfNeeded()` then a
  single `.click()`
- a locator filter that can never match because the text has a suffix, e.g.
  `getByText("Kelompok 1", { exact: true })` against the heading "Kelompok 1 · 1 siswa"
  (times out, resolves to nothing)
- asserting an element is visible while it sits inside a collapsed disclosure

Rule: quote the raw error line (`Error:` plus the `Call log` detail) into the report, and
count the failing runs. A cause carried over from memory is usually wrong — I have written
"probe called .check() twice" and "getByRole status collided" from recall when neither was
the actual failure. If no log shows the failure, withdraw the claim instead of narrating it.

Log each discarded probe and its cause so it is not re-derived as a product finding.

## Verification
A verdict is admissible only when every load-bearing citation is timestamped after the
frozen commit, or is explicitly marked stale and excluded from the verdict.
