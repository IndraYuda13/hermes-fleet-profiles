# Proxy Isolation & 403 Error Mitigation

When self-hosting SearXNG or running curl requests via a VPN/Datacenter proxy, bot-detection can trigger `403 Forbidden` or empty responses, specifically:

- SearXNG returning `403 Forbidden` due to missing `X-Forwarded-For` or `X-Real-IP` headers (common when queried without a properly configured reverse proxy).
- Raw CLI searches (curl/DuckDuckGo/Yahoo/Brave) returning empty results (`""`) because the proxy IP is flagged.

## Protocol for Agent Responses
When encountering these connectivity/proxy errors during an information retrieval task:
1. **Report AND Continue**: Report the 403/empty result to the user immediately so they know the infrastructure is degraded, BUT DO NOT STOP.
2. **Fallback Strategy**: In the *same turn*, pivot to alternative methods:
   - Try `multi-search-engine` for alternative search endpoints.
   - If all external requests fail, explicitly state that you are falling back to internal knowledge, and provide the requested information from internal memory so the user's primary request is still fulfilled.
3. **Troubleshooting Options**: Offer to troubleshoot the SearXNG Docker container (e.g., checking `docker ps`, inspecting `limiter.toml`, or reverse proxy logs) after providing the fallback results.