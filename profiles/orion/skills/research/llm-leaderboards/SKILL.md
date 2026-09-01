---
name: llm-leaderboards
description: Extract data from LLM leaderboards such as LMArena (LMSys) and correctly differentiate between aggregators and official sources.
---

# LLM Leaderboards Data Extraction

Automates retrieving rankings from leading AI model leaderboards.

## Core Rules
1. **Always fetch from the live official source.** When asked to check an official ranking like "lmarena" or "LMSys Chatbot Arena," go to the official domain (`https://lmarena.ai/leaderboard` — redirects to `https://arena.ai/leaderboard` as of mid-2026) using the `browser_navigate` and `browser_snapshot` tools to get live data.
2. **Do not substitute with aggregator sites.** Sites like `swfte.com` or other SEO blogs may provide easier-to-parse data via internal JSON structures, but they are often inaccurate, delayed, or manipulated. You must only read from the official source requested.
3. **Handle Client-Side Rendering (CSR):** Official modern leaderboards (like LMArena) use heavy CSR (React/Next.js). A simple `curl` or `web_extract` will fail because the data is loaded via JavaScript.
4. **Tool Selection:** You MUST use the `browser` stack (Playwright via `browser_navigate` and `browser_snapshot`, clicking through tabs via `browser_click`) to wait for the DOM to render the data tables completely.

## Tool Selection & Efficient Extraction
1. **Navigation:** Use Playwright (`mcp__Playwright__browser_navigate`) to navigate to `https://lmarena.ai/leaderboard`.
2. **Snapshot vs Evaluate:** `browser_snapshot` on `arena.ai/leaderboard` can exceed 500KB due to deep React tree rendering, resulting in truncation.
3. **Recommended Fast Path (`browser_evaluate`):** Execute `mcp__Playwright__browser_evaluate` with function `() => document.body.innerText`. This returns all top-10 sections (Agent, Text, WebDev, Vision, Document, etc.) cleanly formatted in plain text, bypassing snapshot overhead and truncation issues.

## Pitfalls & Troubleshooting
- **Cloudflare/Bot Protections:** If `browser_navigate` encounters a blank page, captchas, or blocks, ensure you are allowing adequate time for the page to fully load and run its JavaScript.
- **Navigating the Data:** Use `browser_snapshot` to inspect interactive element references, and click on tabs (like the "Text" or "Coding" leaderboards) using `browser_click` to expose the desired data.
- **Overview page has multiple arenas:** The `/leaderboard` landing is an overview showing top-10 charts for Agent, Text, WebDev, Vision, Document, etc. Initial `browser_snapshot` after `browser_navigate` to `https://lmarena.ai/leaderboard` (redirects to `https://arena.ai/leaderboard`) already includes full **Agent top 10** plus other arena top-10s. For "top N Agent/Text/WebDev" with N ≤ 10, read the overview snapshot — do not click into sub-tabs.
- **Direct category URLs for Rank > 10:** For requests asking for more than the top 10 (e.g. top 25, top 50) or full rankings, navigate directly to `https://arena.ai/leaderboard/<category>` (e.g. `/leaderboard/text`, `/leaderboard/agent`, `/leaderboard/webdev`). The table rows can be extracted cleanly using `document.querySelectorAll('table tr, [role="row"]')` via Playwright or browser evaluation.
- **Agent arena metric ≠ Elo:** Agent overview ranks by **net improvement %** (e.g. `12.72% ±2.00%`), not the numeric Elo used by Text/WebDev/Vision. Report the metric as shown; do not relabel Agent % as "score/Elo".
- **Vendor labels incomplete in a11y tree:** Snapshot often shows Anthropic/Meta icons as text but OpenAI/Google/others as bare model names. Do not invent missing org labels; copy model strings exactly from the snapshot.
- **Dedicated Arena URLs:** When rank > 10 (e.g. Top 25/full list) is requested, navigate directly to `https://arena.ai/leaderboard/agent` (or `/leaderboard/text`, etc.) instead of the `/leaderboard` overview to get the complete dataset.
- **Inaccurate Scrapes:** Avoid writing quick Python scraping scripts that look for `<script id="__NEXT_DATA__">` on aggregator websites, as this violates the direct source requirement and often leads to hallucinated or stale information.

## References
- `references/lmarena-agent-overview.md` — Agent arena metric, overview-enough rule, snapshot gotchas.