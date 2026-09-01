# Upstream Error Backoff & Idempotency State Machine Verification

When designing or verifying automated recurring worker routines (e.g. streaming bots, payout triggers, reward claims, polling engines) that interact with upstream third-party APIs:

## 1. Upstream Quota & In-Review Defect Patterns
Automated workers often experience "Incomplete State Machine & Idempotency Leakage" when:
- An upstream system accepts a mutation (e.g. payout request, batch task submit) and transitions the resource to an asynchronous `UNDER_REVIEW` or `PENDING_PROCESSED` state.
- Local worker loops continue to observe the local threshold condition (e.g. balance >= $0.10) because the upstream pending balance is not deducted until processing completes.
- Worker repeatedly fires the trigger endpoint every loop cycle, receiving errors like `transactionsBeingChecked` or `alreadyInQueue`.
- This causes log pollution, rate limit bans, or anti-fraud account flagging.

## 2. Invariant Contracts for Verification

### INV-001: Short-Circuit & Zero-Spamming Invariant
- Once an upstream in-review response or status is detected, subsequent scheduled executions MUST short-circuit in memory without dispatching network calls to mutation endpoints.
- Verifiable via mock call counts: `assert api_mock.call_count == 1` across N consecutive loop iterations during cooldown.

### INV-002: Cooldown & Recovery State Transitions
- State lifecycle: `IDLE` -> `SUBMITTED` -> (`IN_REVIEW` / `BACKOFF`) -> `RECOVERED` -> `IDLE`.
- Workers must maintain a backoff timestamp (`cooldown_until`) and check upstream status query endpoints (e.g. transaction history) rather than mutation endpoints to detect completion (`PAID` or `REJECTED`).

### INV-003: Telemetry & Multi-Tier Sync
- In-memory state changes must be persisted atomically to local state files (`fleet_state.json`) so restarts retain the backoff window.
- Telemetry dashboards must render distinct visual badges for `UNDER_REVIEW` / `COOLDOWN` states to avoid operator confusion.

## 3. Test Design & Mock Fixtures
1. **Mock Sequence Test:**
   - Turn 1: Return error `transactionsBeingChecked` or status code 3.
   - Turns 2..N: Run tick loop; verify call count remains frozen at 1.
2. **Reboot Persistence Test:**
   - Simulate worker crash, reload from state file, verify worker does not fire mutation on startup if `now < cooldown_until`.
3. **Status Resolution Test:**
   - Mock history endpoint returning `PAID` (status 1) or `ERROR` (status 0). Verify state resets to `IDLE` and allows next legitimate withdrawal.
