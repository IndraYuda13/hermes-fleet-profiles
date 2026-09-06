# Production Safe Design Iteration & Rollback Protocol

When experimenting with radical design overhaul on live production systems (e.g. `lemontopup.indrayuda.my.id`), follow this strict workflow to prevent disrupting existing production workflows and ensure instant zero-downtime rollback:

## 1. Pre-Execution Production Snapshot
Before modifying any live template, markup (`index.html`), stylesheet (`styles.css`), or application scripts (`app.js`):
1. **Record Git SHA & Status**: Ensure the repository working tree is clean and record the current stable commit hash:
   ```bash
   git -C <project-dir> rev-parse HEAD
   ```
2. **Dedicated Staging / Backup Branch**: Create a backup branch or tag for instant reference:
   ```bash
   git -C <project-dir> branch backup-ui-stable-$(date +%Y%m%d)
   ```

## 2. Operator Feedback Loop & User Preference Adherence
- **Taste & Brand Fit Alignment**: Design archetypes must match user taste and business brand identity. If a user rejects a design direction ("balikin aja kayak sebelum lu ubah"), do NOT argue or attempt micro-fixes over the rejected paradigm.
- **Immediate Clean Rollback**: Execute instant hard reset to the recorded stable revision and restart services immediately:
   ```bash
   git -C <project-dir> reset --hard <STABLE_SHA>
   systemctl restart <service_name>
   ```
- **Live State & Screenshot Verification**: Immediately re-verify live URL status (`curl -sI <URL>`) and capture a fresh headless browser screenshot via `google-chrome --headless=new --screenshot=/tmp/restored.png <URL>` to deliver visual proof of restoration to the user.

## 3. Proactive Notification Rule
- **Never Leave the Operator Hanging**: Multi-agent task executions (AURORA -> FRAME -> PRISM -> LENS -> SENTINEL) run asynchronously. As Lead Orchestrator (ORION), you must proactively notify the user with summary facts and visual media (`MEDIA:/path/to/screenshot.png`) as soon as the final quality gate passes, without waiting for the operator to ask "udah kah?".
