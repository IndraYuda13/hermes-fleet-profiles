const { chromium } = require('playwright');
const fs = require('fs');

const targetUrl = process.argv[2];
if (!targetUrl) {
    console.error("Usage: node scrape_quiz.js <quiz_url>");
    process.exit(1);
}

(async () => {
    const userDataDir = '/root/.openclaw/workspace/state/lms_chrome_profile';
    const context = await chromium.launchPersistentContext(userDataDir, {
        headless: true,
        proxy: { server: 'http://20.192.4.173:33101', username: 'surfstudio-proxyId-node01', password: 'a89fba258b5953c10c091290cfd85240fdba6be655d411a3' },
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
    });
    
    try {
        const page = await context.newPage();
        console.log('Navigating to quiz: ' + targetUrl);
        await page.goto(targetUrl, { waitUntil: 'commit', timeout: 60000 });
        await page.waitForTimeout(5000);

        if (page.url().includes('/login/')) {
            console.log('OIDC redirect detected. Logging in...');
            const oidc = await page.$('.login-identityprovider-btn, a[href*="auth/oidc"]');
            if (oidc) {
                await oidc.click();
                await page.waitForTimeout(10000);
            }
            await page.goto(targetUrl, { waitUntil: 'commit' });
            await page.waitForTimeout(5000);
        }

        const attemptBtn = await page.$('form.quizattempt input[type="submit"], button:has-text("Continue your attempt"), button:has-text("Re-attempt quiz"), button:has-text("Attempt quiz")');
        if (attemptBtn) {
            console.log('Clicking attempt button...');
            await attemptBtn.click();
            await page.waitForTimeout(5000);
            const confirmBtn = await page.$('input[type="button"][value="Start attempt"], button:has-text("Start attempt")');
            if (confirmBtn) {
                await confirmBtn.click();
                await page.waitForTimeout(5000);
            }
        }

        console.log('Current URL:', page.url());
        const attemptMatch = page.url().match(/attempt=(\d+)/);
        if (!attemptMatch) throw new Error('Could not enter the quiz attempt page.');
        const attemptId = attemptMatch[1];
        console.log('Active Attempt ID:', attemptId);

        let questions = [];
        let hasNext = true;
        let pIndex = 0;

        while (hasNext) {
            let targetPageUrl = `https://lms.telkomuniversity.ac.id/mod/quiz/attempt.php?attempt=${attemptId}&page=${pIndex}`;
            console.log(`Navigating to page index ${pIndex}...`);
            
            let loaded = false;
            for(let r=0; r<3; r++) {
                try {
                    await page.goto(targetPageUrl, { waitUntil: 'commit', timeout: 35000 });
                    await page.waitForTimeout(2000);
                    loaded = true;
                    break;
                } catch(e) {
                    console.log(`Retry ${r+1} failed for page index ${pIndex}`);
                    await page.waitForTimeout(4000);
                }
            }

            if(!loaded) {
                 console.log("Could not load page. Finishing.");
                 break;
            }

            const qData = await page.evaluate(() => {
                const results = [];
                document.querySelectorAll('.que').forEach(qNode => {
                    const qNum = qNode.querySelector('.no')?.innerText.trim().replace(/Question\s+/i, '') || '';
                    const qText = qNode.querySelector('.qtext')?.innerText.trim() || '';
                    const options = Array.from(qNode.querySelectorAll('.answer div[class^="r"]')).map(opt => {
                        const label = opt.querySelector('label, span.flex-fill') || opt;
                        let text = label.innerText.trim();
                        text = text.replace(/^[a-z]\.\s*/i, '').trim();
                        return text;
                    });
                    results.push({ qNum, qText, options });
                });
                return results;
            });

            if (qData && qData.length > 0) {
                questions.push(...qData);
                console.log(`Scraped ${qData.length} questions from page index ${pIndex}.`);
                pIndex++;
            } else {
                console.log("No questions found. Reached end of quiz.");
                hasNext = false;
            }

            if(pIndex > 150) break; // safety cap
        }

        const scrapedData = {
            quizUrl: targetUrl,
            attemptId: attemptId,
            questions: questions
        };

        fs.writeFileSync('/tmp/scraped_quiz.json', JSON.stringify(scrapedData, null, 2));
        console.log(`Scraped ${questions.length} questions successfully.`);

    } catch (err) {
        console.error('Error in scrape:', err);
    } finally {
        await context.close();
    }
})();
