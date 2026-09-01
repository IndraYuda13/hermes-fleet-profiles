---
name: vps-service-operations
description: Use when maintaining a VPS-hosted service, investigating disk pressure, container logs, log rotation, proxy egress, search-service blocks, or safe runtime cleanup.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [vps, docker, disk, logs, journald, searxng, proxy, maintenance]
    related_skills: [systematic-debugging, service-connectivity-troubleshooting]
---

# VPS Service Operations

## Overview

Run VPS maintenance as evidence-driven service operations: measure first, identify the owning service, make the smallest reversible change, and verify both capacity and service health afterward.

## When to Use

- Disk usage or logs are growing unexpectedly.
- Docker images/containers, journald, or logrotate need maintenance.
- A self-hosted SearXNG service has empty results, CAPTCHA/rate-limit symptoms, or proxy egress failures.

## Capacity and Logs

```bash
df -h
du -h --max-depth=1 / 2>/dev/null | sort -hr
journalctl --disk-usage
docker ps -a --filter status=exited --format 'table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Size}}'
```

Prefer targeted cleanup. Inspect stopped containers before any prune; obtain approval before aggressive Docker pruning with volumes. For active logs, truncate or rotate correctly—deleting an open file does not necessarily free its held space. If logrotate reports insecure parent permissions, fix the ownership/`su` configuration deliberately, then rerun and verify logging health.

## Hosted Search Services

For SearXNG, inspect container logs for upstream CAPTCHA, rate limiting, timeout, and proxy errors before editing configuration. Test proxy reachability from inside the actual container; minimal images may provide `wget` rather than `curl`. Treat datacenter/VPN IP reputation as a real external constraint: rotation cannot guarantee a search engine will accept the egress IP.

Keep service-local protections and rate limits justified. When internal calls are blocked, verify trusted-network headers and application configuration rather than disabling detection globally without a bounded reason.

## Verification Checklist

- [ ] Pre-change capacity/service status was recorded.
- [ ] Cleanup scope excluded active data and unapproved volumes.
- [ ] Container/service logs identified the affected component.
- [ ] Post-change `df`, relevant service status, and one functional request were checked.
