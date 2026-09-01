---
name: multi-search-engine
description: Search across multiple public web search engines without API keys when engine diversity, regional coverage, Chinese engines, advanced operators, or cross-engine validation is explicitly needed. Do not use as the default fallback for ordinary web research; prefer ddg-search or deep-research-pro first.
---

# Multi Search Engine

Use this skill only when the task benefits from multiple engines or region-specific search behavior.

## Routing Rules

- For ordinary no-key web search fallback, prefer `ddg-search` first.
- For thorough cited research, prefer `deep-research-pro` first.
- Use this skill when the user explicitly wants:
  - multiple engines compared side by side
  - Chinese/domestic engine coverage
  - operator-heavy searching across engines
  - cross-engine validation of weak/noisy results
  - engine-specific behavior such as WolframAlpha or Startpage

## Reliability Notes

- Search result pages can block `web_fetch` with captchas/challenges.
- Do not assume Google/Bing/Brave pages will render cleanly via raw fetch.
- Prefer the engines that are most likely to return readable HTML first.
- If one engine blocks, switch engines instead of looping on the same blocked endpoint.
- **Bot Detection on VPN/Datacenter IPs**: Engines aggressively block headless browsers and CLI tools originating from VPN or Datacenter IPs. If you receive CAPTCHAs, `Too many request (suspended_time=...)`, or DDG bot warnings, do not endlessly rotate proxies within the same flagged subnet. Instead, switch to `9router-web-search` (e.g. using `gemini` backend) — delegating search to a provider's infrastructure completely bypasses local IP blocks and anti-bot systems. 
- **Tool Failure Reporting Rule**: Per user preference, if any search tool (or any tool in general) errors out or returns empty results, YOU MUST REPORT IT to the user immediately. **HOWEVER**, do not use this as an excuse to stop or wait for instructions. In the same response where you report the error, actively execute your fallback strategy (e.g., trying another engine or falling back to internal knowledge) so the user's primary goal is still advanced.
- For self-hosted SearXNG troubleshooting (proxy isolation, 403 headers), see `references/searxng-troubleshooting.md`.

## Search Engines

### Domestic / CN-focused
- **Baidu**: `https://www.baidu.com/s?wd={keyword}`
- **Bing CN**: `https://cn.bing.com/search?q={keyword}&ensearch=0`
- **Bing INT via CN endpoint**: `https://cn.bing.com/search?q={keyword}&ensearch=1`
- **360**: `https://www.so.com/s?q={keyword}`
- **Sogou**: `https://sogou.com/web?query={keyword}`
- **WeChat**: `https://wx.sogou.com/weixin?type=2&query={keyword}`
- **Toutiao**: `https://so.toutiao.com/search?keyword={keyword}`
- **Jisilu**: `https://www.jisilu.cn/explore/?keyword={keyword}`

### Global / Privacy / Alt
- **DuckDuckGo**: `https://duckduckgo.com/html/?q={keyword}`
- **Yahoo**: `https://search.yahoo.com/search?p={keyword}`
- **Startpage**: `https://www.startpage.com/sp/search?query={keyword}`
- **Brave**: `https://search.brave.com/search?q={keyword}`
- **Ecosia**: `https://www.ecosia.org/search?q={keyword}`
- **Qwant**: `https://www.qwant.com/?q={keyword}`
- **WolframAlpha**: `https://www.wolframalpha.com/input?i={keyword}`

## Operator Patterns

- `site:github.com react hooks`
- `filetype:pdf annual report`
- `"exact phrase"`
- `python -snake`
- `cat OR dog`

## Time Filter Notes

Some engines support time filters, but support is engine-specific and brittle. Treat these as best-effort, not guaranteed:
- `tbs=qdr:h` past hour
- `tbs=qdr:d` past day
- `tbs=qdr:w` past week
- `tbs=qdr:m` past month
- `tbs=qdr:y` past year

## Practical Use Pattern

1. Pick the engine based on the request's real need.
2. Fetch the result page once.
3. If blocked or unreadable, switch engines.
4. Pull the target result URL.
5. Fetch the actual destination page instead of over-analyzing the search result page itself.

## References

- `references/international-search.md` for extra examples and patterns.
