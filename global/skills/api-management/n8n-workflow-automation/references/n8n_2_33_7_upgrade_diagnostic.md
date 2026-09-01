# n8n 2.31.7 -> 2.33.7 Upgrade & Task Runner Diagnostic Log

## System & Deployment State
- **Container:** `n8n`
- **Database:** PostgreSQL (`firecrawl-nuq-postgres-1`)
- **Old Version:** `2.31.7`
- **New Version:** `2.33.7` (`docker.n8n.io/n8nio/n8n:2.33.7`)
- **Backup Artifacts:**
  - PostgreSQL Dump: `/root/n8n_backup_phase0/n8n_db_dump.pgdump` (`SHA256: 76a69c336fee8ff04f5048d5e4d36ae93bd578ecff9cdaf5f1b8d848c260101d`)
  - Workflows Export: `/root/n8n_backup_phase0/workflows_export.json` (`SHA256: a2837d704cdc39c963cfe7cf111d6ce6624a99134e4af82c248cd9ffc8ab6efd`)

## Key Findings & Diagnostics

### 1. HTTP Fetch Node Item Inflation & OOM Root Cause
- **Issue:** 9 HTTP fetch nodes in `MAI V2.2 - 01 Market Intelligence Master` did not specify `executeOnce: true`.
- **Mechanism:** Upstream node `Fetch BTC 15m Klines` returned 192 kline items. Subsequent HTTP nodes executed once per incoming item, causing exponential data reference inflation to **46,080 item references per step** in `execution_data`.
- **Impact:** PostgreSQL execution data ballooned to over 1.3 million array elements, causing Node.js heap exhaustion (`FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory`) and Task Broker socket stalls.
- **Fix:** Enabled `executeOnce: true` on all 9 market data HTTP fetch nodes. HTTP execution time dropped from 15+ minutes to 3.9 seconds total.

### 2. Science Schedule Trigger Activation Errors
- **Issue:** Workflows `MAI V3 - 11 Scorecards and Calibration` and `MAI V3 - 14 Champion Challenger Promotion Review` threw `WorkflowActivationError: Invalid interval` during startup.
- **Root Cause:** Mismatch in `n8n-nodes-base.scheduleTrigger` parameter format across versions (1.2 vs 1.3).
- **Fix:** Replaced schedule triggers with `n8n-nodes-base.cron` (v1) using standard cron expressions (`0 */6 * * *` and `0 0 */7 * *`). Startup activation errors completely eliminated.
