---
name: agent-prompt-adoption
description: Use when porting external AI agent prompts into profiles.
---

# Agent Prompt Adoption & Architecture Porting

This skill defines the end-to-end workflow for reverse engineering, extracting, budgeting, and porting modular system prompts and agent skills from external AI agent codebases into Hermes profiles.

## Architecture Contract

When adopting prompts from complex external agents, never dump raw monolithic prompt text into a profile. Use a tiered adoption model:

1. **SOUL.md (Identity & Behavioral Core):** Contains only the primary agent personality, instructions, lifecycle, tool-calling discipline, and posture. Must follow the upstream assembler order and fit strictly within the profile's dynamic context cap.
2. **Modular Skills (Execution Playbooks):** Vendored external skills (e.g. pentesting playbooks, security modules) mapped to standard Hermes `skills/<category>/<name>/SKILL.md` structures.
3. **Archive Skill (`<agent>-prompt-archive`):** On-demand reference skill preserving all conditional variants (alternate modes, postures, approvals), auxiliary prompts (summarization, vision, auto-review), and original source scripts byte-exact.

## Procedure

1. **Audit & Map Prompt Locations:**
   - Locate the core prompt assembler (e.g., `systemPrompt` or builder function).
   - Identify prompt caching boundaries (e.g., Anthropic dynamic vs static splits).
   - Catalog auxiliary prompts: subagent profiles, auto-review ("Approve for me"), doom-loop detection, vision/OCR, and context summarization.
   - Catalog external skill libraries (e.g., Strix, specialized playbooks).

2. **Extract String Literals Byte-Exact:**
   - Parse template literals and multiline strings preserving verbatim contents.
   - Account for backslash line-continuations (`\␊`) and escaped quotes (`\"`, `\'`, `\``) by enabling multiline matching (`re.DOTALL`).
   - Resolve template interpolation `${variable}` deterministically for target profile parameters.

3. **Calculate Capacity & Compose SOUL.md:**
   - Calculate Hermes SOUL cap: `cap = max(20000, min(int(context_length * 4 * 0.06), 500000))`.
   - Assemble sections in native assembler order.
   - Verify `len(soul) <= cap` before writing to avoid automated head/tail truncation by Hermes prompt builder.
   - Exclude environment-contradicting sections (e.g., cloud sandbox paths on a local host) from SOUL.md and route them to the archive skill.

4. **Port Modular Skills:**
   - Verify skill frontmatter: ensure each module has valid `name` and `description`.
   - Check name collisions against existing profile skills before copying.
   - Ensure skill directory names follow standard conventions without deep invalid nesting.

5. **Package the Prompt Archive Skill:**
   - Create `<name>-prompt-archive` under profile skills.
   - Place all conditional variants in `references/core-system-prompt-variants.md`.
   - Bundle auxiliary prompts into topical references (`references/aux-*.md`).
   - Keep reproduction artifacts (resolver script, resolved JSON, source copies) in `scripts/`.

6. **Verify Post-Adoption State:**
   - Run `hermes -p <profile> prompt-size --json` to verify clean parsing, system prompt byte deltas, and enabled skill counts.
   - Verify skill discovery with `hermes -p <profile> skills list`.
   - Confirm backup of pre-adoption SOUL exists in `<profile>/backups/`.

## Pitfalls

- **Multiline Continuation Truncation:** Regex scanners without `re.DOTALL` truncate multiline template literals at the first newline or backslash continuation, silently dropping prompt sections. Always assert resolved lengths against source spans.
- **Silent Truncation by Cap:** Writing a SOUL.md larger than Hermes's dynamic cap triggers silent head/tail truncation during session initialization. Keep SOUL under `max(20K, min(ctx*4*0.06, 500K))`.
- **False Runtime Claims:** Upstream prompts often assert proprietary cloud sandbox environments or free-tier restrictions. Injecting them into a local profile causes hallucinated runtime errors. Keep them in the reference archive, not SOUL.md.
- **Skill Description Budget:** New skills must have descriptions under 60 characters with trigger-first phrasing, or the Hermes skill index truncates them and breaks discovery.