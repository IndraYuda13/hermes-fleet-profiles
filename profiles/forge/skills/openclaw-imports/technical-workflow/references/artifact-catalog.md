# Artifact Catalog

Use this catalog to choose the lightest artifact set that still keeps the work controlled.

## Core artifacts

These are the default building blocks.

### 1. Workframe

Purpose:
- lock the objective
- define the success oracle
- expose constraints
- name the evidence target

Use when:
- any non-trivial technical task starts

### 2. Parent checklist

Purpose:
- keep top-level progress visible
- prevent drift into side quests
- make restarts resumable

Use when:
- the work has more than one meaningful step

### 3. Execution note

Purpose:
- capture what changed, what was observed, and what it means

Use when:
- important findings appear during execution

### 4. Verification record

Purpose:
- store the proof behind claims like fixed, confirmed, works, or blocked

Use when:
- the task reaches a checkpoint or completion claim

## Planning artifacts

### 5. Implementation plan

Purpose:
- break work into ordered or parallel-safe tasks
- make file targets and verification explicit
- surface review points early

Use when:
- building a feature
- doing a refactor
- resuming a messy codebase
- coordinating subagents

Minimum contents:
- summary
- user review required if decisions are open
- phase or wave list
- task table with file targets and verification
- risks and assumptions

### 6. Decision log

Purpose:
- record choices, rejected alternatives, and why

Use when:
- stack, architecture, protocol, or tooling choices matter
- future sessions would otherwise repeat the same debate

## Automation artifacts

### 7. Flow map

Purpose:
- describe the real flow of pages, endpoints, timers, redirects, or bot states

Use when:
- browser or API automation is involved
- session, captcha, shortlink, queue, or auth boundaries matter

### 8. Oracle map

Purpose:
- separate intermediate hints from true downstream success signals

Use when:
- UI movement can be mistaken for success
- callbacks or logs look positive but may be incomplete

### 9. Blocker log

Purpose:
- capture blockers with exact evidence, not vague complaints

Use when:
- repeated retries fail
- access, anti-bot, or environment issues shape the plan

## Reverse-engineering artifacts

### 10. Boundary catalog

Purpose:
- track the real control points that determine behavior

Examples:
- auth gate
- request-signing input
- WebView bridge
- JNI or native bridge
- parser boundary
- pinning boundary
- reward or state mutation boundary

Use when:
- reverse engineering, modding, or bypass work is active

### 11. Hypothesis log

Purpose:
- record what is suspected, what evidence supports it, and what falsified it

Use when:
- the path is not fully proven yet

### 12. Proof log

Purpose:
- store real evidence behind a raised claim

Use when:
- promoting a boundary claim from suspected to proven

## Change-tracking artifacts

### 13. Change log

Purpose:
- preserve why a code or patch change exists
- prevent later removal of a fix whose reason would be forgotten

Use when:
- code, patch logic, or automation behavior changed

Minimum contents:
- what changed
- where it changed
- why it changed
- triggering bug or evidence
- what must not be casually removed later

## Selection rules

### Small direct fix

Use:
- workframe
- parent checklist
- verification record

### Feature or refactor

Use:
- workframe
- parent checklist
- implementation plan
- change log
- verification record

### Automation or bot flow

Use:
- workframe
- parent checklist
- flow map or oracle map
- blocker log if needed
- verification record

### Reverse engineering or modding

Use:
- workframe
- parent checklist
- boundary catalog
- hypothesis log
- proof log
- change log if code or patch logic changed

### Ambiguous research or debug lane

Use:
- workframe
- parent checklist
- research note or decision log
- verification record for each major conclusion
