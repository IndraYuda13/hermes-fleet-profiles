# Read-only engineering artifact audit

Use this for architecture/ADR, implementation-plan, build-log, and phase-gate reviews where files must not be changed.

## 1. Anchor the reviewed snapshot

Before judging content, record the branch, `HEAD`, working-tree status, and hashes of reviewed artifacts. Re-check these at the end because parallel workers or the author may update files during the audit. If hashes changed, classify findings against the final snapshot instead of silently reporting stale line numbers.

State explicitly that the review was read-only and list any files changed by the reviewer, normally none.

## 2. Review ADR quality

For each ADR verify:

- context/problem and binding constraints are clear;
- decision is specific enough to implement;
- alternatives and rejected options are recorded;
- consequences and operational trade-offs are stated;
- terminology and state ordering match architecture diagrams and plans;
- unresolved ambiguity is represented as a caveat, not hidden by `Accepted` status;
- dependency or upstream claims are pinned to reproducible versions/commits.

Pay special attention to authorization terms such as `signed`, `approved`, `immutable`, and `append-only`. Require precise semantics rather than security-flavored wording.

## 3. Review plan actionability

A roadmap is not automatically an executable implementation plan. An actionable plan should provide:

- exact create/modify/test paths;
- small, independently verifiable tasks;
- dependency order and phase gates;
- exact commands and expected RED/GREEN outcomes;
- concrete acceptance oracles;
- explicit commit/checkpoint boundaries;
- decomposition of oversized checklist items.

Flag one-checkbox epics such as “implement all adapters/skills” even when overall phase ordering is sensible.

## 4. Review build-log evidence

Separate honest status reporting from reproducible proof.

A useful build log records:

- commands verbatim, not prose that merely describes a command;
- timestamps, tool versions, exit codes, and sanitized stdout/stderr;
- commit/tree identity or file hashes tied to the result;
- failures, retries, unresolved reviews, and pending gates;
- external probes with request shape and response metadata but no credentials.

A line like `GATE_PASS` is weak evidence if the repository contains neither the runnable gate nor the digests/inputs that produced it. Downgrade the claim rather than assuming the result is false.

## 5. Secret review and claim discipline

Scan the whole relevant tree, including untracked artifacts, for high-signal credential formats and suspicious assignments. Manually classify placeholders, local example credentials, hashes, and real secrets.

Use bounded wording:

- Good: “No secret material was found in the reviewed repository snapshot.”
- Too broad: “The key was never printed or logged.”

Repository inspection cannot prove historical absence from terminals, external logs, deleted files, or unrelated systems. If no dedicated scanner is available, disclose that regex/manual review was used instead of presenting equivalent assurance.

## 6. Cross-artifact consistency checks

Trace key contracts through ADRs, architecture, plan, build log, and master specification:

- stage and state ordering;
- success, rejection, timeout, cancellation, and uncertain-result paths;
- optional operation versus mandatory authorization;
- dependency versions and lock strategy;
- trust boundaries and mutation access;
- phase status, checked boxes, and pending reviews.

Draw the missing negative branches mentally. A happy-path diagram can look consistent while rejected or expired flows have no terminal report path.

## 7. External evidence

When feasible, verify pinned upstream metadata and referenced source locations directly. Distinguish:

- source version from published package version;
- declared compatibility from an actually exercised compatibility probe;
- upstream documentation claims from local runtime observations.

Do not re-run secret-bearing probes merely to validate prose unless authorization and redaction controls are explicit.

## Report format

Lead with a verdict such as `PASS`, `PASS WITH NOTES`, or `NEEDS CHANGES`. Then list findings in descending severity with:

- severity;
- exact file and line/range;
- why it matters;
- concrete repair.

Finish with positive observations, secret-scan scope/limitations, snapshot identity, and read-only/no-change confirmation.
