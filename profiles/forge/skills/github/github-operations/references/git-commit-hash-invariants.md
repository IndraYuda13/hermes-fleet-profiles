# Git Commit Hash Invariants & Manifest Pinning

## The Self-Referential SHA Fallacy (The Quine / Fixed-Point Trap)

A Git commit SHA is a cryptographic hash (SHA-1 or SHA-256) computed over:
`commit <size>\0tree <tree_sha>\nparent <parent_sha>\nauthor ...\ncommitter ...\n\n<commit_message>`

The `tree_sha` is the root hash of the Merkle tree containing every tracked file blob in that commit.

### The Infinite Loop Failure Mode
Attempting to record a commit's *own* SHA inside a tracked file within that same commit (e.g. `evidence/manifests/*.json` containing `"git_revision": "<HEAD_SHA>"`):
1. File content changes to insert `<HEAD_SHA>`.
2. The blob hash changes.
3. The root `tree_sha` changes.
4. `git commit --amend` calculates a new, completely different commit hash due to cryptographic avalanche effects (~50% bit flip).
5. Repeating `git commit --amend` in a loop will **never converge**. Finding a SHA fixed-point is computationally equivalent to finding a full hash collision.

## Correct Engineering Patterns for Evidence & Manifest Tracking

1. **Pin Evaluated Code Snapshot (Parent/Target SHA):**
   - Manifests and QA reports should record the `git_revision` of the code artifact that was actually tested/audited (e.g. `feat/implementation` commit or `HEAD~1`).
   - The subsequent evidence/closure commit records those manifests without needing to reference its own uncommitted SHA.

2. **External / Envelope Metadata:**
   - Store final release commit SHAs in external systems: Git tags (`git tag -a v1.0.0`), CI build envelopes, release notes, or database records outside the tree.

3. **Git Notes (`git notes`):**
   - If metadata must be attached to a commit after the fact without altering tree hashes, use Git notes: `git notes add -m '{"qa": "PASS"}' <COMMIT_SHA>`.
