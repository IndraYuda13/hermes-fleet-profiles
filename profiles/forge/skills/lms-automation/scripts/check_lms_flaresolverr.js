const { chromium } = require('playwright');
const fs = require('fs');

async function getFlareSolverr() {
    const res = await fetch("http://127.0.0.1:8191/v1", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            cmd: "request.get",
            url: "https://lms.telkomuniversity.ac.id/login/index.php",
            maxTimeout: 60000
        })
    });
    const data = await res.json();
    return data.solution;
}

(async () => {
    const solution = await getFlareSolverr();
    const STATE = '/root/.openclaw/workspace/state/lms_browser_state.json';
    let savedStorage = undefined;
    if (fs.existsSync(STATE)) {
        try { savedStorage = JSON.parse(fs.readFileSync(STATE, 'utf8')); } catch(e) {}
    }

    const browser = await chromium.launch({
        headless: true,
        executablePath: '/usr/bin/google-chrome',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
    });

    const context = await browser.newContext({
        userAgent: solution.userAgent,
        storageState: savedStorage
    });

    const pwCookies = solution.cookies.map(c => ({
        name: c.name,
        value: c.value,
        domain: c.domain.startsWith('.') ? c.domain.slice(1) : c.domain,
        path: c.path || '/',
        secure: c.secure || false,
        httpOnly: c.httpOnly || false,
        sameSite: 'None'
    }));
    await context.addCookies(pwCookies);

    const page = await context.newPage();
    await page.goto('https://lms.telkomuniversity.ac.id/login/index.php', { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(2000);

    const oidc = await page.$('a[href*="/auth/oidc/"]');
    if (oidc) {
        await oidc.click();
        await page.waitForTimeout(6000);
    }

    const sesskey = await page.evaluate(() => {
        if (window.M && window.M.cfg && window.M.cfg.sesskey) return window.M.cfg.sesskey;
        const l = document.querySelector('a[href*="logout.php?sesskey="]');
        return l ? new URL(l.href).searchParams.get('sesskey') : null;
    });

    if (!sesskey) {
        console.log("Failed to extract sesskey.");
        await browser.close();
        process.exit(1);
    }

    const now = Math.floor(Date.now() / 1000);
    const DAYS_BACK = parseInt(process.argv[2] || '60', 10);
    const DAYS_FWD = parseInt(process.argv[3] || '60', 10);

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
            timesort: await call('core_calendar_get_action_events_by_timesort', {
                limitnum: 50, timesortfrom: d.from, timesortto: d.to, aftereventid: 0
            }),
            monthly: await call('core_calendar_get_calendar_monthly_view', {
                year: n.getFullYear(), month: n.getMonth() + 1,
                courseid: 1, categoryid: 0, includenavigation: true, mini: false
            }),
            courses: await call('core_course_get_enrolled_courses_by_timeline_classification', {
                classification: 'all', limit: 0, offset: 0, sort: 'fullname'
            })
        };
    }, { key: sesskey, from: now - 86400 * DAYS_BACK, to: now + 86400 * DAYS_FWD });

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

    console.log(`\nNOW (WIB): ${new Date().toLocaleString('id-ID', { timeZone: 'Asia/Jakarta' })}`);
    console.log(`WINDOW: -${DAYS_BACK}d .. +${DAYS_FWD}d | total ${all.length}`);
    console.log(`\n=== UPCOMING (${up.length}) ===`);
    up.forEach(e => console.log(`• ${e.name} (${e.course || 'N/A'}) | Deadline: ${fmt(e.t)} [${e.src}]`));
    console.log(`\n=== ALREADY PASSED (${past.length}) ===`);
    past.forEach(e => console.log(`• ${e.name} (${e.course || 'N/A'}) | Selesai: ${fmt(e.t)} [${e.src}]`));

    const courses = res.courses?.[0]?.data?.courses || [];
    console.log(`\n=== ENROLLED COURSES (${courses.length}) ===`);
    courses.forEach(c => console.log(`- [ID: ${c.id}] ${c.fullname} (${c.shortname})`));

    await browser.close();
})();
