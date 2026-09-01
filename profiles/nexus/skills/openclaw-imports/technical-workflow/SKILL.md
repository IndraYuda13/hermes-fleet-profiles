---
name: technical-workflow
description: Artifact-driven workflow overlay for coding, automation, debugging, reverse-engineering support work, and other multi-step technical execution. Use when a task should stay structured, documented, and reviewable through working artifacts such as checklists, implementation plans, decision logs, flow maps, boundary notes, and verification records. Prefer more specific domain skills first, then use this as the cross-cutting process guide so technical work does not drift, lose context, or finish without evidence.
---

# Technical Workflow

Use this skill as the default rigor layer for technical work.

This skill makes the work artifact-driven.
It complements domain skills. It does not replace them.

## Core rule

Do not start from vibes.
Start from evidence, a narrow objective, a success oracle, and a live artifact set.

## Artifact-first rule

For any non-trivial technical task, keep artifacts that make the work reviewable and resumable.

Minimum artifact set:
- workframe: objective, success oracle, constraints, evidence target
- parent checklist: top-level statuses `done`, `in progress`, `pending`
- execution notes: what changed, what was observed, what it means

Use lightweight artifacts for small tasks.
Use richer artifacts for complex tasks.

Read `references/artifact-catalog.md` to choose the right set.

## Workflow

### 0. NOFX AI500 Troubleshooting & Bypass Reference
Jika menemui error `Failed to fetch AI500 list` pada deployment NOFX, baca panduan bypass database di `references/nofx-ai500-troubleshooting.md`.

### 1. Run retrieval preflight

Before touching an existing technical target:
- find the relevant structured notes, roadmap, checklist, boundary notes, flow maps, or change log
- restate three things in short form: what is already known, what the last blocker was, and what the next narrow action is
- if old notes conflict with the current target, call out the mismatch before continuing
- Bug fix = root cause, not symptom. A report names a symptom. Before editing, grep every caller of the function you are touching. Fix it once where all callers route through.
- Test bots in DM (private) first. Telegram Privacy Mode silently drops un-mentioned commands in Supergroups. Verify webhook state before rewriting routing code.

### 2. Define the work frame

Write down or keep explicit:
- objective
- success oracle
- hard constraints or risks
- expected evidence artifact
- likely touched surface

Examples of valid success oracles:
- targeted test or build passes
- exact endpoint or flow returns the downstream expected result
- patched binary or script produces the verified effect
- service restart is followed by concrete healthy state, not just no error text
- reverse-engineering claim is backed by traced code path or real runtime evidence

### 3. Create or refresh the right artifacts

Pick the lightest valid artifact set.

Use these defaults:
- small direct fix: checklist + brief execution note
- feature or refactor: checklist + implementation plan + change log
- automation or bot flow: checklist + flow map or oracle map + blocker notes
- reverse engineering or modding: checklist + boundary catalog + hypothesis log + proof notes
- ambiguous research lane: checklist + research note + decision log

Templates live in `references/artifact-templates.md`.

### 4. Pick the lightest valid execution mode

Choose one:
- **Direct lane** for small, obvious fixes
- **Research lane** when the target is still ambiguous
- **Subagent lane** when independent lanes can run in parallel

Rules:
- do not force subagents for tiny tasks
- use subagents for complex, fan-out, or long-running work
- while subagents run, keep pushing any deterministic local lane that is still available
- do not let the parent checklist disappear just because a subtask became interesting

### 5. Keep a parent checklist alive

For multi-step work, maintain a top-level checklist with statuses like `done`, `in progress`, and `pending`.

Checklist rules:
- only one top-level item should be actively in progress unless true parallel lanes are intended
- after finishing a subtask, return to the parent checklist and restate top-level status
- add subtasks freely, but do not silently replace unfinished sibling items
- if priority changes, say why
- if a task is paused, record the exact blocker and next re-entry action

### 6. Record decisions and proof while working

Do not wait until the end to write down what matters.

Capture during execution:
- decisions that changed the approach
- failed hypotheses worth remembering
- exact files or boundaries touched
- proof that a claim is real
- blockers that would confuse a future restart

If the work changed code, update the project change log in the same cycle.

### 7. Use the right lane adapter

Read `references/lane-adapters.md` for the relevant lane:
- coding and patch work
- automation / bot / web workflow work
- reverse engineering / protocol work

For reverse engineering, use the dedicated `reverse-engineering` skill as the primary domain guide.
Use this skill only as the cross-cutting workflow overlay.

### 8. Verify before claiming completion

Read `references/final-gates.md` before calling work finished.

Minimum completion standard:
- the success oracle is satisfied
- the most relevant evidence is recorded
- the active checklist is updated
- the relevant structured notes are updated in the same cycle
- the project change log is updated if code changed
- the final report explains the active step, finding, meaning, and next step in simple language

## Artifact scaling guide

### Lightweight mode

Use when:
- the task is a small direct fix
- the touched surface is narrow
- the verification oracle is simple

Minimum:
- short workframe
- parent checklist
- verification note

### Standard mode

Use when:
- the task spans multiple files or steps
- there is real risk of drift
- another session may need to resume the work

Minimum:
- short workframe
- parent checklist
- implementation plan or flow map
- execution notes
- verification record

### Deep mode

Use when:
- the task is reverse engineering, automation research, multi-lane debugging, or project bootstrapping
- there are important unknowns or hypotheses
- correctness depends on proving boundaries or downstream effects

Minimum:
- short workframe
- parent checklist
- lane-specific artifact set
- decision log
- proof log
- structured final verification

## Important non-goals

Do not import heavyweight rituals unless the task truly benefits from them.

By default, do **not** force:
- mandatory TDD for every task
- git worktrees for every task
- design-doc theater for obvious fixes
- code-review theater without a real risk or quality reason
- giant plans when a short artifact set is enough

## Output style

For technical progress and final delivery:
- Gunakan Bahasa Indonesia (selalu).
- Berkomunikasi dengan gaya santai, jelas, tanpa menggunakan em dash (—).
- Konfirmasi tugas kompleks dengan cepat, lalu berikan hasil akhirnya nanti.
- explain what you did
- explain what you found
- explain what that means
- explain the next step
- keep it understandable for a non-expert reader unless the user asks for deeper detail
- NEVER use fake output or invent API responses when a tool or network call fails. If a tool fails to return what you need, report the blocker honestly and try an alternative. Inventing plausible-looking data or file contents to bypass a blocker is strictly forbidden.
