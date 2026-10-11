# WordPress surface baseline (single host, unauthenticated, low-and-slow)

Ordered check list for triaging one WordPress host without credentials. Every check is read-only and WAF-survivable. Run the fingerprint first (Server, X-Powered-By, meta `generator` tags, `/readme.html`, theme/plugin asset paths) — generator meta tags often name the theme and plugin versions even when the page exposes no plugin asset URLs.

## 1. Inventory without brute force
- `GET /wp-json/` → the `routes[].namespace` map names plugins that register REST APIs (security, snippets, file-manager, rollback, builder plugins) even when the HTML shows zero plugin asset paths.
- Version each plugin read-only: `GET /wp-content/plugins/<slug>/readme.txt` → `Stable tag:` line. Most plugins expose it; no version.php needed.
- User enumeration: `GET /wp-json/wp/v2/users`, `GET /?author=1..7` (via REST and sitemap both). 401/404 across the board = closed; any username leak = finding.
- XML-RPC: POST `system.listMethods`. A full method list including `wp.getUsersBlogs` and `system.multicall` is a brute-force channel — login-page-hiding plugins do not cover xmlrpc.php, so hidden login + open xmlrpc = the hardening is bypassable.
- Auth oracle in one request: `wp.getUsersBlogs` with bogus credentials → a fault (403 'Incorrect username or password') proves credential validation is reachable without the login form. Never iterate past one bogus probe in triage.

## 2. XML-RPC pingback SSRF — verify out-of-band, aim every probe at your own collector
1. Mint a collector: `POST https://webhook.site/token` with `{"default_content":"pingback-ssrf-test"}` → returns a uuid. Read hits at `GET https://webhook.site/token/<uuid>/requests`.
2. Take one real post URL from `/sitemap.xml` (or `/post-sitemap.xml` for WP).
3. `POST /xmlrpc.php` with `pingback.ping(source=<collector-url>/pingshot, target=<real post URL>)`.
4. A hit on the collector = confirmed unauth SSRF. The hit records the target's egress IP and a UA like `WordPress/<ver>; <site-url>; verifying pingback from <ip>` — save the hit JSON as evidence.
5. Amplification, still pointed only at your collector: wrap N pingback calls in ONE `system.multicall` request → N separate outbound GETs from the target. This proves request-to-connection amplification without touching any third party.
6. Loopback/internal probe: source=`http://127.0.0.1/` — a plain fault with no auth error indicates the fetch runs toward internal targets too.
- Response semantics: `faultCode 0` with empty faultString = ping accepted (fetch attempted); 'source URI' fault strings mean the fetch was refused — re-test once with a different collector URL before concluding blocked.

## 3. REST auth posture — 400 vs 401 decides what to probe next
- `400 rest_missing_callback_param` = the route dispatched to validation before any permission check. Safe follow-up: supply ALL required params but with ids/slugs that cannot exist (`post_id=999999999`, `slug=__not_installed__`).
- `rest_forbidden` 401/403 at that point = permission enforced (closed). A data-bearing answer = broken function-level authorization → route to the idor/BFLA workstream.
- Validation errors can leak inventory: an invalid-slug error that lists every installed plugin slug is an unauth disclosure on its own — save the raw response.
- NEVER supply the final valid value that would complete a state-changing flow (save/rollback/activate/delete). Probe only to the error boundary.

## 4. Known-CVE probes (non-invasive, version-first)
- Always read the installed version from `readme.txt` BEFORE claiming a CVE applies; the version alone can rule it out.
- Really Simple SSL CVE-2024-10924 (unauth admin login bypass, RSSSL ~6.x–7.2.x): `GET /wp-json/wp/v2/users/1?mop_relation=probe` — a full user object returned unauthenticated = vulnerable; `rest_user_invalid_id` 404 or `rest_not_logged_in` 401 = not applicable.
- Generalize: probe the CVE's distinctive REST argument with a bogus value; an auth-enforcing response (401/403) rules the CVE out without any exploitation.

## 5. Hardening checks that should be closed (record each verdict)
- `/wp-admin/install.php` must show 'Already Installed' with NO form; `setup-config.php` must refuse (wp-config exists); `upgrade.php` must not offer a form. A visible form on any of these is critical.
- `wp-login.php?action=register|lostpassword` — open registration on a gov/org site is a finding; note the hidden-login redirect (302→404) pattern as context, it does not affect xmlrpc.
- `/wp-content/uploads/<year>/<month>/` must 403 on listing; individual files returning 200 is normal, not a finding.
- `/wp-content/debug.log`, `wp-config.bak`, `.env`, `.git/HEAD`, `backup.zip`, `dump.sql` → expect 404 (or a WAF page).
- `wp-cron.php` POSTs return a blind 200 regardless of payload — do not interpret the 200 as anything.
- `?s=<svg/onload=alert(1)>probe` reflected XSS check: count every occurrence of the probe token and verify EACH one is entity/URL-encoded; one raw hit = reflected XSS, all-encoded = closed. Check title tag, JSON-LD blocks, breadcrumb markup, and the `<h1>` — different template layers encode differently.
- `/wp-json/oembed/1.0/proxy?url=` → 401 = proxy closed (open oEmbed proxy would be an SSRF variant).

## Rate discipline
The full baseline is ≈60 requests. On hosts with an active WAF plugin: single curls or thread pools ≤8, batches spread over tens of minutes, zero credential guessing. The deliverable is a clean finding set, not a ban.
