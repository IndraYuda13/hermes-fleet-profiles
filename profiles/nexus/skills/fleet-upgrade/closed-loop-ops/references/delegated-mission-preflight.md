# Delegated Mission Pre-flight and Abort Report

Use when another agent, a plan file, or an orchestrator hands you an approved mission with an acceptance-criteria list. Pre-flight is cheap; discovering the gap after you have written artifacts is not.

## Pre-flight checklist

- [ ] Terminal state: what exactly counts as done, in the requester's words.
- [ ] Required operations: list every command/tool the mission's verification steps need (build, hash, render, package edit, visual check). Confirm each is achievable in this session's exposed tool surface.
- [ ] Path resolution: every skill and script path the mission names resolves inside THIS profile's skill directory. A path under another profile's directory is not available to you even if the file exists on disk.
- [ ] Write scope: exact output paths you may create; sources that are read-only; explicit prohibitions (no VCS init, no overwriting originals).
- [ ] Evidence binding: which hashes/artifacts the requester expects to be bound to the result.
- [ ] Gap report: any unmet item stated up front, with which acceptance criteria it blocks.

Decision: if a required operation is unavailable, report the gap and pause. Do not silently substitute a weaker check, and do not produce the artifact anyway.

## Abort report template

Keep it to the questions asked; no narrative, no remediation offer.

- Did a run start, and how far (read-only recon vs content writes)?
- Exact files changed: list them, or state none, and show the search that proves none were created.
- Confirmation: paused, no further action taken.
- Unavailable verification: name the specific check you could not run and why, without implying it passed.

## Evidence discipline

- claim_scope must stay within evidence_scope. If a check could not be run, mark that check BLOCKED rather than restating prior or assumed results.
- Do not reuse an integrity value from before a write; rebind evidence to the current revision or state that binding was not possible.
- Never present a plan, an approval, or another agent's confidence as evidence of a result.
