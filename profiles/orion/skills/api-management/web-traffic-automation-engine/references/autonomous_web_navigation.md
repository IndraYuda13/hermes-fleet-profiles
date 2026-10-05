# Autonomous Web Navigation Agent Architecture

Stateful multi-turn loop, element normalization, depth-aware backtracking, and guardrail handling for autonomous web agents.

## 1. Multi-Turn Stateful Loop Architecture
An autonomous web navigator must operate as a discrete state machine:
`[Target URL] -> [Render Page] -> [Interactive Element Normalizer] -> [LLM Decision Engine] -> [State Controller & Stack Mutator]`

Actions:
- `EXTRACT`: Direct target payload URL found (requires MIME & size verification).
- `CLICK`: Intermediate element required (pass sequential target ID).
- `UNDO`: Dead-end, deceptive ad, or irrelevant subpage encountered.
- `ABORT`: Paywall, mandatory malware prompt, or hostile origin.

## 2. Depth-Aware Backtracking Protocol
- **Turn <= 1 (Landing Page):** An `UNDO` action means the entry page has no valid navigation path. Abort the site immediately and return to candidates. Do not backtrack to an empty history stack.
- **Turn > 1 (Subpages):** An `UNDO` action pops the bad state from `history_stack`, appends the offending URL/selector to `memory.rejected_traps`, and restores the previous page URL. Select an alternate candidate on the parent page without re-evaluating the bad link.

## 3. Session Memory & Anti-Loop Invariant
Every iteration must carry stateful session memory:
- `visited_urls`: Set of loaded URLs to detect circular redirects (A -> B -> A).
- `clicked_elements`: Log of clicked target IDs, texts, and destinations.
- `rejected_traps`: Blacklist of URLs, ad traps, or dead-ends encountered during backtracking.

## 4. Interactive Element Normalization Barrier
Never pass raw HTML or full accessibility trees to the LLM decision node:
1. Extract only interactive `<a>`, `<button>`, and `<form>` tags.
2. Resolve relative URLs to absolute origins.
3. Strip chrome links (`home`, `about`, `privacy`, `terms`, `contact`, `login`).
4. Filter known ad networks and cloakers (`googleads`, `adsterra`, `propellerads`, `monetag`, `ouo.io`).
5. Assign sequential integer IDs (`[1]`, `[2]`, `[3]`) and pass only the top 20-30 relevant candidates.

## 5. Direct Link MIME & Size Verification
Before concluding an `EXTRACT` action as successful:
- Issue an HTTP `HEAD` or byte-range request.
- Assert `Content-Type` matches expected binary (e.g. `application/vnd.android.package-archive` or `application/octet-stream`).
- Assert `Content-Length` exceeds minimum threshold (e.g. >1 MB for APKs) to reject error pages disguised with target file extensions.

## 6. Safety Refusal & Heuristic Fallbacks
When navigating sensitive software or terms, upstream LLMs may return safety refusals instead of JSON:
- Wrap completions in defensive `try/catch` validation.
- Fall back to deterministic scoring: score unvisited buttons by target file extension (`.apk`, `.zip`), size patterns (`\d+MB`), and version strings (`v\d+`). If a direct file link is detected, auto-select `EXTRACT`; otherwise `CLICK` the highest-scoring candidate.
