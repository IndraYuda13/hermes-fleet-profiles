# Scrum Workbook Import

## Supported workbook shape

The importer expects these exact non-example sheets:
- `User Stories`
- `Product Backlog`
- `Sprint Backlog`

It intentionally ignores the `Contoh` sheets.

## Current mapping

### User Stories sheet
- unique `Epic/Modul` values -> Jira `Epic`
- each user story row -> Jira `Story` under the matching Epic

### Product Backlog sheet
- each PBI row -> Jira `Feature`
- PBI is attached to the best-matching Epic using text similarity against the user story sheet

### Sprint Backlog sheet
- each sprint task row -> Jira `Subtask`
- subtask parent -> matching PBI/Feature by `PBI ID`

## Sprint handling

Current tenant board `KAN` is a `simple` board and Jira Agile API reports `The board does not support sprints`.

So V1 uses `--sprint-mode labels` by default:
- `Sprint 1` -> label like `sprint-sprint-1`
- sprint goal stays in the issue description

If the default project board shows too many issues because it includes epics, stories, features, and subtasks together, the practical non-destructive fix is to create a separate Kanban board filtered to sprint-task issues only, for example:

```jql
project = KAN AND labels = "sprint-task" ORDER BY created ASC
```

That yields a board whose totals match the sprint backlog rows without deleting the higher-level backlog structure.

If real sprint support is enabled later, upgrade the importer to create actual sprints and assign issues there.

## Safe commands

Preview full hierarchy import:

```bash
python3 scripts/jira_scrum_workbook_import.py \
  --file /root/.openclaw/workspace/state/jira-simasu/Group\ 6\ -\ Scrum\ Planning.xlsx \
  --project KAN
```

Apply full hierarchy import:

```bash
python3 scripts/jira_scrum_workbook_import.py \
  --file /root/.openclaw/workspace/state/jira-simasu/Group\ 6\ -\ Scrum\ Planning.xlsx \
  --project KAN \
  --apply
```

## Exact-39 board mode

If the user wants the default project board total to stay exactly equal to the Sprint Backlog row count, do **not** import epics and backlog layers into that same board-first space.

Use sprint-only import instead:

```bash
python3 scripts/jira_sprint_only_import.py \
  --file /root/.openclaw/workspace/state/jira-simasu/Group\ 6\ -\ Scrum\ Planning\ NEW.xlsx \
  --project PS \
  --apply
```

This creates one board item per Sprint Backlog row, preserving sprint/PBI/module/PIC metadata in labels and descriptions while keeping the board total equal to the spreadsheet task count.

Important follow-up rule:
- if you later add real Epic issues into that same simple project board and attach the tasks to those epics, the default board total will increase because the Epic issues also appear on the board
- on tenant `PS`, adding 8 epics after a clean 39-task sprint-only import changed board `5` from `39` items to `47` items
- if the user wants both real epic parenting and a task-only 39-card working view, use a second filtered board for `labels = "sprint-task"`

## Idempotency

Created issues are labeled with source labels like:
- `src-epic-autentikasi`
- `src-us-01`
- `src-pbi-01`
- `src-sb-row-2`

This lets the importer skip re-creating items that already exist.
