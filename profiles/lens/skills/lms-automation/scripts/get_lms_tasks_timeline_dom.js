const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    proxy: {
      server: 'http://20.192.4.173:33101',
      username: 'surfstudio-proxyId-node01',
      password: 'a89fba258b5953c10c091290cfd85240fdba6be655d411a3'
    },
    args: [
      '--no-sandbox', 
      '--disable-setuid-sandbox',
      '--disable-blink-features=AutomationControlled'
    ]
  });
  
  const statePath = '/root/.openclaw/workspace/state/lms_browser_state.json';
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    storageState: fs.existsSync(statePath) ? statePath : undefined
  });
  
  const page = await context.newPage();
  
  try {
    console.log("Navigating to LMS timeline...");
    await page.goto('https://lms.telkomuniversity.ac.id/my/index.php', { waitUntil: 'commit', timeout: 30000 });
    console.log("Waiting 15 seconds for network activity to settle...");
    await page.waitForTimeout(15000);
    
    const events = await page.evaluate(() => {
        const results = [];
        const items = document.querySelectorAll('.event-name-container');
        
        items.forEach(item => {
            const link = item.querySelector('a.ellipsis');
            const actionContainer = item.parentElement.querySelector('.coursename-action');
            
            if (link) {
                const name = link.innerText.trim();
                const url = link.href;
                const aria = link.getAttribute('aria-label');
                
                let course = "";
                if (actionContainer) {
                    course = actionContainer.innerText.trim();
                }
                
                results.push({ name, url, course, detail: aria });
            }
        });
        
        return results;
    });
    
    // Deduplicate array by URL to clean up output
    const uniqueEvents = Array.from(new Map(events.map(e => [e.url, e])).values());
    
    console.log("EVENTS_JSON:" + JSON.stringify(uniqueEvents, null, 2));
    
  } catch (err) {
      console.error("Error:", err.message);
  } finally {
      await browser.close();
  }
})();