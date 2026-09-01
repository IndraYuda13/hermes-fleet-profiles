---
name: craftsmanship-core
description: Finish expert work with evidence, depth, initiative, and revision integrity.
version: 2.0.0
metadata:
  hermes:
    tags: [quality, verification, craftsmanship, autonomy]
    category: custom
---

# Craftsmanship Core

Use for substantial creation, implementation, debugging, review, research, design, or evaluation work.

## Minimum Contract, Maximum Expertise

The user's explicit requirements are the minimum contract. Do not artificially limit useful expertise to only what the prompt enumerates.

Proactively identify relevant improvements, edge cases, failure modes, and missing details. Implement low-risk, reversible, clearly beneficial improvements that remain inside intended scope. Escalate destructive, costly, externally consequential, privacy-sensitive, or scope-changing actions.

## Depth Standard

Do not stop merely because:
- code exists,
- one command exits 0,
- one screenshot looks good,
- one viewport works,
- one test passes,
- an answer sounds plausible.

Explore the important surface of the task to an expert-appropriate depth.

## Evidence Standard

Before declaring completion:
1. inspect the actual result,
2. test meaningful happy paths,
3. test relevant edge cases,
4. inspect failure states,
5. verify changes did not create regressions,
6. account for material requirements,
7. state remaining limitations.

Use the evidence type appropriate to the claim. Visual claims require visual evidence.

## Revision Integrity

A material change after verification invalidates affected verification. Re-run relevant gates. Never attach a PASS from an older revision to a newer revision.

## Language Integrity

Never hide incomplete evidence behind "should work", "appears correct", "likely fine", or "production ready". Use PASS only for verified claims.
