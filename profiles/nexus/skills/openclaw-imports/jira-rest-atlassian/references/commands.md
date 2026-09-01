# Commands

## Identity and access

```bash
python3 scripts/jira_cli.py myself
python3 scripts/jira_cli.py project --key KAN
python3 scripts/jira_cli.py search --jql "project = KAN ORDER BY updated DESC" --limit 10
```

## Field discovery

```bash
python3 scripts/jira_cli.py fields --query status
python3 scripts/jira_cli.py fields --query priority
python3 scripts/jira_cli.py fields --query sprint
```

## Issue read and update

```bash
python3 scripts/jira_cli.py issue-get KAN-1
python3 scripts/jira_cli.py issue-update KAN-1 --fields '{"summary":"Updated title"}'
python3 scripts/jira_cli.py issue-comment KAN-1 --body "Progress synced from spreadsheet review."
python3 scripts/jira_cli.py transitions KAN-1
python3 scripts/jira_cli.py transition KAN-1 --name Done
```

## Create issue from JSON

```bash
python3 scripts/jira_cli.py issue-create --payload @payload.json
```

Example payload:

```json
{
  "fields": {
    "project": {"key": "KAN"},
    "summary": "New task from Brodayy",
    "issuetype": {"name": "Task"},
    "description": {
      "version": 1,
      "type": "doc",
      "content": [
        {
          "type": "paragraph",
          "content": [{"type": "text", "text": "Created from structured input."}]
        }
      ]
    }
  }
}
```
