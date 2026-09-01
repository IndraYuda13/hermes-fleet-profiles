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
Use for follow-ups, approvals, applications, bookings, reminders, delegated admin, or any task whose completion depends on a future action or response.

## Procedure
1. Define the true terminal state (approved, paid, received, booked, resolved), not an intermediate action such as "email sent".
2. Record owner, next action, due date or trigger condition, dependency, and evidence.
3. Distinguish WAITING from DONE.
4. Set an appropriate follow-up/reminder when a future hinge exists and user intent permits it.
5. On response/change, update the next action and close only when terminal criteria are satisfied.
6. Escalate overdue or blocked items with the concrete dependency and proposed next step.

## Verification
Every active obligation has owner + next action + trigger/deadline + dependency. Every closed item has terminal-state evidence.
