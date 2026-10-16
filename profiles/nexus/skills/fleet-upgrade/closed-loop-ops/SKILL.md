---
name: closed-loop-ops
description: Track obligations until a true terminal state.
version: 1.0.0
author: Fleet Upgrade Research
license: MIT
metadata:
  hermes:
    tags: [operations, follow-up, tasks, reminders]
    category: fleet-upgrade
---
# Closed-Loop Operations

## When to Use
Use for follow-ups, approvals, applications, bookings, reminders, delegated admin, or any task whose completion depends on a future action or response. Also use before executing a delegated multi-step mission handed to you by another agent, a plan file, or an orchestrator: the mission is itself an obligation, and pre-flight is part of closing it.

## Pre-flight before accepting a delegated mission
Do this before any artifact is produced; it is the cheapest point to fail.
1. Enumerate the operations the mission requires (build, hash, render, visual check, package edit) and confirm each is achievable with the tools actually exposed in this session.
2. Resolve every skill and script path the mission names against THIS profile's own skill directory; a path under another profile's directory does not exist for you even if it exists on disk.
3. Confirm write scope: the exact output paths you may create, and the sources that are protected read-only.
4. Report any confirmed gap to the requester before starting, stating which acceptance criteria cannot be met.
Checklist and abort-report template: references/delegated-mission-preflight.md.

## Procedure
1. Define the true terminal state (approved, paid, received, booked, resolved), not an intermediate action such as "email sent".
2. Record owner, next action, due date or trigger condition, dependency, and evidence.
3. Distinguish WAITING from DONE.
4. Set an appropriate follow-up/reminder when a future hinge exists and user intent permits it.
5. On response/change, update the next action and close only when terminal criteria are satisfied.
6. Escalate overdue or blocked items with the concrete dependency and proposed next step.

## Pitfalls
- Never widen the claim past the evidence: state only what you actually ran and read. A check you could not perform (hash, render, visual inspection) is reported as BLOCKED for that specific check, never implied to have passed.
- Do not state an integrity value you could not compute. Downgrade to "no write was issued by this session" and say why the value is unavailable.
- On an abort or stop, run reads only, then answer exactly what was asked: whether a run started, the exact files changed, and confirmation of pause. Prove the negative by searching the target paths rather than asserting it, and do not pad the reply with a narrative or remediation plan.
- When a mission is paused over a scope or authorization objection, do not remediate, install, or repair on your own initiative; hold position and ask.
- Keep the change set small enough that an abort stays clean: read-only reconnaissance is reversible, content writes are not.
- Treat a decision or answer that arrives bundled with a halt as authoritative for the halt; honor the stop first and revisit the decision separately.

## Verification
Every active obligation has owner + next action + trigger/deadline + dependency. Every closed item has terminal-state evidence. Before starting a delegated mission: required operations, skill/script paths, and write scope are all confirmed available and in-profile, or the gap is reported to the requester.
