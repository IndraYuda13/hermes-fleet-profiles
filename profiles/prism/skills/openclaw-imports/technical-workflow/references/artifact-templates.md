# Artifact Templates

Use these as lightweight templates. Adapt them to the target project instead of forcing every section.

## 1. Workframe

```md
# Workframe

## Objective
- 

## Success Oracle
- 

## Constraints / Risks
- 

## Evidence Target
- 

## Likely Touched Surface
- 
```

## 2. Parent checklist

```md
# Checklist

- [ ] Item 1
- [ ] Item 2
- [ ] Item 3

## Status
- done:
- in progress:
- pending:
```

## 3. Implementation plan

```md
# Implementation Plan

## Summary
- 

## User Review Required
- 

## Phase 1
### Goal
- 

| Task ID | File / Surface | Action | Verification | Status |
|---|---|---|---|---|
| TASK-001 | path/to/file | exact change | exact proof | pending |

## Phase 2
### Goal
- 

| Task ID | File / Surface | Action | Verification | Status |
|---|---|---|---|---|
| TASK-002 | path/to/file | exact change | exact proof | pending |

## Risks / Assumptions
- 
```

## 4. Decision log

```md
# Decision Log

## DEC-001
- date:
- topic:
- chosen:
- alternatives:
- reason:
- impact:
```

## 5. Flow map

```md
# Flow Map

## Entry
- 

## Steps
1. 
2. 
3. 

## Boundaries
- auth:
- session:
- captcha:
- timer / queue:
- endpoint:

## Downstream Success Signal
- 

## False Positive Signals
- 
```

## 6. Oracle map

```md
# Oracle Map

| Signal | Type | Meaning | Enough to claim success? |
|---|---|---|---|
| UI changed | intermediate | page moved | no |
| callback fired | intermediate | handler executed | no |
| final endpoint state changed | downstream | real effect happened | yes |
```

## 7. Blocker log

```md
# Blocker Log

## BLK-001
- blocker:
- exact evidence:
- current impact:
- failed attempts:
- next hypothesis:
```

## 8. Boundary catalog

```md
# Boundary Catalog

## BDY-001
- boundary type:
- location:
- role:
- current status: proven / open / falsified
- evidence:
- next action:
```

## 9. Hypothesis log

```md
# Hypothesis Log

## HYP-001
- statement:
- why it seems plausible:
- evidence for:
- evidence against:
- status: open / supported / falsified / proven
- next test:
```

## 10. Proof log

```md
# Proof Log

## PRF-001
- claim:
- artifact or file:
- exact evidence:
- downstream effect:
- confidence: low / medium / high
```

## 11. Change log entry

```md
## YYYY-MM-DD - short title
- files:
- change:
- trigger:
- evidence:
- reason this exists:
- removal warning:
```

## 12. Verification record

```md
# Verification Record

## Claim
- 

## Oracle Checked
- 

## Evidence
- 

## Result
- passed / failed / partial

## Next Step
- 
```
