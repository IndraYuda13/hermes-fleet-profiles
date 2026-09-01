# Blocker Claims

Use this file before saying work is blocked, impossible, or not reproducible.

## A blocker claim is valid when
- the blocker is concrete
- the blocker is current, not stale hearsay
- the next reasonable lane was tried or explicitly ruled out
- the blocker explains why progress cannot continue right now

## Bad blocker patterns
- one failed attempt becomes `cannot`
- UI friction becomes `impossible`
- early 403/Cloudflare/captcha becomes the whole architecture
- stale public clues outrank a working local artifact

## Better wording
- `blocked on X until Y`
- `HTTP lane not yet proven, browser lane still open`
- `current evidence narrows the issue to Z, but oracle not closed yet`
- `no final success yet; next cheapest check is ...`

## Negative-claim rule
The stronger the negative claim, the stronger the evidence required.