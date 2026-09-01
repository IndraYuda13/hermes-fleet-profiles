# Pari-Mutuel Game Loop & Settlement Engine Architecture

Reference architecture for building real-time timed round games (e.g. 60-second Parity / Binary Outcome / Duel games) with Express, Socket.IO, SQLite, and Provably Fair hashing.

## 1. Round State Machine (60-Second Cycle)

```
[00s -------------- 50s] ---------> [50s ----------- 60s] ---------> [60s / 00s]
     BETTING PHASE                         LOCK & REVEAL                NEW ROUND
 - Accept bets                        - Bets locked (reject new)     - Reset state
 - Real-time pot broadcast            - Number roll animation        - Next round ID
 - Allow bet cancellations            - Compute math settlement
                                      - Credit balances & broadcast
```

### State Definitions
- `BETTING_OPEN` (0s - 50s): Accepts new bets, updates pot counters in memory, persists to DB.
- `LOCKED_REVEALING` (50s - 60s): Locks all mutations, calculates winner, executes payout transaction.
- `SETTLED`: Stores final audit record, reveals server seed, broadcasts result toast.

---

## 2. Settlement Mathematics & Invariants

Let:
- $P_{A}$ = Total pool on Choice A
- $P_{B}$ = Total pool on Choice B
- Total Pool $P_{total} = P_A + P_B$

### Case 1: Zero-Opponent Invariant (Refund Condition)
If $P_A = 0$ or $P_B = 0$:
- No opposing bets exist to form a prize pool.
- **Rule**: Every player receives 100% principal refund regardless of drawn outcome.
- Payout: $\text{Refund}_i = B_i$
- Net balance change = 0.

### Case 2: Active Duel Settlement
If $P_A > 0$ and $P_B > 0$:
- Winning outcome choice = $W$, Losing outcome choice = $L$.
- Total losing pool = $P_L$.
- Platform House Edge = $0.05 \times P_L$ (5%).
- Net Prize Pool = $0.95 \times P_L$ (95%).
- **Equal Share Model**:
  $$\text{Payout}_i = B_i + \frac{0.95 \times P_L}{N_{winners}}$$
- **Proportional Share Model**:
  $$\text{Payout}_i = B_i + \left( \frac{B_i}{P_W} \times 0.95 \times P_L \right)$$

### Conservation of Capital Invariant:
$$\sum_{i} \text{Payout}_i + \text{HouseFee} = P_{total}$$

### Provably Fair Verification Response Contract Pitfall

When returning the JSON result from a Provably Fair verification endpoint (e.g. `/api/provably-fair/verify`), ensure the backend payload schema strictly matches what the frontend UI evaluates:
- Always include explicit boolean flags and exact property names: `{ valid: boolean, hashMatch: boolean, outcomeMatch: boolean, recomputedHash: string, computedNumber: number, computedParity: string }`.
- If the frontend checks `v.hashMatch` and `v.recomputedHash` while the backend only returns `{ validCommitment, validOutcome, seedHash }`, the UI will read `Recomputed Hash: undefined` and falsely trigger a `VERIFICATION FAILED / TAMPER DETECTED` UI state even when cryptographic hashes actually match.

---

## 3. Provably Fair Pre-Commitment Verification

1. **Pre-Round**:
   ```javascript
   const crypto = require('crypto');
   const serverSeed = crypto.randomBytes(32).toString('hex');
   const seedHash = crypto.createHash('sha256').update(`${serverSeed}:${roundId}`).digest('hex');
   // Broadcast seedHash to players before round starts
   ```
2. **Outcome Derivation**:
   ```javascript
   const hashInt = parseInt(seedHash.slice(0, 8), 16);
   const drawnNumber = (hashInt % 9999) + 1; // 1 - 9999
   const parity = (drawnNumber % 2 === 1) ? 'GANJIL' : 'GENAP';
   ```
3. **Post-Round**:
   Reveal `serverSeed`. Clients can verify `SHA256(serverSeed + ":" + roundId) === seedHash`.
