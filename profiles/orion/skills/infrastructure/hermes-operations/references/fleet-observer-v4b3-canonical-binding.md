# Fleet Observer V4B.3 Canonical Activity Binding Operations

## Overview
Fleet Observer (`hermes-fleet-observer.service`) indexes multi-agent A2A calls and Kanban events into canonical activity views on Telegram.

## Authoritative Database Schema (V4B.3+)
- **Database Path:** `/var/lib/hermes-fleet-observer/analytics.db`
- **Authoritative Table:** `mission_activity_bindings`
  ```sql
  CREATE TABLE mission_activity_bindings(
      mission_id TEXT PRIMARY KEY,
      activity_id INTEGER NOT NULL,
      bound_ts REAL NOT NULL,
      last_event_ts REAL NOT NULL
  );
  ```

## Four-Way Activity Identity Invariant
For hybrid missions (combining Kanban task execution and native A2A consultations), strict canonical acceptance requires that all four activity identifiers match identically:

$$\text{mission\_activity\_bindings.activity\_id} == \text{mission\_edges.activity\_id} == \text{calls.activity\_id} == \text{telegram\_rendered\_activity\_id}$$

### Acceptance Criteria Checklist
1. **Zero manual `mission_id` injection:** Allow runtime lineage propagation to assign `mission_id` naturally (`M-YYYYMMDD-xxxxxxxx`).
2. **Consultation Budget Adherence:** Strictly adhere to the requested A2A call budget (e.g. exactly 1 call from designated specialist, `A2A_ALLOWED=0` for solo workers).
3. **No Split Activities:** Verify the mission is not split across multiple Activity IDs in `analytics.db`.
4. **Authoritative Check:**
   ```bash
   sqlite3 /var/lib/hermes-fleet-observer/analytics.db "SELECT * FROM mission_activity_bindings WHERE mission_id = 'M-xxxxxxxx';"
   ```
