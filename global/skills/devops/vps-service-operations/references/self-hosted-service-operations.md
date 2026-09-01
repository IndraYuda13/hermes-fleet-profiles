---
name: self-hosted-service-operations
description: Use when operating or troubleshooting long-lived self-hosted services, containers, proxy fleets, resource exhaustion, or service-specific runtime failures on a VPS.
version: 1.0.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [vps, docker, services, searxng, proxies, maintenance, operations]
    related_skills: [network-proxy-troubleshooting]
---

# Self-Hosted Service Operations

## Overview

Use this umbrella for the common control loop around a persistent service: inspect its state, prove the failing path, make a narrow configuration/runtime change, and verify the service plus its resource footprint. Service-specific commands and hard-won failure modes live in references so the main workflow remains searchable by the operational class.

## Operating loop

1. Identify the owning service/container/unit, its configuration source, and the expected health signal.
2. Inspect status, recent logs, ports/networks, and disk/memory pressure before restarting anything.
3. Reproduce the request or job at the nearest useful boundary.
4. Change one configuration or runtime condition; restart/recreate only the affected unit.
5. Verify health, logs, external behavior, and disk/resource state after the change.

## Resource and log maintenance

Start with filesystem and journal measurements. Inspect stopped Docker containers before pruning; never use an aggressive volume prune without explicit confirmation. Truncate an actively written log rather than removing its open file, and validate logrotate configuration after remediation. See `references/vps-disk-maintenance.md` and `references/logrotate-insecure-permissions.md`.

## Containerized search and proxy services

For SearXNG-like services, distinguish upstream engine blocking from local networking failure by inspecting container logs and testing proxy connectivity inside the container. Prefer a shared Docker network/service DNS over brittle host-bridge routes. Treat commercial/VPS proxy reputation as a separate issue from rotation configuration. See `references/searxng-operations.md`.

## Stateful worker/bot services

For a long-running worker using a proxy fleet, verify its exact virtualenv, account/token store, proxy format, and interactive/headless mode. Preserve stateful authentication databases before resets. Test proxy nodes without spraying one endpoint, and keep connector/DNS behavior explicit. See `references/grass-bot-management.md` and `references/grass-proxies-generator.py`.

## Verification checklist

- [ ] The responsible unit/container and config path were identified.
- [ ] Relevant logs and resource measurements were collected before remediation.
- [ ] Only the affected service was restarted or recreated.
- [ ] The user-facing health signal and the service logs agree after the change.
- [ ] Any cleanup avoided unreviewed persistent volumes, credentials, and active logs.
