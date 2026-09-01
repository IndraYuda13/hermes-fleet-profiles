# Cloudflare & Microsoft SSO Troubleshooting for CeLOE LMS

During automated sessions checking the CeLOE LMS (lms.telkomuniversity.ac.id), Cloudflare Turnstile challenges and Microsoft SSO redirection loops frequently block headless/standard automated flows. This reference documents the patterns observed and the exact workarounds that succeeded.

## Cloudflare Turnstile Blocking Patterns

1. **Proxy IP Reputation Blocks:**
   - **Symptom:** Running Playwright through the Surfshark proxy (`20.192.4.173:33101`) triggers an infinite Cloudflare Turnstile loop ("Just a moment..." challenge page).
   - **Reason:** The proxy IP has a high risk score, causing Cloudflare WAF to continuously prompt for Turnstile verification.
   - **Fix:** Disable the proxy option in Playwright launch options and connect directly. Direct connection from the host IP often bypasses or easily resolves Turnstile challenges.

2. **Headless vs. Headful (xvfb-run) Resolution:**
   - **Symptom:** Headless browser runs (`headless: true`) get silently blocked at the Turnstile page, and automatic Turnstile resolution fails.
   - **Fix:** Launch Playwright in headful mode (`headless: false`) wrapped in `xvfb-run` (virtual frame buffer):
     ```bash
     xvfb-run -a env NODE_PATH=/root/.openclaw/workspace/node_modules node script.js
     ```
     This allows Turnstile's client-side canvas and rendering checks to evaluate successfully.

3. **Flaresolverr Hangs:**
   - **Symptom:** Flaresolverr service times out or throws `ECONNRESET` / socket hang up errors.
   - **Fix:** Rely on headful Playwright with a persistent context instead of Flaresolverr for MoodleSession verification. If Flaresolverr is mandatory, ensure a service restart:
     ```bash
     docker restart flaresolverr
     ```

## Microsoft SSO Redirection Handling

When checking or logging into CeLOE LMS, the OIDC handshake (`/auth/oidc/`) redirects to `login.microsoftonline.com`.

1. **OIDC Navigation Timeouts:**
   - **Symptom:** Clicking the "Sign in with Microsoft" button (`a[href*="/auth/oidc/"]`) results in `navigation timeout` because the transition from the LMS domain to Microsoft and back to LMS takes longer than 30s.
   - **Fix:** Catch the navigation timeout and monitor the page URL. If the page lands on `login.microsoftonline.com`, wait for the user session redirection automatically:
     ```javascript
     await page.click('a[href*="/auth/oidc/"]');
     await page.waitForNavigation({ waitUntil: 'networkidle', timeout: 60000 }).catch(e => console.log("Redirection taking time..."));
     ```

2. **Persistent Context Session Reuse:**
   - **Symptom:** Login sessions expire, prompting for password or MFA on every run.
   - **Fix:** Always use a persistent user data directory (`launchPersistentContext`) at `/root/.openclaw/workspace/state/lms_chrome_profile`. This stores and reuses cookies, local storage, and the Microsoft SSO state, preventing subsequent MFA prompts.
