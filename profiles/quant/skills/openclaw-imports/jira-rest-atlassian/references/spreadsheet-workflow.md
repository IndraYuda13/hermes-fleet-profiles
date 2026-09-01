# Spreadsheet Workflow

## Default stance

Treat spreadsheet-driven Jira changes as high-context writes.

Default safe sequence:
1. inspect headers
2. preview plan only
3. spot-check a few target issues
4. apply only when the mapping looks correct

## Supported columns in V1

Recognized case-insensitive header aliases:
- issue key: `issue_key`, `key`, `jira_key`, `ticket`, `ticket_key`, `issue`
- summary: `summary`, `title`, `task`, `issue_summary`
- description: `description`, `desc`, `details`
- comment: `comment`, `note`, `update`, `remarks`
- status/transition: `status`, `transition`, `state`
- priority: `priority`
- labels: `labels`, `tags`

## Preview first

```bash
python3 scripts/jira_excel_sync.py --file ./updates.xlsx --sheet Sheet1 --project KAN
```

## Apply only after preview is clean

```bash
python3 scripts/jira_excel_sync.py --file ./updates.xlsx --sheet Sheet1 --project KAN --apply
```

## Current V1 limits

- rows without issue keys are skipped
- custom fields are not auto-mapped in V1
- transition names must match an available Jira transition for that issue
- ambiguous spreadsheets should be clarified before apply
