// Round 9 screenshots, one page load: node shots.js <url> <jobs.json>. Each job: {out, cam: [x,y,z,tx,ty,tz]} or {out, route, t} or {out, open: id} ; options paths, assumed, conf.
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const url = process.argv[2], jobs = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
  const browser = await chromium.launch({ executablePath: '/opt/hermes/tools/chromium-1208/chrome-linux64/chrome', args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 1400, height: 900 } });
  const page = await ctx.newPage();
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('response', (r) => { if (r.status() >= 400) errors.push(r.status() + ' ' + r.url()); });
  page.on('request', (r) => { if (r.url().includes('/_local/')) errors.push('LOCAL ' + r.url()); });
  await page.goto(url, { waitUntil: 'load', timeout: 120000 });
  await page.waitForFunction(() => window.__ready === true, null, { timeout: 180000 });
  for (const j of jobs) {
    await page.evaluate((j) => {
      const v = window.viewer;
      if (v.tour.get()) v.tour.stop();
      for (const k of ['paths', 'assumed', 'conf', 'halls', 'walls']) if (k in j) v.state[k] = j[k];
      v.apply();
      if (j.route) { v.tour.start(j.route, j.t || 0); return; }
      if (j.cam) { v.camera.position.set(...j.cam.slice(0, 3)); v.controls.target.set(...j.cam.slice(3, 6)); v.controls.update(); v.render(); }
    }, j);
    if (j.open) { await page.evaluate((id) => window.viewer.open(id), j.open); await page.waitForTimeout(2500); }
    await page.waitForTimeout(j.wait || 700);
    await page.screenshot({ path: j.out });
    if (j.panel) {
      await page.addStyleTag({ content: '#bpanel{position:absolute!important;bottom:auto!important;height:auto!important;max-height:none!important;overflow:visible!important}' });
      await page.waitForTimeout(400);
      const box = await page.locator('#bpanel').boundingBox();
      if (box) await page.screenshot({ path: j.panel, clip: { x: box.x, y: box.y, width: box.width, height: Math.min(box.height, 6000) }, fullPage: true });
    }
    console.log(j.out);
  }
  console.log(errors.length ? 'ERRORS: ' + errors.slice(0, 8).join(' | ') : 'clean');
  await browser.close();
})();
