# Givvy Snake Mine Initial Triage

## Target
- App family: Givvy
- Selected initial target: **Snake Mine**
- Package: `com.app.snake.mine.adventure`
- Official site page: `https://givvyapps.com/apps/snake-mine/`
- Public mirror page with package confirmation: `https://apps.qoo-app.com/en/app/150523`

## Top-level checklist
- `done` Confirm public identity of the target
- `done` Check whether official store/referral metadata is trustworthy
- `done` Recover a live family-level Givvy reward-shell baseline from older artifacts
- `in progress` Acquire a verified Snake Mine APK or equivalent client artifact
- `pending` Bind Snake Mine to its real backend host and snake-specific claim path
- `pending` Build and verify a Snake Mine autoclaim lane

## What is now proven
- Snake Mine is a real public Givvy title, not just a remembered name.
- QooApp still exposes a live public app page for Snake Mine and confirms:
  - package: `com.app.snake.mine.adventure`
  - app name: `Snake Mine`
  - developer: `BIGBILLION TECHNOLOGY`
  - Google Play package link: `https://play.google.com/store/apps/details?id=com.app.snake.mine.adventure`
- APKPure still has a real public details page for the target package and exposes the normal downloader entry path:
  - details page form: `https://apkpure.com/id/snake-mine/com.app.snake.mine.adventure`
  - downloader handoff: `https://apkpure.com/id/apk-downloader?p=com.app.snake.mine.adventure`
- The current Play Store page returns `404`, so public Play metadata is stale / removed even though third-party mirrors still remember the package.
- QooApp page keeps the package ID but leaves version, last-updated, and APK size blank. Treat those fields as unknown until an artifact is recovered.
- DuckDuckGo snippets show Snake Mine shortlinks under `app-earnings-link.com/snakeMine/...`, so the referral slug `snakeMine` is real.
- QooApp page also exposes a native-client deep link:
  - `qoohelper://app?id=150523&package_id=com.app.snake.mine.adventure`
- Inline QooApp page config exposes a related download/install handoff URL:
  - `https://apps.qqaoop.com/en/150523/dl`
- Hitting the QooApp helper route in a normal browser does not yield an APK file. It returns a `412` notice that tells the user to scan with QooApp or install/open the QooApp client first.
- QooApp screenshots show a wallet / rewards shell, not only game screens. Visible UI includes a gift icon, money-bag tab, profile tab, and referral/team-style icon. That strengthens the shared-shell hypothesis.

## What is proven about the official Givvy website
- `givvyapps.com/apps/snake-mine/` exists and is a real custom post entry on the Givvy WordPress site.
- The page itself is not trustworthy as a source of the real store link.
- Multiple different Givvy app pages currently embed the exact same `STORE` button target:
  - `https://app-earnings-link.com/sumatraIslandGold/58xmkjzax234fru24su`
- That means the current website store button is effectively a shared broken widget, not per-app truth.
- `app-earnings-link.com` currently returns an `undefined` redirect page for both the broken `sumatraIslandGold` path and tested Snake Mine shortlink paths, so this shortlink system is not a reliable artifact-acquisition lane right now.

## Family-shell reuse that is now proven live
A separate durable Givvy artifact, the public repo `IndraLawliet13/givvy`, still exposes a working old shell template for **Lucky Scratch Card**.

From that repo and live probes, the following family-level shell pieces are proven:
- package example: `com.appearnings.luckyscratchcard`
- reward host example: `givvy-scratch-card-new.herokuapp.com`
- config host: `givvy-general-config.herokuapp.com`
- app login / claim crypto: AES-ECB with `MD5("appWorldKey")`
- foreground / status crypto: AES-ECB with a fixed 16-byte key embedded in the script
- main endpoints:
  - `/loginEstablished`
  - `/getPresentReward`
  - `/sendForegroundStatus`
  - `/getStatus`
- main headers include app-specific `packageName`, `version`, `language`, and okhttp-style `User-Agent`

## Live protocol verification already completed on the family shell
The Lucky Scratch shell was replayed live with synthetic test values and produced a real downstream reward response.

### Verified facts
- `loginEstablished` accepts a replayable encrypted payload derived from:
  - `deviceType`
  - `version`
  - `deviceId`
  - `verts`
- The backend reuses the same account for the same `deviceId` and creates a new account for a different `deviceId`.
- `sendForegroundStatus` and `getStatus` both return structured config / anti-abuse / ad-provider data when the payload is encrypted correctly.
- After the sequence `loginEstablished -> sendForegroundStatus -> getStatus -> short wait -> getPresentReward`, the backend returned a real success payload with earned credits and balance update.

### One verified reward oracle
- successful claim response included:
  - `statusCode: 200`
  - `earnCredits: 2358`
  - `credits: 2358`
  - `userBalanceDouble: "0.0024"`
- This proves the family shell is not only metadata-readable. It is replayable at least for the Lucky Scratch specimen host.

## Snake-specific boundary catalog
### 1. Artifact acquisition boundary
- status: `open`
- relevance: without the APK or an equivalent direct client artifact, Snake-specific constants remain unproven.
- proven so far:
  - package identity is public
  - screenshots and public descriptions exist
  - APKPure captcha / downloader flow is real and reachable from a browser session
  - a valid captcha solve can produce `region_download` success plus a signed `down_url`
  - QooApp web confirms app id `150523` for this package but only exposes browser HTML plus native-client handoff
  - AppBrain also sees the title and marks it removed from Play while still naming developer `BIGBILLION TECHNOLOGY`
  - direct Google Play details URL currently returns 404 for this package from this runtime
  - Evozi web page is reachable but its actual download API host `api-apk.evozi.com` is not resolvable from this VPS
  - no verified APK/APKS has been recovered yet

### APKPure acquisition sub-findings
- The downloader JSONP endpoint is confirmed live:
  - `https://a.apkpure.com/api/v1/region_download`
- One real success oracle already happened at the API layer:
  - submitting a valid captcha returned `status_code: SUCCESS`
  - the response contained a signed `down_url` on `download.apkpure.com`
- Honest blocker after that success:
  - opening the returned `down_url` in the same browser session did **not** yield an APK download
  - the request immediately redirected back into APKPure error pages for this package, ending at:
    - `https://apkpure.com/error?e=ItemNotFound&p=com.app.snake.mine.adventure`
- Meaning:
  - captcha solve is **not** the final blocker
  - `region_download SUCCESS` is only a mid-layer oracle, not a real artifact oracle
  - the real failure now looks server-side on APKPure's download handoff for this package in this runtime

### 2. Store / referral boundary
- status: `narrowed`
- relevance: shortlinks often point toward the real acquisition or referral lane.
- proven so far:
  - Snake Mine shortlink slug is `snakeMine`
  - official Givvy site store button is globally broken / reused
  - tested shortlinks currently collapse to `undefined`
  - QooApp knows the target as native deep link `qoohelper://app?id=150523&package_id=com.app.snake.mine.adventure`
  - QooApp browser download page `/en/dl/150523` returns HTML 200 and rewrites buttons into `intent://apps.qoo-app.com/app/150523...package=com.qooapp.qoohelper...`, so the real acquisition step lives in the native client, not in the static web page

### 3. Shared reward-shell boundary
- status: `primary`
- relevance: this is the strongest current path toward Snake Mine autoclaim once Snake-specific constants are found.
- proven so far:
  - Snake Mine UI shows reward-shell behavior visually
  - older Givvy automation artifacts reveal the family protocol
  - the family protocol was replayed successfully on a live sibling host

### 4. Snake-specific reward-host boundary
- status: `open`
- relevance: the real host is needed for Snake-specific login and claim replay.
- tried and falsified:
  - a bounded set of obvious Heroku guesses such as `snake-mine.herokuapp.com`, `snake-mine-new.herokuapp.com`, `givvy-snake-mine.herokuapp.com`, and similar variants all returned Heroku `No such app`
- meaning:
  - the Snake backend host is not safely guessable from the title alone

### 5. Claim oracle boundary
- status: `family-level proven`, `Snake-specific open`
- relevance: this decides whether we can honestly say `autoclaim works`
- proven so far:
  - Lucky Scratch family shell can be replayed to a real claim success
- not yet proven:
  - Snake Mine host, claim timer, or claim endpoint sequence

## What failed or should not be repeated blindly
- Do not trust the current Givvy website `STORE` button as per-app truth.
- Do not treat `app-earnings-link.com` as a reliable current acquisition source without a fresh proof, because tested paths currently resolve to `undefined`.
- Do not assume the Snake backend host from the app title alone. A bounded host-guess pass already failed.
- Do not report `APKPure works` just because captcha was solved or `region_download` returned `SUCCESS`.
- Do not treat the signed `download.apkpure.com` URL as a guaranteed APK artifact. In this runtime it redirected back into APKPure error handling instead of returning the file.
- Do not assume QooApp web exposes a raw APK link for this title. The proven browser path stops at native `qoohelper` intent handoff.
- Do not assume Google Play direct web availability just because mirror pages reference Play. In this runtime the Play details URL for this package returned 404.
- Do not rely on Evozi as a quiet fallback here. Its front page may load while the real backend API host is not resolvable from this VPS.
- Do not claim Snake Mine autoclaim is working yet. The working oracle is currently only proven on the sibling Lucky Scratch shell.

## Best current next action
1. Recover a real Snake Mine APK / APKS from a device, a normal user browser session, or another artifact lane outside this failing APKPure handoff.
2. Once the APK is in hand, extract:
   - base API host
   - package / version truth
   - referral slug / deep links
   - reward / foreground / config classes
3. Best VPS-native acquisition lane now known: use `apkeep` with a real Google AAS token, because Aurora anonymous-token dispensers are Cloudflare-blocked from this VPS.
4. Current `apkeep` sub-blocker: the provided one-time `oauth_token` failed to mint an AAS token here, and `apkeep` can misleadingly print that failure while still exiting with code `0`, so success must be validated by checking for a real printed AAS token or downloaded files.
5. If APKPure is retried, capture the full redirect chain of the signed `down_url` in a real browser and treat that chain itself as the next debugging target.
6. Port the already verified family-shell replay onto Snake Mine and demand a Snake-specific reward oracle before claiming success.

## Main lesson
For Givvy apps, the fastest first move is still not gameplay RE. The productive lane is to recover the shared reward shell, then bind each title to its own concrete host / version / artifact. Snake Mine now has strong public identity and strong family-shell evidence, but its snake-specific backend is still the missing bridge.
