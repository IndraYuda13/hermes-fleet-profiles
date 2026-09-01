# Progress Discipline for Reverse Engineering Sessions

## Why this exists

Reverse-engineering work decays fast across resets when milestones live only in short-term context. The fix is simple: write the milestone down immediately.

## Mandatory rule

For any meaningful progress point, persist it before continuing too far.

A meaningful progress point includes:
- a newly pinned method/function/selector/address
- a confirmed blocker that rules out a false path
- a failed probe that saves future time
- a real artifact capture such as a dump, trace, or registration table
- a strategy pivot such as moving from static lifting to app-driven oracle patching

## Minimum note contents

Every persisted milestone should answer:
- What is now proven?
- What is still unproven?
- What was tried and failed?
- What should not be retried blindly?
- What is the narrowest next best action?

## Anti-patterns

Do not rely on:
- mental notes
- chat-only summaries without file updates
- vague phrases like "almost there" without artifact references
- carrying offsets/addresses between sessions without revalidation against the current binary

## Checklist rule
- Each active reverse-engineering target should have a live checklist in structured notes.
- Minimum statuses:
  - DONE
  - IN PROGRESS
  - NOT STARTED
- Add new checklist items when new relevant subproblems are discovered.

## Execution bias
- Try to complete the active checklist item in one run.
- Do not keep stopping with unnecessary "continue?" questions.
- Pause only when there is a real blocker, missing critical input, or a risky/destructive boundary.

## Parallelism rule
- If reverse-engineering subtasks are independent, parallel sub-agents are encouraged.
- Good examples: artifact triage, static string scans, endpoint extraction, config comparison, and note synthesis.

## Clarification rule
- For a fresh target, research the artifact structure first and form a checklist before asking clarifications.
- If the modding/reverse-engineering goal is still ambiguous after research, ask with concrete option sets based on what the artifact appears capable of changing.

## Practical workflow

1. Before continuing an existing target, re-read the relevant structured notes first.
   - Minimum recall set:
     - active case note under `references/lessons/cases/`
     - relevant reusable pattern notes under `references/lessons/patterns/`
     - `references/investigation-ledger.md` if the target is tracked there
2. Refresh or extend the checklist for the target.
3. Run the active probe or implementation step.
4. Save artifact/log/dump.
5. Update active case note and checklist state.
6. If reusable, append a one-line pointer into `INDEX.md`.
7. Only then continue to the next probe.

## Distilled lesson

If a reverse-engineering milestone is not written down, treat it as non-durable and likely to be lost on reset.
