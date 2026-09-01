# n8n Docker Workflow Activation Runbook

## Observed deployment pattern

The n8n server runs in a Docker container named `n8n` and exposes port 5678 only on localhost. The CLI is available inside the container. The current publish command warns that changes do not take effect while the server is running, so restart is part of the activation procedure.

## Safe batch procedure

1. List current state:
   ```bash
   docker exec n8n n8n list:workflow --active=true
   docker exec n8n n8n list:workflow --active=false
   ```
2. Export selected workflows when trigger and dependency inspection is needed:
   ```bash
   docker exec n8n n8n export:workflow --all --output=/tmp/workflows.json
   docker cp n8n:/tmp/workflows.json /tmp/workflows.json
   ```
   The output file created by the CLI is inside the container.
3. Publish the error handler or child workflow first when a target references it. Then publish each target:
   ```bash
   docker exec n8n n8n publish:workflow --id=<id>
   ```
4. Restart once after the batch:
   ```bash
   docker restart n8n
   curl -fsS http://127.0.0.1:5678/healthz
   ```
5. Verify with both `list:workflow --active=true` and exported JSON fields `active` plus `activeVersionId`.
6. Read recent startup logs. A target is verified by an `Activated workflow` entry or by the active-state export. Ignore unrelated triggerless utility workflows unless they were explicitly requested.

## Triggerless workflow rule & Startup Blocking Pitfall

Do not activate bootstrap, regression, or utility workflows that contain only a manual trigger or no trigger, or workflows with invalid trigger rules (e.g. `minutesInterval > 59`).

**Cascading Startup Block:** If any workflow is set to `active = true` in PostgreSQL but fails activation (e.g. missing trigger node or `WorkflowActivationError: Invalid interval`), n8n's `ActiveWorkflowManager` enters an exponential retry loop on startup (retrying at 2s, 4s, 8s ... up to 4096s+). This retry loop can stall or delay the activation of other valid active schedule triggers across the instance.

**Remediation:**
1. Identify failing active workflows in docker logs (`docker logs --since 1h n8n | grep -i "Activation of workflow"`).
2. Deactivate/unpublish all failing utility or broken workflows:
   ```bash
   docker exec n8n n8n unpublish:workflow --id=<broken_workflow_id>
   ```
3. Restart n8n container (`docker restart n8n`) and confirm in startup logs that `ActiveWorkflowManager` finishes initializing all valid active workflows cleanly without retry loops.

## Evidence checklist

- `/healthz` returns `{"status":"ok"}`.
- Every requested workflow ID appears in `list:workflow --active=true`.
- Every requested workflow has `active: true` and a non-null `activeVersionId` in the exported JSON.
- Startup logs do not report an activation failure for the requested targets.
- Any remaining errors are named and scoped to unrelated workflows.
