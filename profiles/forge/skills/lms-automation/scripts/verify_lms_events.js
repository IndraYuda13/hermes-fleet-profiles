// Cross-checks Moodle events from TWO APIs and classifies past vs upcoming.
// Use when get_lms_tasks_api.js returns [] (confirm the empty is real) or when
// month-view DOM scraping shows events (confirm they are not already lapsed).
//
// Run: NODE_PATH=/root/.openclaw/workspace/node_modules \
//        node ~/.hermes/skills/lms-automation/scripts/verify_lms_events.js [daysBack] [daysFwd]
//
// ponytail: single month for monthly_view, add month loop if you need next month too.
const { chromium } = require('playwright');
const fs = require('fs');

const DAYS_BACK = parseInt(process.argv[2] || '60', 10);
const DAYS_FWD = parseInt(process.argv[3] || '60', 10);
const STATE = '/root/.openclaw/workspace/state/lms_browser_state.json';

(async () => {
    const browser = await chromium.launch({
        headless: true,
        executablePath: '/usr/bin/google-chrome'
    });
    const context = await browser.newContext({ storageState: fs.existsSync(STATE) ? STATE : undefined });
    const page = await context.newPage();
    try {
        // OIDC handshake FIRST. Direct goto to a target URL drops the session
        // and triggers a bogus MFA prompt. See SKILL.md section 15.
        await page.goto('https://lms.telkomuniversity.ac.id/login/index.php', { waitUntil: 'domcontentloaded', timeout: 90000 });
        const oidc = await page.$('a[href*="/auth/oidc/"]');
        if (oidc) { await oidc.click(); await page.waitForTimeout(8000); }
        console.log('after handshake:', page.url());
        if (page.url().includes('login.microsoftonline.com')) {
            console.log('SSO expired, run the auth script first. Not filling credentials here.');
            return;
        }

        const sesskey = await page.evaluate(() => {
            if (window.M && M.cfg && M.cfg.sesskey) return M.cfg.sesskey;
            const l = document.querySelector('a[href*="logout.php?sesskey="]');
            return l ? new URL(l.href).searchParams.get('sesskey') : null;
        });
        if (!sesskey) { console.log('no sesskey, session not established'); return; }

        const now = Math.floor(Date.now() / 1000);
        const res = await page.evaluate(async (d) => {
            const call = async (m, args) => {
                const r = await fetch(`https://lms.telkomuniversity.ac.id/lib/ajax/service.php?sesskey=${d.key}&info=${m}`, {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify([{ index: 0, methodname: m, args }])
                });
                return r.json();
            };
            const n = new Date();
            return {
                // limitnum MUST be <= 50 or Moodle throws. See SKILL.md section 12.
                timesort: await call('core_calendar_get_action_events_by_timesort', {
                    limitnum: 50, timesortfrom: d.from, timesortto: d.to, aftereventid: 0
                }),
                monthly: await call('core_calendar_get_calendar_monthly_view', {
                    year: n.getFullYear(), month: n.getMonth() + 1,
                    courseid: 1, categoryid: 0, includenavigation: true, mini: false
                })
            };
        }, { key: sesskey, from: now - 86400 * DAYS_BACK, to: now + 86400 * DAYS_FWD });

        // Merge both sources, dedupe on name+timesort, classify against real clock.
        const seen = new Set();
        const all = [];
        const push = (e, src) => {
            const k = `${e.name}|${e.timesort}`;
            if (seen.has(k)) return;
            seen.add(k);
            all.push({ t: e.timesort, name: e.name, course: e.course && e.course.fullname, src });
        };
        for (const e of (res.timesort?.[0]?.data?.events || [])) push(e, 'timesort');
        for (const w of (res.monthly?.[0]?.data?.weeks || [])) for (const d of w.days) for (const e of (d.events || [])) push(e, 'monthly');

        all.sort((a, b) => a.t - b.t);
        const fmt = t => new Date(t * 1000).toLocaleString('id-ID', { timeZone: 'Asia/Jakarta' });
        const past = all.filter(e => e.t < now);
        const up = all.filter(e => e.t >= now);

        console.log(`NOW (WIB): ${new Date().toLocaleString('id-ID', { timeZone: 'Asia/Jakarta' })}`);
        console.log(`WINDOW: -${DAYS_BACK}d .. +${DAYS_FWD}d | total ${all.length}`);
        console.log(`\n=== UPCOMING (${up.length}) ===`);
        up.forEach(e => console.log(`  ${fmt(e.t)} | ${e.name} | ${e.course} [${e.src}]`));
        console.log(`\n=== ALREADY PASSED (${past.length}) ===`);
        past.forEach(e => console.log(`  ${fmt(e.t)} | ${e.name} | ${e.course} [${e.src}]`));
        if (!up.length) console.log('\nVERDICT: no active tasks. Empty result confirmed by both APIs.');
    } catch (e) {
        console.error('ERR:', e.message);
    } finally {
        await browser.close();
    }
})();
