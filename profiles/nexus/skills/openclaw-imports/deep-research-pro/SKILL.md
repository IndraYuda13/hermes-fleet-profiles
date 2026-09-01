---
name: deep-research-pro
description: Run multi-source deep research with strong citation discipline using available tools (web_search and web_fetch). Use when the user asks for thorough research, comparisons, market scans, or decision support with cited findings.
---

# Deep Research Pro (Patched for this environment)

Produce deep, cited research reports without hallucination.

## Workflow

1. Clarify objective briefly (1-2 questions) unless user says to proceed directly.
2. Break topic into 3-5 sub-questions.
3. For each sub-question:
   - Run `web_search` with targeted keywords.
   - Collect diverse sources (official docs, reputable media, research, data pages).
4. Read high-value URLs with `web_fetch`.
5. Synthesize findings with explicit caveats and confidence.
6. Deliver concise summary first, then full report when needed.

## Tool Mapping (required)

- Use `web_search` for discovery when available.
- If `web_search` is unavailable or rate-limited, use `ddg-search` pattern via `web_fetch` as fallback.
- Use `web_fetch` for content extraction.
- Do not rely on external local scripts or fixed filesystem paths outside this workspace.

## Source Quality Rules

1. Every material claim should have a source.
2. Prefer recent sources for fast-changing topics.
3. Cross-check key claims across multiple sources.
4. If sources conflict, state the conflict clearly.
5. If evidence is weak, say "insufficient evidence".

## Report Template

```md
# [Topic] — Deep Research Report
Generated: [date/time]
Sources reviewed: [N]
Confidence: [High/Medium/Low]

## Executive Summary
- ...

## Key Findings
1. ... (Source: URL)
2. ... (Source: URL)

## Risks / Uncertainty
- ...

## Recommendations / Takeaways
- ...

## Sources
- [Title] - URL
- ...
```

## Output Style

- Start with practical conclusion.
- Keep reasoning transparent.
- Keep language direct and factual.
