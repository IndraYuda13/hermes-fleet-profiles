# Pre-commit review reference

Review the actual diff and its surrounding call sites before committing. Check correctness, trust boundaries, error paths, public contracts, test coverage, and unintended generated/debug/secrets changes. Run the focused tests and configured lint/type checks. Report findings by severity with file/line evidence; distinguish blocking defects from optional cleanup.

For a pull request, read the metadata and changed-file list before the diff, check out the exact head when practical, and post only findings that remain valid after local verification.
