# SearXNG Troubleshooting & Proxy Setup

When configuring a self-hosted SearXNG instance (especially in Docker) to route outgoing searches through local proxies, keep these pitfalls and fixes in mind:

## 1. Docker Network Isolation (ConnectTimeout)
If SearXNG is running in a Docker container and your proxies (e.g., local VPN nodes) are in other containers on different bridge networks, configuring SearXNG to use `127.0.0.1:PORT` or `172.17.0.1:PORT` will result in `ConnectTimeout` or `All connection attempts failed`.
**Fix:** Use the host's fully routable IP (e.g., `20.192.4.173:PORT`) in the proxy URL, or attach both SearXNG and the proxy containers to a shared custom Docker network.

## 2. Proxy Rotation Syntax (`settings.yml`)
To rotate searches across multiple proxy nodes, define them as a list under the `outgoing` block:
```yaml
outgoing:
  request_timeout: 5.0
  proxies:
    all://:
      - "http://user:pass@IP:PORT1"
      - "http://user:pass@IP:PORT2"
```

## 3. HTTP 403 / Missing Header Errors
Updating to the latest SearXNG image may introduce strict bot detection headers. 
If SearXNG returns HTTP 403 and the logs show: `ERROR:searx.botdetection: X-Forwarded-For nor X-Real-IP header is set!`
**Fix:** Your reverse proxy must pass these headers to the SearXNG container, or you must configure SearXNG's `limiter.toml` and network settings to allow direct access without strict header validation.

## 4. The Limits of IP Rotation (Anti-Bot)
Rotating local VPN proxies does NOT bypass CAPTCHAs if the VPN provider's entire IP subnet (e.g., Datacenter IPs) is flagged by Google or DuckDuckGo. Search engines can easily fingerprint headless Playwright instances and `curl` requests differently from normal human browser traffic (which carries cookies and canvas data). 
If you receive `Too many request (suspended_time=180)` or "bots use DuckDuckGo too", do not get stuck in a loop trying to bypass it with simple proxy rotation. Escalate to the user to either wait out the cooldown, or switch to the `9router-web-search` skill (using an LLM provider like `gemini` with Grounding). Using 9Router offloads the search to the provider's infrastructure, which completely bypasses local CAPTCHAs, IP blocks, and headless browser detection.