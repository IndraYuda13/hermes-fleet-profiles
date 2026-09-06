# Functional QA Manifest Structure

Standard output structure for PRISM functional QA runs. Used by fleet gauntlet missions.

## Required Fields in `prism-functional.json`

```json
{
  "mission_id": "UI-YYYYMMDD-XXXXXXXX",
  "phase": "functional-qa",
  "agent": "prism",
  "git_revision": "<sha from git rev-parse HEAD>",
  "verdict": "PASS",
  "timestamp": "<ISO 8601>",
  "evidence": [
    {
      "test_id": "T1.1",
      "category": "load",
      "name": "HTTP 200 response",
      "status": "PASS",
      "detail": "Status: 200"
    }
  ],
  "summary": { "total": 119, "passed": 117, "failed": 0, "warnings": 2 }
}
```

## Standard Test Categories

| Category | ID Prefix | What It Covers |
|----------|-----------|----------------|
| `load` | T1.x | HTTP status, JS errors, console errors, critical DOM elements |
| `layout` | T2.x | Command strip, panes, rows rendered, brand text, tabs |
| `content` | T3.x | Anti-slop: lorem/undefined/TODO/NaN/null/[object Object] |
| `interaction` | T4.x | Click: row select, tab switch, filters, modals, dropdowns, resolve flow |
| `keyboard` | T5.x | Ctrl+K, Esc, J/K nav, number keys, N, Tab, arrow keys in palette |
| `state` | T6.x | Active, resolved, loading (skeleton), error (banner+retry), empty |
| `responsive` | T7.x | 320/390/768/1440/1920px: overflow, pane layout, mobile bar, row render |
| `e2e` | T8.x | End-to-end flows (declare incident, resolve, etc.) |
| `sort` | T9.x | Sort controls reorder correctly |
| `a11y` | T10.x | ARIA roles/labels, tabindex, lang attr, meta viewport |

## File Layout

```
<workspace>/
  FUNCTIONAL_QA.md                         # Human-readable report
  evidence/manifests/
    prism-functional.json                  # Machine-readable manifest
    screenshot-320px.png                   # Responsive screenshots
    screenshot-390px.png
    screenshot-768px.png
    screenshot-1440px.png
    screenshot-1920px.png
```

## Verdict Rules

- **PASS**: 0 FAIL results (WARN allowed)
- **FAIL**: >= 1 FAIL result
- Process exit code: 0 for PASS, 1 for FAIL
