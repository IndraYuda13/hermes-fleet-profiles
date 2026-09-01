---
name: telemetry-dashboard-verification
description: Use when verifying live dashboards and telemetry API sync.
---

# Telemetry Dashboard Verification

Use this skill when implementing, auditing, or verifying live web dashboards, telemetry servers, reverse-proxy caching layers, and upstream third-party API state synchronization.

## Core Verification Invariants

### 1. Upstream Pagination & Ordering Invariants
- Upstream third-party APIs often default to ascending sorting (`sort: asc, field: id`).
- Extract nested records defensively (e.g. check both `data.history.data` and `data.items`).
- Always apply deterministic reverse sorting before returning the "latest" item to consumers:
  ```python
  sorted_items = sorted(
      items,
      key=lambda x: int(x.get("unixtime", 0) or x.get("id", 0)),
      reverse=True,
  )
  latest = sorted_items[0]
  ```

### 2. Live Rendering & Cache-Busting Protocol
- Serve live templates directly from disk rather than relying on stale in-memory module constants.
- Enforce strict anti-caching HTTP headers across HTML delivery and JSON telemetry endpoints:
  ```http
  Cache-Control: no-cache, no-store, must-revalidate
  Pragma: no-cache
  Expires: 0
  ```
- Use client-side timestamp query params (`?_t=${Date.now()}`) to bypass intermediate proxy / CDN caching layers.

### 3. State Machine Lock & Backoff Enforcement
- Intermediate processing states (e.g., `UNDER REVIEW`, `IN PROGRESS`) must establish safety locks (`under_review = True`).
- Automated worker tasks must enforce backoff cooldowns to eliminate network spam.
- Terminal states (`PAID`, `ERROR`) must automatically release the safety locks.

### 4. Multi-View & Anti-CLS UI Inspection
- Validate rendering consistency across all view modes (e.g. Card View, Matrix Table View).
- Ensure placeholders with fixed spatial dimensions prevent Cumulative Layout Shift (CLS) when telemetry updates dynamically.
