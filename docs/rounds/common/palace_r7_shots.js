// Round 7 screenshots: node shots.js <jobs.json>. Each job: {url, out, width, height, panel (true: capture the building panel whole), full (full page), wait (ms)}
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch({ executablePath: process.env.CHROME || '/opt/hermes/tools/chromium-1208/chrome-linux64/chrome', args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  for (const j of jobs) {
    const ctx = await browser.newContext({ viewport: { width: j.width || 1400, height: j.height || 900 }, deviceScaleFactor: j.dpr || 1 });
    const page = await ctx.newPage();
    const errors = [];
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
    page.on('pageerror', (e) => errors.push(String(e)));
    page.on('requestfailed', (r) => { if (r.url() !== j.url) errors.push('failed ' + r.url()); });
    page.on('response', (r) => { if (r.status() >= 400) errors.push(r.status() + ' ' + r.url()); });
    await page.goto(j.url, { waitUntil: 'load', timeout: 90000 });
    await page.waitForTimeout(j.wait || 2500);
    if (j.full) { const H = await page.evaluate(() => document.documentElement.scrollHeight); for (let y = 0; y < H; y += 600) { await page.evaluate((v) => window.scrollTo(0, v), y); await page.waitForTimeout(250); } await page.evaluate(() => window.scrollTo(0, 0)); await page.waitForTimeout(1500); }
    if (j.panel) {
      await page.waitForSelector('#bpanel:not([hidden])', { timeout: 60000 });
      await page.waitForTimeout(j.wait || 4000);
      await page.addStyleTag({ content: '#bpanel{position:absolute!important;bottom:auto!important;height:auto!important;max-height:none!important;overflow:visible!important} details.ev-more{}' });
      if (j.open) await page.evaluate(() => document.querySelectorAll('#bpanel details').forEach((d) => { d.open = true; }));
      await page.waitForTimeout(800);
      const box = await page.locator('#bpanel').boundingBox();
      await page.screenshot({ path: j.out, clip: { x: box.x, y: box.y, width: box.width, height: Math.min(box.height, j.maxh || 9000) }, fullPage: true });
    } else if (j.full) {
      // one page load, captured in segments of 3000 px (tall single captures repeat themselves past about 8000 px here), stitched by stitch.py
      const H = await page.evaluate(() => document.documentElement.scrollHeight);
      const W = j.width || 1400;
      let n = 0;
      for (let y = 0; y < H; y += 3000, n++) {
        await page.screenshot({ path: j.out.replace(/\.png$/, `.part${String(n).padStart(2, '0')}.png`), clip: { x: 0, y, width: W, height: Math.min(3000, H - y) }, fullPage: true });
      }
    } else {
      await page.screenshot({ path: j.out });
    }
    console.log(j.out, errors.length ? 'ERRORS: ' + errors.slice(0, 5).join(' | ') : 'clean');
    await ctx.close();
  }
  await browser.close();
})();
