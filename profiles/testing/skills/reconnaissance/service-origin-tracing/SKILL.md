---
name: service-origin-tracing
version: 1.0.0
author: Hermes Agent
title: Service Origin Tracing
description: "Use when tracing where a domain or service actually runs."
tags: [networking, docker, cloudflared, tracing, infrastructure]
related_skills: [web-surface-triage, asset-discovery]
---

# Service Origin Tracing

## When to Use

Load when the user asks where a domain/service actually runs — "program aslinya run di mana", "port berapa", "is it running normal", "why is my client hitting this domain". Not for attack-surface scanning (use web-surface-triage) or passive asset discovery (use asset-discovery); this is the point-diagnostic for ONE named service.

Trace an internet-facing domain to the process that actually serves it on this host. The asking pattern is "where does X really run, what port, is it healthy?" — answer with the full path (domain → edge → tunnel/port → container), each step evidenced, not just the resolved IP.

## Procedure

1. **Resolve the domain**: `getent hosts <domain>` and `python3 -c "import socket; print(socket.gethostbyname_ex('<domain>'))"`. Cloudflare ranges (104.x / 172.6x, 2606:4700::/32) mean proxied — origin is hidden behind a tunnel/CDN and must be matched by tunnel config, not IP.
2. **Fingerprint the host**: `hostname -I` (local IPs), `curl -s -m 10 ifconfig.me` (public IP). If the resolved IP is not among these, the service is either remote or proxied back to this host.
3. **Find the listener**: `ss -tlnp` (process names + PIDs) and `docker ps --format '{{.Names}} | {{.Status}} | {{.Ports}}'`. Stack names matching the domain (`firecrawl-*` for firecrawl.<host>) usually pin the service; `docker inspect <container> --format 'image: {{.Config.Image}} | status: {{.State.Status}} | started: {{.State.StartedAt}}'` gives its identity and uptime.
4. **Find the tunnel (when proxied)**: `ps aux | grep -i [c]loudflared` shows running tunnels and their `--config` paths; then `grep -B1 -A2 '<domain>' /etc/cloudflared/*.yml` yields the `hostname: …` / `service: http://127.0.0.1:<port>` ingress pair — that port IS the origin. Also check per-app quick tunnels under the user's home (`/root/.<app>/cloudflared/`) and `/tmp/cloudflared-*` configs.
5. **Prove the path**: health-check local vs via-domain — `curl -s -m 8 -o /dev/null -w 'HTTP %{http_code} (%{time_total}s)' http://127.0.0.1:<port><ep>` and the same against the domain. For APIs, run one real authenticated request (e.g. Firecrawl `POST /v1/scrape` with the client's API key) against BOTH endpoints; identical payloads prove same origin. A 404 on a made-up endpoint is still a fingerprint: byte-identical error pages local vs domain prove the same backend.
6. **Verdict**: running/healthy from container state + response codes, latency delta from the timing fields (via-CDN adds ~0.1s vs ~2ms direct loopback).

## Pitfalls

- Read the tunnel config file instead of guessing proxying — one cloudflared instance on a multi-service host can carry dozens of hostname→port mappings, and the target's mapping sits in the list with all the others.
- Publish binding is attack surface: `0.0.0.0:<port>` on a public host means direct internet reachability that bypasses any CDN/tunnel gate — check the cloud NSG/firewall and flag weak or default-looking API keys as findings. Binding to `127.0.0.1` closes it.
- Performance finding worth reporting: the client can usually point at `http://127.0.0.1:<port>` and skip the CDN round-trip entirely — offer it, never apply unasked.
- The API key the client uses lives in its config (grep it from the Hermes profile config when the client is Hermes); never print it, pass it only via the request header.
