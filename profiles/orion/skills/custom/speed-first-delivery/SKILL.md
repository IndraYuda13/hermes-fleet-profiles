---
name: speed-first-delivery
description: Use when fast delivery is requested. Ship a working slice.
---

# Speed-First Delivery

## Default workflow

- Build the smallest complete version the owner can open and use first.
- Parallelize only truly independent work, usually UI and local data/API.
- Use one integration pass, one current-revision build/test pass, then publish a reversible preview when authorized.
- Report in plain language: what works now, what is deliberately unavailable, and the next meaningful gap.
- Defer polish, broad edge-case hardening, and non-material review loops until after the usable milestone is live.

## Do not compromise

- Never fake payment, payment success, authentication, user data, or provider integration.
- Never overwrite a dirty legacy system when an isolated release and rollback can be used.
- Never claim no bugs or production-complete without matching evidence.

## Fast acceptance bar

Before saying the usable milestone is done, verify the exact revision with the smallest relevant checks: build, core tests, primary flow exercise, and deployment/readback if published. Keep any remaining audit non-blocking unless it finds a material defect.
