const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
    const browser = await chromium.launch({
        headless: true,
        executablePath: '/usr/bin/google-chrome',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
        // proxy removed - using direct / flaresolverr
    });

    const statePath = '/root/.openclaw/workspace/state/lms_browser_state.json';
    const context = await browser.newContext({
        storageState: fs.existsSync(statePath) ? statePath : undefined
    });

    const page = await context.newPage();
    console.log('Navigating to LMS Dashboard (commit only)...');
    
    try {
        // Use 'commit' to bypass heavy telemetry / tracking scripts hanging networkidle
        await page.goto('https://lms.telkomuniversity.ac.id/my/', { waitUntil: 'commit', timeout: 30000 });
        console.log('Page navigated (commit). Waiting 10 seconds for rendering...');
        await page.waitForTimeout(10000);

        console.log('Current URL:', page.url());

        if (page.url().includes('login.microsoftonline.com') || page.url().includes('login') || page.url().includes('oidc')) {
            console.log('Not logged in. Redirected to login page.');
            
            // Login index page logic for OIDC button clicking
            if (page.url().includes('login/index.php')) {
                console.log('On Moodle login index. Clicking OIDC button...');
                const hasOidc = await page.locator('a[href*="/auth/oidc/"]').count();
                if (hasOidc > 0) {
                    await page.click('a[href*="/auth/oidc/"]');
                    await page.waitForTimeout(10000);
                } else {
                    console.log('No OIDC link found on login index. Falling back to direct /auth/oidc/ navigation...');
                    await page.goto('https://lms.telkomuniversity.ac.id/auth/oidc/', { waitUntil: 'commit', timeout: 30000 });
                    await page.waitForTimeout(10000);
                }
            } else if (!page.url().includes('login.microsoftonline.com')) {
                console.log('Navigating to Moodle OIDC login...');
                await page.goto('https://lms.telkomuniversity.ac.id/auth/oidc/', { waitUntil: 'commit', timeout: 30000 });
                await page.waitForTimeout(10000);
            }

            console.log('Current URL at login stage:', page.url());

            if (page.url().includes('login.microsoftonline.com')) {
                // Check if we are on the Microsoft Login flow where email input is present
                const emailInput = await page.locator('input[type="email"]').count();
                if (emailInput > 0) {
                    console.log('Entering email...');
                    await page.fill('input[type="email"]', 'indrayuda@student.telkomuniversity.ac.id');
                    await page.click('input[type="submit"], input#idSIButton9');
                    await page.waitForTimeout(5000);
                } else {
                    console.log('Email input not found, checking for profile picker...');
                    const profileTile = await page.locator('div.tile, div[role="button"]').count();
                    if (profileTile > 0) {
                        await page.click('div.tile, div[role="button"]');
                        await page.waitForTimeout(5000);
                    }
                }
                
                console.log('Entering password...');
                await page.fill('input[type="password"]', 'Yuda@4321');
                await page.click('input[type="submit"], input#idSIButton9');
                await page.waitForTimeout(8000);

                console.log('Current URL after password:', page.url());
                await page.screenshot({ path: '/tmp/lms_auth_mfa.png' });
                console.log('Saved screenshot of MFA screen to /tmp/lms_auth_mfa.png');
                
                console.log('=== INPUT_REQUIRED ===');
                const codeFile = '/tmp/mfa_code.txt';
                if (fs.existsSync(codeFile)) {
                    fs.unlinkSync(codeFile);
                }

                console.log('Waiting for /tmp/mfa_code.txt to be created by the user...');
                let code = "";
                for (let i = 0; i < 90; i++) {
                    if (fs.existsSync(codeFile)) {
                        code = fs.readFileSync(codeFile, 'utf8').trim();
                        console.log('Received MFA code:', code);
                        fs.unlinkSync(codeFile);
                        break;
                    }
                    await page.waitForTimeout(1000);
                }

                if (!code) {
                    console.log('TIMEOUT: No MFA code received.');
                    await browser.close();
                    process.exit(1);
                }

                console.log('Entering MFA code...');
                await page.fill('input[name="otc"]', code);
                await page.click('input[type="submit"][value="Verify"]');
                await page.waitForTimeout(8000);

                console.log('URL after verification:', page.url());
                await page.screenshot({ path: '/tmp/lms_auth_post_verify.png' });

                if (page.url().includes('login.microsoftonline.com')) {
                    const stayBtn = await page.$('input[type="submit"][value="Yes"], input#idSIButton9');
                    if (stayBtn) {
                        await stayBtn.click();
                        console.log('Clicked "Stay signed in".');
                        await page.waitForTimeout(8000);
                    }
                }

                console.log('URL after login completion:', page.url());
                await context.storageState({ path: statePath });
                console.log('Saved session state.');
            }
        } else {
            console.log('Already logged in! URL:', page.url());
        }

        // Re-navigate to my page to ensure we extract sesskey
        if (!page.url().includes('/my/')) {
            console.log('Navigating to dashboard /my/');
            await page.goto('https://lms.telkomuniversity.ac.id/my/', { waitUntil: 'commit', timeout: 30000 });
            await page.waitForTimeout(10000);
        }

        console.log('Extracting sesskey...');
        const sesskey = await page.evaluate(() => {
            if (window.M && window.M.cfg && window.M.cfg.sesskey) {
                return window.M.cfg.sesskey;
            }
            const logoutLink = document.querySelector('a[href*="logout.php?sesskey="]');
            if (logoutLink) {
                return new URL(logoutLink.href).searchParams.get('sesskey');
            }
            return null;
        });

        if (!sesskey) {
            console.log('Could not find sesskey.');
            await page.screenshot({ path: '/tmp/dashboard_error.png', fullPage: true });
            await browser.close();
            process.exit(1);
        }

        console.log(`Found sesskey: ${sesskey}`);
        console.log('Fetching tasks via Moodle API...');

        const payload = [{
            "index": 0,
            "methodname": "core_calendar_get_action_events_by_timesort",
            "args": {
                "limitnum": 30,
                "timesortfrom": Math.floor(Date.now() / 1000) - 86400,
                "timesortto": Math.floor(Date.now() / 1000) + (86400 * 30),
                "aftereventid": 0
            }
        }];

        const response = await page.evaluate(async (data) => {
            const { key, payload } = data;
            const res = await fetch(`https://lms.telkomuniversity.ac.id/lib/ajax/service.php?sesskey=${key}&info=core_calendar_get_action_events_by_timesort`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            return res.json();
        }, { key: sesskey, payload });

        console.log('=== EVENTS_JSON_START ===');
        console.log(JSON.stringify(response[0].data.events));
        console.log('=== EVENTS_JSON_END ===');

    } catch (err) {
        console.error('Error during run:', err);
        await page.screenshot({ path: '/tmp/lms_run_error.png', fullPage: true });
    } finally {
        await browser.close();
    }
})();