const { chromium } = require('playwright');
const fs = require('fs');

// Comprehensive Quiz Solver Rules for "Self Management" / "Post-Test Self Management"
function solveQuiz(text, options) {
    const q = text.toLowerCase();
    const getLetter = (index) => String.fromCharCode(65 + index);

    // Q1: Setiap individu memiliki gaya belajar sesuai dengan karakteristiknya. Manakah pernyataaan yang termasuk bagian gaya belajar kinestetik?
    if (q.includes('gaya belajar kinestetik') || (q.includes('kinestetik') && q.includes('karakteristiknya'))) {
        const idx = options.findIndex(o => o.text.toLowerCase().includes('belajar dengan melakukan kegiatan secara langsung') || o.text.toLowerCase().includes('menyentuh') || o.text.toLowerCase().includes('terlibat langsung'));
        if (idx !== -1) return [getLetter(idx)];
    }

    // Q2: Manakah dari pernyataan berikut yang membantu untuk keberhasilan dalam meraih keinginan?
    if (q.includes('keberhasilan dalam meraih keinginan') || q.includes('meraih keinginan')) {
        const idx = options.findIndex(o => o.text.toLowerCase().includes('mengendalikan ketakutan') || o.text.toLowerCase().includes('tidak cemas menghadapi kegagalan'));
        if (idx !== -1) return [getLetter(idx)];
    }

    // Q3: Pernyataan berkaitan dengan Self awareness adalah…
    if (q.includes('berkaitan dengan self awareness adalah') || q.includes('berkaitan dengan self awareness adalah…')) {
        const idx = options.findIndex(o => o.text.toLowerCase().includes('pemahaman individu secara mendalam terhadap dirinya seperti emosi, kekuatan, kelemahan, kebutuhan') || o.text.toLowerCase().includes('dorongan, dan lingkungan sekitar'));
        if (idx !== -1) return [getLetter(idx)];
    }

    // Q4: Cara menentukan tujuan yang efektif adalah…
    if (q.includes('menentukan tujuan yang efektif adalah') || q.includes('menentukan tujuan yang efektif adalah…')) {
        const idx = options.findIndex(o => o.text.toLowerCase().includes('realistis terhadap tujuan dan tenggat waktu') || o.text.toLowerCase().includes('tenggat waktu tercapainya tujuan'));
        if (idx !== -1) return [getLetter(idx)];
    }

    // Q5: Manakah diantara pernyataan berikut yang menunjukkan seseorang yang memiliki kesadaran penuh akan dirinya baik secara internal maupun eksternal?
    if (q.includes('kesadaran penuh akan dirinya baik secara internal maupun eksternal') || q.includes('kesadaran penuh akan dirinya')) {
        const idx = options.findIndex(o => o.text.toLowerCase().includes('cintia menyadari kekuatan') || o.text.toLowerCase().includes('menerima masukan dari orang lain'));
        if (idx !== -1) return [getLetter(idx)];
    }

    // Q6: Berikut beberapa manfaat yang didapat jika mahasiswa mengetahui gaya belajar yang tepat bagi dirinya, kecuali
    if (q.includes('mengetahui gaya belajar yang tepat bagi dirinya, kecuali') || q.includes('gaya belajar yang tepat bagi dirinya, kecuali')) {
        const idx = options.findIndex(o => o.text.toLowerCase().includes('meningkatkan kewaspadaan') || o.text.toLowerCase().includes('kewaspadaan dalam proses belajar'));
        if (idx !== -1) return [getLetter(idx)];
    }

    // Q7: Dr. Lewis Terman menyatakan bahwa terdapat tiga faktor terpenting penentu kesuksesan seseorang, diantaranya kecuali…
    if (q.includes('lewis terman') || q.includes('tiga faktor terpenting penentu kesuksesan')) {
        const idx = options.findIndex(o => o.text.toLowerCase().includes('kecerdasan') || o.text.toLowerCase() === 'b.' || o.text.toLowerCase().includes('kecerdasan'));
        if (idx !== -1) return [getLetter(idx)];
    }

    // Q8: Upaya yang dapat dilakukan menghadapi tekanan saat pertama masuk sebagai mahasiswa baru adalah
    if (q.includes('menghadapi tekanan saat pertama masuk sebagai mahasiswa baru') || q.includes('tekanan saat pertama masuk')) {
        const idx = options.findIndex(o => o.text.toLowerCase().includes('memilih cara belajar yang paling realistis') || o.text.toLowerCase().includes('gaya belajar anda'));
        if (idx !== -1) return [getLetter(idx)];
    }

    // Q9: Sukses belajar di Perguruan Tinggi
    if (q.includes('sukses belajar di perguruan tinggi adalah') || q.includes('sukses belajar di perguruan tinggi') || q.includes('ipk 3.25')) {
        const idx = options.findIndex(o => o.text.includes('2, 3, 5') || o.text.toLowerCase().includes('2, 3, 5') || o.text.includes('2,3,5'));
        if (idx !== -1) return [getLetter(idx)];
    }

    // Q10: Uraian yang tepat tentang internal self awareness, kecuali…
    if (q.includes('internal self awareness, kecuali') || q.includes('internal self awareness, kecuali…')) {
        const idx = options.findIndex(o => o.text.toLowerCase().includes('tingkat stress tidak berhubungan') || o.text.toLowerCase().includes('tingkat stress tidak berhubungan dengan pemahaman diri'));
        if (idx !== -1) return [getLetter(idx)];
    }

    // Q11: Andi seringkali belajar di malam hari...
    if (q.includes('seringkali belajar di malam hari') || q.includes('menemukan kebiasaan belajar lebih efektif')) {
        const idx = options.findIndex(o => o.text.toLowerCase().includes('mengidentifikasi kebiasaan') || o.text.toLowerCase().includes('mengidentifikasi kebiasaan belajarnya'));
        if (idx !== -1) return [getLetter(idx)];
    }

    // Q12: Manfaat yang didapatkan saat kita memiliki self awareness adalah, kecuali
    if (q.includes('manfaat yang didapatkan saat kita memiliki self awareness adalah, kecuali') || (q.includes('memiliki self awareness') && q.includes('kecuali') && q.includes('tanggungjawab'))) {
        const idx = options.findIndex(o => o.text.toLowerCase().includes('mengetahui kekurangan diri agar kita fokus untuk mengatasinya') || o.text.toLowerCase().includes('kekurangan diri agar kita fokus'));
        if (idx !== -1) return [getLetter(idx)];
    }

    // Q13: Setiap individu dapat berubah, namun ada hal yang tidak dapat diubah pada dirinya. Diantaranya, kecuali…
    if (q.includes('hal yang tidak dapat diubah pada dirinya. diantaranya, kecuali') || q.includes('tidak dapat diubah pada dirinya. diantaranya, kecuali…')) {
        const idx = options.findIndex(o => o.text.toLowerCase().includes('kebiasaan') || o.text.toLowerCase() === 'kebiasaan');
        if (idx !== -1) return [getLetter(idx)];
    }

    // Q14: Berdasarkan pernyataan di bawah ini, pilihlah pernyataan tepat dalam penulisan tujuan yang paling efektif…
    if (q.includes('pernyataan tepat dalam penulisan tujuan yang paling efektif') || q.includes('penulisan tujuan yang paling efektif')) {
        const idx = options.findIndex(o => o.text.toLowerCase().includes('anwar berencana untuk lulus') || o.text.toLowerCase().includes('ipk di atas 3.30 dan tidak ada nilai c'));
        if (idx !== -1) return [getLetter(idx)];
    }

    // Q15: Intan seorang mahasiswa di jurusan Manajemen...
    if (q.includes('intan seorang mahasiswa') || q.includes('penentuan tujuan yang dilakukan oleh intan')) {
        const idx = options.findIndex(o => o.text.toLowerCase().includes('terukur dan spesifik') || o.text.toLowerCase().includes('terukur dan spesifik'));
        if (idx !== -1) return [getLetter(idx)];
    }

    // Heuristic fallback: pick longest option
    let longestIdx = 0;
    let maxLen = 0;
    options.forEach((opt, idx) => {
        if (opt.text.length > maxLen) {
            maxLen = opt.text.length;
            longestIdx = idx;
        }
    });

    return [getLetter(longestIdx)];
}

const targetUrl = process.argv[2];
const flareCookies = JSON.parse(process.argv[3]);
const flareUA = process.argv[4];

console.log(`Target URL: ${targetUrl}`);

(async () => {
    const startTime = Date.now();
    const browser = await chromium.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
    });

    const statePath = '/root/.openclaw/workspace/state/lms_cookies.json';
    const context = await browser.newContext({
        userAgent: flareUA
    });

    // Map cookies
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

    if (fs.existsSync(statePath)) {
        const savedState = JSON.parse(fs.readFileSync(statePath, 'utf8'));
        const savedCookies = savedState.cookies || [];
        for (const sc of savedCookies) {
            const exists = mappedCookies.some(mc => mc.name === sc.name && mc.domain === sc.domain);
            if (!exists) {
                mappedCookies.push({
                    name: sc.name,
                    value: sc.value,
                    domain: sc.domain,
                    path: sc.path,
                    expires: sc.expires || -1,
                    httpOnly: sc.httpOnly,
                    secure: sc.secure,
                    sameSite: sc.sameSite
                });
            }
        }
        await context.addCookies(mappedCookies);
    }

    const page = await context.newPage();
    
    try {
        console.log('Refreshing OIDC Login session...');
        await page.goto('https://lms.telkomuniversity.ac.id/auth/oidc/', { waitUntil: 'commit', timeout: 30000 });
        await page.waitForTimeout(6000);

        console.log(`Navigating to target quiz page: ${targetUrl}`);
        await page.goto(targetUrl, { waitUntil: 'commit', timeout: 30000 });
        await page.waitForTimeout(6000);

        const continueBtn = await page.$('form.quizattempt input[type="submit"], button:has-text("Continue your attempt"), button:has-text("Re-attempt quiz"), button:has-text("Attempt quiz")');
        if (continueBtn) {
            console.log('Clicking Attempt/Re-attempt/Continue button...');
            await continueBtn.click();
            await page.waitForTimeout(6000);
            
            const startAttemptConfirmBtn = await page.$('input[type="button"][value="Start attempt"], button:has-text("Start attempt")');
            if (startAttemptConfirmBtn) {
                console.log('Confirming start attempt...');
                await startAttemptConfirmBtn.click();
                await page.waitForTimeout(6000);
            }
        }

        let finished = false;
        let iteration = 0;

        while (!finished && iteration < 30) {
            iteration++;
            console.log(`--- Quiz Loop Iteration ${iteration} ---`);
            
            const qData = await page.evaluate(() => {
                const qNode = document.querySelector('.que');
                if (!qNode) return null;
                
                const qNum = qNode.querySelector('.no')?.innerText.trim().replace(/Question\s+/i, '');
                const qText = qNode.querySelector('.qtext')?.innerText.trim();
                const options = Array.from(qNode.querySelectorAll('.answer div[class^="r"]')).map((opt, idx) => {
                    const label = opt.querySelector('label, span.flex-fill') || opt;
                    const input = opt.querySelector('input');
                    return {
                        id: input?.id || '',
                        letter: String.fromCharCode(65 + idx),
                        text: label?.innerText?.trim() || ''
                    };
                });
                return { qNum, qText, options };
            });

            if (!qData) {
                console.log('No question node found. Checking if we are on the summary page...');
                const summaryText = await page.evaluate(() => document.body.innerText);
                if (summaryText.includes('Summary of attempt') || summaryText.includes('Submit all and finish') || summaryText.includes('Kirim semua dan selesai')) {
                    console.log('On summary page. Submitting quiz...');
                    
                    const submitAllBtn = await page.$('button:has-text("Submit all and finish"), input[type="submit"][value*="Submit all"]');
                    if (submitAllBtn) {
                        await submitAllBtn.click();
                        await page.waitForTimeout(3000);
                        
                        await page.evaluate(() => {
                            const buttons = Array.from(document.querySelectorAll(".modal-dialog button, .modal-dialog input, button.btn-primary, button.btn-danger"));
                            const target = buttons.find(b => {
                                const txt = (b.innerText || b.value || "").toLowerCase();
                                return txt.includes("submit all") || txt.includes("kirim semua") || txt.includes("finish") || txt.includes("selesai");
                            });
                            if (target) target.click();
                        });
                        await page.waitForTimeout(10000);
                        console.log('Quiz submitted successfully!');
                    }
                    finished = true;
                    break;
                }
                break;
            }

            console.log(`Question ${qData.qNum}: ${qData.qText}`);
            const resolved = solveQuiz(qData.qText, qData.options);
            console.log(`Choosing Option: ${resolved[0]}`);

            const chosenOption = qData.options.find(o => resolved.includes(o.letter));
            if (chosenOption) {
                await page.evaluate((targetId) => {
                    const input = document.getElementById(targetId);
                    if (input) {
                        input.click();
                        input.checked = true;
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }, chosenOption.id);
                await page.waitForTimeout(1500);
            }

            // Click Next page
            const nextInput = await page.$('input[value="Next page"], input[value="Next"], input[value="Selanjutnya"]');
            if (nextInput) {
                console.log('Clicking Next page...');
                await nextInput.click();
                await page.waitForLoadState('commit');
                await page.waitForTimeout(4000);
            } else {
                console.log('No next page button. Attempting to click Finish attempt...');
                const finishBtn = await page.$('a:has-text("Finish attempt"), button:has-text("Finish"), button:has-text("Selesaikan")');
                if (finishBtn) {
                    await finishBtn.click();
                    await page.waitForLoadState('commit');
                    await page.waitForTimeout(4000);
                } else {
                    finished = true;
                }
            }
        }

        const endTime = Date.now();
        const durationSec = Math.round((endTime - startTime) / 1000);
        console.log(`Total duration: ${durationSec} seconds`);

        console.log('Taking final results page screenshot...');
        await page.screenshot({ path: '/tmp/lms_quiz_final_results.png', fullPage: true });
        console.log('Saved screenshot to /tmp/lms_quiz_final_results.png');

    } catch (err) {
        console.error('Error during run:', err);
    } finally {
        await browser.close();
    }
})();
