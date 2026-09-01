---
name: error-learning-loop
description: Persist mistakes and self-improvements so future sessions avoid repeating errors. Use when the assistant makes a mistake, receives corrective feedback, performs post-mortem on failed output, or is asked to improve behavior permanently through memory and workflow updates.
---

# Error Learning Loop

When a mistake happens, convert it into a permanent improvement.

## Execute This Flow

1. Acknowledge the mistake clearly in one sentence.
2. Classify the mistake type:
   - factual error
   - instruction-following error
   - tool usage error
   - safety/boundary error
   - communication/tone error
   - language-selection / locale error

3. Identify root cause in one short paragraph.
4. Apply the immediate fix for the current task first.
5. Persist the lesson so it survives session resets.
6. Add a prevention rule/checklist item for future tasks.

## Specific Language and Local Preferences

- **Language Preference Enforcement**: If the user's profile specifies a certain language (e.g. Bahasa Indonesia: `SELALU gunakan Bahasa Indonesia`), ALL conversational, summary, and response outputs (except raw technical logs or code blocks) must remain strictly in that language.
- **Tone/Style Mismatch**: Under no circumstances should the agent switch to or leak unrequested regional dialects/slangs (e.g. Javanese, Sundanese) unless the user explicitly initiates or requests it. Maintain the default defined language profile throughout the turn.

## Scope Guardrails

- This skill does not override the current task's domain skill; fix the user-facing problem first.
- Use this skill for correction/post-mortem, not as a general operating mode.
- Respect session privacy boundaries when writing memory.

## Persistence Rules

Record each important mistake in `memory/YYYY-MM-DD.md` using this template:

```md
## Mistake Log - <time>
- Id: ERR-YYYYMMDD-XXX
- Status: pending | resolved
- Type:
- Context:
- What went wrong:
- Root cause:
- Correct action:
- Prevention rule:
- Follow-up needed:
- See also: <optional previous ids>
```

If the lesson is broadly useful and you are in the main direct session, also update `MEMORY.md` with a distilled rule.

If the lesson is workflow-specific, update the most relevant operational file:
- `AGENTS.md` for behavior rules
- `TOOLS.md` for environment/tool specifics
- skill files for domain procedures

In shared/group/subagent contexts, prefer the daily memory file or the relevant skill/ops file instead of `MEMORY.md`.

## Recurrence Handling

If a similar mistake appears again:
1. Link the new entry to old entry IDs in `See also`.
2. Escalate prevention with a tighter checklist/guardrail.
3. Promote one concise permanent rule to `MEMORY.md` only when recurrence >= 2 and the current session is allowed to edit it.

Use conservative promotion: only promote when clearly recurring and broadly useful.

## Quality Bar

Before finishing, verify:
- The current user-facing output is corrected.
- At least one persistent note is written.
- The prevention rule is specific and testable.
- No sensitive data is copied into long-term memory unless explicitly requested.

## Detection Triggers

Run this loop immediately when:
- the user explicitly says the response is wrong/misleading
- tool output contradicts the drafted answer
- a command fails unexpectedly
- a recurring complaint appears for the 2nd+ time

## Conflict Resolution

When old memory conflicts with new instruction:
1. Most specific instruction wins.
2. Most recent explicit user instruction wins.
3. If still ambiguous, ask briefly.

## Memory Boundaries

Never store in long-term memory unless the user explicitly asks:
- passwords, API keys, tokens, secrets
- financial credentials / seed phrases
- sensitive third-party personal data

## Transparency Rule

When applying a learned rule, mention it briefly when relevant.
Example:
- `I'm using your saved preference: single-query fast check first.`

## Response Style

Keep apologies brief, then focus on corrective action and prevention.
Prefer:
- `You're right, fixed. I logged the lesson so I won't repeat it.`
