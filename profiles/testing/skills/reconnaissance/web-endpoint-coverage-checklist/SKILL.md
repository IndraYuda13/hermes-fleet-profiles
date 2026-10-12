---
name: web-endpoint-coverage-checklist
description: "Use when testing web apps: per-endpoint battery."
version: 1.0.0
author: Hermes Agent (testing profile)
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [pentest, web, checklist, coverage, scope]
    related_skills: [web-pentest-indonesia, web-surface-triage, pentest-run-discipline, sql-injection, xss, ssrf, xxe]
---

# Web endpoint coverage checklist

Guarantees every input of every endpoint gets the full battery — not just the
class that paid off first. Derived from a systematic base checklist (base_web_pentest),
adapted to this host's toolchain (`web-pentest-indonesia` has the concrete commands).

Use at the start as a plan skeleton and at close-out as a coverage proof. Every
cell of the matrix ends as: evidence / ruled out with reason / needs-validation /
NOT TESTED — the last one must be named in the report.

## When to Use

- Starting a web-app engagement: build the test plan from the battery in Step 2.
- Testing a new endpoint or input mid-engagement: walk its row before closing it.
- At close-out: prove coverage (every cell closed) before writing the report.
- Pair with `web-pentest-indonesia` (toolchain + commands) and
  `pentest-run-discipline` (long-run caps + handoff).

## Step 0 — scope fence (once per engagement)

1. Fill the scope template (`templates/scope_of_work.md`) before any scanning:
   allowed targets, out-of-scope, allowed/forbidden actions, rate limits, test
   accounts, stop conditions, evidence expectations.
2. Scope-check protocol before EVERY network action: extract every hostname, IP,
   CIDR, URL, callback domain, and file path the action could touch; match each
   against allowed targets; treat non-exact matches as out of scope; strip
   out-of-scope entries from multi-target tools; ambiguous → stop and ask.
3. New host/domain/bucket/service discovered during testing → record as finding
   candidate, do NOT test it until scope is confirmed.
4. Standing rules (this user): never use real accounts or recovered credentials in
   any request; one bogus login probe max where lockout could hit real users; no
   account creation on targets.

## Step 1 — map endpoints & inputs

Crawl + history + brute (commands in `web-pentest-indonesia` §Standard flow).
Record: every URL, every input/param, auth vs unauth surface, upload features,
front-end tech (determines payload contexts). This inventory is the "for each"
of step 2 — nothing gets tested that isn't on it, nothing on it gets skipped
unexplained.

## Step 2 — per-endpoint battery (in this order)

For EACH endpoint × EACH input:

a. **Path traversal / LFI** — assume Linux target; try `/etc/passwd`; focus on
   file download/view/retrieval features; PHP targets also try wrappers
   (`php://filter/convert.base64-encode/resource=...`); confirm by body content.

b. **CSRF** — does a token exist, is it required, bound to session, checked
   server-side? Test without token, POST→GET conversion, token reuse from another
   session, SameSite=Lax/Strict behaviour. (Only a finding if state changes.)

c. **XSS** — per input, first inject a unique marker (`XSS_TEST_123`) and locate
   the reflection context (HTML body / attribute / JS string / CSS). Then
   context-specific payloads; unusual tags/event handlers when filtered. Confirm
   EXECUTION (headless browser), not reflection. Scale via `dalfox`, verify by hand.

d. **SQLi** — highest-yield on Indonesian targets: numeric GET params
   (`page=`, `id=`, `berita=`, `jurusan=`). Start from a saved request so headers
   match; WAF bypass history here: `/*!50000*/`. Blind → parallel time-based
   technique skill. `--risk 2` default; risk 3 only with explicit approval.

e. **Command injection** — time-based first (`sleep 5` delta), then filter bypasses
   (`${IFS}`, backticks, encoding), `commix` where applicable; blind → OOB
   (interactsh). No claim without timing delta or interaction log.

f. **SSRF** — OOB first: paste an interactsh URL into every URL-consuming feature
   (fetch-by-URL, image/avatar import, PDF/screenshot generators, webhooks,
   import/export). Internal targets only within scope; never hit cloud metadata
   unless the engagement says so.

g. **XXE** — endpoints accepting XML; XML-based uploads (`.svg`, `.docx` — unzip,
   inject into `word/document.xml`, rezip); OOB DTD via interactsh for blind.

h. **File upload** — try extensions `.php/.jsp/.asp/.aspx/.sh/.exe`; bypasses:
   double extension (`shell.php.jpg`), null byte (`shell.php%00.jpg`), case tricks,
   `Content-Type` swap, magic-byte prefix. Then: where does the file land, is it
   downloadable, is it EXECUTED? PHP servers also test `.htaccess`/`.user.ini`
   upload if permitted. Office/XML uploads → revisit XXE.

i. **Unsafe file download / archive handling** — predict upload paths
   (`/uploads/x.php`), check `Content-Disposition`/inline execution; if the app
   unpacks archives, test zip-slip entry names.

Order rationale: a→i goes from cheapest/highest-yield to most situational; jump
directly to the class matching the tech stack (e.g. upload battery first on a
file-heavy CMS) but finish the whole row before closing the endpoint.

## Step 3 — close-out proof

- Matrix complete: every input × battery cell = evidence / ruled out / needs-
  validation / NOT TESTED (named in report).
- No "looks fine" without a test behind it; scanner hits and reflections are
  leads until confirmed (`web-surface-triage`, `counterevidence`).
- Untested is an acceptable closing state; silence is not.

## Knowledge capture (anonymized)

When storing a reusable technique (skill, memory note, template) learned during an
engagement: anonymize all target identifiers — `{target_ip}`, `{target_domain}`,
`{username}`, `{password}`, `{token}`, `{api_key}`, `{port}` (standard ports stay);
keep exploitation context so the technique stays reusable. Store in English.

## Supporting files

- `templates/scope_of_work.md` — engagement scope + scope-check template.
