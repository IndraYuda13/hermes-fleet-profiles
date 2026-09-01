# Target
- Name: CeLOE LMS Tel U 4.5.0
- Type: Android app archive / APK delivery zip
- Goal: Learn how the app handles LMS access, auth/session persistence, WebView/browser handoff, and any reusable artifacts that can reduce repeated relogins for Telkom University LMS workflows.
- Scope / boundaries: Static triage first from the provided zip in workspace downloads. Focus on auth/session/storage/network surfaces relevant to the user's own LMS access.

## Current Milestone
- Correct artifact identified and statically triaged.
- Base conclusion is now stable: CeLOE app is a branded Moodle Mobile hybrid shell, and the most promising speedup lane is Moodle mobile auth/session mapping rather than native-code reversing.

## Artifacts
- `/root/.openclaw/workspace/downloads/CeLOE LMS Tel U_4.5.0.zip`
- `/root/.openclaw/workspace/projects/reverse-lms-celoe-app/`
- `/root/.openclaw/workspace/projects/reverse-lms-celoe-app/CHECKLIST.md`
- `/root/.openclaw/workspace/projects/reverse-lms-celoe-app/payload_unpacked/`

## Confirmed Findings
- The earlier generic `Downloads---...zip` was the wrong target; this case uses the workspace download artifact instead.
- The zip is an APKPure-style bundle containing:
  - base APK `id.ac.telkomuniversity.celoestudent.apk`
  - split APKs such as `config.arm64_v8a.apk`, language splits, and density splits
  - `manifest.json`
- Package / version:
  - package: `id.ac.telkomuniversity.celoestudent`
  - versionName: `4.5.0`
  - versionCode: `45002`
- Framework identity:
  - hybrid app, not pure native
  - Apache Cordova + Ionic WebView + Angular bundle in `assets/www/`
  - effectively a branded `Moodle Mobile 4.5.0` shell
- Strong branding / config clues:
  - `CeLOE LMS Tel-U`
  - `Moodle App`
  - `wsservice: moodle_mobile_app`
  - `customurlscheme: moodlemobile`
  - `onlyallowlistedsites: false`
- Target URLs hardcoded in web bundle:
  - `https://lms.telkomuniversity.ac.id`
  - `https://onlinelearning.telkomuniversity.ac.id`
  - `https://sandbox.telkomuniversity.ac.id`
  - `https://celoe.telkomuniversity.ac.id`
  - `https://celoe.telkomuniversity.ac.id/api`
- Exact login selector lane is now mapped:
  - login lazy module lands on route `/login/site`
  - chooser component is `CoreLoginSitePage` in chunk `3832.9a75c3c622b10d9a.js`
  - LMS button calls `connectLMS()` -> `SITE_URL_LMS`
  - MOOC button calls `connectMOOC()` -> `SITE_URL_MOOC`
  - only debug flag switches prod vs sandbox targets
- Exact auth decision gate is now mapped:
  - `CoreSites.checkSite()` calls public config WS `tool_mobile_get_public_config`
  - returned `typeoflogin` decides the lane
  - enum values found in JS:
    - `APP = 1`
    - `BROWSER = 2`
    - `EMBEDDED = 3`
  - helper `isSSOLoginNeeded()` returns true for `BROWSER` or `EMBEDDED`
- Exact token flow is now mapped:
  - credentials page calls `CoreSites.getUserToken(siteUrl, username, password)`
  - request goes to `${siteUrl}/login/token.php?lang=...`
  - response field `privatetoken` is captured as `privateToken`
  - then `CoreSites.newSite(siteUrl, token, privateToken)` persists the site
- Exact persistence model is now mapped:
  - site metadata row goes to DB table `sites`
  - DB row intentionally stores `token:""` and `privateToken:""`
  - real `token` and `privateToken` are stored via `storeTokensInSecureStorage(siteId, token, privateToken)`
  - DB write and secure-storage write are launched together with `Promise.all`
  - restoring a site later hydrates token/privateToken back from secure storage, not from plaintext DB
- Exact siteId / secure-storage naming is now mapped:
  - `siteId = md5(siteurl + username)` via `createSiteID(siteurl, username)`
  - secure-storage collection / namespace name is the `siteId`
  - token keys inside that collection are exactly `token` and `privateToken`
  - Android SharedPreferences namespace pattern is `moodlemobile_shared_prefs_<siteId>`
- Exact crypto binding is now mapped:
  - secure values are encrypted before being written to SharedPreferences
  - crypto helper stores sodium key material in prefs `com.adobe.phonegap.push`
  - important keys include `SODIUM_KEY_PUBLIC` and `SODIUM_KEY_PRIVATE`
  - Android Keystore alias used for unwrap/protection is `moodlemobile`
  - implication: naming/derivation is recoverable statically, but real decryption remains device-bound because the keystore alias is part of the chain
- Exact SSO browser flow is now mapped:
  - `prepareForSSOLogin()` builds launch URL, defaulting to `/admin/tool/mobile/launch.php`
  - it stores launch data including `siteUrl`, `passport`, `redirectPath`, `redirectOptions`, `urlToOpen`, and `ssoUrlParams`
  - `openBrowserForSSOLogin()` chooses embedded vs external browser from `typeoflogin`
  - callback is validated by `validateBrowserSSOLogin()` and carries `signature:::token:::privateToken`
  - signature check uses host + `passport`, so canonical host consistency matters
- Storage/session clues:
  - DB name path hinted by code: `MoodleMobile`
  - `sites` metadata is stored in DB
  - token / privateToken are not kept plaintext in the main site row and are pushed into secure storage via `storeTokensInSecureStorage(...)`
  - this means copying only shared prefs or only the visible DB is unlikely to preserve a full logged-in state
- Network/runtime config is permissive:
  - `<access origin="*">`, `<allow-navigation href="*">`, `<allow-intent href="*">`
  - base network security config allows cleartext traffic
- CeLOE-specific wrappers above stock Moodle Mobile are now confirmed:
  - fixed LMS/MOOC selector shell (`CoreLoginSitePage`) instead of generic site-entry UI
  - CeLOE/Tel-U branded login assets
  - custom post-login `CELOE_API/v1/MoodleAppTour` fetch for onboarding/tour modal
  - customized main/home shell with extra help/support component
- External storage usage is now mapped:
  - Android file base uses `cordova.file.externalApplicationStorageDirectory`
  - likely accessible content paths are under `/storage/emulated/0/Android/data/id.ac.telkomuniversity.celoestudent/files/`
  - notable subpaths include `sites/<siteId>/sharedfiles/`, `sites/<siteId>/h5p/`, `tmp/`, and `nosite/`
  - these look useful for offline content / shared attachments, not for core auth/session secrets
- High-confidence practical implication:
  - static APK analysis helps map the lane, but the real anti-relogin shortcut likely depends on preserving or extracting device-side app state: secure storage + DB + any browser-side OIDC state
  - without root/internal app-data access, the remaining static APK yield is now low; the best practical shortcut shifts to browser-session reuse rather than deeper APK-only reversing

## Hypotheses In Play
- The most reusable future shortcut will come from combining:
  - persisted Microsoft/Telkom OIDC browser state
  - Moodle mobile token/privateToken state from app storage
- Dynamic device-side inspection is needed to prove the exact files/records that change after successful login and refresh.

## Probes Run
- Located the real target file in `/root/.openclaw/workspace/downloads/`.
- Unpacked the APKPure zip bundle and identified the real base APK + split APKs.
- Inspected archive contents with `file`, `unzip`, and split listings.
- Performed manifest/framework/static triage with `aapt`, `apktool`, and string/asset scans.
- Extracted auth/session/network clues from `assets/www/`, `res/xml/config.xml`, and `res/xml/network_security_config.xml`.

## Blockers
- No live device/app-data dump yet, so secure-storage details are still inferred from static code and config rather than confirmed from runtime files.
- No dynamic traffic capture yet, so exact live endpoint ordering and callback details are not yet proven packet-by-packet.

## Next Best Action
- If Boskuu wants operational reuse from the app itself, move to dynamic analysis on a device/emulator or app-data export:
  1. inspect `/data/data/id.ac.telkomuniversity.celoestudent/`
  2. dump the `MoodleMobile` DB and surrounding storage
  3. identify secure-storage artifacts after a fresh successful login
  4. observe Microsoft/OIDC -> Moodle callback behavior and token refresh
- If Boskuu wants the fastest practical result without root, switch effort to browser-session workflow hardening:
  1. reuse the persistent LMS browser profile
  2. test whether the login lands directly on dashboard or still hits the CeLOE landing page
  3. script the minimal path through Microsoft/OIDC when a refresh is needed
  4. keep this as the main operational lane while the app-based lane remains blocked by device-bound storage
- Secondary static follow-up only if explicitly desired:
  1. map migration / fallback logic for any legacy plaintext token rows or upgrade paths
  2. test whether the same live login behavior can be reproduced more cleanly from browser automation than from the app lane

## Distilled Reusable Lesson
- When the user says a file was sent manually to workspace/downloads, check that folder directly before assuming the newest inbound media attachment is the right artifact.
- For Moodle-branded campus apps, the first strong hypothesis should be: hybrid Moodle Mobile shell + web/OIDC login + token/privateToken in app storage, not a bespoke native LMS protocol.
- The final login-mode gate is server-driven public config (`tool_mobile_get_public_config.typeoflogin`), not just the visible mobile UI. If `typeoflogin` forces browser/embedded SSO, the real shortcut problem shifts from form automation to preserving launch-data consistency, secure token storage, and browser/OIDC state.
- For Moodle Mobile-derived apps, static reversing can often recover exact storage naming (`siteId`, prefs namespace, key names) even when the secrets themselves stay device-bound behind Android Keystore.
