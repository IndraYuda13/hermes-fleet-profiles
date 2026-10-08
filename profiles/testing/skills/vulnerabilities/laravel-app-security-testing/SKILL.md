---
name: laravel-app-security-testing
description: "Use when pentesting a Laravel/PHP web app."
version: 1.0.0
author: Nous Research
license: MIT
metadata:
  hermes:
    tags: [laravel, php, web-pentest, authorization, exposure, sqli, app-debug]
    category: vulnerabilities
    related_skills: [web-surface-triage, idor, broken-function-level-authorization, information-disclosure, vulnerability-disclosure-reporting]
---

# Laravel / PHP Web Application Security Testing

Authorized testing of Laravel (and similar MVC PHP) apps. On these targets the payoff is almost always **authorization gaps and unauthenticated data exposure**, not CVE scanning: a route that lives outside the auth middleware group, or a controller param that is not validated, leaks the whole dataset. Generic scanners (nuclei/ffuf) reliably come up empty here — spend your time on route/param enumeration and debug-mode abuse instead.

## When to use

- Target is (or smells like) Laravel: `XSRF-TOKEN` + `laravel_session`/`<app>_session` cookies, `<meta name="csrf-token">`, `204` on `/sanctum/csrf-cookie`, hidden `_token` form field.
- Any MVC PHP app behind a CDN where you must find authz/exposure issues quickly.

## Procedure

1. **Fingerprint & map routes.** Confirm Laravel via the cookie pair and form token. Probe routes and classify by status: `302 -> /login` = behind the auth gate; `200` = open; `403` on `/.env` = dotfiles blocked (still try concrete paths like `/storage/logs/laravel.log`).
2. **Enumerate query parameters — highest-yield step.** Laravel list/detail pages commonly take `?<model>_id=`, `?page_<section>=`, `?date=`, `?<filter>`. These frequently lack validation and decide which records render. Iterate the ID and confirm the response actually changes.
3. **Hunt unauth data exposure.** Confirm with a **fresh guest session (empty cookie jar)** — a `200` returning real PII with no session IS the finding. Fetch the list index AND every paginated **detail page** (detail pages hold the sensitive per-record data); follow the pagination params to enumerate them all.
4. **Test media/file serving.** `/storage/**` is often aliased and served directly, bypassing authz. A directory `403` does NOT mean files are protected — extract a concrete filename from a detail page (photo, signature, attachment) and request it anonymously.
5. **Trigger debug mode (`APP_DEBUG`).** Send a wrong **type** to a typed param (int expected → `page_x=abc`; date expected → `date='`). With `APP_DEBUG=true` you get a full Ignition/Whoops page (HTTP 500, often ~1 MB) leaking framework + PHP version, absolute server path, stack trace, and the **raw SQL** of the last query. Capture the version banner line and one raw query as proof.
6. **SQL injection.** Manual first (`'`, `"`, numeric, `1 AND 1=2`), then `sqlmap -p <params> --level=3 --risk=2`. Compare responses by **exact body/size/hash**, not just status code.
7. **Headers / CORS / methods.** Check security headers, `Access-Control-Allow-Origin`, `OPTIONS/TRACE/PUT`, and whether POST-only routes exist (`405` on GET).

## Pitfalls

- **A `302 -> /login` is the auth gate, not a bug.** Only count what a request with NO session/cookie returns with real content. Mislabelling the gate inflates the report with non-findings.
- **A page param that accepts arbitrary input (500 vs 200) is NOT automatically SQLi.** Laravel may validate/cast it. `date='` producing `InvalidFormatException` is Carbon date parsing, not SQL. Confirm with sqlmap.
- **sqlmap time-based false positives on paginated params are routine.** It may print `parameter appears to be '<DBMS> time-based blind ... injectable'` and, in the very next lines, `false positive or unexploitable injection point detected` / `does not seem to be injectable`. Treat the lone first hit as an FP; a genuine injection survives the boolean + exact-match confirmation.
- **Opaque route tokens are not IDOR by themselves.** Tokens like `eyJpdi...` (Laravel encrypted payload) are unpredictable — the finding is the **missing authorization on the whole section** (the index links every token), not token predictability.
- **`APP_DEBUG=true` on production is HIGH on its own** (version + server path + raw SQL). Also check `telescope` / `horizon` / `_ignition/health-check`; usually `404` once debug is off, but high-value when present.
- **Behind Cloudflare, TLS/cipher findings are the edge's config, not the origin's.** State that caveat; do not attribute weak ciphers to the app server.
- **Enumerate scale before claiming it.** Paginate the listing, collect every detail link, dedupe by unique identifier (NIS/ID) in code — never eyeball "some records". Use `scripts/enumerate_paginated_exposure.py`.

## Laravel tells / paths

| Signal | Meaning |
|---|---|
| `XSRF-TOKEN` + `laravel_session`/`*_session` (`eyJpdi...`) | Laravel; encrypted cookies |
| `204` on `/sanctum/csrf-cookie` | Sanctum present |
| `<title>Laravel</title>` on error | default error view (debug off) |
| huge Ignition/Whoops page on 500 | `APP_DEBUG=true` |
| `/storage/<dir>/<file>` returning 200 anonymously | storage symlink served directly |
| `/index.html`, `/up` default content | default scaffold left in place |
| `403` on `/.env`, `/storage/logs/*` | dotfiles/dir blocked (files may still resolve) |

## Deliverable (this user)

Package the final engagement as a **clean PDF** with a reproduction appendix containing **raw `curl` request/response** per finding (redact opaque tokens as `<token>`; mask emails/secrets in any shared copy). Build from styled HTML → PDF (e.g. `weasyprint report.html report.pdf`), render a page or two to PNG and eyeball the layout before shipping, and keep the raw evidence set separately.

## Handoff

Confirmed exposures → `information-disclosure`; object/action authz → `idor` / `broken-function-level-authorization`; scanner false-positive triage → `web-surface-triage`; report packaging → `vulnerability-disclosure-reporting`.
