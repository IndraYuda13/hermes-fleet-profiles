---
name: verification-gate
description: Final-claim and evidence-discipline overlay for coding, automation, reverse engineering, ops, and multi-step technical work. Use when the agent is about to say a task is done, fixed, confirmed, works, blocked, impossible, or otherwise make a high-confidence claim. Enforce success oracles, downstream proof, checklist sync, note sync, and precise wording for partial progress.
---

# Verification Gate

Use this skill before making a strong claim.

Strong claims include:
- done
- fixed
- confirmed
- works
- solved
- blocked
- impossible
- root cause found

## Gate 1. Name the claim type

Decide which claim is being made:
- success claim
- blocker claim
- root-cause claim
- partial-progress claim

Different claims need different proof. Do not use one type of proof to justify another type of claim.

## Gate 2. Define the oracle

Write the exact oracle.

Examples:
- target test passes
- exact final URL or downstream response matches expectation
- service restart is followed by healthy process plus real successful task outcome
- seller flow reaches the downstream balance/update state, not just an intermediate success message
- reverse-engineering claim is backed by trace/xref/hook/packet evidence, not function-name vibes

If there is no oracle, the claim is not ready.

## Gate 3. Check downstream proof

Ask:
- is the proof only intermediate?
- is it only UI movement?
- is it only a pretty log line?
- did the claimed downstream effect really happen?

If the downstream effect is not proven, downgrade the wording.

## Gate 4. Match wording to proof

Allowed wording depends on proof quality.

- Use **confirmed / fixed / works** only when the oracle is satisfied.
- Use **likely / narrowed / partial / pending verification** when evidence is strong but the oracle is not closed.
- Use **blocked by X** only when the blocker is real and the next reasonable lane has been checked.
- Do not say **impossible** unless the relevant lanes were actually tested or ruled out by hard constraints.

## Gate 5. Sync state before reporting

Before sending the result:
- update the top-level checklist
- update the relevant note, roadmap, or boundary record
- update the project change log if code changed
- if this lives in its own repo, finish repo hygiene
- if this is workspace knowledge, run the workspace backup lane

## Gate 6. Report plainly

Final report should include:
- active step
- result
- proof
- meaning
- next step or remaining risk

Read `references/oracle-patterns.md` when choosing proof for a claim.
Read `references/blocker-claims.md` when the result is negative or incomplete.
