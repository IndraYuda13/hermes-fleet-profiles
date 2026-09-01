---
name: live-ui-kanban-orchestration
description: Use when orchestrating UI/UX refactoring and Kanban task creation for live Docker services.
version: 1.0.0
metadata:
  hermes:
    tags: [ui, kanban, orchestration, devops, docker]
    category: custom
---

# Live UI Kanban Orchestration

## Overview
Workflow for discovering live service environments, decomposing UI refactoring requests, creating structured Kanban tasks, and triggering worker dispatch.

## Core Rules & Workflow

### 1. Discover Workspace & Live Target
Before creating Kanban tasks for a live domain:
- Inspect running Docker container labels to identify the project source workspace path:
  `docker inspect <container_name> | grep -i "com.docker.compose.project.working_dir"`
- Verify frontend and backend ports and container health before delegating.

### 2. Kanban Task Creation Parameters
When calling `kanban_create`:
- **Title (REQUIRED):** `title` is mandatory on every call; omitting `title` causes an immediate kernel error (`title is required`).
- **Workspace:** Set `workspace_kind="dir"` and `workspace_path="<discovered_path>"`.
- **Dependencies:** Use `parents=["<parent_task_id>"]` to enforce execution order (e.g. Design -> Implement -> Test -> Audit).

### 3. Execution & Manual Dispatch
If tasks remain in `ready` state and are not picked up immediately:
- Run `hermes kanban dispatch` via `terminal` to trigger dispatcher evaluation and spawn assigned profiles.
