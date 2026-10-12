# Runner filesystem and database isolation

Use when verifying test runners that write generated logs or depend on prepared external databases.

## Procedure
1. Inspect every actual output write and every runner mode before editing. Include dynamic paths and outputs written earlier than another output sharing their directory.
2. Build an artifact-free source copy with `git archive <revision>` extracted into a new managed scratch directory. If verifying uncommitted runner changes, overlay only the owned files. Reuse dependencies through a symlink when suitable; do not copy ignored artifact directories or remove artifacts from the user's working tree.
3. Read database identity, server port, migration ledger digests and relevant test-default configuration before running SQL. Set the test connection explicitly. A matching database name alone does not prove schema or configuration compatibility.
4. Reproduce the original runner failure in the clean copy without running prepare. Preparation can create the missing output directory and mask the bug.
5. Route every artifact write through one helper that runs `mkdir(dirname(path), { recursive: true })` immediately before `writeFile(path, content)`. Keep default paths repository-relative; do not encode the verification host's scratch paths. Let filesystem errors propagate.
6. Run the original mode and full relevant runner mode from separate fresh source roots after the final edit. Exercise all distinct output paths with the exact helper on the real filesystem, including repeat writes and mode-specific dynamic outputs that the full mode does not cover.
7. If SQL fails before later writes, distinguish database-state incompatibility from filesystem regression. Read the ledger/configuration and use a compatible already-prepared isolated database when available; do not alter SQL, reset schemas or change policy defaults merely to make a runner-only fix pass.
8. Run scoped lint, formatting and diff checks. If a package-manager exec unexpectedly attempts dependency installation or module removal, stop that mutation and invoke the already-installed local tool entry point directly when available, such as `node node_modules/eslint/bin/eslint.js <owned-file> --max-warnings=0`.
9. Keep an untracked handoff with revision, runner hash, explicit database identity, reproduction and final commands, exit codes, output inventory and residual limits. Preserve failed-run evidence with its reason; do not present a partial SQL run as a complete suite pass.

## Failure mechanisms to guard
- Create parents at each write, not only during prepare or a preceding branch: fresh checkouts omit ignored artifact directories and mode ordering changes which directory exists first.
- Test absent-directory behavior on real filesystems: mocks and existing artifacts hide ENOENT failures.
- Keep database migration digest and configuration checks separate: current migrations can coexist with mutable policy state that violates suite assumptions.
- Avoid preparation or resets during a narrowly scoped runner repair: those actions mutate test state and can conceal the original defect or interfere with another verifier.
