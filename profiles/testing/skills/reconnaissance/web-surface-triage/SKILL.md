---
name: web-surface-triage
description: Separate real web exposures from scanner false positives.
version: 1.1.0
author: Nous Research
license: MIT
metadata:
  hermes:
    tags: [recon, triage, false-positive, exposure, cdn, waf]
    category: reconnaissance
    related_skills: [asset-discovery, information-disclosure, vulnerability-disclosure-reporting]
---

# Web Surface Triage

Discovery (see `asset-discovery`) produces hundreds of hosts and thousands of scanner hits; most are noise. This skill is the second half: decide which candidates are REAL exposures, which are artifacts, and which surface is worth testing next. Getting this wrong wastes the engagement on false positives and destroys report credibility — apply it before anything is written up.

## When to use

- After a subdomain/inventory pass, when you have a list of live hosts and a pile of scanner output.
- Any time a scanner or wordlist reports an "exposure" you have not personally confirmed.
- Before reporting: every finding must survive this triage.
- A single target URL handed to you with no scanner output — treat the page itself as the discovery pass: fingerprint, extract nav/version/asset intel from the HTML, then run the platform baseline (WordPress: `references/wordpress-surface-baseline.md`).
- A target that times out from every sandbox tool while DNS still resolves — the host filters datacenter IP ranges. Re-route the whole test through the cloud browser's separate egress (`references/datacenter-blocked-targets.md`).
- A host behind an interactive anti-bot challenge (Cloudflare "Just a moment...") that still needs recon — keep testing it instead of parking it, via `references/browser-grade-fetching.md` (local FlareSolverr + pacing).

## Procedure

1. **Fingerprint every live host** — status, title, `Server`, `X-Powered-By`, tech, and whether it sits behind a CDN/WAF or is a **direct origin** (no WAF). Origins are the higher-value targets: no edge protection and often a different, older stack. `httpx -l hosts.txt -sc -title -server -td -tls-grab -json`.
2. **Run a bounded exposure sweep** — a fixed path list (VCS/backups/config/admin/API-spec/dir-listing) across all hosts, recording `status` **plus** `Content-Type` **plus** a short body snippet. Never trust the status alone.
3. **Confirm before recording.** For each candidate, open the raw body/headers and check the artifact is genuinely what the scanner claims. This is the step that separates a real finding from a false positive.
4. **Classify** every candidate as `real` / `false-positive` / `needs-validation`, with the specific test that decided it.
5. **Recover real endpoints** from login links and redirect JavaScript (below) rather than brute-forcing parameter names.
6. **Report only what you reproduced.** Map each confirmed artifact to its vulnerability class, score honestly, and hand off with `vulnerability-disclosure-reporting`.

## Classification rules (the core of this skill)

Judge a candidate by **`Content-Type` + body content**, not by status code. A 200 is meaningless on its own.

| Signal | Verdict |
|---|---|
| 200 `text/html` whose body is the site's own index/SPA shell, for an arbitrary path | **False positive** — router catch-all. SPA sites return the index for `/actuator/heapdump`, `/Dockerfile`, `/docker-compose.yml`, `/vendor/phpunit/.../eval-stdin.php`, `/actuator/env`, etc. |
| 200 `text/html` with the WAF's block-page wording (e.g. "Situs dalam perbaikan", "Laman diblokir", "Attention Required") | **False positive** — a WAF block served with HTTP 200. It masks the request; it is not an exposure. |
| 200 with `Content-Type: application/sql`, `application/json`, `text/plain`, `application/gzip`, `application/octet-stream` and real artifact content | **Real** — machine-readable types that are not `text/html` are the strongest signal. |
| Same artifact served for many different paths (identical `ETag`/`Content-Length`) | **One finding**, not many. A server-side fallback (e.g. any `*.sql` path serving one dump) is a single rule. |
| `.git/HEAD` body starting `ref:`; `.git/config` containing `[core]`; config backup containing `define(`/`password`/`[configuration]` | **Real** (validate the content, not the path). |
| Open directory listing (`<h1>Index of /`, `Parent Directory`) | **Real** — but only if the body is genuinely the autoindex page, not the site's 404 dressed as 200. |
| Login form present (`name="pma_username"`, `name="pma_password"`, a framework login `<title>`) | **Real** exposed panel; note it is a *gate*, not unauthenticated access — calibrate severity accordingly. |
| `403` for a sensitive path (`.env`, `.git/config`) where a random path gets `404` | **Blocked, not confirmed**: the file may exist behind an edge WAF. Classify as protected until shown otherwise; probe inside the same host for paths the WAF does not cover (different extension, uppercase, encoded) before calling it either way. |
| `200` + body identical to the site's homepage for the SAME sensitive path | **WAF catch-all on that path class** — the WAF rewrites the block into the site's own page. Verify by comparing the two bodies byte-for-byte; use the platform's real fingerprint endpoint (e.g. `/wp-json/`) to confirm the WAF's coverage boundaries. |

## Recovering endpoints without brute force

- **Read login links, not guesses.** `href="/login"`, `href="/sso"`, `href="/admin"` reveal the real auth path; requesting guessed variants (`/oauth/authorize`, `/.well-known/openid-configuration`) blind wastes requests and usually 404s.
- **Inventory every external host the site's own menus link to, then resolve each.** Menu/footer links to third-party domains are part of the trust surface: harvest `https?://` hosts from the nav HTML, check the A record, and fetch the page. A linked domain with no A record (registrar MX only) or serving "for sale" content is burnable — anyone can re-register it and host a phishing portal under the official menu's label. That is a High supply-chain finding, not a dead link.
- **Decode mangled redirect JavaScript.** Sites that redirect client-side often emit garbage because the URL was embedded unquoted, e.g. `top.location=Jam.BMKG` came from `location="https://jam.bmkg.go.id/"` mangled by the template. When a redirect target is a bare token, `grep -oE 'https?://[a-z0-9.-]+' <bundle>` and test the plausible hosts twice before trusting it — do **not** treat a crafted-looking hostname as a valid domain.
- **Follow the app's SSO link to find the IdP.** The app that serves the login link is usually un-challenged even when the IdP is bot-walled; its 302 `Location` gives the authorize URL, realm, and `client_id`. Pivot there, then apply the `oauth` skill's redirect tests.

## Management-appliance fingerprints (recognise by the login-redirect endpoint)

| Endpoint seen in the redirect chain | Product |
|---|---|
| `/remote/login` (+ `/remote/fgt_lang`) | FortiGate SSL-VPN |
| `/auth/realms/<realm>/protocol/openid-connect/auth` | Keycloak |
| `/portal/` with an `openresty` 302 | appliance admin portal |
| `<title>phpMyAdmin</title>` + `pma_username` | phpMyAdmin |
| PRTG ASCII banner in the HTML comment | PRTG Network Monitor |

## CORS

- `Access-Control-Allow-Origin: *` **together with** `Access-Control-Allow-Credentials: true` is an invalid combination that conforming browsers reject; on its own it is a **hardening/Medium-low** item, NOT a cross-origin data-theft High. Reserve High for an origin that is reflected/whitelisted **and** an authenticated endpoint returning sensitive data to that origin. Check whether the value is static `*` or reflected from the request `Origin` — that distinction decides severity.

## Pitfalls

- **An app whose only visible entry is a login form still has an unauthenticated API.** Read the login page's `<script>` blocks: on this class of PHP app the login page fetches a hidden API (e.g. `/API_ABSEN/api.php?id=&fp=`) before/without any auth, and the flag-style params it uses (`&cekreg`, `&reg`, `&cekpass`, `&bypass`, `&getsiswa`) are separate code paths, each with its own logic — branch-fuzz the flags, don't test the endpoint as one blob.
- **Enumerate backup/dump filenames, not just `.git`/`.env`.** A DB-named file at the web root (`<dbname>.sql`, matching the app's MySQL schema name) is a common, high-impact exposure that generic `backup.zip` lists miss. The schema name is usually leaked by the app itself (JS fetch paths, error messages) — feed it to the dump-name list. A public dump both is a finding *and* reveals the app's real tables/columns for later tests.
- **Read `sso.php`-style files by fuzzing parameter *names*, not just values.** A response that differs per param name (`?key=` gives 'wrong key' versus 'tidak diijinkan'/'not allowed' for every other name) exposes the accepted parameter and its validation wording; the value it echoes is the injection surface to test next.
- **Framework-independence:** the same patterns (hidden API called from login JS, action-by-flag params, `<dbname>.sql` at root) recur across hand-rolled PHP school/attendance/absensi apps. Fingerprint the stack first, then apply these checks before broad wordlist scans.
- **A 200 to an arbitrary path is the default behaviour of an SPA, not a finding.** Confirm the `Content-Type` and body before writing anything down.
- **A shell 200 for `/api/*` on the static host does not mean the API is missing.** SPAs name their real backend in the config chunk (a `modulepreload` script exporting the API base); the client may also monkey-patch `window.fetch` for runtime-only routes. Test endpoints against the configured host before calling anything a soft-404, and hand the bundle work to `spa-frontend-recon`.
- **A WAF block page can arrive with HTTP 200.** Save the raw body and read it; block wording means blocked.
- **Do not disable TLS verification (`curl -k`) by reflex.** A valid cert is identity evidence; a cert-verification error is itself informative and may indicate an internal name or a misissued cert. Inspect first: `echo | openssl s_client -connect host:443 -servername host -showcerts | grep -E ' s:| i:'` — a leaf-only chain (no issuer entries beyond the leaf) still passes browsers via AIA fetch but breaks curl/openssl and non-browser API clients, and the incomplete chain is itself a Low finding. Record it, then proceed with `-k` noting the justification. (Traffic routed through a local Burp proxy always needs `-k`: Burp's CA is not in the system store.)
- **A hard cut on SQLi-looking input is a WAF, and it maps cleanly.** When a single quote passes but `' OR '…`, `UNION`, `SLEEP(`, `BENCHMARK(` return `000`/connection-drop, that is an inline WAF signature, not a broken app — the payload class determines the block. Map the boundary first (which tokens survive: inline comments, case mixing, nested encoding) so later injection work knows the rule set instead of rediscovering it per request. The same class of WAF often 403s dotfiles (`.env`, `.git/config`) while letting them through as other extensions; that asymmetry is the classic bypass seam.
- **A whole record-format returning byte-identical bodies is an application-layer block, not a vulnerability.** If every username/password variant (fake user, real-looking, pseudonymous, wildcard) returns the same body hash and generic error, the target validates centrally (LDAP bind / single query); payload escapes are being handled. Record as a positive defensive verdict with the exact probe set — do not report user enumeration that the evidence contradicts.
- **A blocked request is not a clean result.** If a WAF challenge stops you testing a host, mark it **untested**, not "no issue" — the test never ran.
- **Fingerprint the WAF before pacing the test, then stay low-and-slow.** An active WAF plugin (Wordfence etc. — its REST namespace in `/wp-json/` gives it away even when page HTML hides it) is compatible with a complete triage: single curls or pools ≤8 workers, tens of requests spread over tens of minutes, zero credential guessing. Bursts convert a clean finding set into a ban that marks the host untested.
- **Parameter-validation errors enumerate server state — probe with a bogus value for a required param, never a real one.** `400 rest_missing_callback_param` means the route dispatched to validation before any permission check; `401/403 rest_forbidden` at the same spot means auth is enforced. When the error lists accepted values (e.g. every installed plugin slug), that list is already an unauth inventory disclosure. Follow with all required params set but ids/slugs that cannot exist, and never supply the final value that completes a state-changing flow (save/rollback/activate).
- **Listed ≠ active.** A component revealed by inventory is only live attack surface if its code loads: confirm a known asset (`readme.txt` for the version, a css/js for load state — a 404 asset usually means the plugin is inactive) before scoring any CVE against it.
- **Do not claim impact you did not reproduce.** An RCE whose trigger route returns 404 is not an RCE; label it needs-validation and keep the narrative factual.
- **A suspiciously synthetic dataset** (generic names, mixed public email domains, an obvious "backup admin" row) is often a canary planted to catch researchers who over-exploit. Report the exposure; do not download or exfiltrate the full artifact.

## Handoff

Route confirmed findings by class: exposed files/panels/debug → `information-disclosure`; OAuth/OIDC → `oauth`; dangling DNS → `subdomain-takeover`; report packaging → `vulnerability-disclosure-reporting`.
