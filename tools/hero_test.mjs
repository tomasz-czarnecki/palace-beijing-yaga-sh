// The homepage hero (Round 22b): the full-screen carousel of AI pictures, on the EN and zh pages.
// Checks: autoplay turns the slide, pause holds it, arrows, dots and keys work, the locator's dot moves with the slide, reduced
// motion never turns it, the phone takes the 2:3 crop, only slide 1 and then the next one are fetched, slide 1 takes its 3840
// after load on a wide high-density screen, no console errors and no failed requests; and it prints what the first load weighs.
// node tools/hero_test.mjs [--port 8985]   (needs the scratch Playwright, as tools/loader_test.mjs)
import { spawn } from 'node:child_process';
import { createRequire } from 'node:module';
const REPO = new URL('..', import.meta.url).pathname.replace(/\/$/, '');
const require = createRequire('/opt/data/cache/scratch/palace_r11_kit_tools/node_modules/noop.js');
const { chromium } = require('playwright');
const pi = process.argv.indexOf('--port');
const PORT = pi > 0 ? Number(process.argv[pi + 1]) : 8985;
const BASE = `http://127.0.0.1:${PORT}/`;
const srv = spawn(REPO + '/.venv/bin/python', [REPO + '/tools/serve_local.py', '--port', String(PORT), '--public'], { cwd: REPO, stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
for (let k = 0; k < 60; k++) { try { await fetch(BASE, { method: 'HEAD' }); break; } catch { await sleep(300); } }
const browser = await chromium.launch({ executablePath: '/opt/hermes/tools/chromium-1208/chrome-linux64/chrome', args: ['--no-sandbox'] });
const results = [];
const ok = (name, pass, info = '') => { results.push(pass); console.log(`${pass ? 'PASS' : 'FAIL'}  ${name}${info ? '  ' + info : ''}`); };
const kb = (n) => `${Math.round(n / 1024)} KB`;

async function open(path, opts = {}) {
  const ctx = await browser.newContext({ viewport: opts.viewport || { width: 1920, height: 1080 }, deviceScaleFactor: opts.dpr || 1, reducedMotion: opts.reduced ? 'reduce' : 'no-preference' });
  const page = await ctx.newPage();
  const errors = [];
  const heroes = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push('pageerror: ' + e));
  page.on('requestfailed', (r) => errors.push('failed: ' + r.url()));
  page.on('response', (r) => { if (r.status() >= 400) errors.push(`${r.status()}: ${r.url()}`); });
  page.on('request', (r) => { const m = r.url().match(/hero-(\d)-[a-z-]+-(\w+)\.webp/); if (m) heroes.push(`${m[1]}-${m[2]}`); });
  await page.goto(BASE + path, { waitUntil: 'load' });
  return { ctx, page, errors, heroes };
}
const at = (page) => page.evaluate(() => Number(document.querySelector('.hero-full').dataset.at));
const dot = (page) => page.evaluate(() => { const c = document.querySelector('.hero-loc.is-on .gm-dot'); return `${c.getAttribute('cx')},${c.getAttribute('cy')}`; });
const waitAt = (page, i, ms = 4000) => page.waitForFunction((i) => document.querySelector('.hero-full').dataset.at === String(i), i, { timeout: ms }).then(() => true, () => false);

try {
  for (const lang of ['', 'zh/']) {
    const tag = lang ? 'zh' : 'en';
    // 1920 x 1080, one density: what loads, autoplay, the controls
    const { ctx, page, errors, heroes } = await open(lang);
    const firstLoad = [...heroes];
    ok(`${tag}: before load only slide 1 is fetched`, firstLoad.length === 1 && firstLoad[0].startsWith('1-'), firstLoad.join(' '));
    await sleep(3000);
    ok(`${tag}: slide 1 is fetched once`, heroes.filter((h) => h.startsWith('1-')).length === 1, heroes.join(' '));
    const w = await page.evaluate(() => performance.getEntriesByType('resource').concat(performance.getEntriesByType('navigation')).reduce((s, e) => s + (e.transferSize || e.encodedBodySize || 0), 0));
    const pic = await page.evaluate(() => { const e = performance.getEntriesByType('resource').find((r) => /hero-1-/.test(r.name)); return e ? [e.name.split('/').pop(), e.transferSize || e.encodedBodySize] : null; });
    console.log(`      ${tag} 1920x1080: transferred 3 s after load (with the next slide and lazy pictures near the fold) ${kb(w)}; slide 1 ${pic?.[0]} ${kb(pic?.[1] || 0)}`);
    await sleep(3500); // after load, on idle: the next slide only
    ok(`${tag}: after load the next slide only`, heroes.filter((h) => h.startsWith('2-')).length === 1 && !heroes.some((h) => /^[345]-/.test(h)), heroes.join(' '));
    const d0 = await dot(page);
    const t0 = Date.now();
    const turned = await waitAt(page, 1, 12000);
    ok(`${tag}: autoplay turns to slide 2`, turned, `${((Date.now() - t0) / 1000).toFixed(1)} s after the idle start`);
    ok(`${tag}: the locator's dot moves with the slide`, (await dot(page)) !== d0, `${d0} -> ${await dot(page)}`);
    const caption = await page.evaluate(() => [document.querySelectorAll('.hero-cap.is-on').length, document.querySelector('.hero-cap.is-on').dataset.i, document.querySelector('.hero-cap.is-on .hero-ai')?.textContent]);
    ok(`${tag}: one caption shown, the slide's, with the AI label`, caption[0] === 1 && caption[1] === '1' && /AI/.test(caption[2] || ''), caption[2]);
    await sleep(1500);
    ok(`${tag}: slide 3 fetched only now (one ahead)`, heroes.some((h) => h.startsWith('3-')) && !heroes.some((h) => /^[45]-/.test(h)), heroes.join(' '));
    // pause
    await page.click('.hero-pause');
    const p0 = await at(page);
    ok(`${tag}: pause button says play`, (await page.getAttribute('.hero-pause', 'data-state')) === 'stopped');
    await sleep(10000);
    ok(`${tag}: paused, it stays`, (await at(page)) === p0, `slide ${p0 + 1}`);
    await page.click('.hero-pause');
    // arrows, dots, keys
    await page.mouse.move(960, 300);
    const a0 = await at(page);
    await page.click('.hero-next');
    ok(`${tag}: next arrow`, await waitAt(page, (a0 + 1) % 5));
    await page.click('.hero-prev');
    ok(`${tag}: previous arrow`, await waitAt(page, a0));
    await page.click('.hero-dot >> nth=3');
    ok(`${tag}: dot 4`, await waitAt(page, 3));
    await page.focus('.hero-dot >> nth=3');
    await page.keyboard.press('ArrowRight');
    ok(`${tag}: arrow key right`, await waitAt(page, 4));
    await page.keyboard.press('ArrowRight');
    ok(`${tag}: wraps round to slide 1`, await waitAt(page, 0));
    // hover on the controls holds it
    await page.hover('.hero-dot >> nth=0');
    ok(`${tag}: hovering the controls holds the clock`, await page.evaluate(() => document.querySelector('.hero-full').hasAttribute('data-still')));
    // the lightbox opens the 3840
    await page.click('.hero-cap.is-on .hero-large');
    const lb = await page.evaluate(() => ({ open: !!document.querySelector('dialog[open]'), src: document.querySelector('dialog.lb img')?.src.split('/').pop(), cap: document.querySelector('dialog.lb .lb-cap')?.textContent }));
    ok(`${tag}: View large opens the 3840 in the lightbox, with the AI note`, lb.open && /-3840\.webp$/.test(lb.src) && /AI/.test(lb.cap), lb.src);
    await page.keyboard.press('Escape');
    const sw = await page.evaluate(() => document.documentElement.scrollWidth);
    ok(`${tag}: no horizontal scroll at 1920`, sw <= 1920, String(sw));
    ok(`${tag}: no console errors or failed requests at 1920`, errors.length === 0, errors.slice(0, 4).join(' | '));
    await ctx.close();

    // reduced motion: shows slide 1 and the controls, never turns by itself
    {
      const { ctx, page, errors } = await open(lang, { reduced: true });
      await sleep(11000);
      ok(`${tag}: reduced motion, no autoplay`, (await at(page)) === 0 && (await page.getAttribute('.hero-pause', 'data-state')) === 'stopped');
      await page.click('.hero-next');
      ok(`${tag}: reduced motion, the arrow still works`, await waitAt(page, 1));
      ok(`${tag}: no errors with reduced motion`, errors.length === 0, errors.slice(0, 3).join(' | '));
      await ctx.close();
    }
    // phone: the 2:3 crop, no horizontal scroll
    {
      const { ctx, page, errors, heroes } = await open(lang, { viewport: { width: 390, height: 844 }, dpr: 3 });
      await page.waitForFunction(() => document.querySelector('.hero-slide.is-on img').currentSrc);
      const src = await page.evaluate(() => document.querySelector('.hero-slide.is-on img').currentSrc.split('/').pop());
      ok(`${tag}: phone takes the 2:3 crop`, /-phone\.webp$/.test(src), src);
      const w = await page.evaluate(() => performance.getEntriesByType('resource').concat(performance.getEntriesByType('navigation')).reduce((s, e) => s + (e.transferSize || e.encodedBodySize || 0), 0));
      console.log(`      ${tag} 390x844 @3x: transferred at the load event ${kb(w)}; hero files ${heroes.join(' ')}`);
      const sw = await page.evaluate(() => document.documentElement.scrollWidth);
      ok(`${tag}: no horizontal scroll at 390`, sw <= 390, String(sw));
      ok(`${tag}: locator shown on the phone`, await page.evaluate(() => { const r = document.querySelector('.hero-loc.is-on .gmap').getBoundingClientRect(); return r.width >= 70 && r.top >= 0; }));
      ok(`${tag}: no errors on the phone`, errors.length === 0, errors.slice(0, 3).join(' | '));
      await ctx.close();
    }
  }
  // a wide high-density screen: slide 1 starts at 2560 and takes the 3840 after load
  {
    const { ctx, page, heroes } = await open('', { viewport: { width: 1920, height: 1080 }, dpr: 2 });
    const before = heroes.filter((h) => h.startsWith('1-'));
    await sleep(4000);
    const src = await page.evaluate(() => document.querySelector('.hero-slide[data-slide] img').currentSrc.split('/').pop());
    ok('1920 @2x: first paint at most the 2560, then the 3840', before.length === 1 && /2560/.test(before[0]) && /-3840\.webp$/.test(src), `${before.join(' ')} -> ${src}`);
    await ctx.close();
  }
} finally { await browser.close(); srv.kill(); }
const failed = results.filter((r) => !r).length;
console.log(`\n${results.length - failed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
