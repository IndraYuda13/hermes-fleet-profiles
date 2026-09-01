---
name: searxng-operations
description: Managing SearXNG docker deployments, configuring outbound proxy rotation, and troubleshooting search engine blocks/rate limits.
triggers:
  - Troubleshooting SearXNG empty results or timeouts
  - Configuring proxy rotation in SearXNG settings.yml
  - Debugging SearxEngineCaptchaException or Too many request errors
---

# SearXNG Operations & Troubleshooting

This skill covers debugging and configuring SearXNG running in a Docker container, specifically around outbound proxies, rate limiting, and network connectivity.

## 1. Checking Logs for Blocks/Rate Limits
When SearXNG returns empty results without an explicit tool error, check the container logs for rate limits or CAPTCHAs imposed by upstream search engines:
```bash
docker logs --tail 50 <searxng_container> | grep -iE "captcha|too many request|timeout|connecterror"
```
Common upstream blocks:
- `SearxEngineCaptchaException: CAPTCHA (suspended_time=3600)` (Often Google)
- `SearxEngineTooManyRequestsException: Too many request (suspended_time=180)` (Often Brave/DDG)

## 2. Configuring Outbound Proxy Rotation
To avoid IP bans, configure SearXNG to rotate outbound traffic through multiple proxies in `/etc/searxng/settings.yml`:
```yaml
outgoing:
  request_timeout: 5.0
  proxies:
    all://:
      - "http://user:pass@ip1:port"
      - "http://user:pass@ip2:port"
```
*Note: Restart the container (`docker restart <container>`) to apply `settings.yml` changes.*

## 3. Testing Proxy Connectivity Inside SearXNG
SearXNG's official lightweight container image often lacks `curl`. Use `wget` to test if a proxy works from *inside* the container:
```bash
docker exec <searxng_container> wget -qO- --proxy=on -e use_proxy=yes -e http_proxy=http://user:pass@ip:port http://ip-api.com/json
```

## ⚠️ Pitfalls & Known Issues

1. **Docker Network Isolation (ConnectError):** 
   If you point SearXNG's `settings.yml` to proxies hosted on the same host using the default docker bridge gateway (e.g., `172.17.0.1:31001`), it may fail with `httpx.ConnectError: All connection attempts failed`.
   *Fix:* Point it to the host's **public IP** (e.g., `20.192.4.173:31001`) or put both the SearXNG container and proxy containers on a shared custom docker network.

2. **Datacenter / Commercial VPN IPs are heavily blacklisted:**
   Even if proxy rotation works flawlessly, IPs from commercial VPNs (like Surfshark) or Datacenters (like Azure/AWS) are aggressively flagged by Google, Brave, and DuckDuckGo. They will frequently hit `Too many request` or CAPTCHA blocks regardless of rotation.
   *Workaround:* If SearXNG is persistently blocked by datacenter IP reputation, fall back to scraping search engines directly using internal tools like `ddg-search` (DuckDuckGo Lite), which tend to be more resilient.

3. **Proxy Container Crash (tinyproxy Permission Denied):**
   If an upstream proxy container (e.g., `surfshark-proxy-studio` node) times out and its logs show `tinyproxy: Could not open file /dev/stdout: Permission denied`, a simple `docker restart` will fail to fix the internal state. Recreate it completely via compose:
   ```bash
   docker compose rm -f -s -v <service_name>
   docker compose up -d <service_name>
   ```

## 4. Disabling Bot Detection (HTTP 403 on Local Requests)
If SearXNG blocks internal tool requests (e.g., returning HTTP 403 with `X-Forwarded-For nor X-Real-IP header is set!` in logs), disable the limiter and local IP filtering in `/etc/searxng/settings.yml`. Note that this config file is usually bind-mounted from the host; edit the host file, not inside the container:
```yaml
server:
  limiter: false
botdetection:
  ip_limit:
    filter_link_local: false
```