# Boundary Patterns

Use this file to decide where to instrument next.

## Coding / script bugs
- function input boundary
- parsed config boundary
- branch-condition boundary
- file read/write boundary
- state persistence boundary

## Automation / bot / web flows
- login/auth boundary
- session/cookie boundary
- selector/callback boundary
- timer/queue boundary
- message-anchor boundary
- downstream success boundary

## Ops / service incidents
- process alive vs actually healthy boundary
- config loaded vs config applied boundary
- restart success vs workload success boundary
- local health vs external dependency boundary

## Reverse engineering / protocol
- request-signing input boundary
- parser/validator boundary
- bridge or JNI boundary
- trust or pinning boundary
- reward or state-mutation boundary

## Quick rule
Find the first place where known-good input becomes wrong output or where a valid action stops producing the expected downstream effect.