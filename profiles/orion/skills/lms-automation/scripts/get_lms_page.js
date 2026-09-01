const { chromium } = require('playwright');
const fs = require('fs');
const http = require('http');

const targetUrl = process.argv[2] || 'https://lms.telkomuniversity.ac.id/my/';
// ponytail: share one state file with get_lms_tasks_api.js. lms_cookies.json went stale
// and silently triggered MFA while the API scraper's session was still valid.
const statePath = '/root/.openclaw/workspace/state/lms_browser_state.json';

console.log(`Target URL: ${targetUrl}`);

async function getFlaresolverrCookies() {
    const postData = JSON.stringify({
        cmd: 'request.get',
        url: 'https://lms.telkomuniversity.ac.id/login/index.php',
        maxTimeout: 60000
    });
    
    return new Promise((resolve, reject) => {
        const req = http.request({
            hostname: '127.0.0.1',
            port: 8191,
            path: '/v1',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }
        }, (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => {
                try {
                    resolve(JSON.parse(data));
                } catch (e) {
                    reject(e);
                }
            });
        });
        
        req.on('error', reject);
        req.write(postData);
        req.end();
    });
}

(async () => {
    let flareCookies = [];
    let flareUA = undefined;
    
    try {
        console.log('Attempting to solve Cloudflare challenge via Flaresolverr...');
        const res = await getFlaresolverrCookies();
        if (res && res.status === 'ok') {
            console.log('Flaresolverr successfully bypassed Cloudflare.');
            flareCookies = res.solution.cookies;
            flareUA = res.solution.userAgent;
        } else {
            console.log('Flaresolverr returned non-ok status. Proceeding directly...');
        }
    } catch (err) {
        console.log(`Flaresolverr request failed (${err.message}). Proceeding directly...`);
    }

    let useProxy = true;
    let browser;
    let context;
    let page;

    async function initBrowser(proxyEnabled) {
        const launchOptions = {
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
        };

        if (proxyEnabled) {
            launchOptions.proxy = {
                server: 'http://20.192.4.173:33101',
                username: 'surfstudio-proxyId-node01',
                password: 'a89fba258b5953c10c091290cfd85240fdba6be655d411a3'
            };
        }

        browser = await chromium.launch(launchOptions);
        
        context = await browser.newContext({
            userAgent: flareUA,
            storageState: fs.existsSync(statePath) ? statePath : undefined
        });

        if (flareCookies && flareCookies.length > 0) {
            const mappedCookies = flareCookies.map(c => ({
                name: c.name,
                value: c.value,
                domain: c.domain,
                path: c.path,
                expires: c.expiry || -1,
                httpOnly: c.httpOnly,
                secure: c.secure,
                sameSite: c.sameSite === 'None' ? 'None' : (c.sameSite === 'Strict' ? 'Strict' : 'Lax')
            }));
            await context.addCookies(mappedCookies);
        }

        page = await context.newPage();
    }

    await initBrowser(useProxy);
    
    try {
        console.log(`Navigating to ${targetUrl} (commit only)...`);
        try {
            await page.goto(targetUrl, { waitUntil: 'commit', timeout: 30000 });
        } catch (gotoErr) {
            if (useProxy && (gotoErr.message.includes('ERR_PROXY_CONNECTION_FAILED') || gotoErr.message.includes('ERR_TUNNEL_CONNECTION_FAILED'))) {
                console.warn('Proxy connection failed. Retrying without proxy...');
                await browser.close();
                useProxy = false;
                await initBrowser(useProxy);
                await page.goto(targetUrl, { waitUntil: 'commit', timeout: 30000 });
            } else {
                throw gotoErr;
            }
        }

        await page.waitForTimeout(8000);
        console.log('Page loaded. URL:', page.url());

        if (page.url().includes('login.microsoftonline.com') || page.url().includes('login') || page.url().includes('oidc')) {
            console.log('Not logged in / Session expired. Redirecting to OIDC login page...');
            
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
                await page.goto('https://lms.telkomuniversity.ac.id/auth/oidc/', { waitUntil: 'commit', timeout: 30000 });
                await page.waitForTimeout(8000);
            }

            if (page.url().includes('login.microsoftonline.com')) {
                const emailInput = await page.locator('input[type="email"]').count();
                if (emailInput > 0) {
                    console.log('Entering email...');
                    await page.fill('input[type="email"]', 'indrayuda@student.telkomuniversity.ac.id');
                    await page.click('input[type="submit"], input#idSIButton9');
                    await page.waitForTimeout(5000);
                } else {
                    console.log('No email input found. Proceeding to password...');
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
                await page.click('input[type="submit"][value="Verify"], input#idSIButton9');
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
                const state = await context.storageState();
                fs.writeFileSync(statePath, JSON.stringify(state));
                console.log('Saved session state.');

                // Now re-navigate to targetUrl
                console.log(`Re-navigating to ${targetUrl}...`);
                await page.goto(targetUrl, { waitUntil: 'commit', timeout: 30000 });
                await page.waitForTimeout(8000);
            }
        }

        console.log('Taking page screenshot...');
        await page.screenshot({ path: '/tmp/lms_page_screenshot.png', fullPage: true });
        console.log('Saved screenshot of page to /tmp/lms_page_screenshot.png');

        const contentText = await page.evaluate(() => {
            const region = document.querySelector('#region-main') || document.body;
            return region ? region.innerText : 'No content found';
        });

        console.log('=== PAGE CONTENT START ===');
        console.log(contentText);
        console.log('=== PAGE CONTENT END ===');

    } catch (err) {
        console.error('Error during run:', err);
    } finally {
        await browser.close();
    }
})();